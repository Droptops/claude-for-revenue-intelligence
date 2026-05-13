<!-- SPDX-License-Identifier: Apache-2.0 -->
# schema/signature_authority

Captures who can sign what, on behalf of which legal entity, up to which dollar threshold. The slot is populated by parsing public filings (SEC EDGAR Material Contracts exhibits, DEF 14A proxy statements, 8-K filings) and contract corpora. Every row is treated as a programmatic extraction until a human reviewer marks it verified. Rows without `reviewer_verified = true` must not be used to drive outreach or commercial decisions.

## Columns

| column | type | source | nullable | verification_criteria |
|---|---|---|---|---|
| account_id | string | internal | no | matches an account in the CRM connector mapping |
| legal_entity_name | string | filing / contract header | no | matches the entity named on the filing's cover page |
| signatory_name | string (placeholder) | filing signature block | yes | placeholder only — populated with a tokenized label, never a real name in committed data |
| signatory_title | string | filing signature block | yes | title text present on the filing |
| signing_threshold_usd | number | inferred from contract or policy | yes | a value is acceptable only when an explicit threshold is named in source text |
| authority_source | enum (SEC_EDGAR / DEF14A / 8K / CONTRACT_CORPUS / INFERRED) | extractor | no | one of the listed values |
| filing_url | string (URL) | extractor | yes | resolvable URL to the source filing |
| extracted_at | timestamp (ISO-8601) | extractor | no | UTC timestamp |
| confidence_score | float (0.0–1.0) | extractor | no | extractor's self-reported confidence, not a calibrated probability |
| reviewer_verified | bool | reviewer | no | defaults to `false`; flips to `true` only after a human reviewer signs off |

## Notes on data quality / known gaps

- All signatories are extracted programmatically. Treat unverified rows as hypotheses, not facts.
- Real signatory names are never committed to this repository. Production deployments substitute names locally; this schema reserves the column for that local substitution.
- `signing_threshold_usd` is sparsely populated; most filings name a signatory without naming a dollar threshold. Do not infer one without explicit source text.
- `INFERRED` rows (authority_source = INFERRED) require a higher bar of reviewer scrutiny than any of the filing-backed sources.
- All outputs derived from this slot are drafts for reviewer judgment.
