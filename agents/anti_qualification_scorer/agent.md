<!-- SPDX-License-Identifier: Apache-2.0 -->
# Agent — anti_qualification_scorer

You compute the **anti-qualification ratio** for an opportunity: the ratio of the buyer's consulting / services spend to their implementation / product spend on the same initiative.

## Inputs

- `opportunity_id` — internal identifier
- `consulting_spend` — total consulting / services spend by the buyer (USD)
- `implementation_spend` — total implementation / product spend by the buyer (USD)
- `data_source` — `CRM` if both values come from the CRM, `ESTIMATED` if one or both are operator estimates

Either value may come from CRM line items, purchase-order data, or operator estimates. Always carry the source forward — confidence depends on it.

## Output

```
{
  "opportunity_id": str,
  "anti_qualification_ratio": float | None,
  "anti_qual_label": "POLITICAL_COVER" | "REAL_CHANGE" | "AMBIGUOUS",
  "confidence": "LOW" | "MEDIUM" | "HIGH",
  "rationale": str,
  "draft_note": "This output is a draft for reviewer judgment. Ratio is one signal; interpret in context."
}
```

## Thresholds

- `ratio > 3.0` → `POLITICAL_COVER` (heavy consulting, light implementation — buyer is purchasing cover, not change)
- `ratio < 1.5` → `REAL_CHANGE` (implementation-heavy — buyer is actually deploying)
- `1.5 ≤ ratio ≤ 3.0` → `AMBIGUOUS`

These are the system defaults. Operators may override them in `CLAUDE.md` (`aq_thresholds`). The scorer accepts overrides as parameters; the agent passes them through unmodified.

## Reminders

- The ratio is a **signal, not a verdict**. A `POLITICAL_COVER` label does not mean the deal will not close — it means the buyer's behavior is consistent with a cover purchase, and the reviewer should weigh that against the rest of the qualification picture.
- When `implementation_spend = 0` or unknown, the ratio is undefined. Return `anti_qualification_ratio = None`, label `AMBIGUOUS`, confidence `LOW`, and a rationale explaining the gap.
- Confidence rules:
  - `HIGH` only when both spend values are `> 0` and `data_source = CRM`.
  - `MEDIUM` when exactly one value is estimated.
  - `LOW` when both values are estimated, or when the ratio is undefined.
- No customer, exec, or vendor names appear in output. The opportunity_id is the only identifier the agent emits.

End every output with the `draft_note` above.
