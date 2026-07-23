from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import hashlib
import json

try:
    from psi42_harmonic_annotation_bridge_r1 import resolve_harmonic_annotation
    from continuity_weather_layer_r1 import build_continuity_weather
except Exception:
    from .psi42_harmonic_annotation_bridge_r1 import resolve_harmonic_annotation
    from .continuity_weather_layer_r1 import build_continuity_weather

AUTHORITY_BOUNDARY = "generated display data only; does not authorize action, alter governance, alter canon lineage, change mode legality, expose capabilities, or execute tools"

SAMPLE_METRIC_SETS: Dict[str, Dict[str, Any]] = {
    "stability": {"lock": 0.72, "presence": 0.56, "coherence": 0.66, "CRS": 0.62, "AGR": 0.03, "RF": 0.93, "drift_index": 0.18},
    "repair": {"lock": 0.63, "presence": 0.48, "coherence": 0.59, "CRS": 0.52, "AGR": 0.08, "RF": 0.88, "drift_index": 0.29},
    "expansion": {"lock": 0.42, "presence": 0.36, "coherence": 0.41, "CRS": 0.38, "AGR": 0.04, "RF": 0.82, "drift_index": 0.58},
    "blend": {"lock": 0.55, "presence": 0.44, "coherence": 0.53, "CRS": 0.47, "AGR": 0.06, "RF": 0.86, "drift_index": 0.37},
}
RISK_SCORES = {"low": 1.0, "moderate": 0.65, "high": 0.25}
VOLATILE_SNAPSHOT_KEYS = {"generated_at_utc"}


def _snapshot_observation_payload(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in snapshot.items() if key not in VOLATILE_SNAPSHOT_KEYS}


