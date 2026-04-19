from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .project_return_repo_native_r1 import ProjectReturnStore
    from .workspace_host_repo_native_r1 import WorkspaceHostStore
except Exception:
    from project_return_repo_native_r1 import ProjectReturnStore
    from workspace_host_repo_native_r1 import WorkspaceHostStore


@dataclass
class HostSnapshot:
    snapshot_id: str


class ContinuityRestoreStore:
    """Compatibility bridge that presents the older spike-facing API over the repo-native project return store."""

    def __init__(self, base_dir: str | Path):
        self._store = ProjectReturnStore(base_dir)

    def create_session(
        self,
        *,
        project_id: str,
        mode: str = "Continuity",
        artifacts_in_scope: Optional[List[str]] = None,
        workspace_state: Optional[Dict[str, Any]] = None,
        continuation_notes: Optional[List[str]] = None,
    ):
        session = self._store.create_session(project_id=project_id, mode=mode, artifacts_in_scope=artifacts_in_scope)
        if workspace_state is not None:
            session.workspace_state = dict(workspace_state)
        if continuation_notes is not None:
            session.continuation_notes = list(continuation_notes)
        self._store.save_session(session)
        return session

    def save_session(self, session) -> None:
        self._store.save_session(session)

    def write_checkpoint(self, session_id: str, label: str):
        return self._store.write_checkpoint(session_id, label)

    def project_return_payload(self, project_id: str) -> dict:
        return self._store.project_return_payload(project_id)


class LuminaWorkspaceHost:
    """Compatibility bridge that presents the older spike-facing host API over the repo-native workspace host store."""

    def __init__(self, base_dir: str | Path):
        self._store = WorkspaceHostStore(base_dir)

    def create_host_session(
        self,
        *,
        project_id: str,
        mode: str = "Continuity",
        active_layout_id: str = "default-workspace",
        focus_target: Optional[str] = None,
        artifacts_in_scope: Optional[List[str]] = None,
        linked_restore_checkpoint: Optional[str] = None,
        continuation_notes: Optional[List[str]] = None,
    ):
        session = self._store.create_session(project_id=project_id, mode=mode, active_layout_id=active_layout_id)
        session.focus_target = focus_target
        session.artifacts_in_scope = list(artifacts_in_scope or [])
        session.linked_restore_checkpoint = linked_restore_checkpoint
        session.continuation_notes = list(continuation_notes or [])
        self._store.save_session(session)
        return session

    def upsert_panel(
        self,
        host_session_id: str,
        *,
        panel_id: str,
        panel_type: str,
        title: str,
        zone: str,
        visible: bool = True,
        priority: int = 50,
        payload: Optional[Dict[str, Any]] = None,
    ):
        session = self._store.load_session(host_session_id)
        panels = [row for row in session.panels if row.get("panel_id") != panel_id]
        panels.append(
            {
                "panel_id": panel_id,
                "panel_type": panel_type,
                "title": title,
                "zone": zone,
                "visible": visible,
                "priority": priority,
                "payload": dict(payload or {}),
            }
        )
        session.panels = sorted(panels, key=lambda item: (item.get("zone", ""), item.get("priority", 50), item.get("panel_id", "")))
        self._store.save_session(session)
        return session

    def bind_tool(
        self,
        host_session_id: str,
        *,
        tool_id: str,
        label: str,
        launch_target: str,
        context_keys: Optional[List[str]] = None,
        pinned: bool = False,
    ):
        session = self._store.load_session(host_session_id)
        tools = [row for row in session.tool_bindings if row.get("tool_id") != tool_id]
        tools.append(
            {
                "tool_id": tool_id,
                "label": label,
                "launch_target": launch_target,
                "context_keys": list(context_keys or []),
                "pinned": pinned,
            }
        )
        session.tool_bindings = sorted(tools, key=lambda item: (not item.get("pinned", False), item.get("label", "").casefold()))
        self._store.save_session(session)
        return session

    def attach_reference(
        self,
        host_session_id: str,
        *,
        reference_id: str,
        label: str,
        source: str,
        kind: str = "reference",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        session = self._store.load_session(host_session_id)
        refs = [row for row in session.references if row.get("reference_id") != reference_id]
        refs.append(
            {
                "reference_id": reference_id,
                "label": label,
                "source": source,
                "kind": kind,
                "metadata": dict(metadata or {}),
            }
        )
        session.references = sorted(refs, key=lambda item: (item.get("kind", ""), item.get("label", "").casefold()))
        self._store.save_session(session)
        return session

    def write_host_snapshot(self, host_session_id: str, *, last_completed_action: Optional[str] = None):
        bundle = self._store.write_snapshot(host_session_id)
        return HostSnapshot(snapshot_id=f"host-{bundle['host_session_id']}")

    def emit_host_bundle(self, project_id: str) -> dict:
        path = self._store._bundle_path(project_id)
        with path.open("r", encoding="utf-8") as f:
            return __import__("json").load(f)
