<!-- SPDX-License-Identifier: Apache-2.0 -->
# Explorations

This file is a lightweight thought log for open questions. Entries should be
concrete enough to revisit, but they do not need to be fully argued before
being captured.

1. **Operator-tunable anti-qualification bands per segment**

   The reference `enterprise-account-based` skill uses 3.0 and 1.5 as default
   ratio thresholds. It is open whether those thresholds should vary by segment,
   deal size, or sales motion, since a services-heavy buying pattern may mean
   different things in different books of business.

   Current thinking: defaults are a skill-level starting point; per-segment or
   per-fork overrides may be necessary above a certain operator scale.

   What would resolve it: empirical study on cohort data.

2. **Calibrated probabilities vs. ordinal scores**

   Best Next First Dollar emits a 0-100 score. It is open whether the operator
   would be better served by a calibrated probability of close, especially when
   comparing opportunities across segments.

   Current thinking: probability is the right long-term answer but requires
   training data the repo does not assume.

   What would resolve it: separate calibration module that consumes the score
   and an outcome history.

3. **Trigger-event taxonomy expansion**

   The trigger-event taxonomy is intentionally small today. It is open whether
   it should include patent filings, lawsuit filings, regulatory inquiries, or
   leadership social-media activity.

   Current thinking: each addition has a noise cost; new types should be added
   only when an existing type would meaningfully misclassify.

   What would resolve it: case-by-case justification per proposed type.

4. **Relationship-edge strength as a numeric weight**

   `persona_graph.relationship_edges` is categorical today. It is open whether
   edges should carry a 0.0-1.0 weight derived from observed signal, such as
   meeting recency, mutual mentions, or shared decision history.

   Current thinking: useful for tier scoring but introduces an interpretability
   cost.

   What would resolve it: prototype a weighted version on a single test
   account.

5. **Multi-currency support in schema**

   `signing_threshold_usd` and `deal_size` are USD-only. It is open whether the
   schema should support arbitrary currency codes and retain original currency
   values alongside normalized reporting values.

   Current thinking: yes for any operator with a non-US book; the cost is a
   column rename and a conversion layer.

   What would resolve it: schema migration plus a connector contract for FX
   rates.

6. **Eval calibration tests**

   Current evals check label accuracy and deterministic behavior. It is open
   whether they should also check confidence calibration, such as whether
   `HIGH` confidence rows are right more often than `LOW` confidence rows.

   Current thinking: yes, but requires accumulating an outcome ledger first.

   What would resolve it: add a longitudinal evals/ledger.

7. **Persona graph decay windows**

   Persona coverage currently treats engagement status as a field supplied by
   the operator or connector. It is open whether the repo should define default
   decay windows that turn stale engagement into `DARK` or a lower-confidence
   coverage signal.

   Current thinking: decay windows would make reviews more consistent, but the
   defaults probably differ by segment and sales motion.

   What would resolve it: compare stale-touch patterns against closed-won and
   closed-lost outcomes across a few anonymized books.

8. **Board-vs-plan filter vs. optimizer**

   The board-vs-plan scorer is a deterministic constraint filter. It is open
   whether the next step should be a true constrained optimizer that maximizes
   expected revenue or coverage under capacity constraints.

   Current thinking: the filter is easier to audit and should remain the first
   interface; optimization may belong behind a separate module.

   What would resolve it: prototype an optimizer using synthetic capacity
   constraints and compare whether its recommendations remain explainable.

9. **Closed-lost reason vocabulary drift**

   Closed-lost postmortems rely on normalized reason labels. It is open how the
   repo should detect when those labels drift, overlap, or stop matching the
   real patterns reviewers are seeing.

   Current thinking: the vocabulary should stay small, with drift handled by
   periodic review rather than automatic label creation.

   What would resolve it: quarterly review of postmortems with a small report
   on unmapped or repeatedly ambiguous reasons.

Closing note: this file evolves. Contributions to it via PR are welcome; the
format is intentionally lightweight to lower the cost of capturing a
half-formed idea.
