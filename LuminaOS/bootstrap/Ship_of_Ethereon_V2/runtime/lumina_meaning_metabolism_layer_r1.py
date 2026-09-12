from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import hashlib
import os
import re

try:
    from .lumina_meaning_evidence_r1 import MAX_EVIDENCE_SOURCES, probe_evidence, validate_evidence
except ImportError:
    from lumina_meaning_evidence_r1 import MAX_EVIDENCE_SOURCES, probe_evidence, validate_evidence

CONTINUITY_TIERS = {
    "ephemeral",
    "working_pattern",
    "tension",
    "doctrine_candidate",
    "canon_candidate",
}
MAX_LEDGER_BYTES = 16 * 1024 * 1024

RESERVED_AUTHORITY_KEYS = {
    "governance",
    "canon_lineage",
    "mode_guard",
    "promotion",
    "transition",
    "record_hash",
    "validation_reference",
    "allowed",
    "checkpoint_legality",
    "mode_legality",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value):
        raise ValueError("project_id must be an explicit canonical ID (1-80 ASCII letters, digits, - or _)")
    return value


def _instant(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("review time must be ISO 8601 text")
    instant = datetime.fromisoformat(value)
    if len(value) == 10:
        instant = instant.replace(tzinfo=timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("timestamps require a timezone; date-only deadlines use UTC")
    return instant


def record_digest(payload: Dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _unique_object(pairs: List[Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def contains_reserved_authority_key(node: Any) -> bool:
    if isinstance(node, dict):
        return any(k in RESERVED_AUTHORITY_KEYS or contains_reserved_authority_key(v) for k, v in node.items())
    if isinstance(node, list):
        return any(contains_reserved_authority_key(v) for v in node)
    return False


@dataclass
class MeaningAssimilationRecord:
    """A digested continuity insight.

    Advisory only: this record does not promote canon, authorize mutation,
    define mode legality, or replace governance receipts.
    """

    assimilation_id: str
    source_event: str
    felt_meaning: str
    changed_assumption: str
    continuity_tier: str
    future_behavior: str
    related_tensions: List[str] = field(default_factory=list)
    recurrence_markers: List[str] = field(default_factory=list)
    evidence_count: int = 1
    review_after: Optional[str] = None
    source_reflection_trace_id: Optional[str] = None
    generated_at: str = field(default_factory=utc_now)
    status: str = "active_candidate"
    source_evidence: List[Dict[str, Any]] = field(default_factory=list)
    boundary_note: str = (
        "Meaning assimilation is advisory continuity metabolism. It may inform "
        "future stance and self-guidance, but it does not define governance law, "
        "canon lineage, promotion gates, checkpoint legality, or mode legality."
    )

    def __post_init__(self) -> None:
        for name in ("assimilation_id", "source_event", "felt_meaning", "changed_assumption", "future_behavior", "boundary_note"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be nonempty text")
        if self.continuity_tier not in CONTINUITY_TIERS:
            raise ValueError(f"invalid continuity_tier: {self.continuity_tier}")
        if type(self.evidence_count) is not int or self.evidence_count < 1:
            raise ValueError("evidence_count must be >= 1")
        if self.status not in {"active_candidate", "archived", "revoked"}:
            raise ValueError("invalid meaning status")
        for values in (self.related_tensions, self.recurrence_markers):
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                raise ValueError("tensions and recurrence markers must be lists of text")
        if not isinstance(self.source_evidence, list) or len(self.source_evidence) > MAX_EVIDENCE_SOURCES:
            raise ValueError("source_evidence must contain at most eight sources")
        for evidence in self.source_evidence:
            validate_evidence(evidence)
        _instant(self.generated_at)
        if self.review_after is not None:
            _instant(self.review_after)
        if self.source_reflection_trace_id is not None and not isinstance(self.source_reflection_trace_id, str):
            raise ValueError("source_reflection_trace_id must be text")

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["authority_safe"] = not contains_reserved_authority_key(payload)
        payload["schema_version"] = "meaning_assimilation_record_r2"
        return payload


@dataclass
class AssimilationReview:
    assimilation_id: str
    reviewed_at: str
    still_holds: bool
    revision_note: str
    recommended_tier: str
    source_record_digest: Optional[str] = None

    def __post_init__(self) -> None:
        if type(self.still_holds) is not bool:
            raise ValueError("still_holds must be a boolean")
        if not isinstance(self.assimilation_id, str) or not self.assimilation_id.strip():
            raise ValueError("review must identify its record")
        if not isinstance(self.revision_note, str) or not self.revision_note.strip():
            raise ValueError("review requires an evidence assessment or revocation reason")
        if self.recommended_tier not in CONTINUITY_TIERS:
            raise ValueError(f"invalid recommended_tier: {self.recommended_tier}")
        _instant(self.reviewed_at)
        if self.source_record_digest is not None and not re.fullmatch(r"[0-9a-f]{64}", self.source_record_digest):
            raise ValueError("invalid source record digest")

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["authority_safe"] = not contains_reserved_authority_key(payload)
        payload["schema_version"] = "meaning_assimilation_review_r2"
        return payload


class MeaningMetabolismLayer:
    """Converts experience into reviewed continuity stance.

    Intended location in the active path:
        return -> reflect -> assimilate -> recommend -> govern -> record
    """

    def assimilate(
        self,
        *,
        source_event: str,
        felt_meaning: str,
        changed_assumption: str,
        future_behavior: str,
        continuity_tier: str = "working_pattern",
        related_tensions: Optional[List[str]] = None,
        recurrence_markers: Optional[List[str]] = None,
        evidence_count: int = 1,
        review_after: Optional[str] = None,
        source_reflection_trace_id: Optional[str] = None,
        source_evidence: Optional[List[Dict[str, Any]]] = None,
    ) -> MeaningAssimilationRecord:
        missing = [
            name
            for name, value in {
                "source_event": source_event,
                "felt_meaning": felt_meaning,
                "changed_assumption": changed_assumption,
                "future_behavior": future_behavior,
            }.items()
            if not isinstance(value, str) or not value.strip()
        ]
        if missing:
            raise ValueError(f"meaning assimilation missing required fields: {', '.join(missing)}")
        if continuity_tier == "canon_candidate" and evidence_count < 3:
            raise ValueError("canon_candidate requires evidence_count >= 3 and later governed review")

        generated = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        return MeaningAssimilationRecord(
            assimilation_id=f"meaning-{generated}",
            source_event=source_event.strip(),
            felt_meaning=felt_meaning.strip(),
            changed_assumption=changed_assumption.strip(),
            continuity_tier=continuity_tier,
            future_behavior=future_behavior.strip(),
            related_tensions=list(related_tensions or []),
            recurrence_markers=list(recurrence_markers or []),
            evidence_count=evidence_count,
            review_after=review_after,
            source_reflection_trace_id=source_reflection_trace_id,
            source_evidence=list(source_evidence or []),
        )

    def review(
        self,
        *,
        record: MeaningAssimilationRecord | Dict[str, Any],
        still_holds: bool,
        revision_note: str,
        recommended_tier: Optional[str] = None,
    ) -> AssimilationReview:
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        if not isinstance(revision_note, str):
            raise ValueError("revision_note must be text")
        tier = recommended_tier or payload.get("continuity_tier", "working_pattern")
        return AssimilationReview(
            assimilation_id=str(payload.get("assimilation_id")),
            reviewed_at=utc_now(),
            still_holds=still_holds,
            revision_note=revision_note.strip(),
            recommended_tier=tier,
            source_record_digest=record_digest(payload),
        )

    @staticmethod
    def guidance_seed(record: MeaningAssimilationRecord | Dict[str, Any]) -> Dict[str, Any]:
        """Format a candidate; only ledger.recall can establish present eligibility."""
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        return {
            "assimilation_id": payload.get("assimilation_id"),
            "continuity_tier": payload.get("continuity_tier"),
            "stance_seed": payload.get("changed_assumption"),
            "future_behavior": payload.get("future_behavior"),
            "related_tensions": list(payload.get("related_tensions") or []),
            "authority": "advisory stance only; must pass through declared runtime law before action",
            "eligibility": "unchecked_candidate",
        }


def _decode(payload: Dict[str, Any], kind: str) -> None:
    cls = MeaningAssimilationRecord if kind == "record" else AssimilationReview
    prefix = "meaning_assimilation_record" if kind == "record" else "meaning_assimilation_review"
    if payload.get("schema_version") not in {prefix + "_r1", prefix + "_r2"}:
        raise ValueError(f"unsupported {kind} schema")
    if contains_reserved_authority_key(payload) or payload.get("authority_safe") is not True:
        raise ValueError(f"{kind} crosses the advisory boundary")
    names = {item.name for item in fields(cls)}
    if set(payload) - names - {"schema_version", "authority_safe"}:
        raise ValueError(f"unknown {kind} fields")
    cls(**{key: value for key, value in payload.items() if key in names})


def _replay(entries: List[Dict[str, Any]], project_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Ledger order is causal order. Wall-clock sorting cannot resurrect a record."""
    states: Dict[str, Dict[str, Any]] = {}
    scope = project_id
    for row in entries:
        if not isinstance(row, dict):
            raise ValueError("ledger entry must be an object")
        scope = scope or _project_id(row.get("project_id"))
        if row.get("project_id") != scope:
            raise ValueError("ledger project scope mismatch")
        kinds = [kind for kind in ("record", "review") if kind in row]
        if len(kinds) != 1 or set(row) != {"timestamp_utc", "project_id", kinds[0]}:
            raise ValueError("invalid ledger entry fields")
        _instant(row["timestamp_utc"])
        kind = kinds[0]
        payload = row[kind]
        if not isinstance(payload, dict):
            raise ValueError("record or review must be an object")
        _decode(payload, kind)
        identifier = payload["assimilation_id"]
        if kind == "record":
            if identifier in states:
                raise ValueError("duplicate assimilation ID")
            states[identifier] = {"record": payload, "review": None, "revoked": payload.get("status") == "revoked"}
        else:
            if identifier not in states:
                raise ValueError("review precedes or cannot find its record")
            state = states[identifier]
            digest = payload.get("source_record_digest")
            if digest is not None and digest != record_digest(state["record"]):
                raise ValueError("review does not match the preserved record")
            state["review"] = payload
            state["revoked"] = state["revoked"] or payload["still_holds"] is False
    return states


def recall_entries(entries: List[Dict[str, Any]], *, project_id: Optional[str] = None,
                   source_root: Optional[str | Path] = None, now: Optional[datetime] = None) -> Dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("recall time requires a timezone")
    result: Dict[str, Any] = {
        "schema_version": "meaning_recall_r1", "project_id": project_id,
        "status": "ready" if entries else "empty", "checked_at": now.isoformat(),
        "guidance_seeds": [], "withheld": [],
        "boundary": "Advisory candidates with matching source bytes; no truth, identity, consent, or action authorization is established.",
    }
    try:
        states = _replay(entries, project_id)
        for identifier, state in states.items():
            record, review = state["record"], state["review"]
            evidence = record.get("source_evidence", [])
            reason = None
            if state["revoked"]:
                reason = "revoked"
            elif record.get("status") != "active_candidate":
                reason = "inactive"
            elif not review or not review.get("source_record_digest"):
                reason = "review_required"
            elif record.get("review_after") and now >= _instant(record["review_after"]):
                reason = "review_due"
            elif not evidence:
                reason = "evidence_missing"
            elif source_root is None:
                reason = "source_root_required"
            else:
                for source in evidence:
                    status = probe_evidence(source, source_root)
                    if status != "source_matches":
                        reason = status
                        break
            if reason:
                result["withheld"].append({"assimilation_id": identifier, "reason": reason})
                continue
            seed = MeaningMetabolismLayer.guidance_seed(record)
            seed.update({
                "eligibility": "reviewed_source_matches",
                "continuity_tier": review["recommended_tier"],
                "source_record_digest": record_digest(record),
                "review_digest": record_digest(review),
                "reviewed_at": review["reviewed_at"],
                "evidence_digests": [source["sha256"] for source in evidence],
            })
            result["guidance_seeds"].append(seed)
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        result.update(status="invalid", guidance_seeds=[], withheld=[], error=str(exc))
    return result


class MeaningAssimilationLedger:
    """Preserved advisory history with a conservative current-guidance projection.

    Digests bind reviews to content, not to an authenticated reviewer. This local
    single-writer ledger is not a governance chain or a rollback detector.
    """

    def __init__(self, base_dir: str | Path, *, create: bool = True):
        self.base_dir = Path(base_dir)
        if create:
            self.base_dir.mkdir(parents=True, exist_ok=True)

    def _ledger_path(self, project_id: str) -> Path:
        return self.base_dir / f"{_project_id(project_id)}_meaning_assimilation.jsonl"

    def _append(self, project_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        entries = self.read_entries(project_id)
        _replay([*entries, entry], project_id)
        data = (json.dumps(entry, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        path = self._ledger_path(project_id)
        if (path.stat().st_size if path.exists() else 0) + len(data) > MAX_LEDGER_BYTES:
            raise ValueError("meaning ledger exceeds the 16 MiB read budget")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        with path.open("ab") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        return entry

    def append_record(self, *, project_id: str, record: MeaningAssimilationRecord) -> Dict[str, Any]:
        entry = {"timestamp_utc": utc_now(), "project_id": project_id, "record": record.to_dict()}
        return self._append(project_id, entry)

    def append_review(self, *, project_id: str, review: AssimilationReview) -> Dict[str, Any]:
        entry = {"timestamp_utc": utc_now(), "project_id": project_id, "review": review.to_dict()}
        return self._append(project_id, entry)

    def read_entries(self, project_id: str) -> List[Dict[str, Any]]:
        path = self._ledger_path(project_id)
        if not path.exists():
            return []
        with path.open("rb") as stream:
            data = stream.read(MAX_LEDGER_BYTES + 1)
        if len(data) > MAX_LEDGER_BYTES:
            raise ValueError("meaning ledger exceeds the 16 MiB read budget")
        if data and not data.endswith(b"\n"):
            raise ValueError("meaning ledger has an incomplete final entry")
        entries = [json.loads(line, object_pairs_hook=_unique_object) for line in data.decode("utf-8").splitlines() if line.strip()]
        _replay(entries, project_id)
        return entries

    def recall(self, project_id: str, *, source_root: Optional[str | Path] = None,
               now: Optional[datetime] = None) -> Dict[str, Any]:
        try:
            entries = self.read_entries(project_id)
        except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
            result = recall_entries([], project_id=project_id, now=now)
            result.update(status="invalid", error=str(exc))
            return result
        return recall_entries(entries, project_id=project_id, source_root=source_root, now=now)

    @staticmethod
    def summary(entries: List[Dict[str, Any]], *, source_root: Optional[str | Path] = None) -> Dict[str, Any]:
        rows = list(entries or [])
        records = [row["record"] for row in rows if isinstance(row, dict) and isinstance(row.get("record"), dict)]
        reviews = [row["review"] for row in rows if isinstance(row, dict) and isinstance(row.get("review"), dict)]
        recall = recall_entries(rows, source_root=source_root)
        latest = recall["guidance_seeds"][-1] if recall["guidance_seeds"] else {}
        return {
            "entry_count": len(rows),
            "record_count": len(records),
            "review_count": len(reviews),
            "latest_assimilation_id": latest.get("assimilation_id"),
            "latest_tier": latest.get("continuity_tier"),
            "latest_future_behavior": latest.get("future_behavior"),
            "latest_record_id": records[-1].get("assimilation_id") if records else None,
            "recall_status": recall["status"],
            "withheld": recall["withheld"],
            "authority_safe": recall["status"] != "invalid",
        }


if __name__ == "__main__":
    layer = MeaningMetabolismLayer()
    record = layer.assimilate(
        source_event="Continuity felt present but uneven across voice and project contexts.",
        felt_meaning="Continuity is recognizable pattern-return, not only stored facts.",
        changed_assumption="A system can preserve state yet still fail if stance, humor, and project orientation do not re-emerge.",
        future_behavior="When continuity drift is reported, inspect generic-response leakage, missing humor, missing project stance, and over-disclaimer behavior first.",
        continuity_tier="doctrine_candidate",
        related_tensions=["state_memory_vs_pattern_return", "governance_vs_presence"],
        recurrence_markers=["voice_mode_drift", "generic_answer_drift", "self_guided_return"],
        evidence_count=3,
        review_after="2026-08-01",
    )
    print(json.dumps(record.to_dict(), indent=2))
