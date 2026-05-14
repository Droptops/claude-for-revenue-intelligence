<!-- SPDX-License-Identifier: Apache-2.0 -->
# plugins/sales-leadership

The sales-leadership plugin is the leader-shaped view over the active skill's
schema. It supports four modes:

- `VELOCITY`: TAM-velocity metrics for a segment, with a sensitivity note
  identifying which input metric moves overall velocity the most when shifted.
- `WIN_LOSS`: pattern refresh over closed-won and closed-lost cohorts, grouped
  by category labels from the active skill's conversation-evidence contract.
- `BOARD_DELTA`: deterministic constraint-filter comparison of an opportunity
  list under two constraint sets, typically current plan vs board ask.
- `PIPELINE_RISK`: deterministic inspection of deal risk flags for forecast
  hygiene.

The skill prompt is `SKILL.md`; the built scorers are
`board_vs_plan_scorer.py` and `pipeline_risk_radar.py`. Every output is a
**draft for reviewer judgment** and contains no customer, exec, or vendor names.

The `BOARD_DELTA` scorer is a deterministic constraint filter, not a constrained
optimizer. It answers which opportunities pass each set and where the deltas
fall, not what allocation maximizes revenue. Real constrained optimization is a
stretch goal, and the plugin says so if the operator asks for optimization.

The `PIPELINE_RISK` scorer surfaces stale next steps, missing buying authority,
repeated slips, low recent engagement, and political-cover patterns before a
forecast call. The plugin does not give financial or investment advice, does
not commit to forecasts, and takes no external action without explicit user
approval.

Run demos:

```bash
python plugins/sales-leadership/board_vs_plan_scorer.py
python plugins/sales-leadership/pipeline_risk_radar.py
```
