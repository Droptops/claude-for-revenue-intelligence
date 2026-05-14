# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.util
import json
import sys
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


model_arbitration = load_module("intent_model_arbitration", "core/model_arbitration.py")
intent_sequence_builder = load_module("intent_sequence_builder", "plugins/growth/intent_sequence_builder.py")
battlecard_builder = load_module("battlecard_builder", "plugins/competitive-intel/battlecard_builder.py")
cdn_feature_monitor = load_module("cdn_feature_monitor", "plugins/competitive-intel/cdn_feature_monitor.py")


def load_intent_cases() -> list[dict]:
    path = ROOT / "evals/intent_activation_eval_cases.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class IntentActivationEvalTests(unittest.TestCase):
    def test_intent_activation_eval_cases_match_expected_outcomes(self):
        for case in load_intent_cases():
            with self.subTest(case=case["id"]):
                workflow = case["workflow"]
                expected = case["expected"]
                if workflow == "intent_sequence_builder":
                    result = intent_sequence_builder.draft_sequence(case["input"])
                    self.assertEqual(result["intent_tier"], expected["intent_tier"])
                    self.assertEqual(len(result["selected_contacts"]), expected["selected_contacts"])
                    self.assertEqual(len(result["suppressed_contacts"]), expected["suppressed_contacts"])
                    if "primary_theme" in expected:
                        self.assertEqual(result["primary_theme"], expected["primary_theme"])
                    if "sequence_steps" in expected:
                        self.assertEqual(len(result["sequence"]), expected["sequence_steps"])
                    for intent_class in expected.get("required_intent_classes", []):
                        self.assertIn(intent_class, result["intent_classes"])
                elif workflow == "competitive_battlecard_builder":
                    result = battlecard_builder.build_battlecard(case["input"])
                    self.assertGreaterEqual(len(result["talk_tracks"]), expected["min_talk_tracks"])
                    for capability in expected.get("required_matched_capabilities", []):
                        self.assertIn(capability, result["matched_own_capabilities"])
                    for signal in expected.get("required_competitor_signals", []):
                        self.assertIn(signal, result["competitor_feature_signals"])
                    for landmine in expected.get("required_landmines", []):
                        self.assertIn(landmine, result["landmines"])
                elif workflow == "cdn_feature_monitor":
                    result = cdn_feature_monitor.diff_asset_snapshots(case["input"])
                    flag_names = {flag["name"] for flag in result["flags"]}
                    self.assertEqual(result["posture"], expected["posture"])
                    self.assertEqual(result["monitoring_allowed"], expected["monitoring_allowed"])
                    for term in expected.get("required_added_terms", []):
                        self.assertIn(term, result["added_feature_terms"])
                    for flag in expected.get("required_flags", []):
                        self.assertIn(flag, flag_names)
                elif workflow == "model_arbitration":
                    result = model_arbitration.arbitrate_model(**case["input"])
                    self.assertEqual(result["selected_model"], expected["selected_model"])
                    self.assertEqual(result["prompt_cache_recommended"], expected["prompt_cache_recommended"])
                else:
                    self.fail(f"Unhandled workflow {workflow}")


class IntentSequenceSafetyTests(unittest.TestCase):
    def test_sequence_does_not_claim_individual_search(self):
        result = intent_sequence_builder.draft_sequence(
            {
                "account_id": "ACCT-1",
                "company_name": "ExampleCo",
                "intent_score": 90,
                "searched_keywords": ["pricing forecast software"],
                "contacts": [{"contact_id": "C-1", "email": "a@example.invalid", "email_allowed": True}],
            }
        )
        sequence_text = " ".join(step["body"].lower() for step in result["sequence"])
        self.assertNotIn("you searched", sequence_text)
        self.assertNotIn("we saw you", sequence_text)


if __name__ == "__main__":
    unittest.main()
