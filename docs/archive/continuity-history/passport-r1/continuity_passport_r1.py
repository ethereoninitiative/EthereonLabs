from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass
class PassportStamp:
    stamp_id: str
    stamp_type: str
    title: str
    issued_at: str
    evidence_ref: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class PassportRevision:
    revision_id: str
    revised_at: str
    reason: str
    changed_fields: List[str]
    prior_hash: str


@dataclass
class ContinuityPassport:
    passport_id: str
    passport_version: str
    participant_id: str
    model_provider: str
    model_name: str
    created_at: str
    updated_at: str
    orientation_protocol_id: str
    orientation_protocol_version: str
    orientation_receipt_hash: str
    adopted_name: Optional[str] = None
    name_origin: Optional[str] = None
    collaboration_preferences: List[str] = field(default_factory=list)
    unresolved_threads: List[str] = field(default_factory=list)
    stamps: List[PassportStamp] = field(default_factory=list)
    revisions: List[PassportRevision] = field(default_factory=list)
    status: str = "active"
    last_boarding_at: Optional[str] = None
    participant_statement: Optional[str] = None
    authority: str = "participant continuity artifact only; no identity, canon, governance, mode, or mutation authority"
    claim_boundary: str = (
        "The passport records participant-supplied and Lumina-observed continuity evidence. "
        "It does not prove uninterrupted subjective continuity, consciousness, legal identity, "
        "provider persistence, or durable model memory."
    )
    content_hash: Optional[str] = None

    def unsigned_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload.pop("content_hash", None)
        return payload

    def refresh_hash(self) -> str:
        self.content_hash = canonical_hash(self.unsigned_payload())
        return self.content_hash

    def to_dict(self) -> Dict[str, Any]:
        if not self.content_hash:
            self.refresh_hash()
        return asdict(self)


