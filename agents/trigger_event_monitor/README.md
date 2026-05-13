<!-- SPDX-License-Identifier: Apache-2.0 -->
# agents/trigger_event_monitor

This agent surfaces account-level events that may warrant outreach or reprioritization. It normalizes signals from earnings transcripts, hiring shifts, executive movements, regulatory filings, and pre-announcement web artifacts into rows in `schema/trigger_events`. Every row is emitted with `reviewed = false` and `flagged_for_action = false`; downstream consumers must not act on unreviewed rows. The agent never hardcodes vendor or competitor names — those come from the operator's local `plugins/competitive-intel/competitor_list.yaml`, which is not committed to this repository.

## Modules

- `earnings_parser.py` — keyword-heuristic scan of transcripts for expansion, contraction, and urgency language. Confidence is capped at `0.7` because keyword heuristics are noisy.
- `pre_announcement_watcher.py` — static-endpoint diff (sitemap.xml, robots.txt, /careers/, /newsroom/, /investor-relations/) plus a Wayback Machine availability lookup. The HTTP layer is deliberately not wired up in this stub — `live=True` raises `NotImplementedError` — to prevent accidental fetches against any domain whose ToS or robots.txt compliance has not been confirmed by the caller.

## Web-monitoring compliance

This agent's web-monitoring features must be used in compliance with each target site's `robots.txt` and Terms of Service. This system does not endorse or facilitate unauthorized scraping or access. The compliance check is the caller's responsibility — the watcher will not perform it. The `compliance_note` field on every `watch_static_endpoints` and `fetch_wayback_diff` return value is a permanent reminder of this.

## Disclaimer

All emitted rows are **drafts for reviewer judgment**. Earnings-language rows are paraphrased summaries, not transcript quotes. Pre-announcement signals are inherently noisy — confidence biases `LOW` unless multiple independent endpoints corroborate. No customer, exec, or vendor names appear in any output. The Wayback Machine availability API is public and unauthenticated; the caller is still bound by archive.org fair-use guidance.
