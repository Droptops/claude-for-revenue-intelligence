# SPDX-License-Identifier: Apache-2.0
"""Runtime binding helper for skill-aware agents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skills.loader import SkillConfig, load_active_skill


@dataclass(frozen=True)
class AgentContext:
    agent_name: str
    skill: SkillConfig

    @property
    def schema_paths(self) -> dict[str, Path]:
        return self.skill.schema_slot_paths()

    @property
    def theory_constants(self) -> dict:
        return self.skill.theory_constants


def resolve_agent_context(
    agent_name: str,
    root: Path | None = None,
    profile_path: Path | None = None,
) -> AgentContext:
    skill = load_active_skill(root, profile_path)
    if agent_name not in skill.agent_roster:
        raise ValueError(f"agent {agent_name!r} is not active for skill {skill.name!r}")
    return AgentContext(agent_name=agent_name, skill=skill)
