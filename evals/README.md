<!-- SPDX-License-Identifier: Apache-2.0 -->
# Evals

The evals are deterministic behavior checks for scorer outputs. Unit tests
verify code paths and implementation details. Evals verify that known input
cases continue to produce the same labels, scores, ordering, and delta buckets
that an operator would expect from the current heuristics.

The runner is stdlib-only. The YAML case files use a small subset parsed by
`evals/run_evals.py`: dictionaries, lists, strings, numbers, booleans, and
nulls. This keeps local and CI execution dependency-free.

Some newer workflow fixtures are JSONL files consumed directly by tests. These
are still deterministic guardrail cases, not benchmarks and not claims about
model performance.

## Files

- `anti_qualification/cases.yaml`: expected anti-qualification labels,
  confidence, and ratios.
- `best_next_first_dollar/cases.yaml`: expected account ranking and scoring
  behavior.
- `board_vs_plan/cases.yaml`: expected board-vs-plan pass counts and deltas.
- `forkability/cases.yaml`: expected skill slot bindings and theory constants.
- `revenue_play_eval_cases.jsonl`: expected outcomes for pipeline risk,
  renewal radar, schema health, and model arbitration.
- `growth_eval_cases.jsonl`: expected outcomes for market-share posture,
  campaign ROI, search intent, and growth model arbitration.
- `intent_activation_eval_cases.jsonl`: expected outcomes for account-level
  intent sequencing, competitive battlecards, public asset monitoring, and
  related model arbitration.

## Add a YAML Case

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
suite-specific expected fields for scorer behavior:

- `anti_qualification`: `anti_qual_label`, `confidence`, `ratio_approx`,
  `raises`
- `best_next_first_dollar`: `expected_order`, `score_min`, `score_max`,
  `confidence`, `score_breakdown`
- `board_vs_plan`: `set_a_pass_count`, `set_b_pass_count`, `delta_labels`,
  `largest_bucket`
- `forkability`: `must_include_slots`, `must_exclude_slots`,
  `theory_constants_include`

## Run Locally

```bash
python evals/run_evals.py
python -m unittest discover -s tests
```

`evals/run_evals.py` discovers every `evals/*/cases.yaml` file, runs the
corresponding scorer, prints a per-suite summary, and prints details for any
failed case. The unit test suite covers the JSONL workflow fixtures.

## Exit Codes

- `0`: all YAML cases passed
- `1`: one or more YAML cases failed
