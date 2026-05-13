# SPDX-License-Identifier: Apache-2.0
"""Competitive battlecard builder.

The battlecard only uses supplied evidence. It avoids unsupported claims and
keeps competitor talk tracks factual enough for sales and marketing review.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.model_arbitration import arbitrate_model, estimate_record_tokens


def _norm(value: str) -> str:
    return " ".join(value.lower().replace("_", " ").replace("-", " ").split())


def _unique(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        clean = value.strip()
        key = _norm(clean)
        if clean and key not in seen:
            seen.add(key)
            result.append(clean)
    return result


def _match_terms(terms: list[str], corpus: list[str]) -> list[str]:
    matches = []
    normalized_corpus = [_norm(item) for item in corpus]
    for term in terms:
        normalized = _norm(term)
        if normalized and any(normalized in item or item in normalized for item in normalized_corpus):
            matches.append(term)
    return _unique(matches)


def build_battlecard(profile: dict[str, Any]) -> dict[str, Any]:
    competitor_name = profile.get("competitor_name") or "Competitor"
    searched_keywords = [str(item) for item in profile.get("searched_keywords") or []]
    competitor_terms = [str(item) for item in profile.get("competitor_terms") or []]
    own_capabilities = [str(item) for item in profile.get("own_capabilities") or []]
    competitor_claims = [str(item) for item in profile.get("competitor_claims") or []]
    observed_feature_terms = [str(item) for item in profile.get("observed_feature_terms") or []]
    proof_points = [str(item) for item in profile.get("proof_points") or []]
    customer_objections = [str(item) for item in profile.get("customer_objections") or []]

    keyword_terms = _unique(searched_keywords + competitor_terms)
    competitor_feature_signals = _unique(competitor_claims + observed_feature_terms)
    matched_own = _match_terms(own_capabilities, keyword_terms + competitor_feature_signals)
    competitor_only = [
        term
        for term in competitor_feature_signals
        if _norm(term) not in {_norm(capability) for capability in own_capabilities}
    ]
    own_only = [
        capability
        for capability in own_capabilities
        if _norm(capability) not in {_norm(term) for term in competitor_feature_signals}
    ]

    talk_tracks = []
    if matched_own:
        talk_tracks.append(
            {
                "name": "Match the active research theme",
                "prompt": f"Lead with {matched_own[0]} because it overlaps the observed evaluation language.",
                "evidence": matched_own[:3],
            }
        )
    if competitor_only:
        talk_tracks.append(
            {
                "name": "Verify competitor claim",
                "prompt": f"Ask whether {competitor_name}'s {competitor_only[0]} is required now or a future-state nice-to-have.",
                "evidence": competitor_only[:3],
            }
        )
    if own_only:
        talk_tracks.append(
            {
                "name": "Differentiate without attacking",
                "prompt": f"Anchor on your verified advantage: {own_only[0]}. Tie it to buyer risk, not vendor mudslinging.",
                "evidence": own_only[:3],
            }
        )

    discovery_questions = [
        "Which outcome made this evaluation urgent now?",
        "What proof would make the buying committee comfortable switching or adding a vendor?",
        "Where does the current process fail: data quality, adoption, forecast confidence, or campaign ROI?",
    ]
    if competitor_only:
        discovery_questions.append(f"How important is {competitor_only[0]} compared with implementation speed and measurable revenue impact?")
    if searched_keywords:
        discovery_questions.append(f"When your team searches around '{searched_keywords[0]}', what problem are they trying to solve first?")

    landmines = [
        "Do not claim feature superiority without a cited source or customer-approved proof point.",
        "Do not imply an individual searched a keyword; keep intent language at account level.",
    ]
    if not proof_points:
        landmines.append("No proof points supplied; treat every differentiated claim as draft-only.")
    if profile.get("evidence_conflict"):
        landmines.append("Evidence conflict detected; route this battlecard through human review before field use.")

    objection_responses = []
    for objection in customer_objections[:4]:
        objection_responses.append(
            {
                "objection": objection,
                "response": "Acknowledge the concern, ask for the decision criterion behind it, then map only evidence-backed proof.",
            }
        )

    model_policy = arbitrate_model(
        "competitive_battlecard_builder",
        estimated_input_tokens=estimate_record_tokens(profile),
        high_stakes=bool(profile.get("strategic_competitor")) or bool(profile.get("board_visible")),
        evidence_conflict=bool(profile.get("evidence_conflict")) or len(proof_points) == 0,
    )

    return {
        "competitor_name": competitor_name,
        "keyword_terms": keyword_terms,
        "competitor_feature_signals": competitor_feature_signals,
        "matched_own_capabilities": matched_own,
        "competitor_only_signals": competitor_only,
        "own_differentiators": own_only,
        "talk_tracks": talk_tracks,
        "discovery_questions": discovery_questions,
        "objection_responses": objection_responses,
        "landmines": landmines,
        "proof_points": proof_points,
        "model_policy": model_policy,
        "draft_note": "Draft for reviewer judgment. Use only evidence-backed claims in customer-facing material.",
    }


def _demo() -> None:
    profile = {
        "competitor_name": "Example Rival",
        "searched_keywords": ["forecast accuracy software", "revenue intelligence alternative"],
        "competitor_terms": ["Example Rival alternative"],
        "own_capabilities": ["forecast accuracy", "schema health gate", "campaign ROI payback"],
        "competitor_claims": ["conversation intelligence", "forecast accuracy", "AI deal summaries"],
        "observed_feature_terms": ["copilot", "deal inspection"],
        "proof_points": ["Validated pipeline-risk demo and tests in repo"],
        "customer_objections": ["We already have a call-recording platform."],
    }
    result = build_battlecard(profile)
    print("battlecard_builder - demo run")
    print(f"{result['competitor_name']}: tracks={len(result['talk_tracks'])} model={result['model_policy']['selected_model']}")
    for track in result["talk_tracks"]:
        print(f"  - {track['name']}: {track['prompt']}")


if __name__ == "__main__":
    _demo()
