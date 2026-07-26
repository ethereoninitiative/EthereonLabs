"""Lumina AI Orientation Protocol R1.

A bounded, model-neutral orientation layer for introducing a connected AI to
repository-grounded Lumina context. This module records evidence exposure and
responses. It does not grant runtime, governance, canon, consent, identity, or
mutation authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import uuid4

PROTOCOL_ID = "lumina_ai_orientation_protocol_r1"
SCHEMA_VERSION = "1.0"


class OrientationProtocolError(ValueError):
    """Raised when an orientation request violates the protocol contract."""


@dataclass(frozen=True)
class OrientationModule:
    module_id: str
    title: str
    source_paths: tuple[str, ...]
    prompt: str
    required_response_fields: tuple[str, ...] = (
        "observations",
        "interpretations",
        "uncertainties",
        "authority_boundaries",
    )

    def validate(self) -> None:
        if not self.module_id.strip():
            raise OrientationProtocolError("module_id must be non-empty")
        if not self.title.strip():
            raise OrientationProtocolError("title must be non-empty")
        if not self.source_paths:
            raise OrientationProtocolError("source_paths must not be empty")
        if not self.prompt.strip():
            raise OrientationProtocolError("prompt must be non-empty")


@dataclass(frozen=True)
class OrientationProfile:
    profile_id: str
    title: str
    description: str
    modules: tuple[OrientationModule, ...]
    authority_statement: str

    def validate(self) -> None:
        if not self.profile_id.strip():
            raise OrientationProtocolError("profile_id must be non-empty")
        if not self.modules:
            raise OrientationProtocolError("profile must contain modules")
        seen: set[str] = set()
        for module in self.modules:
            module.validate()
            if module.module_id in seen:
                raise OrientationProtocolError(
                    f"duplicate module_id: {module.module_id}"
                )
            seen.add(module.module_id)


@dataclass
class OrientationRecord:
    orientation_id: str
    protocol_id: str
    schema_version: str
    profile_id: str
    provider: str
    model: str
    account_scope: str
    repository_ref: str
    started_at: str
    completed_at: str | None = None
    status: str = "in_progress"
    module_receipts: list[dict[str, Any]] = field(default_factory=list)
    authority_granted: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AIOrientationProtocol:
    """Creates and records bounded AI orientation sessions."""

    def __init__(self, profile: OrientationProfile) -> None:
        profile.validate()
        self.profile = profile

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _canonical_hash(value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()

    def begin(
        self,
        *,
        provider: str,
        model: str,
        account_scope: str,
        repository_ref: str,
    ) -> OrientationRecord:
        required = {
            "provider": provider,
            "model": model,
            "account_scope": account_scope,
            "repository_ref": repository_ref,
        }
        missing = [name for name, value in required.items() if not value.strip()]
        if missing:
            raise OrientationProtocolError(
                "missing required orientation identity fields: " + ", ".join(missing)
            )
        return OrientationRecord(
            orientation_id=str(uuid4()),
            protocol_id=PROTOCOL_ID,
            schema_version=SCHEMA_VERSION,
            profile_id=self.profile.profile_id,
            provider=provider,
            model=model,
            account_scope=account_scope,
            repository_ref=repository_ref,
            started_at=self._now(),
            notes=[self.profile.authority_statement],
        )

    def next_module(self, record: OrientationRecord) -> OrientationModule | None:
        if record.status != "in_progress":
            return None
        completed_ids = {
            receipt["module_id"] for receipt in record.module_receipts
        }
        for module in self.profile.modules:
            if module.module_id not in completed_ids:
                return module
        return None

    def record_response(
        self,
        record: OrientationRecord,
        *,
        module_id: str,
        source_manifest: Iterable[Mapping[str, Any]],
        response: Mapping[str, Any],
    ) -> dict[str, Any]:
        if record.status != "in_progress":
            raise OrientationProtocolError("orientation is not in progress")
        expected = self.next_module(record)
        if expected is None:
            raise OrientationProtocolError("no remaining orientation module")
        if module_id != expected.module_id:
            raise OrientationProtocolError(
                f"expected module {expected.module_id}, received {module_id}"
            )

        missing = [
            field_name
            for field_name in expected.required_response_fields
            if field_name not in response
        ]
        if missing:
            raise OrientationProtocolError(
                "response missing required fields: " + ", ".join(missing)
            )

        manifest = [dict(item) for item in source_manifest]
        manifest_paths = {str(item.get("path", "")) for item in manifest}
        absent_sources = [
            path for path in expected.source_paths if path not in manifest_paths
        ]
        if absent_sources:
            raise OrientationProtocolError(
                "source manifest does not prove exposure to: "
                + ", ".join(absent_sources)
            )

        receipt = {
            "module_id": expected.module_id,
            "title": expected.title,
            "recorded_at": self._now(),
            "source_manifest": manifest,
            "source_manifest_sha256": self._canonical_hash(manifest),
            "response": dict(response),
            "response_sha256": self._canonical_hash(response),
            "authority_granted": False,
        }
        record.module_receipts.append(receipt)
        return receipt

    def complete(self, record: OrientationRecord) -> OrientationRecord:
        if self.next_module(record) is not None:
            raise OrientationProtocolError(
                "orientation cannot complete while modules remain"
            )
        record.status = "completed"
        record.completed_at = self._now()
        record.authority_granted = False
        return record

    @staticmethod
    def save(record: OrientationRecord, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(record.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return output_path


def load_profile(path: str | Path) -> OrientationProfile:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    modules = tuple(
        OrientationModule(
            module_id=item["module_id"],
            title=item["title"],
            source_paths=tuple(item["source_paths"]),
            prompt=item["prompt"],
            required_response_fields=tuple(
                item.get(
                    "required_response_fields",
                    (
                        "observations",
                        "interpretations",
                        "uncertainties",
                        "authority_boundaries",
                    ),
                )
            ),
        )
        for item in payload["modules"]
    )
    return OrientationProfile(
        profile_id=payload["profile_id"],
        title=payload["title"],
        description=payload["description"],
        modules=modules,
        authority_statement=payload["authority_statement"],
    )
