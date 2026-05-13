<!-- SPDX-License-Identifier: Apache-2.0 -->
# plugins/sales-leadership

The sales-leadership plugin is the leader-shaped view over the active skill's
schema. It supports three modes:

- `VELOCITY`: TAM-velocity metrics for a segment.
- `WIN_LOSS`: pattern refresh over closed-won and closed-lost cohorts, grouped
  by category labels from the active skill's conversation-evidence contract.
- `BOARD_DELTA`: deterministic constraint-filter comparison of an opportunity
  list under two constraint sets.

The skill prompt is `SKILL.md`; the scorer is `board_vs_plan_scorer.py`. Every
output is a **draft for reviewer judgment** and contains no customer, exec, or
vendor names.

The `BOARD_DELTA` scorer is a **deterministic constraint filter, not a
constrained optimizer**. It answers which opportunities pass each set and where
the deltas fall, not what allocation maximizes revenue. The plugin does not give
financial or investment advice, does not commit to forecasts, and takes no
external action without explicit user approval.

Run the scorer standalone with:

```bash
python plugins/sales-leadership/board_vs_plan_scorer.py
```
