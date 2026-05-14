<!-- SPDX-License-Identifier: Apache-2.0 -->
# Revenue Intelligence Design Notes

This repo does not try to clone a commercial revenue-intelligence platform. The
goal is to capture the enterprise workflows that are feasible to implement with
the existing six-slot schema and that can create practical impact quickly.

## Source-Backed Patterns

Public product docs and market pages cluster around a few durable patterns:

- Pipeline inspection: summarize forecast-category movement, pipeline change,
  and manager inspection views.
- Deal execution risk: surface active deal value, expected close date, sales
  methodology completeness, activity timelines, and risk assessments.
- Forecast confidence: use current and historical deal data to improve forecast
  hygiene and identify risk early.
- Retention and expansion: connect implementation outcomes, renewal signal,
  account activity, and trigger events.
- Evidence discipline: use call/activity references and summaries rather than
  treating polished narrative as source data.

## What Is Turnkey Here

The first enterprise-ready layer is deterministic and connector-ready:

1. `plugins/revops/schema_health.py`
   - Prevents expensive model synthesis over incomplete source rows.
   - Best first step for any enterprise because poor CRM hygiene breaks every
     downstream workflow.

2. `plugins/sales-leadership/pipeline_risk_radar.py`
   - Turns common forecast-review failure modes into visible flags.
   - Focuses on stale next steps, low engagement, repeated slips, missing
     authority, weak persona coverage, and political-cover patterns.

3. `plugins/customer-success/renewal_radar.py`
   - Separates churn-save motions from expansion motions.
   - Uses renewal timing, usage trend, support trend, implementation status,
     executive sponsor presence, contract diffs, and news sentiment labels.

4. `core/model_arbitration.py`
   - Adds token-aware model selection per workflow.
   - Uses relative cost tiers and context fit rather than hardcoded prices.
   - Recommends prompt caching for repeated account context when useful.

5. `evals/revenue_play_eval_cases.jsonl`
   - Provides deterministic eval fixtures for high-impact paths.
   - These fixtures validate routing/scoring behavior, not model quality.

## Model Selection Policy

The arbitration layer uses model families rather than brittle dated aliases:

- Haiku-class: schema checks, simple classifications, deterministic summaries.
- Sonnet-class: balanced synthesis across CRM, calls, trigger events, and
  account history.
- Opus-class: high-stakes executive forecast and renewal narratives where
  ambiguity or board-facing impact justifies the cost.
- Long-context Sonnet-class: large transcript packs, win/loss cohorts, or long
  account histories that exceed normal context.

The policy is deliberately conservative: spend cheap tokens first, fix missing
data before synthesis, then escalate visibly when stakes or ambiguity justify it.

## Public References

- Salesforce Pipeline Inspection documentation:
  https://help.salesforce.com/s/articleView?id=sales.pipeline_inspection_drive_revenue_using_parent.htm&type=5
- Salesforce Revenue Intelligence overview:
  https://www.salesforce.com/sales/revenue-intelligence/
- Gong deal intelligence explainer:
  https://help.gong.io/v1/docs/explainer-deal-intelligence
- Gong revenue forecasting overview:
  https://www.gong.io/platform/revenue-forecasting-software
- Clari Forecast overview:
  https://www.clari.com/products/forecast/
- Anthropic context-window documentation:
  https://docs.claude.com/en/docs/build-with-claude/context-windows
- Anthropic prompt-caching documentation:
  https://docs.claude.com/en/docs/build-with-claude/prompt-caching
