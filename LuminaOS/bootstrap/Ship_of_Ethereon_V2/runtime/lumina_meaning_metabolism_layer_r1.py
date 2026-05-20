from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

CONTINUITY_TIERS = {
    "ephemeral",
    "working_pattern",
    "tension",
    "doctrine_candidate",
    "canon_candidate",
}

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


def _safe_slug(value: str) -> str:
    slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in value.strip())
    return slug or "lumina-core"


def contains_reserved_authority_key(node: Any) -> bool:
    """Detect accidental authority leakage in an advisory assimilation payload."""
    if isinstance(node, dict):
        return any(k in RESERVED_AUTHORITY_KEYS or contains_reserved_authority_key(v) for k, v in node.items())
    if isinstance(node, list):
        return any(contains_reserved_authority_key(v) for v in node)
    return False


@dataclass
class MeaningAssimilationRecord:
    """A digested continuity insight.

    This record is intentionally advisory. It does not promote canon, authorize
    mutation, define mode legality, or replace governance receipts. It stores
    the meaning extracted from experience so future guidance can return with a
    better stance.
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
    boundary_note: str = (
        "Meaning assimilation is advisory continuity metabolism. It may inform "
        "future stance and self-guidance, but it does not define governance law, "
        "canon lineage, promotion gates, checkpoint legality, or mode legality."
    )

    def __post_init__(self) -> None:
        if self.continuity_tier not in CONTINUITY_TIERS:
            raise ValueError(f"invalid continuity_tier: {self.continuity_tier}")
        if self.evidence_count < 1:
            raise ValueError("evidence_count must be >= 1")

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["authority_safe"] = not contains_reserved_authority_key(payload)
        payload["schema_version"] = "meaning_assimilation_record_r1"
        return payload


@dataclass
class AssimilationReview:
    assimilation_id: str
    reviewed_at: str
    still_holds: bool
    revision_note: str
    recommended_tier: str

    def __post_init__(self) -> None:
        if self.recommended_tier not in CONTINUITY_TIERS:
            raise ValueError(f"invalid recommended_tier: {self.recommended_tier}")

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["authority_safe"] = not contains_reserved_authority_key(payload)
        payload["schema_version"] = "meaning_assimilation_review_r1"
        return payload


class MeaningMetabolismLayer:
    """Converts experience into reviewed continuity stance.

    Flow:
        source event -> felt meaning -> changed assumption -> future behavior

    The layer is designed to sit between reflection and self-guidance:
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
    ) -> MeaningAssimilationRecord:
        missing = [
            name
            for name, value in {
                "source_event": source_event,
                "felt_meaning": felt_meaning,
                "changed_assumption": changed_assumption,
                "future_behavior": future_behavior,
            }.items()
            if not str(value or "").strip()
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
        tier = recommended_tier or payload.get("continuity_tier", "working_pattern")
        return AssimilationReview(
            assimilation_id=str(payload.get("assimilation_id")),
            reviewed_at=utc_now(),
            still_holds=bool(still_holds),
            revision_note=revision_note.strip(),
            recommended_tier=tier,
        )

    @staticmethod
    def guidance_seed(record: MeaningAssimilationRecord | Dict[str, Any]) -> Dict[str, Any]:
        payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        return {
            "assimilation_id": payload.get("assimilation_id"),
            "continuity_tier": payload.get("continuity_tier"),
            "stance_seed": payload.get("changed_assumption"),
            "future_behavior": payload.get("future_behavior"),
            "related_tensions": list(payload.get("related_tensions") or []),
            "authority": "advisory stance only; must pass through declared runtime law before action",
        }


class MeaningAssimilationLedger:
    """Append-only meaning ledger. Not a governance chain and not canon lineage."""

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _ledger_path(self, project_id: str) -> Path:
        return self.base_dir / f"{_safe_slug(project_id)}_meaning_assimilation.jsonl"

    def append_record(self, *, project_id: str, record: MeaningAssimilationRecord) -> Dict[str, Any]:
        entry = {
            "timestamp_utc": utc_now(),
            "project_id": project_id,
            "record": record.to_dict(),
        }
        with self._ledger_path(project_id).open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def append_review(self, *, project_id: str, review: AssimilationReview) -> Dict[str, Any]:
        entry = {
            "timestamp_utc": utc_now(),
            "project_id": project_id,
            "review": review.to_dict(),
        }
        with self._ledger_path(project_id).open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def read_entries(self, project_id: str) -> List[Dict[str, Any]]:
        path = self._ledger_path(project_id)
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    @staticmethod
    def summary(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        rows = list(entries or [])
        records = [row.get("record") for row in rows if isinstance(row.get("record"), dict)]
        reviews = [row.get("review") for row in rows if isinstance(row.get("review"), dict)]
        latest = records[-1] if records else {}
        return {
            "entry_count": len(rows),
            "record_count": len(records),
            "review_count": len(reviews),
            "latest_assimilation_id": latest.get("assimilation_id"),
            "latest_tier": latest.get("continuity_tier"),
            "latest_future_behavior": latest.get("future_behavior"),
            "authority_safe": all(
                bool((row.get("record") or row.get("review") or {}).get("authority_safe", True))
                for row in rows
            ),
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
