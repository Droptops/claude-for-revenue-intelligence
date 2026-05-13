<!-- SPDX-License-Identifier: Apache-2.0 -->
# schema/persona_graph

Stores the influence map for an account: who matters, what role they play, and how they relate to one another. The schema is intentionally pseudonymous — `person_id` is an opaque key, and no real names appear in any committed file. Real names live only in the agent's local working store, keyed by `person_id`, and never round-trip through this repository.

## Columns

| column | type | source | nullable | verification_criteria |
|---|---|---|---|---|
| account_id | string | internal | no | matches an account in the CRM connector mapping |
| person_id | string (pseudonymous key) | persona-graph builder | no | stable per (account_id, person) pair; never a real name |
| person_role_label | string | extractor (title / signal) | no | normalized to a role taxonomy (e.g. ECONOMIC_BUYER, CHAMPION, TECHNICAL_EVALUATOR, BLOCKER, USER) |
| influence_tier | int (1–3) | scorer | no | 1 = decision authority, 2 = influencer, 3 = aware-but-peripheral |
| relationship_edges | JSON array of `{from_id, to_id, relationship_type}` | extractor | yes | every `from_id` / `to_id` references an existing `person_id` in scope |
| last_updated | timestamp (ISO-8601) | builder | no | UTC timestamp of most recent edit |
| data_source | string | builder | no | identifies the upstream signal: CRM, conversation_evidence, signature_authority, manual |

## Notes on data quality / known gaps

- `person_id` is the only key. Schema rows do not carry email addresses or names; those are stored locally in the agent's private working store.
- `relationship_type` values are not yet standardized. A controlled vocabulary lands when the role taxonomy stabilizes.
- `influence_tier` is a scorer output, not ground truth. It is drafted from observable signals (signature authority, meeting attendance, mentions in calls) and should be reviewed.
- The graph is sparse by design — only persons with at least one observed signal land here. Absence is not evidence of non-involvement.
- All outputs derived from this slot are drafts for reviewer judgment.
