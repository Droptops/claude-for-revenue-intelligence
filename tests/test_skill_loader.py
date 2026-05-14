# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


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


skill_loader = load_module("skill_loader", "skills/loader.py")
aq_scorer = load_module(
    "skill_loader_aq_scorer",
    "agents/anti_qualification_scorer/aq_scorer.py",
)


class SkillLoaderTests(unittest.TestCase):
    def test_load_active_skill_defaults_to_reference_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_profile = Path(tmp) / "CLAUDE.local.md"
            skill = skill_loader.load_active_skill(ROOT, profile_path=missing_profile)

        self.assertEqual(skill.name, "enterprise-account-based")
        self.assertIn("anti_qualification", skill.theory_constants)

    def test_load_active_skill_reads_profile_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "CLAUDE.local.md"
            profile.write_text(
                "```yaml\nactive_skill: enterprise-account-based\n```\n",
                encoding="utf-8",
            )

            skill = skill_loader.load_active_skill(ROOT, profile_path=profile)

        self.assertEqual(skill.name, "enterprise-account-based")

    def test_installed_motion_skills_have_required_fields(self):
        skills = skill_loader.list_available_skills(ROOT)
        names = {skill.name for skill in skills}

        self.assertIn("enterprise-account-based", names)
        self.assertNotIn("deal_review_template", names)
        for skill in skills:
            self.assertTrue(skill.description)
            self.assertTrue(skill.schema_slots)
            self.assertIsInstance(skill.agent_roster, list)
            self.assertIsInstance(skill.plugin_defaults, list)
            self.assertIsInstance(skill.cookbook_set, list)
            self.assertIsInstance(skill.theory_constants, dict)

    def test_legacy_operator_template_is_not_loaded_as_motion_skill(self):
        legacy = ROOT / "skills" / "deal_review_template" / "SKILL.md"

        with self.assertRaises(skill_loader.SkillLoadError):
            skill_loader.load_skill_file(legacy)

    def test_reference_skill_preserves_schema_slots_and_aq_behavior(self):
        skill = skill_loader.load_skill("enterprise-account-based", ROOT)
        slot_paths = skill.schema_slot_paths()

        self.assertEqual(
            set(slot_paths),
            {
                "signature_authority",
                "persona_graph",
                "funnel_telemetry",
                "outcome_telemetry",
                "conversation_evidence",
                "trigger_events",
            },
        )
        for path in slot_paths.values():
            self.assertTrue(path.exists(), path)
        manifest = skill.schema_manifest()
        self.assertEqual(set(manifest["slots"]), set(slot_paths))

        thresholds = skill.theory_constants["anti_qualification"]
        self.assertEqual(thresholds["political_cover_min"], 3.0)
        self.assertEqual(thresholds["real_change_max"], 1.5)

        political = aq_scorer.score_opportunity("opp-1", 800, 200)
        real_change = aq_scorer.score_opportunity("opp-2", 100, 500)
        edge = aq_scorer.score_opportunity("opp-3", 300, 100)

        self.assertEqual(political["anti_qual_label"], "POLITICAL_COVER")
        self.assertEqual(real_change["anti_qual_label"], "REAL_CHANGE")
        self.assertEqual(edge["anti_qual_label"], "AMBIGUOUS")

    def test_example_fork_stubs_have_valid_skill_and_schema_directory(self):
        fork_root = ROOT / "examples" / "forks"
        expected = {
            "finserv-enterprise",
            "plg-self-serve",
            "healthcare-patient-acquisition",
        }
        found = {path.parent.name for path in fork_root.glob("*/SKILL.md")}

        self.assertEqual(found, expected)
        for skill_file in sorted(fork_root.glob("*/SKILL.md")):
            skill = skill_loader.load_skill_file(skill_file)
            self.assertTrue((skill.skill_dir / "README.md").exists())
            self.assertTrue((skill.skill_dir / "agents.md").exists())
            self.assertTrue((skill.skill_dir / "schema").is_dir())
            manifest = skill.schema_manifest()
            self.assertEqual(
                set(manifest["slots"]),
                {slot["name"] for slot in skill.schema_slots},
            )
            for path in skill.schema_slot_paths().values():
                self.assertTrue(path.exists(), path)

    def test_invalid_skill_metadata_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_file = Path(tmp) / "SKILL.md"
            skill_file.write_text(
                """+++
{
  "name": "bad",
  "description": "",
  "schema_slots": [],
  "agent_roster": [],
  "plugin_defaults": [],
  "cookbook_set": [],
  "theory_constants": {}
}
+++
# Bad Skill
""",
                encoding="utf-8",
            )

            with self.assertRaises(skill_loader.SkillLoadError):
                skill_loader.load_skill_file(skill_file)

    def test_schema_slot_paths_must_be_safe_relative_paths(self):
        for unsafe_path in ("../schema.md", "C:/tmp/schema.md"):
            with self.subTest(unsafe_path=unsafe_path):
                with tempfile.TemporaryDirectory() as tmp:
                    skill_file = Path(tmp) / "SKILL.md"
                    skill_file.write_text(
                        f"""+++
{{
  "name": "bad",
  "description": "Bad skill with an unsafe path.",
  "schema_slots": [
    {{ "name": "escape", "path": "{unsafe_path}" }}
  ],
  "agent_roster": [],
  "plugin_defaults": [],
  "cookbook_set": [],
  "theory_constants": {{}}
}}
+++
# Bad Skill
""",
                        encoding="utf-8",
                    )

                    with self.assertRaises(skill_loader.SkillLoadError):
                        skill_loader.load_skill_file(skill_file)


if __name__ == "__main__":
    unittest.main()
