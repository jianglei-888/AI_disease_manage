"""RAG 评估的 pytest 入口。

默认通过 marker `rag_eval` 跳过：
- `pytest` → 跳过（不跑评估）
- `pytest -m rag_eval` → 跑评估
- `pytest -m "not rag_eval"` → 只跑单元测试（其实 pytest 默认就跳过）

跑完会写 reports/eval_*.md 和 reports/eval_*.json。
"""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

import pytest

# 把项目根加进 sys.path（pytest 不会自动加）
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings  # noqa: E402
from tests.rag_eval import report as rag_report  # noqa: E402
from tests.rag_eval.metrics import aggregate  # noqa: E402
from tests.rag_eval.runner import evaluate_all  # noqa: E402


pytestmark = pytest.mark.rag_eval


@pytest.mark.asyncio
async def test_rag_eval_full(
    qa_samples, embedder, milvus_client, judge_llm, rag_chain,
):
    """跑完整 20 题评估，写报告，断言阈值。"""
    assert qa_samples, "qa_set.yaml 没读到样本"

    t0 = time.time()
    records = await evaluate_all(
        qa_samples,
        milvus=milvus_client,
        embedder=embedder,
        rag_chain=rag_chain,
        judge_llm=judge_llm,
        collection=settings.MILVUS_COLLECTION,
        top_k=3,
        concurrency=5,
    )
    total_ms = int((time.time() - t0) * 1000)

    summary = aggregate(records)
    rag_report.write(
        records,
        summary,
        model=settings.LLM_MODEL,
        concurrency=5,
        total_ms=total_ms,
    )

    # 阈值断言（fail 时 pytest 会显示具体指标）
    assert summary.hit_at_3 >= 0.80, f"Hit@3 = {summary.hit_at_3:.2f}, 阈值 0.80"
    assert summary.mrr >= 0.60, f"MRR = {summary.mrr:.2f}, 阈值 0.60"
    assert summary.faithfulness >= 4.0, f"忠实性 = {summary.faithfulness:.2f}, 阈值 4.0"
    assert summary.relevance >= 4.0, f"相关性 = {summary.relevance:.2f}, 阈值 4.0"
    assert summary.completeness >= 3.5, f"完整性 = {summary.completeness:.2f}, 阈值 3.5"
    assert summary.refusal >= 4.5, f"拒答准确 = {summary.refusal:.2f}, 阈值 4.5"