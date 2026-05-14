# SPDX-License-Identifier: Apache-2.0
"""Intent-to-sequence builder for account-based growth teams.

Connector-neutral input can come from 6sense, ZoomInfo, G2, Bombora, first-party
site activity, CRM campaigns, or a manually reviewed CSV. The output is a draft
sequence for reviewer judgment, not an automated send.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.model_arbitration import arbitrate_model, estimate_record_tokens
from plugins.growth.search_intent_mapper import classify_intent


KEYWORD_THEME_MAP: dict[str, tuple[str, ...]] = {
    "forecast_accuracy": ("forecast", "forecast accuracy", "pipeline forecast", "commit risk"),
    "pipeline_quality": ("pipeline quality", "pipeline inspection", "pipeline risk", "deal risk"),
    "competitive_replacement": ("alternative", "vs", "replace", "replacement", "migration"),
    "marketing_roi": ("campaign roi", "roas", "cac payback", "attribution"),
    "renewal_risk": ("renewal", "churn", "expansion", "customer success"),
    "data_quality": ("schema", "data quality", "crm hygiene", "source quality"),
}


def _num(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _intent_tier(score: float) -> str:
    if score >= 75:
        return "HIGH"
    if score >= 50:
        return "MEDIUM"
    return "LOW"


def _keyword_texts(keywords: list[Any]) -> list[str]:
    values: list[str] = []
    for item in keywords:
        if isinstance(item, dict):
            value = str(item.get("keyword") or item.get("topic") or "").strip()
        else:
            value = str(item).strip()
        if value:
            values.append(value)
    return values


def map_keyword_themes(keywords: list[Any], competitor_terms: list[str] | None = None) -> dict[str, Any]:
    keyword_texts = _keyword_texts(keywords)
    competitor_terms = [term.lower() for term in competitor_terms or []]
    themes: dict[str, list[str]] = {}
    competitor_mentions: list[str] = []
    intents: list[str] = []

    for keyword in keyword_texts:
        lowered = keyword.lower()
        intents.append(classify_intent(keyword, competitor_terms))
        for theme, terms in KEYWORD_THEME_MAP.items():
            if any(term in lowered for term in terms):
                themes.setdefault(theme, []).append(keyword)
        for competitor in competitor_terms:
            if competitor and competitor in lowered:
                competitor_mentions.append(keyword)

    if not themes and keyword_texts:
        themes["category_research"] = keyword_texts

    return {
        "themes": themes,
        "competitor_mentions": competitor_mentions,
        "intent_classes": sorted(set(intents)),
    }


def _contact_score(contact: dict[str, Any]) -> int:
    title = str(contact.get("title") or "").lower()
    persona = str(contact.get("persona") or "").lower()
    seniority = str(contact.get("seniority") or "").lower()
    score = 0
    if any(term in title for term in ("chief", "cfo", "cro", "cmo", "vp", "vice president", "head of")):
        score += 30
    if any(term in persona for term in ("revops", "revenue", "sales", "marketing", "growth", "demand", "finance")):
        score += 25
    if any(term in seniority for term in ("executive", "vp", "director", "head")):
        score += 15
    if contact.get("recent_engagement"):
        score += 15
    if contact.get("known_champion"):
        score += 10
    if contact.get("email_verified"):
        score += 5
    return score


def select_contacts(contacts: list[dict[str, Any]], *, max_contacts: int = 3) -> dict[str, Any]:
    eligible: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    for contact in contacts:
        reasons = []
        if contact.get("opted_out"):
            reasons.append("OPTED_OUT")
        if contact.get("email_allowed") is False:
            reasons.append("EMAIL_NOT_ALLOWED")
        if not contact.get("email") and not contact.get("linkedin_url"):
            reasons.append("NO_CONTACT_ROUTE")
        if reasons:
            suppressed.append({"contact_id": contact.get("contact_id"), "reasons": reasons})
            continue
        enriched = dict(contact)
        enriched["routing_score"] = _contact_score(contact)
        eligible.append(enriched)

    selected = sorted(eligible, key=lambda row: row["routing_score"], reverse=True)[:max_contacts]
    return {"selected": selected, "suppressed": suppressed}


def _primary_theme(mapped: dict[str, Any]) -> str:
    themes = mapped["themes"]
    if not themes:
        return "category_research"
    return sorted(themes.items(), key=lambda item: (-len(item[1]), item[0]))[0][0]


def _theme_phrase(theme: str) -> str:
    return {
        "forecast_accuracy": "forecast accuracy and pipeline confidence",
        "pipeline_quality": "pipeline quality and deal-risk visibility",
        "competitive_replacement": "evaluating alternatives without losing proof or context",
        "marketing_roi": "campaign ROI, attribution, and CAC payback",
        "renewal_risk": "renewal risk and expansion timing",
        "data_quality": "CRM data quality and source confidence",
        "category_research": "revenue-intelligence operating discipline",
    }.get(theme, theme.replace("_", " "))


def draft_sequence(account: dict[str, Any]) -> dict[str, Any]:
    keywords = account.get("intent_keywords") or account.get("searched_keywords") or []
    competitor_terms = account.get("competitor_terms") or []
    mapped = map_keyword_themes(keywords, competitor_terms)
    routing = select_contacts(account.get("contacts") or [])
    selected_contacts = routing["selected"]

    intent_score = _num(account.get("intent_score"))
    primary_theme = _primary_theme(mapped)
    theme_phrase = _theme_phrase(primary_theme)
    company_name = account.get("company_name") or "your team"
    competitor_context = mapped["competitor_mentions"]
    competitor_phrase = ""
    if competitor_context:
        competitor_phrase = " I also included a neutral comparison angle because this looks like an alternatives-style research pattern."

    sequence = [
        {
            "day": 0,
            "channel": "email",
            "subject": f"{theme_phrase} at {company_name}",
            "body": (
                f"Hi {{first_name}}, noticed {company_name} may be prioritizing {theme_phrase}. "
                "Teams usually get stuck when the signal is visible but not tied to pipeline, renewal, and campaign outcomes."
                f"{competitor_phrase} Worth comparing notes on what is real signal versus noise?"
            ),
            "cta": "Ask for a 15-minute signal review.",
        },
        {
            "day": 2,
            "channel": "email",
            "subject": "A quick way to separate signal from noise",
            "body": (
                f"One practical test for {theme_phrase}: can the team trace the signal to a named account, a buying-committee role, "
                "a current business trigger, and a measurable next action? If one of those is missing, the motion usually becomes generic outreach."
            ),
            "cta": "Offer a one-page diagnostic checklist.",
        },
        {
            "day": 5,
            "channel": "email",
            "subject": "Where the sequence should change",
            "body": (
                "The sequence should adapt by theme: executive proof for forecast risk, finance language for ROI/payback, "
                "and factual comparison points for alternative evaluation. Happy to share the routing logic we use for this."
            ),
            "cta": "Offer to send a tailored sequence map.",
        },
        {
            "day": 9,
            "channel": "email",
            "subject": "Should I close the loop?",
            "body": (
                f"If {theme_phrase} is not active for your team, I will close the loop. If it is, I can send a short account-intent map "
                "showing the likely themes, stakeholders, and next-best plays."
            ),
            "cta": "Ask whether to send the map or close the loop.",
        },
    ]

    compliance_checks = [
        "Use account-level intent language; do not say an individual searched a term.",
        "Do not send to opted-out contacts or contacts without a permitted route.",
        "Keep competitor claims factual and evidence-linked.",
        "Route final copy through the operator's email compliance and unsubscribe process.",
    ]

    model_policy = arbitrate_model(
        "intent_sequence_builder",
        estimated_input_tokens=estimate_record_tokens(account),
        high_stakes=intent_score >= 85 or bool(account.get("executive_sequence")),
        evidence_conflict=bool(account.get("evidence_conflict")) or _num(account.get("source_confidence_pct"), 100) < 60,
    )

    return {
        "account_id": account.get("account_id"),
        "company_name": company_name,
        "intent_tier": _intent_tier(intent_score),
        "intent_score": round(intent_score),
        "primary_theme": primary_theme,
        "themes": mapped["themes"],
        "intent_classes": mapped["intent_classes"],
        "competitor_mentions": competitor_context,
        "selected_contacts": selected_contacts,
        "suppressed_contacts": routing["suppressed"],
        "sequence": sequence,
        "compliance_checks": compliance_checks,
        "model_policy": model_policy,
        "draft_note": "Draft for reviewer judgment. Personalize from permitted account-level context, not individual surveillance language.",
    }


def _demo() -> None:
    account = {
        "account_id": "ACCT-INTENT-1",
        "company_name": "ExampleCo",
        "intent_score": 88,
        "source_system": "6sense_or_zoominfo",
        "source_confidence_pct": 72,
        "searched_keywords": [
            "pipeline forecast accuracy software",
            "gong alternative revenue intelligence",
            "campaign roi attribution",
        ],
        "competitor_terms": ["gong"],
        "contacts": [
            {
                "contact_id": "C-1",
                "first_name": "Avery",
                "title": "VP Revenue Operations",
                "persona": "RevOps",
                "seniority": "VP",
                "email": "placeholder@example.invalid",
                "email_verified": True,
                "email_allowed": True,
            },
            {
                "contact_id": "C-2",
                "first_name": "Sam",
                "title": "Director Demand Generation",
                "persona": "Marketing",
                "seniority": "Director",
                "email": "placeholder2@example.invalid",
                "email_allowed": True,
                "recent_engagement": True,
            },
        ],
    }
    result = draft_sequence(account)
    print("intent_sequence_builder - demo run")
    print(f"{result['account_id']}: {result['intent_tier']} theme={result['primary_theme']} model={result['model_policy']['selected_model']}")
    print(f"selected_contacts={len(result['selected_contacts'])} suppressed={len(result['suppressed_contacts'])}")
    for step in result["sequence"][:2]:
        print(f"  day {step['day']}: {step['subject']}")


if __name__ == "__main__":
    _demo()
