import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from . import runtime_runner_r1_merged as runner_mod
    from .lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
    from .lumina_working_stance_voice_r1 import LuminaWorkingStanceVoice
except Exception:
    import runtime_runner_r1_merged as runner_mod
    from lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
    try:
        from lumina_working_stance_voice_r1 import LuminaWorkingStanceVoice
    except Exception:
        LuminaWorkingStanceVoice = None


runner_mod.ContinuityRestoreStore = ContinuityRestoreStore
runner_mod.LuminaWorkspaceHost = LuminaWorkspaceHost


class ReturnHostBridgedRuntimeRunner(runner_mod.RuntimeRunner):
    """Preferred repo-native runner when Lumina return/host behavior should use the bootstrap-local bridge layer."""

    def _shared_surface_base_dir(self) -> Path:
        return Path(self.base_dir) / "lumina_project_surface"

    def _voice_reports_dir(self) -> Path:
        path = Path(self.base_dir) / "voice_reports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def _deep_merge(cls, base_payload: Optional[Dict[str, Any]], overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        merged = dict(base_payload or {})
        for key, value in (overrides or {}).items():
            existing = merged.get(key)
            if isinstance(existing, dict) and isinstance(value, dict):
                merged[key] = cls._deep_merge(existing, value)
            else:
                merged[key] = value
        return merged

    @staticmethod
    def _summarize_project_return(resolved_project_return: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        if not resolved_project_return:
            return None
        latest = dict(resolved_project_return.get("latest_restore") or {})
        return {
            "return_strategy": resolved_project_return.get("return_strategy"),
            "checkpoint_path": latest.get("checkpoint_path"),
            "current_mode": latest.get("current_mode"),
            "linked_host_bundle": latest.get("linked_host_bundle"),
            "pending_next_action": latest.get("pending_next_action"),
            "last_completed_action": latest.get("last_completed_action"),
        }

    @staticmethod
    def _summarize_host_bundle(resolved_host_bundle: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        if not resolved_host_bundle:
            return None
        return {
            "active_layout_id": resolved_host_bundle.get("active_layout_id"),
            "focus_target": resolved_host_bundle.get("focus_target"),
            "panel_ids": [row.get("panel_id") for row in resolved_host_bundle.get("panels", []) if row.get("panel_id")],
            "pinned_tool_ids": [
                row.get("tool_id")
                for row in resolved_host_bundle.get("tool_bindings", [])
                if row.get("tool_id") and row.get("pinned")
            ],
            "reference_ids": [
                row.get("reference_id")
                for row in resolved_host_bundle.get("references", [])
                if row.get("reference_id")
            ],
            "linked_restore_checkpoint": resolved_host_bundle.get("linked_restore_checkpoint"),
        }

    @staticmethod
    def _working_stance_note(working_stance: Optional[Dict[str, Any]] = None) -> str:
        stance = dict(working_stance or {})
        focus = stance.get("focus_target") or "unspecified focus"
        layout = stance.get("active_layout_id") or "default-workspace"
        panel_count = len(stance.get("open_panels", []))
        return f"Working stance at bundle build: layout={layout}; focus={focus}; panels={panel_count}"

    def _derive_working_stance(
        self,
        *,
        requested_action: str,
        resolved_project_return: Optional[Dict[str, Any]] = None,
        resolved_host_bundle: Optional[Dict[str, Any]] = None,
        host_snapshot_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        host_bundle = dict(resolved_host_bundle or {})
        latest_restore = dict((resolved_project_return or {}).get("latest_restore") or {})
        return {
            "active_layout_id": host_bundle.get("active_layout_id", "runtime-cycle-layout"),
            "focus_target": host_bundle.get("focus_target") or requested_action,
            "open_panels": [row.get("panel_id") for row in host_bundle.get("panels", []) if row.get("panel_id")],
            "pinned_tools": [
                row.get("tool_id")
                for row in host_bundle.get("tool_bindings", [])
                if row.get("tool_id") and row.get("pinned")
            ],
            "reference_ids": [
                row.get("reference_id")
                for row in host_bundle.get("references", [])
                if row.get("reference_id")
            ],
            "linked_restore_checkpoint": host_bundle.get("linked_restore_checkpoint") or latest_restore.get("checkpoint_path"),
            "linked_host_bundle": latest_restore.get("linked_host_bundle"),
            "last_host_snapshot_id": host_snapshot_id,
        }

    def _resolve_existing_surface(
        self,
        *,
        project_id: str,
        requested_action: str,
    ) -> Dict[str, Any]:
        resolved_project_return = None
        resolved_host_bundle = None

        continuity = ContinuityRestoreStore(self._shared_surface_base_dir())
        try:
            resolved_project_return = continuity.project_return_payload(project_id)
        except Exception:
            resolved_project_return = None

        host = LuminaWorkspaceHost(self._shared_surface_base_dir())
        try:
            resolved_host_bundle = host.emit_host_bundle(project_id)
        except Exception:
            resolved_host_bundle = None

        return {
            "project_id": project_id,
            "resolved_project_return": resolved_project_return,
            "resolved_host_bundle": resolved_host_bundle,
            "working_stance": self._derive_working_stance(
                requested_action=requested_action,
                resolved_project_return=resolved_project_return,
                resolved_host_bundle=resolved_host_bundle,
            ),
        }

    def _maybe_run_lumina_return_host(
        self,
        *,
        target_mode: str,
        requested_action: str,
        raw_user_input: Optional[str],
        project_id: Optional[str],
        exposed_capabilities: list[Dict[str, Any]],
        artifacts_in_scope: list[str],
    ) -> Optional[Dict[str, Any]]:
        capability_ids = {cap.get("capability_id") for cap in exposed_capabilities}
        if "continuity_restore_store" not in capability_ids:
            return None

        resolved_project_id = self._resolve_lumina_project_id(project_id, requested_action, raw_user_input)
        base_dir = self._shared_surface_base_dir()

        continuity = ContinuityRestoreStore(base_dir)
        session = continuity.create_session(
            project_id=resolved_project_id,
            mode=target_mode,
            artifacts_in_scope=list(artifacts_in_scope),
            workspace_state={"active_mode": target_mode, "requested_action": requested_action},
            continuation_notes=[f"runtime cycle: {requested_action}"],
        )
        session.pending_next_action = f"continue from {requested_action}"
        session.last_completed_action = f"runtime_cycle:{requested_action}"
        continuity.save_session(session)

        checkpoint_one = continuity.write_checkpoint(session.session_id, f"{requested_action}_{target_mode}_checkpoint_only")
        payload_one = continuity.project_return_payload(resolved_project_id)

        artifacts: Dict[str, Any] = {
            "project_id": resolved_project_id,
            "base_dir": str(base_dir),
            "capability_ids": sorted(capability_ids & {"continuity_restore_store", "lumina_workspace_host"}),
            "checkpoint_only": {
                "checkpoint_path": str(checkpoint_one),
                "payload": payload_one,
            },
        }

        if "lumina_workspace_host" not in capability_ids:
            return artifacts

        host = LuminaWorkspaceHost(base_dir)
        host_session = host.create_host_session(
            project_id=resolved_project_id,
            mode=target_mode,
            active_layout_id="runtime-cycle-layout",
            focus_target=requested_action,
            artifacts_in_scope=list(artifacts_in_scope),
            linked_restore_checkpoint=str(checkpoint_one),
            continuation_notes=["workspace host remains bounded and checkpoint-linked"],
        )
        host.upsert_panel(
            host_session.host_session_id,
            panel_id="runtime-summary",
            panel_type="summary",
            title="Runtime Summary",
            zone="center",
            priority=10,
            payload={"requested_action": requested_action, "target_mode": target_mode},
        )
        host.bind_tool(
            host_session.host_session_id,
            tool_id="resolve-latest-project-return",
            label="Resolve Latest Project Return Payload",
            launch_target="project_return_repo_native_r1.py::project_return_payload",
            context_keys=["project_id"],
            pinned=True,
        )
        host.attach_reference(
            host_session.host_session_id,
            reference_id="bootstrap-readme",
            label="Bootstrap README",
            source="LuminaOS/bootstrap/Ship_of_Ethereon_V2/README.md",
            kind="runtime-reference",
        )
        host_snapshot = host.write_host_snapshot(
            host_session.host_session_id,
            last_completed_action=f"runtime_cycle:{requested_action}",
        )
        host_bundle = host.emit_host_bundle(resolved_project_id)

        checkpoint_two = continuity.write_checkpoint(session.session_id, f"{requested_action}_{target_mode}_checkpoint_plus_host")
        payload_two = continuity.project_return_payload(resolved_project_id)

        artifacts["checkpoint_plus_host"] = {
            "checkpoint_path": str(checkpoint_two),
            "payload": payload_two,
            "host_bundle": host_bundle,
            "host_snapshot_id": host_snapshot.snapshot_id,
        }
        return artifacts

    def _project_context_overrides(self, surface: Dict[str, Any]) -> Dict[str, Any]:
        working_stance = surface.get("working_stance") or {}
        return {
            "artifact_context": {
                "active_project_id": surface.get("project_id"),
                "working_stance_summary": dict(working_stance),
                "resolved_project_return": self._summarize_project_return(surface.get("resolved_project_return")),
                "resolved_host_bundle": self._summarize_host_bundle(surface.get("resolved_host_bundle")),
            },
            "memory_context": {
                "project_id": surface.get("project_id"),
                "working_stance_focus": working_stance.get("focus_target"),
                "session_continuation_notes": [self._working_stance_note(working_stance)],
            },
        }

    def _apply_working_stance_projection(
        self,
        *,
        result,
        requested_action: str,
        target_mode: str,
        fallback_surface: Dict[str, Any],
    ) -> None:
        project_id = fallback_surface.get("project_id")
        latest_payload = None
        latest_host_bundle = None
        latest_host_snapshot_id = None

        if result.lumina_return_host_artifacts:
            latest_payload = (
                result.lumina_return_host_artifacts.get("checkpoint_plus_host", {}).get("payload")
                or result.lumina_return_host_artifacts.get("checkpoint_only", {}).get("payload")
            )
            latest_host_bundle = result.lumina_return_host_artifacts.get("checkpoint_plus_host", {}).get("host_bundle")
            latest_host_snapshot_id = result.lumina_return_host_artifacts.get("checkpoint_plus_host", {}).get("host_snapshot_id")

        resolved_project_return = latest_payload or fallback_surface.get("resolved_project_return")
        resolved_host_bundle = latest_host_bundle or fallback_surface.get("resolved_host_bundle")
        working_stance = self._derive_working_stance(
            requested_action=requested_action,
            resolved_project_return=resolved_project_return,
            resolved_host_bundle=resolved_host_bundle,
            host_snapshot_id=latest_host_snapshot_id,
        )

        session_path = Path(result.session_path)
        if session_path.exists():
            with session_path.open("r", encoding="utf-8") as f:
                session_payload = json.load(f)
            session_payload["project_id"] = project_id
            session_payload["working_stance"] = working_stance
            with session_path.open("w", encoding="utf-8") as f:
                json.dump(session_payload, f, indent=2)

        bundle_path = self.context_builder.output_dir / f"{result.context_bundle_id}.json"
        if bundle_path.exists():
            with bundle_path.open("r", encoding="utf-8") as f:
                bundle_payload = json.load(f)
            bundle_payload.setdefault("artifact_context", {})
            bundle_payload.setdefault("memory_context", {})
            bundle_payload["artifact_context"]["active_project_id"] = project_id
            bundle_payload["artifact_context"]["working_stance_summary"] = working_stance
            bundle_payload["artifact_context"]["resolved_project_return"] = self._summarize_project_return(resolved_project_return)
            bundle_payload["artifact_context"]["resolved_host_bundle"] = self._summarize_host_bundle(resolved_host_bundle)
            bundle_payload["memory_context"]["project_id"] = project_id
            bundle_payload["memory_context"]["working_stance_focus"] = working_stance.get("focus_target")
            notes = list(bundle_payload["memory_context"].get("session_continuation_notes", []))
            stance_note = self._working_stance_note(working_stance)
            if stance_note not in notes:
                notes.append(stance_note)
            bundle_payload["memory_context"]["session_continuation_notes"] = notes
            with bundle_path.open("w", encoding="utf-8") as f:
                json.dump(bundle_payload, f, indent=2)

        self._append_governance_event(
            event_type="working_stance_projection",
            session_id=result.session_id,
            previous_mode=target_mode,
            new_mode=target_mode,
            allowed=True,
            reason="project stance projected through return-host bridge",
            requested_action=requested_action,
            action_type=result.action_type,
            metadata={
                "project_id": project_id,
                "focus_target": working_stance.get("focus_target"),
                "has_resolved_project_return": bool(resolved_project_return),
                "has_resolved_host_bundle": bool(resolved_host_bundle),
            },
        )
        result.governance_chain_status = self._current_chain_status()
        log_path = Path(result.log_path)
        if log_path.exists():
            with log_path.open("w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2)

    def _emit_working_stance_voice(self, *, result, target_mode: str, requested_action: str) -> None:
        if LuminaWorkingStanceVoice is None:
            return

        session_path = Path(result.session_path)
        if not session_path.exists():
            return

        bundle_path = self.context_builder.output_dir / f"{result.context_bundle_id}.json"
        voice = LuminaWorkingStanceVoice()
        report = voice.report(
            session_path=session_path,
            context_bundle_path=bundle_path if bundle_path.exists() else None,
        )

        report_path = self._voice_reports_dir() / f"{result.run_id}_working_stance_voice.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)

        result.governance["working_stance_voice"] = {
            "allowed": True,
            "report_path": str(report_path),
            "project_id": report.project_id,
            "focus_target": report.focus_target,
            "machine_brief": report.machine_brief,
            "human_brief": report.human_brief,
            "utterance": report.utterance,
            "boundary_note": report.boundary_note,
        }

        self._append_governance_event(
            event_type="working_stance_voice",
            session_id=result.session_id,
            previous_mode=target_mode,
            new_mode=target_mode,
            allowed=True,
            reason="emitted descriptive working stance voice",
            requested_action=requested_action,
            action_type=result.action_type,
            metadata={
                "project_id": report.project_id,
                "focus_target": report.focus_target,
                "report_path": str(report_path),
            },
        )
        result.governance_chain_status = self._current_chain_status()
        log_path = Path(result.log_path)
        if log_path.exists():
            with log_path.open("w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2)

    def run_cycle(self, *, project_id: Optional[str] = None, context_bundle_overrides: Optional[Dict[str, Any]] = None, target_mode: Optional[str] = None, requested_action: str = "sea_trial_cycle", raw_user_input: Optional[str] = None, **kwargs: Any):
        target_mode = target_mode or kwargs.get("current_mode", "Continuity")
        resolved_project_id = self._resolve_lumina_project_id(project_id, requested_action, raw_user_input)
        existing_surface = self._resolve_existing_surface(
            project_id=resolved_project_id,
            requested_action=requested_action,
        )
        merged_overrides = self._deep_merge(
            context_bundle_overrides,
            self._project_context_overrides(existing_surface),
        )
        result = super().run_cycle(
            target_mode=target_mode,
            requested_action=requested_action,
            raw_user_input=raw_user_input,
            project_id=resolved_project_id,
            context_bundle_overrides=merged_overrides,
            **kwargs,
        )
        self._apply_working_stance_projection(
            result=result,
            requested_action=requested_action,
            target_mode=target_mode,
            fallback_surface=existing_surface,
        )
        self._emit_working_stance_voice(
            result=result,
            target_mode=target_mode,
            requested_action=requested_action,
        )
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one tiny Ethereon runtime cycle with repo-native return/host bridging.")
    parser.add_argument("--current-mode", default="Continuity")
    parser.add_argument("--target-mode", default=None)
    parser.add_argument("--action", default="sea_trial_cycle")
    parser.add_argument("--action-type", default="transition", choices=sorted(runner_mod.VALID_ACTION_TYPES))
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


def _maybe_json(text):
    if not text:
        return None
    return json.loads(text)


if __name__ == "__main__":
    args = parse_args()
    runner = ReturnHostBridgedRuntimeRunner()
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
