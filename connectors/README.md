<!-- SPDX-License-Identifier: Apache-2.0 -->
# connectors/

MCP connectors bind external systems of record to the active skill's schema.
Each connector exposes two adapters:

- a **read-only adapter** with `read_account(account_id: str) -> dict`, used by
  agents to populate schema slots
- a **write adapter** with `upsert_record(schema_slot: str, record: dict) ->
  bool`, used only when the operator has explicitly opted in

All connectors default to read-only. Write operations require explicit operator
opt-in through a per-connector configuration flag that defaults to `false`; no
connector is permitted to write on its own initiative.

`base.py` defines the tiny protocol. `mock.py` provides an in-memory connector
for tests and demos.

**Status: no production connectors built yet.** The reference skill lists
planned integrations for Salesforce, Gong, Outreach, Slack, and Google Drive.
Forks may bind different connector names in their own `SKILL.md`.
