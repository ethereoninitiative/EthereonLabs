from __future__ import annotations

"""Non-governing provenance receipts for observable cross-layer coupling.

This module makes a signal crossing between Lumina components inspectable. It
does not route the signal, apply its effect, or grant the signal authority.
Accepted receipts remain diagnostic evidence only.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
import hashlib
import json
import uuid


SCHEMA_VERSION = "lumina-mycelial-coupling-receipt-v0.1"
AUTHORITY_BOUNDARY = (
    "diagnostic coupling evidence only; never creates governance, canon, mode, "
    "checkpoint, mutation, promotion, identity, or capability authority"
)

ALLOWED_RELATIONS = {"context", "memory", "diagnostic", "operator", "projection"}
ALLOWED_EVIDENCE_KINDS = {"observed", "derived", "symbolic", "operator-provided"}
ALLOWED_MEMORY_EFFECTS = {"none", "retrieval-weight", "topology", "threshold", "checkpoint"}
ALLOWED_RETENTIONS = {"ephemeral", "session", "append-only"}

SIGNED_FIELDS = (
    "schema_version",
    "signal_id",
    "source",
    "destination",
    "relation",
    "created_at",
    "evidence_kind",
    "evidence_reference",
    "evidence_digest",
    "confidence",
    "reversible",
    "authority_effect",
    "memory_effect",
    "retention",
    "effect_summary",
    "parent_receipt",
    "authority_boundary",
)
RECEIPT_FIELDS = frozenset((*SIGNED_FIELDS, "receipt_hash"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _sha256(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def compute_receipt_hash(payload: Mapping[str, Any]) -> str:
    """Compute the receipt hash from the exact signed field set."""
    return _sha256({field: payload.get(field) for field in SIGNED_FIELDS})


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


@dataclass(frozen=True)
class CouplingReceipt:
    schema_version: str
    signal_id: str
    source: str
    destination: str
    relation: str
    created_at: str
    evidence_kind: str
    evidence_reference: str
    evidence_digest: str
    confidence: float
    reversible: bool
    authority_effect: bool
    memory_effect: str
    retention: str
    effect_summary: str
    parent_receipt: Optional[str]
    authority_boundary: str
    receipt_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReceiptValidation:
    valid: bool
    errors: List[str]
    receipt_hash: Optional[str]
    signal_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CouplingReceiptDecision:
    status: str
    accepted: bool
    replay: bool
    quarantined: bool
    receipt_hash: Optional[str]
    signal_id: Optional[str]
    reasons: List[str]
    authority_effect: bool = False
    authority_event_created: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_coupling_receipt(
    *,
    source: str,
    destination: str,
    relation: str,
    evidence_kind: str,
    evidence_reference: str,
    evidence_payload: Any,
    confidence: float,
    reversible: bool,
    memory_effect: str,
    retention: str,
    effect_summary: str,
    authority_effect: bool = False,
    parent_receipt: Optional[str] = None,
    signal_id: Optional[str] = None,
    created_at: Optional[str] = None,
) -> CouplingReceipt:
    """Create a hashed coupling receipt while enforcing zero authority effect."""
    if authority_effect is not False:
        raise ValueError("coupling receipts may not declare authority_effect=true")

    payload: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "signal_id": signal_id or f"signal-{uuid.uuid4().hex}",
        "source": source,
        "destination": destination,
        "relation": relation,
        "created_at": created_at or utc_now(),
        "evidence_kind": evidence_kind,
        "evidence_reference": evidence_reference,
        "evidence_digest": _sha256(evidence_payload),
        "confidence": confidence,
        "reversible": reversible,
        "authority_effect": False,
        "memory_effect": memory_effect,
        "retention": retention,
        "effect_summary": effect_summary,
        "parent_receipt": parent_receipt,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
    payload["receipt_hash"] = compute_receipt_hash(payload)
    validation = validate_receipt(payload)
    if not validation.valid:
        raise ValueError("invalid coupling receipt: " + "; ".join(validation.errors))
    return CouplingReceipt(**payload)


def validate_receipt(payload: Mapping[str, Any]) -> ReceiptValidation:
    errors: List[str] = []
    keys = set(payload)
    missing = sorted(RECEIPT_FIELDS - keys)
    unexpected = sorted(keys - RECEIPT_FIELDS)
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if unexpected:
        errors.append("unexpected fields: " + ", ".join(unexpected))

    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version mismatch")

    for field in ("signal_id", "source", "destination", "evidence_reference", "effect_summary"):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")

    if payload.get("relation") not in ALLOWED_RELATIONS:
        errors.append("relation is not allowed")
    if payload.get("evidence_kind") not in ALLOWED_EVIDENCE_KINDS:
        errors.append("evidence_kind is not allowed")
    if payload.get("memory_effect") not in ALLOWED_MEMORY_EFFECTS:
        errors.append("memory_effect is not allowed")
    if payload.get("retention") not in ALLOWED_RETENTIONS:
        errors.append("retention is not allowed")

    confidence = payload.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        errors.append("confidence must be numeric")
    elif not 0.0 <= float(confidence) <= 1.0:
        errors.append("confidence must be between 0.0 and 1.0")

    if not isinstance(payload.get("reversible"), bool):
        errors.append("reversible must be boolean")
    if payload.get("authority_effect") is not False:
        errors.append("authority_effect must be false")
    if payload.get("authority_boundary") != AUTHORITY_BOUNDARY:
        errors.append("authority_boundary mismatch")

    parent = payload.get("parent_receipt")
    if parent is not None and not _is_sha256(parent):
        errors.append("parent_receipt must be null or a SHA-256 receipt hash")
    if not _is_sha256(payload.get("evidence_digest")):
        errors.append("evidence_digest must be SHA-256")

    created_at = payload.get("created_at")
    if not isinstance(created_at, str):
        errors.append("created_at must be an ISO-8601 string")
    else:
        try:
            parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                errors.append("created_at must include a timezone")
        except ValueError:
            errors.append("created_at must be valid ISO-8601")

    receipt_hash = payload.get("receipt_hash")
    if not _is_sha256(receipt_hash):
        errors.append("receipt_hash must be SHA-256")
    elif not missing and compute_receipt_hash(payload) != receipt_hash:
        errors.append("receipt_hash mismatch")

    return ReceiptValidation(
        valid=not errors,
        errors=errors,
        receipt_hash=receipt_hash if isinstance(receipt_hash, str) else None,
        signal_id=payload.get("signal_id") if isinstance(payload.get("signal_id"), str) else None,
    )


class CouplingReceiptLedger:
    """Append accepted receipts and classify intake without creating authority.

    Replays are recorded as intake decisions but are not appended as new
    receipts. Invalid, conflicting, or orphaned receipts are quarantined as
    decisions only. This ledger is diagnostic and is not a governance ledger.
    """

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.receipts_path = self.base_dir / "coupling_receipts_r1.jsonl"
        self.decisions_path = self.base_dir / "coupling_receipt_intake_r1.jsonl"

    @staticmethod
    def _payload(receipt: CouplingReceipt | Mapping[str, Any]) -> Dict[str, Any]:
        return receipt.to_dict() if isinstance(receipt, CouplingReceipt) else dict(receipt)

    @staticmethod
    def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
        return rows

    @staticmethod
    def _append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(payload), sort_keys=True, ensure_ascii=False) + "\n")

    def read_receipts(self) -> List[Dict[str, Any]]:
        return self._read_jsonl(self.receipts_path)

    def read_decisions(self) -> List[Dict[str, Any]]:
        return self._read_jsonl(self.decisions_path)

    def _record_decision(self, decision: CouplingReceiptDecision) -> CouplingReceiptDecision:
        payload = decision.to_dict()
        payload["decided_at"] = utc_now()
        payload["authority_boundary"] = AUTHORITY_BOUNDARY
        self._append_jsonl(self.decisions_path, payload)
        return decision

    def ingest(self, receipt: CouplingReceipt | Mapping[str, Any]) -> CouplingReceiptDecision:
        payload = self._payload(receipt)
        validation = validate_receipt(payload)
        if not validation.valid:
            return self._record_decision(
                CouplingReceiptDecision(
                    status="quarantined",
                    accepted=False,
                    replay=False,
                    quarantined=True,
                    receipt_hash=validation.receipt_hash,
                    signal_id=validation.signal_id,
                    reasons=validation.errors,
                )
            )

        existing_integrity = self.verify_integrity()
        if not existing_integrity["valid"]:
            return self._record_decision(
                CouplingReceiptDecision(
                    status="quarantined",
                    accepted=False,
                    replay=False,
                    quarantined=True,
                    receipt_hash=validation.receipt_hash,
                    signal_id=validation.signal_id,
                    reasons=["accepted receipt history failed integrity verification"],
                )
            )
        existing = self.read_receipts()
        by_hash = {row.get("receipt_hash"): row for row in existing}
        by_signal = {row.get("signal_id"): row for row in existing}
        receipt_hash = str(payload["receipt_hash"])
        signal_id = str(payload["signal_id"])

        if receipt_hash in by_hash:
            return self._record_decision(
                CouplingReceiptDecision(
                    status="replay",
                    accepted=False,
                    replay=True,
                    quarantined=False,
                    receipt_hash=receipt_hash,
                    signal_id=signal_id,
                    reasons=["historical receipt replay; no new coupling or authority event created"],
                )
            )
        if signal_id in by_signal:
            return self._record_decision(
                CouplingReceiptDecision(
                    status="quarantined",
                    accepted=False,
                    replay=False,
                    quarantined=True,
                    receipt_hash=receipt_hash,
                    signal_id=signal_id,
                    reasons=["signal_id already exists with different receipt content"],
                )
            )

        parent = payload.get("parent_receipt")
        if parent is not None and parent not in by_hash:
            return self._record_decision(
                CouplingReceiptDecision(
                    status="quarantined",
                    accepted=False,
                    replay=False,
                    quarantined=True,
                    receipt_hash=receipt_hash,
                    signal_id=signal_id,
                    reasons=["parent_receipt is not present in accepted history"],
                )
            )

        self._append_jsonl(self.receipts_path, payload)
        return self._record_decision(
            CouplingReceiptDecision(
                status="accepted",
                accepted=True,
                replay=False,
                quarantined=False,
                receipt_hash=receipt_hash,
                signal_id=signal_id,
                reasons=["receipt accepted as non-governing coupling evidence"],
            )
        )

    def verify_integrity(self) -> Dict[str, Any]:
        errors: List[str] = []
        seen_hashes: set[str] = set()
        seen_signals: set[str] = set()
        try:
            rows = self.read_receipts()
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            rows = []
            errors.append(f"receipt history is unreadable: {exc}")
        for index, payload in enumerate(rows):
            if not isinstance(payload, dict):
                errors.append(f"receipt[{index}]: receipt must be a JSON object")
                continue
            validation = validate_receipt(payload)
            if not validation.valid:
                errors.extend(f"receipt[{index}]: {error}" for error in validation.errors)
                continue
            receipt_hash = str(payload["receipt_hash"])
            signal_id = str(payload["signal_id"])
            if receipt_hash in seen_hashes:
                errors.append(f"receipt[{index}]: duplicate receipt_hash")
            if signal_id in seen_signals:
                errors.append(f"receipt[{index}]: duplicate signal_id")
            parent = payload.get("parent_receipt")
            if parent is not None and parent not in seen_hashes:
                errors.append(f"receipt[{index}]: parent is missing or appears after child")
            seen_hashes.add(receipt_hash)
            seen_signals.add(signal_id)
        try:
            decision_count = len(self.read_decisions())
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            decision_count = 0
            errors.append(f"intake decision history is unreadable: {exc}")
        return {
            "schema_version": "lumina-mycelial-coupling-ledger-integrity-r1",
            "valid": not errors,
            "receipt_count": len(rows),
            "decision_count": decision_count,
            "errors": errors,
            "authority_effect": False,
            "authority_boundary": AUTHORITY_BOUNDARY,
        }
