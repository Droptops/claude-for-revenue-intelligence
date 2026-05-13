# schema/

The `/schema` directory contains column-level data contracts for each of the six schema slots. Each file defines column names, data sources, verification criteria, and nullability. These contracts are the primary interface consumed by agents and plugins; if a contract changes, the downstream consumers follow.

## Schema slots

| Schema | File | Status |
|---|---|---|
| signature_authority | `signature_authority.md` | stub |
| persona_graph | `persona_graph.md` | stub |
| funnel_telemetry | `funnel_telemetry.md` | stub |
| outcome_telemetry | `outcome_telemetry.md` | stub |
| conversation_evidence | `conversation_evidence.md` | stub |
| trigger_events | `trigger_events.md` | stub |

Day 1 commits the table only. Column-level contracts land in Day 2.
