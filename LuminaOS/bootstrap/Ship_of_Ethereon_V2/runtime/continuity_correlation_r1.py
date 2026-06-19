from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid

SCHEMA_VERSION = "lumina-continuity-correlation-r1"


def read_marker(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


@dataclass(frozen=True)
class ContinuityCorrelation:
    schema_version: str
    correlation_id: str
    project_slug: Optional[str]
    harbor_session_id: Optional[str]
    runtime_session_id: Optional[str]
    restore_session_id: Optional[str]
    host_session_id: Optional[str]
    authority_boundary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def active_workspace(state_root: Path) -> Dict[str, Optional[str]]:
    project = read_marker(state_root / "active_project.json")
    session = read_marker(state_root / "active_session.json")
    project_slug = project.get("active_project_slug")
    session_project = session.get("project_slug")
    if project_slug and session_project and project_slug != session_project:
        raise ValueError("active project and session markers disagree")
    return {
        "project_slug": str(project_slug or session_project) if (project_slug or session_project) else None,
        "harbor_session_id": str(session.get("active_session_id")) if session.get("active_session_id") else None,
    }


def create_correlation(
    *,
    state_root: Optional[Path] = None,
    project_slug: Optional[str] = None,
    harbor_session_id: Optional[str] = None,
    runtime_session_id: Optional[str] = None,
    restore_session_id: Optional[str] = None,
    host_session_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> ContinuityCorrelation:
    if state_root is not None:
        active = active_workspace(state_root)
        project_slug = project_slug or active["project_slug"]
        harbor_session_id = harbor_session_id or active["harbor_session_id"]
    if not any([harbor_session_id, runtime_session_id, restore_session_id, host_session_id]):
        raise ValueError("at least one session reference is required")
    return ContinuityCorrelation(
        schema_version=SCHEMA_VERSION,
        correlation_id=correlation_id or f"lumina-{uuid.uuid4().hex}",
        project_slug=project_slug,
        harbor_session_id=harbor_session_id,
        runtime_session_id=runtime_session_id,
        restore_session_id=restore_session_id,
        host_session_id=host_session_id,
        authority_boundary="Correlation does not transfer governance, canon, checkpoint, or capability authority.",
    )
