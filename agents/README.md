# agents/

One agent per schema slot, plus a cross-slot `anti_qualification_scorer`. Agents have a single responsibility — populate or watch one part of the schema — and are designed to be readable in isolation.

| Agent | File | Status |
|---|---|---|
| Signature Authority Miner | `signature_authority_miner/` | stub |
| Persona Graph Builder | `persona_graph_builder/` | stub |
| Funnel Telemetry Loader | `funnel_telemetry_loader/` | stub |
| Outcome Telemetry Watcher | `outcome_telemetry_watcher/` | stub |
| Conversation Evidence Indexer | `conversation_evidence_indexer/` | stub |
| Trigger Event Monitor | `trigger_event_monitor/` | stub |
| Anti-Qualification Scorer | `anti_qualification_scorer/` | stub |

Day 1 commits the table only. `signature_authority_miner` reaches a runnable stub in Day 2.
