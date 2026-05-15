<!-- SPDX-License-Identifier: Apache-2.0 -->
# Why this repo exists

One claim, one workflow, one number to track.

## The claim

Most enterprise B2B deals that look the same in CRM behave very differently
post-close. Some buyers fund implementation; others fund consulting around the
implementation. The first kind becomes a customer. The second kind becomes a
press release.

The **anti-qualification ratio** — buyer-side consulting spend divided by
buyer-side implementation spend — is one observable proxy for that split. Not
a complete proxy. One signal. The thresholds (`> 3.0` → `POLITICAL_COVER`,
`< 1.5` → `REAL_CHANGE`) are skill-level theory constants, not universal laws.

## The workflow

The repo's headline workflow is the **morning dossier**: for an AE's priority
accounts, surface overnight trigger events, persona-graph coverage gaps,
funnel outliers, and an anti-qualification label on each open opportunity.
The dossier names recommended next steps but never executes them. Every output
is a draft for reviewer judgment.

`cookbooks/morning_dossier.md` is the specification. `demo/morning_dossier_demo.py`
runs it on synthetic data with no external dependencies.

## The number

For any heuristic, the question is: *does it predict anything?*

`evals/anti_qualification_cohort.py` generates 200 synthetic deals with planted
buyer intent and noisy spend ratios, then asks how well the scorer's
`POLITICAL_COVER` predictions track ground-truth implementation failure.
Reported as precision / recall / F1. The cohort is synthetic so the absolute
number isn't a calibration claim — it's a regression detector. A real
calibration would replace the synthesis with anonymized cohort data the
operator owns.

## What the schema is for

The six-slot schema (`signature_authority`, `persona_graph`, `funnel_telemetry`,
`outcome_telemetry`, `conversation_evidence`, `trigger_events`) is the contract
between agents and plugins. Agents populate slots. Plugins read them. The
schema lets you replace any agent without rewriting any plugin.

The schema lives in the active skill (`skills/enterprise-account-based/`), not
in the base harness. A different motion can supply a different slot set. The
`skills/loader.py` mechanism is there for when a second motion earns its keep —
the goal is not maximal forkability for its own sake.

## What this repo is not

- Not a vendor product or commercial benchmark.
- Not a replacement for human judgment. Every output is a draft.
- Not a forecasting system. The model arbitration policy is a routing helper,
  not a Bayesian forecaster.
- Not a scraper. Pre-announcement-watcher features must respect `robots.txt`
  and Terms of Service for every target domain.
- Not a data vault. No customer names, executive names, deal names, or
  proprietary methodologies appear in this repository. Anything operator-
  specific lives in `CLAUDE.local.md`, which is git-ignored.

## Influences

The architecture takes the Karpathy framing of a small repo that earns
specialization by being read end-to-end. The intent here is not to maximize
fork surface area; it is to keep the base small enough that a reader can hold
the whole thing in their head, then specialize one slot at a time.
