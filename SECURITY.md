# Security Policy

This project is a reference implementation for revenue-intelligence workflows. Real deployments may connect to CRM, call-recording, or other business systems, so public examples must stay separated from customer data and credentials.

## Reporting

Do not publish credentials, private URLs, customer records, sales-call transcripts, or exploit details in a public issue. Use GitHub private vulnerability reporting when available. If private reporting is unavailable, open a minimal issue without sensitive details and request a private channel.

## Data handling

- Keep filled-in practice profiles in `CLAUDE.local.md`; the committed `CLAUDE.md` is a template only.
- Keep connector credentials in local/provider-managed secret stores, never source files.
- Do not commit real customer names, executive names, deal names, call transcripts, CRM exports, account IDs, or proprietary pipeline data.
- Use synthetic or explicitly redistributable fixtures in examples and tests.
- Do not commit API keys, populated `.env` files, private keys, session URLs, or private drafting artifacts.

If sensitive material is accidentally committed, rotate or revoke it where possible and evaluate both Git history and merged pull-request refs; deleting the working-tree file alone is not a complete remediation.
