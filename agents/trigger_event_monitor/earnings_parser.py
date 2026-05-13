# SPDX-License-Identifier: Apache-2.0
"""Earnings-language parser — keyword heuristic stub.

Scans an earnings-call transcript (or prepared-remarks excerpt) for three
families of language signal:

    expansion   — "accelerating", "increasing investment", "new markets", ...
    contraction — "headcount reduction", "cost discipline", "reprioritizing", ...
    urgency     — "this quarter", "immediate", "within 90 days", ...

Returns one row per detected signal. Every row is a draft for reviewer
judgment. Keyword heuristics are noisy by design — bias confidence low.

# TODO: replace keyword heuristic with structured LLM extraction pass
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


_EXPANSION_TERMS = [
    "accelerating",
    "accelerate",
    "increasing investment",
    "new markets",
    "expand into",
    "expanding into",
    "scaling up",
    "ramp up",
    "tailwind",
]

_CONTRACTION_TERMS = [
    "headcount reduction",
    "reduction in force",
    "cost discipline",
    "cost reduction",
    "reprioritizing",
    "reprioritize",
    "rationalize",
    "softness",
    "headwind",
    "pause hiring",
]

_URGENCY_TERMS = [
    "this quarter",
    "immediate",
    "immediately",
    "within 90 days",
    "next 90 days",
    "near-term",
    "as soon as possible",
]


def _confidence_for_family(family: str, hit_count: int) -> float:
    """Cap confidence at 0.7 for keyword heuristics; never go higher."""
    base = {"expansion": 0.4, "contraction": 0.5, "urgency": 0.3}.get(family, 0.3)
    bump = min(0.3, 0.1 * (hit_count - 1)) if hit_count > 1 else 0.0
    return round(min(0.7, base + bump), 2)


def _scan(text: str, terms: list[str]) -> list[tuple[str, str]]:
    """Return list of (matched_term, surrounding_snippet)."""
    hits: list[tuple[str, str]] = []
    lower = text.lower()
    for term in terms:
        for m in re.finditer(re.escape(term.lower()), lower):
            start = max(0, m.start() - 80)
            end = min(len(text), m.end() + 80)
            snippet = re.sub(r"\s+", " ", text[start:end]).strip()
            hits.append((term, snippet))
    return hits


def parse_earnings_transcript(transcript_text: str, account_id: str) -> list[dict[str, Any]]:
    """Return a list of EARNINGS_LANGUAGE event rows."""
    if not transcript_text or not account_id:
        return []

    families = {
        "expansion": _scan(transcript_text, _EXPANSION_TERMS),
        "contraction": _scan(transcript_text, _CONTRACTION_TERMS),
        "urgency": _scan(transcript_text, _URGENCY_TERMS),
    }

    now = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []

    for family, hits in families.items():
        if not hits:
            continue
        # one row per family per transcript; carry up to 3 example snippets
        examples = [snippet for _, snippet in hits[:3]]
        terms_seen = sorted({term for term, _ in hits})
        rows.append({
            "account_id": account_id,
            "event_type": "EARNINGS_LANGUAGE",
            "signal_family": family,
            "signal_summary": (
                f"{family} language detected ({len(hits)} hit(s)); "
                f"terms: {', '.join(terms_seen)}"
            ),
            "example_snippets": examples,
            "confidence_score": _confidence_for_family(family, len(hits)),
            "extraction_method": "KEYWORD_HEURISTIC",
            "extracted_at": now,
            "draft_note": "Draft for reviewer judgment. Keyword heuristic; verify against transcript.",
        })

    return rows


# ---------- standalone demo ----------

_SYNTHETIC_TRANSCRIPT = """\
Operator: Welcome to the Placeholder Issuer Q4 earnings call.

CEO (placeholder): We are accelerating investment in new markets this quarter
and expect to expand into adjacent verticals near-term.

CFO (placeholder): At the same time, we are exercising cost discipline and
reprioritizing several non-core initiatives. We expect immediate impact on
operating margin.

Analyst (placeholder): Any guidance on the 90-day plan?

CEO (placeholder): We have firm commitments within 90 days.
"""


def _demo() -> None:
    rows = parse_earnings_transcript(
        transcript_text=_SYNTHETIC_TRANSCRIPT,
        account_id="ACCT-PLACEHOLDER",
    )
    print("earnings_parser — demo run on synthetic transcript")
    print("Draft for reviewer judgment. No real company or exec names.")
    print("-" * 72)
    for i, r in enumerate(rows, start=1):
        print(f"row {i}: family={r['signal_family']} conf={r['confidence_score']}")
        print(f"  summary: {r['signal_summary']}")
        for s in r["example_snippets"]:
            print(f"   - {s}")
        print()
    print(f"rows: {len(rows)}")


if __name__ == "__main__":
    _demo()
