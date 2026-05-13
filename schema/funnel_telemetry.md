<!-- SPDX-License-Identifier: Apache-2.0 -->
# schema/funnel_telemetry

Per-opportunity telemetry that supports clone-profile matching, anti-qualification scoring, and outlier detection. The slot is the input substrate for the AE plugin's Best Next First Dollar scorer and for sales-leadership rollups. Rows are written once per opportunity and updated as stages advance.

## Columns

| column | type | source | nullable | verification_criteria |
|---|---|---|---|---|
| opportunity_id | string | CRM | no | matches an opportunity in the CRM connector mapping |
| account_id | string | CRM | no | matches an account in the CRM connector mapping |
| first_contact_date | date | CRM / activity log | yes | first observed touch on the opportunity |
| touch_count | int | activity log | no | non-negative integer |
| days_to_close | int | derived | yes | populated only for closed opportunities |
| outcome | enum (CW / CL / OPEN) | CRM | no | CW = closed-won, CL = closed-lost, OPEN = in-flight |
| clone_profile_match | bool | clone scorer | no | true only when the account matches the closed-won clone profile derived from the practice profile |
| anti_clone_profile_match | bool | clone scorer | no | true only when the account matches the closed-lost anti-clone profile |
| anti_qualification_ratio | float | derived | yes | ratio of consulting/services spend to implementation/product spend on the deal |
| anti_qual_label | enum (POLITICAL_COVER / REAL_CHANGE / AMBIGUOUS) | derived | yes | derived from `anti_qualification_ratio` (see below) |
| stage_timestamps | JSON object `{stage_name: ISO-8601 timestamp}` | CRM | yes | every key is a known stage name |
| outlier_flag | bool | outlier detector | no | defaults to false |
| outlier_reason | string | outlier detector | yes | populated only when `outlier_flag = true` |

## Anti-qualification ratio: label assignment

- `anti_qualification_ratio > 3.0` → `POLITICAL_COVER`: heavy consulting / services spend relative to implementation. Buyer is purchasing political cover, not change.
- `anti_qualification_ratio < 1.5` → `REAL_CHANGE`: implementation-heavy spend. Buyer is actually deploying.
- `1.5 ≤ ratio ≤ 3.0` → `AMBIGUOUS`: insufficient signal to label.

The thresholds are the system default. Operators may override them in `CLAUDE.md` after running the cold-start interview question on their own closed-won cohort.

## Notes on data quality / known gaps

- `anti_qualification_ratio` is operator-supplied or computed from purchase-order data; it is not derivable from CRM alone.
- `clone_profile_match` and `anti_clone_profile_match` are scorer outputs and can both be false on the same row — a deal does not have to fit either profile.
- `outlier_flag` is intentionally lossy: it surfaces candidates for human review and is not a verdict.
- All outputs derived from this slot are drafts for reviewer judgment.
