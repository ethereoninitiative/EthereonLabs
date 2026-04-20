from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

try:
    from .runtime_runner_return_host_bridge_r1 import ReturnHostBridgedRuntimeRunner
except Exception:
    from runtime_runner_return_host_bridge_r1 import ReturnHostBridgedRuntimeRunner

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
            return Path(_state_root_helper())
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent / ".lumina_state" / "ship_of_ethereon_v2"
    return Path(__file__).resolve().parents[4] / ".lumina_state" / "ship_of_ethereon_v2"


BASE_DIR = infer_state_root() / "sea_trials_lumina_working_stance_r1"
if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}


def _read_json(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> Dict[str, Any]:
    runner = ReturnHostBridgedRuntimeRunner(base_dir=BASE_DIR)

    first = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="trial_working_stance_first_pass",
        action_type="audit",
        project_id="lumina-core",
        runtime_config=SAFE_RUNTIME_CONFIG,
    )
    first_session = _read_json(first.session_path)
    first_bundle = _read_json(runner.context_builder.output_dir / f"{first.context_bundle_id}.json")

    second = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="trial_working_stance_second_pass",
        action_type="audit",
        project_id="lumina-core",
        runtime_config=SAFE_RUNTIME_CONFIG,
    )
    second_session = _read_json(second.session_path)
    second_bundle = _read_json(runner.context_builder.output_dir / f"{second.context_bundle_id}.json")

    first_checks = {
        "session_project_id_present": first_session.get("project_id") == "lumina-core",
        "session_working_stance_present": isinstance(first_session.get("working_stance"), dict),
        "context_active_project_id_present": first_bundle.get("artifact_context", {}).get("active_project_id") == "lumina-core",
        "context_working_stance_summary_present": isinstance(first_bundle.get("artifact_context", {}).get("working_stance_summary"), dict),
    }

    second_checks = {
        "resolved_project_return_present": isinstance(second_bundle.get("artifact_context", {}).get("resolved_project_return"), dict),
        "resolved_host_bundle_present": isinstance(second_bundle.get("artifact_context", {}).get("resolved_host_bundle"), dict),
        "resolved_return_strategy_checkpoint_plus_host": second_bundle.get("artifact_context", {}).get("resolved_project_return", {}).get("return_strategy") == "checkpoint_plus_host",
        "session_focus_updated_to_second_action": second_session.get("working_stance", {}).get("focus_target") == "trial_working_stance_second_pass",
        "session_linked_restore_checkpoint_present": bool(second_session.get("working_stance", {}).get("linked_restore_checkpoint")),
        "session_linked_host_bundle_present": bool(second_session.get("working_stance", {}).get("linked_host_bundle")),
    }

    summary = {
        "suite": "Lumina Working Stance Sea Trial r1",
        "passed": all(first_checks.values()) and all(second_checks.values()),
        "first_run": {
            "run_id": first.run_id,
            "context_bundle_id": first.context_bundle_id,
            "session_path": first.session_path,
            "checks": first_checks,
        },
        "second_run": {
            "run_id": second.run_id,
            "context_bundle_id": second.context_bundle_id,
            "session_path": second.session_path,
            "checks": second_checks,
            "resolved_project_return": second_bundle.get("artifact_context", {}).get("resolved_project_return"),
            "resolved_host_bundle": second_bundle.get("artifact_context", {}).get("resolved_host_bundle"),
            "working_stance": second_session.get("working_stance"),
        },
    }

    summary_path = BASE_DIR / "sea_trials_lumina_working_stance_r1_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {"summary_path": str(summary_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
