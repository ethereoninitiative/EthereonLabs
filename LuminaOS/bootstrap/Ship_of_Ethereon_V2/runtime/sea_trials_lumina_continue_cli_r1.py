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


def main() -> Dict[str, Any]:
    if BASE_DIR.exists():
        shutil.rmtree(BASE_DIR)
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    seed = _seed_existing_return_state()
    proc, receipt = _run_cli()

    runtime_log: Dict[str, Any] = {}
    log_path = Path(receipt.get("log_path") or "")
    if log_path.exists():
        runtime_log = json.loads(log_path.read_text(encoding="utf-8"))

    preflight_gov = dict((runtime_log.get("governance") or {}).get("self_guided_continue_preflight") or {})
    checks = {
        "seed_cycle_passed": seed.get("halted") is False,
        "cli_exit_zero": proc.returncode == 0,
        "cli_emitted_json_receipt": bool(receipt),
        "existing_pending_action_selected": receipt.get("selected_next_action") == EXPECTED_SELECTED,
        "preflight_used_pending_history": receipt.get("preflight_guidance_strategy") in {
            "pending_next_action",
            "pending_next_action_history_aligned",
        },
        "preflight_confidence_high": receipt.get("preflight_confidence_label") in {"high", "very_high"},
        "observation_only": receipt.get("target_mode") == "Observation" and receipt.get("action_type") == "audit",
        "cycle_not_halted": receipt.get("halted") is False,
        "governance_chain_valid": receipt.get("governance_chain_valid") is True,
        "self_guidance_exposed": receipt.get("self_guidance_exposed") is True,
        "checkpoint_written": bool(receipt.get("checkpoint_path")) and Path(receipt["checkpoint_path"]).exists(),
        "selected_action_became_runtime_focus": runtime_log.get("requested_action") == EXPECTED_SELECTED,
        "preflight_governance_receipt_present": preflight_gov.get("selected_next_action") == EXPECTED_SELECTED,
        "preflight_scope_remains_advisory": preflight_gov.get("scope") == "Observation/audit focus selection only",
        "no_mutating_action_type": runtime_log.get("action_type") not in {"mutation", "promotion"},
    }

    summary = {
        "suite": "Lumina Continue CLI Sea Trial r1",
        "passed": all(checks.values()),
        "checks": checks,
        "project_id": PROJECT_ID,
        "seed_action": SEED_ACTION,
        "expected_selected_action": EXPECTED_SELECTED,
        "seed_run_id": seed.get("run_id"),
        "continue_run_id": receipt.get("run_id"),
        "receipt": receipt,
        "cli_stderr": proc.stderr.strip(),
        "runtime_log_path": str(log_path) if log_path else None,
    }

    summary_path = BASE_DIR / "sea_trials_lumina_continue_cli_r1_report.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return {"summary_path": str(summary_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
    if not output["summary"]["passed"]:
        raise SystemExit(1)
