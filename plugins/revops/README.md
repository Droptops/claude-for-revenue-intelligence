<!-- SPDX-License-Identifier: Apache-2.0 -->
# plugins/revops

RevOps views over schema health, connector coverage, and data-quality blockers.
The first built module is `schema_health.py`, a deterministic gate that checks
whether required fields are populated before higher-cost model synthesis runs.

Run the demo:

```bash
python plugins/revops/schema_health.py
```
