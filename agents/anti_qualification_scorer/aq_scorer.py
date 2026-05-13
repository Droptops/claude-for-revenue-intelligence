# SPDX-License-Identifier: Apache-2.0
"""Anti-qualification scorer.

Computes the ratio of consulting / services spend to implementation /
product spend, and labels the opportunity by thresholds loaded from the
active skill's theory constants.

The ratio is a signal, not a verdict. Every output is a draft for
reviewer judgment.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.loader import load_active_skill  # noqa: E402


@dataclass(frozen=True)
class Thresholds:
    political_cover_min: float
    real_change_max: float


_DRAFT_NOTE = (
    "This output is a draft for reviewer judgment. "
    "Ratio is one signal; interpret in context."
)


def active_skill_thresholds() -> Thresholds:
    """Return anti-qualification thresholds from the active skill."""

    skill = load_active_skill(ROOT)
    values = skill.theory_constants.get("anti_qualification")
    if not isinstance(values, dict):
        raise ValueError(
            f"active skill {skill.name!r} does not define anti_qualification constants"
        )
    return Thresholds(
        political_cover_min=float(values["political_cover_min"]),
        real_change_max=float(values["real_change_max"]),
    )


def _coerce_thresholds(thresholds: Thresholds | Mapping[str, Any] | None) -> Thresholds:
    if thresholds is None:
        return active_skill_thresholds()
    if isinstance(thresholds, Thresholds):
        return thresholds
    return Thresholds(
        political_cover_min=float(thresholds["political_cover_min"]),
        real_change_max=float(thresholds["real_change_max"]),
    )


def _label_for_ratio(ratio: float | None, t: Thresholds) -> str:
    if ratio is None:
        return "AMBIGUOUS"
    if ratio > t.political_cover_min:
        return "POLITICAL_COVER"
    if ratio < t.real_change_max:
        return "REAL_CHANGE"
    return "AMBIGUOUS"


def _confidence(consulting_spend: float, implementation_spend: float, data_source: str, ratio_defined: bool) -> str:
    if not ratio_defined:
        return "LOW"
    data_source = data_source.upper()
    if data_source == "CRM" and consulting_spend > 0 and implementation_spend > 0:
        return "HIGH"
    if data_source in {"CRM_PARTIAL", "MIXED"}:
        return "MEDIUM"
    if data_source == "ESTIMATED":
        return "LOW"
    # default: treat anything other than full CRM as MEDIUM
    return "MEDIUM"


def score_opportunity(
    opportunity_id: str,
    consulting_spend: float,
    implementation_spend: float,
    *,
    data_source: str = "CRM",
    thresholds: Thresholds | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Score one opportunity.

    Parameters
    ----------
    opportunity_id :
        Internal identifier. Carried through to output.
    consulting_spend :
        Buyer's consulting / services spend on the initiative, USD.
    implementation_spend :
        Buyer's implementation / product spend on the initiative, USD.
    data_source :
        One of "CRM", "CRM_PARTIAL", "MIXED", "ESTIMATED". Controls
        confidence.
    thresholds :
        Optional override. When omitted, values are read from the active skill.
    """
    thresholds = _coerce_thresholds(thresholds)
    if consulting_spend < 0 or implementation_spend < 0:
        raise ValueError("spend values must be non-negative")

    if implementation_spend == 0:
        ratio: float | None = None
        rationale = "Implementation spend is zero or unknown; ratio undefined."
    else:
        ratio = round(consulting_spend / implementation_spend, 3)
        rationale = (
            f"consulting_spend / implementation_spend = "
            f"{consulting_spend:.2f} / {implementation_spend:.2f} = {ratio}"
        )

    label = _label_for_ratio(ratio, thresholds)
    confidence = _confidence(
        consulting_spend, implementation_spend, data_source, ratio is not None
    )

    return {
        "opportunity_id": opportunity_id,
        "anti_qualification_ratio": ratio,
        "anti_qual_label": label,
        "confidence": confidence,
        "rationale": rationale,
        "draft_note": _DRAFT_NOTE,
    }


# ---------- standalone demo ----------

def _demo() -> None:
    samples = [
        # POLITICAL_COVER — heavy consulting, light implementation
        {"opportunity_id": "OPP-PC-1", "consulting_spend": 800_000.0, "implementation_spend": 200_000.0, "data_source": "CRM"},
        # REAL_CHANGE — implementation-heavy
        {"opportunity_id": "OPP-RC-1", "consulting_spend": 150_000.0, "implementation_spend": 600_000.0, "data_source": "CRM"},
        # AMBIGUOUS — middle of the band
        {"opportunity_id": "OPP-AM-1", "consulting_spend": 400_000.0, "implementation_spend": 200_000.0, "data_source": "CRM_PARTIAL"},
        # Edge case — undefined ratio
        {"opportunity_id": "OPP-NA-1", "consulting_spend": 250_000.0, "implementation_spend": 0.0, "data_source": "ESTIMATED"},
    ]

    print("anti_qualification_scorer — demo run")
    print("Draft for reviewer judgment. No real opportunity data.")
    print("-" * 72)
    for s in samples:
        r = score_opportunity(**s)
        print(f"{r['opportunity_id']}:")
        for k, v in r.items():
            if k == "opportunity_id":
                continue
            print(f"  {k}: {v}")
        print()


if __name__ == "__main__":
    _demo()
