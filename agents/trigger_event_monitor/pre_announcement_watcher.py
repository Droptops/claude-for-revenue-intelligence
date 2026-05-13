# SPDX-License-Identifier: Apache-2.0
# Web monitoring must comply with each target site's robots.txt and Terms of
# Service. This module does not facilitate unauthorized access. The caller is
# responsible for confirming compliance before invoking any function here.

"""Pre-announcement watcher — static-endpoint diff stub.

Compares two snapshots of a small set of public-facing endpoints:

    /sitemap.xml
    /robots.txt
    /careers/        (job-title patterns only; no candidate data)
    /newsroom/       (new slugs vs prior snapshot)
    /investor-relations/   (new slugs vs prior snapshot)

The diff is the signal. Every new slug or sitemap entry is a candidate
pre-announcement event row. Confidence biases LOW unless multiple endpoints
corroborate.

This module is a stub. The HTTP and content-fetch layers are deliberately
not wired up — callers receive an empty diff or a NotImplementedError when
they request a live fetch. This is to prevent accidental scraping of any
target whose ToS or robots.txt compliance has not been confirmed by the
caller.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse


_COMPLIANCE_NOTE = (
    "Caller is responsible for verifying robots.txt compliance and Terms of "
    "Service before invoking this function on any target domain."
)


def _signal_strength(num_new_paths: int, endpoint_count: int) -> str:
    if endpoint_count >= 3 and num_new_paths >= 5:
        return "HIGH"
    if endpoint_count >= 2 and num_new_paths >= 2:
        return "MEDIUM"
    return "LOW"


def watch_static_endpoints(
    base_url: str,
    paths_to_check: list[str],
    prior_snapshot: dict | None,
    *,
    live: bool = False,
) -> dict[str, Any]:
    """Diff the current snapshot against a prior snapshot for one base URL.

    Returns:
        {
            "base_url": str,
            "checked_at": ISO-8601 timestamp (UTC),
            "new_paths_detected": list[str],
            "diff_summary": str,
            "signal_strength": "LOW" | "MEDIUM" | "HIGH",
            "compliance_note": str,
        }
    """
    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("base_url must be an absolute URL with scheme and host")

    checked_at = datetime.now(timezone.utc).isoformat()

    # Stub mode: no live fetch. Use the prior_snapshot keys as the current
    # set so the diff is always empty by construction.
    if not live:
        prior_paths = set((prior_snapshot or {}).get("paths", []))
        current_paths = prior_paths  # no-op — stub does not fetch
        new_paths = sorted(current_paths - prior_paths)
        endpoints_with_diff = 0
        return {
            "base_url": base_url,
            "checked_at": checked_at,
            "new_paths_detected": new_paths,
            "diff_summary": (
                "Stub mode: no live fetch performed. Diff is empty by construction. "
                f"{len(paths_to_check)} endpoints would have been checked in live mode."
            ),
            "signal_strength": _signal_strength(len(new_paths), endpoints_with_diff),
            "compliance_note": _COMPLIANCE_NOTE,
        }

    raise NotImplementedError(
        "Live fetch is not wired up. The caller must implement the HTTP layer "
        "and must confirm robots.txt and Terms of Service compliance for each "
        "target domain before enabling it. " + _COMPLIANCE_NOTE
    )


def fetch_wayback_diff(url: str, days_back: int = 30, *, live: bool = False) -> dict[str, Any]:
    """Look up a Wayback Machine snapshot for a URL.

    Public availability API:
        https://archive.org/wayback/available?url=<url>&timestamp=<YYYYMMDD>

    Returns:
        {
            "url": str,
            "available": bool,
            "closest_snapshot_url": str | None,
            "delta_note": str,
        }
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("url must be an absolute URL with scheme and host")
    if days_back < 0:
        raise ValueError("days_back must be non-negative")

    if not live:
        return {
            "url": url,
            "available": False,
            "closest_snapshot_url": None,
            "delta_note": (
                "Stub mode: no live archive.org call performed. "
                f"Would have requested closest snapshot within {days_back} days. "
                + _COMPLIANCE_NOTE
            ),
        }

    raise NotImplementedError(
        "Live archive.org availability call is not wired up in this stub. "
        + _COMPLIANCE_NOTE
    )


# ---------- standalone demo ----------

def _demo() -> None:
    placeholder_url = "https://placeholder.invalid"  # synthetic; not a real domain
    paths = ["/sitemap.xml", "/robots.txt", "/careers/", "/newsroom/", "/investor-relations/"]

    print("pre_announcement_watcher — demo dry-run")
    print("Draft for reviewer judgment. No live web traffic; stub mode.")
    print("Web monitoring must comply with each target site's robots.txt and ToS.")
    print("-" * 72)

    result = watch_static_endpoints(
        base_url=placeholder_url,
        paths_to_check=paths,
        prior_snapshot=None,
        live=False,
    )
    print("watch_static_endpoints:")
    for k, v in result.items():
        print(f"  {k}: {v}")
    print()

    wb = fetch_wayback_diff(
        url=f"{placeholder_url}/newsroom/",
        days_back=30,
        live=False,
    )
    print("fetch_wayback_diff:")
    for k, v in wb.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    _demo()
