<!-- SPDX-License-Identifier: Apache-2.0 -->
# agents/anti_qualification_scorer

This agent computes the **anti-qualification ratio** for an opportunity: the
ratio of the buyer's consulting / services spend to their implementation /
product spend on the same initiative. The result is one of three labels:
`POLITICAL_COVER`, `REAL_CHANGE`, or `AMBIGUOUS`.

Default thresholds are loaded from the active skill's `theory_constants` via
`skills/loader.py`. Operators may still pass explicit threshold overrides.

The scorer is a deterministic heuristic, not a learned model. Confidence is
`HIGH` only when both spend values are sourced from the CRM and both are
positive; `MEDIUM` when one is estimated; `LOW` otherwise or when the ratio is
undefined. Every output carries the `draft_note` `"This output is a draft for
reviewer judgment. Ratio is one signal; interpret in context."` The ratio is a
behavioral signal about how the buyer is allocating budget, not a verdict on
whether the deal will close. No customer, exec, or vendor names appear in any
output; the `opportunity_id` is the only identifier emitted.
