<!-- SPDX-License-Identifier: Apache-2.0 -->
# plugins/ae

The AE plugin is the account-executive view over the active skill's schema. It
does not introduce new data; it assembles persona dossiers, recommends next
outreach steps, and scores opportunities with the Best Next First Dollar
heuristic. Every output is a **draft for reviewer judgment**. The plugin takes
no external action without explicit user approval.

## How To Run

The plugin is loaded by Claude as a skill prompt. The operator invokes it in one
of three modes:

- `DOSSIER` - build a persona-graph summary for one account.
- `SEQUENCE` - recommend the next outreach step for one opportunity.
- `SCORE` - rank a set of opportunities with `best_next_first_dollar.py`.

The scorer is also runnable standalone for verification:

```bash
python plugins/ae/best_next_first_dollar.py
```

The demo data does not represent any real account.

## How It Reads The Practice Profile

On every invocation the plugin reads `CLAUDE.local.md` when present and falls
back to `CLAUDE.md` only for demos. It uses:

- `active_skill` - to load schema slots and theory constants.
- `role` - to confirm it is being run by an AE.
- `deal_size_range` and `avg_cycle_days` - to interpret stage-age penalties.
- `aq_ratio_baseline` and any local `aq_thresholds` - to interpret each
  opportunity's `anti_qualification_ratio`.

If `aq_ratio_baseline` is `null`, the plugin refuses to emit a `SCORE` output
and asks the operator to complete cold-start calibration.

## Disclaimer

The scorer is a deterministic weighted heuristic, not a learned model and not a
constrained optimizer. No customer names, exec names, or vendor names appear in
any output produced by this plugin. Web-monitoring inputs cited by any source
row must respect each target site's `robots.txt` and Terms of Service.
