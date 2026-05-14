<!-- SPDX-License-Identifier: Apache-2.0 -->
# Quickstart

## 1. Prerequisites

- Python 3.10 or later.
- An Anthropic API key (`ANTHROPIC_API_KEY`) if you run Claude-backed flows.
- Optional credentials for source systems you intend to wire up: Salesforce,
  Gong, Outreach, Slack, Google Drive, or fork-specific connectors.

## 2. Install

No external Python dependencies are required. All agent, loader, and scorer
modules use the standard library only.

## 3. Validate The Repo

Run the unit tests:

```bash
python -m unittest discover -s tests
```

Run the evals:

```bash
python evals/run_evals.py
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
python plugins/competitive-intel/battlecard_builder.py
python plugins/competitive-intel/cdn_feature_monitor.py
python plugins/growth/market_share_tracker.py
python plugins/growth/campaign_roi_tracker.py
python plugins/growth/search_intent_mapper.py
python plugins/growth/intent_sequence_builder.py
python plugins/revops/schema_health.py
python plugins/sales-leadership/board_vs_plan_scorer.py
python plugins/sales-leadership/pipeline_risk_radar.py
```

## 4. Cold-Start Interview

Run the cold-start helper to create `CLAUDE.local.md`. The file is ignored by
git so local practice details do not get committed.

```bash
python tools/cold_start.py
```

For a non-interactive default install:

```bash
python tools/cold_start.py --non-interactive --skill enterprise-account-based --force
```

List installed motion skills and bindings with:

```bash
python tools/inspect_skill.py
```

When agents run, `skills/loader.py` reads `CLAUDE.local.md`, loads the selected
skill, and binds:

- schema slots
- agent roster
- plugin defaults
- cookbook set
- connector bindings
- theory constants

If `CLAUDE.local.md` is absent or has no `active_skill`, the loader falls back to
`enterprise-account-based`.

See the interview prompts in `CLAUDE.md`. When running plugins, use
`CLAUDE.local.md` if present and fall back to the template only for demos.

## 5. Create A New Skill From An Example

Copy an example fork into a new installed skill:

```bash
python tools/new_skill.py plg-self-serve skills/my-plg-motion
```

Then set `active_skill: my-plg-motion` in `CLAUDE.local.md` and inspect it:

```bash
python tools/inspect_skill.py
```

The PLG example has a tiny runnable demo:

```bash
python examples/forks/plg-self-serve/demo.py
```
