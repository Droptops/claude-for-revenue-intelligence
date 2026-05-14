<!-- SPDX-License-Identifier: Apache-2.0 -->
# claude-for-revenue-intelligence

`claude-for-revenue-intelligence` is a small, readable agent harness for
schema-driven revenue intelligence. It is designed to be forked and specialized
through skills: the base stays motion-agnostic, while each skill binds schema
slots, agent roster, persona plugin defaults, cookbook set, connector bindings,
and motion-specific theory constants.

Nothing here is a vendor product or a commercial benchmark. It is a reference
implementation meant to be read end-to-end and adapted.

## The Pattern

The harness follows this flow:

`schema -> agents -> persona plugins -> cookbooks -> connectors`

- **Schema**: column contracts supplied by the active skill.
- **Agents**: small modules that populate or watch schema slots.
- **Persona plugins**: role-shaped views over the same skill-bound schema.
- **Cookbooks**: end-to-end workflows that compose agents and plugins.
- **Connectors**: read/write adapters for systems of record, defaulting to
  read-only.

The loader at `skills/loader.py` reads `CLAUDE.local.md`, selects the active
skill, and exposes the bindings agents need. If no local profile exists, the
loader falls back to `enterprise-account-based`.

## How To Specialize

Run the cold-start interview in `QUICKSTART.md` and choose an installed skill,
or fork one of the examples under `examples/forks/`.

A specialization lives in a folder with a `SKILL.md` and its own schema
contracts. The base harness should not hardcode motion assumptions; it should
read schema slots and theory constants from the active skill.

Executable helpers make that loop concrete:

```bash
python tools/inspect_skill.py
python tools/cold_start.py --non-interactive --skill enterprise-account-based --profile-path CLAUDE.local.md
python tools/new_skill.py plg-self-serve skills/my-plg-motion
```

`inspect_skill.py` prints the active bindings. `cold_start.py` writes a local
practice profile. `new_skill.py` copies an example fork into a new skill folder.

## Reference Skill

The default reference skill is:

- `skills/enterprise-account-based/`

This is the original six-part model, relocated without changing its semantics.
It remains the default behavior for current agents, plugins, demos, and evals.

## Example Forks

Stub overlays demonstrate that the harness can bind very different motions:

- `examples/forks/finserv-enterprise/`: current six-part model plus regulatory
  filings emphasis.
- `examples/forks/plg-self-serve/`: product usage, activation events, and
  expansion signals.
- `examples/forks/healthcare-patient-acquisition/`: referral authority, episode
  telemetry, and outcome evidence.

The examples intentionally do not implement full agents.

## Reference Skill Slots

The `enterprise-account-based` skill supplies these schema slots:

- **`signature_authority`**: actual signatory data from public SEC filings and
  contract corpora; pen-on-paper authority, not titles.
- **`persona_graph`**: relationship and influence map per account; who decides,
  who blocks, who champions, and how those edges are observed.
- **`funnel_telemetry`**: first-contact date, touch count, days to close,
  opportunity counter, outlier filter, and the anti-qualification ratio. The
  ratio formula and thresholds are skill-level theory constants.
- **`outcome_telemetry`**: post-implementation news, contract diffs, renewal
  signals; the slot that tells you whether the deal you closed actually became
  a customer.
- **`conversation_evidence`**: call references, closed-lost post-mortems, and
  feature-gap flags. Pointers, not transcripts.
- **`trigger_events`**: earnings language, hiring signals, executive movement,
  regulatory filings, competitor signals, and pre-announcement signals.

Column-level contracts live in `skills/enterprise-account-based/schema/`.
The root `schema/README.md` explains why schema contracts now live per skill.
Each schema directory also carries a `manifest.json` so tests and tools can
validate slot contracts without scraping Markdown tables.

## Agents

Each agent populates or watches a skill-bound schema slot. One responsibility
per agent.

- **Signature Authority Miner**: populates `signature_authority` from public
  filings and contract corpora.
- **Persona Graph Builder**: assembles `persona_graph` per account.
- **Funnel Telemetry Loader**: loads `funnel_telemetry` from CRM and outreach
  systems.
- **Outcome Telemetry Watcher**: watches news, filings, and contract diffs into
  `outcome_telemetry`.
- **Conversation Evidence Indexer**: indexes call references into
  `conversation_evidence`.
- **Trigger Event Monitor**: emits records into `trigger_events`.
- **Anti-Qualification Scorer**: computes the consulting/implementation spend
  ratio using thresholds from the active skill.

See `agents/`.

## Plugins

Plugins are persona-shaped views over the active skill's schema. They do not
introduce new data; they assemble role-specific summaries.

- **`ae`**: account-executive-shaped views, including target-account dossiers
  and next-best action scoring.
- **`sales-leadership`**: pipeline-level views, board-vs-plan deltas,
  anti-qualification cohort reporting, and pipeline risk inspection.
