# SPDX-License-Identifier: Apache-2.0
"""Search intent mapper for growth and category creation.

Maps query-level demand into action: content gap, competitor intercept,
category education, or paid/organic protection. Inputs can come from Search
Console exports, Google Trends, keyword tools, or CRM-attributed query tables.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.model_arbitration import arbitrate_model, estimate_record_tokens


def _num(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _pct_value(value: Any, default: float = 0.0) -> float:
    raw = _num(value, default)
    if 0 < raw <= 1:
        raw *= 100
    return max(0.0, min(100.0, raw))


def classify_intent(query: str, competitor_terms: list[str] | None = None) -> str:
    text = query.lower()
    competitor_terms = [term.lower() for term in competitor_terms or []]
    if any(term and term in text for term in competitor_terms) or " vs " in text or "alternative" in text:
        return "COMPETITOR_INTERCEPT"
    if any(term in text for term in ("pricing", "demo", "rfp", "vendor", "software", "platform", "tool", "solution")):
        return "BUYING_INTENT"
    if any(term in text for term in ("how to", "template", "best practice", "guide", "what is", "definition")):
        return "EDUCATION_DEMAND"
    if any(term in text for term in ("reduce", "improve", "fix", "risk", "problem", "forecast accuracy", "pipeline quality")):
        return "PROBLEM_DEMAND"
    return "CATEGORY_DEMAND"


def _expected_ctr(avg_position: float) -> float:
    if avg_position <= 1:
        return 25.0
    if avg_position <= 3:
        return 15.0
    if avg_position <= 5:
        return 8.0
    if avg_position <= 10:
        return 4.0
    return 1.5


def _priority_tier(score: int) -> str:
    if score >= 75:
        return "HIGH"
    if score >= 45:
        return "MEDIUM"
    return "LOW"


def score_query(row: dict[str, Any]) -> dict[str, Any]:
    query = str(row.get("query") or "")
    intent = classify_intent(query, row.get("competitor_terms"))
    impressions = max(0.0, _num(row.get("impressions")))
    clicks = max(0.0, _num(row.get("clicks")))
    ctr_pct = (clicks / impressions) * 100 if impressions > 0 else 0.0
    avg_position = _num(row.get("avg_position"), 100.0)
    expected_ctr_pct = _expected_ctr(avg_position)
    ctr_gap_pct = max(0.0, expected_ctr_pct - ctr_pct)
    cpc = _num(row.get("estimated_cpc"))
    difficulty_pct = _pct_value(row.get("difficulty_pct"), 50.0)
    business_fit_pct = _pct_value(row.get("business_fit_pct"), 50.0)
    conversion_rate_pct = _pct_value(row.get("conversion_rate"))
    win_rate_pct = _pct_value(row.get("deal_win_rate"))

    volume_score = min(100.0, math.log10(impressions + 1) * 25)
    conversion_score = min(100.0, conversion_rate_pct * 8 + win_rate_pct * 0.4)
    position_gap_score = 0.0 if avg_position <= 3 else min(100.0, (avg_position - 3) * 10)
    difficulty_score = 100.0 - difficulty_pct
    multiplier = {
        "BUYING_INTENT": 1.20,
        "COMPETITOR_INTERCEPT": 1.15,
        "PROBLEM_DEMAND": 1.05,
        "CATEGORY_DEMAND": 0.95,
        "EDUCATION_DEMAND": 0.80,
    }[intent]
    priority_score = round(
        min(
            100.0,
            (
                volume_score * 0.25
                + business_fit_pct * 0.25
                + conversion_score * 0.20
                + difficulty_score * 0.15
                + position_gap_score * 0.15
            )
            * multiplier,
        )
    )

    flags: list[dict[str, Any]] = []
    if impressions >= 1_000 and ctr_pct < expected_ctr_pct * 0.5:
        flags.append({"name": "SERP_MESSAGE_GAP", "evidence": f"ctr_pct={ctr_pct:.1f}; expected_ctr_pct={expected_ctr_pct:.1f}", "action": "Rewrite title, meta, and above-fold promise for the query intent."})
    if avg_position > 5 and business_fit_pct >= 70:
        flags.append({"name": "CONTENT_GAP", "evidence": f"avg_position={avg_position:.1f}; business_fit_pct={business_fit_pct:.1f}", "action": "Create or refresh a page that directly answers this query cluster."})
    if intent in {"BUYING_INTENT", "COMPETITOR_INTERCEPT"} and avg_position > 3:
        flags.append({"name": "BUYING_INTENT_UNDERCAPTURED", "evidence": f"intent={intent}; avg_position={avg_position:.1f}", "action": "Prioritize landing page, proof, and sales handoff before broad awareness content."})
    if cpc >= 20 and avg_position > 3:
        flags.append({"name": "HIGH_CPC_PROTECT_WITH_ORGANIC", "evidence": f"estimated_cpc={cpc:.2f}", "action": "Use organic content and proof assets to reduce paid dependency."})
    if business_fit_pct < 40 and impressions >= 2_000:
        flags.append({"name": "LOW_FIT_DEMAND", "evidence": f"business_fit_pct={business_fit_pct:.1f}", "action": "Do not chase volume until the query maps to a winnable segment."})

    if intent == "COMPETITOR_INTERCEPT":
        recommended_action = "Build a factual alternatives/comparison asset and route matched accounts to competitive plays."
    elif "CONTENT_GAP" in {flag["name"] for flag in flags}:
        recommended_action = "Create or refresh content for this cluster before adding paid spend."
    elif "SERP_MESSAGE_GAP" in {flag["name"] for flag in flags}:
        recommended_action = "Fix search result messaging and landing-page promise."
    elif priority_score >= 75:
        recommended_action = "Promote to campaign backlog with sales handoff and ROI tracking."
    else:
        recommended_action = "Monitor as supporting demand signal."

    estimated_pipeline = _num(row.get("estimated_monthly_pipeline"))
    model_policy = arbitrate_model(
        "search_intent_mapper",
        estimated_input_tokens=estimate_record_tokens(row),
        high_stakes=estimated_pipeline >= 250_000 or priority_score >= 85,
        evidence_conflict=bool(row.get("evidence_conflict")),
    )

    return {
        "query": query,
        "intent": intent,
        "priority_score": priority_score,
        "priority_tier": _priority_tier(priority_score),
        "impressions": round(impressions),
        "ctr_pct": round(ctr_pct, 1),
        "expected_ctr_pct": round(expected_ctr_pct, 1),
        "avg_position": round(avg_position, 1),
        "business_fit_pct": round(business_fit_pct, 1),
        "flags": flags,
        "recommended_action": recommended_action,
        "model_policy": model_policy,
        "draft_note": "Draft for reviewer judgment. Search demand is a leading indicator, not proof of closed revenue.",
    }


def score_queries(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [score_query(row) for row in rows]
    return {
        "queries": sorted(scored, key=lambda row: row["priority_score"], reverse=True),
        "high_priority": sum(1 for row in scored if row["priority_tier"] == "HIGH"),
        "competitor_intercepts": sum(1 for row in scored if row["intent"] == "COMPETITOR_INTERCEPT"),
        "content_gaps": sum(1 for row in scored for flag in row["flags"] if flag["name"] == "CONTENT_GAP"),
    }


def _demo() -> None:
    samples = [
        {
            "query": "pipeline forecast accuracy software",
            "impressions": 8_500,
            "clicks": 140,
            "avg_position": 7.2,
            "estimated_cpc": 28,
            "difficulty_pct": 42,
            "business_fit_pct": 88,
            "conversion_rate": 0.045,
            "deal_win_rate": 0.22,
            "estimated_monthly_pipeline": 180_000,
        },
        {
            "query": "gong alternative revenue intelligence",
            "competitor_terms": ["gong"],
            "impressions": 2_400,
            "clicks": 35,
            "avg_position": 8.0,
            "estimated_cpc": 35,
            "difficulty_pct": 55,
            "business_fit_pct": 82,
            "conversion_rate": 0.035,
            "deal_win_rate": 0.18,
        },
    ]
    print("search_intent_mapper - demo run")
    for row in score_queries(samples)["queries"]:
        print(f"{row['query']}: {row['priority_tier']} {row['priority_score']} intent={row['intent']} model={row['model_policy']['selected_model']}")
        for flag in row["flags"][:3]:
            print(f"  - {flag['name']}: {flag['action']}")


if __name__ == "__main__":
    _demo()
