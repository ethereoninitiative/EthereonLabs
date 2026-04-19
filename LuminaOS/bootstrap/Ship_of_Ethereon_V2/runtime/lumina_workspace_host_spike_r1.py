from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PanelState:
    panel_id: str
    panel_type: str
    title: str
    zone: str
    visible: bool = True
    priority: int = 50
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ToolBinding:
    tool_id: str
    label: str
    launch_target: str
    context_keys: List[str] = field(default_factory=list)
    pinned: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReferenceSurface:
    reference_id: str
    label: str
    source: str
    kind: str = "reference"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LuminaHostSession:
    host_session_id: str
    started_at: str
    project_id: str
    current_mode: str = "Continuity"
    active_layout_id: str = "default-workspace"
    panels: List[PanelState] = field(default_factory=list)
    tool_bindings: List[ToolBinding] = field(default_factory=list)
    references: List[ReferenceSurface] = field(default_factory=list)
    focus_target: Optional[str] = None
    continuation_notes: List[str] = field(default_factory=list)
    artifacts_in_scope: List[str] = field(default_factory=list)
    linked_restore_checkpoint: Optional[str] = None
    last_snapshot: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "panels": [panel.to_dict() for panel in self.panels],
            "tool_bindings": [tool.to_dict() for tool in self.tool_bindings],
            "references": [reference.to_dict() for reference in self.references],
        }


