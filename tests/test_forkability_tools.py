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


skill_loader = load_module("tool_skill_loader", "skills/loader.py")
cold_start = load_module("tool_cold_start", "tools/cold_start.py")
inspect_skill = load_module("tool_inspect_skill", "tools/inspect_skill.py")
new_skill = load_module("tool_new_skill", "tools/new_skill.py")
plg_demo = load_module("tool_plg_demo", "examples/forks/plg-self-serve/demo.py")
connector_mock = load_module("tool_connector_mock", "connectors/mock.py")
agent_runtime = load_module("tool_agent_runtime", "agents/runtime.py")


class ForkabilityToolTests(unittest.TestCase):
    def test_cold_start_writes_profile_that_loader_can_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "CLAUDE.local.md"
            fields = dict(cold_start.PROFILE_FIELDS)
            fields["active_skill"] = "enterprise-account-based"

            cold_start.write_profile(profile, fields)
            skill = skill_loader.load_active_skill(ROOT, profile_path=profile)

        self.assertEqual(skill.name, "enterprise-account-based")

    def test_inspect_skill_payload_exposes_bindings(self):
        skill = skill_loader.load_skill("enterprise-account-based", ROOT)
        payload = inspect_skill.skill_payload(skill)

        self.assertEqual(payload["name"], "enterprise-account-based")
        self.assertIn("funnel_telemetry", payload["schema_slots"])
        self.assertIn("anti_qualification", payload["theory_constants"])

    def test_new_skill_copies_example_and_rewrites_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "my-plg-motion"

            created = new_skill.create_skill_from_template("plg-self-serve", str(target))
            skill = skill_loader.load_skill_file(created / "SKILL.md")

        self.assertEqual(skill.name, "my-plg-motion")
        slots = {slot["name"] for slot in skill.schema_slots}
        self.assertEqual(
            slots,
            {"product_usage_telemetry", "activation_events", "expansion_signals"},
        )
        self.assertNotIn("funnel_telemetry", slots)

    def test_plg_demo_ranks_synthetic_workspaces(self):
        ranked = plg_demo.rank_workspaces(plg_demo.WORKSPACES)

        self.assertEqual(ranked[0]["workspace_id"], "WORKSPACE_ALPHA")
        self.assertGreater(ranked[0]["score"], ranked[1]["score"])

    def test_in_memory_connector_defaults_read_only(self):
        connector = connector_mock.InMemoryConnector(
            {"ACCOUNT_1": {"account_id": "ACCOUNT_1", "segment": "synthetic"}}
        )

        self.assertEqual(connector.read_account("ACCOUNT_1")["segment"], "synthetic")
        with self.assertRaises(PermissionError):
            connector.upsert_record("funnel_telemetry", {"opportunity_id": "OPP_1"})

    def test_in_memory_connector_writes_when_enabled(self):
        connector = connector_mock.InMemoryConnector(write_enabled=True)

        self.assertTrue(connector.upsert_record("slot", {"id": "ROW_1"}))
        self.assertEqual(connector.records["slot"][0]["id"], "ROW_1")

    def test_agent_runtime_resolves_active_agent_binding(self):
        context = agent_runtime.resolve_agent_context("anti_qualification_scorer", ROOT)

        self.assertEqual(context.skill.name, "enterprise-account-based")
        self.assertIn("funnel_telemetry", context.schema_paths)
        self.assertIn("anti_qualification", context.theory_constants)


if __name__ == "__main__":
    unittest.main()