- **`revops`**: schema health, source quality, and coverage gaps.
- **`customer-success`**: renewal risk and expansion-fit radar.
- **`growth`**: market-share posture, campaign ROI/payback, search intent,
  category-demand capture, and intent-to-sequence drafting.
- **`competitive-intel`**: competitor signals, battlecards, and permitted
  public asset-change review.

See `plugins/`.

## Cookbooks

Cookbooks are readable workflows that compose agents and plugins.

- **Morning dossier**: daily per-account briefing assembled across the
  reference skill slots.
- **Revenue command center**: weekly forecast and daily inspection loop that
  runs schema health, pipeline risk, renewal/expansion radar, and model
  arbitration.
- **Growth command center**: category-demand, campaign ROI, and search-intent
  loop for market creation and capture.
- **Intent activation and competitive response**: high-intent account routing,
  compliant sequence drafts, battlecards, and public asset-change review.
- **Pre-announcement watcher**: planned workflow for publicly observable
  pre-announcement signals.
- **Signal velocity monitor**: planned rate-of-change workflow.
- **Renewal radar**: planned renewal-risk workflow.
- **Win/loss interview integrator**: planned post-mortem workflow.

See `cookbooks/`.

## Connectors

Connector stubs bind systems of record to the active skill's schema. The
minimal code contract lives in `connectors/base.py`, with an in-memory test
connector in `connectors/mock.py`.

Reference connector names include Salesforce, Gong, Outreach, Slack, Google
Drive, 6sense, ZoomInfo, Search Console, GA4, and ad platforms. Connectors
default to read-only. Write operations require explicit operator opt-in. Forks
may bind different connector names in their own `SKILL.md`.

See `connectors/`.

## Getting Started

See `QUICKSTART.md` for prerequisites, validation, and the cold-start interview
that produces a per-installation `CLAUDE.local.md` practice profile with an
`active_skill`.

## Validation

The repository has no required third-party Python dependencies. Run:

```bash
python -m unittest discover -s tests
python evals/run_evals.py
python tools/inspect_skill.py --json
python examples/forks/plg-self-serve/demo.py
```

The GitHub Actions workflow in `.github/workflows/validate.yml` runs the tests,
evals, forkability tool checks, and smoke checks for every built agent and
plugin demo.

## Model Arbitration

`core/model_arbitration.py` provides a token-aware routing policy for each built
workflow. It picks the smallest Claude model tier that satisfies context size,
reasoning need, relative cost band, and high-stakes escalation flags. This
keeps cheap deterministic checks on a fast model path while preserving an
explicit escalation route for board-facing forecast or renewal narratives.

Design rationale and public reference links live in
[`docs/revenue_intelligence_design_notes.md`](docs/revenue_intelligence_design_notes.md),
[`docs/growth_intelligence_design_notes.md`](docs/growth_intelligence_design_notes.md),
and
[`docs/intent_activation_design_notes.md`](docs/intent_activation_design_notes.md).

## Roadmap

- **Day 1.** Repo skeleton: schema slots, agent / plugin / cookbook /
  connector stubs, README + QUICKSTART + CLAUDE.md scaffold.
- **Day 2.** Schema column contracts, cold-start profile workflow, and first
  runnable agent stub.
- **Day 3.** Morning dossier, AE and sales-leadership scorers, trigger-event
  monitor, anti-qualification scorer, and deferred connector stubs.
- **Day 4.** Skills make the harness motion-agnostic; example forks prove that
  the base can bind different slot sets without hardcoding a motion.
- **Day 5.** Enterprise revenue, growth, intent activation, competitive
  response, and forkability tooling make the repo executable end to end.

## Contributing

See `CONTRIBUTING.md` for repository scope, what does and does not belong here,
and the pull-request checklist. Operator-specific data belongs in
`CLAUDE.local.md` and other locally ignored files, not in this repository.

## Influences And Prior Art

This repository draws on the public discourse of revenue-intelligence product
categories, the public canon of sales qualification and methodology, and
adjacent buyer-behavior analysis traditions. The current architecture is also
influenced by the February 2026 Karpathy framing of a maximally forkable repo
whose skills fork it into exotic configurations.

## Disclaimers

- **Drafts, not decisions.** All agent and cookbook outputs are drafts intended
  for human reviewer judgment. Nothing here claims completeness or accuracy.
- **Not advice.** Outputs do not constitute legal, financial, or investment
  advice.
- **Web monitoring compliance.** Pre-announcement-watcher and any similar
  feature that observes external sites must be used in compliance with each
  target site's `robots.txt` and Terms of Service. No unauthorized scraping is
  performed or condoned.
- **No embedded customer or executive data.** This repository contains no
  customer names, executive names, or proprietary methodology references.
  Anything operator-specific belongs in the cold-start `CLAUDE.local.md`
  practice profile produced locally, not in this repo.
