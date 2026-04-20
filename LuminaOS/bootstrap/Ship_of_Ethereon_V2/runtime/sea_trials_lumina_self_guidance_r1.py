from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

try:
    from .runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner
except Exception:
    from runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner

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
            candidate = Path(_state_root_helper()).resolve()
            if candidate.exists():
                return candidate
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent / ".lumina_state" / "ship_of_ethereon_v2"
    return Path(__file__).resolve().parent / "_runtime_state" / "ship_of_ethereon_v2"


def infer_runtime_root() -> Path:
    if _runtime_root_helper is not None:
        try:
            return Path(_runtime_root_helper())
        except Exception:
            pass
    return Path(__file__).resolve().parent


BASE_DIR = infer_state_root() / "sea_trials_lumina_self_guidance_r1"
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

ARTIFACTS = [
    "runtime_runner_self_guided_bridge_r1.py",
    "lumina_self_guidance_steward_r1.py",
    "runtime_runner_return_host_bridge_r1.py",
    "project_return_repo_native_r1.py",
    "workspace_host_repo_native_r1.py",
    "capability_registry_r1.json",
]


def main() -> Dict[str, Any]:
    runner = SelfGuidedReturnHostRuntimeRunner(
        base_dir=BASE_DIR,
        registry_path=infer_runtime_root() / "capability_registry_r1.json",
    )
    result = runner.run_cycle(
        current_mode="Continuity",
        target_mode="Observation",
        requested_action="lumina_self_guidance_probe",
        action_type="audit",
        ethereonic_overlay=ETHEREONIC_OVERLAY,
        project_id="lumina-core",
        enabled_feature_flags=[
            "ETHEREON_OBSERVATION",
            "ETHEREON_PSI42",
            "ETHEREON_CONTINUITY_RESTORE",
            "ETHEREON_LUMINA_HOST",
            "ETHEREON_SELF_GUIDANCE",
        ],
        runtime_config=SAFE_RUNTIME_CONFIG,
        artifacts=ARTIFACTS,
        continuation_notes=["self-guidance probe active"],
    )

    with Path(result.session_path).open("r", encoding="utf-8") as f:
        session_payload = json.load(f)

    bundle_path = runner.context_builder.output_dir / f"{result.context_bundle_id}.json"
    with bundle_path.open("r", encoding="utf-8") as f:
        bundle_payload = json.load(f)

    advisory_summary = (
        bundle_payload.get("artifact_context", {}).get("self_guidance_advisory_summary", {})
    )
    memory_context = bundle_payload.get("memory_context", {})
    governance_entry = result.governance.get("self_guidance_execution", {})

    checks = {
        "capability_exposed": "lumina_self_guidance_steward" in [cap.get("capability_id") for cap in result.exposed_capabilities],
        "advisory_attached_to_bundle": isinstance(advisory_summary, dict) and bool(advisory_summary),
        "advisory_attached_to_session": session_payload.get("self_guidance_advisory", {}).get("recommended_next_action") == advisory_summary.get("recommended_next_action"),
        "recommended_next_action_propagated": memory_context.get("recommended_next_action") == advisory_summary.get("recommended_next_action"),
        "pending_action_preferred": advisory_summary.get("recommended_next_action") == "continue from lumina_self_guidance_probe",
        "confidence_label_high": advisory_summary.get("confidence_label") == "high",
        "boundary_note_present": "Advisory only" in advisory_summary.get("boundary_note", ""),
        "governance_records_execution_not_authority": governance_entry.get("allowed") is True and governance_entry.get("recommended_next_action") == advisory_summary.get("recommended_next_action"),
    }

    summary = {
        "suite": "Lumina Self-Guidance Sea Trial r1",
        "passed": all(checks.values()),
        "checks": checks,
        "context_bundle_id": result.context_bundle_id,
        "session_path": result.session_path,
        "checkpoint_path": result.checkpoint_path,
        "self_guidance_advisory_summary": advisory_summary,
        "memory_context": memory_context,
        "governance_entry": governance_entry,
    }

    summary_path = BASE_DIR / "sea_trials_lumina_self_guidance_r1_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {"summary_path": str(summary_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
