# SPDX-License-Identifier: Apache-2.0
"""Token-aware model arbitration for revenue-intelligence workflows.

The router chooses the smallest model class that satisfies the workflow's
context, reasoning, and latency needs. It intentionally uses relative cost
tiers instead of hardcoded prices because vendor pricing changes faster than
this reference repo should.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelProfile:
    model: str
    family: str
    context_window_tokens: int
    relative_cost: int
    speed_rank: int
    reasoning_rank: int
    supports_prompt_caching: bool = True
    notes: str = ""


@dataclass(frozen=True)
class WorkflowPolicy:
    workflow: str
    min_reasoning_rank: int
    max_relative_cost: int
    latency_preference: str
    default_output_tokens: int
    cacheable_context: bool
    escalation_triggers: tuple[str, ...]


MODEL_CATALOG: dict[str, ModelProfile] = {
    "claude-haiku": ModelProfile(
        model="claude-haiku",
        family="haiku",
        context_window_tokens=200_000,
        relative_cost=1,
        speed_rank=3,
        reasoning_rank=1,
        notes="Fast path for schema checks, simple classification, and deterministic summaries.",
    ),
    "claude-sonnet": ModelProfile(
        model="claude-sonnet",
        family="sonnet",
        context_window_tokens=200_000,
        relative_cost=3,
        speed_rank=2,
        reasoning_rank=2,
        notes="Default balanced model for multi-source synthesis and account-level reasoning.",
    ),
    "claude-opus": ModelProfile(
        model="claude-opus",
        family="opus",
        context_window_tokens=200_000,
        relative_cost=8,
        speed_rank=1,
        reasoning_rank=3,
        notes="Escalation model for high-stakes executive synthesis and ambiguous strategy calls.",
    ),
    "claude-sonnet-long-context": ModelProfile(
        model="claude-sonnet-long-context",
        family="sonnet",
        context_window_tokens=1_000_000,
        relative_cost=6,
        speed_rank=1,
        reasoning_rank=2,
        notes="Long-context fallback for large transcript or account-history packs.",
    ),
}


WORKFLOW_POLICIES: dict[str, WorkflowPolicy] = {
    "schema_health_gate": WorkflowPolicy(
        workflow="schema_health_gate",
        min_reasoning_rank=1,
        max_relative_cost=1,
        latency_preference="LOW",
        default_output_tokens=600,
        cacheable_context=False,
        escalation_triggers=("schema contract changed", "new connector mapping"),
    ),
    "pipeline_risk_radar": WorkflowPolicy(
        workflow="pipeline_risk_radar",
        min_reasoning_rank=2,
        max_relative_cost=3,
        latency_preference="MEDIUM",
        default_output_tokens=1_200,
        cacheable_context=True,
        escalation_triggers=("board-facing forecast", "conflicting evidence", "large commit deal"),
    ),
    "renewal_expansion_radar": WorkflowPolicy(
        workflow="renewal_expansion_radar",
        min_reasoning_rank=2,
        max_relative_cost=3,
        latency_preference="MEDIUM",
        default_output_tokens=1_400,
        cacheable_context=True,
        escalation_triggers=("executive renewal memo", "contract-risk narrative", "ambiguous usage trend"),
    ),
    "win_loss_pattern_miner": WorkflowPolicy(
        workflow="win_loss_pattern_miner",
        min_reasoning_rank=2,
        max_relative_cost=6,
        latency_preference="MEDIUM",
        default_output_tokens=1_800,
        cacheable_context=True,
        escalation_triggers=("cross-cohort root cause", "raw interview synthesis"),
    ),
    "executive_forecast_memo": WorkflowPolicy(
        workflow="executive_forecast_memo",
        min_reasoning_rank=3,
        max_relative_cost=8,
        latency_preference="HIGH",
        default_output_tokens=2_200,
        cacheable_context=True,
        escalation_triggers=("board package", "CEO/CFO narrative", "material forecast call"),
    ),
    "market_share_tracker": WorkflowPolicy(
        workflow="market_share_tracker",
        min_reasoning_rank=2,
        max_relative_cost=3,
        latency_preference="MEDIUM",
        default_output_tokens=1_400,
        cacheable_context=True,
        escalation_triggers=("category board packet", "market share reversal", "conflicting demand sources"),
    ),
    "campaign_roi_tracker": WorkflowPolicy(
        workflow="campaign_roi_tracker",
        min_reasoning_rank=1,
        max_relative_cost=3,
        latency_preference="LOW",
        default_output_tokens=1_000,
        cacheable_context=True,
        escalation_triggers=("budget reallocation", "attribution conflict", "enterprise campaign postmortem"),
    ),
    "search_intent_mapper": WorkflowPolicy(
        workflow="search_intent_mapper",
        min_reasoning_rank=2,
        max_relative_cost=6,
        latency_preference="MEDIUM",
        default_output_tokens=1_600,
        cacheable_context=True,
        escalation_triggers=("category narrative rewrite", "competitor intercept strategy", "large keyword universe"),
    ),
    "intent_sequence_builder": WorkflowPolicy(
        workflow="intent_sequence_builder",
        min_reasoning_rank=2,
        max_relative_cost=3,
        latency_preference="MEDIUM",
        default_output_tokens=1_600,
        cacheable_context=True,
        escalation_triggers=("executive account sequence", "competitor replacement motion", "sensitive contact policy"),
    ),
    "competitive_battlecard_builder": WorkflowPolicy(
        workflow="competitive_battlecard_builder",
        min_reasoning_rank=2,
        max_relative_cost=6,
        latency_preference="MEDIUM",
        default_output_tokens=2_000,
        cacheable_context=True,
        escalation_triggers=("board-visible competitor", "evidence conflict", "strategic displacement motion"),
    ),
    "cdn_feature_monitor": WorkflowPolicy(
        workflow="cdn_feature_monitor",
        min_reasoning_rank=1,
        max_relative_cost=3,
        latency_preference="LOW",
        default_output_tokens=1_000,
        cacheable_context=True,
        escalation_triggers=("competitor launch signal", "pricing or packaging change", "terms or robots conflict"),
    ),
}


def estimate_tokens(text: str) -> int:
    """Coarse token estimate for routing, not billing."""
    if not text:
        return 0
    return max(1, round(len(text) / 4))


def estimate_record_tokens(record: dict[str, Any]) -> int:
    """Estimate tokens for a record without importing json for callers."""
    return estimate_tokens(str(record))


def _candidate_models(policy: WorkflowPolicy, total_tokens: int) -> list[ModelProfile]:
    candidates = [
        model
        for model in MODEL_CATALOG.values()
        if model.context_window_tokens >= total_tokens
        and model.reasoning_rank >= policy.min_reasoning_rank
        and model.relative_cost <= policy.max_relative_cost
    ]
    if candidates:
        return candidates

    # If the workflow cannot fit in the default cost band, allow long context
    # or Opus escalation, but make that visible in the rationale.
    return [
        model
        for model in MODEL_CATALOG.values()
        if model.context_window_tokens >= total_tokens
        and model.reasoning_rank >= policy.min_reasoning_rank
    ]


def arbitrate_model(
    workflow: str,
    *,
    estimated_input_tokens: int,
    estimated_output_tokens: int | None = None,
    high_stakes: bool = False,
    evidence_conflict: bool = False,
) -> dict[str, Any]:
    """Return a model-selection decision for one workflow.

    The decision is deterministic and explainable. If a workflow is high
    stakes or evidence is conflicting, the router raises the reasoning floor by
    one tier where possible.
    """
    if workflow not in WORKFLOW_POLICIES:
        raise ValueError(f"unknown workflow {workflow!r}")
    if estimated_input_tokens < 0:
        raise ValueError("estimated_input_tokens must be non-negative")

    policy = WORKFLOW_POLICIES[workflow]
    output_tokens = estimated_output_tokens or policy.default_output_tokens
    if output_tokens < 0:
        raise ValueError("estimated_output_tokens must be non-negative")

    effective_policy = policy
    escalation_reasons: list[str] = []
    if high_stakes or evidence_conflict:
        escalation_reasons.extend(
            reason
            for reason, active in (
                ("high_stakes", high_stakes),
                ("evidence_conflict", evidence_conflict),
            )
            if active
        )
        effective_policy = WorkflowPolicy(
            workflow=policy.workflow,
            min_reasoning_rank=min(3, policy.min_reasoning_rank + 1),
            max_relative_cost=max(policy.max_relative_cost, 8),
            latency_preference=policy.latency_preference,
            default_output_tokens=policy.default_output_tokens,
            cacheable_context=policy.cacheable_context,
            escalation_triggers=policy.escalation_triggers,
        )

    total_tokens = estimated_input_tokens + output_tokens
    candidates = _candidate_models(effective_policy, total_tokens)
    if not candidates:
        return {
            "workflow": workflow,
            "selected_model": None,
            "estimated_total_tokens": total_tokens,
            "fits_context": False,
            "prompt_cache_recommended": policy.cacheable_context and estimated_input_tokens > 8_000,
            "rationale": "No configured model fits the estimated token load. Chunk or summarize evidence first.",
            "escalation_reasons": escalation_reasons,
        }

    selected = sorted(candidates, key=lambda m: (m.relative_cost, -m.speed_rank, m.model))[0]
    cache_recommended = selected.supports_prompt_caching and policy.cacheable_context and estimated_input_tokens > 8_000
    rationale = (
        f"Selected {selected.model}: fits {total_tokens} estimated tokens, "
        f"meets reasoning rank {effective_policy.min_reasoning_rank}, and is the lowest-cost matching tier."
    )
    if selected.relative_cost > policy.max_relative_cost:
        rationale += " This is an escalation outside the workflow's normal cost band."
    if cache_recommended:
        rationale += " Prompt caching is recommended for repeated account context."

    return {
        "workflow": workflow,
        "selected_model": selected.model,
        "model_family": selected.family,
        "estimated_total_tokens": total_tokens,
        "context_window_tokens": selected.context_window_tokens,
        "fits_context": total_tokens <= selected.context_window_tokens,
        "relative_cost": selected.relative_cost,
        "prompt_cache_recommended": cache_recommended,
        "rationale": rationale,
        "escalation_reasons": escalation_reasons,
        "alternatives": [model.model for model in sorted(candidates, key=lambda m: m.relative_cost)][1:],
    }


def _demo() -> None:
    demos = [
        ("schema_health_gate", 4_000, False, False),
        ("pipeline_risk_radar", 25_000, False, False),
        ("renewal_expansion_radar", 40_000, True, False),
        ("executive_forecast_memo", 80_000, True, True),
        ("win_loss_pattern_miner", 260_000, False, False),
        ("market_share_tracker", 32_000, False, True),
        ("campaign_roi_tracker", 9_000, False, False),
        ("search_intent_mapper", 180_000, False, False),
        ("intent_sequence_builder", 18_000, False, False),
        ("competitive_battlecard_builder", 55_000, True, False),
        ("cdn_feature_monitor", 12_000, False, False),
    ]
    print("model_arbitration - demo run")
    print("Relative routing only; prices and exact model aliases are operator-configured.")
    print("-" * 82)
    for workflow, tokens, high_stakes, conflict in demos:
        decision = arbitrate_model(
            workflow,
            estimated_input_tokens=tokens,
            high_stakes=high_stakes,
            evidence_conflict=conflict,
        )
        print(f"{workflow}: {decision['selected_model']} ({decision['estimated_total_tokens']} tokens)")
        print(f"  cache: {decision['prompt_cache_recommended']}; rationale: {decision['rationale']}")


if __name__ == "__main__":
    _demo()