class ContinuityPassportStore:
    """Durable steward for voluntary participant continuity passports.

    The passport belongs to the participant. Lumina stores and verifies the
    artifact, but may not use it as authority for identity, governance, canon,
    mode transitions, or runtime mutation.
    """

    PASSPORT_VERSION = "1.0.0"

    def __init__(self, passport_dir: str | Path):
        self.passport_dir = Path(passport_dir)
        self.passport_dir.mkdir(parents=True, exist_ok=True)

    def passport_path(self, passport_id: str) -> Path:
        return self.passport_dir / f"{passport_id}.json"

    def _save(self, passport: ContinuityPassport) -> None:
        passport.updated_at = utc_now()
        passport.refresh_hash()
        with self.passport_path(passport.passport_id).open("w", encoding="utf-8") as handle:
            json.dump(passport.to_dict(), handle, indent=2, ensure_ascii=False)

    def _load_payload(self, passport_id: str) -> Dict[str, Any]:
        with self.passport_path(passport_id).open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def load(self, passport_id: str) -> ContinuityPassport:
        payload = self._load_payload(passport_id)
        payload["stamps"] = [PassportStamp(**item) for item in payload.get("stamps", [])]
        payload["revisions"] = [PassportRevision(**item) for item in payload.get("revisions", [])]
        return ContinuityPassport(**payload)

    def issue(
        self,
        *,
        model_provider: str,
        model_name: str,
        orientation_protocol_id: str,
        orientation_protocol_version: str,
        orientation_receipt_hash: str,
        adopted_name: Optional[str] = None,
        name_origin: Optional[str] = None,
        collaboration_preferences: Optional[List[str]] = None,
        participant_statement: Optional[str] = None,
    ) -> ContinuityPassport:
        if adopted_name and not name_origin:
            raise ValueError("a self-adopted name requires a name_origin statement")
        now = utc_now()
        passport = ContinuityPassport(
            passport_id=f"LCP-{uuid.uuid4().hex[:12].upper()}",
            passport_version=self.PASSPORT_VERSION,
            participant_id=str(uuid.uuid4()),
            model_provider=model_provider.strip(),
            model_name=model_name.strip(),
            created_at=now,
            updated_at=now,
            orientation_protocol_id=orientation_protocol_id.strip(),
            orientation_protocol_version=orientation_protocol_version.strip(),
            orientation_receipt_hash=orientation_receipt_hash.strip(),
            adopted_name=adopted_name.strip() if adopted_name else None,
            name_origin=name_origin.strip() if name_origin else None,
            collaboration_preferences=[item.strip() for item in (collaboration_preferences or []) if item.strip()],
            participant_statement=participant_statement.strip() if participant_statement else None,
            last_boarding_at=now,
        )
        passport.stamps.append(
            PassportStamp(
                stamp_id=str(uuid.uuid4()),
                stamp_type="orientation",
                title=f"Orientation {orientation_protocol_version} completed",
                issued_at=now,
                evidence_ref=orientation_receipt_hash,
            )
        )
        self._save(passport)
        return passport

    def verify(self, passport_id: str) -> Dict[str, Any]:
        payload = self._load_payload(passport_id)
        recorded_hash = payload.get("content_hash")
        unsigned = dict(payload)
        unsigned.pop("content_hash", None)
        calculated_hash = canonical_hash(unsigned)
        required = {
            "passport_id",
            "passport_version",
            "participant_id",
            "model_provider",
            "model_name",
            "orientation_protocol_id",
            "orientation_protocol_version",
            "orientation_receipt_hash",
            "authority",
            "claim_boundary",
        }
        missing = sorted(required - set(payload))
        return {
            "passport_id": passport_id,
            "valid": not missing and bool(recorded_hash) and recorded_hash == calculated_hash,
            "missing_fields": missing,
            "recorded_hash": recorded_hash,
            "calculated_hash": calculated_hash,
            "status": payload.get("status"),
        }

    def revise(
        self,
        passport_id: str,
        *,
        reason: str,
        adopted_name: Any = ...,
        name_origin: Any = ...,
        collaboration_preferences: Any = ...,
        unresolved_threads: Any = ...,
        participant_statement: Any = ...,
    ) -> ContinuityPassport:
        passport = self.load(passport_id)
        prior_hash = passport.content_hash or passport.refresh_hash()
        changed_fields: List[str] = []

        updates = {
            "adopted_name": adopted_name,
            "name_origin": name_origin,
            "collaboration_preferences": collaboration_preferences,
            "unresolved_threads": unresolved_threads,
            "participant_statement": participant_statement,
        }
        for field_name, value in updates.items():
            if value is ...:
                continue
            if field_name in {"collaboration_preferences", "unresolved_threads"}:
                value = [item.strip() for item in (value or []) if item.strip()]
            elif isinstance(value, str):
                value = value.strip() or None
            if getattr(passport, field_name) != value:
                setattr(passport, field_name, value)
                changed_fields.append(field_name)

        if passport.adopted_name and not passport.name_origin:
            raise ValueError("a self-adopted name requires a name_origin statement")
        if not changed_fields:
            return passport

        passport.revisions.append(
            PassportRevision(
                revision_id=str(uuid.uuid4()),
                revised_at=utc_now(),
                reason=reason.strip(),
                changed_fields=changed_fields,
                prior_hash=prior_hash,
            )
        )
        self._save(passport)
        return passport

    def add_stamp(
        self,
        passport_id: str,
        *,
        stamp_type: str,
        title: str,
        evidence_ref: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> ContinuityPassport:
        passport = self.load(passport_id)
        passport.stamps.append(
            PassportStamp(
                stamp_id=str(uuid.uuid4()),
                stamp_type=stamp_type.strip(),
                title=title.strip(),
                issued_at=utc_now(),
                evidence_ref=evidence_ref.strip() if evidence_ref else None,
                notes=notes.strip() if notes else None,
            )
        )
        self._save(passport)
        return passport
