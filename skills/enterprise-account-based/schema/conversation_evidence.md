<!-- SPDX-License-Identifier: Apache-2.0 -->
# enterprise-account-based/schema/conversation_evidence

An index over call recordings and their post-mortems. The slot stores summaries only — verbatim transcripts and raw audio do not enter this repository. Closed-lost post-mortems are structured to make patterns greppable across a cohort without exposing transcript content.

## Columns

| column | type | source | nullable | verification_criteria |
|---|---|---|---|---|
| account_id | string | internal | no | matches an account in the CRM connector mapping |
| opportunity_id | string | CRM | no | matches an opportunity in the CRM connector mapping |
| call_ref_id | string | call platform | no | stable platform-provided identifier for the call |
| call_platform | enum (GONG / CHORUS / OTHER) | connector | no | matches a configured call connector |
| call_date | date | call platform | no | date the call occurred |
| transcript_excerpt_summary | string | summarizer | yes | paraphrased summary; verbatim transcript text is not stored in this schema |
| closed_lost_postmortem | JSON `{primary_reason, secondary_reasons[], feature_gaps[], competitor_named (bool)}` | reviewer / summarizer | yes | populated only when the parent opportunity is closed-lost |
| indexed_at | timestamp (ISO-8601) | indexer | no | UTC timestamp of indexing pass |

## Closed-lost post-mortem structure

- `primary_reason` is a single normalized label (e.g. PRICE, FIT, TIMING, CHAMPION_LOST, INCUMBENT, NO_DECISION).
- `secondary_reasons` is a list of zero or more labels from the same vocabulary.
- `feature_gaps` is a list of capability-category labels (no vendor names — capability categories only).
- `competitor_named` is a boolean. Specific competitor identities, if needed, live in the competitive-intel plugin's local store, not in this schema.

## Notes on data quality / known gaps

- Verbatim transcripts are intentionally absent. Anything that requires reading raw transcript text must hit the call platform directly through its connector, with the operator's credentials and the platform's audit trail.
- `closed_lost_postmortem` is most reliable when populated by a reviewer immediately after the loss is recorded. Summarizer-populated rows should be treated as drafts.
- Feature-gap labels are a controlled vocabulary; ad-hoc strings should be normalized before insertion.
- All outputs derived from this slot are drafts for reviewer judgment.
