# SPDX-License-Identifier: Apache-2.0
"""Create a new skill by copying an example fork or installed skill."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.loader import load_skill_file  # noqa: E402


_FRONT_MATTER = re.compile(
    r"\A(?P<prefix>(?:<!--[^>]*-->\s*)?)\+\+\+\s*\n(?P<body>.*?)\n\+\+\+",
    re.DOTALL,
)


def _safe_relative(value: str) -> bool:
    paths = (PurePosixPath(value), PureWindowsPath(value))
    return not any(path.is_absolute() or ".." in path.parts for path in paths)


def resolve_source(source: str, root: Path = ROOT) -> Path:
    candidates = [
        root / "examples" / "forks" / source,
        root / "skills" / source,
        Path(source),
        root / source,
    ]
    for candidate in candidates:
        if candidate.exists() and (candidate / "SKILL.md").exists():
            return candidate.resolve()
    raise FileNotFoundError(f"could not resolve skill source {source!r}")


def resolve_target(target: str, root: Path = ROOT) -> Path:
    target_path = Path(target)
    if not target_path.is_absolute() and len(target_path.parts) == 1:
        target_path = root / "skills" / target
    elif not target_path.is_absolute():
        if not _safe_relative(target):
            raise ValueError(f"unsafe target path {target!r}")
        target_path = root / target_path
    return target_path.resolve()


def _rewrite_skill_name(skill_file: Path, name: str, description: str | None) -> None:
    text = skill_file.read_text(encoding="utf-8")
    match = _FRONT_MATTER.search(text)
    if match is None:
        raise ValueError(f"{skill_file} has no JSON front matter")
    data = json.loads(match.group("body"))
    data["name"] = name
    if description:
        data["description"] = description
    front_matter = "+++\n" + json.dumps(data, indent=2, sort_keys=False) + "\n+++"
    updated = match.group("prefix") + front_matter + text[match.end():]
    skill_file.write_text(updated, encoding="utf-8")


def create_skill_from_template(
    source: str,
    target: str,
    *,
    root: Path = ROOT,
    description: str | None = None,
    force: bool = False,
) -> Path:
    source_dir = resolve_source(source, root)
    target_dir = resolve_target(target, root)
    root = root.resolve()
    if target_dir == root:
        raise ValueError("target cannot be the repository root")
    if target_dir.exists():
        if not force:
            raise FileExistsError(f"{target_dir} already exists; pass --force to overwrite")
        if not (target_dir / "SKILL.md").exists():
            raise ValueError(f"refusing to overwrite non-skill directory {target_dir}")
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)
    _rewrite_skill_name(target_dir / "SKILL.md", target_dir.name, description)
    load_skill_file(target_dir / "SKILL.md")
    return target_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Example fork name, installed skill name, or path.")
    parser.add_argument("target", help="New skill name or path under the repo.")
    parser.add_argument("--description", default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    target = create_skill_from_template(
        args.source,
        args.target,
        description=args.description,
        force=args.force,
    )
    print(f"created {target}")
    print(f"next: set active_skill: {target.name} in CLAUDE.local.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
