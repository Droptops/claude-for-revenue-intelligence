# SPDX-License-Identifier: Apache-2.0
"""SEC EDGAR filing fetcher — stub.

Public API; no auth required. SEC fair-use guidance asks aggregators to stay
under 10 requests/sec per source IP and to identify themselves via a
descriptive User-Agent. Both are enforced (softly) here.

This module is a stub. The HTTP layer is deliberately not wired up — callers
get a clear NotImplementedError when they ask for a live fetch — so that the
stub cannot be used to scrape any non-EDGAR endpoint by accident. Demo runs
return an empty list.

EDGAR full-text search endpoint (for reference, not invoked by the stub):
    https://efts.sec.gov/LATEST/search-index?q=...&forms=...&dateRange=custom
"""

from __future__ import annotations

import time
from typing import Any


# ---------- rate limiting ----------

_EDGAR_MAX_RPS = 10  # SEC fair-use guidance: stay under 10 requests/sec.
_LAST_REQUEST_TS: list[float] = []


def _rate_limit_gate() -> None:
    """Cooperative rate limiter. Sleeps if the last second held ≥ 10 requests."""
    now = time.monotonic()
    cutoff = now - 1.0
    while _LAST_REQUEST_TS and _LAST_REQUEST_TS[0] < cutoff:
        _LAST_REQUEST_TS.pop(0)
    if len(_LAST_REQUEST_TS) >= _EDGAR_MAX_RPS:
        sleep_for = 1.0 - (now - _LAST_REQUEST_TS[0])
        if sleep_for > 0:
            time.sleep(sleep_for)
    _LAST_REQUEST_TS.append(time.monotonic())


# ---------- public api ----------

_SUPPORTED_FORMS = {"10-K", "10-Q", "DEF 14A", "8-K"}


def fetch_filings(
    cik: str,
    form_types: list[str],
    max_results: int = 10,
    *,
    live: bool = False,
) -> list[dict[str, Any]]:
    """Return filing metadata for a CIK.

    Each element:
        {
            "accession_number": str,
            "filing_date": str (YYYY-MM-DD),
            "form_type": str,
            "filing_url": str,
            "exhibit_urls": list[str],
        }

    Parameters
    ----------
    cik :
        SEC Central Index Key. Operator-supplied. Never hardcoded in callers
        outside the demo block of this module.
    form_types :
        Subset of {"10-K", "10-Q", "DEF 14A", "8-K"}.
    max_results :
        Cap on rows returned.
    live :
        Must be explicitly set to True to attempt a real fetch. The stub
        raises NotImplementedError in that case — the HTTP layer is left
        unwired on purpose.
    """
    if not cik or not cik.strip():
        raise ValueError("cik must be a non-empty string")
    bad = [f for f in form_types if f not in _SUPPORTED_FORMS]
    if bad:
        raise ValueError(f"unsupported form types: {bad}; supported: {sorted(_SUPPORTED_FORMS)}")
    if max_results <= 0:
        return []

    if not live:
        return []

    _rate_limit_gate()
    raise NotImplementedError(
        "Live EDGAR fetch is not wired up in this stub. The caller is "
        "responsible for implementing the HTTP layer with a descriptive "
        "User-Agent (per SEC fair-use guidance) and for staying under "
        f"{_EDGAR_MAX_RPS} requests/sec."
    )


# ---------- standalone demo ----------

def _demo() -> None:
    """Dry-run demo. Uses a clearly synthetic CIK placeholder."""
    placeholder_cik = "0000000000"  # not a real registrant — demo only

    print("sec_edgar_fetcher — demo dry-run")
    print("Draft for reviewer judgment. No live EDGAR call is made.")
    print("-" * 64)
    rows = fetch_filings(
        cik=placeholder_cik,
        form_types=["10-K", "DEF 14A", "8-K"],
        max_results=10,
        live=False,
    )
    print(f"placeholder_cik = {placeholder_cik}")
    print(f"requested form_types = ['10-K', 'DEF 14A', '8-K']")
    print(f"result count = {len(rows)}")
    print("Rate-limit gate enforces <= 10 requests/sec per SEC fair-use guidance.")


if __name__ == "__main__":
    _demo()
