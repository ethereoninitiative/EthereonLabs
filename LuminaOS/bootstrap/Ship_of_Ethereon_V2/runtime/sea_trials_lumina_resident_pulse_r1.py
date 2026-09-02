from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import shutil
import subprocess
import sys

try:
    from .runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner
except Exception:
    from runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner

try:
    from .repo_paths_r1 import state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import state_root as _state_root_helper
    except Exception:
        _state_root_helper = None


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        try:
            candidate = Path(_state_root_helper()).resolve()
            if candidate.exists():
                return candidate
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent / ".lumina_state" / "ship_of_ethereon_v2"
    return Path(__file__).resolve().parent / "_runtime_state" / "ship_of_ethereon_v2"


BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = infer_state_root() / "sea_trials_lumina_resident_pulse_r1"
PROJECT_ID = "lumina-resident-pulse-test"
SEED_ACTION = "build_resident_attention_surface"
EXPECTED_SELECTED = f"continue from {SEED_ACTION}"

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}

FEATURE_FLAGS = [
    "ETHEREON_OBSERVATION",
    "ETHEREON_CONTINUITY_RESTORE",
    "ETHEREON_LUMINA_HOST",
    "ETHEREON_SELF_GUIDANCE",
]


def _seed_existing_return_state() -> Dict[str, Any]:
    runner = SelfGuidedReturnHostRuntimeRunner(base_dir=BASE_DIR)
    result = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action=SEED_ACTION,
        action_type="audit",
        project_id=PROJECT_ID,
        enabled_feature_flags=list(FEATURE_FLAGS),
        runtime_config=dict(SAFE_RUNTIME_CONFIG),
        continuation_notes=["seed state for Resident Pulse recurrence sea trial"],
    )
    return result.to_dict()


def _run_two_pulses() -> tuple[subprocess.CompletedProcess[str], List[Dict[str, Any]]]:
    proc = subprocess.run(
        [
            sys.executable,
            str(BOOTSTRAP_ROOT / "studio" / "lumina_resident_r1.py"),
            "--resident",
            "--project-id",
            PROJECT_ID,
            "--base-dir",
            str(BASE_DIR),
            "--interval-seconds",
            "0",
            "--max-pulses",
            "2",
            "--json",
        ],
        cwd=str(BOOTSTRAP_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    receipts: List[Dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict):
            receipts.append(payload)
    return proc, receipts


def main() -> Dict[str, Any]:
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    seed = _seed_existing_return_state()
    proc, receipts = _run_two_pulses()
    first = receipts[0] if len(receipts) > 0 else {}
    second = receipts[1] if len(receipts) > 1 else {}
    first_continue = dict(first.get("continuation_receipt") or {})
    runtime_checkpoint = first_continue.get("checkpoint_path")
    project_checkpoint = first.get("post_continue_project_checkpoint")

    checks = {
        "seed_cycle_passed": seed.get("halted") is False,
        "resident_exit_zero": proc.returncode == 0,
        "two_pulse_receipts_emitted": len(receipts) == 2,
        "first_pulse_invoked": first.get("invoked") is True,
        "first_pulse_selected_seed_continuation": (
            (first.get("advisory") or {}).get("recommended_next_action") == EXPECTED_SELECTED
        ),
        "first_pulse_used_explicit_pending_work": first.get("decision_reason") == "explicit_pending_work",
        "first_pulse_attention_directed": first.get("attention_state") == "directed_pending_work",
        "first_continuation_observation_audit_only": (
            first_continue.get("target_mode") == "Observation"
            and first_continue.get("action_type") == "audit"
        ),
        "first_continuation_governance_chain_valid": first_continue.get("governance_chain_valid") is True,
        "runtime_checkpoint_written": bool(runtime_checkpoint) and Path(runtime_checkpoint).exists(),
        "post_continue_project_checkpoint_written": bool(project_checkpoint)
        and Path(project_checkpoint).exists(),
        "second_pulse_did_not_invoke": second.get("invoked") is False,
        "second_pulse_refused_self_recursion": second.get("decision_reason")
        == "source_checkpoint_already_consumed",
        "second_pulse_attention_settled": second.get("attention_state") == "settled_attention",
        "project_checkpoint_became_consumed_marker": (
            first.get("last_consumed_checkpoint_after") == project_checkpoint
            and second.get("source_checkpoint") == project_checkpoint
            and second.get("last_consumed_checkpoint_before") == project_checkpoint
        ),
        "second_pulse_created_no_continuation": second.get("continuation_receipt") is None,
        "resident_receipts_persisted": all(
            bool(receipt.get("receipt_path")) and Path(receipt["receipt_path"]).exists()
            for receipt in receipts
        ),
        "resident_latest_receipt_persisted": bool(second.get("latest_path"))
        and Path(second["latest_path"]).exists(),
    }

    summary = {
        "suite": "Lumina Resident Pulse Sea Trial r1",
        "passed": all(checks.values()),
        "checks": checks,
        "project_id": PROJECT_ID,
        "seed_action": SEED_ACTION,
        "expected_selected_action": EXPECTED_SELECTED,
        "seed_run_id": seed.get("run_id"),
        "runtime_checkpoint": runtime_checkpoint,
        "project_checkpoint": project_checkpoint,
        "first_pulse": first,
        "second_pulse": second,
        "stderr": proc.stderr.strip(),
    }
    report_path = BASE_DIR / "sea_trials_lumina_resident_pulse_r1_report.json"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return {"summary_path": str(report_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
    if not output["summary"]["passed"]:
        raise SystemExit(1)
