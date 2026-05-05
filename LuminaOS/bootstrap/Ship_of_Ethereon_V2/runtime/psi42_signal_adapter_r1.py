from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, Optional


@dataclass
class Psi42SignalReceipt:
    schema_version: str
    created_at_utc: str
    phase: str
    signal_id: str
    input_digest: str
    context_digest: str
    alignment_score: float
    drift_score: float
    notes: Dict[str, Any]
    authority_boundary: str = (
        "signal continuity telemetry only; does not authorize execution, mutation, promotion, "
        "mode transition, canon change, governance change, or capability exposure"
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Psi42SignalAdapter:
    """Bounded Lumina adapter for Psi-42 signal continuity.

    This adapter treats Psi-42 as telemetry: capture, alignment, drift, and emission receipts.
    It is intentionally descriptive, not interpretive or authoritative.
    """

    schema_version = "psi42_signal_adapter_r1"

    @staticmethod
    def _digest(payload: Any) -> str:
        encoded = repr(payload).encode("utf-8")
        return sha256(encoded).hexdigest()

    @staticmethod
    def _bounded_ratio(a: int, b: int) -> float:
        if max(a, b) == 0:
            return 1.0
        return round(min(a, b) / max(a, b), 4)

    def capture_signal(
        self,
        raw_input: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        previous_signal: Optional[Dict[str, Any]] = None,
    ) -> Psi42SignalReceipt:
        context = dict(context or {})
        input_digest = self._digest(raw_input)
        context_digest = self._digest(context)

        previous_digest = (previous_signal or {}).get("input_digest")
        drift_score = 0.0 if previous_digest == input_digest else 1.0 if previous_digest else 0.25
        alignment_score = self._bounded_ratio(len(raw_input), len(repr(context)))

        signal_id = self._digest({
            "phase": "capture",
            "input_digest": input_digest,
            "context_digest": context_digest,
            "created_at_hint": len(raw_input),
        })[:16]

        return Psi42SignalReceipt(
            schema_version=self.schema_version,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            phase="capture",
            signal_id=signal_id,
            input_digest=input_digest,
            context_digest=context_digest,
            alignment_score=alignment_score,
            drift_score=drift_score,
            notes={
                "context_keys": sorted(context.keys()),
                "previous_signal_present": previous_signal is not None,
                "telemetry_only": True,
            },
        )

    def emit_signal(
        self,
        output: str,
        *,
        capture_receipt: Psi42SignalReceipt,
        reflection: Optional[Dict[str, Any]] = None,
    ) -> Psi42SignalReceipt:
        reflection = dict(reflection or {})
        output_digest = self._digest(output)
        reflection_digest = self._digest(reflection)
        alignment_score = self._bounded_ratio(len(output), len(repr(reflection)) or 1)

        signal_id = self._digest({
            "phase": "emit",
            "capture_signal_id": capture_receipt.signal_id,
            "output_digest": output_digest,
            "reflection_digest": reflection_digest,
        })[:16]

        return Psi42SignalReceipt(
            schema_version=self.schema_version,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            phase="emit",
            signal_id=signal_id,
            input_digest=output_digest,
            context_digest=reflection_digest,
            alignment_score=alignment_score,
            drift_score=capture_receipt.drift_score,
            notes={
                "capture_signal_id": capture_receipt.signal_id,
                "reflection_present": bool(reflection),
                "telemetry_only": True,
            },
        )
