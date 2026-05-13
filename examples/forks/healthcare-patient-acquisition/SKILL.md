<!-- SPDX-License-Identifier: Apache-2.0 -->
+++
{
  "name": "healthcare-patient-acquisition",
  "description": "Use this stub fork for healthcare patient-acquisition motions where referral authority, episode telemetry, and outcome evidence replace enterprise account and funnel assumptions.",
  "schema_slots": [
    { "name": "referral_authority", "path": "schema/referral_authority.md" },
    { "name": "episode_telemetry", "path": "schema/episode_telemetry.md" },
    { "name": "outcome_evidence", "path": "schema/outcome_evidence.md" }
  ],
  "agent_roster": [
    "referral_authority_mapper_stub",
    "episode_telemetry_loader_stub",
    "outcome_evidence_monitor_stub"
  ],
  "plugin_defaults": [
    "practice-growth",
    "operations"
  ],
  "cookbook_set": [
    "referral_dossier_stub",
    "episode_outcome_review_stub"
  ],
  "connector_bindings": [
    "crm",
    "ehr-summary",
    "call-center"
  ],
  "theory_constants": {
    "patient_acquisition": {
      "referral_staleness_days": 90,
      "minimum_episode_volume": 20
    }
  }
}
+++

# Healthcare Patient Acquisition Fork Stub

This example changes the slot set around referral authority, episode telemetry,
and outcome evidence. It is a proof of shape, not a complete healthcare system.
Any real deployment must add local compliance review and data-handling controls.
