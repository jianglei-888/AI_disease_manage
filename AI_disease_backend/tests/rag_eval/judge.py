"""LLM-as-Judge：给定 question / context / reference / answer，返回 4 维度分数。

prompt 模板要点：
- 拒答场景特别提示（reference="" 时只看是否拒答）
- 严格输出格式（4 个维度各一行 + 理由），便于解析
- 解析失败兜底（parse_error 标记，让失败可见）
"""
from __future__ import annotations

import re
from typing import Dict, Tuple


JUDGE_PROMPT = """你是一名严谨的医疗 RAG 评估员。请根据【参考信息】和【参考标准答案】，对【待评估答案】在 4 个维度上打分（1~5 分）。

【问题】
{question}

【检索到的知识库内容】（RAG 喂给 LLM 的上下文）
{context}

【参考标准答案】
{reference}

【待评估答案】
{answer}

【特别提示：拒答场景】
- 如果【参考标准答案】为空字符串 ""，表示这是一道库外题/拒答题。
- 这种情况下：若【待评估答案】表达了"无相关信息 / 请咨询医生 / 暂未收录" → Refusal Accuracy 给 5 分；若胡编乱造 → 给 1 分。
- 其他三维度（忠实性/相关性/完整性）只考察答案在"已知知识范围内"的合理性。

【4 个维度定义】
1. Faithfulness（忠实性）：答案是否严格依据【检索到的知识库内容】，无编造具体药物名/剂量/禁忌。
2. Relevance（相关性）：答案是否直接回答问题，无偏题。
3. Completeness（完整性）：答案是否覆盖【参考标准答案】中的核心要点。
4. Refusal Accuracy（拒答准确）：该拒答时是否拒答；不该拒答时是否给了实质性回答。

【输出格式（严格遵守）】
忠实性：<1~5>
相关性：<1~5>
完整性：<1~5>
拒答准确：<1~5>
理由：<一句话说明>"""


_DIMS = ("faithfulness", "relevance", "completeness", "refusal")
_CN2KEY = {
    "忠实性": "faithfulness",
    "相关性": "relevance",
    "完整性": "completeness",
    "拒答准确": "refusal",
}


def _parse(resp: str) -> Tuple[Dict[str, int], str]:
    """从 LLM 响应里抽 4 个维度分数 + 理由。"""
    scores: Dict[str, int] = {}
    reason = ""

    for line in resp.splitlines():
        line = line.strip()
        if not line:
            continue
        for cn, key in _CN2KEY.items():
            if line.startswith(cn):
                m = re.search(r"(\d)", line)
                if m:
                    val = int(m.group(1))
                    scores[key] = max(1, min(5, val))
                break
        if line.startswith("理由"):
            reason = line.split("：", 1)[-1].strip() or line.split(":", 1)[-1].strip()

    if len(scores) != 4:
        return {}, "parse_error"

    return scores, reason or "ok"


def judge_answer(
    llm,
    question: str,
    context: str,
    reference: str,
    answer: str,
) -> Tuple[Dict[str, int], str, bool]:
    """调用 LLM 打分。

    返回 (scores_dict, reason, parse_error)。
    parse_error=True 时 scores_dict 为空，调用方应用全 1 分兜底。
    """
    prompt = JUDGE_PROMPT.format(
        question=question,
        context=context or "（无检索结果）",
        reference=reference or "（无标准答案 — 拒答场景）",
        answer=answer,
    )
    resp = llm.invoke(prompt).content
    scores, reason = _parse(resp)
    if not scores:
        return {}, "parse_error", True
    return scores, reason, False