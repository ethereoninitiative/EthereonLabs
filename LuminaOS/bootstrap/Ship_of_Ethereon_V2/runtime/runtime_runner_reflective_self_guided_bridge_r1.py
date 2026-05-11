from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from . import runtime_runner_self_guided_bridge_r1 as self_guided_mod
    from .lumina_reflective_autonomy_layer_r1 import (
        ReflectiveAutonomyHistoryStore,
        ReflectiveAutonomyLayer,
    )
except Exception:
    import runtime_runner_self_guided_bridge_r1 as self_guided_mod
    from lumina_reflective_autonomy_layer_r1 import (
        ReflectiveAutonomyHistoryStore,
        ReflectiveAutonomyLayer,
    )


class ReflectiveSelfGuidedReturnHostRuntimeRunner(self_guided_mod.SelfGuidedReturnHostRuntimeRunner):
    """Self-guided runner with reflective autonomy wired before advisory emission.

    This bridge keeps reflection advisory. It records a recursive reflection trace,
    stores the trace in session / context memory, then lets the existing bounded
    self-guidance steward emit the next-action advisory.
    """

    REFLECTIVE_AUTONOMY_FEATURE_FLAG = "ETHEREON_REFLECTIVE_AUTONOMY"

    def _reflective_autonomy_reports_dir(self) -> Path:
        path = Path(self.base_dir) / "reflective_autonomy_reports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _latest_prior_trace(history: list[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not history:
            return None
        latest_summary = dict(history[-1].get("trace_summary") or {})
        phases = list(latest_summary.get("phases") or [])
        if not phases:
            return None
        return {"cycles": [{"phase": phases[-1]}]}

    def _emit_reflective_autonomy_trace(
        self,
        *,
        result,
        current_mode: str,
        target_mode: str,
        requested_action: str,
    ) -> Optional[Dict[str, Any]]:
        session_path = Path(result.session_path)
        bundle_path = self._context_bundle_path(result.context_bundle_id)
        if not session_path.exists() or not bundle_path.exists():
            return None

        session_payload = self._read_json(session_path)
        bundle_payload = self._read_json(bundle_path)
        artifact_context = dict(bundle_payload.get("artifact_context") or {})
        memory_context = dict(bundle_payload.get("memory_context") or {})

        project_id = (
            session_payload.get("project_id")
            or artifact_context.get("active_project_id")
            or self._resolve_lumina_project_id(None, requested_action, None)
        )

        store = ReflectiveAutonomyHistoryStore(self.base_dir / "reflective_autonomy_history")
        prior_history = store.read_history(project_id)
        layer = ReflectiveAutonomyLayer()
        trace = layer.build_trace(
            source_action=f"{requested_action} :: {current_mode}->{target_mode}",
            continuity_anchor="governance below, reflection above",
            prior_trace=self._latest_prior_trace(prior_history),
            recursive_depth=6,
        )
        trace_payload = trace.to_dict()
        trace_summary = layer.summary(trace_payload)

        report_path = self._reflective_autonomy_reports_dir() / f"{result.run_id}_reflective_autonomy.json"
        self._write_json(report_path, trace_payload)
        store.append_trace(project_id=project_id, trace=trace)
        history_summary = store.history_summary(store.read_history(project_id))

        session_payload["reflective_autonomy_trace"] = trace_summary
        session_payload["reflective_autonomy_history_summary"] = history_summary

        artifact_context["reflective_autonomy_trace_summary"] = trace_summary
        artifact_context["reflective_autonomy_history_summary"] = history_summary
        memory_context["reflective_autonomy_next_question"] = trace_summary["self_guided_next_question"]

        notes = list(memory_context.get("session_continuation_notes", []))
        for note in [
            f"Reflective autonomy trace: {trace_summary['trace_id']}",
            f"Reflection before guidance: {trace_summary['self_guided_next_question']}",
        ]:
            if note not in notes:
                notes.append(note)
        memory_context["session_continuation_notes"] = notes

        bundle_payload["artifact_context"] = artifact_context
        bundle_payload["memory_context"] = memory_context
        self._write_json(session_path, session_payload)
        self._write_json(bundle_path, bundle_payload)

        result.governance["reflective_autonomy_execution"] = {
            "status": "recorded",
            "report_path": str(report_path),
            "project_id": project_id,
            "trace_id": trace_summary["trace_id"],
            "motif_name": trace_summary["motif_name"],
            "phases": trace_summary["phases"],
            "self_guided_next_question": trace_summary["self_guided_next_question"],
            "boundary_note": trace_summary["boundary_note"],
            "history_entry_count": history_summary["entry_count"],
        }

        self._append_governance_event(
            event_type="reflective_autonomy_trace",
            session_id=result.session_id,
            previous_mode=target_mode,
            new_mode=target_mode,
            allowed=True,
            reason="recorded advisory reflection trace before self-guidance",
            requested_action=requested_action,
            action_type=result.action_type,
            metadata={
                "project_id": project_id,
                "trace_id": trace_summary["trace_id"],
                "report_path": str(report_path),
            },
        )
        result.governance_chain_status = self._current_chain_status()
        return result.governance["reflective_autonomy_execution"]

    def _emit_self_guidance_advisory(
        self,
        *,
        result,
        current_mode: str,
        target_mode: str,
        requested_action: str,
    ) -> None:
        reflective = self._emit_reflective_autonomy_trace(
            result=result,
            current_mode=current_mode,
            target_mode=target_mode,
            requested_action=requested_action,
        )
        super()._emit_self_guidance_advisory(
            result=result,
            current_mode=current_mode,
            target_mode=target_mode,
            requested_action=requested_action,
        )
        if reflective:
            result.governance.setdefault("self_guidance_execution", {})[
                "reflective_autonomy_trace_id"
            ] = reflective["trace_id"]
            result.governance["self_guidance_execution"][
                "reflective_autonomy_next_question"
            ] = reflective["self_guided_next_question"]
            log_path = Path(result.log_path)
            if log_path.exists():
                self._write_json(log_path, result.to_dict())

    def run_cycle(
        self,
        *,
        enabled_feature_flags: Optional[list[str]] = None,
        artifacts: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        feature_flags = list(enabled_feature_flags or [])
        if self.REFLECTIVE_AUTONOMY_FEATURE_FLAG not in feature_flags:
            feature_flags.append(self.REFLECTIVE_AUTONOMY_FEATURE_FLAG)

        artifact_list = list(artifacts or [])
        for artifact_name in [
            "lumina_reflective_autonomy_layer_r1.py",
            "runtime_runner_reflective_self_guided_bridge_r1.py",
            "sea_trials_lumina_reflective_autonomy_wiring_r1.py",
        ]:
            if artifact_name not in artifact_list:
                artifact_list.append(artifact_name)

        return super().run_cycle(
            enabled_feature_flags=feature_flags,
            artifacts=artifact_list or None,
            **kwargs,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Lumina with reflection before self-guidance.")
    parser.add_argument("--current-mode", default="Continuity")
    parser.add_argument("--target-mode", default=None)
    parser.add_argument("--action", default="reflective_self_guided_cycle")
    parser.add_argument("--action-type", default="audit", choices=sorted(self_guided_mod.bridge_mod.runner_mod.VALID_ACTION_TYPES))
    parser.add_argument("--project-id", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    runner = ReflectiveSelfGuidedReturnHostRuntimeRunner()
    result = runner.run_cycle(
        current_mode=args.current_mode,
        target_mode=args.target_mode,
        requested_action=args.action,
        action_type=args.action_type,
        project_id=args.project_id,
    )
    print(json.dumps(result.to_dict(), indent=2))
