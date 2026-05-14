<!-- SPDX-License-Identifier: Apache-2.0 -->
# Persona Dossier - [ACCOUNT_LABEL]

> Template. Fill the placeholders. Do not substitute real account or person
> names. Use `[ACCOUNT_LABEL]` and `person_id` values from the active skill's
> `persona_graph` slot. Every section below is a draft for reviewer judgment.

## Account Overview

- **Account label:** `[ACCOUNT_LABEL]`
- **Segment / shape:** _(short descriptor: segment, motion, observable size band)_
- **Opportunity state:** _(OPEN / CW / CL, plus stage if OPEN)_
- **Last reviewed:** _(YYYY-MM-DD)_

## Influence Tier 1 (Decision Authority)

List each person from the active skill's `persona_graph` where
`influence_tier = 1`.

| person_id | role_label | engagement_status |
|---|---|---|
| `[person_id]` | _(role label, e.g. ECONOMIC_BUYER)_ | _(ENGAGED / DARK / UNCONTACTED)_ |
| `[person_id]` | | |

## Influence Tier 2 (Influencers)

| person_id | role_label | engagement_status |
|---|---|---|
| `[person_id]` | _(e.g. CHAMPION, TECHNICAL_EVALUATOR)_ | |
| `[person_id]` | | |

## Influence Tier 3 (Aware-But-Peripheral)

| person_id | role_label | engagement_status |
|---|---|---|
| `[person_id]` | _(e.g. USER, OBSERVER)_ | |

## Key Relationships

List relationships from the `relationship_edges` array in the active skill's
`persona_graph`. Use `person_id`s only.

- `[from_id]` -> `[to_id]`: _(relationship_type, e.g. REPORTS_TO, PEER_OF, BLOCKED_BY)_
- `[from_id]` -> `[to_id]`: _(relationship_type)_

## Open Questions / Gaps

Enumerate what is unknown. The dossier is most useful when the gaps are
explicit.

- _(e.g. economic buyer not yet identified)_
- _(e.g. champion engaged, but no tier-1 contact)_
- _(e.g. no trigger event observed in the last 60 days)_

## Recommended Next Action

A single concrete next step. This is a **draft**. The reviewer must approve
before any action is taken on the account.

- **Action:** _(one sentence: what to do)_
- **Why:** _(one sentence: what signal supports it)_
- **Approval required from:** _(reviewer role)_

---

_Draft for reviewer judgment. Verify against source data before acting._
