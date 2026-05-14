# SPDX-License-Identifier: Apache-2.0
"""Show the active or selected skill bindings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.loader import SkillConfig, load_active_skill, load_skill  # noqa: E402


def skill_payload(skill: SkillConfig) -> dict[str, Any]:
    manifest = skill.schema_manifest()
    return {
        "name": skill.name,
        "description": skill.description,
        "schema_slots": [slot["name"] for slot in skill.schema_slots],
        "schema_paths": {
            name: str(path.relative_to(ROOT))
            for name, path in skill.schema_slot_paths().items()
        },
        "schema_manifest": str(skill.schema_manifest_path().relative_to(ROOT)),
        "manifest_slots": sorted(manifest.get("slots", {}).keys()),
        "agent_roster": skill.agent_roster,
        "plugin_defaults": skill.plugin_defaults,
        "cookbook_set": skill.cookbook_set,
        "connector_bindings": skill.connector_bindings,
        "theory_constants": skill.theory_constants,
    }


def print_text(payload: dict[str, Any]) -> None:
    print(f"active_skill: {payload['name']}")
    print(f"description: {payload['description']}")
    for key in (
        "schema_slots",
        "agent_roster",
        "plugin_defaults",
        "cookbook_set",
        "connector_bindings",
    ):
        print(f"{key}:")
        for value in payload[key]:
            print(f"  - {value}")
    print("theory_constants:")
    print(json.dumps(payload["theory_constants"], indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", default=None, help="Load a named installed skill.")
    parser.add_argument("--profile-path", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    args = parser.parse_args(argv)

    skill = load_skill(args.skill, ROOT) if args.skill else load_active_skill(ROOT, args.profile_path)
    payload = skill_payload(skill)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_text(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
