# SPDX-License-Identifier: Apache-2.0
"""Board-vs-plan delta scorer.

This is a deterministic constraint filter, not a constrained optimizer.
Real optimization (maximize expected revenue subject to constraints) is a
stretch goal. The scorer answers a narrower question: given two constraint
sets (e.g. "current plan" vs "board ask"), which opportunities pass each,
and where do the deltas fall?

Every output is a draft for reviewer judgment.
"""

from __future__ import annotations

from typing import Any


def _passes(opp: dict[str, Any], constraints: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return (passes, list of failed-constraint names)."""
    failed: list[str] = []

    min_deal_size = constraints.get("min_deal_size")
    if min_deal_size is not None and float(opp.get("deal_size", 0.0)) < float(min_deal_size):
        failed.append("min_deal_size")

    max_cycle_days = constraints.get("max_cycle_days")
    if max_cycle_days is not None and int(opp.get("cycle_days", 0)) > int(max_cycle_days):
        failed.append("max_cycle_days")

    if constraints.get("required_clone_match") and not bool(opp.get("clone_profile_match")):
        failed.append("required_clone_match")

    min_persona_coverage = constraints.get("min_persona_coverage")
    if min_persona_coverage is not None and float(opp.get("persona_coverage_score", 0.0)) < float(min_persona_coverage):
        failed.append("min_persona_coverage")

    return (len(failed) == 0, failed)


def _delta_label(passes_a: bool, passes_b: bool) -> str:
    if passes_a and passes_b:
        return "PASSED_BOTH"
    if passes_a and not passes_b:
        return "PASSED_A_ONLY"
    if not passes_a and passes_b:
        return "PASSED_B_ONLY"
    return "PASSED_NEITHER"


def compute_board_delta(
    constraint_set_a: dict[str, Any],
    constraint_set_b: dict[str, Any],
    opportunities: list[dict[str, Any]],
) -> dict[str, Any]:
    """Score opportunities under two constraint sets; surface the deltas.

    Constraint set keys (all optional):
        min_deal_size            float — USD floor
        max_cycle_days           int   — cycle-day ceiling
        required_clone_match     bool  — require clone_profile_match
        min_persona_coverage     float — persona_coverage_score floor

    Opportunity keys (operator-supplied):
        opportunity_id, deal_size, cycle_days, clone_profile_match,
        persona_coverage_score

    Returns:
        {
            "set_a_pass_count": int,
            "set_b_pass_count": int,
            "delta_opportunities": list[{
                "opportunity_id": str,
                "set_a_pass": bool,
                "set_b_pass": bool,
                "delta_label": str,
                "failed_in_a": list[str],
                "failed_in_b": list[str],
            }],
            "summary": str,
            "draft_note": str,
        }
    """
    rows: list[dict[str, Any]] = []
    set_a_pass_count = 0
    set_b_pass_count = 0
    bucket_counts = {"PASSED_BOTH": 0, "PASSED_A_ONLY": 0, "PASSED_B_ONLY": 0, "PASSED_NEITHER": 0}

    for opp in opportunities:
        passes_a, failed_a = _passes(opp, constraint_set_a)
        passes_b, failed_b = _passes(opp, constraint_set_b)
        label = _delta_label(passes_a, passes_b)
        bucket_counts[label] += 1
        if passes_a:
            set_a_pass_count += 1
        if passes_b:
            set_b_pass_count += 1
        rows.append({
            "opportunity_id": opp.get("opportunity_id"),
            "set_a_pass": passes_a,
            "set_b_pass": passes_b,
            "delta_label": label,
            "failed_in_a": failed_a,
            "failed_in_b": failed_b,
        })

    largest_bucket = max(bucket_counts, key=lambda k: bucket_counts[k])
    summary = (
        f"set A passed {set_a_pass_count}/{len(opportunities)}; "
        f"set B passed {set_b_pass_count}/{len(opportunities)}; "
        f"largest delta bucket: {largest_bucket} ({bucket_counts[largest_bucket]})."
    )

    return {
        "set_a_pass_count": set_a_pass_count,
        "set_b_pass_count": set_b_pass_count,
        "delta_opportunities": rows,
        "summary": summary,
        "draft_note": (
            "Draft for reviewer judgment. Deterministic constraint filter, "
            "not a constrained optimizer."
        ),
    }


# ---------- standalone demo ----------

def _demo() -> None:
    constraint_set_a = {
        # "current plan": looser
        "min_deal_size": 50_000.0,
        "max_cycle_days": 180,
        "required_clone_match": False,
        "min_persona_coverage": 0.3,
    }
    constraint_set_b = {
        # "board ask": tighter
        "min_deal_size": 100_000.0,
        "max_cycle_days": 120,
        "required_clone_match": True,
        "min_persona_coverage": 0.5,
    }

    opportunities = [
        {
            "opportunity_id": "OPP-1",
            "deal_size": 250_000.0,
            "cycle_days": 90,
            "clone_profile_match": True,
            "persona_coverage_score": 0.75,
        },
        {
            "opportunity_id": "OPP-2",
            "deal_size": 60_000.0,
            "cycle_days": 110,
            "clone_profile_match": True,
            "persona_coverage_score": 0.40,
        },
        {
            "opportunity_id": "OPP-3",
            "deal_size": 180_000.0,
            "cycle_days": 200,
            "clone_profile_match": False,
            "persona_coverage_score": 0.55,
        },
        {
            "opportunity_id": "OPP-4",
            "deal_size": 30_000.0,
            "cycle_days": 60,
            "clone_profile_match": False,
            "persona_coverage_score": 0.20,
        },
    ]

    result = compute_board_delta(constraint_set_a, constraint_set_b, opportunities)

    print("board_vs_plan_scorer — demo run")
    print("Draft for reviewer judgment. Deterministic constraint filter; not an optimizer.")
    print("-" * 78)
    print(f"set A pass count: {result['set_a_pass_count']}")
    print(f"set B pass count: {result['set_b_pass_count']}")
    print()
    header = f"{'opportunity':<14}{'A':>4}{'B':>4}  {'delta_label':<16} failed_in_a / failed_in_b"
    print(header)
    print("-" * 78)
    for r in result["delta_opportunities"]:
        a_mark = "Y" if r["set_a_pass"] else "."
        b_mark = "Y" if r["set_b_pass"] else "."
        fa = ",".join(r["failed_in_a"]) or "-"
        fb = ",".join(r["failed_in_b"]) or "-"
        print(f"{str(r['opportunity_id']):<14}{a_mark:>4}{b_mark:>4}  {r['delta_label']:<16} {fa} / {fb}")
    print()
    print("summary:", result["summary"])


if __name__ == "__main__":
    _demo()
