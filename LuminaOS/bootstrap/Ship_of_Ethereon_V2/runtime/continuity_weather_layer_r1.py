from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

try:
    from psi42_harmonic_annotation_bridge_r1 import resolve_harmonic_annotation
except Exception:
    try:
        from .psi42_harmonic_annotation_bridge_r1 import resolve_harmonic_annotation
    except Exception:
        resolve_harmonic_annotation = None


AUTHORITY_BOUNDARY = (
    "weather advisory only; does not affect governance, canon lineage, mode legality, "
    "checkpoint legality, capability exposure, mutation, promotion, or user consent"
)


@dataclass(frozen=True)
class ContinuityWeatherState:
    weather_state: str
    dominant_harmonic: str
    recommended_stance: str
    summary: str
    drift_level: str
    stability_level: str
    risk_level: str
    raw_metric_snapshot: Dict[str, float]
    harmonic_annotation: Dict[str, Any]
    authority_boundary: str = AUTHORITY_BOUNDARY

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _num(metrics: Dict[str, Any], key: str, default: float = 0.0) -> float:
    value = metrics.get(key, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _level(value: float, *, low: float = 0.33, high: float = 0.66) -> str:
    if value >= high:
        return "high"
    if value >= low:
        return "moderate"
    return "low"


def _inverse_level(value: float, *, low: float = 0.33, high: float = 0.66) -> str:
    if value >= high:
        return "high"
    if value >= low:
        return "moderate"
    return "low"


def build_continuity_weather(
    metrics: Dict[str, Any],
    *,
    harmonic_annotation: Optional[Dict[str, Any]] = None,
    requested_action: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a non-authoritative continuity weather state.

    The weather layer summarizes Psi-42-style metrics and harmonic annotations for
    human situational awareness. It must not authorize actions or alter runtime law.
    """

    metrics_copy = deepcopy(metrics or {})
    if harmonic_annotation is None:
        if resolve_harmonic_annotation is None:
            harmonic_annotation = {
                "dominant_frequency": "432+528",
                "recommended_stance": "blend",
                "label": "coherence_repair_blend",
                "diagnostic_phrase": "coherence held through active stabilization",
                "authority_boundary": AUTHORITY_BOUNDARY,
            }
        else:
            harmonic_annotation = resolve_harmonic_annotation(metrics_copy, requested_action=requested_action)
    else:
        harmonic_annotation = deepcopy(harmonic_annotation)

    lock = _num(metrics_copy, "lock", _num(metrics_copy, "alignment_strength", 0.0))
    presence = _num(metrics_copy, "presence", 0.0)
    coherence = _num(metrics_copy, "coherence", _num(metrics_copy, "signal_coherence", 0.0))
    crs = _num(metrics_copy, "CRS", _num(metrics_copy, "continuity_recovery_score", 0.0))
    agr = _num(metrics_copy, "AGR", 0.0)
    rf = _num(metrics_copy, "RF", _num(metrics_copy, "recomposition_fidelity", 0.0))
    drift = _num(metrics_copy, "decoherence_index", _num(metrics_copy, "drift_index", 1.0 - max(lock, coherence)))

    stability_score = max(0.0, min(1.0, 0.35 * lock + 0.25 * presence + 0.25 * coherence + 0.15 * crs))
    repair_score = max(0.0, min(1.0, 0.45 * agr + 0.35 * (1.0 - rf if rf else 0.0) + 0.20 * crs))
    drift_score = max(0.0, min(1.0, drift))

    dominant = str(harmonic_annotation.get("dominant_frequency", "432+528"))
    stance = str(harmonic_annotation.get("recommended_stance", "blend"))

    if drift_score >= 0.66 and dominant == "963":
        weather_state = "branching_front"
        summary = "branching paths detected; keep resolution advisory"
    elif repair_score >= 0.28 or dominant == "528":
        weather_state = "coherent_repair"
        summary = "repair path active; coherence stabilizing"
    elif stability_score >= 0.58 and dominant == "432":
        weather_state = "clear_continuity"
        summary = "continuity surface held"
    elif stability_score < 0.30 and drift_score >= 0.50:
        weather_state = "drift_watch"
        summary = "drift rising; consolidate before action"
    else:
        weather_state = "mixed_weather"
        summary = "coherence held through active stabilization"

    risk_level = "low"
    if drift_score >= 0.66 or stability_score < 0.30:
        risk_level = "high"
    elif drift_score >= 0.35 or repair_score >= 0.25:
        risk_level = "moderate"

    raw_metric_snapshot = {
        "lock": lock,
        "presence": presence,
        "coherence": coherence,
        "CRS": crs,
        "AGR": agr,
        "RF": rf,
        "drift_index": drift_score,
        "stability_score": stability_score,
        "repair_score": repair_score,
    }

    return ContinuityWeatherState(
        weather_state=weather_state,
        dominant_harmonic=dominant,
        recommended_stance=stance,
        summary=summary,
        drift_level=_inverse_level(drift_score),
        stability_level=_level(stability_score),
        risk_level=risk_level,
        raw_metric_snapshot=raw_metric_snapshot,
        harmonic_annotation=harmonic_annotation,
    ).to_dict()


def attach_weather_to_supplemental_context(
    supplemental_ethereonic_context: Dict[str, Any],
    weather_state: Dict[str, Any],
) -> Dict[str, Any]:
    """Attach weather as supplemental context only, returning a new dict."""

    result = dict(supplemental_ethereonic_context or {})
    result["continuity_weather"] = {
        "schema_version": "continuity_weather_layer_r1",
        **deepcopy(weather_state or {}),
    }
    return result


if __name__ == "__main__":
    sample_metrics = {
        "lock": 0.64,
        "presence": 0.50,
        "coherence": 0.61,
        "CRS": 0.56,
        "AGR": 0.04,
        "RF": 0.90,
    }
    print(build_continuity_weather(sample_metrics))
