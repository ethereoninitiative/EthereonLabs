from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import shutil

try:
    from .runtime_runner_psi42_v18_adapter_r1 import RuntimeRunner
except Exception:
    from runtime_runner_psi42_v18_adapter_r1 import RuntimeRunner


BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / "_runtime_state" / "sea_trials_runtime_runner_psi42_v18_wiring_r1"

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


def check_runner_prefers_v18() -> Dict[str, Any]:
    if STATE_DIR.exists():
        shutil.rmtree(STATE_DIR)
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    runner = RuntimeRunner(base_dir=STATE_DIR / "runner")
    result = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="psi42_v18_wiring_sea_trial",
        action_type="audit",
        enabled_feature_flags=[
            "ETHEREON_OBSERVATION",
            "ETHEREON_PSI42",
            "ETHEREON_PSI42_V17",
            "ETHEREON_PSI42_V18",
            "ETHEREON_RESONANCE",
        ],
        ethereonic_overlay={
            "active": True,
            "anchor_language": ["english"],
            "continuity_phrase": "v1.8 wiring sea trial",
            "harmonic_signature": [],
            "spiral_reference": None,
        },
        runtime_config={
            "toki_pona_required_for_resume": False,
            "binary_required_for_transition_validation": False,
            "light_language_required_for_capability_loading": False,
            "harmonic_frequency_required_for_mode_legality": False,
        },
        raw_user_input="Run a bounded Observation audit through Psi-42 v1.8 wiring.",
        project_id="lumina-os",
    ).to_dict()

    probe = result.get("probe_artifacts") or {}
    metrics = probe.get("metrics") or {}
    diagnostics = probe.get("transceiver_diagnostics") or {}
    exposed_ids = {cap.get("capability_id") for cap in result.get("exposed_capabilities", [])}
    governance = result.get("governance") or {}
    checks = {
        "cycle_not_halted": result.get("halted") is False,
        "governance_chain_valid": (result.get("governance_chain_status") or {}).get("valid") is True,
        "v18_capability_exposed": "psi42_transceiver_v18" in exposed_ids,
        "probe_executed_as_v18": probe.get("instrument_version") == "v1.8",
        "diagnostics_present": REQUIRED_DIAGNOSTICS.issubset(set(diagnostics.keys())),
        "metrics_include_presence_index": "presence_index" in metrics,
        "metrics_include_tuning_lock": "tuning_lock" in metrics,
        "derived_drift_profile_present": isinstance(probe.get("derived_drift_profile"), str),
        "authority_boundary_excludes_governance": "governance law" in (probe.get("authority_boundary") or {}).get("does_not_own", []),
        "capability_exposure_recorded": "capability_exposure" in governance,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "result_summary": {
            "run_id": result.get("run_id"),
            "probe_version": probe.get("instrument_version"),
            "probe_run_id": probe.get("run_id"),
            "derived_drift_profile": probe.get("derived_drift_profile"),
            "diagnostics": diagnostics,
            "exposed_capabilities": sorted(exposed_ids),
            "log_path": result.get("log_path"),
        },
    }


def main() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = [
        {"trial_name": "runner_prefers_v18", **check_runner_prefers_v18()},
    ]
    summary = {
        "suite": "Sea Trials Runtime Runner Psi-42 v1.8 Wiring r1",
        "passed": all(item.get("passed") for item in results),
        "results": results,
        "state_dir": str(STATE_DIR),
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = STATE_DIR / "sea_trials_runtime_runner_psi42_v18_wiring_r1_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    summary["summary_path"] = str(summary_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
