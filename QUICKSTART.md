<!-- SPDX-License-Identifier: Apache-2.0 -->
# Quickstart

## 1. Prerequisites

- Python 3.10 or later.
- An Anthropic API key (`ANTHROPIC_API_KEY`).
- Optional credentials for any source systems you intend to wire up: Salesforce, Gong, Outreach, Slack, Google Drive.

## 2. Install

No external Python dependencies required. All agent and scorer modules use the standard library only.

## 3. Validate the Repo

Run the unit tests:

```bash
python -m unittest discover -s tests
```

Run the demo smoke checks:

```bash
python agents/anti_qualification_scorer/aq_scorer.py
python agents/signature_authority_miner/sec_edgar_fetcher.py
python agents/signature_authority_miner/signatory_extractor.py
python agents/trigger_event_monitor/earnings_parser.py
python agents/trigger_event_monitor/pre_announcement_watcher.py
python core/model_arbitration.py
python plugins/ae/best_next_first_dollar.py
python plugins/customer-success/renewal_radar.py
python plugins/revops/schema_health.py
python plugins/sales-leadership/board_vs_plan_scorer.py
python plugins/sales-leadership/pipeline_risk_radar.py
```

## 4. Cold-Start Interview

Copy `CLAUDE.md` to `CLAUDE.local.md`, then fill in the YAML block in the local copy. `CLAUDE.local.md` is ignored by git so local practice details do not get committed.

```bash
cp CLAUDE.md CLAUDE.local.md
```

See the interview prompts in `CLAUDE.md`. When running plugins, use `CLAUDE.local.md` if present and fall back to the template only for demos.
