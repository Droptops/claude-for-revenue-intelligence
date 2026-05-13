# SPDX-License-Identifier: Apache-2.0
"""Schema health gate for RevOps.

Use this before model synthesis. If the source rows are missing required fields,
do not spend tokens asking a model to write a polished narrative from bad data.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.model_arbitration import arbitrate_model, estimate_record_tokens


SLOT_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "funnel_telemetry": (
        "opportunity_id",
        "account_id",
        "touch_count",
        "outcome",
        "clone_profile_match",
        "anti_clone_profile_match",
        "outlier_flag",
    ),
    "outcome_telemetry": (
        "account_id",
        "opportunity_id",
        "contract_diff_detected",
        "renewal_signal",
        "last_monitored_at",
        "monitor_source",
    ),
    "conversation_evidence": (
        "account_id",
        "opportunity_id",
        "call_ref_id",
        "call_platform",
        "call_date",
        "indexed_at",
    ),
    "trigger_events": (
        "account_id",
        "event_type",
        "signal_summary",
        "confidence_score",
        "extracted_at",
    ),
}


def score_slot(slot: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    if slot not in SLOT_REQUIREMENTS:
        raise ValueError(f"unknown slot {slot!r}")

    required = SLOT_REQUIREMENTS[slot]
    missing_cells: list[dict[str, Any]] = []
    total_required = len(required) * len(rows)

    for index, row in enumerate(rows):
        for field in required:
            if row.get(field) in (None, ""):
                missing_cells.append({"row_index": index, "field": field})

    complete_cells = total_required - len(missing_cells)
    completeness = 1.0 if total_required == 0 else complete_cells / total_required
    health_score = round(completeness * 100, 1)
    if health_score >= 95:
        tier = "GREEN"
    elif health_score >= 80:
        tier = "YELLOW"
    else:
        tier = "RED"

    blocked_workflows = []
    if tier == "RED":
        blocked_workflows.extend(["executive_forecast_memo", "renewal_expansion_radar"])
    if slot == "conversation_evidence" and missing_cells:
        blocked_workflows.append("win_loss_pattern_miner")

    model_policy = arbitrate_model(
        "schema_health_gate",
        estimated_input_tokens=sum(estimate_record_tokens(row) for row in rows),
    )

    return {
        "slot": slot,
        "row_count": len(rows),
        "health_score": health_score,
        "health_tier": tier,
        "missing_cells": missing_cells,
        "blocked_workflows": sorted(set(blocked_workflows)),
        "model_policy": model_policy,
        "draft_note": "Draft for reviewer judgment. Fix source data before synthesizing executive narratives.",
    }


def score_schema_batch(batch: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    slots = [score_slot(slot, rows) for slot, rows in batch.items()]
    red = [slot for slot in slots if slot["health_tier"] == "RED"]
    yellow = [slot for slot in slots if slot["health_tier"] == "YELLOW"]
    return {
        "slot_results": slots,
        "summary": f"{len(red)} red slots, {len(yellow)} yellow slots, {len(slots)} total slots checked.",
        "ready_for_executive_synthesis": not red,
    }


def _demo() -> None:
    batch = {
        "funnel_telemetry": [
            {
                "opportunity_id": "OPP-1",
                "account_id": "ACCT-1",
                "touch_count": 5,
                "outcome": "OPEN",
                "clone_profile_match": True,
                "anti_clone_profile_match": False,
                "outlier_flag": False,
            },
            {
                "opportunity_id": "OPP-2",
                "account_id": None,
                "touch_count": 0,
                "outcome": "OPEN",
                "clone_profile_match": False,
                "anti_clone_profile_match": False,
                "outlier_flag": False,
            },
        ]
    }
    result = score_schema_batch(batch)
    print("schema_health - demo run")
    print(result["summary"])
    for slot in result["slot_results"]:
        print(f"{slot['slot']}: {slot['health_tier']} {slot['health_score']} missing={len(slot['missing_cells'])} model={slot['model_policy']['selected_model']}")


if __name__ == "__main__":
    _demo()
