from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

try:
    from .repo_paths_r1 import state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import state_root as _state_root_helper
    except Exception:
        _state_root_helper = None

MODULE_SLUG = "workspace_host_repo_native_r1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        return Path(_state_root_helper()).resolve()
    return Path(__file__).resolve().parent / "_runtime_state" / "ship_of_ethereon_v2"


BASE_DIR = infer_state_root() / MODULE_SLUG


@dataclass
class HostSession:
    host_session_id: str
    started_at: str
    project_id: str
    current_mode: str = "Continuity"
    active_layout_id: str = "default-workspace"
    focus_target: str | None = None
    panels: list[dict] = field(default_factory=list)
    tool_bindings: list[dict] = field(default_factory=list)
    references: list[dict] = field(default_factory=list)
    continuation_notes: list[str] = field(default_factory=list)
    artifacts_in_scope: list[str] = field(default_factory=list)
    linked_restore_checkpoint: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class WorkspaceHostStore:
    """Repo-native proof that Lumina can restore a bounded working surface."""

    def __init__(self, base_dir: str | Path = BASE_DIR):
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / "host_sessions"
        self.snapshot_latest_dir = self.base_dir / "host_snapshots" / "latest"
        self.bundle_dir = self.base_dir / "host_bundles"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_latest_dir.mkdir(parents=True, exist_ok=True)
        self.bundle_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_slug(value: str) -> str:
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in value.strip())
        return slug or "default-project"

    def _session_path(self, host_session_id: str) -> Path:
        return self.session_dir / f"{host_session_id}.json"

    def _latest_snapshot_path(self, project_id: str) -> Path:
        return self.snapshot_latest_dir / f"{self._safe_slug(project_id)}.json"

    def _bundle_path(self, project_id: str) -> Path:
        return self.bundle_dir / f"{self._safe_slug(project_id)}.json"

    def create_session(self, project_id: str, mode: str = "Continuity", active_layout_id: str = "default-workspace") -> HostSession:
        session = HostSession(
            host_session_id=str(uuid.uuid4()),
            started_at=utc_now(),
            project_id=project_id.strip() or "default-project",
            current_mode=mode,
            active_layout_id=active_layout_id,
        )
        self.save_session(session)
        return session

    def save_session(self, session: HostSession) -> None:
        with self._session_path(session.host_session_id).open("w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2)

    def load_session(self, host_session_id: str) -> HostSession:
        with self._session_path(host_session_id).open("r", encoding="utf-8") as f:
            return HostSession(**json.load(f))

    def set_surface(self, host_session_id: str, *, focus_target=None, panels=None, tool_bindings=None, references=None, continuation_notes=None, linked_restore_checkpoint=None) -> HostSession:
        session = self.load_session(host_session_id)
        if focus_target is not None:
            session.focus_target = focus_target
        if panels is not None:
            session.panels = list(panels)
        if tool_bindings is not None:
            session.tool_bindings = list(tool_bindings)
        if references is not None:
            session.references = list(references)
        if continuation_notes is not None:
            session.continuation_notes = list(continuation_notes)
        if linked_restore_checkpoint is not None:
            session.linked_restore_checkpoint = linked_restore_checkpoint
        self.save_session(session)
        return session

    def write_snapshot(self, host_session_id: str) -> dict:
        session = self.load_session(host_session_id)
        snapshot = {
            "project_id": session.project_id,
            "host_session_id": session.host_session_id,
            "captured_at": utc_now(),
            "current_mode": session.current_mode,
            "active_layout_id": session.active_layout_id,
            "focus_target": session.focus_target,
            "panels": session.panels,
            "tool_bindings": session.tool_bindings,
            "references": session.references,
            "continuation_notes": session.continuation_notes,
            "artifacts_in_scope": session.artifacts_in_scope,
            "linked_restore_checkpoint": session.linked_restore_checkpoint,
        }
        with self._latest_snapshot_path(session.project_id).open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
        bundle = {"bundle_type": "lumina_host_workspace_r1", **snapshot}
        with self._bundle_path(session.project_id).open("w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)
        return bundle
