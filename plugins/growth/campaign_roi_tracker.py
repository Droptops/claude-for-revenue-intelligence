# SPDX-License-Identifier: Apache-2.0
"""Campaign ROI and payback tracker.

The goal is to keep growth teams from celebrating vanity attribution when the
pipeline quality or CAC payback does not support scaling spend.
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


def _pct_value(value: Any, default: float = 0.0) -> float:
    raw = _num(value, default)
    if 0 < raw <= 1:
        raw *= 100
    return max(0.0, min(100.0, raw))


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def _campaign_decision(roi_pct: float | None, payback_months: float | None, quality_score: int, attribution_score: int) -> str:
    if roi_pct is not None and roi_pct < 0 and quality_score < 50:
        return "CUT_OR_REWORK"
    if attribution_score < 55:
        return "FIX_ATTRIBUTION"
    if roi_pct is not None and roi_pct >= 50 and quality_score >= 65 and (payback_months is None or payback_months <= 18):
        return "SCALE"
    return "KEEP_TESTING"


def assess_campaign(campaign: dict[str, Any]) -> dict[str, Any]:
    spend = _num(campaign.get("spend"))
    attributed_revenue = _num(campaign.get("attributed_revenue"))
    closed_won_revenue = _num(campaign.get("closed_won_revenue"))
    associated_deal_value = _num(campaign.get("associated_deal_value"))
    new_arr = _num(campaign.get("new_arr"), closed_won_revenue)
    gross_margin_pct = _pct_value(campaign.get("gross_margin_pct"), 75.0)
    gross_margin = gross_margin_pct / 100

    roi_basis = (campaign.get("roi_basis") or "attributed_revenue").lower()
    revenue_for_roi = {
        "attributed_revenue": attributed_revenue,
        "closed_won_revenue": closed_won_revenue,
        "associated_deal_value": associated_deal_value,
    }.get(roi_basis, attributed_revenue)

    roi_pct = None if spend <= 0 else ((revenue_for_roi - spend) / spend) * 100
    roas = _safe_ratio(revenue_for_roi, spend)
    gross_profit_after_spend = revenue_for_roi * gross_margin - spend
    monthly_gross_arr = (new_arr * gross_margin) / 12 if new_arr > 0 else 0
    payback_months = None if monthly_gross_arr <= 0 else spend / monthly_gross_arr

    target_match = _pct_value(campaign.get("target_account_match_rate"))
    sales_accepted = _pct_value(campaign.get("sales_accepted_rate"))
    opportunity_conversion = _pct_value(campaign.get("opportunity_conversion_rate"))
    persona_match = _pct_value(campaign.get("persona_match_rate"), target_match)
    quality_score = round(
        target_match * 0.30
        + sales_accepted * 0.30
        + min(100.0, opportunity_conversion * 4) * 0.25
        + persona_match * 0.15
    )

    attribution_score = 45
    attribution_score += 20 if campaign.get("holdout_or_geo_split_present") else 0
    attribution_score += 15 if campaign.get("offline_conversion_imported") else 0
    attribution_score += 10 if campaign.get("crm_campaign_ids_complete") else 0
    attribution_score += 10 if campaign.get("multi_touch_paths_available") else 0
    attribution_score -= 20 if campaign.get("view_through_only") else 0
    attribution_score -= 15 if spend <= 0 else 0
    attribution_score = max(0, min(100, attribution_score))

    flags: list[dict[str, Any]] = []
    if roi_pct is not None and roi_pct < 0:
        flags.append({"name": "NEGATIVE_ROI", "evidence": f"roi_pct={roi_pct:.1f}", "action": "Pause scale-up until creative, offer, or audience quality improves."})
    if payback_months is not None and payback_months > 18:
        flags.append({"name": "PAYBACK_TOO_LONG", "evidence": f"payback_months={payback_months:.1f}", "action": "Move budget toward channels with faster gross-margin payback."})
    if quality_score < 50:
        flags.append({"name": "LOW_PIPELINE_QUALITY", "evidence": f"quality_score={quality_score}", "action": "Inspect lead fit before trusting attributed revenue."})
    if attribution_score < 55:
        flags.append({"name": "ATTRIBUTION_WEAK", "evidence": f"attribution_score={attribution_score}", "action": "Fix campaign IDs, offline conversion import, or holdout design before reallocating budget."})
    if associated_deal_value < spend * 2 and closed_won_revenue <= 0:
        flags.append({"name": "SPEND_WITHOUT_PIPELINE", "evidence": f"associated_deal_value={associated_deal_value:.0f}; spend={spend:.0f}", "action": "Stop treating impressions or MQLs as a revenue proxy for this campaign."})
    if roas is not None and roas >= 3 and quality_score < 50:
        flags.append({"name": "HIGH_ROAS_LOW_QUALITY", "evidence": f"roas={roas:.2f}; quality_score={quality_score}", "action": "Audit whether conversion value is overstating low-fit demand."})

    decision = _campaign_decision(roi_pct, payback_months, quality_score, attribution_score)
    action = {
        "SCALE": "Scale with guardrails: preserve holdout measurement and watch payback.",
        "FIX_ATTRIBUTION": "Fix measurement before declaring a winner.",
        "CUT_OR_REWORK": "Cut or rework the campaign before more budget is committed.",
        "KEEP_TESTING": "Keep testing until ROI, payback, and pipeline quality align.",
    }[decision]

    model_policy = arbitrate_model(
        "campaign_roi_tracker",
        estimated_input_tokens=estimate_record_tokens(campaign),
        high_stakes=bool(campaign.get("board_visible")) or spend >= 250_000,
        evidence_conflict=(roi_pct is not None and roi_pct > 0 and quality_score < 50) or bool(campaign.get("evidence_conflict")),
    )

    return {
        "campaign_id": campaign.get("campaign_id"),
        "campaign_name": campaign.get("campaign_name"),
        "roi_basis": roi_basis,
        "roi_pct": None if roi_pct is None else round(roi_pct, 1),
        "roas": None if roas is None else round(roas, 2),
        "gross_profit_after_spend": round(gross_profit_after_spend, 2),
        "cac_payback_months": None if payback_months is None else round(payback_months, 1),
        "pipeline_quality_score": quality_score,
        "attribution_confidence_score": attribution_score,
        "decision": decision,
        "recommended_action": action,
        "flags": flags,
        "model_policy": model_policy,
        "draft_note": "Draft for reviewer judgment. ROI depends on the selected attribution basis and finance-owned spend inputs.",
    }


def assess_campaigns(campaigns: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [assess_campaign(campaign) for campaign in campaigns]
    return {
        "campaigns": rows,
        "scale": sum(1 for row in rows if row["decision"] == "SCALE"),
        "fix_attribution": sum(1 for row in rows if row["decision"] == "FIX_ATTRIBUTION"),
        "cut_or_rework": sum(1 for row in rows if row["decision"] == "CUT_OR_REWORK"),
    }


def _demo() -> None:
    samples = [
        {
            "campaign_id": "CMP-SEARCH-001",
            "campaign_name": "Category search capture",
            "spend": 80_000,
            "attributed_revenue": 260_000,
            "closed_won_revenue": 220_000,
            "new_arr": 220_000,
            "gross_margin_pct": 78,
            "target_account_match_rate": 0.82,
            "sales_accepted_rate": 0.74,
            "opportunity_conversion_rate": 0.18,
            "persona_match_rate": 0.80,
            "holdout_or_geo_split_present": True,
            "offline_conversion_imported": True,
            "crm_campaign_ids_complete": True,
            "multi_touch_paths_available": True,
        },
        {
            "campaign_id": "CMP-EVENT-002",
            "campaign_name": "Broad awareness event",
            "spend": 120_000,
            "attributed_revenue": 50_000,
            "associated_deal_value": 90_000,
            "new_arr": 30_000,
            "target_account_match_rate": 0.30,
            "sales_accepted_rate": 0.25,
            "opportunity_conversion_rate": 0.04,
            "crm_campaign_ids_complete": False,
        },
    ]
    print("campaign_roi_tracker - demo run")
    for row in assess_campaigns(samples)["campaigns"]:
        print(f"{row['campaign_id']}: {row['decision']} roi={row['roi_pct']} roas={row['roas']} payback={row['cac_payback_months']} model={row['model_policy']['selected_model']}")
        for flag in row["flags"][:3]:
            print(f"  - {flag['name']}: {flag['action']}")


if __name__ == "__main__":
    _demo()
