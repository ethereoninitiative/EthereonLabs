from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    from .runtime_truth_emitter_r1 import RuntimeTruthEmitter
except Exception:
    from runtime_truth_emitter_r1 import RuntimeTruthEmitter

try:
    from .repo_paths_r1 import repo_root as _repo_root_helper, runtime_root as _runtime_root_helper, state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import repo_root as _repo_root_helper, runtime_root as _runtime_root_helper, state_root as _state_root_helper
    except Exception:
        _repo_root_helper = None
        _runtime_root_helper = None
        _state_root_helper = None


def infer_runtime_root() -> Path:
    if _runtime_root_helper is not None:
        try:
            candidate = Path(_runtime_root_helper()).resolve()
            if candidate.exists():
                return candidate
        except Exception:
            pass
    return Path(__file__).resolve().parent


def infer_repo_root() -> Path:
    if _repo_root_helper is not None:
        try:
            candidate = Path(_repo_root_helper()).resolve()
            if candidate.exists():
                return candidate
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "public").exists() or (parent / "LuminaOS").exists():
            return parent
    return infer_runtime_root()


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        try:
            candidate = Path(_state_root_helper()).resolve()
            if candidate.exists() or candidate.parent.exists():
                return candidate
        except Exception:
            pass
    return infer_repo_root() / ".lumina_state" / "ship_of_ethereon_v2"


RUNTIME_ROOT = infer_runtime_root()
REPO_ROOT = infer_repo_root()
STATE_ROOT = infer_state_root()
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
