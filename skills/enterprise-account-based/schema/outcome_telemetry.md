<!-- SPDX-License-Identifier: Apache-2.0 -->
# enterprise-account-based/schema/outcome_telemetry

Tracks what happens after the contract is signed: implementation progress, post-sale news signals, contract diffs, and renewal indicators. The slot is the bridge between booked revenue and retained revenue. Web-monitoring inputs that contribute to this slot must respect each target site's `robots.txt` and Terms of Service.

## Columns

| column | type | source | nullable | verification_criteria |
|---|---|---|---|---|
| account_id | string | internal | no | matches an account in the CRM connector mapping |
| opportunity_id | string | CRM | no | matches the closed-won opportunity that produced the implementation |
| implementation_start_date | date | CRM / project log | yes | non-null once kickoff is recorded |
| news_signals | JSON array of `{date, headline_summary, sentiment}` | news monitor | yes | `sentiment` ∈ {POSITIVE, NEGATIVE, NEUTRAL}; `headline_summary` is a paraphrase, not the raw headline |
| contract_diff_detected | bool | contract monitor | no | true only when a structural diff is observed against the last-indexed contract version |
| contract_diff_summary | string | contract monitor | yes | paraphrased summary; no verbatim contract clauses are stored |
| renewal_signal | enum (STRONG / WEAK / NONE / UNKNOWN) | scorer | no | UNKNOWN is the safe default when signal quality is insufficient |
| last_monitored_at | timestamp (ISO-8601) | monitor | no | UTC timestamp of most recent monitor pass |
| monitor_source | string | monitor | no | identifies the upstream monitor: news_api, contract_monitor, cdn_monitor, manual |

## Notes on data quality / known gaps

- News-signal sentiment is a model output, not editorial judgment. Treat aggregate trends, not individual rows, as the signal.
- `contract_diff_summary` is paraphrased. The repository does not store verbatim contract text.
- `renewal_signal` is a coarse scorer and biases toward `UNKNOWN`. Treat `STRONG` as a prompt to investigate, not a verdict.
- All web-monitoring inputs that contribute to this slot must comply with each target site's `robots.txt` and Terms of Service. This system does not endorse or facilitate unauthorized scraping.
- All outputs derived from this slot are drafts for reviewer judgment.
