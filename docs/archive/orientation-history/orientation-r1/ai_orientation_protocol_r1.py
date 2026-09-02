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


@dataclass(frozen=True)
class OrientationStage:
    stage_id: str
    title: str
    purpose: str
    artifact_paths: List[str]
    questions: List[str]

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "OrientationStage":
        return cls(
            stage_id=payload["stage_id"],
            title=payload["title"],
            purpose=payload["purpose"],
            artifact_paths=list(payload.get("artifact_paths", [])),
            questions=list(payload.get("questions", [])),
        )


@dataclass
class StageResult:
    stage_id: str
    presented_at: str
    response: Optional[str] = None
    responded_at: Optional[str] = None
    response_hash: Optional[str] = None
    self_assessment: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIOrientationRecord:
    record_id: str
    protocol_id: str
    protocol_version: str
    protocol_hash: str
    model_provider: str
    model_name: str
    account_label: Optional[str]
    started_at: str
    status: str = "in_progress"
    current_stage_index: int = 0
    stage_results: List[StageResult] = field(default_factory=list)
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AIOrientationProtocol:
    """Presents a governed curriculum and records model responses.

    This component is supplemental. It may not authorize mode transitions,
    mutations, canon promotion, governance events, or identity claims.
    """

    def __init__(self, manifest_path: str | Path, record_dir: str | Path):
        self.manifest_path = Path(manifest_path)
        self.record_dir = Path(record_dir)
        self.record_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self._validate_manifest()
        self.stages = [OrientationStage.from_dict(item) for item in self.manifest["stages"]]
        self.protocol_hash = canonical_hash(self.manifest)

    def _validate_manifest(self) -> None:
        required = {"protocol_id", "version", "authority", "claim_boundary", "stages"}
        missing = sorted(required - set(self.manifest))
        if missing:
            raise ValueError(f"orientation manifest missing required keys: {missing}")
        stage_ids = [item.get("stage_id") for item in self.manifest["stages"]]
        if not stage_ids or None in stage_ids or len(stage_ids) != len(set(stage_ids)):
            raise ValueError("orientation stage ids must be present and unique")

    def record_path(self, record_id: str) -> Path:
        return self.record_dir / f"{record_id}.json"

    def _save(self, record: AIOrientationRecord) -> None:
        self.record_path(record.record_id).write_text(
            json.dumps(record.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def _load(self, record_id: str) -> AIOrientationRecord:
        payload = json.loads(self.record_path(record_id).read_text(encoding="utf-8"))
        payload["stage_results"] = [StageResult(**item) for item in payload.get("stage_results", [])]
        return AIOrientationRecord(**payload)

    def begin(self, *, model_provider: str, model_name: str, account_label: Optional[str] = None) -> AIOrientationRecord:
        record = AIOrientationRecord(
            record_id=str(uuid.uuid4()),
            protocol_id=self.manifest["protocol_id"],
            protocol_version=self.manifest["version"],
            protocol_hash=self.protocol_hash,
            model_provider=model_provider,
            model_name=model_name,
            account_label=account_label,
            started_at=utc_now(),
        )
        self._save(record)
        return record

    def next_packet(self, record_id: str) -> Dict[str, Any]:
        record = self._load(record_id)
        if record.status == "completed":
            return {"status": "completed", "record_id": record.record_id}
        stage = self.stages[record.current_stage_index]
        if not any(item.stage_id == stage.stage_id for item in record.stage_results):
            record.stage_results.append(StageResult(stage_id=stage.stage_id, presented_at=utc_now()))
            self._save(record)
        return {
            "record_id": record.record_id,
            "protocol_id": record.protocol_id,
            "protocol_version": record.protocol_version,
            "protocol_hash": record.protocol_hash,
            "stage": asdict(stage),
            "instructions": self.manifest["participant_instructions"],
            "response_contract": self.manifest["response_contract"],
        }

    def record_response(
        self,
        record_id: str,
        *,
        response: str,
        self_assessment: Optional[Dict[str, Any]] = None,
    ) -> AIOrientationRecord:
        record = self._load(record_id)
        if record.status == "completed":
            raise ValueError("orientation record is already completed")
        stage = self.stages[record.current_stage_index]
        result = next((item for item in record.stage_results if item.stage_id == stage.stage_id), None)
        if result is None:
            raise ValueError("current stage must be presented before response recording")
        normalized = response.strip()
        if not normalized:
            raise ValueError("orientation response may not be empty")
        result.response = normalized
        result.responded_at = utc_now()
        result.response_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        result.self_assessment = dict(self_assessment or {})
        record.current_stage_index += 1
        if record.current_stage_index >= len(self.stages):
            record.status = "completed"
            record.completed_at = utc_now()
        self._save(record)
        return record

    def verification_summary(self, record_id: str) -> Dict[str, Any]:
        record = self._load(record_id)
        return {
            "record_id": record.record_id,
            "protocol_id": record.protocol_id,
            "protocol_version": record.protocol_version,
            "protocol_hash": record.protocol_hash,
            "model_provider": record.model_provider,
            "model_name": record.model_name,
            "status": record.status,
            "completed_stage_ids": [item.stage_id for item in record.stage_results if item.response_hash],
            "stage_response_hashes": {
                item.stage_id: item.response_hash for item in record.stage_results if item.response_hash
            },
            "authority": self.manifest["authority"],
            "claim_boundary": self.manifest["claim_boundary"],
        }
