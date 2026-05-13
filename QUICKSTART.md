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
python plugins/ae/best_next_first_dollar.py
python plugins/sales-leadership/board_vs_plan_scorer.py
```

## 4. Cold-Start Interview

Copy `CLAUDE.md` to `CLAUDE.local.md`, then fill in the YAML block in the local
copy. `CLAUDE.local.md` is ignored by git so local practice details do not get
committed.

```bash
cp CLAUDE.md CLAUDE.local.md
```

The interview now starts by selecting a skill. List installed motion skills with:

```bash
python -c "from skills.loader import list_available_skills; [print(f'{s.name}: {s.description}') for s in list_available_skills()]"
```

Write the selected identifier to the profile:

```yaml
active_skill: enterprise-account-based
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
