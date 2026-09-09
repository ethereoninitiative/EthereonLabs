"""Read existing local return evidence for Bridge without constructing a store.

Verification means bounded local artifact agreement and a stable read, not
signed provenance, governance permission, or proof of resident identity.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import sys
from typing import Any

RUNTIME_ROOT = Path(__file__).resolve().parents[1] / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from lumina_continuation_action_r1 import continuation_target, normalize_continuation_action
from lumina_return_host_repo_native_bridge_r1 import bounded_storage_root
from project_return_repo_native_r1 import ProjectReturnStore
from repo_paths_r1 import state_root as configured_state_root
from resonant_return_panel_r1 import INPUT_SCHEMA, build_panel

SCHEMA_VERSION = "lumina-bridge-return-r1"
MAX_FILE_BYTES = 1_048_576
OLDER_AFTER_SECONDS = 86_400
RETURN_KEYS = (
    "project_id", "session_id", "current_mode", "artifacts_in_scope", "workspace_state",
    "continuation_notes", "pending_next_action", "last_completed_action",
)
RETURN_AUTHORITY_BOUNDARY = (
    "Bridge verifies local return/checkpoint/session agreement, host checkpoint linkage, "
    "and source stability while reading. Guidance history is parsed and project-scoped; "
    "historical references are not independently verified. Digests identify observed bytes, "
    "not signed provenance. All next directions remain advisory and await runtime governance."
)


class ReturnEvidenceError(ValueError):
    def __init__(self, message: str, status: str = "verification_failed"):
        super().__init__(message)
        self.status = status


def _object(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise ReturnEvidenceError(f"{label} must be a JSON object.")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReturnEvidenceError(f"{label} is missing or malformed.")
    return value


def _identifier(value: Any, label: str) -> str:
    value = _text(value, label)
    if len(value) > 200 or any(not (char.isalnum() or char in "-_") for char in value):
        raise ReturnEvidenceError(f"{label} is not a valid local identifier.")
    return value


def _timestamp(value: Any, label: str, now: datetime) -> datetime:
    try:
        result = datetime.fromisoformat(_text(value, label).replace("Z", "+00:00"))
        if result.tzinfo is None or (result - now).total_seconds() > 300:
            raise ValueError("unknown timezone or future timestamp")
        return result
    except (TypeError, ValueError) as exc:
        raise ReturnEvidenceError(f"{label} is invalid or ahead of the local clock.") from exc


def _unique_pairs(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReturnEvidenceError("Source JSON contains a duplicate key.")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ReturnEvidenceError(f"Source JSON contains a non-finite number: {value}.")


class SnapshotReader:
    """Read fixed owner paths, remembering both bytes and meaningful absences."""

    def __init__(self):
        self.records: list[dict] = []

    @staticmethod
    def _bytes(root: Path, path: Path) -> bytes | None:
        # Check lexical containment before following any path component.
        path = Path(os.path.abspath(path))
        try:
            parts = path.relative_to(root).parts
        except ValueError as exc:
            raise ReturnEvidenceError("An evidence reference leaves its owning store.") from exc
        if any(parent.is_symlink() for parent in (root, *root.parents)):
            raise ReturnEvidenceError("Symlinked evidence stores are not accepted.")
        current = root
        for part in parts:
            current = current / part
            if current.is_symlink():
                raise ReturnEvidenceError("Symlinked evidence is not accepted.")
        try:
            info = path.stat()
        except FileNotFoundError:
            return None
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE_BYTES:
            raise ReturnEvidenceError("Evidence must be a regular file of at most 1 MiB.")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        with os.fdopen(os.open(path, flags), "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise ReturnEvidenceError("Evidence stopped being a regular file.")
            raw = handle.read(MAX_FILE_BYTES + 1)
        if len(raw) > MAX_FILE_BYTES:
            raise ReturnEvidenceError("Evidence exceeds the 1 MiB read bound.")
        return raw

    def read(self, root: Path, path: Path, role: str, *, optional: bool = False, jsonl: bool = False) -> Any:
        raw = self._bytes(root, path)
        self.records.append({"root": root, "path": path, "role": role, "raw": raw})
        if raw is None:
            if optional:
                return [] if jsonl else None
            raise ReturnEvidenceError(f"The {role.replace('_', ' ')} file is missing.", "missing_evidence")
        try:
            def parse(text: str) -> dict:
                return _object(json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant), role)
            text = raw.decode("utf-8")
            return [parse(line) for line in text.splitlines() if line.strip()] if jsonl else parse(text)
        except (UnicodeError, ValueError, RecursionError) as exc:
            raise ReturnEvidenceError(f"The {role.replace('_', ' ')} file is malformed: {exc}") from exc

    def ensure_stable(self) -> None:
        for record in self.records:
            if self._bytes(record["root"], record["path"]) != record["raw"]:
                raise ReturnEvidenceError("Saved state changed during inspection. Refresh to read it again.", "changed_during_read")

    def provenance(self) -> list[dict]:
        return [{
            "role": row["role"], "path": str(row["path"]), "present": row["raw"] is not None,
            "sha256": sha256(row["raw"]).hexdigest() if row["raw"] is not None else None,
            "bytes": len(row["raw"]) if row["raw"] is not None else 0,
        } for row in self.records]


def _same_return(left: dict, right: dict, label: str) -> None:
    if any(key not in left or key not in right or left[key] != right[key] for key in RETURN_KEYS):
        raise ReturnEvidenceError(f"{label} disagrees with the latest project return.")


def _checkpoint(reader: SnapshotReader, surface: Path, reference: Any, role: str) -> tuple[Path, dict]:
    path = Path(_text(reference, role))
    if not path.is_absolute():
        raise ReturnEvidenceError("Checkpoint references must be absolute local owner paths.")
    return path, reader.read(surface / "checkpoints", path, role)


def load_bridge_return(*, state_root: Path | None = None, runtime_base: Path | None = None,
                       now: datetime | None = None) -> dict:
    """Project one active Harbor project's verified saved return into the panel."""
    root = Path(state_root if state_root is not None else configured_state_root()).resolve()
    base = Path(runtime_base if runtime_base is not None else root / "runtime_runner_r1_actiontype_logging").resolve()
    surface = bounded_storage_root(base / "lumina_project_surface")
    observed = now or datetime.now(timezone.utc)
    reader = SnapshotReader()
    result = {
        "schema_version": SCHEMA_VERSION, "observed_at": observed.isoformat(), "read_only": True,
        "status": "no_active_project", "verified": False, "project_id": None, "project_name": None,
        "panel": None, "freshness": None, "provenance": [], "host_linkage": None,
        "verification_scope": "local artifact agreement and stable source reads",
        "governance_verified": False, "signatures_verified": False, "execution_authorized": False,
        "authority_boundary": RETURN_AUTHORITY_BOUNDARY,
    }
    try:
        marker = reader.read(root, root / "active_project.json", "active_project", optional=True)
        if marker is None:
            reader.ensure_stable()
            result["message"] = "Open a Harbor project to see its saved return point."
            return result
        project_id = _identifier(marker.get("active_project_slug"), "Active project slug")
        result.update(project_id=project_id, project_name=_text(marker.get("active_project_name") or project_id, "Project name"))
        slug = ProjectReturnStore._safe_slug(project_id)
        restore = reader.read(surface, surface / "project_restores" / "latest" / f"{slug}.json", "project_return")
        if restore.get("project_id") != project_id:
            raise ReturnEvidenceError("The return file belongs to a different project.")
        session_id = _identifier(restore.get("session_id"), "Return session ID")
        checkpoint_path, checkpoint = _checkpoint(reader, surface, restore.get("checkpoint_path"), "return_checkpoint")
        checkpoint_state = _object(checkpoint.get("session_state"), "Checkpoint session state")
        session = reader.read(surface, surface / "sessions" / f"{session_id}.json", "return_session")
        _same_return(restore, checkpoint_state, "The saved checkpoint")
        _same_return(restore, session, "The saved session")
        if session.get("last_checkpoint") != str(checkpoint_path):
            raise ReturnEvidenceError("The session points to a different latest checkpoint.")
        saved = _timestamp(restore.get("captured_at"), "Return timestamp", observed)
        checkpoint_time = _timestamp(checkpoint.get("created_at"), "Checkpoint timestamp", observed)
        if checkpoint_time > saved:
            raise ReturnEvidenceError("The return timestamp precedes its checkpoint.")

        host_path = surface / "host_bundles" / f"{slug}.json"
        host = reader.read(surface, host_path, "host_bundle", optional=True)
        if host is not None:
            host_snapshot = reader.read(surface, surface / "host_snapshots" / "latest" / f"{slug}.json", "host_snapshot")
            if (host.get("bundle_type") != "lumina_host_workspace_r1" or host.get("project_id") != project_id
                    or {key: value for key, value in host.items() if key != "bundle_type"} != host_snapshot):
                raise ReturnEvidenceError("The host bundle and its saved snapshot disagree.")
            _timestamp(host.get("captured_at"), "Host timestamp", observed)
            linked_path, linked = _checkpoint(reader, surface, host.get("linked_restore_checkpoint"), "host_checkpoint")
            _same_return(restore, _object(linked.get("session_state"), "Host checkpoint session"), "The host checkpoint")
            linked_time = _timestamp(linked.get("created_at"), "Host checkpoint timestamp", observed)
            relationship = "current_checkpoint"
            if linked_path != checkpoint_path:
                if checkpoint_state.get("last_checkpoint") != str(linked_path) or linked_time > checkpoint_time:
                    raise ReturnEvidenceError("The host checkpoint is not the latest checkpoint's matching predecessor.")
                relationship = "matching_previous_checkpoint"
            result["host_linkage"] = {
                "status": relationship, "checkpoint_ref": str(linked_path), "verified": True,
                "stored_host_reference": restore.get("linked_host_bundle"),
                "resolved_host_reference": str(host_path),
            }
        elif restore.get("linked_host_bundle"):
            raise ReturnEvidenceError("The return references a host bundle that is missing.", "missing_evidence")

        history_path = base / "self_guidance_history" / "projects" / f"{slug}.jsonl"
        history = reader.read(base, history_path, "guidance_history", optional=True, jsonl=True)
        for row in history:
            if row.get("project_id") != project_id:
                raise ReturnEvidenceError("Guidance history contains a different project.")
            _timestamp(row.get("timestamp_utc"), "Guidance timestamp", observed)

        # Match the return owner's local-host rebinding without changing saved bytes.
        latest = dict(restore)
        if host is not None:
            latest["linked_host_bundle"] = str(host_path)
        host = host or {}
        host_summary = {key: host[key] for key in ("project_id", "focus_target", "active_layout_id") if key in host}
        for target, key, identifier in (("panel_ids", "panels", "panel_id"),
                                        ("reference_ids", "references", "reference_id"),
                                        ("pinned_tool_ids", "tool_bindings", "tool_id")):
            rows = host.get(key, [])
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ReturnEvidenceError(f"Host {key} must contain objects.")
            host_summary[target] = [row[identifier] for row in rows if row.get(identifier) and (key != "tool_bindings" or row.get("pinned"))]
        # Preserve the actual host checkpoint in host_linkage/provenance, rather
        # than projecting its verified predecessor as a conflicting current link.
        stance = {
            "focus_target": host.get("focus_target") or "continue_from_latest_checkpoint",
            "open_panels": host_summary["panel_ids"], "reference_ids": host_summary["reference_ids"],
            "pinned_tools": host_summary["pinned_tool_ids"],
        }
        candidates = []
        pending = latest.get("pending_next_action")
        focus = host.get("focus_target")
        for source, action, label, reference in (
            ("saved-next-action", pending, "Saved next action", str(checkpoint_path)),
            ("workspace-focus", f"continue::{focus}" if focus else None, "Workspace focus", str(host_path)),
        ):
            if not action or (source == "workspace-focus" and pending and continuation_target(pending) == continuation_target(focus)):
                continue
            candidates.append({
                "trajectory_id": source, "label": label, "action": normalize_continuation_action(action),
                "vector": {"instantiated_state": 1.0, "continuity_history": 1.0,
                           "relational_context": float(source == "workspace-focus" and bool(host_summary["reference_ids"])),
                           "orientation_field": 1.0, "potential_trajectories": 1.0},
                "evidence_refs": [reference],
            })
        panel = build_panel({
            "schema_version": INPUT_SCHEMA, "evidence_scope": "supplied_snapshot", "project_id": project_id,
            "requested_action": "continue_from_latest_checkpoint",
            "resolved_project_return": {"project_id": project_id, "latest_restore": latest,
                                        "return_strategy": "checkpoint_plus_host" if host else "checkpoint_only"},
            "resolved_host_bundle": host_summary, "working_stance": stance,
            "guidance_history": history, "candidates": candidates,
        })
        reader.ensure_stable()
        age = max(0, int((observed - saved).total_seconds()))
        result.update(
            status="ready", verified=True, panel=panel,
            message="Saved return evidence agrees. Next directions await a governed cycle.",
            freshness={"saved_at": saved.isoformat(), "age_seconds": age,
                       "status": "older_saved_state" if age > OLDER_AFTER_SECONDS else "recent_saved_state",
                       "older_after_seconds": OLDER_AFTER_SECONDS, "stable_during_read": True},
        )
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        result.update(status=getattr(exc, "status", "verification_failed"), message=str(exc), verified=False, panel=None)
    finally:
        result["provenance"] = reader.provenance()
    return result
