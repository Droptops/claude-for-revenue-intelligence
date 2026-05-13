<!-- SPDX-License-Identifier: Apache-2.0 -->
# Architecture

This repository is split into a small base harness and motion-specific skills.
The design influence is the February 2026 Karpathy framing of a maximally
forkable repo whose skills fork it into exotic configurations. In this repo,
the forkable base is the agent harness; skills are the specialization unit.

## Base Harness

The base is intentionally small enough for a security or revenue team to read
end-to-end. It owns the durable pattern:

`schema -> agents -> persona plugins -> cookbooks -> connectors`

The base does not own a universal schema. It owns the loader and the execution
shape:

- `skills/loader.py` reads `CLAUDE.local.md`.
- `active_skill` selects a folder under `skills/`.
- The selected skill binds schema slots, agent roster, plugin defaults,
  cookbook set, connector bindings, and theory constants.
- Agents read those bindings at runtime.

This keeps `/agents/` motion-agnostic. An agent may know how to compute or
transform a signal, but it should not hardcode the business theory that decides
which threshold, slot set, or buying motion is universal.

## Skills

A skill is a self-contained specialization folder with a `SKILL.md` and schema
contracts. The required fields are:

- `name`
- `description`
- `schema_slots`
- `agent_roster`
- `plugin_defaults`
- `cookbook_set`
- `theory_constants`

The reference skill, `skills/enterprise-account-based/`, preserves the original
six-part revenue-intelligence schema:

- `signature_authority`
- `persona_graph`
- `funnel_telemetry`
- `outcome_telemetry`
- `conversation_evidence`
- `trigger_events`

The anti-qualification ratio is a good example of a skill-level theory
constant. It is useful for the enterprise account-based motion, so it lives in
`skills/enterprise-account-based/SKILL.md`. It is not a base schema contract.

## Creating A New Fork

Start from an example under `examples/forks/`:

1. Copy the nearest example folder into a new repository or a new folder under
   `skills/`.
2. Rename `SKILL.md` and update `name` and `description`.
3. Replace `schema_slots` with the slots your motion actually needs.
4. Add or remove agent names, plugin defaults, cookbooks, connectors, and theory
   constants.
5. Run the cold-start interview and set `active_skill` in `CLAUDE.local.md`.

The example forks are deliberately thin. They prove that the base can bind a
different schema and roster without adding motion assumptions to the harness.
When a fork graduates from stub to working configuration, add the minimum agent
code and tests needed for that motion, keeping reusable harness behavior in the
base.
