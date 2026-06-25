"""RAG 评估独立入口：`python -m tests.rag_eval`。

不依赖 pytest，方便 CI 单独跑评估 / 调试。
"""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


async def _run():
    from config.settings import settings
    from app.utils.embeddings import DashScopeCompatibleEmbeddings
    from langchain_openai import ChatOpenAI
    from lang_chain_core.rag_core import rag as rag_singleton
    from pymilvus import MilvusClient
    from tests.rag_eval import report as rag_report
    from tests.rag_eval.metrics import aggregate
    from tests.rag_eval.runner import evaluate_all, load_qa_samples

    yaml_path = Path(__file__).resolve().parent / "data" / "qa_set.yaml"
    samples = load_qa_samples(str(yaml_path))
    print(f"加载 {len(samples)} 条评估样本")

    embedder = DashScopeCompatibleEmbeddings()
    milvus = MilvusClient(uri=settings.MILVUS_URI, db_name=settings.MILVUS_DB)
    judge_llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        temperature=0,
    )
    rag_chain = rag_singleton.get_chain()

    t0 = time.time()
    records = await evaluate_all(
        samples,
        milvus=milvus,
        embedder=embedder,
        rag_chain=rag_chain,
        judge_llm=judge_llm,
        collection=settings.MILVUS_COLLECTION,
        top_k=3,
        concurrency=5,
    )
    total_ms = int((time.time() - t0) * 1000)

    summary = aggregate(records)
    rag_report.write(records, summary, model=settings.LLM_MODEL, concurrency=5, total_ms=total_ms)

    if not summary.threshold_pass:
        print(f"\n⚠️  阈值未通过，失败样本：{summary.failed_ids}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(_run())