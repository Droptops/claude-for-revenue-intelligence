# SPDX-License-Identifier: Apache-2.0
"""Runnable toy demo for the PLG self-serve fork stub."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import sys


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.loader import load_skill_file  # noqa: E402


SKILL_PATH = Path(__file__).resolve().parent / "SKILL.md"

WORKSPACES = [
    {
        "workspace_id": "WORKSPACE_ALPHA",
        "active_user_count": 8,
        "core_action_count": 42,
        "days_from_signup": 4,
        "expansion_signal_count": 2,
    },
    {
        "workspace_id": "WORKSPACE_BETA",
        "active_user_count": 3,
        "core_action_count": 9,
        "days_from_signup": 11,
        "expansion_signal_count": 0,
    },
]


def score_workspace(workspace: dict[str, Any], constants: dict[str, Any]) -> dict[str, Any]:
    activation_days = int(constants["target_first_value_days"])
    min_active_users = int(constants["expansion_signal_min_active_users"])

    activation_score = 35 if workspace["days_from_signup"] <= activation_days else 10
    usage_score = min(35, workspace["core_action_count"])
    expansion_score = 20 if workspace["active_user_count"] >= min_active_users else 0
    expansion_score += min(10, workspace["expansion_signal_count"] * 5)

    score = min(100, activation_score + usage_score + expansion_score)
    return {
        "workspace_id": workspace["workspace_id"],
        "score": score,
        "activated_within_target": workspace["days_from_signup"] <= activation_days,
        "active_user_threshold_met": workspace["active_user_count"] >= min_active_users,
    }


def rank_workspaces(workspaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    skill = load_skill_file(SKILL_PATH)
    constants = skill.theory_constants["activation"]
    scored = [score_workspace(workspace, constants) for workspace in workspaces]
    return sorted(scored, key=lambda row: row["score"], reverse=True)


def main() -> int:
    skill = load_skill_file(SKILL_PATH)
    print("plg-self-serve demo")
    print(f"skill: {skill.name}")
    print("schema_slots: " + ", ".join(slot["name"] for slot in skill.schema_slots))
    print("Draft for reviewer judgment. Synthetic workspace data only.")
    print("-" * 72)
    for index, row in enumerate(rank_workspaces(WORKSPACES), start=1):
        print(
            f"{index}. {row['workspace_id']} score={row['score']} "
            f"activated={row['activated_within_target']} "
            f"active_users_met={row['active_user_threshold_met']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
