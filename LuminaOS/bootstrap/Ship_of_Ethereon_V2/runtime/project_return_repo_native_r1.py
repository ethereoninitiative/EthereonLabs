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

MODULE_SLUG = "project_return_repo_native_r1"
HOST_MODULE_SLUG = "workspace_host_repo_native_r1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        return Path(_state_root_helper()).resolve()
    return Path(__file__).resolve().parent / "_runtime_state" / "ship_of_ethereon_v2"


BASE_DIR = infer_state_root() / MODULE_SLUG


@dataclass
class SessionState:
    session_id: str
    started_at: str
    project_id: str
    current_mode: str = "Continuity"
    artifacts_in_scope: list[str] = field(default_factory=list)
    workspace_state: dict = field(default_factory=dict)
    continuation_notes: list[str] = field(default_factory=list)
    pending_next_action: str | None = None
    last_completed_action: str | None = None
    last_checkpoint: str | None = None
    linked_host_bundle: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


class ProjectReturnStore:
    """Repo-native proof that Lumina can resume a project without guessing."""

    def __init__(self, base_dir: str | Path = BASE_DIR):
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / "sessions"
        self.checkpoint_dir = self.base_dir / "checkpoints"
        self.restore_latest_dir = self.base_dir / "project_restores" / "latest"
        self.host_bundle_dir = infer_state_root() / HOST_MODULE_SLUG / "host_bundles"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.restore_latest_dir.mkdir(parents=True, exist_ok=True)
        self.host_bundle_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_slug(value: str) -> str:
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in value.strip())
        return slug or "default-project"

    def _session_path(self, session_id: str) -> Path:
        return self.session_dir / f"{session_id}.json"

    def _checkpoint_path(self, session_id: str, label: str) -> Path:
        return self.checkpoint_dir / f"{session_id}__{self._safe_slug(label)}.json"

    def _latest_restore_path(self, project_id: str) -> Path:
        return self.restore_latest_dir / f"{self._safe_slug(project_id)}.json"

    def _host_bundle_path(self, project_id: str) -> Path:
        return self.host_bundle_dir / f"{self._safe_slug(project_id)}.json"

    def create_session(self, project_id: str, mode: str = "Continuity", artifacts_in_scope=None) -> SessionState:
        state = SessionState(
            session_id=str(uuid.uuid4()),
            started_at=utc_now(),
            project_id=project_id.strip() or "default-project",
            current_mode=mode,
            artifacts_in_scope=list(artifacts_in_scope or []),
            linked_host_bundle=str(self._host_bundle_path(project_id)) if self._host_bundle_path(project_id).exists() else None,
        )
        self.save_session(state)
        return state

    def save_session(self, state: SessionState) -> None:
        state.linked_host_bundle = str(self._host_bundle_path(state.project_id)) if self._host_bundle_path(state.project_id).exists() else None
        with self._session_path(state.session_id).open("w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2)

    def load_session(self, session_id: str) -> SessionState:
        with self._session_path(session_id).open("r", encoding="utf-8") as f:
            return SessionState(**json.load(f))

    def write_checkpoint(self, session_id: str, label: str) -> Path:
        state = self.load_session(session_id)
        path = self._checkpoint_path(session_id, label)
        with path.open("w", encoding="utf-8") as f:
            json.dump({"checkpoint_label": label, "created_at": utc_now(), "session_state": state.to_dict()}, f, indent=2)
        state.last_checkpoint = str(path)
        self.save_session(state)
        with self._latest_restore_path(state.project_id).open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "project_id": state.project_id,
                    "session_id": state.session_id,
                    "checkpoint_path": str(path),
                    "captured_at": utc_now(),
                    "current_mode": state.current_mode,
                    "artifacts_in_scope": state.artifacts_in_scope,
                    "workspace_state": state.workspace_state,
                    "continuation_notes": state.continuation_notes,
                    "pending_next_action": state.pending_next_action,
                    "last_completed_action": state.last_completed_action,
                    "linked_host_bundle": state.linked_host_bundle,
                },
                f,
                indent=2,
            )
        return path

    def project_return_payload(self, project_id: str) -> dict:
        latest_path = self._latest_restore_path(project_id)
        if not latest_path.exists():
            raise FileNotFoundError(project_id)
        with latest_path.open("r", encoding="utf-8") as f:
            latest_restore = json.load(f)
        host_bundle = None
        if self._host_bundle_path(project_id).exists():
            with self._host_bundle_path(project_id).open("r", encoding="utf-8") as f:
                host_bundle = json.load(f)
        return {
            "project_id": project_id,
            "return_strategy": "checkpoint_plus_host" if host_bundle else "checkpoint_only",
            "latest_restore": latest_restore,
            "host_bundle": host_bundle,
        }
