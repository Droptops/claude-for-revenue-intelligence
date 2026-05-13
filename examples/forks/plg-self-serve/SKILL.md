<!-- SPDX-License-Identifier: Apache-2.0 -->
+++
{
  "name": "plg-self-serve",
  "description": "Use this stub fork for product-led self-serve revenue motions where product usage, activation, and expansion signals matter more than enterprise buying-committee evidence.",
  "schema_slots": [
    { "name": "product_usage_telemetry", "path": "schema/product_usage_telemetry.md" },
    { "name": "activation_events", "path": "schema/activation_events.md" },
    { "name": "expansion_signals", "path": "schema/expansion_signals.md" }
  ],
  "agent_roster": [
    "product_usage_loader_stub",
    "activation_event_monitor_stub",
    "expansion_signal_scorer_stub"
  ],
  "plugin_defaults": [
    "growth",
    "customer-success"
  ],
  "cookbook_set": [
    "activation_review_stub",
    "expansion_queue_stub"
  ],
  "connector_bindings": [
    "product-analytics",
    "billing",
    "workspace-admin"
  ],
  "theory_constants": {
    "activation": {
      "target_first_value_days": 7,
      "expansion_signal_min_active_users": 5
    }
  }
}
+++

# PLG Self-Serve Fork Stub

This example replaces the enterprise six-slot model with a product-led slot
set. It is intentionally a stub: the point is to show that the base harness can
bind a different schema and roster without changing base agents.
