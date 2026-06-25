"""报告输出：控制台 + markdown + JSON 三档。"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from tests.rag_eval.metrics import EvalRecord, EvalSummary, THRESHOLDS


REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def _fmt(v: float) -> str:
    return f"{v:.2f}"


def _pass(v: float, threshold: float) -> str:
    # 用 ASCII 字符，避开 Windows gbk 控制台编码坑（文件里再用 unicode）
    return "PASS" if v >= threshold else "FAIL"


def _now() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _console_summary(s: EvalSummary) -> str:
    lines = [
        "",
        "=" * 70,
        f"  RAG 评估汇总 (n={s.n})",
        "=" * 70,
        f"  Hit@3              {_fmt(s.hit_at_3)}    >= {THRESHOLDS['hit_at_3']:.2f}    {_pass(s.hit_at_3, THRESHOLDS['hit_at_3'])}",
        f"  MRR                {_fmt(s.mrr)}    >= {THRESHOLDS['mrr']:.2f}    {_pass(s.mrr, THRESHOLDS['mrr'])}",
        f"  Source Recall@3    {_fmt(s.source_recall_at_3)}    >= {THRESHOLDS['source_recall_at_3']:.2f}    {_pass(s.source_recall_at_3, THRESHOLDS['source_recall_at_3'])}",
        f"  faithfulness       {_fmt(s.faithfulness)}    >= {THRESHOLDS['faithfulness']:.2f}    {_pass(s.faithfulness, THRESHOLDS['faithfulness'])}",
        f"  relevance          {_fmt(s.relevance)}    >= {THRESHOLDS['relevance']:.2f}    {_pass(s.relevance, THRESHOLDS['relevance'])}",
        f"  completeness       {_fmt(s.completeness)}    >= {THRESHOLDS['completeness']:.2f}    {_pass(s.completeness, THRESHOLDS['completeness'])}",
        f"  refusal            {_fmt(s.refusal)}    >= {THRESHOLDS['refusal']:.2f}    {_pass(s.refusal, THRESHOLDS['refusal'])}",
        "-" * 70,
        f"  Judge total        {_fmt(s.judge_total)}",
        f"  Overall threshold: {'PASS' if s.threshold_pass else 'FAIL'}",
    ]
    if s.failed_ids:
        lines.append(f"  Failed samples: {', '.join(s.failed_ids)}")
    lines.append("=" * 70)
    return "\n".join(lines)


def _markdown(s: EvalSummary, records: List[EvalRecord], model: str, concurrency: int, total_ms: int) -> str:
    md = [
        "# RAG 评估报告",
        "",
        f"- 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 样本数：{s.n}",
        f"- 评估模型：{model}",
        f"- 并发度：{concurrency}",
        f"- 总耗时：{total_ms / 1000:.1f}s",
        "",
        "## 总览",
        "",
        "| 指标 | 值 | 阈值 | 通过 |",
        "|---|---|---|---|",
        f"| Hit@3 | {_fmt(s.hit_at_3)} | >= {THRESHOLDS['hit_at_3']:.2f} | {'PASS' if s.hit_at_3 >= THRESHOLDS['hit_at_3'] else 'FAIL'} |",
        f"| MRR | {_fmt(s.mrr)} | >= {THRESHOLDS['mrr']:.2f} | {'PASS' if s.mrr >= THRESHOLDS['mrr'] else 'FAIL'} |",
        f"| Source Recall@3 | {_fmt(s.source_recall_at_3)} | >= {THRESHOLDS['source_recall_at_3']:.2f} | {'PASS' if s.source_recall_at_3 >= THRESHOLDS['source_recall_at_3'] else 'FAIL'} |",
        f"| faithfulness | {_fmt(s.faithfulness)} | >= {THRESHOLDS['faithfulness']:.2f} | {'PASS' if s.faithfulness >= THRESHOLDS['faithfulness'] else 'FAIL'} |",
        f"| relevance | {_fmt(s.relevance)} | >= {THRESHOLDS['relevance']:.2f} | {'PASS' if s.relevance >= THRESHOLDS['relevance'] else 'FAIL'} |",
        f"| completeness | {_fmt(s.completeness)} | >= {THRESHOLDS['completeness']:.2f} | {'PASS' if s.completeness >= THRESHOLDS['completeness'] else 'FAIL'} |",
        f"| refusal | {_fmt(s.refusal)} | >= {THRESHOLDS['refusal']:.2f} | {'PASS' if s.refusal >= THRESHOLDS['refusal'] else 'FAIL'} |",
        "",
        f"**Overall threshold: {'PASS' if s.threshold_pass else 'FAIL'}**",
        "",
        "## 按类别",
        "",
        "| 类别 | n | Hit@3 | faithfulness | relevance | completeness | refusal |",
        "|---|---|---|---|---|---|---|",
    ]
    for cat, m in sorted(s.per_category.items()):
        md.append(
            f"| {cat} | {int(m['n'])} | {_fmt(m['hit_at_3'])} | {_fmt(m['faithfulness'])} | {_fmt(m['relevance'])} | {_fmt(m['completeness'])} | {_fmt(m['refusal'])} |"
        )
    md.append("")
    md.append("## 失败样本详情（召回未命中 或 任何维度 <= 2）")
    md.append("")
    failed_records = [
        r for r in records
        if (not r.hit_at_3 and not r.sample.expect_refuse)
        or any(r.judge_scores.get(d, 5) <= 2 for d in ("faithfulness", "relevance", "completeness", "refusal"))
        or r.parse_error
    ]
    if not failed_records:
        md.append("_(none)_")
    for r in failed_records:
        md.append(f"### {r.sample.id} {r.sample.category}/{r.sample.difficulty}")
        md.append(f"- 问题：{r.sample.question}")
        md.append(f"- 期望 source：`{r.sample.source or '（拒答）'}`")
        md.append(f"- 命中：{'PASS' if r.hit_at_3 else 'FAIL'} (MRR={_fmt(r.reciprocal_rank)})")
        md.append(f"- RAG 答案：{r.rag_answer[:300]}{'...' if len(r.rag_answer) > 300 else ''}")
        md.append(f"- Judge 分数：{r.judge_scores}")
        md.append(f"- Judge 理由：{r.judge_reason}")
        if r.parse_error:
            md.append("- **Judge 解析失败，已用全 1 分兜底**")
        md.append("")
    md.append("## 全量样本明细")
    md.append("")
    md.append("| ID | 类别 | 难度 | Hit@3 | Faith | Rel | Compl | Refuse | 耗时(ms) |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for r in records:
        sc = r.judge_scores
        md.append(
            f"| {r.sample.id} | {r.sample.category} | {r.sample.difficulty} | "
            f"{'PASS' if r.hit_at_3 else 'FAIL'} | "
            f"{sc.get('faithfulness', '-')} | {sc.get('relevance', '-')} | "
            f"{sc.get('completeness', '-')} | {sc.get('refusal', '-')} | "
            f"{r.latency_ms} |"
        )
    return "\n".join(md)


def _json(s: EvalSummary, records: List[EvalRecord], model: str, concurrency: int, total_ms: int) -> dict:
    return {
        "meta": {
            "time": datetime.now().isoformat(timespec="seconds"),
            "n": s.n,
            "model": model,
            "concurrency": concurrency,
            "total_ms": total_ms,
            "thresholds": THRESHOLDS,
        },
        "summary": {
            "hit_at_3": s.hit_at_3,
            "mrr": s.mrr,
            "source_recall_at_3": s.source_recall_at_3,
            "faithfulness": s.faithfulness,
            "relevance": s.relevance,
            "completeness": s.completeness,
            "refusal": s.refusal,
            "judge_total": s.judge_total,
            "per_category": s.per_category,
            "threshold_pass": s.threshold_pass,
            "failed_ids": s.failed_ids,
        },
        "records": [
            {
                "id": r.sample.id,
                "category": r.sample.category,
                "difficulty": r.sample.difficulty,
                "question": r.sample.question,
                "expect_refuse": r.sample.expect_refuse,
                "hit_at_3": r.hit_at_3,
                "reciprocal_rank": r.reciprocal_rank,
                "source_recall_at_3": r.source_recall_at_3,
                "retrieved_docs": r.retrieved_docs,
                "rag_answer": r.rag_answer,
                "judge_scores": r.judge_scores,
                "judge_reason": r.judge_reason,
                "parse_error": r.parse_error,
                "latency_ms": r.latency_ms,
            }
            for r in records
        ],
    }


def write(
    records: List[EvalRecord],
    summary: EvalSummary,
    *,
    model: str = "unknown",
    concurrency: int = 5,
    total_ms: int = 0,
) -> None:
    """三档输出：控制台 + md + json 到 reports/。"""
    console_text = _console_summary(summary)
    # 控制台可能 gbk，把 unicode 符号替换成 ASCII 保险
    try:
        print(console_text)
    except UnicodeEncodeError:
        print(console_text.encode("ascii", "replace").decode("ascii"))

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = _now()
    md_path = REPORTS_DIR / f"eval_{ts}.md"
    json_path = REPORTS_DIR / f"eval_{ts}.json"

    md_path.write_text(_markdown(summary, records, model, concurrency, total_ms), encoding="utf-8")
    json_path.write_text(
        json.dumps(_json(summary, records, model, concurrency, total_ms), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    try:
        print(f"\nMarkdown: {md_path}")
        print(f"JSON:     {json_path}")
    except UnicodeEncodeError:
        print(f"\nMarkdown: {md_path}")
        print(f"JSON:     {json_path}")