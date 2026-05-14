<!-- SPDX-License-Identifier: Apache-2.0 -->
# Evals

The evals are deterministic behavior checks for scorer outputs. Unit tests
verify code paths and implementation details. Evals verify that known input
cases continue to produce the same labels, scores, ordering, and delta buckets
that an operator would expect from the current heuristics.

The runner is stdlib-only. The case files use a small YAML subset parsed by
`evals/run_evals.py`: dictionaries, lists, strings, numbers, booleans, and
nulls. This keeps local and CI execution dependency-free.

## Add a Case

Each suite has an `evals/<suite>/cases.yaml` file. Add one top-level list item
per case:

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
```

The runner discovers every `evals/*/cases.yaml` file, runs the corresponding
scorer, prints a per-suite summary, and prints details for any failed case.

## Exit Codes

- `0`: all cases passed
- `1`: one or more cases failed
