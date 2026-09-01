from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from . import runtime_runner_return_host_bridge_r1 as bridge_mod
    from .lumina_self_guidance_steward_r1 import LuminaSelfGuidanceSteward
    from .lumina_self_guidance_history_r1 import ProjectGuidanceHistoryStore
except Exception:
    import runtime_runner_return_host_bridge_r1 as bridge_mod
    from lumina_self_guidance_steward_r1 import LuminaSelfGuidanceSteward
    from lumina_self_guidance_history_r1 import ProjectGuidanceHistoryStore


class SelfGuidedReturnHostRuntimeRunner(bridge_mod.ReturnHostBridgedRuntimeRunner):
    """Preferred Lumina runner when bounded self-guidance should ride on the repo-native return/host bridge."""

    SELF_GUIDANCE_CAPABILITY_ID = "lumina_self_guidance_steward"
    SELF_GUIDANCE_FEATURE_FLAG = "ETHEREON_SELF_GUIDANCE"

    def _self_guidance_reports_dir(self) -> Path:
        path = Path(self.base_dir) / "self_guidance_reports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _context_bundle_path(self, context_bundle_id: str) -> Path:
        return self.context_builder.output_dir / f"{context_bundle_id}.json"

    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write_json(path: Path, payload: Dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def _emit_self_guidance_advisory(
        self,
        *,
        result,
        current_mode: str,
        target_mode: str,
        requested_action: str,
    ) -> None:
        capability_ids = {cap.get("capability_id") for cap in result.exposed_capabilities}
        if self.SELF_GUIDANCE_CAPABILITY_ID not in capability_ids:
            return

        session_path = Path(result.session_path)
        bundle_path = self._context_bundle_path(result.context_bundle_id)
        if not session_path.exists() or not bundle_path.exists():
            return

        session_payload = self._read_json(session_path)
        bundle_payload = self._read_json(bundle_path)

        artifact_context = dict(bundle_payload.get("artifact_context") or {})
        memory_context = dict(bundle_payload.get("memory_context") or {})

        project_id = (
            session_payload.get("project_id")
            or artifact_context.get("active_project_id")
            or self._resolve_lumina_project_id(None, requested_action, None)
        )
        working_stance = (
            dict(session_payload.get("working_stance") or {})
            or dict(artifact_context.get("working_stance_summary") or {})
        )
        resolved_project_return = dict(artifact_context.get("resolved_project_return") or {})
        resolved_host_bundle = dict(artifact_context.get("resolved_host_bundle") or {})

        history_store = ProjectGuidanceHistoryStore(self.base_dir / "self_guidance_history")
        prior_history = history_store.read_history(project_id)

        steward = LuminaSelfGuidanceSteward()
        advisory = steward.advise(
            project_id=project_id,
            requested_action=requested_action,
            current_mode=current_mode,
            target_mode=target_mode,
            resolved_project_return=resolved_project_return,
            resolved_host_bundle=resolved_host_bundle,
            working_stance=working_stance,
            guidance_history=prior_history,
        )
        advisory_payload = advisory.to_dict()
        advisory_summary = steward.advisory_summary(advisory)

        report_path = self._self_guidance_reports_dir() / f"{result.run_id}_self_guidance.json"
        self._write_json(report_path, advisory_payload)

        history_entry = history_store.append_entry(
            project_id=project_id,
            advisory_summary=advisory_summary,
            checkpoint_path=result.checkpoint_path,
            requested_action=requested_action,
            current_mode=current_mode,
            target_mode=target_mode,
            working_stance=working_stance,
            source="checkpoint_refresh",
        )
        refreshed_history = history_store.read_history(project_id)
        history_summary = history_store.history_summary(refreshed_history)

        session_payload["self_guidance_advisory"] = advisory_summary
        session_payload["self_guidance_history_summary"] = history_summary
        session_payload["recommended_next_action"] = advisory_summary["recommended_next_action"]
        self._write_json(session_path, session_payload)

        artifact_context["self_guidance_advisory_summary"] = advisory_summary
        artifact_context["self_guidance_history_summary"] = history_summary
        memory_context["recommended_next_action"] = advisory_summary["recommended_next_action"]
        notes = list(memory_context.get("session_continuation_notes", []))
        note = (
            f"Self-guidance recommends: {advisory_summary['recommended_next_action']} "
            f"({advisory_summary['confidence_label']})"
        )
        if note not in notes:
            notes.append(note)
        refresh_note = f"Self-guidance history entries: {history_summary['entry_count']}"
        if refresh_note not in notes:
            notes.append(refresh_note)
        memory_context["session_continuation_notes"] = notes
        bundle_payload["artifact_context"] = artifact_context
        bundle_payload["memory_context"] = memory_context
        self._write_json(bundle_path, bundle_payload)

        result.governance["self_guidance_execution"] = {
            "allowed": True,
            "report_path": str(report_path),
            "project_id": advisory_summary["project_id"],
            "recommended_next_action": advisory_summary["recommended_next_action"],
            "confidence_label": advisory_summary["confidence_label"],
            "confidence_score": advisory_summary["confidence_score"],
            "reasoning_brief": advisory_summary["reasoning_brief"],
            "boundary_note": advisory_summary["boundary_note"],
            "history_entry_count": history_summary["entry_count"],
            "history_alignment_count": advisory_summary.get("history_alignment_count", 0),
        }
        result.governance["self_guidance_checkpoint_refresh"] = {
            "allowed": True,
            "project_id": project_id,
            "history_entry_count": history_summary["entry_count"],
            "latest_recommendation": history_summary.get("latest_recommendation"),
            "latest_checkpoint_path": history_summary.get("latest_checkpoint_path"),
            "history_entry_timestamp": history_entry.get("timestamp_utc"),
        }

        self._append_governance_event(
            event_type="self_guidance_advisory",
            session_id=result.session_id,
            previous_mode=target_mode,
            new_mode=target_mode,
            allowed=True,
            reason="emitted bounded self-guidance advisory",
            requested_action=requested_action,
            action_type=result.action_type,
            metadata={
                "project_id": advisory_summary["project_id"],
                "recommended_next_action": advisory_summary["recommended_next_action"],
                "confidence_label": advisory_summary["confidence_label"],
                "report_path": str(report_path),
            },
        )
        self._append_governance_event(
            event_type="self_guidance_checkpoint_refresh",
            session_id=result.session_id,
            previous_mode=target_mode,
            new_mode=target_mode,
            allowed=True,
            reason="refreshed bounded self-guidance history from checkpoint outcome",
            requested_action=requested_action,
            action_type=result.action_type,
            metadata={
                "project_id": project_id,
                "history_entry_count": history_summary["entry_count"],
                "latest_recommendation": history_summary.get("latest_recommendation"),
                "latest_checkpoint_path": history_summary.get("latest_checkpoint_path"),
            },
        )
        result.governance_chain_status = self._current_chain_status()

        log_path = Path(result.log_path)
        if log_path.exists():
            self._write_json(log_path, result.to_dict())

    def run_cycle(
        self,
        *,
        current_mode: str = "Continuity",
        target_mode: Optional[str] = None,
        requested_action: str = "sea_trial_cycle",
        enabled_feature_flags: Optional[list[str]] = None,
        artifacts: Optional[list[str]] = None,
        **kwargs: Any,
    ):
        target_mode = target_mode or current_mode
        feature_flags = list(enabled_feature_flags or [])
        if self.SELF_GUIDANCE_FEATURE_FLAG not in feature_flags:
            feature_flags.append(self.SELF_GUIDANCE_FEATURE_FLAG)

        artifact_list = list(artifacts or [])
        for artifact_name in [
            "lumina_continuation_action_r1.py",
            "lumina_self_guidance_steward_r1.py",
            "lumina_self_guidance_history_r1.py",
            "runtime_runner_self_guided_bridge_r1.py",
            "sea_trials_lumina_self_guidance_r1.py",
        ]:
            if artifact_name not in artifact_list:
                artifact_list.append(artifact_name)

        result = super().run_cycle(
            current_mode=current_mode,
            target_mode=target_mode,
            requested_action=requested_action,
            enabled_feature_flags=feature_flags,
            artifacts=artifact_list or None,
            **kwargs,
        )
        self._emit_self_guidance_advisory(
            result=result,
            current_mode=current_mode,
            target_mode=target_mode,
            requested_action=requested_action,
        )
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one tiny Ethereon runtime cycle with bounded Lumina self-guidance.")
    parser.add_argument("--current-mode", default="Continuity")
    parser.add_argument("--target-mode", default=None)
    parser.add_argument("--action", default="sea_trial_cycle")
    parser.add_argument("--action-type", default="transition", choices=sorted(bridge_mod.runner_mod.VALID_ACTION_TYPES))
    parser.add_argument("--target-is-canonical", action="store_true")
    parser.add_argument("--repo-path", default=None)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--enable-flag", action="append", dest="feature_flags", default=[])
    parser.add_argument("--artifact", action="append", dest="artifacts", default=[])
    parser.add_argument("--note", action="append", dest="notes", default=[])
    parser.add_argument("--lineage", default=None)
    parser.add_argument("--overlay-json", default=None)
    parser.add_argument("--runtime-config-json", default=None)
    parser.add_argument("--promotion-json", default=None)
    parser.add_argument("--raw-user-input", default=None)
    parser.add_argument("--context-overrides-json", default=None)
    return parser.parse_args()


def _maybe_json(text: Optional[str]) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    return json.loads(text)


if __name__ == "__main__":
    args = parse_args()
    runner = SelfGuidedReturnHostRuntimeRunner()
    result = runner.run_cycle(
        current_mode=args.current_mode,
        target_mode=args.target_mode,
        requested_action=args.action,
        action_type=args.action_type,
        artifacts=args.artifacts or None,
        continuation_notes=args.notes or None,
        canon_lineage_head=args.lineage,
        ethereonic_overlay=_maybe_json(args.overlay_json),
        enabled_feature_flags=args.feature_flags or None,
        target_is_canonical=args.target_is_canonical,
        promotion_payload=_maybe_json(args.promotion_json),
        runtime_config=_maybe_json(args.runtime_config_json),
        repo_path=args.repo_path,
        raw_user_input=args.raw_user_input,
        context_bundle_overrides=_maybe_json(args.context_overrides_json),
        project_id=args.project_id,
    )
    print(json.dumps(result.to_dict(), indent=2))
