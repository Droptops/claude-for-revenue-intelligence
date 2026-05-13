# SPDX-License-Identifier: Apache-2.0
"""Signatory extractor — regex + heuristic stub.

Scans filing text for signature blocks. Looks for the canonical patterns:

    By:       <Name>
    /s/       <Name>
    Name:     <Name>
    Title:    <Title>
    Date:     <Date>

Returns one row per detected signature block. Names extracted here go only
to the agent's private working store, keyed by a pseudonymous person_id.
The schema row written downstream stores a placeholder token, not a real
name.

# TODO: replace regex heuristic with structured LLM extraction pass
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any


_BY_LINE = re.compile(r"^\s*By:\s*(?P<name>.+?)\s*$", re.MULTILINE)
_SLASH_S = re.compile(r"^\s*/s/\s*(?P<name>.+?)\s*$", re.MULTILINE)
_NAME_LINE = re.compile(r"^\s*Name:\s*(?P<name>.+?)\s*$", re.MULTILINE)
_TITLE_LINE = re.compile(r"^\s*Title:\s*(?P<title>.+?)\s*$", re.MULTILINE)
_DATE_LINE = re.compile(r"^\s*Date:\s*(?P<date>.+?)\s*$", re.MULTILINE)


def _normalize_date(raw: str) -> str | None:
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _confidence_for_block(has_name: bool, has_title: bool, has_date: bool) -> float:
    """Coarse confidence based on which canonical fields were detected."""
    score = 0.0
    if has_name:
        score += 0.5
    if has_title:
        score += 0.3
    if has_date:
        score += 0.2
    return round(score, 2)


def extract_signatories(filing_text: str, source_url: str) -> list[dict[str, Any]]:
    """Extract signatory rows from a filing's text.

    Each row:
        {
            "signatory_name":    str,       # real name; goes to private store
            "signatory_title":   str | None,
            "signing_date":      str | None (ISO-8601),
            "signing_context":   str,       # short surrounding snippet
            "source_url":        str,
            "confidence_score":  float,
            "extraction_method": "REGEX_HEURISTIC",
            "draft_note":        str,
        }
    """
    if not filing_text:
        return []

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    name_matches = list(_BY_LINE.finditer(filing_text)) + list(_SLASH_S.finditer(filing_text)) + list(_NAME_LINE.finditer(filing_text))

    for m in name_matches:
        name = m.group("name").strip().strip(".,;:")
        if not name or name.lower() in {"name", "title", "date"}:
            continue
        # de-dupe within a single filing
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)

        # Search forward a short window for an adjacent Title: / Date: line
        window = filing_text[m.end(): m.end() + 240]
        t_match = _TITLE_LINE.search(window)
        d_match = _DATE_LINE.search(window)
        title = t_match.group("title").strip() if t_match else None
        signing_date = _normalize_date(d_match.group("date")) if d_match else None

        # Context: ~80 chars before and 160 chars after, single line
        ctx_start = max(0, m.start() - 80)
        ctx_end = min(len(filing_text), m.end() + 160)
        context_raw = filing_text[ctx_start:ctx_end].replace("\n", " ").strip()
        signing_context = re.sub(r"\s+", " ", context_raw)[:240]

        confidence = _confidence_for_block(
            has_name=True,
            has_title=title is not None,
            has_date=signing_date is not None,
        )

        rows.append({
            "signatory_name": name,
            "signatory_title": title,
            "signing_date": signing_date,
            "signing_context": signing_context,
            "source_url": source_url,
            "confidence_score": confidence,
            "extraction_method": "REGEX_HEURISTIC",
            "draft_note": "Draft for reviewer judgment. Verify against source filing before use.",
        })

    return rows


# ---------- standalone demo ----------

_SYNTHETIC_FILING = """\
IN WITNESS WHEREOF, the parties have executed this Agreement as of the
date first written above.

PLACEHOLDER REGISTRANT, INC.

By:    Placeholder Signatory One
Name:  Placeholder Signatory One
Title: Authorized Officer
Date:  2026-02-14

PLACEHOLDER COUNTERPARTY, LLC

/s/   Placeholder Signatory Two
Name: Placeholder Signatory Two
Title: Managing Director
Date: February 14, 2026
"""


def _demo() -> None:
    rows = extract_signatories(
        filing_text=_SYNTHETIC_FILING,
        source_url="https://example.invalid/synthetic-filing",
    )
    print("signatory_extractor — demo run on synthetic filing snippet")
    print("Draft for reviewer judgment. No real names; all signatories are placeholders.")
    print("-" * 72)
    for i, r in enumerate(rows, start=1):
        print(f"row {i}:")
        for k, v in r.items():
            print(f"  {k}: {v}")
        print()
    print(f"extracted rows: {len(rows)}")


if __name__ == "__main__":
    _demo()
