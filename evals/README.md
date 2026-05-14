<!-- SPDX-License-Identifier: Apache-2.0 -->
# evals

Small deterministic eval fixtures for the built revenue-intelligence modules.
These are not benchmarks and do not claim model performance. They are guardrail
cases for the repo's routing and scoring logic.

## Files

- `revenue_play_eval_cases.jsonl`: expected outcomes for pipeline risk, renewal
  radar, schema health, and model arbitration.
- `growth_eval_cases.jsonl`: expected outcomes for market-share posture,
  campaign ROI, search intent, and growth model arbitration.
- `intent_activation_eval_cases.jsonl`: expected outcomes for account-level
  intent sequencing, competitive battlecards, public asset monitoring, and
  related model arbitration.

Run the test suite:

```bash
python -m unittest discover -s tests
```
