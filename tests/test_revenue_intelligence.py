# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.util
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


aq_scorer = load_module(
    "aq_scorer",
    "agents/anti_qualification_scorer/aq_scorer.py",
)
signatory_extractor = load_module(
    "signatory_extractor",
    "agents/signature_authority_miner/signatory_extractor.py",
)
sec_edgar_fetcher = load_module(
    "sec_edgar_fetcher",
    "agents/signature_authority_miner/sec_edgar_fetcher.py",
)
earnings_parser = load_module(
    "earnings_parser",
    "agents/trigger_event_monitor/earnings_parser.py",
)
pre_announcement_watcher = load_module(
    "pre_announcement_watcher",
    "agents/trigger_event_monitor/pre_announcement_watcher.py",
)
best_next_first_dollar = load_module(
    "best_next_first_dollar",
    "plugins/ae/best_next_first_dollar.py",
)
board_vs_plan_scorer = load_module(
    "board_vs_plan_scorer",
    "plugins/sales-leadership/board_vs_plan_scorer.py",
)


class AntiQualificationScorerTests(unittest.TestCase):
    def test_labels_ratio_bands_and_normalizes_source(self):
        political = aq_scorer.score_opportunity("opp-1", 800, 200, data_source="crm")
        real_change = aq_scorer.score_opportunity("opp-2", 100, 500)
        ambiguous = aq_scorer.score_opportunity("opp-3", 300, 150)

        self.assertEqual(political["anti_qual_label"], "POLITICAL_COVER")
        self.assertEqual(political["confidence"], "HIGH")
        self.assertEqual(real_change["anti_qual_label"], "REAL_CHANGE")
        self.assertEqual(ambiguous["anti_qual_label"], "AMBIGUOUS")

    def test_zero_implementation_spend_is_defined_low_confidence(self):
        result = aq_scorer.score_opportunity("opp-1", 250, 0, data_source="CRM")
        self.assertIsNone(result["anti_qualification_ratio"])
        self.assertEqual(result["anti_qual_label"], "AMBIGUOUS")
        self.assertEqual(result["confidence"], "LOW")

    def test_negative_spend_rejected(self):
        with self.assertRaises(ValueError):
            aq_scorer.score_opportunity("opp-1", -1, 100)


class BestNextFirstDollarTests(unittest.TestCase):
    def test_rank_orders_by_score_and_clamps_negative_triggers(self):
        ranked = best_next_first_dollar.rank_opportunities(
            [
                {
                    "opportunity_id": "weak",
                    "days_in_stage": 90,
                    "anti_qualification_ratio": 4.0,
                    "clone_profile_match": False,
                    "trigger_event_count": -3,
                    "persona_coverage_score": 0.1,
                    "outcome_signal": "NONE",
                },
                {
                    "opportunity_id": "strong",
                    "days_in_stage": 10,
                    "anti_qualification_ratio": 1.2,
                    "clone_profile_match": True,
                    "trigger_event_count": 3,
                    "persona_coverage_score": 0.8,
                    "outcome_signal": "STRONG",
                },
            ]
        )

        self.assertEqual(ranked[0]["opportunity_id"], "strong")
        self.assertGreaterEqual(ranked[1]["score_breakdown"]["trigger_events"], 0.0)


class BoardVsPlanTests(unittest.TestCase):
    def test_delta_buckets_are_reported(self):
        result = board_vs_plan_scorer.compute_board_delta(
            {"min_deal_size": 50_000, "required_clone_match": False},
            {"min_deal_size": 100_000, "required_clone_match": True},
            [
                {"opportunity_id": "a", "deal_size": 120_000, "clone_profile_match": True},
                {"opportunity_id": "b", "deal_size": 70_000, "clone_profile_match": True},
            ],
        )

        self.assertEqual(result["set_a_pass_count"], 2)
        self.assertEqual(result["set_b_pass_count"], 1)
        self.assertEqual(result["delta_opportunities"][1]["delta_label"], "PASSED_A_ONLY")


class ExtractorAndMonitorTests(unittest.TestCase):
    def test_signatory_extractor_deduplicates_name_lines(self):
        text = """
By: Placeholder Person
Name: Placeholder Person
Title: Authorized Officer
Date: February 14, 2026
"""
        rows = signatory_extractor.extract_signatories(text, "https://example.invalid/filing")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["signing_date"], "2026-02-14")
        self.assertEqual(rows[0]["confidence_score"], 0.9)

    def test_earnings_parser_groups_signal_families(self):
        rows = earnings_parser.parse_earnings_transcript(
            "We are accelerating this quarter while exercising cost discipline.",
            "ACCT-1",
        )
        families = {row["signal_family"] for row in rows}
        self.assertEqual(families, {"expansion", "contraction", "urgency"})

    def test_stub_fetchers_do_not_perform_live_network_by_default(self):
        filings = sec_edgar_fetcher.fetch_filings("0000000000", ["10-K"], live=False)
        diff = pre_announcement_watcher.watch_static_endpoints(
            "https://placeholder.invalid",
            ["/sitemap.xml"],
            prior_snapshot=None,
            live=False,
        )

        self.assertEqual(filings, [])
        self.assertEqual(diff["new_paths_detected"], [])


if __name__ == "__main__":
    unittest.main()
