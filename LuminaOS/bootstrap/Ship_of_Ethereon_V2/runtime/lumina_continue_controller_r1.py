from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    from .runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner
    from .lumina_self_guidance_steward_r1 import LuminaSelfGuidanceSteward
    from .lumina_self_guidance_history_r1 import ProjectGuidanceHistoryStore
except Exception:
    from runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner
    from lumina_self_guidance_steward_r1 import LuminaSelfGuidanceSteward
    from lumina_self_guidance_history_r1 import ProjectGuidanceHistoryStore


SAFE_RUNTIME_CONFIG: Dict[str, bool] = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}

DEFAULT_FEATURE_FLAGS = [
    "ETHEREON_OBSERVATION",
    "ETHEREON_CONTINUITY_RESTORE",
    "ETHEREON_LUMINA_HOST",
    "ETHEREON_SELF_GUIDANCE",
]

DEFAULT_ARTIFACTS = [
    "runtime/runtime_spine_r1.py",
    "runtime/runtime_runner_r1_merged.py",
    "runtime/runtime_runner_return_host_bridge_r1.py",
    "runtime/runtime_runner_self_guided_bridge_r1.py",
    "runtime/lumina_continuation_action_r1.py",
    "runtime/lumina_self_guidance_steward_r1.py",
    "runtime/lumina_self_guidance_history_r1.py",
    "runtime/lumina_continue_controller_r1.py",
    "runtime/project_return_repo_native_r1.py",
    "runtime/workspace_host_repo_native_r1.py",
    "runtime/capability_registry_r1.json",
]


@dataclass
class ContinueResult:
    preflight_advisory: Dict[str, Any]
    runtime_result: Dict[str, Any]

    def compact_receipt(self) -> Dict[str, Any]:
        governance = dict(self.runtime_result.get("governance") or {})
        exposed = list(self.runtime_result.get("exposed_capabilities") or [])
        post_guidance = dict(governance.get("self_guidance_execution") or {})
        return {
            "run_id": self.runtime_result.get("run_id"),
            "project_id": self.preflight_advisory.get("project_id"),
            "selected_next_action": self.preflight_advisory.get("recommended_next_action"),
            "preflight_guidance_strategy": self.preflight_advisory.get("guidance_strategy"),
            "preflight_confidence_label": self.preflight_advisory.get("confidence_label"),
            "preflight_confidence_score": self.preflight_advisory.get("confidence_score"),
            "preflight_reasoning_brief": self.preflight_advisory.get("reasoning_brief"),
            "preflight_boundary_note": self.preflight_advisory.get("boundary_note"),
            "target_mode": self.runtime_result.get("target_mode"),
            "action_type": self.runtime_result.get("action_type"),
            "halted": self.runtime_result.get("halted"),
            "halt_reason": self.runtime_result.get("halt_reason"),
            "checkpoint_path": self.runtime_result.get("checkpoint_path"),
            "log_path": self.runtime_result.get("log_path"),
            "governance_chain_valid": (self.runtime_result.get("governance_chain_status") or {}).get("valid"),
            "self_guidance_exposed": "lumina_self_guidance_steward" in {
                cap.get("capability_id") for cap in exposed
            },
            "post_cycle_recommended_next_action": post_guidance.get("recommended_next_action"),
            "authority_boundary": (
                "The selected action may focus a governed Observation/audit cycle only. "
                "Self-guidance remains advisory and cannot authorize mutation, promotion, canon, or mode-law changes."
            ),
        }


