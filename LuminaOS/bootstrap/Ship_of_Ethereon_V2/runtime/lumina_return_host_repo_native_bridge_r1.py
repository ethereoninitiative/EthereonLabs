from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

try:
    from .project_return_repo_native_r1 import ProjectReturnStore
    from .workspace_host_repo_native_r1 import WorkspaceHostStore
except Exception:
    from project_return_repo_native_r1 import ProjectReturnStore
    from workspace_host_repo_native_r1 import WorkspaceHostStore


PATH_BUDGET = 240
RESERVED_CHILD_PATH = 96
COMPACT_NAMESPACE = "return_host"


def _digest_token(value: str, length: int = 16) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:length]


def bounded_storage_root(base_dir: str | Path) -> Path:
    """Return a deterministic physical root with room for child artifacts.

    Runtime callers may supply a semantically useful namespace containing full
    session IDs and action labels. Those values remain in receipts, but when the
    projected child path would exceed the portable budget the physical storage
    root is compacted beneath the runtime owner directory.
    """

    requested = Path(base_dir)
    if len(str(requested)) + RESERVED_CHILD_PATH <= PATH_BUDGET:
        return requested

    anchor = requested
    while anchor.parent != anchor and anchor.name != "lumina_return_host_artifacts":
        anchor = anchor.parent
    owner_root = anchor.parent if anchor.name == "lumina_return_host_artifacts" else requested.parent
    return owner_root / COMPACT_NAMESPACE / _digest_token(str(requested))


def _checkpoint_storage_label(label: str) -> str:
    return f"checkpoint-{_digest_token(label)}"


@dataclass
class HostSnapshot:
    snapshot_id: str


class ContinuityRestoreStore:
    """Compatibility bridge over the repo-native project return store.

    Full semantic identifiers remain inside JSON payloads. Physical storage may
    use a compact deterministic root and compact checkpoint filename so an
    installed Windows prefix cannot exhaust the filesystem path budget.
    """

    def __init__(self, base_dir: str | Path):
        self.requested_base_dir = Path(base_dir)
        self.storage_base_dir = bounded_storage_root(self.requested_base_dir)
        self.storage_root_compacted = self.storage_base_dir != self.requested_base_dir
        self._store = ProjectReturnStore(self.storage_base_dir)

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
        storage_label = _checkpoint_storage_label(label)
        path = self._store.write_checkpoint(session_id, storage_label)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["checkpoint_label"] = label
        payload["storage_label"] = storage_label
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def project_return_payload(self, project_id: str) -> dict:
        payload = self._store.project_return_payload(project_id)
        local_host_bundle = self.storage_base_dir / "host_bundles" / f"{WorkspaceHostStore._safe_slug(project_id)}.json"
        if local_host_bundle.exists():
            host_bundle = json.loads(local_host_bundle.read_text(encoding="utf-8"))
            payload["host_bundle"] = host_bundle
            payload["return_strategy"] = "checkpoint_plus_host"
            latest_restore = payload.get("latest_restore")
            if isinstance(latest_restore, dict):
                latest_restore["linked_host_bundle"] = str(local_host_bundle)
        payload["storage"] = {
            "requested_base_dir": str(self.requested_base_dir),
            "storage_base_dir": str(self.storage_base_dir),
            "storage_root_compacted": self.storage_root_compacted,
            "path_budget": PATH_BUDGET,
        }
        return payload


class LuminaWorkspaceHost:
    """Compatibility bridge over the repo-native workspace host store."""

    def __init__(self, base_dir: str | Path):
        self.requested_base_dir = Path(base_dir)
        self.storage_base_dir = bounded_storage_root(self.requested_base_dir)
        self.storage_root_compacted = self.storage_base_dir != self.requested_base_dir
        self._store = WorkspaceHostStore(self.storage_base_dir)

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
            payload = json.load(f)
        payload["storage"] = {
            "requested_base_dir": str(self.requested_base_dir),
            "storage_base_dir": str(self.storage_base_dir),
            "storage_root_compacted": self.storage_root_compacted,
            "path_budget": PATH_BUDGET,
        }
        return payload
