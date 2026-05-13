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


model_arbitration = load_module("model_arbitration", "core/model_arbitration.py")
pipeline_risk_radar = load_module(
    "pipeline_risk_radar",
    "plugins/sales-leadership/pipeline_risk_radar.py",
)
renewal_radar = load_module(
    "renewal_radar",
    "plugins/customer-success/renewal_radar.py",
)
schema_health = load_module(
    "schema_health",
    "plugins/revops/schema_health.py",
)


def load_eval_cases() -> list[dict]:
    path = ROOT / "evals/revenue_play_eval_cases.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class EnterpriseRevenuePlayEvalTests(unittest.TestCase):
    def test_eval_cases_match_expected_outcomes(self):
        for case in load_eval_cases():
            with self.subTest(case=case["id"]):
                workflow = case["workflow"]
                expected = case["expected"]
                if workflow == "pipeline_risk_radar":
                    result = pipeline_risk_radar.assess_opportunity(case["input"], as_of="2026-05-13")
                    flag_names = {flag["name"] for flag in result["risk_flags"]}
                    self.assertEqual(result["risk_tier"], expected["risk_tier"])
                    if "min_score" in expected:
                        self.assertGreaterEqual(result["risk_score"], expected["min_score"])
                    if "max_score" in expected:
                        self.assertLessEqual(result["risk_score"], expected["max_score"])
                    for flag in expected["required_flags"]:
                        self.assertIn(flag, flag_names)
                elif workflow == "renewal_expansion_radar":
                    result = renewal_radar.assess_account(case["input"], as_of="2026-05-13")
                    if "churn_risk_tier" in expected:
                        self.assertEqual(result["churn_risk_tier"], expected["churn_risk_tier"])
                    if "expansion_tier" in expected:
                        self.assertEqual(result["expansion_tier"], expected["expansion_tier"])
                    if "min_churn_score" in expected:
                        self.assertGreaterEqual(result["churn_risk_score"], expected["min_churn_score"])
                    if "max_churn_score" in expected:
                        self.assertLessEqual(result["churn_risk_score"], expected["max_churn_score"])
                    if "min_expansion_score" in expected:
                        self.assertGreaterEqual(result["expansion_score"], expected["min_expansion_score"])
                elif workflow == "schema_health_gate":
                    result = schema_health.score_slot(case["slot"], case["input"])
                    self.assertEqual(result["health_tier"], expected["health_tier"])
                    self.assertEqual(len(result["missing_cells"]), expected["missing_count"])
                elif workflow == "model_arbitration":
                    result = model_arbitration.arbitrate_model(**case["input"])
                    self.assertEqual(result["selected_model"], expected["selected_model"])
                    self.assertEqual(result["prompt_cache_recommended"], expected["prompt_cache_recommended"])
                else:
                    self.fail(f"Unhandled workflow {workflow}")


class ModelArbitrationTests(unittest.TestCase):
    def test_unknown_workflow_rejected(self):
        with self.assertRaises(ValueError):
            model_arbitration.arbitrate_model("unknown", estimated_input_tokens=100)

    def test_long_context_routes_to_long_context_model(self):
        decision = model_arbitration.arbitrate_model(
            "win_loss_pattern_miner",
            estimated_input_tokens=260_000,
        )
        self.assertEqual(decision["selected_model"], "claude-sonnet-long-context")
        self.assertTrue(decision["fits_context"])


class PipelineRiskRadarTests(unittest.TestCase):
    def test_commit_large_deal_escalates_model_policy(self):
        result = pipeline_risk_radar.assess_opportunity(
            {
                "opportunity_id": "OPP-1",
                "amount": 300_000,
                "forecast_category": "COMMIT",
                "close_date": "2026-05-01",
                "last_activity_days": 30,
                "next_step_age_days": 30,
                "persona_coverage_score": 0.1,
                "champion_confirmed": False,
                "economic_buyer_confirmed": False,
                "signatory_verified": False,
            },
            as_of="2026-05-13",
        )
        self.assertEqual(result["risk_tier"], "HIGH")
        self.assertEqual(result["model_policy"]["selected_model"], "claude-opus")


if __name__ == "__main__":
    unittest.main()
