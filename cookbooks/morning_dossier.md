<!-- SPDX-License-Identifier: Apache-2.0 -->
# Cookbook — Morning Dossier

## What this cookbook does

This cookbook produces a one-page **morning briefing** for an AE's top 3–5 priority accounts. It combines four signal sources — overnight trigger events, persona-graph coverage gaps, funnel-telemetry outliers, and pre-announcement web signals on the operator's competitor list — into a single dossier the AE can scan over coffee. The cookbook does not act on the AE's behalf. Every step ends in a draft the reviewer must approve before any outreach happens. The cookbook is opinionated about one thing: the dossier should fit on one screen.

## Prerequisites

- **Cold-start complete.** The repo-root `CLAUDE.md` has the `Profile fields` YAML block filled in. At minimum: `role = AE`, `avg_cycle_days`, `aq_ratio_baseline`.
- **At least one account** has rows in `schema/funnel_telemetry` and `schema/trigger_events`.
- **Persona graph populated** (`schema/persona_graph`) for the priority accounts, even if sparse. An empty graph degrades the coverage-gap step to a one-line "no data" note.
- **Competitor list at `plugins/competitive-intel/competitor_list.yaml`** (operator-local, not committed). A template is committed at `plugins/competitive-intel/competitor_list.yaml.example` — copy it and fill in your own entries. Empty list is allowed; the pre-announcement step degrades to category-level signals.
- **AE plugin loaded** (`plugins/ae/`). Each step below invokes the plugin in one of its three modes.

## Step-by-step

Each step lists the prompt you run. Run them in order; the dossier composer in step 5 reads from the outputs of steps 1–4.

### Step 1 — Pull overnight trigger events for priority accounts

Run the `trigger_event_monitor` agent over the last 24 hours for each priority account. Use the agent's `EARNINGS_LANGUAGE`, `EXEC_MOVEMENT`, `HIRING_SIGNAL`, and `REGULATORY_FILING` signal classes here; the pre-announcement class is its own step.

> **Prompt to run**
>
> ```
> Run agents/trigger_event_monitor in batch mode for accounts [ACCOUNT_LABEL_1, ACCOUNT_LABEL_2, ACCOUNT_LABEL_3]. Window: last 24 hours. Signal classes: EARNINGS_LANGUAGE, EXEC_MOVEMENT, HIRING_SIGNAL, REGULATORY_FILING. Return schema/trigger_events rows only; set reviewed=false on every row. Bias confidence low.
> ```

Output: a list of unreviewed `trigger_events` rows. Hand them to step 5; do not act on them yet.

### Step 2 — Check persona-graph coverage gaps

Run the AE plugin in `DOSSIER` mode for each priority account, but only consume the "Open questions / gaps" and "Influence Tier 1 contacts" sections — you are looking for tier-1 contacts marked `DARK` or `UNCONTACTED`, and for accounts where the economic buyer is unidentified.

> **Prompt to run**
>
> ```
> Run plugins/ae in DOSSIER mode for accounts [ACCOUNT_LABEL_1, ACCOUNT_LABEL_2, ACCOUNT_LABEL_3]. Return only the "Influence Tier 1 contacts" table and the "Open questions / gaps" list for each. Skip the rest of the dossier template.
> ```

Output: a per-account list of tier-1 engagement gaps. Empty per-account result is allowed and means "no gaps surfaced" — not "graph is healthy."

### Step 3 — Flag funnel-telemetry outliers

Read `schema/funnel_telemetry` for the priority accounts and surface rows where `outlier_flag = true`, plus any row whose `days_in_stage` exceeds `avg_cycle_days * 1.5` from the practice profile.

> **Prompt to run**
>
> ```
> Read schema/funnel_telemetry for opportunities tied to accounts [ACCOUNT_LABEL_1, ACCOUNT_LABEL_2, ACCOUNT_LABEL_3]. Return any row where (a) outlier_flag is true, or (b) days_in_stage > 1.5 * avg_cycle_days from CLAUDE.md. Include opportunity_id, account_id, stage, days_in_stage, outlier_reason. No customer names.
> ```

Output: a short list of opportunities that warrant attention. The reviewer decides whether each is a real outlier or stale CRM data.

### Step 4 — Run the pre-announcement watcher against the competitor list

Run `agents/trigger_event_monitor` in pre-announcement mode using the operator-local `competitor_list.yaml`. This step is gated by web-monitoring compliance — read the reminder below before running.

