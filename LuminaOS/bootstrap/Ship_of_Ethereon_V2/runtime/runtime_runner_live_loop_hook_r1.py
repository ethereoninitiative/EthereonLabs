from __future__ import annotations

from typing import Any, Dict, Optional

from lumina_live_loop_adapter_r1 import LuminaLiveLoopAdapter


class RuntimeRunnerLiveLoopHook:
    """Minimal hook for attaching Lumina live-loop diagnostics to a runner cycle.

    Intended placement:
    - after input integrity has completed
    - before runtime authority decisions are finalized

    Boundary:
    - diagnostic/advisory only
    - does not authorize execution
    - does not mutate governance
    """

    schema_version = "runtime_runner_live_loop_hook_r1"

    def __init__(self, store_base_path: Optional[str] = None) -> None:
        self.live_loop = LuminaLiveLoopAdapter(store_base_path=store_base_path)

    def build_diagnostic(
        self,
        raw_input: str,
        *,
        mode: str = "Observation",
        context: Optional[Dict[str, Any]] = None,
        output_hint: str = "processed",
    ) -> Dict[str, Any]:
        snapshot = self.live_loop.process_cycle(
            raw_input,
            mode=mode,
            context=context or {},
            output_hint=output_hint,
            persist=True,
        )
        return {
            "schema_version": self.schema_version,
            "authority_boundary": "diagnostic/advisory only; runner remains authority",
            "lumina_live_loop": snapshot,
        }
