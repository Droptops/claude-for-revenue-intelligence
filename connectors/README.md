<!-- SPDX-License-Identifier: Apache-2.0 -->
# connectors/

MCP connectors bind external systems of record to the six-part schema. Each connector exposes two adapters:

- a **read-only adapter** with a `read_account(account_id: str) -> dict` interface, used by agents to populate schema slots, and
- a **write adapter** with an `upsert_record(schema_slot: str, record: dict) -> bool` interface, used only when the operator has explicitly opted in.

All connectors default to read-only. Write operations require explicit operator opt-in — they are gated behind a per-connector configuration flag that defaults to `false`, and no connector is permitted to write on its own initiative.

**Status: no connectors built yet.** Planned integrations: Salesforce, Gong, Outreach, Slack, Google Drive.