> **Compliance reminder.** Pre-announcement monitoring relies on `pre_announcement_watcher.py`. **The caller is responsible for confirming `robots.txt` and Terms of Service allowance for every target domain before invoking the watcher in live mode.** This system does not endorse or facilitate unauthorized scraping or access. If the compliance status of a target domain is unclear, **skip the domain** and note the skip in the dossier.
>
> **Prompt to run**
>
> ```
> Run agents/trigger_event_monitor in PRE_ANNOUNCEMENT mode using plugins/competitive-intel/competitor_list.yaml as the target list. For each domain in the list, confirm robots.txt and Terms of Service allowance before fetching; skip any domain whose status is unclear and emit a one-line skip note. Return PRE_ANNOUNCEMENT trigger_events rows only; set reviewed=false on every row. Confidence biases LOW unless multiple endpoints corroborate.
> ```

Output: zero or more `PRE_ANNOUNCEMENT` rows, plus a list of skipped domains. Both feed step 5.

### Step 5 — Compose the morning dossier

Compose the briefing in `ADVISE` posture — the dossier names recommended next steps but does not execute them. No emails are sent. No CRM rows are written.

> **Prompt to run**
>
> ```
> Compose a morning dossier for accounts [ACCOUNT_LABEL_1, ACCOUNT_LABEL_2, ACCOUNT_LABEL_3] using:
>   - the trigger_events rows from step 1
>   - the persona-coverage gaps from step 2
>   - the funnel outliers from step 3
>   - the pre-announcement rows and skipped-domain notes from step 4
> Posture: ADVISE. Do not send messages, write to the CRM, or call external APIs.
> Use [ACCOUNT_LABEL_n] placeholders; no real customer, exec, or vendor names.
> Fit on one screen. End with "Draft for reviewer judgment. Verify against source data before acting."
> ```

Output: the dossier. Reviewer approves any action before it leaves the dossier.

## Sample output format

The composer should produce something shaped like this. **No real data**; the placeholders below are the template.

```
Morning dossier — 2026-05-12
Accounts in focus: [ACCOUNT_LABEL_1], [ACCOUNT_LABEL_2], [ACCOUNT_LABEL_3]

[ACCOUNT_LABEL_1]
  Trigger events (last 24h):
    - EARNINGS_LANGUAGE / contraction (conf 0.50): <paraphrased summary>
    - EXEC_MOVEMENT (conf 0.65): <paraphrased summary>
  Persona gaps:
    - Economic buyer unidentified.
    - Tier-1 contact [person_id_A] status: DARK (last touch 41d).
  Funnel outliers:
    - OPP-XXXX in stage <STAGE> for 78 days (avg cycle 45d).
  Pre-announcement:
    - none

[ACCOUNT_LABEL_2]
  Trigger events (last 24h):
    - HIRING_SIGNAL (conf 0.40): <paraphrased summary — title-pattern level only>
  Persona gaps:
    - Tier-1 contact [person_id_B] status: ENGAGED.
  Funnel outliers:
    - none
  Pre-announcement:
    - PRE_ANNOUNCEMENT signal on competitor category "legacy-incumbent" (conf 0.30): new /newsroom/ slug.

[ACCOUNT_LABEL_3]
  Trigger events (last 24h):
    - none
  Persona gaps:
    - none
  Funnel outliers:
    - outlier_flag=true on OPP-YYYY: reason "stage skipped without prerequisite milestone".
  Pre-announcement:
    - skipped: <target_domain> — ToS / robots.txt status unclear.

Recommended next actions (drafts; reviewer approves before sending):
  1. [ACCOUNT_LABEL_1] — schedule reconnect with tier-1 [person_id_A].
  2. [ACCOUNT_LABEL_3] — internal review of OPP-YYYY stage entry.

Draft for reviewer judgment. Verify against source data before acting.
```

## Claim boundary

- All outputs from this cookbook are **drafts for reviewer judgment**. The cookbook does not claim completeness or accuracy on the AE's behalf.
- **No customer data appears in this file.** Every example above uses `[ACCOUNT_LABEL_n]` and `person_id` placeholders. Do not paste real account, contact, exec, or vendor names into the dossier, the trigger feeds, or the persona-graph notes.
- **Pre-announcement monitoring requires Terms of Service and `robots.txt` compliance.** The caller — the operator running this cookbook — is responsible for confirming compliance for every target domain before the pre-announcement step runs in live mode. This system does not endorse or facilitate unauthorized scraping or access. When compliance is unclear, skip the domain.
- **No external action is taken without explicit reviewer approval.** Step 5 produces a dossier; it does not send messages or update systems of record.
