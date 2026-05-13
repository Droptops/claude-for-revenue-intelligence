# Revenue Intelligence Practice Profile

<!-- SPDX-License-Identifier: Apache-2.0 -->

This file is the committed **practice profile template** for the `claude-for-revenue-intelligence` repository. Your filled-in profile belongs in `CLAUDE.local.md`, which is ignored by git. Every plugin (AE, Sales Leadership, RevOps, Competitive Intel) should read `CLAUDE.local.md` at start-up when it exists, then fall back to this template for demos.

The committed copy of this file is a **template**. The first time you run the system, copy it to `CLAUDE.local.md` and fill that copy in locally. The filled-in copy stays on your machine; only the template version is committed to the repository.

## How to use

You have two ways to fill in the profile:

1. **Guided:** run the cold-start interview with `claude --profile`. Claude reads each question in the **Interview** section below, prompts you, and writes your answers into the **Profile fields** YAML block at the bottom of this file.
2. **Manual:** copy this file to `CLAUDE.local.md`, answer each question inline if you like, then fill in the YAML block at the bottom of the local copy. The plugins only read the YAML block; the interview text is for your benefit.

When you are done, the practice profile is local-only. Do not commit your filled-in answers. The `.gitignore` for this repository ignores `CLAUDE.local.md` (see `QUICKSTART.md`).

## Interview

Answer each question below. No customer names, exec names, or deal names anywhere — the system is designed to work without them.

1. **What is your primary role?** (AE / Sales Leader / RevOps / Competitive Intel / Other)

2. **What is your typical deal size range?** (e.g. `$60k–$240k ARR`, `$500k+ ARR`)

3. **What CRM are you using?** (Do not enter credentials here — credentials live in `connectors/` with the connector's own setup flow.)

4. **Do you have access to call recording data?** (Gong / Chorus / None)

5. **What is your average sales cycle length in days?**

6. **Describe your ideal closed-won customer in 2–3 sentences.** Focus on shape — segment, motion, what they were trying to change. No real customer names.

7. **Describe your most common closed-lost pattern in 1–2 sentences.** Focus on the failure mode, not the deal.

8. **Anti-qualification question.** In your last 5 closed-won deals, what was the approximate ratio of **consulting / services spend** to **implementation / product spend** on the buyer's side? This calibrates the anti-qualification scorer. The system default thresholds are:
   - ratio `> 3.0` → `POLITICAL_COVER` (heavy consulting, light implementation — the buyer is buying cover, not change)
   - ratio `< 1.5` → `REAL_CHANGE` (implementation-heavy — the buyer is actually deploying)
   - `1.5 ≤ ratio ≤ 3.0` → `AMBIGUOUS`
   You may override these thresholds in `aq_thresholds` below.

9. **What competitor categories are most active in your deals?** (Categories only — e.g. `legacy-incumbent`, `point-tool`, `open-source-DIY`. Specific vendor names belong in `plugins/competitive-intel/competitor_list.yaml` on your local machine, not in this file.)

10. **Do you have a board / plan delta you track?** (Yes / No — if yes, what is the primary metric? e.g. `net-new ARR vs plan`, `pipeline coverage`, `forecast accuracy`.)

## Profile fields

The plugins only read this YAML block. Fill in the values; leave keys you do not use as `null`.

```yaml
role: null                # one of: AE | SALES_LEADER | REVOPS | COMPETITIVE_INTEL | OTHER
deal_size_range: null     # free-text label, e.g. "$60k-$240k ARR"
crm: null                 # one of: SALESFORCE | HUBSPOT | OTHER | NONE
call_platform: null       # one of: GONG | CHORUS | NONE
avg_cycle_days: null      # integer
aq_ratio_baseline: null   # float — your observed ratio on closed-won deals
aq_thresholds:            # optional override of system defaults
  political_cover_min: 3.0
  real_change_max: 1.5
board_metric: null        # free-text — name of the metric, or null if not tracked
competitor_categories: [] # list of category labels, no vendor names
```

## Plugin behavior notes

- **AE plugin** (`plugins/ae/`): reads `role`, `deal_size_range`, `avg_cycle_days`, `aq_ratio_baseline`, and `aq_thresholds`. Uses them to seed the Best Next First Dollar scorer and the persona dossier. Will refuse to emit a SCORE output if `aq_ratio_baseline` is unset, on the assumption that the operator has not yet calibrated the anti-qualification scorer.
- **Sales Leadership plugin** (`plugins/sales-leadership/`): reads `board_metric` and `avg_cycle_days`. Without `board_metric`, the board-vs-plan view falls back to a generic pipeline-coverage view.
- **RevOps plugin** (`plugins/revops/`): reads `crm` and `aq_thresholds`. Uses the thresholds to label rows in `schema/funnel_telemetry`.
- **Competitive Intel plugin** (`plugins/competitive-intel/`): reads `competitor_categories` and the local competitor list. Never emits specific vendor names that are not in the operator's local list.

## Disclaimer

- This profile contains **no customer data**. Do not paste customer names, deal names, exec names, contract text, or proprietary data into this file.
- All plugin and agent outputs are **drafts for reviewer judgment**. The system does not claim completeness or accuracy on the operator's behalf.
- Web-monitoring features must respect each target site's `robots.txt` and Terms of Service. This system does not endorse or facilitate unauthorized scraping.
- No external action (email send, CRM write, calendar invite, etc.) is taken without explicit user approval.
