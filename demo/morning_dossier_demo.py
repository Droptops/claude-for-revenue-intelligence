# SPDX-License-Identifier: Apache-2.0
"""Run a local synthetic morning dossier demo."""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path
from typing import Any

from synthetic_data import (
    ACCOUNTS,
    AVG_CYCLE_DAYS,
    BOARD_CONSTRAINT_SET_A,
    BOARD_CONSTRAINT_SET_B,
    OPPORTUNITIES,
    PERSONAS,
    PRE_ANNOUNCEMENT,
    TRIGGER_EVENTS,
)


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


aq_scorer = load_module(
    "demo_aq_scorer",
    "agents/anti_qualification_scorer/aq_scorer.py",
)
best_next_first_dollar = load_module(
    "demo_best_next_first_dollar",
    "plugins/ae/best_next_first_dollar.py",
)
board_vs_plan_scorer = load_module(
    "demo_board_vs_plan_scorer",
    "plugins/sales-leadership/board_vs_plan_scorer.py",
)


def by_account(rows: list[dict[str, Any]], account_id: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("account_id") == account_id]


def score_anti_qualification(opportunities: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    scored: dict[str, dict[str, Any]] = {}
    for opp in opportunities:
        scored[opp["opportunity_id"]] = aq_scorer.score_opportunity(
            opp["opportunity_id"],
            opp["consulting_spend"],
            opp["implementation_spend"],
            data_source=opp["data_source"],
        )
    return scored


def rank_open_opportunities(
    opportunities: list[dict[str, Any]],
    aq_scores: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    scorer_inputs = []
    for opp in opportunities:
        if opp["outcome"] != "OPEN":
            continue
        scorer_inputs.append(
            {
                "opportunity_id": opp["opportunity_id"],
                "days_in_stage": opp["days_in_stage"],
                "anti_qualification_ratio": aq_scores[opp["opportunity_id"]][
                    "anti_qualification_ratio"
                ],
                "clone_profile_match": opp["clone_profile_match"],
                "trigger_event_count": opp["trigger_event_count"],
                "persona_coverage_score": opp["persona_coverage_score"],
                "outcome_signal": opp["outcome_signal"],
            }
        )
    return best_next_first_dollar.rank_opportunities(scorer_inputs)


def persona_gaps(personas: list[dict[str, Any]]) -> list[str]:
    gaps: list[str] = []
    tier_one = [p for p in personas if p["influence_tier"] == 1]
    if not any(
        p["role_label"] == "economic buyer" and p["engagement_status"] == "ENGAGED"
        for p in tier_one
    ):
        gaps.append("Economic buyer unidentified or not engaged.")
    for persona in tier_one:
        if persona["engagement_status"] in {"DARK", "UNCONTACTED"}:
            last_touch = persona["last_touch_days"]
            if last_touch is None:
                detail = "no recorded touch"
            else:
                detail = f"last touch {last_touch}d"
            gaps.append(
                f"Tier-1 contact [{persona['person_id']}] status: "
                f"{persona['engagement_status']} ({detail})."
            )
    return gaps


def funnel_outliers(opportunities: list[dict[str, Any]]) -> list[str]:
    outliers: list[str] = []
    threshold = AVG_CYCLE_DAYS * 1.5
    for opp in opportunities:
        if opp["outlier_flag"]:
            outliers.append(
                f"outlier_flag=true on {opp['opportunity_id']}: "
                f"reason \"{opp['outlier_reason']}\"."
            )
        elif opp["days_in_stage"] > threshold and opp["outcome"] == "OPEN":
            outliers.append(
                f"{opp['opportunity_id']} in stage {opp['stage']} for "
                f"{opp['days_in_stage']} days (avg cycle {AVG_CYCLE_DAYS}d)."
            )
    return outliers


def format_bullets(items: list[str], indent: str = "    ") -> list[str]:
    if not items:
        return [f"{indent}- none"]
    return [f"{indent}- {item}" for item in items]


def format_trigger_events(events: list[dict[str, Any]]) -> list[str]:
    return format_bullets(
        [
            f"{event['signal_class']} / {event['signal_family']} "
            f"(conf {event['confidence_score']:.2f}): {event['signal_summary']}"
            for event in events
        ]
    )


def format_pre_announcement(account_id: str) -> list[str]:
    items: list[str] = []
    for row in PRE_ANNOUNCEMENT.get(account_id, []):
        if "skipped_domain" in row:
            items.append(f"skipped: {row['skipped_domain']} - {row['reason']}.")
        else:
            items.append(
                f"PRE_ANNOUNCEMENT signal on competitor category "
                f"\"{row['category']}\" (conf {row['confidence_score']:.2f}): "
                f"{row['signal_summary']}"
            )
    return format_bullets(items)


def format_anti_qualification(aq_scores: dict[str, dict[str, Any]]) -> list[str]:
    items: list[str] = []
    for opportunity_id, row in aq_scores.items():
        ratio = row["anti_qualification_ratio"]
        ratio_text = "undefined" if ratio is None else f"{ratio:.3f}"
        items.append(
            f"{opportunity_id}: {row['anti_qual_label']} "
            f"(ratio {ratio_text}, conf {row['confidence']})."
        )
    return format_bullets(items)


def format_best_next(ranked: list[dict[str, Any]]) -> list[str]:
    if not ranked:
        return format_bullets([])
    rows = []
    for rank, row in enumerate(ranked, start=1):
        rows.append(
            f"{rank}. {row['opportunity_id']} score {row['score']:.1f} "
            f"(conf {row['confidence']})."
        )
    return format_bullets(rows)


def board_delta_summary() -> str:
    open_opps = [opp for opp in OPPORTUNITIES if opp["outcome"] == "OPEN"]
    result = board_vs_plan_scorer.compute_board_delta(
        BOARD_CONSTRAINT_SET_A,
        BOARD_CONSTRAINT_SET_B,
        open_opps,
    )
    labels = {
        row["opportunity_id"]: row["delta_label"]
        for row in result["delta_opportunities"]
        if row["delta_label"] != "PASSED_BOTH"
    }
    if labels:
        deltas = ", ".join(f"{opp}: {label}" for opp, label in labels.items())
    else:
        deltas = "no deltas"
    return f"{result['summary']} Deltas: {deltas}."


def recommended_actions(
    account_rankings: dict[str, list[dict[str, Any]]],
    account_gaps: dict[str, list[str]],
) -> list[str]:
    actions: list[str] = []
    for account in ACCOUNTS:
        account_id = account["account_id"]
        ranked = account_rankings.get(account_id, [])
        gaps = account_gaps.get(account_id, [])
        if gaps:
            actions.append(f"{account_id} - review persona gap: {gaps[0]}")
        elif ranked:
            actions.append(
                f"{account_id} - inspect top ranked open opportunity "
                f"{ranked[0]['opportunity_id']} before outreach."
            )
    return actions


def compose_dossier() -> str:
    lines = [
        f"Morning dossier - {date.today().isoformat()}",
        "Accounts in focus: "
        + ", ".join(account["account_id"] for account in ACCOUNTS),
        "",
    ]
    account_rankings: dict[str, list[dict[str, Any]]] = {}
    account_gaps: dict[str, list[str]] = {}

    for account in ACCOUNTS:
        account_id = account["account_id"]
        opportunities = by_account(OPPORTUNITIES, account_id)
        personas = by_account(PERSONAS, account_id)
        events = by_account(TRIGGER_EVENTS, account_id)
        aq_scores = score_anti_qualification(opportunities)
        ranked = rank_open_opportunities(opportunities, aq_scores)
        gaps = persona_gaps(personas)
        account_rankings[account_id] = ranked
        account_gaps[account_id] = gaps

        lines.extend(
            [
                f"[{account_id}]",
                "  Account shape:",
                f"    - segment {account['segment']}; motion {account['motion']}; "
                f"observable size band {account['observable_size_band']}.",
                "  Trigger events (last 24h):",
                *format_trigger_events(events),
                "  Persona gaps:",
                *format_bullets(gaps),
                "  Funnel outliers:",
                *format_bullets(funnel_outliers(opportunities)),
                "  Anti-qualification:",
                *format_anti_qualification(aq_scores),
                "  Best next first dollar:",
                *format_best_next(ranked),
                "  Pre-announcement:",
                *format_pre_announcement(account_id),
                "",
            ]
        )

    lines.extend(
        [
            "Board-vs-plan delta (synthetic constraints):",
            f"  - {board_delta_summary()}",
            "",
            "Recommended next actions (drafts; reviewer approves before sending):",
        ]
    )
    for index, action in enumerate(recommended_actions(account_rankings, account_gaps), start=1):
        lines.append(f"  {index}. {action}")
    lines.extend(
        [
            "",
            "Draft for reviewer judgment. Verify against source data before acting.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    print(compose_dossier())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