@dataclass
class HostSnapshot:
    snapshot_id: str
    project_id: str
    host_session_id: str
    captured_at: str
    current_mode: str
    active_layout_id: str
    panels: List[Dict[str, Any]] = field(default_factory=list)
    tool_bindings: List[Dict[str, Any]] = field(default_factory=list)
    references: List[Dict[str, Any]] = field(default_factory=list)
    focus_target: Optional[str] = None
    continuation_notes: List[str] = field(default_factory=list)
    artifacts_in_scope: List[str] = field(default_factory=list)
    linked_restore_checkpoint: Optional[str] = None
    last_completed_action: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaWorkspaceHost:
    """Minimal host-environment proof for Lumina built around explicit project workspaces."""

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / "host_sessions"
        self.snapshot_history_dir = self.base_dir / "host_snapshots" / "history"
        self.snapshot_latest_dir = self.base_dir / "host_snapshots" / "latest"
        self.bundle_dir = self.base_dir / "host_bundles"

        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_history_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_latest_dir.mkdir(parents=True, exist_ok=True)
        self.bundle_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_slug(value: str) -> str:
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in value.strip())
        return slug or "default-project"

    def session_path(self, host_session_id: str) -> Path:
        return self.session_dir / f"{host_session_id}.json"

    def latest_snapshot_path(self, project_id: str) -> Path:
        return self.snapshot_latest_dir / f"{self._safe_slug(project_id)}.json"

    def snapshot_history_path(self, project_id: str, snapshot_id: str) -> Path:
        return self.snapshot_history_dir / f"{self._safe_slug(project_id)}__{snapshot_id}.json"

    def bundle_path(self, project_id: str) -> Path:
        return self.bundle_dir / f"{self._safe_slug(project_id)}.json"

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
    ) -> LuminaHostSession:
        session = LuminaHostSession(
            host_session_id=str(uuid.uuid4()),
            started_at=utc_now(),
            project_id=project_id.strip() or "default-project",
            current_mode=mode,
            active_layout_id=active_layout_id,
            focus_target=focus_target,
            artifacts_in_scope=list(artifacts_in_scope or []),
            linked_restore_checkpoint=linked_restore_checkpoint,
            continuation_notes=list(continuation_notes or []),
        )
        self._save_session(session)
        return session

    def load_host_session(self, host_session_id: str) -> LuminaHostSession:
        with self.session_path(host_session_id).open("r", encoding="utf-8") as f:
            payload = json.load(f)
        payload["panels"] = [PanelState(**row) for row in payload.get("panels", [])]
        payload["tool_bindings"] = [ToolBinding(**row) for row in payload.get("tool_bindings", [])]
        payload["references"] = [ReferenceSurface(**row) for row in payload.get("references", [])]
        return LuminaHostSession(**payload)

    def set_active_layout(self, host_session_id: str, active_layout_id: str) -> LuminaHostSession:
        session = self.load_host_session(host_session_id)
        session.active_layout_id = active_layout_id
        self._save_session(session)
        return session

    def set_focus_target(self, host_session_id: str, focus_target: Optional[str]) -> LuminaHostSession:
        session = self.load_host_session(host_session_id)
        session.focus_target = focus_target
        self._save_session(session)
        return session

    def add_continuation_note(self, host_session_id: str, note: str) -> LuminaHostSession:
        session = self.load_host_session(host_session_id)
        if note:
            session.continuation_notes.append(note)
        self._save_session(session)
        return session

    def link_restore_checkpoint(self, host_session_id: str, checkpoint_path: str) -> LuminaHostSession:
        session = self.load_host_session(host_session_id)
        session.linked_restore_checkpoint = checkpoint_path
        self._save_session(session)
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
    ) -> LuminaHostSession:
        session = self.load_host_session(host_session_id)
        next_panel = PanelState(
            panel_id=panel_id,
            panel_type=panel_type,
            title=title,
            zone=zone,
            visible=visible,
            priority=priority,
            payload=dict(payload or {}),
        )

        replaced = False
        for index, panel in enumerate(session.panels):
            if panel.panel_id == panel_id:
                session.panels[index] = next_panel
                replaced = True
                break
        if not replaced:
            session.panels.append(next_panel)

        session.panels.sort(key=lambda item: (item.zone, item.priority, item.panel_id))
        self._save_session(session)
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
    ) -> LuminaHostSession:
        session = self.load_host_session(host_session_id)
        next_tool = ToolBinding(
            tool_id=tool_id,
            label=label,
            launch_target=launch_target,
            context_keys=list(context_keys or []),
            pinned=pinned,
        )

        replaced = False
        for index, tool in enumerate(session.tool_bindings):
            if tool.tool_id == tool_id:
                session.tool_bindings[index] = next_tool
                replaced = True
                break
        if not replaced:
            session.tool_bindings.append(next_tool)

        session.tool_bindings.sort(key=lambda item: (not item.pinned, item.label.casefold()))
        self._save_session(session)
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
    ) -> LuminaHostSession:
        session = self.load_host_session(host_session_id)
        next_reference = ReferenceSurface(
            reference_id=reference_id,
            label=label,
            source=source,
            kind=kind,
            metadata=dict(metadata or {}),
        )

        replaced = False
        for index, reference in enumerate(session.references):
            if reference.reference_id == reference_id:
                session.references[index] = next_reference
                replaced = True
                break
        if not replaced:
            session.references.append(next_reference)

        session.references.sort(key=lambda item: (item.kind, item.label.casefold()))
        self._save_session(session)
        return session

    def write_host_snapshot(
        self,
        host_session_id: str,
        *,
        last_completed_action: Optional[str] = None,
    ) -> HostSnapshot:
        session = self.load_host_session(host_session_id)
        snapshot = HostSnapshot(
            snapshot_id=str(uuid.uuid4()),
            project_id=session.project_id,
            host_session_id=session.host_session_id,
            captured_at=utc_now(),
            current_mode=session.current_mode,
            active_layout_id=session.active_layout_id,
            panels=[panel.to_dict() for panel in session.panels],
            tool_bindings=[tool.to_dict() for tool in session.tool_bindings],
            references=[reference.to_dict() for reference in session.references],
            focus_target=session.focus_target,
            continuation_notes=list(session.continuation_notes),
            artifacts_in_scope=list(session.artifacts_in_scope),
            linked_restore_checkpoint=session.linked_restore_checkpoint,
            last_completed_action=last_completed_action,
        )

        history_path = self.snapshot_history_path(session.project_id, snapshot.snapshot_id)
        latest_path = self.latest_snapshot_path(session.project_id)

        with history_path.open("w", encoding="utf-8") as f:
            json.dump(snapshot.to_dict(), f, indent=2)
        with latest_path.open("w", encoding="utf-8") as f:
            json.dump(snapshot.to_dict(), f, indent=2)

        session.last_snapshot = str(latest_path)
        self._save_session(session)
        self.emit_host_bundle(session.project_id)
        return snapshot

    def resolve_latest_snapshot(self, project_id: str) -> Optional[HostSnapshot]:
        path = self.latest_snapshot_path(project_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            return HostSnapshot(**json.load(f))

    def emit_host_bundle(self, project_id: str) -> Dict[str, Any]:
        snapshot = self.resolve_latest_snapshot(project_id)
        if snapshot is None:
            raise FileNotFoundError(f"No host snapshot found for project_id={project_id}")

        bundle = {
            "bundle_type": "lumina_host_workspace_r1",
            "project_id": snapshot.project_id,
            "captured_at": snapshot.captured_at,
            "current_mode": snapshot.current_mode,
            "active_layout_id": snapshot.active_layout_id,
            "focus_target": snapshot.focus_target,
            "panels": snapshot.panels,
            "tool_bindings": snapshot.tool_bindings,
            "references": snapshot.references,
            "continuation_notes": snapshot.continuation_notes,
            "artifacts_in_scope": snapshot.artifacts_in_scope,
            "linked_restore_checkpoint": snapshot.linked_restore_checkpoint,
            "last_completed_action": snapshot.last_completed_action,
        }

        with self.bundle_path(project_id).open("w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)

        return bundle

    def resume_project_host(self, project_id: str) -> Dict[str, Any]:
        snapshot = self.resolve_latest_snapshot(project_id)
        if snapshot is None:
            raise FileNotFoundError(f"No host snapshot found for project_id={project_id}")
        return self.emit_host_bundle(project_id)

    def _save_session(self, session: LuminaHostSession) -> None:
        with self.session_path(session.host_session_id).open("w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2)


if __name__ == "__main__":
    host = LuminaWorkspaceHost("./lumina_workspace_demo")

    session = host.create_host_session(
        project_id="lumina-core",
        mode="Continuity",
        active_layout_id="studio-focus",
        focus_target="continuity-return-lane",
        artifacts_in_scope=["continuity_restore_spike_r1.py", "lumina.html"],
        continuation_notes=["make Lumina host behavior tangible in-repo"],
    )

    host.upsert_panel(
        session.host_session_id,
        panel_id="notes",
        panel_type="text",
        title="Project Notes",
        zone="left",
        priority=10,
        payload={"open_document": "continuation_notes.md"},
    )
    host.upsert_panel(
        session.host_session_id,
        panel_id="references",
        panel_type="reference-rail",
        title="Reference Surfaces",
        zone="right",
        priority=20,
        payload={"count": 2},
    )
    host.bind_tool(
        session.host_session_id,
        tool_id="restore-latest",
        label="Restore Latest Project State",
        launch_target="continuity_restore_spike_r1.py::resume_project",
        context_keys=["project_id"],
        pinned=True,
    )
    host.attach_reference(
        session.host_session_id,
        reference_id="lumina-page",
        label="Lumina public page",
        source="lumina.html",
        kind="site-artifact",
    )
    snapshot = host.write_host_snapshot(
        session.host_session_id,
        last_completed_action="write_host_snapshot",
    )
    print(json.dumps(snapshot.to_dict(), indent=2))
