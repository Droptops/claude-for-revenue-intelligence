<!-- SPDX-License-Identifier: Apache-2.0 -->
# Anti-Hallucination Grounding Notes

This document explains the grounding techniques used across the repository.
The architecture is intentional; here is the why. None of these techniques are
novel. They come from public AI engineering discourse and are applied here in
plain, narrow ways so that generated outputs stay reviewable.

## Techniques

### Schema-bounded outputs

Name: schema-bounded outputs.

Public lineage: structured outputs, JSON schema prompting, and typed tool
interfaces in public LLM engineering practice.

In this repo: agents and plugins are expected to emit only the columns defined
in `schema/`. For example, `schema/trigger_events.md`,
`schema/funnel_telemetry.md`, `schema/persona_graph.md`, and
`schema/signature_authority.md` define the slots downstream code consumes.
The agent prompts point back to those slots instead of asking for free-form
facts.

### Pseudonymous identifiers

Name: pseudonymous identifiers.

Public lineage: data minimization and pseudonymization practices from privacy
engineering, applied to LLM workflows.

In this repo: committed files use `[ACCOUNT_LABEL]`, `opportunity_id`, and
`person_id` values. `schema/signature_authority.md` states that real signatory
names are not committed. `plugins/ae/persona_dossier.md` tells operators to
use `[ACCOUNT_LABEL]` and `person_id` values from `schema/persona_graph` rather
than real account or person names.

### Paraphrased summaries

Name: paraphrased summaries.

Public lineage: retrieval-augmented generation (Lewis et al., 2020) and
source-grounded summarization patterns, with the repo storing summaries rather
than copied source text.

In this repo: `schema/trigger_events.md` stores `signal_summary` as a
paraphrase. `schema/conversation_evidence.md` stores
`transcript_excerpt_summary` and explicitly excludes verbatim transcripts.
`schema/outcome_telemetry.md` stores `contract_diff_summary` as a paraphrase
and excludes verbatim contract clauses.

### Confidence scoring with caps

Name: capped confidence scores.

Public lineage: calibration discipline from probabilistic ML and public LLM
evaluation practice; confidence is treated as a ranking aid, not truth.

In this repo: `agents/trigger_event_monitor/earnings_parser.py` caps keyword
heuristic confidence at `0.7`. `agents/signature_authority_miner/signatory_extractor.py`
caps regex extraction confidence at `0.9`. `schema/trigger_events.md` and
`schema/signature_authority.md` both describe `confidence_score` as the
extractor's self-report, not a calibrated probability.

### Reviewer gate

Name: reviewer-gate pattern.

Public lineage: human-in-the-loop review and chain-of-verification
(Dhuliawala et al., 2023), where generated claims remain candidates until
checked.

In this repo: `schema/signature_authority.md` requires `reviewer_verified` to
default to `false` and says unverified rows must not drive outreach or
commercial decisions. `schema/trigger_events.md` uses `reviewed` and
`flagged_for_action` so unreviewed event rows do not trigger automated action.
The agent prompts repeat the same gate.

### Draft suffix on outputs

Name: draft-for-reviewer suffix.

Public lineage: system-message guardrails and review disclaimers in public LLM
application patterns.

In this repo: `agents/anti_qualification_scorer/agent.md`,
`agents/trigger_event_monitor/agent.md`,
`agents/signature_authority_miner/agent.md`, `plugins/ae/SKILL.md`, and
`plugins/sales-leadership/SKILL.md` all require outputs to end as drafts for
reviewer judgment. The Python scorers also return or print `draft_note`
messages.

### Stub-by-default live network access

Name: stub-by-default live network.

Public lineage: least-privilege integration design and safe-by-default tool
interfaces.

In this repo: `agents/signature_authority_miner/sec_edgar_fetcher.py` defaults
to `live=False` and raises `NotImplementedError` when a caller asks for live
fetching. `agents/trigger_event_monitor/pre_announcement_watcher.py` follows
the same pattern for static endpoint and Wayback checks. This prevents an
agent from making live HTTP calls until the caller wires the transport and
confirms compliance.

### Bias toward ambiguous defaults

Name: ambiguous or unknown defaults.

Public lineage: abstention and uncertainty-aware classification in public
model-evaluation practice.

In this repo: `agents/anti_qualification_scorer/aq_scorer.py` returns
`AMBIGUOUS` when the ratio is undefined or in the middle band. `schema/outcome_telemetry.md`
uses `UNKNOWN` as the safe default for weak renewal signal quality.
`plugins/ae/best_next_first_dollar.py` treats missing outcome signal as
`UNKNOWN` rather than fabricating a stronger label.

## Limitations

These techniques reduce the surface area for hallucination, but they do not
eliminate it. A schema can still hold a wrong value, a paraphrase can still
omit context, and a confidence cap is not calibration. The load-bearing
control is the reviewer gate: generated rows remain drafts until a human
checks the source data and decides whether action is warranted.