class LuminaContinueController:
    """Use existing project-return state to choose one bounded Observation focus without operator prompt steering."""

    FALLBACK_REQUEST = "continue_from_latest_checkpoint"

    def __init__(self, runner: Optional[SelfGuidedReturnHostRuntimeRunner] = None, *, base_dir: Optional[str | Path] = None):
        if runner is not None and base_dir is not None:
            raise ValueError("provide runner or base_dir, not both")
        if runner is not None:
            self.runner = runner
        elif base_dir is not None:
            self.runner = SelfGuidedReturnHostRuntimeRunner(base_dir=Path(base_dir))
        else:
            self.runner = SelfGuidedReturnHostRuntimeRunner()

    def preflight(
        self,
        *,
        project_id: Optional[str],
        requested_action: str = FALLBACK_REQUEST,
        current_mode: str = "Continuity",
        target_mode: str = "Observation",
    ) -> Dict[str, Any]:
        resolved_project_id = self.runner._resolve_lumina_project_id(project_id, requested_action, None)
        surface = self.runner._resolve_existing_surface(
            project_id=resolved_project_id,
            requested_action=requested_action,
        )
        history_store = ProjectGuidanceHistoryStore(Path(self.runner.base_dir) / "self_guidance_history")
        prior_history = history_store.read_history(resolved_project_id)
        steward = LuminaSelfGuidanceSteward()
        advisory = steward.advise(
            project_id=resolved_project_id,
            requested_action=requested_action,
            current_mode=current_mode,
            target_mode=target_mode,
            resolved_project_return=surface.get("resolved_project_return"),
            resolved_host_bundle=surface.get("resolved_host_bundle"),
            working_stance=surface.get("working_stance"),
            guidance_history=prior_history,
        )
        return steward.advisory_summary(advisory)

    def continue_cycle(
        self,
        *,
        project_id: Optional[str] = None,
        requested_action: str = FALLBACK_REQUEST,
    ) -> ContinueResult:
        current_mode = "Continuity"
        target_mode = "Observation"
        advisory = self.preflight(
            project_id=project_id,
            requested_action=requested_action,
            current_mode=current_mode,
            target_mode=target_mode,
        )
        selected = str(advisory.get("recommended_next_action") or requested_action)

        result = self.runner.run_cycle(
            current_mode=current_mode,
            target_mode=target_mode,
            requested_action=selected,
            action_type="audit",
            project_id=advisory.get("project_id") or project_id,
            enabled_feature_flags=list(DEFAULT_FEATURE_FLAGS),
            runtime_config=dict(SAFE_RUNTIME_CONFIG),
            artifacts=list(DEFAULT_ARTIFACTS),
            continuation_notes=[
                "Lumina continue selected its Observation focus from pre-cycle project-return/self-guidance state.",
                "The selection is advisory input to an audit cycle, not mutation or governance authority.",
            ],
            context_bundle_overrides={
                "memory_context": {
                    "self_guided_continue_preflight": dict(advisory),
                }
            },
        )

        result.governance["self_guided_continue_preflight"] = {
            "allowed": True,
            "project_id": advisory.get("project_id"),
            "selected_next_action": selected,
            "guidance_strategy": advisory.get("guidance_strategy"),
            "confidence_label": advisory.get("confidence_label"),
            "confidence_score": advisory.get("confidence_score"),
            "reasoning_brief": advisory.get("reasoning_brief"),
            "boundary_note": advisory.get("boundary_note"),
            "scope": "Observation/audit focus selection only",
        }
        self.runner._append_governance_event(
            event_type="self_guided_continue_preflight",
            session_id=result.session_id,
            previous_mode=current_mode,
            new_mode=target_mode,
            allowed=True,
            reason="pre-cycle self-guidance selected bounded Observation focus",
            requested_action=selected,
            action_type="audit",
            metadata={
                "project_id": advisory.get("project_id"),
                "guidance_strategy": advisory.get("guidance_strategy"),
                "confidence_label": advisory.get("confidence_label"),
                "selected_next_action": selected,
                "authority_scope": "advisory focus selection only",
            },
        )
        result.governance_chain_status = self.runner._current_chain_status()
        log_path = Path(result.log_path)
        if log_path.exists():
            with log_path.open("w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2)

        return ContinueResult(preflight_advisory=advisory, runtime_result=result.to_dict())
