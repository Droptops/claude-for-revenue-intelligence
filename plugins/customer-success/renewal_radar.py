# SPDX-License-Identifier: Apache-2.0
"""Renewal and expansion radar.

Turnkey retention triage for customer-success and revenue leadership. It
separates churn risk from expansion fit so a team does not confuse "save this"
with "grow this".
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.model_arbitration import arbitrate_model, estimate_record_tokens


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _tier(score: int) -> str:
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def assess_account(account: dict[str, Any], *, as_of: str | None = None) -> dict[str, Any]:
    today = _parse_date(as_of) or date.today()
    renewal_date = _parse_date(account.get("renewal_date"))
    churn_factors: list[dict[str, Any]] = []
    expansion_factors: list[dict[str, Any]] = []

    if renewal_date is None:
        churn_factors.append({"name": "MISSING_RENEWAL_DATE", "points": 12, "evidence": "renewal_date missing"})
    else:
        days_to_renewal = (renewal_date - today).days
        if days_to_renewal < 0:
            churn_factors.append({"name": "RENEWAL_DATE_PAST", "points": 25, "evidence": f"days_to_renewal={days_to_renewal}"})
        elif days_to_renewal <= 90:
            churn_factors.append({"name": "RENEWAL_WINDOW_OPEN", "points": 12, "evidence": f"days_to_renewal={days_to_renewal}"})

    usage_trend = (account.get("usage_trend") or "UNKNOWN").upper()
    if usage_trend == "DOWN":
        churn_factors.append({"name": "USAGE_DOWN", "points": 22, "evidence": "usage_trend=DOWN"})
    elif usage_trend == "UP":
        expansion_factors.append({"name": "USAGE_UP", "points": 22, "evidence": "usage_trend=UP"})

    support_trend = (account.get("support_ticket_trend") or "UNKNOWN").upper()
    if support_trend == "UP":
        churn_factors.append({"name": "SUPPORT_LOAD_UP", "points": 14, "evidence": "support_ticket_trend=UP"})
    elif support_trend == "DOWN":
        expansion_factors.append({"name": "SUPPORT_LOAD_DOWN", "points": 8, "evidence": "support_ticket_trend=DOWN"})

    if not bool(account.get("executive_sponsor_present")):
        churn_factors.append({"name": "NO_EXECUTIVE_SPONSOR", "points": 15, "evidence": "executive_sponsor_present=false"})
    else:
        expansion_factors.append({"name": "EXECUTIVE_SPONSOR_PRESENT", "points": 12, "evidence": "executive_sponsor_present=true"})

    if not bool(account.get("implementation_complete")):
        churn_factors.append({"name": "IMPLEMENTATION_INCOMPLETE", "points": 18, "evidence": "implementation_complete=false"})
    else:
        expansion_factors.append({"name": "IMPLEMENTATION_COMPLETE", "points": 10, "evidence": "implementation_complete=true"})

    renewal_signal = (account.get("renewal_signal") or "UNKNOWN").upper()
    if renewal_signal in {"WEAK", "UNKNOWN"}:
        churn_factors.append({"name": f"RENEWAL_SIGNAL_{renewal_signal}", "points": 12, "evidence": f"renewal_signal={renewal_signal}"})
    elif renewal_signal == "STRONG":
        expansion_factors.append({"name": "RENEWAL_SIGNAL_STRONG", "points": 14, "evidence": "renewal_signal=STRONG"})

    if bool(account.get("contract_diff_detected")):
        churn_factors.append({"name": "CONTRACT_DIFF", "points": 10, "evidence": "contract_diff_detected=true"})

    if (account.get("news_sentiment") or "NEUTRAL").upper() == "NEGATIVE":
        churn_factors.append({"name": "NEGATIVE_NEWS", "points": 10, "evidence": "news_sentiment=NEGATIVE"})

    trigger_events = max(0, int(account.get("trigger_event_count", 0)))
    if trigger_events >= 2:
        expansion_factors.append({"name": "MULTIPLE_TRIGGER_EVENTS", "points": 10, "evidence": f"trigger_event_count={trigger_events}"})

    churn_score = min(100, sum(factor["points"] for factor in churn_factors))
    expansion_score = min(100, sum(factor["points"] for factor in expansion_factors))
    model_policy = arbitrate_model(
        "renewal_expansion_radar",
        estimated_input_tokens=estimate_record_tokens(account),
        high_stakes=churn_score >= 60,
        evidence_conflict=bool(account.get("evidence_conflict")),
    )

    plays = []
    if churn_score >= 60:
        plays.append("Schedule executive sponsor inspection and produce a renewal-save brief.")
    if expansion_score >= 40 and churn_score < 60:
        plays.append("Draft expansion hypothesis tied to observed usage and trigger events.")
    if churn_score < 30 and expansion_score < 30:
        plays.append("Keep on standard renewal watch; no escalation signal detected.")

    return {
        "account_id": account.get("account_id"),
        "churn_risk_score": churn_score,
        "churn_risk_tier": _tier(churn_score),
        "expansion_score": expansion_score,
        "expansion_tier": _tier(expansion_score),
        "churn_factors": churn_factors,
        "expansion_factors": expansion_factors,
        "recommended_plays": plays,
        "model_policy": model_policy,
        "draft_note": "Draft for reviewer judgment. Separate save motions from expansion motions.",
    }


def _demo() -> None:
    samples = [
        {
            "account_id": "ACCT-SAVE",
            "renewal_date": "2026-06-30",
            "usage_trend": "DOWN",
            "support_ticket_trend": "UP",
            "executive_sponsor_present": False,
            "implementation_complete": False,
            "renewal_signal": "WEAK",
            "contract_diff_detected": True,
            "news_sentiment": "NEGATIVE",
        },
        {
            "account_id": "ACCT-GROW",
            "renewal_date": "2026-11-15",
            "usage_trend": "UP",
            "support_ticket_trend": "DOWN",
            "executive_sponsor_present": True,
            "implementation_complete": True,
            "renewal_signal": "STRONG",
            "trigger_event_count": 3,
        },
    ]
    print("renewal_radar - demo run")
    for account in samples:
        row = assess_account(account, as_of="2026-05-13")
        print(f"{row['account_id']}: churn={row['churn_risk_tier']} {row['churn_risk_score']} expansion={row['expansion_tier']} {row['expansion_score']} model={row['model_policy']['selected_model']}")
        for play in row["recommended_plays"]:
            print(f"  - {play}")


if __name__ == "__main__":
    _demo()
