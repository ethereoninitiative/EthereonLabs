from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

from runtime_runner_r1_merged import RuntimeRunner
from psi42_v17_observation_receipt_summary_r1 import summarize


BASE_DIR = Path(__file__).resolve().parent / "_sea_trials_tmp" / "psi42_v17_runtime_integration_r1"
REGISTRY_PATH = Path(__file__).with_name("capability_registry_r1.json")

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}

ETHEREONIC_OVERLAY = {
    "active": True,
    "anchor_language": ["english", "toki_pona", "binary", "light_language"],
    "continuity_phrase": "psi42 v1.7 runtime integration sea trial",
    "harmonic_signature": [432, 528, 963],
    "spiral_reference": "RSE-v1",
}


def main() -> int:
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    runner = RuntimeRunner(base_dir=BASE_DIR, registry_path=REGISTRY_PATH)
    result = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="trial_psi42_v17_runtime_integration",
        action_type="audit",
        enabled_feature_flags=[
            "ETHEREON_OBSERVATION",
            "ETHEREON_PSI42",
            "ETHEREON_PSI42_V17",
            "ETHEREON_RESONANCE",
        ],
        ethereonic_overlay=ETHEREONIC_OVERLAY,
        runtime_config=SAFE_RUNTIME_CONFIG,
        raw_user_input="Run Psi-42 v1.7 runtime integration sea trial.",
    )

    receipt: Dict[str, Any] = result.to_dict()
    summary = summarize(receipt)
    exposed_ids = [
        cap.get("capability_id")
        for cap in receipt.get("exposed_capabilities", [])
        if isinstance(cap, dict)
    ]

    checks = {
        **summary["checks"],
        "overall_summary_pass": summary["overall_pass"],
        "v17_capability_exposed": "psi42_transceiver_v17" in exposed_ids,
        "v16_fallback_still_available": "psi42_transceiver_v16" in exposed_ids,
        "receipt_has_probe_artifacts": isinstance(receipt.get("probe_artifacts"), dict),
        "receipt_has_checkpoint": bool(receipt.get("checkpoint_path")),
    }

    report = {
        "suite": "Sea Trials - Psi-42 v1.7 runtime integration r1",
        "passed": all(checks.values()),
        "checks": checks,
        "summary": summary,
        "exposed_capability_ids": exposed_ids,
        "receipt_run_id": receipt.get("run_id"),
        "receipt_log_path": receipt.get("log_path"),
        "checkpoint_path": receipt.get("checkpoint_path"),
        "governance_log_path": receipt.get("governance_log_path"),
    }

    report_path = BASE_DIR / "sea_trials_psi42_v17_runtime_integration_r1_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
