from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

try:
    from .runtime_runner_orientation_adapter_r1 import OrientationAwareRuntimeRunner
except Exception:
    from runtime_runner_orientation_adapter_r1 import OrientationAwareRuntimeRunner

try:
    from .repo_paths_r1 import runtime_root as _runtime_root_helper, state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import runtime_root as _runtime_root_helper, state_root as _state_root_helper
    except Exception:
        _runtime_root_helper = None
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


def infer_runtime_root() -> Path:
    if _runtime_root_helper is not None:
        try:
            return Path(_runtime_root_helper())
        except Exception:
            pass
    return Path(__file__).resolve().parent


BASE_DIR = infer_state_root() / "sea_trials_orientation_r1"
if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)

ETHEREONIC_OVERLAY = {
    "active": True,
    "anchor_language": ["english", "toki_pona", "binary", "light_language"],
    "continuity_phrase": "threshold as permission",
    "harmonic_signature": [432, 528, 963],
    "spiral_reference": "RSE-v1",
}

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}

PROJECT_ORIENTATION_VECTOR = {
    "focus": "architecture",
    "depth": "foundational",
    "intent": "verify",
    "annotation": "reviewing load-bearing structure before promotion",
}

ARTIFACTS = [
    "project_orientation_vector_v0_1.py",
    "runtime_spine_r1.py",
    "runtime_runner_r1_merged.py",
    "sea_trials_set_one_r1_merged.py",
    "capability_registry_r1.json",
]


def main() -> Dict[str, Any]:
    runner = OrientationAwareRuntimeRunner(
        base_dir=BASE_DIR,
        registry_path=infer_runtime_root() / "capability_registry_r1.json",
    )
    result = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="trial_project_orientation_vector",
        action_type="audit",
        ethereonic_overlay=ETHEREONIC_OVERLAY,
        project_orientation_vector=PROJECT_ORIENTATION_VECTOR,
        enabled_feature_flags=["ETHEREON_OBSERVATION", "ETHEREON_PSI42"],
        runtime_config=SAFE_RUNTIME_CONFIG,
        artifacts=ARTIFACTS,
        continuation_notes=["orientation check active"],
    )

    bundle = runner.read_context_bundle(result.context_bundle_id)
    supplemental = bundle.get("supplemental_ethereonic_context", {})
    artifact_context = bundle.get("artifact_context", {})
    memory_context = bundle.get("memory_context", {})

    project_orientation = supplemental.get("project_orientation_vector", {})
    ordered_artifacts = artifact_context.get("active_design_docs", [])
    continuation_notes = memory_context.get("session_continuation_notes", [])

    checks = {
        "orientation_attached": isinstance(project_orientation, dict) and bool(project_orientation),
        "orientation_focus_matches": project_orientation.get("focus") == "architecture",
        "orientation_authority_matches": project_orientation.get("authority") == "supplemental_ethereonic_context only — read-only from governance perspective",
        "artifact_ordering_changed": ordered_artifacts[:2] == ["runtime_spine_r1.py", "capability_registry_r1.json"],
        "resume_note_present": any("Orientation at last checkpoint:" in note for note in continuation_notes),
        "governance_does_not_own_orientation": "project_orientation_vector" not in result.governance,
    }

    summary = {
        "suite": "Sea Trials Orientation r1",
        "passed": all(checks.values()),
        "checks": checks,
        "context_bundle_id": result.context_bundle_id,
        "ordered_artifacts": ordered_artifacts,
        "continuation_notes": continuation_notes,
        "project_orientation_vector": project_orientation,
        "governance_log_path": result.governance_log_path,
        "checkpoint_path": result.checkpoint_path,
    }

    summary_path = BASE_DIR / "sea_trials_orientation_r1_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {"summary_path": str(summary_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
