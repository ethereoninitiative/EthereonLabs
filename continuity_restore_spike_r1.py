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
class ContinuityState:
    checkpoint_count: int = 0
    resume_count: int = 0


@dataclass
class SessionState:
    session_id: str
    started_at: str
    project_id: str
    current_mode: str = "Continuity"
    artifacts_in_scope: List[str] = field(default_factory=list)
    pending_next_action: Optional[str] = None
    last_completed_action: Optional[str] = None
    workspace_state: Dict[str, Any] = field(default_factory=dict)
    continuation_notes: List[str] = field(default_factory=list)
    continuity_state: ContinuityState = field(default_factory=ContinuityState)
    last_checkpoint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectRestorePoint:
    restore_id: str
    project_id: str
    session_id: str
    checkpoint_path: str
    captured_at: str
    current_mode: str
    artifacts_in_scope: List[str] = field(default_factory=list)
    pending_next_action: Optional[str] = None
    last_completed_action: Optional[str] = None
    workspace_state: Dict[str, Any] = field(default_factory=dict)
    continuation_notes: List[str] = field(default_factory=list)
    last_checkpoint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ContinuityRestoreStore:
    """Minimal project-scoped continuity restore built on explicit checkpoints."""

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / "sessions"
        self.checkpoint_dir = self.base_dir / "checkpoints"
        self.restore_history_dir = self.base_dir / "project_restores" / "history"
        self.restore_latest_dir = self.base_dir / "project_restores" / "latest"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.restore_history_dir.mkdir(parents=True, exist_ok=True)
        self.restore_latest_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_slug(value: str) -> str:
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in value.strip())
        return slug or "default-project"

    def session_path(self, session_id: str) -> Path:
        return self.session_dir / f"{session_id}.json"

    def checkpoint_path(self, session_id: str, label: str) -> Path:
        safe_label = self._safe_slug(label)
        return self.checkpoint_dir / f"{session_id}__{safe_label}.json"

    def latest_restore_path(self, project_id: str) -> Path:
        return self.restore_latest_dir / f"{self._safe_slug(project_id)}.json"

    def restore_history_path(self, project_id: str, restore_id: str) -> Path:
        return self.restore_history_dir / f"{self._safe_slug(project_id)}__{restore_id}.json"

    def create_session(
        self,
        *,
        project_id: str,
        mode: str = "Continuity",
        artifacts_in_scope: Optional[List[str]] = None,
        workspace_state: Optional[Dict[str, Any]] = None,
        continuation_notes: Optional[List[str]] = None,
    ) -> SessionState:
        state = SessionState(
            session_id=str(uuid.uuid4()),
            started_at=utc_now(),
            project_id=project_id.strip() or "default-project",
            current_mode=mode,
            artifacts_in_scope=list(artifacts_in_scope or []),
            workspace_state=dict(workspace_state or {}),
            continuation_notes=list(continuation_notes or []),
        )
        self.save_session(state)
        return state

    def save_session(self, state: SessionState) -> None:
        with self.session_path(state.session_id).open("w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)

    def load_session(self, session_id: str) -> SessionState:
        with self.session_path(session_id).open("r", encoding="utf-8") as f:
            payload = json.load(f)
        payload["continuity_state"] = ContinuityState(**payload.get("continuity_state", {}))
        payload.setdefault("workspace_state", {})
        payload.setdefault("continuation_notes", [])
        return SessionState(**payload)

    def update_workspace_state(self, session_id: str, workspace_state: Dict[str, Any]) -> SessionState:
        state = self.load_session(session_id)
        state.workspace_state.update(dict(workspace_state or {}))
        self.save_session(state)
        return state

    def add_continuation_note(self, session_id: str, note: str) -> SessionState:
        state = self.load_session(session_id)
        if note:
            state.continuation_notes.append(note)
        self.save_session(state)
        return state

    def write_checkpoint(self, session_id: str, label: str) -> Path:
        state = self.load_session(session_id)
        path = self.checkpoint_path(session_id, label)
        payload = {
            "checkpoint_label": label,
            "created_at": utc_now(),
            "session_state": state.to_dict(),
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        state.last_checkpoint = str(path)
        state.continuity_state.checkpoint_count += 1
        self.save_session(state)
        self.capture_restore(session_id=session_id, checkpoint_path=path)
        return path

    def capture_restore(self, *, session_id: str, checkpoint_path: str | Path) -> ProjectRestorePoint:
        state = self.load_session(session_id)
        restore = ProjectRestorePoint(
            restore_id=str(uuid.uuid4()),
            project_id=state.project_id,
            session_id=state.session_id,
            checkpoint_path=str(checkpoint_path),
            captured_at=utc_now(),
            current_mode=state.current_mode,
            artifacts_in_scope=list(state.artifacts_in_scope),
            pending_next_action=state.pending_next_action,
            last_completed_action=state.last_completed_action,
            workspace_state=dict(state.workspace_state),
            continuation_notes=list(state.continuation_notes),
            last_checkpoint=state.last_checkpoint,
        )
        history_path = self.restore_history_path(state.project_id, restore.restore_id)
        latest_path = self.latest_restore_path(state.project_id)
        with history_path.open("w", encoding="utf-8") as f:
            json.dump(restore.to_dict(), f, indent=2)
        with latest_path.open("w", encoding="utf-8") as f:
            json.dump(restore.to_dict(), f, indent=2)
        return restore

    def resolve_latest_restore(self, project_id: str) -> Optional[ProjectRestorePoint]:
        path = self.latest_restore_path(project_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            return ProjectRestorePoint(**json.load(f))

    def resume_from_checkpoint(self, checkpoint_path: str | Path) -> SessionState:
        with Path(checkpoint_path).open("r", encoding="utf-8") as f:
            payload = json.load(f)
        state = self.load_session(payload["session_state"]["session_id"])
        state.continuity_state.resume_count += 1
        self.save_session(state)
        return state

    def resume_project(self, project_id: str) -> SessionState:
        restore = self.resolve_latest_restore(project_id)
        if restore is None:
            raise FileNotFoundError(f"No restore point found for project_id={project_id}")
        return self.resume_from_checkpoint(restore.checkpoint_path)


if __name__ == "__main__":
    store = ContinuityRestoreStore("./continuity_restore_demo")
    session = store.create_session(
        project_id="lumina-core",
        artifacts_in_scope=["runtime_spine_r1.py", "continuity.html"],
        workspace_state={"open_panels": ["notes", "references"]},
        continuation_notes=["continue continuity restore work"],
    )
    session.pending_next_action = "compare restore payload fields"
    session.last_completed_action = "tool:context_bundle"
    store.save_session(session)
    store.write_checkpoint(session.session_id, "continuity_restore_smoke_test")
    latest = store.resolve_latest_restore("lumina-core")
    print(json.dumps(latest.to_dict() if latest else {}, indent=2))
