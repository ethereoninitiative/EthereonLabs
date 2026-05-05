from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from continuity_index_r1 import compute_continuity_index
from psi42_signal_adapter_r1 import Psi42SignalAdapter
from recursive_reflection_layer_r1 import RecursiveReflectionLayer


@dataclass
class LuminaRuntimeLoopReceipt:
    schema_version: str
    created_at_utc: str
    raw_input: str
    mode: str
    signal_capture: Dict[str, Any]
    reflection: Dict[str, Any]
    signal_emit: Dict[str, Any]
    continuity: Dict[str, Any]
    authority_boundary: str = (
        "runtime loop receipt only; diagnostic and advisory; does not authorize execution, mutation, "
        "promotion, mode transition, canon change, governance change, or capability exposure"
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaRuntimeLoop:
    """Callable runtime-facing loop receipt builder.

    This composes Psi-42 signal telemetry, recursive reflection, and continuity index into a
    single portable receipt that can be attached to a governed runtime cycle.
    """

    schema_version = "lumina_runtime_loop_receipt_r1"

    def __init__(self) -> None:
        self.psi42 = Psi42SignalAdapter()
        self.reflection_layer = RecursiveReflectionLayer()

    def build_receipt(
        self,
        raw_input: str,
        *,
        mode: str = "Observation",
        context: Optional[Dict[str, Any]] = None,
        output_hint: str = "processed",
        previous_signal: Optional[Dict[str, Any]] = None,
    ) -> LuminaRuntimeLoopReceipt:
        context = dict(context or {})
        capture = self.psi42.capture_signal(
            raw_input,
            context={"mode": mode, **context},
            previous_signal=previous_signal,
        )
        reflection = self.reflection_layer.reflect(
            raw_input,
            mode=mode,
            constraints=["no_overclaim"],
            prior_stance={
                "psi42_capture_alignment": capture.alignment_score,
                "psi42_capture_drift": capture.drift_score,
                "psi42_signal_id": capture.signal_id,
            },
        )
        emit = self.psi42.emit_signal(
            output_hint,
            capture_receipt=capture,
            reflection=reflection.to_dict(),
        )
        continuity = compute_continuity_index([capture.to_dict(), emit.to_dict()])
        return LuminaRuntimeLoopReceipt(
            schema_version=self.schema_version,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            raw_input=raw_input,
            mode=mode,
            signal_capture=capture.to_dict(),
            reflection=reflection.to_dict(),
            signal_emit=emit.to_dict(),
            continuity=continuity.to_dict(),
        )
