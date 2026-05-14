# SPDX-License-Identifier: Apache-2.0
"""Public asset feature-change monitor.

This module compares operator-provided snapshots of public competitor assets.
It does not crawl or fetch by itself. Operators must provide assets that are
permitted to monitor under robots.txt, Terms of Service, and their own policies.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.model_arbitration import arbitrate_model, estimate_record_tokens


FEATURE_GLOSSARY: dict[str, tuple[str, ...]] = {
    "forecast_copilot": ("forecast copilot", "forecast-ai", "forecast_ai", "predictive forecast"),
    "deal_inspection": ("deal inspection", "pipeline inspection", "deal-risk", "deal_risk"),
    "conversation_intelligence": ("conversation intelligence", "call summary", "transcript", "meeting recap"),
    "campaign_roi": ("campaign roi", "roas", "attribution", "cac payback"),
    "renewal_risk": ("renewal risk", "churn prediction", "customer health", "expansion signal"),
    "data_quality": ("schema health", "crm hygiene", "data quality", "field mapping"),
    "pricing_packaging": ("pricing", "package", "plan", "tier", "seat"),
}

ALLOWED_PERMISSION_VALUES = {"owned_domain", "public_allowed", "partner_provided", "manual_reviewed"}


def _asset_key(asset: dict[str, Any]) -> str:
    url = str(asset.get("url") or "")
    parsed = urlparse(url)
    if parsed.netloc:
        return f"{parsed.netloc.lower()}{parsed.path}"
    return url.lower()


def _hash_asset(asset: dict[str, Any]) -> str:
    if asset.get("sha256"):
        return str(asset["sha256"])
    body = str(asset.get("body_text") or asset.get("content_sample") or asset.get("url") or "")
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _search_space(asset: dict[str, Any]) -> str:
    parts = [
        str(asset.get("url") or ""),
        str(asset.get("body_text") or ""),
        str(asset.get("content_sample") or ""),
        " ".join(str(item) for item in asset.get("declared_terms") or []),
    ]
    return " ".join(parts).lower()


def extract_feature_terms(asset: dict[str, Any]) -> list[str]:
    haystack = _search_space(asset)
    terms = []
    for feature, needles in FEATURE_GLOSSARY.items():
        if any(needle.lower() in haystack for needle in needles):
            terms.append(feature)
    return sorted(set(terms))


def _permission(asset: dict[str, Any]) -> dict[str, Any]:
    permission = str(asset.get("source_permission") or "").lower()
    robots_allowed = asset.get("robots_allowed")
    tos_allowed = asset.get("tos_allowed")
    allowed = permission in ALLOWED_PERMISSION_VALUES
    if robots_allowed is False or tos_allowed is False:
        allowed = False
    if robots_allowed is None or tos_allowed is None:
        allowed = False
    reasons = []
    if permission not in ALLOWED_PERMISSION_VALUES:
        reasons.append("SOURCE_PERMISSION_MISSING_OR_UNSUPPORTED")
    if robots_allowed is not True:
        reasons.append("ROBOTS_NOT_CONFIRMED")
    if tos_allowed is not True:
        reasons.append("TOS_NOT_CONFIRMED")
    return {"allowed": allowed, "reasons": reasons}


def normalize_assets(assets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    normalized = {}
    for asset in assets:
        key = _asset_key(asset)
        if not key:
            continue
        normalized[key] = {
            "url": asset.get("url"),
            "hash": _hash_asset(asset),
            "feature_terms": extract_feature_terms(asset),
            "permission": _permission(asset),
            "content_type": asset.get("content_type"),
        }
    return normalized


def diff_asset_snapshots(snapshot: dict[str, Any]) -> dict[str, Any]:
    previous = normalize_assets(snapshot.get("previous_assets") or [])
    current = normalize_assets(snapshot.get("current_assets") or [])
    previous_keys = set(previous)
    current_keys = set(current)
    added_keys = sorted(current_keys - previous_keys)
    removed_keys = sorted(previous_keys - current_keys)
    changed_keys = sorted(key for key in previous_keys & current_keys if previous[key]["hash"] != current[key]["hash"])

    current_terms = sorted({term for asset in current.values() for term in asset["feature_terms"]})
    previous_terms = sorted({term for asset in previous.values() for term in asset["feature_terms"]})
    added_terms = sorted(set(current_terms) - set(previous_terms))
    removed_terms = sorted(set(previous_terms) - set(current_terms))
    owned_terms = {str(term) for term in snapshot.get("owned_feature_terms") or []}
    parity_gaps = sorted(set(current_terms) - owned_terms)

    permission_issues = [
        {"url": asset["url"], "reasons": asset["permission"]["reasons"]}
        for asset in current.values()
        if not asset["permission"]["allowed"]
    ]
    monitoring_allowed = len(permission_issues) == 0

    flags: list[dict[str, Any]] = []
    if not monitoring_allowed:
        flags.append(
            {
                "name": "MONITORING_NOT_ALLOWED",
                "evidence": f"{len(permission_issues)} asset(s) missing permission confirmation",
                "action": "Do not fetch or use this asset set until robots.txt, ToS, and source permission are confirmed.",
            }
        )
    if added_terms:
        flags.append(
            {
                "name": "FEATURE_SIGNAL_ADDED",
                "evidence": ", ".join(added_terms),
                "action": "Review the changed assets and decide whether this is a launch, packaging test, or noisy implementation detail.",
            }
        )
    if removed_terms:
        flags.append(
            {
                "name": "FEATURE_SIGNAL_REMOVED",
                "evidence": ", ".join(removed_terms),
                "action": "Check whether the competitor deprecated, renamed, or hid the feature language.",
            }
        )
    if parity_gaps and monitoring_allowed:
        flags.append(
            {
                "name": "POSSIBLE_PARITY_GAP",
                "evidence": ", ".join(parity_gaps),
                "action": "Compare against own roadmap and proof before making any field claim.",
            }
        )

    if not monitoring_allowed:
        posture = "NEEDS_PERMISSION_REVIEW"
    elif added_terms:
        posture = "COMPETITOR_ADDED_FEATURE_SIGNAL"
    elif removed_terms:
        posture = "COMPETITOR_REMOVED_FEATURE_SIGNAL"
    elif changed_keys or added_keys or removed_keys:
        posture = "ASSET_CHANGE_NO_FEATURE_SIGNAL"
    else:
        posture = "NO_MATERIAL_CHANGE"

    model_policy = arbitrate_model(
        "cdn_feature_monitor",
        estimated_input_tokens=estimate_record_tokens(snapshot),
        high_stakes=bool(snapshot.get("strategic_competitor")) or "pricing_packaging" in added_terms,
        evidence_conflict=bool(permission_issues) or bool(snapshot.get("evidence_conflict")),
    )

    return {
        "competitor_name": snapshot.get("competitor_name"),
        "posture": posture,
        "monitoring_allowed": monitoring_allowed,
        "added_assets": [current[key]["url"] for key in added_keys],
        "removed_assets": [previous[key]["url"] for key in removed_keys],
        "changed_assets": [current[key]["url"] for key in changed_keys],
        "current_feature_terms": current_terms,
        "added_feature_terms": added_terms,
        "removed_feature_terms": removed_terms,
        "possible_parity_gaps": parity_gaps,
        "permission_issues": permission_issues,
        "flags": flags,
        "model_policy": model_policy,
        "draft_note": "Draft for reviewer judgment. Public asset changes are weak signals until verified against product, docs, or customer evidence.",
    }


def find_asset_urls_from_html(html: str) -> list[str]:
    """Extract script/link asset URLs from an already-permitted HTML snapshot."""
    pattern = re.compile(r"""(?:src|href)=["']([^"']+\.(?:js|css|json))["']""", re.IGNORECASE)
    return sorted(set(pattern.findall(html or "")))


def _demo() -> None:
    snapshot = {
        "competitor_name": "Example Rival",
        "owned_feature_terms": ["deal_inspection", "data_quality", "campaign_roi"],
        "previous_assets": [
            {
                "url": "https://cdn.example.invalid/app.123.js",
                "body_text": "deal inspection conversation intelligence",
                "source_permission": "manual_reviewed",
                "robots_allowed": True,
                "tos_allowed": True,
            }
        ],
        "current_assets": [
            {
                "url": "https://cdn.example.invalid/app.456.js",
                "body_text": "deal inspection conversation intelligence forecast copilot predictive forecast",
                "source_permission": "manual_reviewed",
                "robots_allowed": True,
                "tos_allowed": True,
            }
        ],
    }
    result = diff_asset_snapshots(snapshot)
    print("cdn_feature_monitor - demo run")
    print(f"{result['competitor_name']}: {result['posture']} added={result['added_feature_terms']} model={result['model_policy']['selected_model']}")
    for flag in result["flags"]:
        print(f"  - {flag['name']}: {flag['action']}")


if __name__ == "__main__":
    _demo()
