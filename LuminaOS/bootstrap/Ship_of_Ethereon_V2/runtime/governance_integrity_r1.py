from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def infer_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent
    return Path.cwd()


def repo_relative_path(path: str | Path) -> str:
    resolved = Path(path).resolve()
    root = infer_repo_root().resolve()
    try:
        return str(resolved.relative_to(root))
    except ValueError:
        return str(path)


@dataclass
class GovernanceIntegrityRecord:
    event_id: str
    timestamp_utc: str
    prev_event_hash: Optional[str]
    record_hash: str
    event_type: str
    session_identifier: str
    previous_mode: Optional[str] = None
    new_mode: Optional[str] = None
    allowed: Optional[bool] = None
    reason: Optional[str] = None
    requested_action: Optional[str] = None
    artifact_delta: Optional[Any] = None
    canonical_change: Optional[bool] = None
    validation_reference: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["metadata"] = dict(self.metadata or {})
        return payload


class GovernanceIntegrityChain:
    """Append-only governance rail with record hashing and chain verification."""

    HASH_EXCLUDED_FIELDS = {"record_hash"}

    def __init__(self, log_path: str | Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _rows(self) -> List[Dict[str, Any]]:
        if not self.log_path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        with self.log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def latest_record(self) -> Optional[Dict[str, Any]]:
        rows = self._rows()
        return rows[-1] if rows else None

    def latest_event_hash(self) -> Optional[str]:
        latest = self.latest_record()
        return latest.get("record_hash") if latest else None

    def compute_checkpoint_hash(self, checkpoint_path: str | Path) -> str:
        return sha256_file(checkpoint_path)

    def _record_payload_for_hash(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in payload.items() if k not in self.HASH_EXCLUDED_FIELDS}

    def _compute_record_hash(self, payload: Dict[str, Any]) -> str:
        return sha256_text(canonical_json(self._record_payload_for_hash(payload)))

    def append_verified(
        self,
        *,
        event_type: str,
        session_identifier: str,
        previous_mode: Optional[str] = None,
        new_mode: Optional[str] = None,
        allowed: Optional[bool] = None,
        reason: Optional[str] = None,
        requested_action: Optional[str] = None,
        artifact_delta: Optional[Any] = None,
        canonical_change: Optional[bool] = None,
        validation_reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "event_id": f"gov-{uuid.uuid4().hex[:16]}",
            "timestamp_utc": utc_now(),
            "prev_event_hash": self.latest_event_hash(),
            "event_type": event_type,
            "session_identifier": session_identifier,
            "previous_mode": previous_mode,
            "new_mode": new_mode,
            "allowed": allowed,
            "reason": reason,
            "requested_action": requested_action,
            "artifact_delta": artifact_delta,
            "canonical_change": canonical_change,
            "validation_reference": validation_reference,
            "metadata": dict(metadata or {}),
        }
        record["record_hash"] = self._compute_record_hash(record)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return record

    def verify_chain(self) -> Dict[str, Any]:
        rows = self._rows()
        errors: List[str] = []
        warnings: List[str] = []
        previous_hash: Optional[str] = None
        chain_tainted = False

        for idx, row in enumerate(rows):
            expected_prev = previous_hash
            actual_prev = row.get("prev_event_hash")
            if actual_prev != expected_prev:
                errors.append(
                    f"row {idx}: prev_event_hash mismatch (expected {expected_prev}, got {actual_prev})"
                )
                chain_tainted = True

            actual_hash = row.get("record_hash")
            expected_hash = self._compute_record_hash(row)
            if not actual_hash:
                errors.append(f"row {idx}: missing record_hash")
                chain_tainted = True
            elif actual_hash != expected_hash:
                errors.append(f"row {idx}: record_hash mismatch")
                chain_tainted = True

            if chain_tainted and idx < len(rows) - 1:
                warnings.append(
                    f"row {idx + 1}: downstream linkage follows a tainted chain segment"
                )

            previous_hash = actual_hash if actual_hash == expected_hash else expected_hash

        return {
            "exists": self.log_path.exists(),
            "event_count": len(rows),
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "latest_event_hash": previous_hash,
            "log_path": repo_relative_path(self.log_path),
        }