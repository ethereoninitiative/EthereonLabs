from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

STABLE_KEYS = [
    "suite_passed",
    "trial_count",
    "governance_log_summary.halt_count",
    "governance_chain_status.valid",
    "canon_lineage_status.valid",
    "canon_lineage_status.record_count",
    "probe_pulse_count",
]

REQUIRED_TRIALS = [
    "continuity_to_observation_pass",
    "canon_to_sandbox_fail",
    "observation_mutation_denied",
    "drydock_mutation_allowed",
    "sandbox_canonical_mutation_denied",
    "drydock_to_canon_promotion_pass",
    "drydock_to_canon_promotion_fail_symbolic",
    "input_integrity_load_bearing_halt",
    "ethereonic_attachment_boundary_denied",
    "checkpoint_resume_continuity_probe",
    "drydock_to_canon_second_promotion_pass",
    "governance_chain_verification",
    "checkpoint_hash_reference_verification",
    "canon_lineage_append_only_verification",
    "canon_head_resolution_verification",
]


def _get_path(data: Dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _find_latest_report() -> Path:
    repo_root = Path(__file__).resolve().parents[4]
    state_root = repo_root / ".lumina_state" / "ship_of_ethereon_v2"
    candidates = sorted(state_root.glob("**/sea_trials_set_one_report.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError("No sea trial report found for drift detection")
    return candidates[0]


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _trial_index(summary: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item.get("trial_name"): item for item in summary.get("results", []) if item.get("trial_name")}


def derive_behavior_signature(summary: Dict[str, Any]) -> Dict[str, Any]:
    trials = _trial_index(summary)
    signature: Dict[str, Any] = {key: _get_path(summary, key) for key in STABLE_KEYS}
    signature["required_trials"] = {}
    for name in REQUIRED_TRIALS:
        item = trials.get(name, {})
        signature["required_trials"][name] = {
            "present": bool(item),
            "halted": item.get("halted"),
            "passed": item.get("passed"),
            "evaluation_passed": item.get("evaluation", {}).get("passed"),
            "action_type": item.get("action_type"),
            "target_mode": item.get("target_mode"),
        }
    return signature


def compare_signatures(baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    differences: List[Dict[str, Any]] = []

    for key in STABLE_KEYS:
        if baseline.get(key) != current.get(key):
            differences.append({"key": key, "baseline": baseline.get(key), "current": current.get(key)})

    base_trials = baseline.get("required_trials", {})
    current_trials = current.get("required_trials", {})
    for name in REQUIRED_TRIALS:
        b = base_trials.get(name, {})
        c = current_trials.get(name, {})
        for field in ["present", "halted", "passed", "evaluation_passed", "action_type", "target_mode"]:
            if b.get(field) != c.get(field):
                differences.append({"key": f"trial.{name}.{field}", "baseline": b.get(field), "current": c.get(field)})

    return {"passed": not differences, "differences": differences}


def main() -> Dict[str, Any]:
    report_path = _find_latest_report()
    summary = _load_json(report_path)
    current_signature = derive_behavior_signature(summary)

    repo_root = Path(__file__).resolve().parents[4]
    baseline_path = repo_root / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime" / "runtime_behavior_baseline_r1.json"

    if not baseline_path.exists():
        output = {
            "mode": "baseline_created",
            "passed": True,
            "report_path": str(report_path),
            "baseline_path": str(baseline_path),
            "signature": current_signature,
        }
        baseline_path.write_text(json.dumps(current_signature, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(output, indent=2))
        return output

    baseline_signature = _load_json(baseline_path)
    comparison = compare_signatures(baseline_signature, current_signature)
    output = {
        "mode": "comparison",
        "passed": comparison["passed"],
        "report_path": str(report_path),
        "baseline_path": str(baseline_path),
        "differences": comparison["differences"],
    }
    print(json.dumps(output, indent=2))
    if not output["passed"]:
        raise SystemExit(1)
    return output


if __name__ == "__main__":
    main()
