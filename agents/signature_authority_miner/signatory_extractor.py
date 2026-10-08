# SPDX-License-Identifier: Apache-2.0
"""Signatory extractor.

Two paths, same output shape:

- ``extract_signatories(text, source_url)`` — deterministic regex baseline.
  No API key required; used by tests and demos.
- ``extract_signatories_claude(text, source_url, *, client=None)`` — Claude
  Messages API call with prompt caching on the system instructions. Requires
  ``anthropic>=0.40.0`` and ``ANTHROPIC_API_KEY``.

Both return a list of rows with the schema columns the agent writes into
``signature_authority``. Real names live only in the agent's private working
store, keyed by ``person_id``; downstream schema rows use placeholder tokens.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any


# ---------- regex baseline ----------

_BY_LINE = re.compile(r"^\s*By:\s*(?P<name>.+?)\s*$", re.MULTILINE)
_SLASH_S = re.compile(r"^\s*/s/\s*(?P<name>.+?)\s*$", re.MULTILINE)
_NAME_LINE = re.compile(r"^\s*Name:\s*(?P<name>.+?)\s*$", re.MULTILINE)
_TITLE_LINE = re.compile(r"^\s*Title:\s*(?P<title>.+?)\s*$", re.MULTILINE)
_DATE_LINE = re.compile(r"^\s*Date:\s*(?P<date>.+?)\s*$", re.MULTILINE)

_DRAFT_NOTE = "Draft for reviewer judgment. Verify against source filing before use."


def _normalize_date(raw: str) -> str | None:
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _confidence_for_block(has_name: bool, has_title: bool, has_date: bool) -> float:
    score = 0.0
    if has_name:
        score += 0.5
    if has_title:
        score += 0.3
    if has_date:
        score += 0.2
    return round(min(0.9, score), 2)


def extract_signatories(filing_text: str, source_url: str) -> list[dict[str, Any]]:
    """Extract signatory rows via regex heuristic. No network calls."""
    if not filing_text:
        return []

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    name_matches = (
        list(_BY_LINE.finditer(filing_text))
        + list(_SLASH_S.finditer(filing_text))
        + list(_NAME_LINE.finditer(filing_text))
    )

    for m in name_matches:
        name = m.group("name").strip().strip(".,;:")
        if not name or name.lower() in {"name", "title", "date"}:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)

        window = filing_text[m.end(): m.end() + 240]
        t_match = _TITLE_LINE.search(window)
        d_match = _DATE_LINE.search(window)
        title = t_match.group("title").strip() if t_match else None
        signing_date = _normalize_date(d_match.group("date")) if d_match else None

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
            "draft_note": _DRAFT_NOTE,
        })

    return rows


# ---------- Claude-backed extractor ----------

_SYSTEM_PROMPT = """\
You extract signatures from SEC filings and contract exhibits.

For each signature block in the input, return one JSON object with these keys:
  signatory_name: full name as written in the filing
  signatory_title: title as written, or null if absent
  signing_date: ISO-8601 date (YYYY-MM-DD), or null if absent or ambiguous
  signing_context: a single-line excerpt of up to 240 characters surrounding the signature, with whitespace collapsed
  confidence_score: float in [0.0, 1.0]
                    use 0.9+ only for fully canonical blocks with Name, Title, and Date all present
                    use 0.6-0.8 when one canonical field is missing
                    use 0.3-0.5 when the block is partial or formatting is irregular

Rules:
- Return a JSON array. Nothing else. No prose, no markdown fences.
- If no signature blocks are detected, return [].
- De-duplicate by name within one filing.
- Never fabricate a signatory not present in the text.
- Never infer authority beyond what the filing states (no scoping of signing thresholds, no role inference).
- Title text is what the filing says; do not translate or normalize it.

