<!-- SPDX-License-Identifier: Apache-2.0 -->
+++
{
  "name": "finserv-enterprise",
  "description": "Use this stub fork for regulated financial-services enterprise motions where the reference account-based model still fits, but regulatory filings and review gates deserve first-class emphasis.",
  "schema_slots": [
    { "name": "signature_authority", "path": "schema/signature_authority.md" },
    { "name": "persona_graph", "path": "schema/persona_graph.md" },
    { "name": "funnel_telemetry", "path": "schema/funnel_telemetry.md" },
    { "name": "outcome_telemetry", "path": "schema/outcome_telemetry.md" },
    { "name": "conversation_evidence", "path": "schema/conversation_evidence.md" },
    { "name": "trigger_events", "path": "schema/trigger_events.md" },
    { "name": "regulatory_filings", "path": "schema/regulatory_filings.md" }
  ],
  "agent_roster": [
    "signature_authority_miner",
    "persona_graph_builder",
    "funnel_telemetry_loader",
    "outcome_telemetry_watcher",
    "conversation_evidence_indexer",
    "trigger_event_monitor",
    "regulatory_filing_monitor_stub"
  ],
  "plugin_defaults": [
    "ae",
    "sales-leadership",
    "competitive-intel"
  ],
  "cookbook_set": [
    "morning_dossier",
    "regulatory_review_dossier_stub"
  ],
  "connector_bindings": [
    "salesforce",
    "gong",
    "sec-edgar",
    "regulatory-news"
  ],
  "theory_constants": {
    "anti_qualification": {
      "ratio_formula": "consulting_spend / implementation_spend",
      "political_cover_min": 3.0,
      "real_change_max": 1.5
    }
  }
}
+++

# Finserv Enterprise Fork Stub

This example keeps the reference six-slot enterprise model and adds a
regulatory-filings emphasis. It is intentionally thin: use it as a starting
overlay, then fill in the schema contracts, agents, and cookbooks locally.
