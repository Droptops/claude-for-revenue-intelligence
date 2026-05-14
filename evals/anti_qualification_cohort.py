# SPDX-License-Identifier: Apache-2.0
"""Synthetic cohort eval for the anti-qualification scorer.

Generates 200 synthetic deals with planted buyer intent and noisy
consulting/implementation spend ratios, then asks: when the scorer labels a
deal ``POLITICAL_COVER``, how often does the synthetic ground truth say the
deal failed to drive real implementation?

The data is synthetic. The point is not to prove the heuristic correlates with
reality — it is to detect regressions in the scorer's behavior and to have a
number for each label band rather than a vibe.

Cohort generation is seeded; output is deterministic.
"""

from __future__ import annotations

import importlib.util
import random
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


aq_scorer = _load_module(
    "cohort_aq_scorer",
    "agents/anti_qualification_scorer/aq_scorer.py",
)


COHORT_SIZE = 200
SEED = 42

# Planted prior: rough split of buyer intent in the synthetic universe.
# REAL_CHANGE buyers fund implementation; POLITICAL_COVER buyers fund consulting
# as cover; AMBIGUOUS buyers are mixed.
INTENT_PRIOR = (
    ("REAL_CHANGE", 0.40),
    ("POLITICAL_COVER", 0.30),
    ("AMBIGUOUS", 0.30),
)

# Planted P(deal becomes a real implementation | true intent).
IMPLEMENTATION_RATE = {
    "REAL_CHANGE": 0.80,
    "POLITICAL_COVER": 0.20,
    "AMBIGUOUS": 0.50,
}

# Sanity floor for CI. F1 below this on a fresh cohort = regression.
F1_FLOOR = 0.30


def _sample_intent(rng: random.Random) -> str:
    roll = rng.random()
    cumulative = 0.0
    for label, weight in INTENT_PRIOR:
        cumulative += weight
        if roll < cumulative:
            return label
    return INTENT_PRIOR[-1][0]


def _sample_spends(intent: str, rng: random.Random) -> tuple[float, float, str]:
    """Generate (consulting_spend, implementation_spend, data_source) for a deal.

    Ratios are noisy so the scorer's classification is non-trivial — the
    planted band sets the mean ratio; we add lognormal noise so individual
    deals can land in the wrong band.
    """
    impl = round(rng.uniform(100_000, 800_000), 2)
    if intent == "POLITICAL_COVER":
        target_ratio = rng.uniform(2.5, 5.5)
        data_source = rng.choice(["CRM", "CRM_PARTIAL", "MIXED"])
    elif intent == "REAL_CHANGE":
        target_ratio = rng.uniform(0.3, 1.4)
        data_source = rng.choice(["CRM", "CRM", "CRM_PARTIAL"])
    else:  # AMBIGUOUS
        target_ratio = rng.uniform(1.4, 3.1)
        data_source = rng.choice(["CRM_PARTIAL", "MIXED", "ESTIMATED"])
    noise = rng.gauss(1.0, 0.25)
    ratio = max(0.05, target_ratio * noise)
    consulting = round(impl * ratio, 2)
    return consulting, impl, data_source


def generate_cohort(size: int = COHORT_SIZE, seed: int = SEED) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    cohort: list[dict[str, Any]] = []
    for i in range(size):
        intent = _sample_intent(rng)
        consulting, impl, source = _sample_spends(intent, rng)
        became_customer = rng.random() < IMPLEMENTATION_RATE[intent]
        cohort.append({
            "opportunity_id": f"OPP-{i:04d}",
            "true_intent": intent,
            "became_customer": became_customer,
            "consulting_spend": consulting,
            "implementation_spend": impl,
            "data_source": source,
        })
    return cohort


def score_cohort(cohort: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for deal in cohort:
        prediction = aq_scorer.score_opportunity(
            deal["opportunity_id"],
            deal["consulting_spend"],
            deal["implementation_spend"],
            data_source=deal["data_source"],
        )
        scored.append({**deal, **prediction})
    return scored


def _confusion(scored: list[dict[str, Any]]) -> dict[str, int]:
    """Confusion matrix where positive = predicted POLITICAL_COVER, truth = deal failed to become customer."""
    tp = fp = fn = tn = 0
    for row in scored:
        predicted_pc = row["anti_qual_label"] == "POLITICAL_COVER"
        truth_failed = not row["became_customer"]
        if predicted_pc and truth_failed:
            tp += 1
        elif predicted_pc and not truth_failed:
            fp += 1
        elif not predicted_pc and truth_failed:
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def _precision_recall_f1(cm: dict[str, int]) -> tuple[float, float, float]:
    tp, fp, fn = cm["tp"], cm["fp"], cm["fn"]
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1


def _label_distribution(scored: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"POLITICAL_COVER": 0, "AMBIGUOUS": 0, "REAL_CHANGE": 0}
    for row in scored:
        counts[row["anti_qual_label"]] = counts.get(row["anti_qual_label"], 0) + 1
    return counts


def _intent_band_accuracy(scored: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """How often does each planted intent get its corresponding label?"""
    bands: dict[str, dict[str, int]] = {
        intent: {"POLITICAL_COVER": 0, "AMBIGUOUS": 0, "REAL_CHANGE": 0, "n": 0}
        for intent, _ in INTENT_PRIOR
    }
    for row in scored:
        band = bands[row["true_intent"]]
        band[row["anti_qual_label"]] += 1
        band["n"] += 1
    return bands


def main() -> int:
    cohort = generate_cohort()
    scored = score_cohort(cohort)
    cm = _confusion(scored)
    precision, recall, f1 = _precision_recall_f1(cm)
    label_dist = _label_distribution(scored)
    band_accuracy = _intent_band_accuracy(scored)

    print(f"anti_qualification cohort eval — n={len(cohort)} seed={SEED}")
    print("-" * 72)
    print("Cohort composition (planted intent):")
    for intent, weight in INTENT_PRIOR:
        actual = sum(1 for d in cohort if d["true_intent"] == intent)
        print(f"  {intent:<16} target {weight:.0%}   actual {actual:>3}/{len(cohort)} ({actual / len(cohort):.0%})")
    print()
    print("Predicted label distribution:")
    for label, count in label_dist.items():
        print(f"  {label:<16} {count:>3}/{len(scored)} ({count / len(scored):.0%})")
    print()
    print("Per-intent prediction breakdown (rows = planted intent, columns = predicted label):")
    print(f"  {'planted':<16} {'POLITICAL_COVER':>16} {'AMBIGUOUS':>11} {'REAL_CHANGE':>13}  n")
    for intent in ("REAL_CHANGE", "AMBIGUOUS", "POLITICAL_COVER"):
        b = band_accuracy[intent]
        print(
            f"  {intent:<16} {b['POLITICAL_COVER']:>16} {b['AMBIGUOUS']:>11} "
            f"{b['REAL_CHANGE']:>13}  {b['n']}"
        )
    print()
    print("POLITICAL_COVER detection vs. ground-truth implementation failure:")
    print(f"  TP={cm['tp']}  FP={cm['fp']}  FN={cm['fn']}  TN={cm['tn']}")
    print(f"  precision={precision:.3f}  recall={recall:.3f}  F1={f1:.3f}")
    print()
    print("Draft for reviewer judgment. Cohort is synthetic; numbers track the")
    print("scorer's internal calibration, not real-world buyer behavior.")

    if f1 < F1_FLOOR:
        print()
        print(f"FAIL: F1 {f1:.3f} is below sanity floor {F1_FLOOR:.2f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
