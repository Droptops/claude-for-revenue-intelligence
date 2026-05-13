<!-- SPDX-License-Identifier: Apache-2.0 -->
# Revenue Command Center

This cookbook composes the highest-impact, most feasible revenue-intelligence
loops in this repo. It is designed for a weekly forecast meeting or daily
manager inspection, using only data that most enterprise revenue teams already
have: CRM opportunity fields, activity timestamps, call evidence pointers,
renewal fields, support trend labels, and product usage trend labels.

## Workflow

1. **RevOps schema health gate**
   - Run `plugins/revops/schema_health.py`.
   - If a slot is `RED`, fix connector/source data before spending model tokens
     on executive synthesis.
   - Default model policy: `schema_health_gate` routes to `claude-haiku`.

2. **Pipeline risk radar**
   - Run `plugins/sales-leadership/pipeline_risk_radar.py`.
   - Inspect high-risk commit deals first: stale next step, low recent
     engagement, no champion, no economic buyer, unverified signatory, repeated
     close-date slips, or political-cover pattern.
   - Default model policy: `pipeline_risk_radar` routes to `claude-sonnet`, with
     escalation when a large commit deal has conflicting evidence.

3. **Renewal and expansion radar**
   - Run `plugins/customer-success/renewal_radar.py`.
   - Separate save motions from growth motions. A churn-risk account should not
     be treated like an expansion candidate until the save motion is clear.
   - Default model policy: `renewal_expansion_radar` routes to `claude-sonnet`,
     with escalation for high-risk renewal narratives.

4. **Executive forecast memo**
   - Only after schema health and pipeline risk triage are complete, synthesize
     a short executive narrative from the reviewed rows.
   - Default model policy: `executive_forecast_memo` routes to `claude-opus`
     for board-facing or material forecast decisions.

## Model Arbitration

All built workflows call `core/model_arbitration.py`. The arbitration model uses:

- estimated input and output tokens
- workflow reasoning requirement
- context-window fit
- relative cost tier
- prompt-cache suitability
- high-stakes and conflicting-evidence escalation flags

The goal is not to maximize model quality at any cost. The goal is to use the
smallest model class that is good enough for the workflow, then visibly escalate
when stakes or ambiguity justify it.

## Eval Coverage

The fixtures in `evals/revenue_play_eval_cases.jsonl` cover:

- a high-risk commit deal
- a clean best-case deal
- a save-motion renewal account
- an expansion-fit account
- a schema-health data-quality miss
- low-cost and high-stakes model arbitration paths

Run:

```bash
python -m unittest discover -s tests
```

All outputs are drafts for reviewer judgment. The system does not take external
actions, update CRM, or issue forecasts on its own.
