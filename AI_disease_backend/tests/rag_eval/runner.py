"""RAG 评估入口。

- evaluate_one(sample, ...) → EvalRecord
- evaluate_all(samples, concurrency=5) → List[EvalRecord]

设计要点：
1. Milvus 调用不阻塞（pymilvus 自身有线程池）；embedding/LLM 同步调用 → 全部包到 asyncio.to_thread
2. 并发上限 5，避开 DashScope 限流
3. RAG 检索走原始 MilvusClient.search，**不**走 retrieve_medical_context，
   因为后者会把 top-3 拼成 context 文本，丢掉 score/source 元数据（评估要算 MRR / source recall）
"""
from __future__ import annotations

import asyncio
import time
from typing import List

from lang_chain_core.rag_core import rag as rag_singleton
from pymilvus import MilvusClient

from tests.rag_eval.judge import judge_answer
from tests.rag_eval.metrics import EvalRecord, QASample, compute_recall


def _milvus_search_sync(
    client: MilvusClient, collection: str, vector: list, top_k: int
) -> list:
    """同步调 Milvus 检索（pymilvus 内部有线程池，asyncio 里直接调不会阻塞事件循环）。"""
    res = client.search(
        collection_name=collection,
        data=[vector],
        limit=top_k,
        output_fields=["text", "source"],
    )
    return res[0] if res else []


def _rag_invoke_sync(chain, question: str) -> str:
    """同步调 RAG chain。"""
    try:
        return chain.invoke(question)
    except Exception as e:
        return f"（RAG 调用失败：{e}）"


async def evaluate_one(
    sample: QASample,
    *,
    milvus: MilvusClient,
    embedder,
    rag_chain,
    judge_llm,
    collection: str,
    top_k: int = 3,
) -> EvalRecord:
    """单条评估：embed → search → recall → RAG → judge。"""
    record = EvalRecord(sample=sample)
    t0 = time.time()

    # 1. embed query
    vector = await asyncio.to_thread(embedder.embed_query, sample.question)

    # 2. milvus search
    hits = await asyncio.to_thread(_milvus_search_sync, milvus, collection, vector, top_k)
    record.retrieved_docs = [
        {"text": h["entity"].get("text", ""),
         "source": h["entity"].get("source", ""),
         "distance": h.get("distance") or h.get("score") or 0.0}
        for h in hits
    ]

    # 3. 召回指标
    compute_recall(record)

    # 4. RAG 生成
    rag_answer = await asyncio.to_thread(_rag_invoke_sync, rag_chain, sample.question)
    record.rag_answer = rag_answer

    # 5. LLM-as-Judge
    context_text = "\n\n".join(d["text"] for d in record.retrieved_docs)
    scores, reason, parse_error = await asyncio.to_thread(
        judge_answer,
        judge_llm,
        sample.question,
        context_text,
        sample.reference,
        rag_answer,
    )
    if parse_error:
        # 解析失败兜底：全 1 分 + 标记，让失败可见
        record.judge_scores = {dim: 1 for dim in ("faithfulness", "relevance", "completeness", "refusal")}
        record.judge_reason = "parse_error"
        record.parse_error = True
    else:
        record.judge_scores = scores
        record.judge_reason = reason

    record.latency_ms = int((time.time() - t0) * 1000)
    return record


async def evaluate_all(
    samples: List[QASample],
    *,
    milvus: MilvusClient,
    embedder,
    rag_chain,
    judge_llm,
    collection: str,
    top_k: int = 3,
    concurrency: int = 5,
) -> List[EvalRecord]:
    """并发跑所有样本，信号量控制并发度。"""
    sem = asyncio.Semaphore(concurrency)

    async def _run(s: QASample) -> EvalRecord:
        async with sem:
            return await evaluate_one(
                s,
                milvus=milvus,
                embedder=embedder,
                rag_chain=rag_chain,
                judge_llm=judge_llm,
                collection=collection,
                top_k=top_k,
            )

    return await asyncio.gather(*[_run(s) for s in samples])


def load_qa_samples(yaml_path: str) -> List[QASample]:
    """从 yaml 加载 QASample 列表。"""
    import yaml
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    items = data.get("items", [])
    return [QASample(
        id=it["id"],
        category=it["category"],
        question=it["question"],
        reference=it.get("reference", ""),
        must_hit=it.get("must_hit", []),
        source=it.get("source", ""),
        expect_refuse=it.get("expect_refuse", False),
        difficulty=it.get("difficulty", "medium"),
    ) for it in items]