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

Column-level contracts live in each slot's Markdown file under `schema/`.
A slot-level manifest is synthesized at load time from `SKILL.md`; there is
no separate `manifest.json` to keep in sync.

## Installed motion skills

- [`enterprise-account-based`](enterprise-account-based/SKILL.md) — the
  default reference skill. Six-slot enterprise schema with anti-qualification
  theory constants.

## Legacy operator template

`deal_review_template` remains in place for compatibility. It is a reusable
operator output template, not a motion-specialization skill, and is
intentionally not loaded by `skills/loader.py`.
