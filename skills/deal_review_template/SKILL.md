<!-- SPDX-License-Identifier: Apache-2.0 -->
---
name: deal_review_template
description: Use when an operator needs a structured review of one active or recently closed opportunity.
purpose: >
  Provide a compact, source-bound deal review that an operator can fill in
  before deciding whether to advance, hold, or disqualify an opportunity.
  The template uses placeholders only and points each section back to the
  repository schema slots that should ground the review.
---

# Deal Review Template

## Deal Identifier

- Opportunity: `[OPPORTUNITY_LABEL]`
- Account: `[ACCOUNT_LABEL]`
- Review date: `[YYYY-MM-DD]`
- Reviewer: `[REVIEWER_LABEL]`

Use `schema/funnel_telemetry` for the opportunity identifier, stage, outcome,
and anti-qualification fields.

## Account Shape

- Segment: `[SEGMENT_LABEL]`
- Motion: `[MOTION_LABEL]`
- Observable size band: `[SIZE_BAND_LABEL]`
- Relevant cohort or clone profile: `[CLONE_PROFILE_LABEL]`

Use `schema/persona_graph` for influence coverage and
`schema/outcome_telemetry` for observed prior outcomes. Do not add real account
or person names to this review.

## Where The Deal Is

- Current stage: `[STAGE_LABEL]`
- Days in stage: `[DAYS_IN_STAGE]`
- Last touch: `[LAST_TOUCH_DATE_OR_AGE]`
- Funnel outlier flag: `[true|false]`
- Outlier reason: `[OUTLIER_REASON_OR_NONE]`

See `schema/funnel_telemetry` for `stage`, `days_in_stage`, `outlier_flag`,
and the opportunity's current status.

## Persona Coverage

- Tier 1 engaged: `[person_id, person_id]`
- Tier 1 dark or uncontacted: `[person_id, person_id]`
- Economic buyer status: `[ENGAGED|DARK|UNKNOWN]`
- Technical evaluator status: `[ENGAGED|DARK|UNKNOWN]`
- Missing influence tier: `[TIER_LABEL_OR_NONE]`

Use `schema/persona_graph` for `person_id`, `influence_tier`,
`relationship_edge`, and engagement status. Keep all references pseudonymous.

## Anti-Qualification Check

- Consulting spend: `[CONSULTING_SPEND_BAND]`
- Implementation spend: `[IMPLEMENTATION_SPEND_BAND]`
- Consulting / implementation ratio: `[RATIO_OR_UNDEFINED]`
- Anti-qualification label: `[POLITICAL_COVER|REAL_CHANGE|AMBIGUOUS]`
- Confidence: `[HIGH|MEDIUM|LOW]`

Use `schema/funnel_telemetry` for `anti_qualification_ratio` and
`anti_qual_label`. Treat the label as one signal, not a verdict.

## Recent Trigger Events

- Last 30 days:
  - `[EVENT_TYPE]` / `[SIGNAL_FAMILY]` from `schema/trigger_events`:
    `[PARAPHRASED_SIGNAL_SUMMARY]`
  - `[EVENT_TYPE]` / `[SIGNAL_FAMILY]` from `schema/trigger_events`:
    `[PARAPHRASED_SIGNAL_SUMMARY]`
- Unreviewed events: `[COUNT]`
- Reviewer action needed: `[YES|NO]`

Use `signal_summary` only as a paraphrase. Verify any important detail against
the `source_url` before acting.

## Open Risks

- Persona risk: `[RISK_OR_NONE]`
- Commercial risk: `[RISK_OR_NONE]`
- Timing risk: `[RISK_OR_NONE]`
- Evidence quality risk: `[RISK_OR_NONE]`
- Compliance or review gate: `[RISK_OR_NONE]`

Tie each risk to a schema slot where possible. If the signal is insufficient,
write `UNKNOWN` rather than filling the gap.

## Decision And Next Action

- Decision: `[ADVANCE|HOLD|DISQUALIFY]`
- One-sentence rationale: `[RATIONALE]`
- Next action: `[NEXT_ACTION]`
- Owner: `[OPERATOR_LABEL]`
- Due date: `[YYYY-MM-DD_OR_NONE]`

The decision should reflect the current evidence, anti-qualification check,
persona coverage, trigger events, and funnel telemetry. Do not send outreach or
write back to a system of record from this template.

Draft for reviewer judgment. Verify against source data before acting.
