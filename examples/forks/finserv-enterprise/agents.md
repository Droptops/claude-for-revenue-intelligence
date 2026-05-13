<!-- SPDX-License-Identifier: Apache-2.0 -->
# Agent Roster

- `signature_authority_miner`
- `persona_graph_builder`
- `funnel_telemetry_loader`
- `outcome_telemetry_watcher`
- `conversation_evidence_indexer`
- `trigger_event_monitor`
- `regulatory_filing_monitor_stub`

Only the roster is defined here. Implementations should stay in the base
`agents/` harness or in a fork-local agent directory when the fork graduates
from stub to working configuration.
