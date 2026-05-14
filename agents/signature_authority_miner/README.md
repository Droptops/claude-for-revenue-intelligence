<!-- SPDX-License-Identifier: Apache-2.0 -->
# agents/signature_authority_miner

This agent ingests public SEC filings for a target account and extracts
signing-authority signals. In the reference skill, output flows into
`skills/enterprise-account-based/schema/signature_authority.md`, one row per
detected signatory, with `reviewer_verified` defaulting to `false`.

Every row is a **draft for reviewer judgment** until a human signs off. Real
executive or customer names do not appear in this repository; real names
extracted during a run go only to the agent's private working store, keyed by a
pseudonymous `person_id`.

## Verification Requirement

The extractor is a regex-and-heuristic stub. A `TODO` in
`signatory_extractor.py` flags the replacement work: a structured extraction
pass that lifts the confidence floor. Until that lands, every extracted row
should be treated as a candidate, not a fact. The active skill's schema contract
requires explicit human sign-off before `reviewer_verified` can become `true`.

## Disclaimer

SEC EDGAR is a public-data source and no authentication is required, but the
SEC's fair-use guidance asks aggregators to stay under 10 requests per second
and to identify themselves with a descriptive User-Agent. `sec_edgar_fetcher.py`
enforces the rate ceiling and the HTTP layer is deliberately not wired up in
this stub. All outputs are drafts for reviewer judgment.
