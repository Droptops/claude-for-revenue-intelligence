<!-- SPDX-License-Identifier: Apache-2.0 -->
# Quickstart

## 1. Prerequisites

- Python 3.10 or later.
- An Anthropic API key (`ANTHROPIC_API_KEY`) **only** if you run the Claude
  path of the signature-authority miner. Everything else runs on the standard
  library.

## 2. Install

No required external Python dependencies. Optional Claude integration:

```bash
pip install '.[llm]'    # adds anthropic>=0.40.0
```

## 3. Validate the repo

```bash
python -m unittest discover -s tests
python evals/run_evals.py
python evals/anti_qualification_cohort.py
```

## 4. Run the morning dossier on synthetic data

```bash
python demo/morning_dossier_demo.py
```

This composes the dossier end-to-end across the synthetic fixtures in
`demo/synthetic_data.py`. No network, no API key, no real names.

## 5. Smoke-check the agents and plugins

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

## 6. Cold-start interview

Create `CLAUDE.local.md` so the loader picks up local overrides. The file is
git-ignored.

```bash
python tools/cold_start.py
# or, non-interactive default:
python tools/cold_start.py --non-interactive --skill enterprise-account-based --force
python tools/inspect_skill.py
```

`skills/loader.py` reads `CLAUDE.local.md` and binds the active skill. If the
local profile is absent or has no `active_skill`, the loader falls back to
`enterprise-account-based`.

## 7. Run the Claude extractor (optional)

If `ANTHROPIC_API_KEY` is set, the `signatory_extractor` demo additionally
runs the Claude path on the synthetic filing:

```bash
export ANTHROPIC_API_KEY=...
python agents/signature_authority_miner/signatory_extractor.py
```

The Claude path uses ephemeral prompt caching on the system prompt so batch
runs over multiple filings amortize the instruction tokens.
