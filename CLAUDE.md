# Revenue Intelligence Practice Profile

<!-- SPDX-License-Identifier: Apache-2.0 -->

This file is the committed **practice profile template** for the
`claude-for-revenue-intelligence` repository. Your filled-in profile belongs in
`CLAUDE.local.md`, which is ignored by git. Agents and plugins should read
`CLAUDE.local.md` at startup when it exists, then fall back to this template for
demos only.

The committed copy of this file is a **template**. The first time you run the
system, copy it to `CLAUDE.local.md` and fill that copy in locally. The filled-in
copy stays on your machine; only the template version is committed to the
repository.

## How To Use

You have two ways to fill in the profile:

1. **Guided:** run the cold-start interview with `python tools/cold_start.py`.
   It reads each question in the **Interview** section below, prompts you, and
   writes your answers into the **Profile fields** YAML block.
2. **Manual:** copy this file to `CLAUDE.local.md`, answer each question inline
   if you like, then fill in the YAML block at the bottom of the local copy. The
   loader and plugins only read the YAML block; the interview text is for your
   benefit.

When you are done, the practice profile is local-only. Do not commit your
filled-in answers. The `.gitignore` for this repository ignores
`CLAUDE.local.md`.

## Skill Loader Pattern

The base harness stays motion-agnostic. Agents read schema contracts and theory
constants from the active skill; never hardcode motion-specific assumptions in
`/agents/` or base code.

Do not do this in an agent:

```python
POLITICAL_COVER_MIN = 3.0
```

Do this instead:

```python
from skills.loader import load_active_skill

constants = load_active_skill().theory_constants["anti_qualification"]
```

The active skill is selected by `active_skill` in `CLAUDE.local.md`. If no local
profile exists, the loader falls back to `enterprise-account-based`.

## Interview

Answer each question below. No customer names, exec names, or deal names
anywhere; the system is designed to work without them.

1. **Which skill should this install use?** Start with
   `enterprise-account-based` unless you are deliberately forking a new motion.
   Run `python -c "from skills.loader import list_available_skills; [print(f'{s.name}: {s.description}') for s in list_available_skills()]"`.

2. **What is your primary role?** (AE / Sales Leader / RevOps / Customer
   Success / Other)

3. **What is your typical deal size range?** (e.g. `$60k-$240k ARR`,
   `$500k+ ARR`)

4. **What CRM are you using?** Do not enter credentials here; credentials live
   in `connectors/` with the connector's own setup flow.

5. **Do you have access to call recording data?** (Gong / Chorus / None)

6. **What is your average sales cycle length in days?**

7. **Describe your ideal closed-won customer in 2-3 sentences.** Focus on shape:
   segment, motion, what they were trying to change. No real customer names.

8. **Describe your most common closed-lost pattern in 1-2 sentences.** Focus on
   the failure mode, not the deal.

9. **Anti-qualification calibration.** For the `enterprise-account-based` skill,
   the default thresholds live in
   `skills/enterprise-account-based/SKILL.md`:
   - ratio `> 3.0` -> `POLITICAL_COVER`
   - ratio `< 1.5` -> `REAL_CHANGE`
   - `1.5 <= ratio <= 3.0` -> `AMBIGUOUS`
   In your last 5 closed-won deals, what was the approximate ratio of consulting
   / services spend to implementation / product spend on the buyer's side? You
   may override the active skill's thresholds in `aq_thresholds` below.

10. **Do you have a board / plan delta you track?** (Yes / No. If yes, what is
    the primary metric? e.g. `net-new ARR vs plan`, `pipeline coverage`,
    `forecast accuracy`.)

## Profile Fields

The loader and plugins only read this YAML block. Fill in the values; leave keys
you do not use as `null`.

```yaml
active_skill: enterprise-account-based # selected skill id
role: null                             # one of: AE | SALES_LEADER | REVOPS | CUSTOMER_SUCCESS | OTHER
deal_size_range: null                  # free-text label, e.g. "$60k-$240k ARR"
crm: null                              # one of: SALESFORCE | HUBSPOT | OTHER | NONE
call_platform: null                    # one of: GONG | CHORUS | NONE
avg_cycle_days: null                   # integer
aq_ratio_baseline: null                # float - observed ratio on closed-won deals
aq_thresholds: null                    # optional local override; defaults come from active skill
board_metric: null                     # free-text, or null if not tracked
```

At runtime the loader binds `schema_slots`, `agent_roster`, `plugin_defaults`,
`cookbook_set`, `connector_bindings`, and `theory_constants` from the selected
skill. Do not hand-copy those bindings into this profile unless a local install
needs an explicit override.

## Plugin Behavior Notes

- **AE plugin** (`plugins/ae/`): reads `role`, `deal_size_range`,
  `avg_cycle_days`, `aq_ratio_baseline`, and any local `aq_thresholds`. Uses the
  active skill's schema slots as its data contract. Will refuse to emit a
  `SCORE` output if `aq_ratio_baseline` is unset.
- **Sales Leadership plugin** (`plugins/sales-leadership/`): reads
  `board_metric` and `avg_cycle_days`. Without `board_metric`, the
  board-vs-plan view falls back to a generic pipeline-coverage view.
- **RevOps plugin** (`plugins/revops/`): reads `crm` and any local
  `aq_thresholds`. Uses active-skill theory constants to label rows.
- **Customer Success plugin** (`plugins/customer-success/`): reads
  `aq_ratio_baseline` and active-skill theory constants to label renewal
  and expansion posture.

## Disclaimer

- This profile contains **no customer data**. Do not paste customer names, deal
  names, exec names, contract text, or proprietary data into this file.
- All plugin and agent outputs are **drafts for reviewer judgment**. The system
  does not claim completeness or accuracy on the operator's behalf.
- Web-monitoring features must respect each target site's `robots.txt` and
  Terms of Service. This system does not endorse or facilitate unauthorized
  scraping.
- No external action (email send, CRM write, calendar invite, etc.) is taken
  without explicit user approval.
