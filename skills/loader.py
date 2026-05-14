# SPDX-License-Identifier: Apache-2.0
"""Load motion-specialization skills for the revenue intelligence harness.

Skills use JSON front matter in ``SKILL.md``. The active skill is selected by
``active_skill`` in ``CLAUDE.local.md`` and falls back to the reference skill
when no local profile exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
import json
import re


DEFAULT_SKILL = "enterprise-account-based"

REQUIRED_FIELDS = frozenset(
    {
        "name",
        "description",
        "schema_slots",
        "agent_roster",
        "plugin_defaults",
        "cookbook_set",
        "theory_constants",
    }
)

_JSON_FRONT_MATTER = re.compile(
    r"\A(?:<!--[^>]*-->\s*)?\+\+\+\s*\n(?P<body>.*?)\n\+\+\+",
    re.DOTALL,
)
_ACTIVE_SKILL = re.compile(
    r"(?m)^\s*active_skill\s*:\s*[\"']?(?P<name>[A-Za-z0-9_.-]+)[\"']?\s*(?:#.*)?$"
)


class SkillLoadError(ValueError):
    """Raised when a skill cannot be parsed or validated."""


@dataclass(frozen=True)
class SkillConfig:
    """Resolved skill metadata and bindings."""

    name: str
    description: str
    schema_slots: list[dict[str, str]]
    agent_roster: list[str]
    plugin_defaults: list[str]
    cookbook_set: list[str]
    theory_constants: dict[str, Any]
    connector_bindings: list[str]
    source_path: Path

    @property
    def skill_dir(self) -> Path:
        return self.source_path.parent

    def schema_slot_paths(self) -> dict[str, Path]:
        paths: dict[str, Path] = {}
        for slot in self.schema_slots:
            name = slot["name"]
            paths[name] = (self.skill_dir / slot["path"]).resolve()
        return paths

    def schema_manifest_path(self) -> Path:
        return (self.skill_dir / "schema" / "manifest.json").resolve()

    def schema_manifest(self) -> dict[str, Any]:
        path = self.schema_manifest_path()
        if not path.exists():
            raise SkillLoadError(f"{self.name!r} has no schema manifest at {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SkillLoadError(f"{path} has invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise SkillLoadError(f"{path} must contain a JSON object")
        return data


def repo_root(start: Path | None = None) -> Path:
    """Return the repository root by walking up from ``start``."""

    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "CLAUDE.md").exists() and (candidate / "skills").exists():
            return candidate
    raise SkillLoadError(f"could not find repository root from {current}")


def _parse_skill_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = _JSON_FRONT_MATTER.search(text)
    if match is None:
        raise SkillLoadError(f"{path} does not contain JSON skill front matter")
    try:
        data = json.loads(match.group("body"))
    except json.JSONDecodeError as exc:
        raise SkillLoadError(f"{path} has invalid JSON front matter: {exc}") from exc
    if not isinstance(data, dict):
        raise SkillLoadError(f"{path} front matter must be a JSON object")
    return data


def _is_safe_relative_path(value: str) -> bool:
    paths = (PurePosixPath(value), PureWindowsPath(value))
    return not any(path.is_absolute() or ".." in path.parts for path in paths)


def _validate_skill(data: dict[str, Any], path: Path) -> None:
    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        raise SkillLoadError(f"{path} is missing required fields: {', '.join(missing)}")
    for key in ("name", "description"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise SkillLoadError(f"{path} field {key!r} must be a non-empty string")
    if not isinstance(data["schema_slots"], list) or not data["schema_slots"]:
        raise SkillLoadError(f"{path} must define at least one schema slot")
    for slot in data["schema_slots"]:
        if not isinstance(slot, dict):
            raise SkillLoadError(f"{path} has an invalid schema_slots entry: {slot!r}")
        if not isinstance(slot.get("name"), str) or not slot["name"].strip():
            raise SkillLoadError(f"{path} has a schema slot without a valid name")
        if not isinstance(slot.get("path"), str) or not slot["path"].strip():
            raise SkillLoadError(f"{path} has a schema slot without a valid path")
        if not _is_safe_relative_path(slot["path"]):
            raise SkillLoadError(f"{path} has an invalid schema_slots entry: {slot!r}")
    for key in ("agent_roster", "plugin_defaults", "cookbook_set"):
        if not isinstance(data[key], list):
            raise SkillLoadError(f"{path} field {key!r} must be a list")
        for value in data[key]:
            if not isinstance(value, str) or not value.strip():
                raise SkillLoadError(f"{path} field {key!r} contains an invalid entry")
    if not isinstance(data["theory_constants"], dict):
        raise SkillLoadError(f"{path} field 'theory_constants' must be a table")
    if "connector_bindings" in data:
        if not isinstance(data["connector_bindings"], list):
            raise SkillLoadError(f"{path} field 'connector_bindings' must be a list")
        for value in data["connector_bindings"]:
            if not isinstance(value, str) or not value.strip():
                raise SkillLoadError(
                    f"{path} field 'connector_bindings' contains an invalid entry"
                )


def load_skill_file(path: Path) -> SkillConfig:
    """Load and validate a single ``SKILL.md`` file."""

    path = path.resolve()
    data = _parse_skill_file(path)
    _validate_skill(data, path)
    return SkillConfig(
        name=str(data["name"]),
        description=str(data["description"]),
        schema_slots=list(data["schema_slots"]),
        agent_roster=[str(agent) for agent in data["agent_roster"]],
        plugin_defaults=[str(plugin) for plugin in data["plugin_defaults"]],
        cookbook_set=[str(cookbook) for cookbook in data["cookbook_set"]],
        theory_constants=dict(data["theory_constants"]),
        connector_bindings=[str(connector) for connector in data.get("connector_bindings", [])],
        source_path=path,
    )


def load_skill(skill_name: str = DEFAULT_SKILL, root: Path | None = None) -> SkillConfig:
    """Load a named installed skill from ``/skills/<skill_name>/SKILL.md``."""

    root = repo_root(root)
    return load_skill_file(root / "skills" / skill_name / "SKILL.md")


def _active_skill_name(root: Path, profile_path: Path | None = None) -> str:
    profile = profile_path or root / "CLAUDE.local.md"
    if not profile.exists():
        return DEFAULT_SKILL
    match = _ACTIVE_SKILL.search(profile.read_text(encoding="utf-8"))
    if match is None:
        return DEFAULT_SKILL
    return match.group("name")


def load_active_skill(root: Path | None = None, profile_path: Path | None = None) -> SkillConfig:
    """Load the active skill selected by ``CLAUDE.local.md``.

    If the local profile is absent or has no ``active_skill`` entry, this returns
    the default reference skill, ``enterprise-account-based``.
    """

    root = repo_root(root)
    return load_skill(_active_skill_name(root, profile_path), root)


def list_available_skills(root: Path | None = None) -> list[SkillConfig]:
    """Return installed motion skills that conform to the loader contract."""

    root = repo_root(root)
    skills: list[SkillConfig] = []
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        try:
            skills.append(load_skill_file(path))
        except SkillLoadError:
            # Legacy operator templates may still live under /skills during the
            # transition; they are not active motion-specialization skills.
            continue
    return skills
