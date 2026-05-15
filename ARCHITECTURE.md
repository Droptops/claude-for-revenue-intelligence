<!-- SPDX-License-Identifier: Apache-2.0 -->
# Architecture

A small base harness and one motion-specific skill. The design intent: keep
the base small enough to read end-to-end, then specialize one slot at a time.
See [`docs/WHY.md`](docs/WHY.md) for the rationale.

## Base harness

The base owns the loader and the execution shape:

`schema -> agents -> persona plugins -> cookbooks -> connectors`

- `skills/loader.py` reads `CLAUDE.local.md` and resolves the active skill.
- `active_skill` selects a folder under `skills/`.
- The selected skill binds schema slots, agent roster, plugin defaults,
  cookbook set, connector bindings, and theory constants.
- Agents read those bindings at runtime via `agents/runtime.py`.

The base does not hardcode motion assumptions. An agent may know how to
compute or transform a signal, but the business theory that decides which
threshold or slot set applies lives in the skill.

## Skills

A skill is a self-contained specialization folder with a `SKILL.md`. The
required JSON front matter fields are:

- `name`
- `description`
- `schema_slots`
- `agent_roster`
- `plugin_defaults`
- `cookbook_set`
- `theory_constants`

The reference skill, `skills/enterprise-account-based/`, defines the six-slot
schema (`signature_authority`, `persona_graph`, `funnel_telemetry`,
`outcome_telemetry`, `conversation_evidence`, `trigger_events`) and the
anti-qualification theory constants.

Column-level contracts live in per-slot Markdown files in
`skills/enterprise-account-based/schema/`. A machine-readable slot manifest is
synthesized at load time from `SKILL.md`; there is no separate `manifest.json`
to keep in sync.

## Agents and the Claude path

Most agents are deterministic transforms over schema rows. One agent,
`signature_authority_miner`, has both a deterministic regex baseline and a
Claude-backed extractor that calls the Anthropic Messages API with ephemeral
prompt caching on the system prompt.

The Claude path is opt-in: the `anthropic` SDK is an optional dependency
(`pip install '.[llm]'`), and the regex baseline is what tests exercise.

## Model arbitration

`core/model_arbitration.py` is a token-aware router. Given a workflow name,
estimated input tokens, and optional `high_stakes` / `evidence_conflict`
flags, it returns the smallest Claude tier that satisfies the policy. Six
workflows are wired:

- `schema_health_gate`
- `pipeline_risk_radar`
- `renewal_expansion_radar`
- `win_loss_pattern_miner`
- `executive_forecast_memo`
- `signature_authority_extraction`

The router returns a model name and a `prompt_cache_recommended` boolean. It
does not make API calls.

## Evals

Two harnesses run side by side:

- `evals/run_evals.py` walks `evals/<suite>/cases.yaml` and asserts each case
  against its scorer (deterministic correctness — every case is unit-test
  shaped).
- `evals/anti_qualification_cohort.py` generates 200 synthetic deals with
  planted buyer intent and reports precision / recall / F1 for the scorer's
  `POLITICAL_COVER` predictions. The cohort is seeded; output is
  deterministic. CI gates on a sanity F1 floor, not a calibration claim.

## Why so few moving parts

The harness was deliberately trimmed to one motion, one workflow, and one
heuristic that's measured against a synthetic cohort. Adding a second motion,
second workflow, or second cohort eval should be earned by a real need —
not by symmetry.
