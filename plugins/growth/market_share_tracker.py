# SPDX-License-Identifier: Apache-2.0
"""Market-share and category-demand tracker.

This is deliberately not a call analytics workflow. It watches whether a
company is winning, defending, or undercapturing a specific market segment by
combining revenue share, share-of-search proxy, account coverage, and
high-intent account capture.
"""

from __future__ import annotations

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


def _bounded(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def _pct(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return _bounded((numerator / denominator) * 100)


def _status(rule_score: int, market_share_pct: float, demand_share_pct: float, threshold: float) -> str:
    if market_share_pct >= threshold and demand_share_pct >= threshold:
        return "CATEGORY_LEADER"
    if market_share_pct >= threshold and demand_share_pct < threshold:
        return "DEFEND_LEAD"
    if rule_score >= threshold or market_share_pct >= 40 or demand_share_pct >= threshold:
        return "CONTENDER"
    return "BUILD_DEMAND"


def assess_segment(segment: dict[str, Any], *, rule_threshold_pct: float = 60.0) -> dict[str, Any]:
    """Assess one market segment against rule-of-60 ownership signals."""
    company_revenue = _num(segment.get("company_revenue"))
    market_revenue = _num(segment.get("market_revenue"))
    explicit_share = segment.get("market_share_pct")
    market_share_pct = _bounded(_num(explicit_share) if explicit_share is not None else _pct(company_revenue, market_revenue))

    brand_search = _num(segment.get("brand_search_volume"))
    competitor_search = _num(segment.get("competitor_search_volume"))
    category_search = _num(segment.get("category_search_volume"))
    search_denominator = category_search if category_search > 0 else brand_search + competitor_search
    demand_share_pct = _pct(brand_search, search_denominator)

    target_accounts = _num(segment.get("target_account_count"))
    active_accounts = _num(segment.get("active_account_count"))
    account_coverage_pct = _pct(active_accounts, target_accounts)

    high_intent_accounts = _num(segment.get("high_intent_accounts"))
    captured_high_intent_accounts = _num(segment.get("captured_high_intent_accounts"))
    high_intent_capture_pct = _pct(captured_high_intent_accounts, high_intent_accounts)

    company_growth_pct = _num(segment.get("company_growth_pct"))
    market_growth_pct = _num(segment.get("market_growth_pct"))
    growth_gap_pct = company_growth_pct - market_growth_pct

    rule_score = round(
        market_share_pct * 0.30
        + demand_share_pct * 0.25
        + high_intent_capture_pct * 0.25
        + account_coverage_pct * 0.20
    )
    status = _status(rule_score, market_share_pct, demand_share_pct, rule_threshold_pct)

    flags: list[dict[str, Any]] = []
    if market_share_pct < rule_threshold_pct:
        flags.append(
            {
                "name": "RULE_OF_60_GAP",
                "evidence": f"market_share_pct={market_share_pct:.1f}",
                "action": "Pick the subsegment where demand share, account coverage, and sales capacity can plausibly reach 60 percent first.",
            }
        )
    if demand_share_pct >= market_share_pct + 10:
        flags.append(
            {
                "name": "DEMAND_OUTRUNS_REVENUE",
                "evidence": f"demand_share_pct={demand_share_pct:.1f}; market_share_pct={market_share_pct:.1f}",
                "action": "Route high-intent accounts into a named acquisition motion before demand converts elsewhere.",
            }
        )
    if market_share_pct >= rule_threshold_pct and demand_share_pct + 10 < market_share_pct:
        flags.append(
            {
                "name": "BRAND_SHARE_LAG",
                "evidence": f"market_share_pct={market_share_pct:.1f}; demand_share_pct={demand_share_pct:.1f}",
                "action": "Protect the lead with category narrative, analyst proof, and competitive search coverage.",
            }
        )
    if account_coverage_pct < 50 and target_accounts > 0:
        flags.append(
            {
                "name": "LOW_ACCOUNT_COVERAGE",
                "evidence": f"account_coverage_pct={account_coverage_pct:.1f}",
                "action": "Add named-account coverage before increasing broad media spend.",
            }
        )
    if high_intent_capture_pct < 50 and high_intent_accounts > 0:
        flags.append(
            {
                "name": "LOW_HIGH_INTENT_CAPTURE",
                "evidence": f"high_intent_capture_pct={high_intent_capture_pct:.1f}",
                "action": "Create a fast-lane play for high-intent accounts that are already in market.",
            }
        )
    if growth_gap_pct < -5:
        flags.append(
            {
                "name": "MARKET_GROWTH_DRAG",
                "evidence": f"company_growth_pct={company_growth_pct:.1f}; market_growth_pct={market_growth_pct:.1f}",
                "action": "Inspect whether losses are pricing, channel, positioning, or segment-selection problems.",
            }
        )
    if len(segment.get("confidence_sources") or []) < 2:
        flags.append(
            {
                "name": "INSUFFICIENT_SOURCE_DIVERSITY",
                "evidence": "fewer than two independent demand/share sources",
                "action": "Validate with a second source before using this in a board or budget decision.",
            }
        )

    recommended_motion = {
        "CATEGORY_LEADER": "Defend the lead with proof, conversion capture, and retention expansion.",
        "DEFEND_LEAD": "Treat brand/search weakness as an early-warning system for share loss.",
        "CONTENDER": "Concentrate spend and sales capacity on the subsegment most likely to cross 60 percent.",
        "BUILD_DEMAND": "Build category education and proof before scaling acquisition spend.",
    }[status]

    model_policy = arbitrate_model(
        "market_share_tracker",
        estimated_input_tokens=estimate_record_tokens(segment),
        high_stakes=bool(segment.get("board_visible")) or (market_revenue >= 10_000_000 and market_share_pct >= 50),
        evidence_conflict=bool(segment.get("evidence_conflict")),
    )

    return {
        "segment_id": segment.get("segment_id"),
        "segment_name": segment.get("segment_name"),
        "rule_of_60_score": rule_score,
        "rule_threshold_pct": rule_threshold_pct,
        "status": status,
        "market_share_pct": round(market_share_pct, 1),
        "demand_share_pct": round(demand_share_pct, 1),
        "account_coverage_pct": round(account_coverage_pct, 1),
        "high_intent_capture_pct": round(high_intent_capture_pct, 1),
        "growth_gap_pct": round(growth_gap_pct, 1),
        "flags": flags,
        "recommended_motion": recommended_motion,
        "model_policy": model_policy,
        "draft_note": "Draft for reviewer judgment. Rule-of-60 is a configurable operating heuristic, not a universal market law.",
    }


def assess_market(segments: list[dict[str, Any]], *, rule_threshold_pct: float = 60.0) -> dict[str, Any]:
    rows = [assess_segment(segment, rule_threshold_pct=rule_threshold_pct) for segment in segments]
    return {
        "segments": rows,
        "category_leaders": sum(1 for row in rows if row["status"] == "CATEGORY_LEADER"),
        "contenders": sum(1 for row in rows if row["status"] == "CONTENDER"),
        "rule_of_60_gaps": sum(1 for row in rows for flag in row["flags"] if flag["name"] == "RULE_OF_60_GAP"),
    }


def _demo() -> None:
    samples = [
        {
            "segment_id": "SEG-AI-REVOPS",
            "segment_name": "AI RevOps for enterprise SaaS",
            "market_share_pct": 54,
            "brand_search_volume": 13_000,
            "competitor_search_volume": 7_000,
            "target_account_count": 200,
            "active_account_count": 82,
            "high_intent_accounts": 40,
            "captured_high_intent_accounts": 14,
            "company_growth_pct": 18,
            "market_growth_pct": 28,
            "market_revenue": 12_000_000,
            "confidence_sources": ["crm_win_loss", "search_console"],
        },
        {
            "segment_id": "SEG-FORECAST",
            "segment_name": "Forecast inspection",
            "market_share_pct": 66,
            "brand_search_volume": 9_000,
            "competitor_search_volume": 18_000,
            "target_account_count": 120,
            "active_account_count": 90,
            "high_intent_accounts": 35,
            "captured_high_intent_accounts": 29,
            "company_growth_pct": 12,
            "market_growth_pct": 8,
            "confidence_sources": ["crm_win_loss", "analyst_share", "search_console"],
        },
    ]
    print("market_share_tracker - demo run")
    for row in assess_market(samples)["segments"]:
        print(f"{row['segment_id']}: {row['status']} score={row['rule_of_60_score']} market={row['market_share_pct']} demand={row['demand_share_pct']} model={row['model_policy']['selected_model']}")
        for flag in row["flags"][:3]:
            print(f"  - {flag['name']}: {flag['action']}")


if __name__ == "__main__":
    _demo()
