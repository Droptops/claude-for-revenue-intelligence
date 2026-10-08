<!-- SPDX-License-Identifier: Apache-2.0 -->
# Contributing

This repository is an independent reference implementation. It is intended to be readable end-to-end, adaptable by any operator, and bound to no specific employer, vendor, customer, or commercial methodology. Contributions must preserve that scope.

## Provenance

Code and documentation in this repository should reflect the contributor's own independent work, developed on personal time and personal hardware, without reference to confidential materials of any employer or third party. Contributors are responsible for confirming the provenance of their contributions before submitting them. If a piece of work originated inside an employer's environment, against an employer's data, or as a derivative of an employer's methodology, it does not belong here — even if the surface text is paraphrased.

## What belongs in this repository

- Generic data contracts that any operator could adopt.
- Agent and plugin implementations that run without operator-specific data.
- Cookbooks that compose the above using placeholder identifiers (`[ACCOUNT_LABEL]`, `person_id`, `opportunity_id`).
- Documentation that explains the system in operator-neutral terms.
- Synthetic demo data — fully invented, not anonymized real data.

## What does not belong in this repository

- Customer names, account names, deal names, or opportunity names.
- Executive names, employee names, contact names.
- Vendor names or specific competitor names (use category labels only).
- Internal codenames, project names, or program names from any organization.
- Internal methodologies, frameworks, processes, or schemas from any organization — including verbatim text, close paraphrase, or 1:1 mirrors with renamed fields.
- Confidential financial figures, compensation data, or pricing.
- Verbatim transcript text, contract clauses, or filing text.
- Credentials, tokens, API keys, or connection strings.
- Operator practice profiles — these belong in `CLAUDE.local.md`, which is ignored by git.

The `.gitignore` enforces some of this mechanically. The rest is enforced by reviewer judgment.

## Operator-specific data: where it goes

Everything operator-specific belongs in files that are never committed:

- `CLAUDE.local.md` — your filled-in practice profile (ignored).
- `*.local.yaml`, `*.local.yml`, `*.local.json` — any local config including
  competitor lists, account watchlists, etc. (ignored).
- `.env`, `.env.*` — credentials (ignored).

If a piece of information is specific to one operator, one company, or one deal, it goes in a local file. A contribution that puts operator-specific data into the repository will be rejected.

## Naming

Names of agents, plugins, scorers, and schema slots should describe the function in operator-neutral terms. Avoid names that could be read as branded, internal, or proprietary to any organization. When in doubt, choose the more generic name.

## Pull request checklist

Before opening a pull request, confirm:

- [ ] No real names (customer, exec, employee, contact, vendor) appear in any file.
- [ ] No internal codenames or project names appear in any file.
- [ ] No internal methodologies, frameworks, or schemas are introduced as named contributions.
- [ ] No credentials or secrets are committed.
- [ ] No verbatim third-party text (transcripts, contracts, filings) is included.
- [ ] New examples and demo data are synthetic.
- [ ] New disclaimers preserve the "draft for reviewer judgment" pattern where applicable.
- [ ] The change is consistent with the Provenance section above.

## License

By contributing, you agree your contributions are licensed under the repository's Apache-2.0 license.
