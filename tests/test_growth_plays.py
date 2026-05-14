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


model_arbitration = load_module("growth_model_arbitration", "core/model_arbitration.py")
market_share_tracker = load_module("market_share_tracker", "plugins/growth/market_share_tracker.py")
campaign_roi_tracker = load_module("campaign_roi_tracker", "plugins/growth/campaign_roi_tracker.py")
search_intent_mapper = load_module("search_intent_mapper", "plugins/growth/search_intent_mapper.py")


def load_growth_cases() -> list[dict]:
    path = ROOT / "evals/growth_eval_cases.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class GrowthPlayEvalTests(unittest.TestCase):
    def test_growth_eval_cases_match_expected_outcomes(self):
        for case in load_growth_cases():
            with self.subTest(case=case["id"]):
                workflow = case["workflow"]
                expected = case["expected"]
                if workflow == "market_share_tracker":
                    result = market_share_tracker.assess_segment(case["input"])
                    flag_names = {flag["name"] for flag in result["flags"]}
                    self.assertEqual(result["status"], expected["status"])
                    self.assertGreaterEqual(result["rule_of_60_score"], expected["min_rule_score"])
                    for flag in expected["required_flags"]:
                        self.assertIn(flag, flag_names)
                elif workflow == "campaign_roi_tracker":
                    result = campaign_roi_tracker.assess_campaign(case["input"])
                    flag_names = {flag["name"] for flag in result["flags"]}
                    self.assertEqual(result["decision"], expected["decision"])
                    if "min_roi_pct" in expected:
                        self.assertGreaterEqual(result["roi_pct"], expected["min_roi_pct"])
                    if "max_roi_pct" in expected:
                        self.assertLessEqual(result["roi_pct"], expected["max_roi_pct"])
                    if "max_payback_months" in expected:
                        self.assertLessEqual(result["cac_payback_months"], expected["max_payback_months"])
                    for flag in expected["required_flags"]:
                        self.assertIn(flag, flag_names)
                elif workflow == "search_intent_mapper":
                    result = search_intent_mapper.score_query(case["input"])
                    flag_names = {flag["name"] for flag in result["flags"]}
                    self.assertEqual(result["intent"], expected["intent"])
                    self.assertEqual(result["priority_tier"], expected["priority_tier"])
                    self.assertGreaterEqual(result["priority_score"], expected["min_priority_score"])
                    for flag in expected["required_flags"]:
                        self.assertIn(flag, flag_names)
                elif workflow == "model_arbitration":
                    result = model_arbitration.arbitrate_model(**case["input"])
                    self.assertEqual(result["selected_model"], expected["selected_model"])
                    self.assertEqual(result["prompt_cache_recommended"], expected["prompt_cache_recommended"])
                else:
                    self.fail(f"Unhandled workflow {workflow}")


class SearchIntentMapperTests(unittest.TestCase):
    def test_low_fit_volume_is_not_promoted(self):
        result = search_intent_mapper.score_query(
            {
                "query": "free sales email templates",
                "impressions": 10_000,
                "clicks": 900,
                "avg_position": 2,
                "business_fit_pct": 20,
                "difficulty_pct": 20,
            }
        )
        self.assertEqual(result["priority_tier"], "LOW")
        self.assertIn("LOW_FIT_DEMAND", {flag["name"] for flag in result["flags"]})


if __name__ == "__main__":
    unittest.main()
