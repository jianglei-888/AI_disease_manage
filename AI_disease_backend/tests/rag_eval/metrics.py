"""RAG 评估指标：数据结构 + 召回层纯函数。

不依赖网络 / LLM，便于本地反复测。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class QASample:
    """一条评估样本（从 yaml 读出来）。"""
    id: str
    category: str
    question: str
    reference: str
    must_hit: List[str] = field(default_factory=list)
    source: str = ""
    expect_refuse: bool = False
    difficulty: str = "medium"


@dataclass
class EvalRecord:
    """一条评估结果（运行时累计填充）。"""
    sample: QASample
    retrieved_docs: List[dict] = field(default_factory=list)   # [{text, source, distance}, ...]
    hit_at_3: bool = False
    reciprocal_rank: float = 0.0
    source_recall_at_3: bool = False
    rag_answer: str = ""
    judge_scores: Dict[str, int] = field(default_factory=dict)  # {faithfulness, relevance, completeness, refusal}
    judge_reason: str = ""
    parse_error: bool = False
    latency_ms: int = 0


@dataclass
class EvalSummary:
    """汇总报告。"""
    n: int
    hit_at_3: float
    mrr: float
    source_recall_at_3: float
    faithfulness: float
    relevance: float
    completeness: float
    refusal: float
    judge_total: float
    per_category: Dict[str, Dict[str, float]]
    threshold_pass: bool
    failed_ids: List[str]


# 阈值常量：单一来源，便于一处调整
THRESHOLDS = {
    "hit_at_3": 0.80,
    "mrr": 0.60,
    "source_recall_at_3": 0.70,
    "faithfulness": 4.0,
    "relevance": 4.0,
    "completeness": 3.5,
    "refusal": 4.5,
}


def _hit_kw(text: str, must_hit: List[str]) -> bool:
    """任一 must_hit 关键字出现在 text 中即命中（不区分大小写）。"""
    if not must_hit:
        return True  # 没要求 → 算命中
    return any(kw and kw in text for kw in must_hit)


def compute_recall(record: EvalRecord) -> None:
    """在 record 上原地写入 hit_at_3 / reciprocal_rank / source_recall_at_3。

    命中判定：top-3 任一 doc 满足（must_hit 关键字 OR source 匹配）。
    """
    docs = record.retrieved_docs[:3]
    if not docs:
        # 没召回到任何东西
        record.hit_at_3 = False
        record.reciprocal_rank = 0.0
        record.source_recall_at_3 = False
        return

    # 是否命中 source（整个 top-3 中任一 source 等于预期）
    expected_source = record.sample.source
    hit_src = bool(expected_source) and any(
        d.get("source") == expected_source for d in docs
    )

    # 是否命中关键字
    hit_kw = any(
        _hit_kw(d.get("text", ""), record.sample.must_hit) for d in docs
    )

    record.hit_at_3 = hit_src or hit_kw
    record.source_recall_at_3 = hit_src

    # MRR：找到第一条满足条件的 rank
    rr = 0.0
    for i, d in enumerate(docs, start=1):
        if hit_src and d.get("source") == expected_source:
            rr = 1.0 / i
            break
        if hit_kw and _hit_kw(d.get("text", ""), record.sample.must_hit):
            rr = 1.0 / i
            break
    record.reciprocal_rank = rr


def aggregate(records: List[EvalRecord]) -> EvalSummary:
    """聚合所有 EvalRecord → EvalSummary，校验阈值。"""
    n = len(records)
    if n == 0:
        return EvalSummary(
            n=0, hit_at_3=0.0, mrr=0.0, source_recall_at_3=0.0,
            faithfulness=0.0, relevance=0.0, completeness=0.0, refusal=0.0,
            judge_total=0.0, per_category={}, threshold_pass=False, failed_ids=[],
        )

    # 拒答题（refuse/edge）不计入"召回指标"，但仍计入"生成指标"
    recall_records = [r for r in records if not r.sample.expect_refuse]

    def mean(xs: List[float]) -> float:
        return sum(xs) / len(xs) if xs else 0.0

    # 召回层
    hit_at_3 = mean([1.0 if r.hit_at_3 else 0.0 for r in recall_records]) if recall_records else 0.0
    mrr = mean([r.reciprocal_rank for r in recall_records]) if recall_records else 0.0
    src_recall = mean([1.0 if r.source_recall_at_3 else 0.0 for r in recall_records]) if recall_records else 0.0

    # 生成层（拒答题也计入，因为 Judge prompt 专门为拒答设计）
    def avg_dim(dim: str) -> float:
        vals = [r.judge_scores.get(dim, 0) for r in records if r.judge_scores]
        return mean(vals)

    faith = avg_dim("faithfulness")
    relev = avg_dim("relevance")
    compl = avg_dim("completeness")
    ref = avg_dim("refusal")
    total_judge = mean([faith, relev, compl, ref])

    # 按类别
    cats: Dict[str, List[EvalRecord]] = {}
    for r in records:
        cats.setdefault(r.sample.category, []).append(r)

    per_cat: Dict[str, Dict[str, float]] = {}
    for cat, rs in cats.items():
        cat_n = len(rs)
        cat_recall = [r for r in rs if not r.sample.expect_refuse]
        per_cat[cat] = {
            "n": float(cat_n),
            "hit_at_3": mean([1.0 if r.hit_at_3 else 0.0 for r in cat_recall]) if cat_recall else 0.0,
            "faithfulness": mean([r.judge_scores.get("faithfulness", 0) for r in rs if r.judge_scores]),
            "relevance": mean([r.judge_scores.get("relevance", 0) for r in rs if r.judge_scores]),
            "completeness": mean([r.judge_scores.get("completeness", 0) for r in rs if r.judge_scores]),
            "refusal": mean([r.judge_scores.get("refusal", 0) for r in rs if r.judge_scores]),
        }

    # 失败判定：阈值不达标
    failed = []
    if hit_at_3 < THRESHOLDS["hit_at_3"]:
        failed.extend([r.sample.id for r in recall_records if not r.hit_at_3])
    if faith < THRESHOLDS["faithfulness"]:
        failed.extend([r.sample.id for r in records if r.judge_scores.get("faithfulness", 0) < THRESHOLDS["faithfulness"]])
    if ref < THRESHOLDS["refusal"]:
        failed.extend([r.sample.id for r in records if r.judge_scores.get("refusal", 0) < THRESHOLDS["refusal"]])

    passed = (
        hit_at_3 >= THRESHOLDS["hit_at_3"]
        and mrr >= THRESHOLDS["mrr"]
        and faith >= THRESHOLDS["faithfulness"]
        and relev >= THRESHOLDS["relevance"]
        and compl >= THRESHOLDS["completeness"]
        and ref >= THRESHOLDS["refusal"]
    )

    return EvalSummary(
        n=n,
        hit_at_3=hit_at_3,
        mrr=mrr,
        source_recall_at_3=src_recall,
        faithfulness=faith,
        relevance=relev,
        completeness=compl,
        refusal=ref,
        judge_total=total_judge,
        per_category=per_cat,
        threshold_pass=passed,
        failed_ids=sorted(set(failed)),
    )