<!-- SPDX-License-Identifier: Apache-2.0 -->
+++
{
  "name": "enterprise-account-based",
  "description": "Use this skill for enterprise account-based revenue intelligence motions where the operator needs account-level authority, persona, funnel, outcome, conversation, and trigger-event evidence before prioritizing pursuits or renewals.",
  "schema_slots": [
    { "name": "signature_authority", "path": "schema/signature_authority.md" },
    { "name": "persona_graph", "path": "schema/persona_graph.md" },
    { "name": "funnel_telemetry", "path": "schema/funnel_telemetry.md" },
    { "name": "outcome_telemetry", "path": "schema/outcome_telemetry.md" },
    { "name": "conversation_evidence", "path": "schema/conversation_evidence.md" },
    { "name": "trigger_events", "path": "schema/trigger_events.md" }
  ],
  "agent_roster": [
    "signature_authority_miner",
    "persona_graph_builder",
    "funnel_telemetry_loader",
    "outcome_telemetry_watcher",
    "conversation_evidence_indexer",
    "trigger_event_monitor",
    "anti_qualification_scorer"
  ],
  "plugin_defaults": [
    "ae",
    "sales-leadership",
    "revops",
    "competitive-intel"
  ],
  "cookbook_set": [
    "morning_dossier",
    "pre_announcement_watcher",
    "signal_velocity_monitor",
    "renewal_radar",
    "win_loss_interview_integrator"
  ],
  "connector_bindings": [
    "salesforce",
    "gong",
    "outreach",
    "slack",
    "google-drive"
  ],
  "theory_constants": {
    "anti_qualification": {
      "ratio_formula": "consulting_spend / implementation_spend",
      "political_cover_min": 3.0,
      "real_change_max": 1.5,
      "political_cover_label": "POLITICAL_COVER",
      "real_change_label": "REAL_CHANGE",
      "ambiguous_label": "AMBIGUOUS"
    }
  }
}
+++

# Enterprise Account-Based Revenue Intelligence

This is the reference skill for the repository. It preserves the original
six-part schema and the current agent/plugin/cookbook behavior, but moves the
motion-specific contract into a self-contained specialization unit.

The anti-qualification ratio is intentionally a skill-level theory constant.
It is useful for this enterprise account-based motion, but it is not a base
harness contract and should not be hardcoded in agent modules.

All outputs remain drafts for reviewer judgment. This skill contains no
customer names, executive names, deal names, credentials, or embedded operator
data.
