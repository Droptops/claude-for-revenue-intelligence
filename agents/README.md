<!-- SPDX-License-Identifier: Apache-2.0 -->
# agents/

Agents are small modules that populate or watch schema slots from the active
skill. They should read schema contracts and theory constants through
`skills/loader.py`; do not hardcode motion-specific thresholds or slot sets in
agent code.

Status values: `built` (directory present with a runnable demo), `stub`
(directory present, scaffolding only), `planned` (no directory yet).

| Agent | Folder | Status |
|---|---|---|
| Signature Authority Miner | `signature_authority_miner/` | built |
| Persona Graph Builder | `persona_graph_builder/` | planned |
| Funnel Telemetry Loader | `funnel_telemetry_loader/` | planned |
| Outcome Telemetry Watcher | `outcome_telemetry_watcher/` | planned |
| Conversation Evidence Indexer | `conversation_evidence_indexer/` | planned |
| Trigger Event Monitor | `trigger_event_monitor/` | built |
| Anti-Qualification Scorer | `anti_qualification_scorer/` | built |
