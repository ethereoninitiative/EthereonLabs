from __future__ import annotations

from typing import Any, Dict, Optional

from lumina_runtime_loop_receipt_r1 import LuminaRuntimeLoop
from runtime_loop_receipt_store_r1 import RuntimeLoopReceiptStore


class LuminaLiveLoopAdapter:
    """Runtime-facing adapter for live Lumina loop receipts.

    This connects the callable loop and persistent store without granting execution authority.
    It is intended to be invoked by runtime_runner after input integrity has completed.
    """

    schema_version = "lumina_live_loop_adapter_r1"

    def __init__(self, store_base_path: Optional[str] = None) -> None:
        self.loop = LuminaRuntimeLoop()
        self.store = RuntimeLoopReceiptStore(base_path=store_base_path)

    def process_cycle(
        self,
        raw_input: str,
        *,
        mode: str = "Observation",
        context: Optional[Dict[str, Any]] = None,
        output_hint: str = "processed",
        persist: bool = True,
    ) -> Dict[str, Any]:
        previous_signal = self.store.load_previous_signal()
        receipt = self.loop.build_receipt(
            raw_input,
            mode=mode,
            context=context or {},
            output_hint=output_hint,
            previous_signal=previous_signal,
        ).to_dict()

        live_snapshot = {
            "schema_version": self.schema_version,
            "authority_boundary": "diagnostic/advisory only; runtime remains authority",
            "receipt": receipt,
            "previous_signal_present": previous_signal is not None,
        }

        if persist:
            self.store.append_receipt(receipt)

        return live_snapshot
