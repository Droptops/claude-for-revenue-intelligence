<!-- SPDX-License-Identifier: Apache-2.0 -->
# plugins/ae

The AE plugin is the account-executive view over the six schema slots. It does not introduce new data; it assembles persona dossiers, recommends next outreach steps, and scores opportunities with the Best Next First Dollar heuristic. Every output is a **draft for reviewer judgment** — the plugin takes no external action without explicit user approval.

## How to run

The plugin is loaded by Claude as a skill. The skill prompt is `SKILL.md`. The operator invokes it in one of three modes, named on the command line or in the prompt itself:

- `DOSSIER` — build a persona-graph summary for one account; output uses the template at `persona_dossier.md`.
- `SEQUENCE` — recommend the next outreach step for one opportunity.
- `SCORE` — rank a set of opportunities with `best_next_first_dollar.py`.

The scorer is also runnable standalone for verification:

```
python plugins/ae/best_next_first_dollar.py
```

This runs the demo block with three sample opportunities and prints the ranked output. The demo data does not represent any real account.

## How it reads from `CLAUDE.md`

On every invocation the plugin reads the **Profile fields** YAML block at the bottom of the repo-root `CLAUDE.md`. It uses:

- `role` — to confirm it is being run by an AE (warns otherwise),
- `deal_size_range` and `avg_cycle_days` — to interpret the `days_in_stage` penalty in the scorer,
- `aq_ratio_baseline` and `aq_thresholds` — to interpret each opportunity's `anti_qualification_ratio`.

If `aq_ratio_baseline` is `null`, the plugin refuses to emit a `SCORE` output and asks the operator to complete cold-start question 8.

## Disclaimer

The scorer is a deterministic weighted heuristic, not a learned model and not a constrained optimizer. Real constrained optimization is a stretch goal. No customer names, exec names, or vendor names appear in any output produced by this plugin — accounts are referenced by `[ACCOUNT_LABEL]` and persons by `person_id`. Web-monitoring inputs cited by any source row must respect each target site's `robots.txt` and Terms of Service.