These are drafts for human review. Treat ambiguous cases conservatively — when in doubt, lower confidence rather than omit.
"""


class ClaudeExtractionError(RuntimeError):
    """Raised when the Claude extractor cannot produce a parseable result."""


def _coerce_row(row: dict[str, Any], source_url: str) -> dict[str, Any]:
    name = (row.get("signatory_name") or "").strip()
    if not name:
        raise ClaudeExtractionError(f"row missing signatory_name: {row!r}")
    title = row.get("signatory_title")
    if isinstance(title, str):
        title = title.strip() or None
    signing_date = row.get("signing_date")
    if isinstance(signing_date, str):
        signing_date = signing_date.strip() or None
        normalized = _normalize_date(signing_date) if signing_date else None
        signing_date = normalized or signing_date
    context = row.get("signing_context") or ""
    if isinstance(context, str):
        context = re.sub(r"\s+", " ", context).strip()[:240]
    try:
        confidence = float(row.get("confidence_score", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    return {
        "signatory_name": name,
        "signatory_title": title,
        "signing_date": signing_date,
        "signing_context": context,
        "source_url": source_url,
        "confidence_score": round(confidence, 2),
        "extraction_method": "CLAUDE_STRUCTURED",
        "draft_note": _DRAFT_NOTE,
    }


def _parse_response_json(text: str) -> list[dict[str, Any]]:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate)
        candidate = re.sub(r"\s*```$", "", candidate)
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ClaudeExtractionError(f"model did not return valid JSON: {exc}") from exc
    if not isinstance(parsed, list):
        raise ClaudeExtractionError(f"model returned non-list: {type(parsed).__name__}")
    return parsed


def extract_signatories_claude(
    filing_text: str,
    source_url: str,
    *,
    client: Any = None,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 2048,
) -> list[dict[str, Any]]:
    """Extract signatory rows via Claude. Same return shape as the regex path.

    The system prompt is marked for ephemeral prompt caching so repeated runs
    over many filings amortize the instructions across calls. The filing text
    is sent uncached because it varies per call.

    Lazy-imports ``anthropic`` so this module is still importable without the
    optional SDK installed. Tests and the regex baseline do not exercise this
    path.
    """
    if not filing_text:
        return []

    if client is None:
        try:
            import anthropic  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised only when SDK absent
            raise ClaudeExtractionError(
                "anthropic SDK not installed. `pip install anthropic>=0.40.0` "
                "or pass a pre-built client."
            ) from exc
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ClaudeExtractionError("ANTHROPIC_API_KEY is not set")
        client = anthropic.Anthropic()

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Source URL: {source_url}\n\n"
                    f"Filing text:\n{filing_text}"
                ),
            }
        ],
    )

    text_blocks = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    if not text_blocks:
        raise ClaudeExtractionError("model returned no text content")

    parsed = _parse_response_json("\n".join(text_blocks))
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in parsed:
        if not isinstance(raw, dict):
            continue
        coerced = _coerce_row(raw, source_url)
        key = coerced["signatory_name"].lower()
        if key in seen:
            continue
        seen.add(key)
        rows.append(coerced)
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
    print("signatory_extractor — regex baseline demo on synthetic filing snippet")
    print("Draft for reviewer judgment. No real names; all signatories are placeholders.")
    print("-" * 72)
    for i, r in enumerate(rows, start=1):
        print(f"row {i}:")
        for k, v in r.items():
            print(f"  {k}: {v}")
        print()
    print(f"regex-extracted rows: {len(rows)}")

    if os.environ.get("ANTHROPIC_API_KEY"):
        print()
        print("ANTHROPIC_API_KEY detected — running Claude extractor on same input.")
        try:
            claude_rows = extract_signatories_claude(
                filing_text=_SYNTHETIC_FILING,
                source_url="https://example.invalid/synthetic-filing",
            )
        except ClaudeExtractionError as exc:
            print(f"Claude extractor failed: {exc}")
            return
        print(f"claude-extracted rows: {len(claude_rows)}")
        for i, r in enumerate(claude_rows, start=1):
            print(f"row {i}: {r['signatory_name']} / {r['signatory_title']} / "
                  f"{r['signing_date']} / conf {r['confidence_score']}")
    else:
        print()
        print("Set ANTHROPIC_API_KEY to also run the Claude extractor.")


if __name__ == "__main__":
    _demo()
