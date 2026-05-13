# claude-for-revenue-intelligence

claude-for-revenue-intelligence is a reference data model and Claude agent implementation for revenue intelligence workflows. The repository is organized around a six-part schema; agents, plugins, and cookbooks read from and write to that schema. Nothing here is a vendor product or a commercial benchmark — it is a reference implementation meant to be read end-to-end and adapted.

## Six-Part Data Model

The schema is the headline. Each slot is a column-level data contract under `/schema/`. Agents and plugins consume these contracts; if the contracts change, the rest of the system follows.

- **`signature_authority`** — actual signatory data from public SEC filings and contract corpora; pen-on-paper authority, not titles.
- **`persona_graph`** — relationship and influence map per account; who decides, who blocks, who champions, and how those edges are observed.
- **`funnel_telemetry`** — first-contact date, touch count, days to close, opportunity counter, outlier filter. Includes an anti-qualification column: `consulting_to_implementation_spend_ratio`. A ratio greater than 3 marks a political-cover buyer; less than 1.5 marks a real-change buyer. The column is meant to short-circuit pursuits that look qualified by activity but are not qualified by intent.
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
- **`competitive-intel`** — competitor signals from `trigger_events` and `outcome_telemetry`.

See [`plugins/`](plugins/README.md).

## Cookbooks

End-to-end workflows that compose agents and plugins. Each cookbook is meant to be a readable example, not a packaged product.

- **Morning dossier** — daily per-account briefing assembled across all six schema slots.
- **Pre-announcement watcher** — flags publicly observable pre-announcement signals (earnings cadence, hiring, exec movement, regulatory filings).
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

See [QUICKSTART.md](QUICKSTART.md) for prerequisites, install, and the cold-start interview that produces a per-installation `CLAUDE.md` practice profile.

## Roadmap

- **Day 1.** Repo skeleton: six-part schema slots, agent / plugin / cookbook / connector stubs, README + QUICKSTART + CLAUDE.md scaffold. (This commit.)
- **Day 2.** Schema column contracts for all six slots; cold-start interview that writes a per-installation `CLAUDE.md` practice profile; first agent (`signature_authority_miner`) reaches a runnable stub.
- **Day 3.** First end-to-end cookbook (morning dossier) reads from at least three schema slots; first MCP connector stub becomes a runnable read-only adapter.

## Disclaimers

- **Drafts, not decisions.** All agent and cookbook outputs are drafts intended for human reviewer judgment. Nothing here claims completeness or accuracy.
- **Not advice.** Outputs do not constitute legal, financial, or investment advice.
- **Web monitoring compliance.** Pre-announcement-watcher and any similar feature that observes external sites must be used in compliance with each target site's `robots.txt` and Terms of Service. No unauthorized scraping is performed or condoned.
- **No embedded customer or executive data.** This repository contains no customer names, executive names, or proprietary methodology references. Anything operator-specific belongs in the cold-start `CLAUDE.md` practice profile produced locally, not in this repo.
