"""Resident Intention Origin R1.

Accepts a bounded reflection artifact from an already-running resident cognitive
turn and, only when that artifact explicitly chooses a future return, persists
its reason as a Resident Intention.

The module does not generate reflection itself and does not infer desire from
silence, salience, timers, or operator requests.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
from typing import Any

try:
    from .resident_intention_store_r1 import ResidentIntentionStore
except ImportError:
    from resident_intention_store_r1 import ResidentIntentionStore


REQUIRED_REFLECTION_FIELDS = {
    "schema_version",
    "resident",
    "session_id",
    "reflection_id",
    "observed_context",
    "unresolved_tension",
    "choose_future_return",
    "why_return",
    "desired_next_action",
    "evidence_refs",
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class IntentionOriginResult:
    created: bool
    decision_reason: str
    reflection_hash: str
    intention_receipt: dict[str, Any] | None
    boundary: str = (
        "Evidence of model/runtime-originated intention content within a bounded "
        "resident turn; not identity authentication or proof of phenomenal desire."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "created": self.created,
            "decision_reason": self.decision_reason,
            "reflection_hash": self.reflection_hash,
            "intention_receipt": self.intention_receipt,
            "boundary": self.boundary,
        }


class ResidentIntentionOrigin:
    def __init__(self, *, base_dir: str | Path):
        self.store = ResidentIntentionStore(Path(base_dir) / "resident_intentions")

    @staticmethod
    def validate(reflection: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(reflection, dict) or set(reflection) != REQUIRED_REFLECTION_FIELDS:
            raise ValueError("invalid resident reflection fields")
        if reflection["schema_version"] != "resident-reflection-r1":
            raise ValueError("unsupported resident reflection schema")
        for field in (
            "resident", "session_id", "reflection_id", "observed_context",
            "unresolved_tension", "why_return", "desired_next_action",
        ):
            if not isinstance(reflection[field], str):
                raise ValueError(f"{field} must be text")
        if not reflection["resident"].strip() or not reflection["session_id"].strip() or not reflection["reflection_id"].strip():
            raise ValueError("resident/session/reflection identifiers are required")
        if type(reflection["choose_future_return"]) is not bool:
            raise ValueError("choose_future_return must be boolean")
        refs = reflection["evidence_refs"]
        if not isinstance(refs, list) or not refs or any(not isinstance(r, str) or not r.strip() for r in refs):
            raise ValueError("evidence_refs must contain nonempty references")
        if reflection["choose_future_return"]:
            for field in ("unresolved_tension", "why_return", "desired_next_action"):
                if not reflection[field].strip():
                    raise ValueError(f"{field} is required when choosing a future return")
        return dict(reflection)

    def persist(self, reflection: dict[str, Any]) -> IntentionOriginResult:
        reflection = self.validate(reflection)
        reflection_hash = digest(reflection)
        if not reflection["choose_future_return"]:
            return IntentionOriginResult(
                created=False,
                decision_reason="resident_reflection_declined_future_return",
                reflection_hash=reflection_hash,
                intention_receipt=None,
            )

        resident = reflection["resident"].strip()
        receipt = self.store.create(
            {
                "intention_id": "origin-" + reflection_hash[:24],
                "resident": resident,
                "origin_context": reflection["observed_context"].strip(),
                "statement": reflection["unresolved_tension"].strip(),
                "why_it_matters": reflection["why_return"].strip(),
                "desired_next_action": reflection["desired_next_action"].strip(),
                "parent_intention_id": None,
                "evidence_refs": [
                    *reflection["evidence_refs"],
                    "resident-reflection-sha256:" + reflection_hash,
                ],
            },
            {
                "actor_kind": "resident",
                "resident": resident,
                "session_id": reflection["session_id"].strip(),
                "source_ref": "resident-reflection:" + reflection["reflection_id"].strip(),
            },
        )
        return IntentionOriginResult(
            created=True,
            decision_reason="resident_reflection_chose_future_return",
            reflection_hash=reflection_hash,
            intention_receipt=receipt,
        )
