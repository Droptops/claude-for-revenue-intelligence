<!-- SPDX-License-Identifier: Apache-2.0 -->
# Cookbook - Morning Dossier

## What This Cookbook Does

This cookbook produces a one-page **morning briefing** for an AE's top priority
accounts. It combines overnight trigger events, persona-graph coverage gaps,
funnel-telemetry outliers, and pre-announcement web signals from the operator's
local competitor list. The cookbook does not act on the AE's behalf. Every step
ends in a draft the reviewer must approve before any outreach happens.

## Prerequisites

- **Cold-start complete.** `CLAUDE.local.md` has `active_skill`,
  `avg_cycle_days`, and `aq_ratio_baseline` filled in.
- **Active skill loaded.** Use `skills/loader.py` to resolve schema slots.
- **At least one account** has rows in the active skill's `funnel_telemetry` and
  `trigger_events` slots.
- **Persona graph populated** for the priority accounts, even if sparse.
- **Competitor list at `plugins/competitive-intel/competitor_list.yaml`**
  (operator-local, not committed). Empty list is allowed.
- **AE plugin loaded** (`plugins/ae/`).

## Step 1 - Pull Overnight Trigger Events

Run `agents/trigger_event_monitor` over the last 24 hours for each priority
account. Return active-skill `trigger_events` rows only, set `reviewed=false`,
and bias confidence low.

Output: a list of unreviewed trigger-event rows. Hand them to the composer; do
not act on them yet.

## Step 2 - Check Persona-Graph Coverage Gaps

Run the AE plugin in `DOSSIER` mode for each priority account. Consume only the
Influence Tier 1 contacts and open gaps. Empty per-account result is allowed and
means "no gaps surfaced," not "graph is healthy."

## Step 3 - Flag Funnel-Telemetry Outliers

Read the active skill's `funnel_telemetry` for the priority accounts and surface
rows where `outlier_flag = true`, plus any open row whose `days_in_stage`
exceeds `avg_cycle_days * 1.5` from the practice profile.

Output: a short list of opportunities that warrant attention. The reviewer
decides whether each is a real outlier or stale CRM data.

## Step 4 - Run The Pre-Announcement Watcher

Run `agents/trigger_event_monitor` in pre-announcement mode using the
operator-local `competitor_list.yaml`.

**Compliance reminder.** Pre-announcement monitoring relies on
`pre_announcement_watcher.py`. The caller is responsible for confirming
`robots.txt` and Terms of Service allowance for every target domain before
invoking the watcher in live mode. This system does not endorse or facilitate
unauthorized scraping or access. If compliance status is unclear, skip the
domain and note the skip in the dossier.

## Step 5 - Compose The Morning Dossier

Compose the briefing in `ADVISE` posture. The dossier names recommended next
steps but does not execute them. No emails are sent. No CRM rows are written.

Use:

- trigger-event rows from step 1
- persona-coverage gaps from step 2
- funnel outliers from step 3
- pre-announcement rows and skipped-domain notes from step 4

Use `[ACCOUNT_LABEL_n]` placeholders; no real customer, exec, or vendor names.
End with: `Draft for reviewer judgment. Verify against source data before
acting.`

## Claim Boundary

- All outputs from this cookbook are **drafts for reviewer judgment**.
- **No customer data appears in this file.** Do not paste real account, contact,
  exec, or vendor names into the dossier or source notes.
- **Pre-announcement monitoring requires Terms of Service and `robots.txt`
  compliance.**
- **No external action is taken without explicit reviewer approval.**
