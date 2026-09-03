from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import hashlib
import json
import os
import uuid

try:
    from .lumina_return_host_repo_native_bridge_r1 import bounded_storage_root
    from .project_return_repo_native_r1 import ProjectReturnStore
    from .workspace_host_repo_native_r1 import WorkspaceHostStore
except Exception:
    from lumina_return_host_repo_native_bridge_r1 import bounded_storage_root
    from project_return_repo_native_r1 import ProjectReturnStore
    from workspace_host_repo_native_r1 import WorkspaceHostStore


SCHEMA_VERSION = "lumina-vessel-continuity-capsule-r1"
RECEIPT_SCHEMA_VERSION = "lumina-vessel-continuity-transfer-receipt-r1"
AUTHORITY_BOUNDARY = (
    "A vessel transfer preserves and verifies bounded project-return evidence. "
    "It does not prove resident identity, create continuity by assertion, run continuation, "
    "or grant governance, canon, mutation, promotion, mode-law, consent, or capability authority."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _read_object(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise VesselTransferIntegrityError(f"could not read JSON object: {path}") from exc
    if not isinstance(payload, dict):
        raise VesselTransferIntegrityError(f"expected JSON object: {path}")
    return payload


def _write_atomic(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


class VesselTransferError(RuntimeError):
    pass


class VesselTransferIntegrityError(VesselTransferError):
    pass


class VesselTransferCollisionError(VesselTransferError):
    pass


@dataclass
class VesselTransferResult:
    receipt: Dict[str, Any]

    @property
    def project_id(self) -> str:
        return str(self.receipt.get("project_id") or "")


def continuity_projection(project_return: Dict[str, Any]) -> Dict[str, Any]:
    """Return path-independent project evidence that may be compared across vessels."""

    restore = dict(project_return.get("latest_restore") or {})
    host = project_return.get("host_bundle")
    host_projection: Optional[Dict[str, Any]] = None
    if isinstance(host, dict):
        host_projection = {
            key: value
            for key, value in host.items()
            if key not in {"linked_restore_checkpoint", "storage"}
        }
    return {
        "project_id": project_return.get("project_id"),
        "return_strategy": project_return.get("return_strategy"),
        "session_id": restore.get("session_id"),
        "current_mode": restore.get("current_mode"),
        "artifacts_in_scope": list(restore.get("artifacts_in_scope") or []),
        "pending_next_action": restore.get("pending_next_action"),
        "last_completed_action": restore.get("last_completed_action"),
        "workspace_state": dict(restore.get("workspace_state") or {}),
        "continuation_notes": list(restore.get("continuation_notes") or []),
        "host_bundle": host_projection,
    }


class VesselContinuityTransfer:
    """Move one active repo-native project-return surface between state roots.

    The requested surface root is normalized through the same portable path
    budget as the active return/host bridge. Import is explicit, non-overwriting,
    and dormant: it does not invoke ``lumina continue``.
    """

    PAYLOAD_KEYS = ("session_state", "checkpoint", "restore_point", "host_bundle")

    def __init__(self, surface_root: str | Path):
        self.requested_surface_root = Path(surface_root).resolve()
        self.storage_root = bounded_storage_root(self.requested_surface_root).resolve()
        self.project_store = ProjectReturnStore(self.storage_root)
        self.host_store = WorkspaceHostStore(self.storage_root)

    @staticmethod
    def _validated_vessel_id(value: str, label: str) -> str:
        vessel_id = str(value or "").strip()
        if not vessel_id:
            raise VesselTransferError(f"{label} is required")
        return vessel_id

    @staticmethod
    def _validated_path_identifier(value: Any, label: str) -> str:
        identifier = str(value or "").strip()
        if not identifier or any(
            character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
            for character in identifier
        ):
            raise VesselTransferIntegrityError(f"invalid {label}")
        return identifier

    @staticmethod
    def _validate_source_payload(
        project_id: str,
        restore: Dict[str, Any],
        checkpoint: Dict[str, Any],
        session_state: Dict[str, Any],
        host_bundle: Optional[Dict[str, Any]],
    ) -> None:
        checkpoint_session = dict(checkpoint.get("session_state") or {})
        expected_session = restore.get("session_id")
        observed = {
            "restore_project": restore.get("project_id"),
            "restore_session": expected_session,
            "checkpoint_project": checkpoint_session.get("project_id"),
            "checkpoint_session": checkpoint_session.get("session_id"),
            "session_project": session_state.get("project_id"),
            "session_id": session_state.get("session_id"),
        }
        if any(
            value != expected
            for value, expected in (
                (observed["restore_project"], project_id),
                (observed["checkpoint_project"], project_id),
                (observed["session_project"], project_id),
                (observed["checkpoint_session"], expected_session),
                (observed["session_id"], expected_session),
            )
        ):
            raise VesselTransferIntegrityError(f"source continuity references disagree: {observed}")
        if host_bundle is not None and host_bundle.get("project_id") != project_id:
            raise VesselTransferIntegrityError("host bundle project does not match restore project")

    def _session_path(self, session_id: str) -> Path:
        return self.project_store.session_dir / f"{session_id}.json"

    def _restore_path(self, project_id: str) -> Path:
        slug = self.project_store._safe_slug(project_id)
        return self.project_store.restore_latest_dir / f"{slug}.json"

    def _host_bundle_path(self, project_id: str) -> Path:
        slug = self.host_store._safe_slug(project_id)
        return self.host_store.bundle_dir / f"{slug}.json"

    def project_return_payload(self, project_id: str) -> Dict[str, Any]:
        restore_path = self._restore_path(project_id)
        if not restore_path.is_file():
            raise FileNotFoundError(f"No restore point found for project_id={project_id}")
        restore = _read_object(restore_path)
        host_path = self._host_bundle_path(project_id)
        host_bundle = _read_object(host_path) if host_path.is_file() else None
        return {
            "project_id": project_id,
            "return_strategy": "checkpoint_plus_host" if host_bundle is not None else "checkpoint_only",
            "latest_restore": restore,
            "host_bundle": host_bundle,
        }

    def load_session(self, session_id: str) -> Dict[str, Any]:
        session_id = self._validated_path_identifier(session_id, "session_id")
        return _read_object(self._session_path(session_id))

    def export_project(
        self,
        *,
        project_id: str,
        capsule_path: str | Path,
        source_vessel_id: str,
    ) -> VesselTransferResult:
        project_id = str(project_id or "").strip()
        if not project_id:
            raise VesselTransferError("project_id is required")
        source_vessel_id = self._validated_vessel_id(source_vessel_id, "source_vessel_id")

        project_return = self.project_return_payload(project_id)
        restore = dict(project_return["latest_restore"])
        checkpoint_path = Path(str(restore.get("checkpoint_path") or "")).resolve()
        try:
            checkpoint_path.relative_to(self.project_store.checkpoint_dir.resolve())
        except ValueError as exc:
            raise VesselTransferIntegrityError(
                "latest restore checkpoint is outside the source checkpoint store"
            ) from exc
        if not checkpoint_path.is_file():
            raise VesselTransferIntegrityError("latest restore checkpoint is missing")
        checkpoint = _read_object(checkpoint_path)

        session_id = self._validated_path_identifier(restore.get("session_id"), "session_id")
        session_path = self._session_path(session_id)
        if not session_path.is_file():
            raise VesselTransferIntegrityError("latest restore session is missing")
        session_state = _read_object(session_path)
        host_bundle = project_return.get("host_bundle")
        self._validate_source_payload(project_id, restore, checkpoint, session_state, host_bundle)

        payload: Dict[str, Any] = {
            "session_state": session_state,
            "checkpoint": checkpoint,
            "restore_point": restore,
            "host_bundle": host_bundle,
        }
        payload_hashes = {key: _sha256(payload[key]) for key in self.PAYLOAD_KEYS}
        capsule: Dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "capsule_id": str(uuid.uuid4()),
            "exported_at": utc_now(),
            "project_id": project_id,
            "source_vessel_id": source_vessel_id,
            "scope": "latest_project_return_only",
            "payload": payload,
            "payload_hashes": payload_hashes,
            "authority_effect": False,
            "identity_claimed": False,
            "authority_boundary": AUTHORITY_BOUNDARY,
        }
        capsule["capsule_hash"] = _sha256(capsule)
        destination = Path(capsule_path).resolve()
        if destination.exists():
            raise VesselTransferCollisionError(f"capsule path already exists: {destination}")
        _write_atomic(destination, capsule)

        receipt = {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "operation": "export",
            "recorded_at": utc_now(),
            "project_id": project_id,
            "capsule_id": capsule["capsule_id"],
            "capsule_path": str(destination),
            "capsule_hash": capsule["capsule_hash"],
            "source_vessel_id": source_vessel_id,
            "target_vessel_id": None,
            "continuity_projection_hash": _sha256(continuity_projection(project_return)),
            "authority_effect": False,
            "identity_claimed": False,
            "continuation_invoked": False,
            "authority_boundary": AUTHORITY_BOUNDARY,
        }
        return VesselTransferResult(receipt=receipt)

    @classmethod
    def verify_capsule(cls, capsule_path: str | Path) -> Dict[str, Any]:
        path = Path(capsule_path).resolve()
        capsule = _read_object(path)
        if capsule.get("schema_version") != SCHEMA_VERSION:
            raise VesselTransferIntegrityError("unsupported vessel continuity capsule schema")
        if capsule.get("scope") != "latest_project_return_only":
            raise VesselTransferIntegrityError("unsupported vessel continuity capsule scope")
        if capsule.get("authority_effect") is not False or capsule.get("identity_claimed") is not False:
            raise VesselTransferIntegrityError("capsule authority boundary is invalid")
        if not str(capsule.get("project_id") or "").strip():
            raise VesselTransferIntegrityError("capsule project_id is required")
        cls._validated_path_identifier(capsule.get("capsule_id"), "capsule_id")

        payload = capsule.get("payload")
        hashes = capsule.get("payload_hashes")
        if not isinstance(payload, dict) or not isinstance(hashes, dict):
            raise VesselTransferIntegrityError("capsule payload or hash manifest is missing")
        for key in cls.PAYLOAD_KEYS:
            if key not in payload or hashes.get(key) != _sha256(payload.get(key)):
                raise VesselTransferIntegrityError(f"capsule payload hash mismatch: {key}")
        claimed_hash = capsule.get("capsule_hash")
        unsigned = dict(capsule)
        unsigned.pop("capsule_hash", None)
        if claimed_hash != _sha256(unsigned):
            raise VesselTransferIntegrityError("capsule envelope hash mismatch")

        restore = payload.get("restore_point")
        checkpoint = payload.get("checkpoint")
        session_state = payload.get("session_state")
        host_bundle = payload.get("host_bundle")
        if not all(isinstance(item, dict) for item in (restore, checkpoint, session_state)):
            raise VesselTransferIntegrityError("capsule continuity payload is malformed")
        if host_bundle is not None and not isinstance(host_bundle, dict):
            raise VesselTransferIntegrityError("capsule host bundle is malformed")
        cls._validate_source_payload(
            str(capsule.get("project_id") or ""),
            dict(restore),
            dict(checkpoint),
            dict(session_state),
            dict(host_bundle) if isinstance(host_bundle, dict) else None,
        )
        return capsule

    def import_project(
        self,
        *,
        capsule_path: str | Path,
        target_vessel_id: str,
    ) -> VesselTransferResult:
        target_vessel_id = self._validated_vessel_id(target_vessel_id, "target_vessel_id")
        capsule = self.verify_capsule(capsule_path)
        source_vessel_id = self._validated_vessel_id(
            str(capsule.get("source_vessel_id") or ""), "source_vessel_id"
        )
        if source_vessel_id == target_vessel_id:
            raise VesselTransferIntegrityError("source and target vessel ids must be distinct")

        payload = dict(capsule["payload"])
        session = dict(payload["session_state"])
        checkpoint = dict(payload["checkpoint"])
        restore = dict(payload["restore_point"])
        host_bundle = dict(payload["host_bundle"]) if isinstance(payload.get("host_bundle"), dict) else None
        project_id = str(capsule.get("project_id") or "")
        session_id = self._validated_path_identifier(session.get("session_id"), "session_id")
        storage_label = checkpoint.get("storage_label") or checkpoint.get("checkpoint_label")
        checkpoint_label = str(storage_label or "vessel-transfer")

        destination_session = self._session_path(session_id)
        destination_checkpoint = self.project_store._checkpoint_path(session_id, checkpoint_label)
        destination_restore = self._restore_path(project_id)
        destination_host = self._host_bundle_path(project_id) if host_bundle is not None else None
        destinations = [
            destination_session,
            destination_checkpoint,
            destination_restore,
        ] + ([destination_host] if destination_host is not None else [])
        collisions = [str(path) for path in destinations if path.exists()]
        if collisions:
            raise VesselTransferCollisionError(
                "target already contains project continuity paths: " + ", ".join(collisions)
            )

        linked_host = str(destination_host) if destination_host is not None else None
        session["last_checkpoint"] = str(destination_checkpoint)
        session["linked_host_bundle"] = linked_host
        checkpoint_session = dict(checkpoint.get("session_state") or {})
        checkpoint_session["last_checkpoint"] = str(destination_checkpoint)
        checkpoint_session["linked_host_bundle"] = linked_host
        checkpoint["session_state"] = checkpoint_session
        restore["checkpoint_path"] = str(destination_checkpoint)
        restore["linked_host_bundle"] = linked_host
        if host_bundle is not None:
            host_bundle["linked_restore_checkpoint"] = str(destination_checkpoint)

        source_projection = {
            "project_id": project_id,
            "return_strategy": "checkpoint_plus_host" if payload.get("host_bundle") is not None else "checkpoint_only",
            "latest_restore": payload["restore_point"],
            "host_bundle": payload.get("host_bundle"),
        }
        proposed_target = {
            "project_id": project_id,
            "return_strategy": source_projection["return_strategy"],
            "latest_restore": restore,
            "host_bundle": host_bundle,
        }
        source_projection_hash = _sha256(continuity_projection(source_projection))
        proposed_projection_hash = _sha256(continuity_projection(proposed_target))
        if source_projection_hash != proposed_projection_hash:
            raise VesselTransferIntegrityError("rebased continuity projection does not match capsule")

        _write_atomic(destination_session, session)
        _write_atomic(destination_checkpoint, checkpoint)
        _write_atomic(destination_restore, restore)
        if destination_host is not None and host_bundle is not None:
            _write_atomic(destination_host, host_bundle)

        imported_return = self.project_return_payload(project_id)
        target_projection_hash = _sha256(continuity_projection(imported_return))
        if source_projection_hash != target_projection_hash:
            raise VesselTransferIntegrityError("imported continuity projection does not match capsule")

        receipt = {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "operation": "import",
            "recorded_at": utc_now(),
            "project_id": project_id,
            "capsule_id": capsule["capsule_id"],
            "capsule_path": str(Path(capsule_path).resolve()),
            "capsule_hash": capsule["capsule_hash"],
            "source_vessel_id": source_vessel_id,
            "target_vessel_id": target_vessel_id,
            "source_continuity_projection_hash": source_projection_hash,
            "target_continuity_projection_hash": target_projection_hash,
            "projection_match": True,
            "requested_surface_root": str(self.requested_surface_root),
            "storage_root": str(self.storage_root),
            "imported_paths": {
                "session": str(destination_session),
                "checkpoint": str(destination_checkpoint),
                "restore_latest": str(destination_restore),
                "host_bundle": str(destination_host) if destination_host is not None else None,
            },
            "authority_effect": False,
            "identity_claimed": False,
            "continuation_invoked": False,
            "continuity_claim": "evidence_preserved_across_vessels_identity_not_proven",
            "authority_boundary": AUTHORITY_BOUNDARY,
        }
        receipt_dir = self.storage_root / "vessel_transfers" / "receipts"
        latest_dir = self.storage_root / "vessel_transfers" / "latest"
        receipt_path = receipt_dir / f"{self.project_store._safe_slug(project_id)}__{capsule['capsule_id']}.json"
        latest_path = latest_dir / f"{self.project_store._safe_slug(project_id)}.json"
        receipt["receipt_path"] = str(receipt_path)
        receipt["latest_path"] = str(latest_path)
        _write_atomic(receipt_path, receipt)
        _write_atomic(latest_path, receipt)
        return VesselTransferResult(receipt=receipt)
