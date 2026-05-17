from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    from .runtime_truth_emitter_r1 import RuntimeTruthEmitter
except Exception:
    from runtime_truth_emitter_r1 import RuntimeTruthEmitter


RUNTIME_ROOT = Path(__file__).resolve().parent
REPO_ROOT = RUNTIME_ROOT.parents[3] if len(RUNTIME_ROOT.parents) >= 4 else RUNTIME_ROOT
STATE_ROOT = REPO_ROOT / ".lumina_state" / "ship_of_ethereon_v2"
TRUTH_OUTPUT_DIR = REPO_ROOT / "artifacts" / "runtime_truth" / "current"


def run_runtime_truth_observation_cycle(
    *,
    output_dir: Optional[str | Path] = None,
    governance_log_path: Optional[str | Path] = None,
    canon_lineage_path: Optional[str | Path] = None,
    protocol_path: Optional[str | Path] = None,
    capability_registry_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Run an Observation-only truth receipt generation cycle.

    This adapter wires the RuntimeTruthEmitter into a repeatable observation action.
    It does not mutate governance, canon lineage, mode legality, or capabilities.
    It writes audit receipts only.
    """
    emitter = RuntimeTruthEmitter(
        output_dir=output_dir or TRUTH_OUTPUT_DIR,
        governance_log_path=governance_log_path or STATE_ROOT / "runtime_runner_r2_actiontype_logging" / "governance_log_r2.jsonl",
        canon_lineage_path=canon_lineage_path or STATE_ROOT / "runtime_runner_r2_actiontype_logging" / "canon_lineage_r2.jsonl",
        protocol_path=protocol_path or RUNTIME_ROOT.parent / "protocols" / "Ethereon_Mode_Protocol_v1.3.json",
        capability_registry_path=capability_registry_path or RUNTIME_ROOT / "capability_registry_r1.json",
    )
    return emitter.emit_all()


if __name__ == "__main__":
    print(json.dumps(run_runtime_truth_observation_cycle(), indent=2))
