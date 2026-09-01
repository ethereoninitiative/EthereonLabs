from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
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
BASE_DIR = infer_state_root() / "sea_trials_lumina_continue_cli_r1"
PROJECT_ID = "lumina-continue-cli-test"
SEED_ACTION = "build_portable_continuity_bundle"
EXPECTED_SELECTED = f"continue from {SEED_ACTION}"
LEGACY_COMPOUNDED_SELECTED = f"continue from continue from {SEED_ACTION}"

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
        continuation_notes=["seed state for lumina continue CLI sea trial"],
    )
    return result.to_dict()


def _run_cli() -> tuple[subprocess.CompletedProcess[str], Dict[str, Any]]:
    proc = subprocess.run(
        [
            sys.executable,
            str(BOOTSTRAP_ROOT / "bin" / "lumina"),
            "continue",
            "--project-id",
            PROJECT_ID,
            "--base-dir",
            str(BASE_DIR),
            "--json",
        ],
        cwd=str(BOOTSTRAP_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    payload: Dict[str, Any] = {}
    if proc.stdout.strip():
        try:
            parsed = json.loads(proc.stdout)
            if isinstance(parsed, dict):
                payload = parsed
        except Exception:
            payload = {}
    return proc, payload


def _seed_legacy_compounded_pending_action() -> str:
    """Simulate state written before continuation directives became stable."""

    latest_path = (
        BASE_DIR
        / "lumina_project_surface"
        / "project_restores"
        / "latest"
        / f"{PROJECT_ID}.json"
    )
    payload = json.loads(latest_path.read_text(encoding="utf-8"))
    payload["pending_next_action"] = LEGACY_COMPOUNDED_SELECTED
    latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(latest_path)


def _load_runtime_log(receipt: Dict[str, Any]) -> tuple[Path, Dict[str, Any]]:
    log_path = Path(receipt.get("log_path") or "")
    if not log_path.exists():
        return log_path, {}
    return log_path, json.loads(log_path.read_text(encoding="utf-8"))


def main() -> Dict[str, Any]:
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    seed = _seed_existing_return_state()
    legacy_restore_path = _seed_legacy_compounded_pending_action()
    first_proc, first_receipt = _run_cli()
    repeated_proc, repeated_receipt = _run_cli()

    first_log_path, first_runtime_log = _load_runtime_log(first_receipt)
    repeated_log_path, repeated_runtime_log = _load_runtime_log(repeated_receipt)
    first_preflight_gov = dict(
        (first_runtime_log.get("governance") or {}).get("self_guided_continue_preflight") or {}
    )
    repeated_preflight_gov = dict(
        (repeated_runtime_log.get("governance") or {}).get("self_guided_continue_preflight") or {}
    )
    stable_actions = [
        first_receipt.get("selected_next_action"),
        first_receipt.get("post_cycle_recommended_next_action"),
        repeated_receipt.get("selected_next_action"),
        repeated_receipt.get("post_cycle_recommended_next_action"),
    ]
    checks = {
        "seed_cycle_passed": seed.get("halted") is False,
        "legacy_compounded_state_seeded": Path(legacy_restore_path).exists(),
        "cli_exit_zero": first_proc.returncode == 0,
        "cli_emitted_json_receipt": bool(first_receipt),
        "repeated_cli_exit_zero": repeated_proc.returncode == 0,
        "repeated_cli_emitted_json_receipt": bool(repeated_receipt),
        "legacy_pending_action_repaired_before_selection": first_receipt.get("selected_next_action")
        == EXPECTED_SELECTED,
        "existing_pending_action_selected": first_receipt.get("selected_next_action")
        == EXPECTED_SELECTED,
        "repeated_continue_selected_action_stable": repeated_receipt.get("selected_next_action")
        == EXPECTED_SELECTED,
        "post_cycle_recommendation_stable": first_receipt.get("post_cycle_recommended_next_action")
        == EXPECTED_SELECTED,
        "repeated_post_cycle_recommendation_stable": repeated_receipt.get(
            "post_cycle_recommended_next_action"
        )
        == EXPECTED_SELECTED,
        "continuation_prefix_not_compounded": all(
            isinstance(action, str)
            and action.casefold().count("continue from ") == 1
            for action in stable_actions
        ),
        "preflight_used_pending_history": first_receipt.get("preflight_guidance_strategy") in {
            "pending_next_action",
            "pending_next_action_history_aligned",
        },
        "preflight_confidence_high": first_receipt.get("preflight_confidence_label") in {
            "high",
            "very_high",
        },
        "observation_only": all(
            receipt.get("target_mode") == "Observation" and receipt.get("action_type") == "audit"
            for receipt in [first_receipt, repeated_receipt]
        ),
        "cycles_not_halted": all(
            receipt.get("halted") is False for receipt in [first_receipt, repeated_receipt]
        ),
        "cycle_not_halted": first_receipt.get("halted") is False,
        "governance_chains_valid": all(
            receipt.get("governance_chain_valid") is True
            for receipt in [first_receipt, repeated_receipt]
        ),
        "governance_chain_valid": first_receipt.get("governance_chain_valid") is True,
        "self_guidance_exposed": all(
            receipt.get("self_guidance_exposed") is True
            for receipt in [first_receipt, repeated_receipt]
        ),
        "checkpoints_written": all(
            bool(receipt.get("checkpoint_path")) and Path(receipt["checkpoint_path"]).exists()
            for receipt in [first_receipt, repeated_receipt]
        ),
        "checkpoint_written": bool(first_receipt.get("checkpoint_path"))
        and Path(first_receipt["checkpoint_path"]).exists(),
        "selected_action_became_runtime_focus": all(
            runtime_log.get("requested_action") == EXPECTED_SELECTED
            for runtime_log in [first_runtime_log, repeated_runtime_log]
        ),
        "preflight_governance_receipts_present": all(
            governance.get("selected_next_action") == EXPECTED_SELECTED
            for governance in [first_preflight_gov, repeated_preflight_gov]
        ),
        "preflight_governance_receipt_present": first_preflight_gov.get(
            "selected_next_action"
        )
        == EXPECTED_SELECTED,
        "preflight_scope_remains_advisory": all(
            governance.get("scope") == "Observation/audit focus selection only"
            for governance in [first_preflight_gov, repeated_preflight_gov]
        ),
        "no_mutating_action_type": all(
            runtime_log.get("action_type") not in {"mutation", "promotion"}
            for runtime_log in [first_runtime_log, repeated_runtime_log]
        ),
    }

    summary = {
        "suite": "Lumina Continue CLI Sea Trial r1",
        "passed": all(checks.values()),
        "checks": checks,
        "project_id": PROJECT_ID,
        "seed_action": SEED_ACTION,
        "expected_selected_action": EXPECTED_SELECTED,
        "legacy_compounded_selected_action": LEGACY_COMPOUNDED_SELECTED,
        "legacy_restore_path": legacy_restore_path,
        "seed_run_id": seed.get("run_id"),
        "continue_run_id": first_receipt.get("run_id"),
        "repeated_continue_run_id": repeated_receipt.get("run_id"),
        "receipt": first_receipt,
        "repeated_receipt": repeated_receipt,
        "cli_stderr": first_proc.stderr.strip(),
        "repeated_cli_stderr": repeated_proc.stderr.strip(),
        "runtime_log_path": str(first_log_path) if first_log_path else None,
        "repeated_runtime_log_path": str(repeated_log_path) if repeated_log_path else None,
    }

    summary_path = BASE_DIR / "sea_trials_lumina_continue_cli_r1_report.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return {"summary_path": str(summary_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
    if not output["summary"]["passed"]:
        raise SystemExit(1)
