<!-- SPDX-License-Identifier: Apache-2.0 -->
# agents/trigger_event_monitor

This agent surfaces account-level events that may warrant outreach or
reprioritization. It normalizes signals from earnings transcripts, hiring
shifts, executive movements, regulatory filings, and pre-announcement web
artifacts into the active skill's trigger-events slot. For the reference skill,
that contract is
`skills/enterprise-account-based/schema/trigger_events.md`.

Every row is emitted with `reviewed = false` and `flagged_for_action = false`;
downstream consumers must not act on unreviewed rows. The agent never hardcodes
vendor or competitor names. Those come from an operator-local list (e.g.
`competitor_list.local.yaml`) which is git-ignored by the `*.local.yaml`
pattern in `.gitignore`.

## Modules

- `earnings_parser.py` - keyword-heuristic scan of transcripts for expansion,
  contraction, and urgency language. Confidence is capped at `0.7` because
  keyword heuristics are noisy.
- `pre_announcement_watcher.py` - static-endpoint diff plus Wayback Machine
  availability lookup. The HTTP layer is deliberately not wired up in this
  stub: `live=True` raises `NotImplementedError`.

## Web-Monitoring Compliance

This agent's web-monitoring features must be used in compliance with each target
site's `robots.txt` and Terms of Service. This system does not endorse or
facilitate unauthorized scraping or access. The compliance check is the caller's
responsibility.

## Disclaimer

All emitted rows are **drafts for reviewer judgment**. Earnings-language rows
are paraphrased summaries, not transcript quotes. Pre-announcement signals are
inherently noisy. No customer, exec, or vendor names appear in any output.
