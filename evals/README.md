<!-- SPDX-License-Identifier: Apache-2.0 -->
# Evals

Two harnesses run side by side.

`evals/run_evals.py` is a deterministic suite. Each `evals/<suite>/cases.yaml`
file lists input cases and their expected outputs; the runner asserts each
scorer produces the expected labels, scores, ordering, or delta buckets. It
is stdlib-only.

`evals/anti_qualification_cohort.py` generates 200 synthetic deals with
planted buyer intent and reports precision / recall / F1 for the scorer's
`POLITICAL_COVER` predictions against ground-truth implementation failure.
Output is deterministic (seeded). CI gates on a sanity F1 floor, not a
calibration claim.

The JSONL fixtures are consumed directly by `tests/test_enterprise_revenue_plays.py`.

## Files

- `anti_qualification/cases.yaml`: expected anti-qualification labels,
  confidence, and ratios.
- `best_next_first_dollar/cases.yaml`: expected account ranking and scoring
  behavior.
- `board_vs_plan/cases.yaml`: expected board-vs-plan pass counts and deltas.
- `forkability/cases.yaml`: expected skill slot bindings and theory constants.
- `revenue_play_eval_cases.jsonl`: expected outcomes for pipeline risk,
  renewal radar, schema health, and model arbitration.
- `anti_qualification_cohort.py`: synthetic cohort harness with P/R/F1 report.

## Add a YAML case

Each YAML suite has an `evals/<suite>/cases.yaml` file. Add one top-level list
item per case:

```yaml
- id: aq_001
  category: happy_path
  description: "Heavy consulting buyer is clear political cover"
  inputs:
    opportunity_id: aq_001
    consulting_spend: 800000.0
    implementation_spend: 200000.0
    data_source: CRM
  expected:
    anti_qual_label: POLITICAL_COVER
    confidence: HIGH
    ratio_approx: 4.0
```

Use `expected.raises` for cases that should raise a known exception. Use
suite-specific expected fields:

- `anti_qualification`: `anti_qual_label`, `confidence`, `ratio_approx`,
  `raises`
- `best_next_first_dollar`: `expected_order`, `score_min`, `score_max`,
  `confidence`, `score_breakdown`
- `board_vs_plan`: `set_a_pass_count`, `set_b_pass_count`, `delta_labels`,
  `largest_bucket`
- `forkability`: `must_include_slots`, `must_exclude_slots`,
  `theory_constants_include`

## Run locally

```bash
python evals/run_evals.py
python evals/anti_qualification_cohort.py
python -m unittest discover -s tests
```

## Exit codes

- `0`: all cases passed
- `1`: one or more cases failed, or F1 below the cohort sanity floor
