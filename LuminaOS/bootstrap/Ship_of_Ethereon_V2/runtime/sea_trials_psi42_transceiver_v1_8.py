from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json

try:
    from .psi42_transceiver_v1_8 import Config as Psi42V18Config, ResonanceTransceiverV18
except Exception:
    from psi42_transceiver_v1_8 import Config as Psi42V18Config, ResonanceTransceiverV18


BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / "_runtime_state" / "sea_trials_psi42_transceiver_v1_8"
REQUIRED_DIAGNOSTICS = {
    "presence_index",
    "tuning_lock",
    "carrier_stability",
    "rectification_confidence",
    "amplification_gain",
    "feedback_risk",
    "fading_index",
    "noise_floor",
    "dead_spot_risk",
    "coupling_integrity",
    "time_signal_sync",
}


def check_v18_hybrid_probe() -> Dict[str, Any]:
    rt = ResonanceTransceiverV18(
        Psi42V18Config(output_dir=str(STATE_DIR / "hybrid"), language_mode="neutral", probe_mode="hybrid")
    )
    result = rt.run(
        "Lumina OS receives, tunes, rectifies, amplifies, and recomposes continuity under governance.",
        {"LUMINA": 1.0, "CONTINUITY": 0.9, "GOVERNANCE": 1.0, "SIGNAL": 0.7},
    )
    diagnostics = result.get("transceiver_diagnostics", {})
    metrics = result.get("metrics", {})
    boundary = result.get("authority_boundary", {})
    paths = result.get("paths", {})
    checks = {
        "instrument_class_present": result.get("instrument_class") == "doctrine-aligned transceiver diagnostics wrapper",
        "required_diagnostics_present": REQUIRED_DIAGNOSTICS.issubset(set(diagnostics.keys())),
        "diagnostics_are_metrics": all(isinstance(diagnostics.get(key), (int, float)) for key in REQUIRED_DIAGNOSTICS),
        "presence_index_alias_present": metrics.get("presence_index") == diagnostics.get("presence_index"),
        "derived_drift_profile_present": isinstance(result.get("derived_drift_profile"), str),
        "v17_result_present": isinstance(result.get("v17_result"), dict),
        "topology_receipt_present": isinstance((result.get("v17_result") or {}).get("topology_receipt"), dict),
        "summary_path_present": bool(paths.get("v18_summary_path")),
        "does_not_own_governance": "governance law" in boundary.get("does_not_own", []),
        "does_not_own_human_consent": "human consent" in boundary.get("does_not_own", []),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "result_summary": {
            "run_id": result.get("run_id"),
            "probe_mode": result.get("probe_mode"),
            "derived_drift_profile": result.get("derived_drift_profile"),
            "transceiver_diagnostics": diagnostics,
            "v18_summary_path": paths.get("v18_summary_path"),
        },
    }


def check_run_isolation() -> Dict[str, Any]:
    rt = ResonanceTransceiverV18(
        Psi42V18Config(output_dir=str(STATE_DIR / "isolation"), language_mode="neutral", probe_mode="hybrid")
    )
    first = rt.run("Isolation check one", {"CONTINUITY": 0.8})
    second = rt.run("Isolation check two", {"CONTINUITY": 0.8})
    first_path = first.get("paths", {}).get("v18_summary_path")
    second_path = second.get("paths", {}).get("v18_summary_path")
    checks = {
        "run_ids_differ": first.get("run_id") != second.get("run_id"),
        "summary_paths_differ": first_path != second_path,
        "first_path_contains_first_run_id": bool(first.get("run_id") and first.get("run_id") in str(first_path)),
        "second_path_contains_second_run_id": bool(second.get("run_id") and second.get("run_id") in str(second_path)),
    }
    return {"passed": all(checks.values()), "checks": checks}


def main() -> Dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    results: List[Dict[str, Any]] = [
        {"trial_name": "v18_hybrid_probe", **check_v18_hybrid_probe()},
        {"trial_name": "run_isolation", **check_run_isolation()},
    ]
    summary = {
        "suite": "Sea Trials Psi-42 Transceiver v1.8",
        "passed": all(item.get("passed") for item in results),
        "results": results,
        "state_dir": str(STATE_DIR),
    }
    summary_path = STATE_DIR / "sea_trials_psi42_transceiver_v1_8_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    summary["summary_path"] = str(summary_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
