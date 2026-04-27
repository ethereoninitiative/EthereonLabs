from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from continuity_weather_layer_r1 import build_continuity_weather
except Exception:
    try:
        from .continuity_weather_layer_r1 import build_continuity_weather
    except Exception:
        build_continuity_weather = None


AUTHORITY_BOUNDARY = (
    "display surface only; may show continuity weather but may not authorize action, "
    "alter governance, alter canon lineage, change mode legality, or execute tools"
)


def render_weather_panel(weather_state: Dict[str, Any]) -> str:
    """Render continuity weather as a small human-readable panel."""

    weather = weather_state or {}
    lines = [
        "Lumina Continuity Weather",
        "-------------------------",
        f"State: {weather.get('weather_state', 'unknown')}",
        f"Dominant harmonic: {weather.get('dominant_harmonic', 'unknown')}",
        f"Recommended stance: {weather.get('recommended_stance', 'observe')}",
        f"Risk: {weather.get('risk_level', 'unknown')}",
        f"Summary: {weather.get('summary', 'No continuity weather available.')}",
        "",
        f"Boundary: {AUTHORITY_BOUNDARY}",
    ]
    return "\n".join(lines)


def build_and_render_weather_panel(
    metrics: Dict[str, Any],
    *,
    harmonic_annotation: Optional[Dict[str, Any]] = None,
    requested_action: Optional[str] = None,
) -> str:
    """Build and render weather without granting runtime authority."""

    if build_continuity_weather is None:
        return render_weather_panel(
            {
                "weather_state": "unavailable",
                "dominant_harmonic": "unknown",
                "recommended_stance": "observe",
                "risk_level": "unknown",
                "summary": "Continuity weather layer unavailable; runtime remains functional.",
            }
        )
    weather = build_continuity_weather(
        metrics,
        harmonic_annotation=harmonic_annotation,
        requested_action=requested_action,
    )
    return render_weather_panel(weather)


if __name__ == "__main__":
    sample = {
        "lock": 0.63,
        "presence": 0.48,
        "coherence": 0.59,
        "CRS": 0.52,
        "AGR": 0.08,
        "RF": 0.88,
    }
    print(build_and_render_weather_panel(sample, requested_action="continuity display"))
