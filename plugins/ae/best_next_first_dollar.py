# SPDX-License-Identifier: Apache-2.0
"""Best Next First Dollar — deterministic weighted scorer.

This is a stub. It is a transparent, deterministic, weighted heuristic — not
a learned model and not a constrained optimizer. A real constrained
optimization is a stretch goal. Treat every output as a draft for reviewer
judgment.

Input: a list of opportunity dicts. Each dict has the keys:

    days_in_stage              int
    touch_count                int
    anti_qualification_ratio   float
    clone_profile_match        bool
    trigger_event_count        int
    persona_coverage_score     float in [0.0, 1.0]
    outcome_signal             one of "STRONG" | "WEAK" | "NONE" | "UNKNOWN"

Optional keys:

    opportunity_id             any hashable; carried through to output

Output: a list of dicts ranked by score descending. Each dict has:

    opportunity_id
    score                      float in [0, 100], rounded to 1 decimal
    confidence                 one of "LOW" | "MEDIUM" | "HIGH"
    score_breakdown            dict mapping component name to points

Weights are stubs. The operator overrides them via CLAUDE.md or a
weights.yaml at the same path; weights.yaml is not yet wired up.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


# ---------- weights (stubs; operator-configurable) ----------

@dataclass(frozen=True)
class Weights:
    clone_profile_match: float = 25.0
    persona_coverage_max: float = 20.0
    trigger_event_max: float = 15.0
    trigger_event_cap: int = 3
    anti_qualification_max: float = 15.0
    anti_qualification_floor: float = 1.0
    anti_qualification_ceiling: float = 4.0
    outcome_signal_strong: float = 15.0
    outcome_signal_weak: float = 7.0
    outcome_signal_none: float = 0.0
    outcome_signal_unknown: float = 3.0
    days_in_stage_threshold: int = 30
    days_in_stage_penalty_max: float = 15.0
    days_in_stage_penalty_window: int = 60


DEFAULT_WEIGHTS = Weights()


# ---------- component scorers ----------

def _score_clone(opp: dict[str, Any], w: Weights) -> float:
    return w.clone_profile_match if bool(opp.get("clone_profile_match")) else 0.0


def _score_persona_coverage(opp: dict[str, Any], w: Weights) -> float:
    coverage = float(opp.get("persona_coverage_score", 0.0))
    coverage = max(0.0, min(1.0, coverage))
    return coverage * w.persona_coverage_max


def _score_trigger_events(opp: dict[str, Any], w: Weights) -> float:
    count = int(opp.get("trigger_event_count", 0))
    capped = min(count, w.trigger_event_cap)
    if w.trigger_event_cap == 0:
        return 0.0
    return (capped / w.trigger_event_cap) * w.trigger_event_max


def _score_anti_qualification(opp: dict[str, Any], w: Weights) -> float:
    """Inverted: lower ratio = real-change buyer = higher score."""
    ratio = opp.get("anti_qualification_ratio")
    if ratio is None:
        return 0.0
    ratio = float(ratio)
    lo, hi = w.anti_qualification_floor, w.anti_qualification_ceiling
    if hi <= lo:
        return 0.0
    clamped = max(lo, min(hi, ratio))
    inverted = 1.0 - (clamped - lo) / (hi - lo)
    return inverted * w.anti_qualification_max


def _score_outcome_signal(opp: dict[str, Any], w: Weights) -> float:
    signal = (opp.get("outcome_signal") or "UNKNOWN").upper()
    return {
        "STRONG": w.outcome_signal_strong,
        "WEAK": w.outcome_signal_weak,
        "NONE": w.outcome_signal_none,
        "UNKNOWN": w.outcome_signal_unknown,
    }.get(signal, w.outcome_signal_unknown)


def _days_in_stage_penalty(opp: dict[str, Any], w: Weights) -> float:
    days = int(opp.get("days_in_stage", 0))
    over = days - w.days_in_stage_threshold
    if over <= 0 or w.days_in_stage_penalty_window <= 0:
        return 0.0
    fraction = min(1.0, over / w.days_in_stage_penalty_window)
    return -fraction * w.days_in_stage_penalty_max


# ---------- confidence ----------

def _confidence(opp: dict[str, Any]) -> str:
    clone = bool(opp.get("clone_profile_match"))
    coverage = float(opp.get("persona_coverage_score", 0.0))
    if clone and coverage > 0.6:
        return "HIGH"
    if clone or coverage > 0.6:
        return "MEDIUM"
    return "LOW"


# ---------- public api ----------

def score_opportunity(opp: dict[str, Any], weights: Weights = DEFAULT_WEIGHTS) -> dict[str, Any]:
    breakdown = {
        "clone_profile_match": round(_score_clone(opp, weights), 2),
        "persona_coverage": round(_score_persona_coverage(opp, weights), 2),
        "trigger_events": round(_score_trigger_events(opp, weights), 2),
        "anti_qualification": round(_score_anti_qualification(opp, weights), 2),
        "outcome_signal": round(_score_outcome_signal(opp, weights), 2),
        "days_in_stage_penalty": round(_days_in_stage_penalty(opp, weights), 2),
    }
    raw = sum(breakdown.values())
    score = max(0.0, min(100.0, raw))
    return {
        "opportunity_id": opp.get("opportunity_id"),
        "score": round(score, 1),
        "confidence": _confidence(opp),
        "score_breakdown": breakdown,
    }


def rank_opportunities(opps: Iterable[dict[str, Any]], weights: Weights = DEFAULT_WEIGHTS) -> list[dict[str, Any]]:
    scored = [score_opportunity(o, weights) for o in opps]
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored


# ---------- standalone demo ----------

def _demo() -> None:
    samples = [
        {
            "opportunity_id": "OPP-A",
            "days_in_stage": 14,
            "touch_count": 6,
            "anti_qualification_ratio": 1.2,
            "clone_profile_match": True,
            "trigger_event_count": 2,
            "persona_coverage_score": 0.75,
            "outcome_signal": "STRONG",
        },
        {
            "opportunity_id": "OPP-B",
            "days_in_stage": 75,
            "touch_count": 11,
            "anti_qualification_ratio": 3.4,
            "clone_profile_match": False,
            "trigger_event_count": 0,
            "persona_coverage_score": 0.30,
            "outcome_signal": "WEAK",
        },
        {
            "opportunity_id": "OPP-C",
            "days_in_stage": 42,
            "touch_count": 4,
            "anti_qualification_ratio": 2.1,
            "clone_profile_match": True,
            "trigger_event_count": 4,
            "persona_coverage_score": 0.50,
            "outcome_signal": "UNKNOWN",
        },
    ]

    ranked = rank_opportunities(samples)

    print("Best Next First Dollar — demo run")
    print("Draft for reviewer judgment. Stub scorer; not a constrained optimizer.")
    print("-" * 72)
    header = f"{'rank':<5}{'opportunity':<14}{'score':>7}  {'conf':<7}  breakdown"
    print(header)
    print("-" * 72)
    for i, r in enumerate(ranked, start=1):
        bd = r["score_breakdown"]
        bd_str = ", ".join(f"{k}={v}" for k, v in bd.items())
        print(f"{i:<5}{str(r['opportunity_id']):<14}{r['score']:>7.1f}  {r['confidence']:<7}  {bd_str}")


if __name__ == "__main__":
    _demo()
