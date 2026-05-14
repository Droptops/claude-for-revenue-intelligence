<!-- SPDX-License-Identifier: Apache-2.0 -->
# Skills

Skills are the specialization unit for the harness. A motion skill lives under
`/skills/<skill-name>/` and contains a `SKILL.md` with JSON front matter plus
the schema contracts it binds.

Required `SKILL.md` fields:

- `name`
- `description`
- `schema_slots`
- `agent_roster`
- `plugin_defaults`
- `cookbook_set`
- `theory_constants`

Optional but supported:

- `connector_bindings`

The loader in `skills/loader.py` reads the selected skill from
`CLAUDE.local.md` and falls back to `enterprise-account-based` when no local
selection exists.

Every motion skill schema directory should include `manifest.json`, a
machine-readable summary of the slot names and columns. Markdown remains the
human-readable contract; the manifest gives tests and tools something stable to
validate.

## Installed Motion Skills

- [`enterprise-account-based`](enterprise-account-based/SKILL.md): the original
  six-part revenue-intelligence model, now packaged as the default reference
  skill.

## Example Fork Stubs

- [`finserv-enterprise`](../examples/forks/finserv-enterprise/): current
  six-part model plus regulatory-filings emphasis.
- [`plg-self-serve`](../examples/forks/plg-self-serve/): product usage,
  activation events, and expansion signals.
- [`healthcare-patient-acquisition`](../examples/forks/healthcare-patient-acquisition/):
  referral authority, episode telemetry, and outcome evidence.

## Legacy Operator Template

`deal_review_template` remains in place for compatibility. It is a reusable
operator output template, not a motion-specialization skill, and is intentionally
not loaded by `skills/loader.py`. It is a candidate for relocation to
`cookbooks/` in a follow-up after its references and intended ownership are
reviewed.
