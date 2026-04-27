from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class HarmonicAnnotation:
    """Non-authoritative annotation derived from Psi-42-style probe metrics."""

    dominant_frequency: str
    recommended_stance: str
    label: str
    diagnostic_phrase: str
    evidence: Dict[str, float]
    authority_boundary: str = (
        "annotation only; does not affect governance, canon lineage, mode legality, "
        "checkpoint legality, capability exposure, mutation, promotion, or user consent"
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


DEFAULT_THRESHOLDS = {
    "stable_lock": 0.60,
    "stable_presence": 0.45,
    "repair_signal": 0.18,
    "branch_signal": 0.55,
    "drift_signal": 0.35,
}


def _num(metrics: Dict[str, Any], key: str, default: float = 0.0) -> float:
    value = metrics.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def resolve_harmonic_annotation(
    metrics: Dict[str, Any],
    *,
    requested_action: Optional[str] = None,
    thresholds: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Resolve a harmonic annotation from Psi-42 metrics without changing the metrics.

    This function is intentionally advisory. It reads metric-like fields and returns
    a human-readable harmonic stance. It must not be used as authority for runtime
    decisions.
    """

    limits = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    lock = _num(metrics, "lock", _num(metrics, "alignment_strength", 0.0))
    presence = _num(metrics, "presence", 0.0)
    coherence = _num(metrics, "coherence", _num(metrics, "signal_coherence", 0.0))
    ucs = _num(metrics, "UCS", _num(metrics, "ucs", 0.0))
    crs = _num(metrics, "CRS", _num(metrics, "continuity_recovery_score", 0.0))
    agr = _num(metrics, "AGR", 0.0)
    rf = _num(metrics, "RF", _num(metrics, "recomposition_fidelity", 0.0))
    asi = _num(metrics, "ASI", 0.0)
    drift = _num(metrics, "decoherence_index", _num(metrics, "drift_index", 0.0))

    action = (requested_action or "").lower()
    exploration_hint = any(word in action for word in ["explore", "imagine", "branch", "concept", "interface", "sandbox"])
    repair_hint = any(word in action for word in ["repair", "refactor", "integrate", "bridge", "mitigate", "recompose"])

    evidence = {
        "lock": lock,
        "presence": presence,
        "coherence": coherence,
        "UCS": ucs,
        "CRS": crs,
        "AGR": agr,
        "RF": rf,
        "ASI": asi,
        "drift_index": drift,
    }

    if repair_hint or agr >= limits["repair_signal"] or (crs > 0 and rf < 0.72):
        annotation = HarmonicAnnotation(
            dominant_frequency="528",
            recommended_stance="restructure",
            label="adaptive_transformation",
            diagnostic_phrase="repair path active; governance still required",
            evidence=evidence,
        )
    elif exploration_hint or drift >= limits["branch_signal"] or (coherence < 0.35 and lock < 0.50):
        annotation = HarmonicAnnotation(
            dominant_frequency="963",
            recommended_stance="explore",
            label="conceptual_expansion",
            diagnostic_phrase="branching paths detected; keep resolution advisory",
            evidence=evidence,
        )
    elif lock >= limits["stable_lock"] and presence >= limits["stable_presence"]:
        annotation = HarmonicAnnotation(
            dominant_frequency="432",
            recommended_stance="consolidate",
            label="presence_stability",
            diagnostic_phrase="continuity surface held",
            evidence=evidence,
        )
    else:
        annotation = HarmonicAnnotation(
            dominant_frequency="432+528",
            recommended_stance="blend",
            label="coherence_repair_blend",
            diagnostic_phrase="coherence held through active stabilization",
            evidence=evidence,
        )

    return annotation.to_dict()


def annotate_psi42_result(
    psi42_result: Dict[str, Any],
    *,
    requested_action: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a copied Psi-42 result with a non-authoritative harmonic annotation.

    Raw metrics are deep-copied and preserved. The annotation is added at top level
    under `harmonic_annotation` and may be copied into supplemental context by the
    caller. This helper performs no governance, canon, capability, or checkpoint work.
    """

    copied = deepcopy(psi42_result)
    metrics = copied.get("metrics") if isinstance(copied.get("metrics"), dict) else copied
    copied["harmonic_annotation"] = resolve_harmonic_annotation(
        metrics,
        requested_action=requested_action,
    )
    return copied


def attach_annotation_to_supplemental_context(
    supplemental_ethereonic_context: Dict[str, Any],
    harmonic_annotation: Dict[str, Any],
) -> Dict[str, Any]:
    """Attach annotation as supplemental context only.

    Returns a new dictionary and does not mutate the input.
    """

    result = dict(supplemental_ethereonic_context or {})
    result["harmonic_state"] = {
        "schema_version": "psi42_harmonic_annotation_bridge_r1",
        **dict(harmonic_annotation or {}),
    }
    return result


if __name__ == "__main__":
    sample = {
        "metrics": {
            "lock": 0.68,
            "presence": 0.51,
            "coherence": 0.62,
            "UCS": 0.58,
            "CRS": 0.55,
            "AGR": 0.02,
            "RF": 0.91,
            "ASI": 0.61,
        }
    }
    annotated = annotate_psi42_result(sample, requested_action="continuity probe")
    print(annotated["harmonic_annotation"])
