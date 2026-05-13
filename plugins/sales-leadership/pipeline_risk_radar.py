# SPDX-License-Identifier: Apache-2.0
"""Pipeline risk radar.

Deterministic deal-risk scoring for forecast and pipeline inspection. It is
designed to sit on top of CRM, activity, persona, authority, and conversation
evidence. The score is not a forecast; it is a triage queue for managers and
reps.
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


def _flag(name: str, points: int, evidence: str, action: str) -> dict[str, Any]:
    return {"name": name, "points": points, "evidence": evidence, "recommended_action": action}


def assess_opportunity(opp: dict[str, Any], *, as_of: str | None = None) -> dict[str, Any]:
    """Assess one opportunity and return risk flags plus model policy."""
    today = _parse_date(as_of) or date.today()
    close_date = _parse_date(opp.get("close_date"))
    flags: list[dict[str, Any]] = []

    next_step_age = opp.get("next_step_age_days")
    if next_step_age is None or int(next_step_age) > 14:
        flags.append(_flag(
            "NEXT_STEP_STALE",
            18,
            f"next_step_age_days={next_step_age}",
            "Confirm a dated next step with the buyer and attach it to the opportunity.",
        ))

    last_activity_days = int(opp.get("last_activity_days", 0))
    if last_activity_days > 14:
        flags.append(_flag(
            "LOW_RECENT_ENGAGEMENT",
            16,
            f"last_activity_days={last_activity_days}",
            "Re-open the thread with a value-specific reason or decommit the timing.",
        ))

    if close_date is None:
        flags.append(_flag(
            "MISSING_CLOSE_DATE",
            12,
            "close_date is missing or invalid",
            "Set a close date or move the deal out of forecast inspection.",
        ))
    elif close_date < today:
        flags.append(_flag(
            "PAST_CLOSE_DATE",
            24,
            f"close_date={close_date.isoformat()} as_of={today.isoformat()}",
            "Update close date and require manager review before it remains in commit.",
        ))

    if int(opp.get("close_date_slip_count", 0)) >= 2:
        flags.append(_flag(
            "REPEATED_SLIP",
            12,
            f"close_date_slip_count={opp.get('close_date_slip_count')}",
            "Ask for a mutual action plan with buyer-owned dates.",
        ))

    coverage = float(opp.get("persona_coverage_score", 0.0))
    if coverage < 0.5:
        flags.append(_flag(
            "LOW_PERSONA_COVERAGE",
            12,
            f"persona_coverage_score={coverage}",
            "Map economic buyer, champion, blocker, and signer before next forecast call.",
        ))

    if not bool(opp.get("champion_confirmed")):
        flags.append(_flag(
            "NO_CONFIRMED_CHAMPION",
            14,
            "champion_confirmed=false",
            "Validate whether the named champion can create internal urgency.",
        ))

    if not bool(opp.get("economic_buyer_confirmed")):
        flags.append(_flag(
            "NO_ECONOMIC_BUYER",
            12,
            "economic_buyer_confirmed=false",
            "Find the person who owns budget and success criteria.",
        ))

    if not bool(opp.get("signatory_verified")):
        flags.append(_flag(
            "SIGNATORY_UNVERIFIED",
            10,
            "signatory_verified=false",
            "Confirm who can sign and whether legal/procurement is already engaged.",
        ))

    anti_ratio = opp.get("anti_qualification_ratio")
    if anti_ratio is not None and float(anti_ratio) > 3.0:
        flags.append(_flag(
            "POLITICAL_COVER_PATTERN",
            16,
            f"anti_qualification_ratio={anti_ratio}",
            "Pressure-test whether the buyer is funding implementation or only buying cover.",
        ))

    if (opp.get("forecast_category") or "").upper() == "COMMIT" and flags:
        flags.append(_flag(
            "COMMIT_WITH_OPEN_RISK",
            10,
            "forecast_category=COMMIT and risk flags present",
            "Require a manager-visible exception note before keeping this in commit.",
        ))

    raw_score = min(100, sum(flag["points"] for flag in flags))
    if raw_score >= 60:
        tier = "HIGH"
    elif raw_score >= 30:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    token_decision = arbitrate_model(
        "pipeline_risk_radar",
        estimated_input_tokens=estimate_record_tokens(opp),
        high_stakes=(opp.get("forecast_category") or "").upper() == "COMMIT" and float(opp.get("amount", 0.0)) >= 250_000,
        evidence_conflict=bool(opp.get("evidence_conflict")),
    )

    return {
        "opportunity_id": opp.get("opportunity_id"),
        "account_id": opp.get("account_id"),
        "amount": float(opp.get("amount", 0.0)),
        "risk_score": raw_score,
        "risk_tier": tier,
        "risk_flags": flags,
        "top_recommended_actions": [flag["recommended_action"] for flag in flags[:3]],
        "model_policy": token_decision,
        "draft_note": "Draft for reviewer judgment. Risk score is a triage signal, not a forecast.",
    }


def assess_pipeline(opportunities: list[dict[str, Any]], *, as_of: str | None = None) -> dict[str, Any]:
    rows = [assess_opportunity(opp, as_of=as_of) for opp in opportunities]
    rows.sort(key=lambda row: (row["risk_score"], row["amount"]), reverse=True)
    high_risk = [row for row in rows if row["risk_tier"] == "HIGH"]
    medium_risk = [row for row in rows if row["risk_tier"] == "MEDIUM"]
    return {
        "opportunity_count": len(rows),
        "high_risk_count": len(high_risk),
        "medium_risk_count": len(medium_risk),
        "amount_at_high_risk": round(sum(row["amount"] for row in high_risk), 2),
        "rows": rows,
        "summary": (
            f"{len(high_risk)} high-risk and {len(medium_risk)} medium-risk "
            f"opportunities out of {len(rows)} inspected."
        ),
    }


def _demo() -> None:
    sample = [
        {
            "opportunity_id": "OPP-RISK",
            "account_id": "ACCT-1",
            "amount": 480_000,
            "forecast_category": "COMMIT",
            "close_date": "2026-05-01",
            "last_activity_days": 21,
            "next_step_age_days": 19,
            "close_date_slip_count": 2,
            "persona_coverage_score": 0.35,
            "champion_confirmed": False,
            "economic_buyer_confirmed": False,
            "signatory_verified": False,
            "anti_qualification_ratio": 3.6,
        },
        {
            "opportunity_id": "OPP-HEALTHY",
            "account_id": "ACCT-2",
            "amount": 90_000,
            "forecast_category": "BEST_CASE",
            "close_date": "2026-06-30",
            "last_activity_days": 3,
            "next_step_age_days": 2,
            "close_date_slip_count": 0,
            "persona_coverage_score": 0.8,
            "champion_confirmed": True,
            "economic_buyer_confirmed": True,
            "signatory_verified": True,
            "anti_qualification_ratio": 1.1,
        },
    ]
    result = assess_pipeline(sample, as_of="2026-05-13")
    print("pipeline_risk_radar - demo run")
    print(result["summary"])
    for row in result["rows"]:
        print(f"{row['opportunity_id']}: {row['risk_tier']} {row['risk_score']} model={row['model_policy']['selected_model']}")
        for flag in row["risk_flags"][:3]:
            print(f"  - {flag['name']}: {flag['recommended_action']}")


if __name__ == "__main__":
    _demo()
