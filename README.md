<!-- SPDX-License-Identifier: Apache-2.0 -->
# claude-for-revenue-intelligence

A small, readable agent harness for enterprise account-based revenue
intelligence. One workflow (the **morning dossier**), one heuristic that earns
its keep (**anti-qualification ratio**), one agent that actually calls Claude
(**signature_authority_miner**).

The repo is meant to be read end-to-end and adapted. It is not a vendor
product. Every output is a draft for human reviewer judgment.

See [`docs/WHY.md`](docs/WHY.md) for the one-page rationale.

## The shape

```
schema -> agents -> persona plugins -> cookbooks -> connectors
```

- **Schema**: six column contracts supplied by the active skill.
- **Agents**: small modules that populate or watch schema slots.
- **Plugins**: role-shaped views over the schema (AE, sales-leadership, revops,
  customer-success).
- **Cookbooks**: end-to-end workflows that compose agents and plugins.
- **Connectors**: read/write adapters to systems of record, defaulting to
  read-only.

`skills/loader.py` reads `CLAUDE.local.md` and binds the active skill's
contracts at runtime. If no local profile exists, the default skill is
`enterprise-account-based`.

## The headline workflow

`cookbooks/morning_dossier.md` defines the morning dossier: a one-page
briefing for an AE's priority accounts assembled from overnight trigger
events, persona-graph gaps, funnel outliers, and anti-qualification labels.

Run the synthetic demo end-to-end:

```bash
python demo/morning_dossier_demo.py
```

The dossier ends with recommended next actions. It does not act. No emails are
sent; no CRM rows are written.

## The schema (enterprise-account-based)

Six slots, contracted per skill. Column-level contracts live in
[`skills/enterprise-account-based/schema/`](skills/enterprise-account-based/schema/).

- **`signature_authority`** — pen-on-paper authority from public filings.
- **`persona_graph`** — relationship and influence map per account.
- **`funnel_telemetry`** — opportunity-level facts: dates, touches, ratios,
  outlier flags.
- **`outcome_telemetry`** — post-close signals: implementation start, contract
  diffs, renewal posture.
- **`conversation_evidence`** — call references and closed-lost post-mortems.
- **`trigger_events`** — earnings language, hiring, executive movement,
  filings, pre-announcement signals.

## Agents

| Agent | Slot it populates |
|---|---|
| `signature_authority_miner` | `signature_authority` |
| `persona_graph_builder` | `persona_graph` |
| `funnel_telemetry_loader` | `funnel_telemetry` |
| `outcome_telemetry_watcher` | `outcome_telemetry` |
| `conversation_evidence_indexer` | `conversation_evidence` |
| `trigger_event_monitor` | `trigger_events` |
| `anti_qualification_scorer` | computes the ratio over `funnel_telemetry` |

Most agents are deterministic transforms over schema data. The exception is
**`signature_authority_miner`**, which has two paths:

- **Regex baseline** (`signatory_extractor.extract_signatories`) — no
  dependencies, no API key, used by tests.
- **Claude path** (`signatory_extractor.extract_signatories_claude`) — calls
  the Anthropic Messages API with ephemeral prompt caching on the system
  prompt. Requires `pip install '.[llm]'` and `ANTHROPIC_API_KEY`.

## Plugins

Role-shaped views over the schema. They do not introduce new data.

- **`ae`** — target-account dossiers and next-best-action scoring.
- **`sales-leadership`** — pipeline risk, board-vs-plan deltas.
- **`revops`** — schema health, coverage gaps.
- **`customer-success`** — renewal risk and expansion-fit radar.

## Validation

The repo has no required Python dependencies. Tests, evals, and demos all run
on the standard library.

```bash
python -m unittest discover -s tests
python evals/run_evals.py
python evals/anti_qualification_cohort.py
python tools/inspect_skill.py --json
python demo/morning_dossier_demo.py
```

The cohort eval generates 200 synthetic deals with planted buyer intent and
reports precision / recall / F1 for the scorer's `POLITICAL_COVER` predictions
against ground-truth implementation failure. Numbers are deterministic
(seeded); the eval gates CI on a sanity floor, not a calibration claim.

## Anti-qualification thresholds

The `anti_qualification_scorer` reads its thresholds from the active skill:

```yaml
political_cover_min: 3.0    # ratio > 3.0  → POLITICAL_COVER
real_change_max:    1.5    # ratio < 1.5  → REAL_CHANGE
                            # otherwise   → AMBIGUOUS
```

Operators override them locally in `CLAUDE.local.md` under `aq_thresholds`.

## Model arbitration

`core/model_arbitration.py` is a token-aware router that picks the smallest
Claude tier satisfying each workflow's context size, reasoning floor, and cost
band. It returns a model name; the actual API call lives in the agent. Six
workflows are wired:

- `schema_health_gate`
- `pipeline_risk_radar`
- `renewal_expansion_radar`
- `win_loss_pattern_miner`
- `executive_forecast_memo`
- `signature_authority_extraction`

Prompt caching is recommended for workflows with `cacheable_context=True` and
input over ~8k tokens.

## Cold start

```bash
python tools/cold_start.py
# or, non-interactive:
python tools/cold_start.py --non-interactive --skill enterprise-account-based --force
python tools/inspect_skill.py
```

`CLAUDE.local.md` is git-ignored. No customer names, exec names, or deal names
belong in this repo.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Operator-specific data goes in
locally-ignored files, never in the repository.

## Disclaimers

- **Drafts, not decisions.** All agent and cookbook outputs are drafts for
  human reviewer judgment.
- **Not advice.** Outputs do not constitute legal, financial, or investment
  advice.
- **Web monitoring compliance.** Pre-announcement watcher and any feature that
  observes external sites must respect each target site's `robots.txt` and
  Terms of Service.
- **No embedded customer or executive data.** Operator-specific data belongs
  in `CLAUDE.local.md`.

## License

Apache-2.0. See [`LICENSE`](LICENSE).
