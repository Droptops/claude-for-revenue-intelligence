<!-- SPDX-License-Identifier: Apache-2.0 -->
# schema/trigger_events

A normalized log of account-level events that may justify outreach or reprioritization. Each row is one observed signal, classified by type, with a source URL, an extractor-supplied confidence score, and a reviewer flag. The slot is consumed by the AE plugin's sequence mode and by sales-leadership rollups.

## Columns

| column | type | source | nullable | verification_criteria |
|---|---|---|---|---|
| event_id | string | extractor | no | stable, globally unique within the repository |
| account_id | string | internal | no | matches an account in the CRM connector mapping |
| event_type | enum (EARNINGS_LANGUAGE / HIRING_SIGNAL / EXEC_MOVEMENT / REGULATORY_FILING / COMPETITOR_SIGNAL / PRE_ANNOUNCEMENT) | classifier | no | one of the listed values |
| event_date | date | source | no | date the underlying event occurred or was published |
| signal_summary | string | extractor | no | paraphrased summary, not a verbatim quote |
| source_url | string (URL) | extractor | yes | resolvable URL to the source artifact |
| confidence_score | float (0.0–1.0) | extractor | no | extractor's self-reported confidence; not a calibrated probability |
| reviewed | bool | reviewer | no | defaults to false; flips to true only after human review |
| flagged_for_action | bool | reviewer | no | reviewer marker that this signal warrants downstream action |

## Pre-announcement signal class

`event_type = PRE_ANNOUNCEMENT` covers signals that surface before a public announcement. Typical input streams include diffs of public web artifacts — `sitemap.xml`, `robots.txt`, Wayback Machine snapshots, public CDN paths — that change shape ahead of a launch.

**All web monitoring must comply with each target site's `robots.txt` and Terms of Service.** This system does not endorse or facilitate unauthorized scraping, credential reuse, bypassing of access controls, or any other activity that exceeds the access the target site has explicitly granted to the public. Operators are responsible for confirming the legal and contractual status of any monitoring they configure.

## Notes on data quality / known gaps

- `confidence_score` is the extractor's self-report. It is useful for ranking, not for absolute decisions.
- `signal_summary` is paraphrased; the `source_url` is authoritative for the underlying text.
- `flagged_for_action` is a reviewer flag, not a scorer output. Unflagged rows should not drive automated outreach.
- The event-type taxonomy is intentionally small; new types are added only when an existing type would meaningfully misclassify a row.
- All outputs derived from this slot are drafts for reviewer judgment.
