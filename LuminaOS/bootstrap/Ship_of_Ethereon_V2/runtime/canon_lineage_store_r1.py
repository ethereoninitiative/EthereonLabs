from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
class CanonRecord:
    canon_version: str
    canon_parent: Optional[str]
    canon_commit_summary: str
    canon_timestamp: str
    validation_artifact_reference: str
    governance_event_hash: str
    promotion_payload_hash: str
    runtime_seed_version: str
    notes: Optional[str] = None
    prev_lineage_hash: Optional[str] = None
    lineage_record_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CanonLineageStore:
    """Append-only canon lineage with parent linkage and record hashing."""

    HASH_EXCLUDED_FIELDS = {"lineage_record_hash"}

    def __init__(self, lineage_path: str | Path):
        self.lineage_path = Path(lineage_path)
        self.lineage_path.parent.mkdir(parents=True, exist_ok=True)

    def _rows(self) -> List[Dict[str, Any]]:
        if not self.lineage_path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        with self.lineage_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def read_lineage(self) -> List[Dict[str, Any]]:
        return self._rows()

    def current_head(self) -> Optional[Dict[str, Any]]:
        rows = self._rows()
        return rows[-1] if rows else None

    def latest_lineage_hash(self) -> Optional[str]:
        head = self.current_head()
        return head.get("lineage_record_hash") if head else None

    def _record_payload_for_hash(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in payload.items() if k not in self.HASH_EXCLUDED_FIELDS}

    def _compute_record_hash(self, payload: Dict[str, Any]) -> str:
        return sha256_text(canonical_json(self._record_payload_for_hash(payload)))

    def _next_version(self) -> str:
        rows = self._rows()
        return f"canon-{len(rows)+1:04d}"

    def promote(
        self,
        *,
        canon_commit_summary: str,
        validation_artifact_reference: str,
        governance_event_hash: str,
        promotion_payload: Dict[str, Any],
        runtime_seed_version: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        head = self.current_head()
        record = {
            "canon_version": self._next_version(),
            "canon_parent": head["canon_version"] if head else None,
            "canon_commit_summary": canon_commit_summary,
            "canon_timestamp": utc_now(),
            "validation_artifact_reference": validation_artifact_reference,
            "governance_event_hash": governance_event_hash,
            "promotion_payload_hash": sha256_text(canonical_json(dict(promotion_payload or {}))),
            "runtime_seed_version": runtime_seed_version,
            "notes": notes,
            "prev_lineage_hash": head.get("lineage_record_hash") if head else None,
        }
        record["lineage_record_hash"] = self._compute_record_hash(record)
        with self.lineage_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return record

    def verify_lineage(self) -> Dict[str, Any]:
        rows = self._rows()
        errors: List[str] = []
        warnings: List[str] = []
        previous_hash: Optional[str] = None
        previous_version: Optional[str] = None
        seen_versions = set()
        lineage_tainted = False

        for idx, row in enumerate(rows):
            version = row.get("canon_version")
            if not version:
                errors.append(f"row {idx}: missing canon_version")
                lineage_tainted = True
            elif version in seen_versions:
                errors.append(f"row {idx}: duplicate canon_version {version}")
                lineage_tainted = True
            else:
                seen_versions.add(version)

            expected_parent = previous_version if idx > 0 else None
            if row.get("canon_parent") != expected_parent:
                errors.append(
                    f"row {idx}: canon_parent mismatch (expected {expected_parent}, got {row.get('canon_parent')})"
                )
                lineage_tainted = True

            if row.get("prev_lineage_hash") != previous_hash:
                errors.append(
                    f"row {idx}: prev_lineage_hash mismatch (expected {previous_hash}, got {row.get('prev_lineage_hash')})"
                )
                lineage_tainted = True

            actual_hash = row.get("lineage_record_hash")
            expected_hash = self._compute_record_hash(row)
            if not actual_hash:
                errors.append(f"row {idx}: missing lineage_record_hash")
                lineage_tainted = True
            elif actual_hash != expected_hash:
                errors.append(f"row {idx}: lineage_record_hash mismatch")
                lineage_tainted = True

            if lineage_tainted and idx < len(rows) - 1:
                warnings.append(
                    f"row {idx + 1}: downstream linkage follows a tainted lineage segment"
                )

            previous_hash = actual_hash if actual_hash == expected_hash else expected_hash
            previous_version = version

        return {
            "exists": self.lineage_path.exists(),
            "record_count": len(rows),
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "current_head": rows[-1]["canon_version"] if rows else None,
            "lineage_path": repo_relative_path(self.lineage_path),
        }
