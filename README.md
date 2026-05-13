<!-- SPDX-License-Identifier: Apache-2.0 -->
# claude-for-revenue-intelligence

claude-for-revenue-intelligence is a reference data model and Claude agent implementation for revenue intelligence workflows. The repository is organized around a six-part schema; agents, plugins, and cookbooks read from and write to that schema. Nothing here is a vendor product or a commercial benchmark — it is a reference implementation meant to be read end-to-end and adapted.

## Six-Part Data Model

The schema is the headline. Each slot is a column-level data contract under `/schema/`. Agents and plugins consume these contracts; if the contracts change, the rest of the system follows.

- **`signature_authority`** — actual signatory data from public SEC filings and contract corpora; pen-on-paper authority, not titles.
- **`persona_graph`** — relationship and influence map per account; who decides, who blocks, who champions, and how those edges are observed.
- **`funnel_telemetry`** — first-contact date, touch count, days to close, opportunity counter, outlier filter. Includes an anti-qualification column: `anti_qualification_ratio`. The ratio is computed as `consulting_spend / implementation_spend`. A ratio greater than 3 marks a political-cover buyer; less than 1.5 marks a real-change buyer. The column is meant to short-circuit pursuits that look qualified by activity but are not qualified by intent.
- **`outcome_telemetry`** — post-implementation news, contract diffs, renewal signals; the schema slot that tells you whether the deal you closed actually became a customer.
- **`conversation_evidence`** — call references (Gong/Chorus-compatible), closed-lost post-mortems, feature-gap flags. Pointers, not transcripts, so the schema remains source-of-truth-neutral.
- **`trigger_events`** — earnings language, hiring signals, exec movement, regulatory filings, competitor signals. Timestamped and source-linked.

Column-level contracts and verification criteria live in [`schema/`](schema/README.md).

## Agents

Each agent populates or watches a specific schema slot. One responsibility per agent.

- **Signature Authority Miner** — populates `signature_authority` from public filings and contract corpora.
- **Persona Graph Builder** — assembles `persona_graph` per account.
- **Funnel Telemetry Loader** — loads `funnel_telemetry` from CRM and outreach systems.
- **Outcome Telemetry Watcher** — watches news / filings / contract diffs and writes to `outcome_telemetry`.
- **Conversation Evidence Indexer** — indexes call references into `conversation_evidence`.
- **Trigger Event Monitor** — emits records into `trigger_events` from configured sources.
- **Anti-Qualification Scorer** — computes the consulting/implementation spend ratio and writes it to `funnel_telemetry`.

See [`agents/`](agents/README.md).

## Plugins

Plugins are persona-shaped views over the same schema. They do not introduce new data; they assemble role-specific summaries.

- **`ae`** — account-executive-shaped views (target account dossier, next-best action).
- **`sales-leadership`** — pipeline-level views, anti-qualification cohort reporting.
- **`revops`** — schema health, source quality, coverage gaps.
- **`customer-success`** — renewal risk and expansion-fit radar.
- **`growth`** — market-share posture, campaign ROI/payback, search intent, category-demand capture, and intent-to-sequence drafting.
- **`competitive-intel`** — competitor signals, battlecards, and permitted public asset-change review.

See [`plugins/`](plugins/README.md).

## Cookbooks

End-to-end workflows that compose agents and plugins. Each cookbook is meant to be a readable example, not a packaged product.

- **Morning dossier** — daily per-account briefing assembled across all six schema slots.
- **Revenue command center** — weekly forecast / daily inspection loop that runs schema health, pipeline risk, renewal/expansion radar, and model arbitration.
- **Growth command center** — category-demand, campaign ROI, and search-intent loop for market creation and capture.
- **Intent activation and competitive response** — high-intent account routing, compliant sequence draft, battlecard, and public asset-change review.
- **Pre-announcement watcher** — flags publicly observable pre-announcement signals (earnings cadence, hiring, exec movement, regulatory filings). (cookbook planned; see `agents/trigger_event_monitor/pre_announcement_watcher.py` for the agent module)
- **Signal velocity monitor** — tracks rate-of-change on `trigger_events` and `outcome_telemetry` per account.
- **Renewal radar** — assembles `outcome_telemetry` and `funnel_telemetry` into renewal-risk surfacing.
- **Win/loss interview integrator** — folds post-mortem interview notes into `conversation_evidence`.

See [`cookbooks/`](cookbooks/README.md).

## MCP Connectors

Connector stubs for the systems the agents read from and write to:

- Salesforce
- Gong
- Outreach
- Slack
- Google Drive

Connector contracts live under [`connectors/`](connectors/README.md). Stubs only at Day 1; concrete bindings follow in later milestones.

## Getting Started

See [QUICKSTART.md](QUICKSTART.md) for prerequisites, validation, and the cold-start interview that produces a per-installation `CLAUDE.local.md` practice profile.

## Validation

The repository has no required third-party Python dependencies. Run the unit tests with:

```bash
python -m unittest discover -s tests
```

The GitHub Actions workflow in `.github/workflows/validate.yml` runs the same tests plus smoke checks for every built agent and plugin demo.

## Model Arbitration

`core/model_arbitration.py` provides a token-aware routing policy for each built workflow. It picks the smallest Claude model tier that satisfies context size, reasoning need, relative cost band, and high-stakes escalation flags. This keeps cheap deterministic checks on a fast model path while preserving an explicit escalation route for board-facing forecast or renewal narratives.

Design rationale and public reference links live in [`docs/revenue_intelligence_design_notes.md`](docs/revenue_intelligence_design_notes.md), [`docs/growth_intelligence_design_notes.md`](docs/growth_intelligence_design_notes.md), and [`docs/intent_activation_design_notes.md`](docs/intent_activation_design_notes.md).

## Roadmap

- **Day 1.** Repo skeleton: six-part schema slots, agent / plugin / cookbook / connector stubs, README + QUICKSTART + CLAUDE.md scaffold.
- **Day 2.** Schema column contracts for all six slots; cold-start interview that writes a per-installation `CLAUDE.md` practice profile; first agent (`signature_authority_miner`) reaches a runnable stub.
- **Day 3.** First end-to-end cookbook (morning dossier) reads from at least three schema slots; AE plugin Best Next First Dollar scorer; sales-leadership plugin with board-vs-plan delta scorer; trigger-event monitor and anti-qualification scorer agents. MCP connector stubs deferred; see `connectors/README.md` for planned integrations.

## Disclaimers

- **Drafts, not decisions.** All agent and cookbook outputs are drafts intended for human reviewer judgment. Nothing here claims completeness or accuracy.
- **Not advice.** Outputs do not constitute legal, financial, or investment advice.
- **Web monitoring compliance.** Pre-announcement-watcher and any similar feature that observes external sites must be used in compliance with each target site's `robots.txt` and Terms of Service. No unauthorized scraping is performed or condoned.
- **No embedded customer or executive data.** This repository contains no customer names, executive names, or proprietary methodology references. Anything operator-specific belongs in the cold-start `CLAUDE.md` practice profile produced locally, not in this repo.
