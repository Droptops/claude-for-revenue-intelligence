<!-- SPDX-License-Identifier: Apache-2.0 -->
# agents/

One agent per schema slot, plus a cross-slot `anti_qualification_scorer`. Agents have a single responsibility — populate or watch one part of the schema — and are designed to be readable in isolation.

Status values: `built` (directory present with a runnable demo), `stub` (directory present, scaffolding only), `planned` (no directory yet).

| Agent | File | Status |
|---|---|---|
| Signature Authority Miner | `signature_authority_miner/` | built |
| Persona Graph Builder | `persona_graph_builder/` | planned |
| Funnel Telemetry Loader | `funnel_telemetry_loader/` | planned |
| Outcome Telemetry Watcher | `outcome_telemetry_watcher/` | planned |
| Conversation Evidence Indexer | `conversation_evidence_indexer/` | planned |
| Trigger Event Monitor | `trigger_event_monitor/` | built |
| Anti-Qualification Scorer | `anti_qualification_scorer/` | built |
