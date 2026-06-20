from __future__ import annotations

"""Living Framework Ignition R1.

Detects when an active interpretive framework begins recursively observing its
own response under contact with a subject or environmental field. Ignition is
descriptive and non-governing; it never authorizes runtime action.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import hashlib
import json


FRAMEWORK_DEPTH_STATES = ("dormant", "active", "ignited")
DEEPENING_PASS_IDS = (
    "perspective_inversion",
    "continuity_comparison",
    "counterpoint",
)
IGNITION_TRIGGER = "self_observation_under_contact"
AUTHORITY_BOUNDARY = (
    "Ignition describes recursive interpretive depth only. It may unlock deeper "
    "framework passes, but may not authorize actions, alter governance law, "
    "promote canon, validate checkpoints, define mode legality, or expose capabilities."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class IgnitionEvidence:
    self_observation: bool
    perspective_inversion: bool = False
    assumption_revealed: bool = False
    orientation_changed: bool = False
    new_internal_relations: List[List[str]] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    observed_at: str = field(default_factory=utc_now)

    def reinforcing_signals(self) -> List[str]:
        signals: List[str] = []
        if self.perspective_inversion:
            signals.append("perspective_inversion")
        if self.assumption_revealed:
            signals.append("assumption_revealed")
        if self.orientation_changed:
            signals.append("orientation_changed")
        if self.new_internal_relations:
            signals.append("new_internal_relation")
        return signals

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IgnitionReceipt:
    schema_version: str
    activation_id: str
    framework_id: str
    correlation_id: Optional[str]
    catalyst: str
    state_before: str
    state_after: str
    ignition_detected: bool
    trigger: Optional[str]
    ignition_pass: Optional[str]
    reinforcing_signals: List[str]
    revealed_relations: List[List[str]]
    deepening_passes: List[str]
    evidence: Dict[str, Any]
    authority_boundary: str
    receipt_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IgnitionReceiptStore:
    """Persists one atomic ignition receipt per chamber activation."""

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, receipt: IgnitionReceipt) -> Path:
        path = self.base_dir / f"{receipt.activation_id}__ignition.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(receipt.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(path)
        return path


class LivingFrameworkIgnition:
    """Evaluate self-reflective ignition for an existing chamber activation."""

    @staticmethod
    def dormant_state(framework_id: str) -> Dict[str, Any]:
        return {
            "framework_id": framework_id,
            "depth_state": "dormant",
            "ignition_detected": False,
            "authority_boundary": AUTHORITY_BOUNDARY,
        }

    @staticmethod
    def _payload(chamber_result: Any) -> Dict[str, Any]:
        if hasattr(chamber_result, "to_dict"):
            payload = chamber_result.to_dict()
        else:
            payload = dict(chamber_result)
        if not isinstance(payload.get("activation"), dict):
            raise ValueError("chamber_result must contain an activation object")
        return payload

    @staticmethod
    def _select_ignition_pass(
        *,
        available_passes: Iterable[str],
        evidence: IgnitionEvidence,
        requested_pass: Optional[str],
    ) -> Optional[str]:
        available = list(available_passes)
        if requested_pass is not None:
            if requested_pass not in available:
                raise ValueError(f"ignition_pass is not present in the chamber plan: {requested_pass}")
            return requested_pass
        if evidence.perspective_inversion and "perspective_inversion" in available:
            return "perspective_inversion"
        if (evidence.orientation_changed or evidence.new_internal_relations) and "continuity_comparison" in available:
            return "continuity_comparison"
        if evidence.assumption_revealed and "counterpoint" in available:
            return "counterpoint"
        return available[0] if available else None

    def evaluate(
        self,
        chamber_result: Any,
        *,
        evidence: IgnitionEvidence,
        ignition_pass: Optional[str] = None,
    ) -> IgnitionReceipt:
        payload = self._payload(chamber_result)
        activation = payload["activation"]
        framework = payload.get("framework") or {}
        plan = payload.get("refraction_plan") or []
        planned_passes = [
            str(row.get("pass_id"))
            for row in plan
            if isinstance(row, dict) and row.get("pass_id")
        ]
        available_deepening = [
            pass_id for pass_id in DEEPENING_PASS_IDS if pass_id in planned_passes
        ]
        reinforcing = evidence.reinforcing_signals()

        # Self-observation is the required spark. A reinforcing structural effect
        # must also be present so evocative language alone cannot claim ignition.
        ignited = evidence.self_observation and bool(reinforcing)
        selected_pass = (
            self._select_ignition_pass(
                available_passes=available_deepening,
                evidence=evidence,
                requested_pass=ignition_pass,
            )
            if ignited
            else None
        )
        catalyst = str(
            activation.get("environmental_field")
            or activation.get("subject")
            or "unspecified-contact"
        )
        unhashed = {
            "schema_version": "living-framework-ignition-r1",
            "activation_id": str(activation.get("activation_id")),
            "framework_id": str(
                activation.get("framework_id")
                or framework.get("framework_id")
                or "unknown-framework"
            ),
            "correlation_id": (
                str(activation["correlation_id"])
                if activation.get("correlation_id")
                else None
            ),
            "catalyst": catalyst,
            "state_before": "active",
            "state_after": "ignited" if ignited else "active",
            "ignition_detected": ignited,
            "trigger": IGNITION_TRIGGER if ignited else None,
            "ignition_pass": selected_pass,
            "reinforcing_signals": reinforcing,
            "revealed_relations": [
                [str(part) for part in relation]
                for relation in evidence.new_internal_relations
            ],
            "deepening_passes": available_deepening if ignited else [],
            "evidence": evidence.to_dict(),
            "authority_boundary": AUTHORITY_BOUNDARY,
        }
        return IgnitionReceipt(receipt_hash=canonical_hash(unhashed), **unhashed)
