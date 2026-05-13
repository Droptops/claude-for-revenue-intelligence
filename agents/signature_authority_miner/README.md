<!-- SPDX-License-Identifier: Apache-2.0 -->
# agents/signature_authority_miner

This agent ingests public SEC filings (10-K and 10-Q exhibit indexes, DEF 14A proxy statements, 8-K filings) for a target account and extracts signing-authority signals. The output flows into `schema/signature_authority`, one row per detected signatory, with `reviewer_verified` defaulting to `false`. Every row is a **draft for reviewer judgment** until a human signs off.

## Data flow

```
operator-supplied (account_id, CIK)
        ↓
sec_edgar_fetcher.fetch_filings()      ← SEC EDGAR public API; ≤ 10 rps
        ↓ filing metadata + exhibit URLs
signatory_extractor.extract_signatories()   ← regex + heuristics
        ↓ rows (with real names)
agent.md normalization                  ← maps to schema columns
        ↓
        ┌─────────────────────────────────────────────────────────────┐
        │  schema/signature_authority   (placeholder token for name)  │
        │  private working store         (real name, keyed by pid)    │
        └─────────────────────────────────────────────────────────────┘
```

## Verification requirement

The extractor is a regex-and-heuristic stub. A `TODO` in `signatory_extractor.py` flags the replacement work — a structured LLM extraction pass — that lifts the confidence floor. Until that lands, every extracted row should be treated as a candidate, not a fact. The `reviewer_verified` column on `schema/signature_authority` does not flip to `true` without explicit human sign-off; the schema definition enforces this and the agent prompt repeats it. The `INFERRED` value of `authority_source` is reserved for cases where the filing names a signatory but no explicit authority text — those rows carry a lower confidence and require closer review.

## Disclaimer

No real executive or customer names appear in this repository. Real names extracted during a run go only to the agent's private working store, keyed by a pseudonymous `person_id`; the schema row stores a placeholder token. SEC EDGAR is a public-data source and no authentication is required, but the SEC's fair-use guidance asks aggregators to stay under 10 requests per second and to identify themselves with a descriptive User-Agent — `sec_edgar_fetcher.py` enforces the rate ceiling and the HTTP layer is deliberately not wired up in this stub. All outputs are drafts for reviewer judgment.