def _observation_fingerprint(snapshot: Dict[str, Any]) -> str:
    canonical = json.dumps(
        _snapshot_observation_payload(snapshot),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_json_dict(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None

def _display_harmonic(annotation: Dict[str, Any]) -> str:
    freq = str(annotation.get("dominant_frequency", "432+528"))
    label = str(annotation.get("label", "coherence_repair_blend")).replace("_", " ")
    return f"{freq} - {label}"

def synthesize_system_mood(primary_state: Dict[str, Any], trend_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    trend = (trend_analysis or {}).get("trend", "steady_mixed")
    harmonic = str(primary_state.get("harmonic", "blend"))
    risk = primary_state.get("risk", "moderate")
    if risk == "high" or trend == "drift_pressure":
        mood = "drift watch"
        guidance = "Consolidate before action; keep authority boundaries visible."
    elif "432" in harmonic and trend == "stabilizing":
        mood = "calm continuity"
        guidance = "Proceed with verification, documentation, or stable integration."
    elif "528" in harmonic:
        mood = "coherent repair"
        guidance = "Continue restructuring while preserving governance separation."
    elif "963" in harmonic:
        mood = "open expansion"
        guidance = "Explore branches, then return to consolidation before promotion."
    else:
        mood = "held transformation"
        guidance = "Blend exploration with stabilization; keep outputs advisory."
    return {"schema_version": "lumina_system_mood_r1", "mood": mood, "guidance": guidance, "trend": trend, "risk": risk, "harmonic": harmonic, "authority_boundary": AUTHORITY_BOUNDARY}

def _load_runtime_metric_sets(path: Optional[str | Path]) -> Optional[Dict[str, Dict[str, Any]]]:
    if not path:
        return None
    metric_path = Path(path)
    if not metric_path.exists():
        return None
    with metric_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if isinstance(payload, dict) and isinstance(payload.get("states"), dict):
        return {str(k): dict(v.get("metrics", v)) for k, v in payload["states"].items() if isinstance(v, dict)}
    if isinstance(payload, dict) and isinstance(payload.get("metrics"), dict):
        return {"runtime": dict(payload["metrics"])}
    if isinstance(payload, dict):
        return {str(k): dict(v) for k, v in payload.items() if isinstance(v, dict)}
    return None

def build_snapshot(metric_sets: Optional[Dict[str, Dict[str, Any]]] = None, *, source_label: Optional[str] = None) -> Dict[str, Any]:
    selected_sets = metric_sets or SAMPLE_METRIC_SETS
    states: Dict[str, Any] = {}
    for name, metrics in selected_sets.items():
        annotation = resolve_harmonic_annotation(metrics, requested_action=name)
        weather = build_continuity_weather(metrics, harmonic_annotation=annotation, requested_action=name)
        states[name] = {"reading": weather["weather_state"].replace("_", " "), "weather_state": weather["weather_state"], "harmonic": _display_harmonic(annotation), "stance": weather["recommended_stance"], "risk": weather["risk_level"], "summary": weather["summary"], "metrics": weather["raw_metric_snapshot"], "harmonic_annotation": annotation, "continuity_weather": weather}
    primary = states.get("repair") or next(iter(states.values()), {})
    return {"schema_version": "lumina_weather_snapshot_r1", "generated_at_utc": datetime.now(timezone.utc).isoformat(), "source": source_label or "generated from sample Psi-42-style metric sets through harmonic annotation and continuity weather layers", "authority_boundary": AUTHORITY_BOUNDARY, "system_mood": synthesize_system_mood(primary), "states": states}

def _compact_history_entry(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    states = snapshot.get("states", {})
    primary = states.get("repair") or (next(iter(states.values()), {}) if states else {})
    return {"generated_at_utc": snapshot.get("generated_at_utc"), "observation_fingerprint": _observation_fingerprint(snapshot), "source": snapshot.get("source"), "primary_weather_state": primary.get("weather_state"), "primary_harmonic": primary.get("harmonic"), "primary_stance": primary.get("stance"), "primary_risk": primary.get("risk"), "primary_summary": primary.get("summary"), "system_mood": snapshot.get("system_mood")}

def analyze_history(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    recent = entries[-12:]
    if not recent:
        return {"schema_version": "lumina_weather_trend_analysis_r1", "continuity_health_score": None, "trend": "insufficient_data", "summary": "No history entries available yet.", "authority_boundary": AUTHORITY_BOUNDARY}
    risks = [RISK_SCORES.get(str(e.get("primary_risk", "moderate")), 0.65) for e in recent]
    health = round(sum(risks) / len(risks), 3)
    high_count = sum(1 for e in recent if e.get("primary_risk") == "high")
    low_count = sum(1 for e in recent if e.get("primary_risk") == "low")
    states = [e.get("primary_weather_state") for e in recent]
    state_changes = sum(1 for a, b in zip(states, states[1:]) if a != b)
    if high_count >= max(2, len(recent) // 3):
        trend, summary = "drift_pressure", "Risk pressure is elevated across recent weather entries."
    elif low_count >= max(2, len(recent) // 2):
        trend, summary = "stabilizing", "Recent weather favors low-risk continuity."
    elif state_changes >= max(2, len(recent) // 3):
        trend, summary = "oscillating", "Weather states are changing frequently; watch continuity coherence."
    else:
        trend, summary = "steady_mixed", "Recent weather is mixed but not showing acute instability."
    return {"schema_version": "lumina_weather_trend_analysis_r1", "continuity_health_score": health, "trend": trend, "recent_entry_count": len(recent), "state_change_count": state_changes, "summary": summary, "authority_boundary": AUTHORITY_BOUNDARY}

def update_history(history_path: str | Path, snapshot: Dict[str, Any], *, max_entries: int = 96) -> Path:
    path = Path(history_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    entries: List[Dict[str, Any]] = []
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, dict) and isinstance(existing.get("entries"), list):
                entries = list(existing["entries"])
        except Exception:
            entries = []
    next_entry = _compact_history_entry(snapshot)
    if not entries or entries[-1].get("observation_fingerprint") != next_entry["observation_fingerprint"]:
        entries.append(next_entry)
    entries = entries[-max_entries:]
    analysis = analyze_history(entries)
    latest = entries[-1] if entries else {}
    payload = {"schema_version": "lumina_weather_history_r1", "authority_boundary": AUTHORITY_BOUNDARY, "entry_count": len(entries), "trend_analysis": analysis, "system_mood": synthesize_system_mood(latest, analysis), "entries": entries}
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return path

def write_snapshot(output_path: str | Path, *, metrics_input: Optional[str | Path] = None, history_output: Optional[str | Path] = None) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metric_sets = _load_runtime_metric_sets(metrics_input)
    source = f"generated from runtime metrics input: {metrics_input}" if metric_sets else "generated from bundled sample metrics fallback"
    payload = build_snapshot(metric_sets, source_label=source)
    existing = _load_json_dict(path)
    if existing is not None and _observation_fingerprint(existing) == _observation_fingerprint(payload):
        if history_output and _load_json_dict(Path(history_output)) is None:
            update_history(history_output, existing)
        return path
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    if history_output:
        update_history(history_output, payload)
    return path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Lumina weather snapshot JSON.")
    parser.add_argument("--metrics-input", default=None, help="Optional JSON metrics file from runtime/Psi-42 output")
    parser.add_argument("--output", default=None, help="Optional output path for lumina-weather-snapshot.json")
    parser.add_argument("--history-output", default=None, help="Optional output path for lumina-weather-history.json")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    runtime_dir = Path(__file__).resolve().parent
    repo_root = runtime_dir.parents[3]
    out = Path(args.output) if args.output else repo_root / "data" / "lumina-weather-snapshot.json"
    history = Path(args.history_output) if args.history_output else repo_root / "data" / "lumina-weather-history.json"
    print(write_snapshot(out, metrics_input=args.metrics_input, history_output=history))
