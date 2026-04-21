from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import shutil

try:
    from .runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner
    from .lumina_self_guidance_history_r1 import ProjectGuidanceHistoryStore
except Exception:
    from runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner
    from lumina_self_guidance_history_r1 import ProjectGuidanceHistoryStore

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
    "lumina_self_guidance_history_r1.py",
    "runtime_runner_return_host_bridge_r1.py",
    "project_return_repo_native_r1.py",
    "workspace_host_repo_native_r1.py",
    "capability_registry_r1.json",
]


def _load_bundle(runner: SelfGuidedReturnHostRuntimeRunner, context_bundle_id: str) -> Dict[str, Any]:
    bundle_path = runner.context_builder.output_dir / f"{context_bundle_id}.json"
    with bundle_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_session(session_path: str) -> Dict[str, Any]:
    with Path(session_path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _run_probe(runner: SelfGuidedReturnHostRuntimeRunner):
    return runner.run_cycle(
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


def main() -> Dict[str, Any]:
    runner = SelfGuidedReturnHostRuntimeRunner(
        base_dir=BASE_DIR,
        registry_path=infer_runtime_root() / "capability_registry_r1.json",
    )

    first = _run_probe(runner)
    second = _run_probe(runner)

    second_bundle = _load_bundle(runner, second.context_bundle_id)
    second_session = _load_session(second.session_path)

    advisory_summary = second_bundle.get("artifact_context", {}).get("self_guidance_advisory_summary", {})
    history_summary = second_bundle.get("artifact_context", {}).get("self_guidance_history_summary", {})
    memory_context = second_bundle.get("memory_context", {})
    governance_entry = second.governance.get("self_guidance_execution", {})
    refresh_entry = second.governance.get("self_guidance_checkpoint_refresh", {})

    history_store = ProjectGuidanceHistoryStore(BASE_DIR / "self_guidance_history")
    stored_history = history_store.read_history("lumina-core")

    checks = {
        "capability_exposed": "lumina_self_guidance_steward" in [cap.get("capability_id") for cap in second.exposed_capabilities],
        "advisory_attached_to_bundle": isinstance(advisory_summary, dict) and bool(advisory_summary),
        "history_summary_attached": isinstance(history_summary, dict) and bool(history_summary),
        "advisory_attached_to_session": second_session.get("self_guidance_advisory", {}).get("recommended_next_action") == advisory_summary.get("recommended_next_action"),
        "history_summary_attached_to_session": second_session.get("self_guidance_history_summary", {}).get("entry_count") == history_summary.get("entry_count"),
        "recommended_next_action_propagated": memory_context.get("recommended_next_action") == advisory_summary.get("recommended_next_action"),
        "pending_action_preferred": advisory_summary.get("recommended_next_action") == "continue from lumina_self_guidance_probe",
        "history_alignment_strategy_active": advisory_summary.get("guidance_strategy") == "pending_next_action_history_aligned",
        "history_count_grew": history_summary.get("entry_count", 0) >= 2,
        "history_alignment_count_grew": advisory_summary.get("history_alignment_count", 0) >= 1,
        "history_store_contains_two_entries": len(stored_history) >= 2,
        "checkpoint_refresh_recorded": refresh_entry.get("history_entry_count", 0) >= 2,
        "governance_records_execution_not_authority": governance_entry.get("allowed") is True and governance_entry.get("recommended_next_action") == advisory_summary.get("recommended_next_action"),
    }

    summary = {
        "suite": "Lumina Self-Guidance Sea Trial r2",
        "passed": all(checks.values()),
        "checks": checks,
        "first_run_id": first.run_id,
        "second_run_id": second.run_id,
        "context_bundle_id": second.context_bundle_id,
        "session_path": second.session_path,
        "checkpoint_path": second.checkpoint_path,
        "self_guidance_advisory_summary": advisory_summary,
        "self_guidance_history_summary": history_summary,
        "memory_context": memory_context,
        "governance_entry": governance_entry,
        "checkpoint_refresh_entry": refresh_entry,
        "stored_history": stored_history,
    }

    summary_path = BASE_DIR / "sea_trials_lumina_self_guidance_r1_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {"summary_path": str(summary_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
