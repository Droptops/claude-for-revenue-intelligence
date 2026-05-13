<!-- SPDX-License-Identifier: Apache-2.0 -->
# schema/

The `/schema` directory contains column-level data contracts for each of the six schema slots. Each file defines column names, data sources, verification criteria, and nullability. These contracts are the primary interface consumed by agents and plugins; if a contract changes, the downstream consumers follow.

Status values: `built` (column-level contract present), `stub` (file present, scaffolding only), `planned` (file not yet written).

## Schema slots

| Schema | File | Status |
|---|---|---|
| signature_authority | `signature_authority.md` | built |
| persona_graph | `persona_graph.md` | built |
| funnel_telemetry | `funnel_telemetry.md` | built |
| outcome_telemetry | `outcome_telemetry.md` | built |
| conversation_evidence | `conversation_evidence.md` | built |
| trigger_events | `trigger_events.md` | built |

All schema contracts are current as of Day 2.
