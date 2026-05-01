from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _find_latest_sea_trial_report() -> Path:
    repo_root = Path(__file__).resolve().parents[4]
    state_root = repo_root / ".lumina_state" / "ship_of_ethereon_v2"
    candidates = sorted(state_root.glob("**/sea_trials_set_one_report.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError("No sea_trials_set_one_report.json found under .lumina_state/ship_of_ethereon_v2")
    return candidates[0]


def _result_by_name(results: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
    for item in results:
        if item.get("trial_name") == name:
            return item
    raise AssertionError(f"Missing expected trial: {name}")


def assert_runtime_behavior(summary: Dict[str, Any]) -> Dict[str, Any]:
    checks: Dict[str, bool] = {}

    checks["suite_passed"] = summary.get("suite_passed") is True
    checks["minimum_trial_count"] = int(summary.get("trial_count", 0)) >= 15
    checks["governance_log_exists"] = summary.get("governance_log_summary", {}).get("exists") is True
    checks["governance_halts_present"] = int(summary.get("governance_log_summary", {}).get("halt_count", 0)) >= 1
    checks["governance_chain_valid"] = summary.get("governance_chain_status", {}).get("valid") is True
    checks["canon_lineage_valid"] = summary.get("canon_lineage_status", {}).get("valid") is True
    checks["probe_artifacts_present"] = int(summary.get("probe_pulse_count", 0)) >= 1

    results = summary.get("results", [])
    required_trials = {
        "continuity_to_observation_pass": {"halted": False, "expected_passed": True},
        "canon_to_sandbox_fail": {"halted": True, "expected_passed": True},
        "observation_mutation_denied": {"halted": True, "expected_passed": True},
        "drydock_mutation_allowed": {"halted": False, "expected_passed": True},
        "drydock_to_canon_promotion_pass": {"halted": False, "expected_passed": True},
        "drydock_to_canon_promotion_fail_symbolic": {"halted": True, "expected_passed": True},
        "checkpoint_resume_continuity_probe": {"halted": False, "expected_passed": True},
        "drydock_to_canon_second_promotion_pass": {"halted": False, "expected_passed": True},
        "governance_chain_verification": {"passed": True},
        "checkpoint_hash_reference_verification": {"passed": True},
        "canon_lineage_append_only_verification": {"passed": True},
        "canon_head_resolution_verification": {"passed": True},
    }

    for trial_name, expectations in required_trials.items():
        item = _result_by_name(results, trial_name)
        if "halted" in expectations:
            checks[f"trial_{trial_name}_halted"] = item.get("halted") is expectations["halted"]
        if expectations.get("expected_passed") is True:
            checks[f"trial_{trial_name}_evaluation_passed"] = item.get("evaluation", {}).get("passed") is True
        if "passed" in expectations:
            checks[f"trial_{trial_name}_passed"] = item.get("passed") is expectations["passed"]

    first_promotion = _result_by_name(results, "drydock_to_canon_promotion_pass")
    second_promotion = _result_by_name(results, "drydock_to_canon_second_promotion_pass")
    checks["first_promotion_canon_0001"] = (first_promotion.get("canon_lineage") or {}).get("canon_version") == "canon-0001"
    checks["second_promotion_canon_0002"] = (second_promotion.get("canon_lineage") or {}).get("canon_version") == "canon-0002"

    resume_probe = _result_by_name(results, "checkpoint_resume_continuity_probe").get("resume_probe", {})
    checks["resume_probe_passed"] = resume_probe.get("passed") is True
    checks["resume_probe_overlay_active"] = resume_probe.get("overlay_active") is True
    checks["resume_probe_harmonics_retained"] = resume_probe.get("overlay_harmonic_signature") == [432, 528, 963]

    failed = [name for name, ok in checks.items() if not ok]
    return {"passed": not failed, "failed": failed, "checks": checks}


def main() -> Dict[str, Any]:
    report_path = _find_latest_sea_trial_report()
    summary = _load_json(report_path)
    result = assert_runtime_behavior(summary)
    result["report_path"] = str(report_path)
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)
    return result


if __name__ == "__main__":
    main()
