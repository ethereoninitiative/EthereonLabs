from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import argparse
import json

try:
    from .runtime_spine_r1 import GovernanceLog
except Exception:
    from runtime_spine_r1 import GovernanceLog

try:
    from .repo_paths_r1 import state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import state_root as _state_root_helper
    except Exception:
        _state_root_helper = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        try:
            candidate = Path(_state_root_helper()).resolve()
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            root = parent / ".lumina_state" / "ship_of_ethereon_v2"
            root.mkdir(parents=True, exist_ok=True)
            return root
    root = Path(__file__).resolve().parent / "_runtime_state" / "ship_of_ethereon_v2"
    root.mkdir(parents=True, exist_ok=True)
    return root


DEFAULT_BASE_DIR = infer_state_root() / "governance_heartbeat_r1"
DEFAULT_GOVERNANCE_LOG = DEFAULT_BASE_DIR / "governance_log_r1.jsonl"
DEFAULT_RECEIPT = DEFAULT_BASE_DIR / "governance_heartbeat_001_receipt.json"


def build_heartbeat_metadata() -> Dict[str, Any]:
    return {
        "heartbeat_id": "governance-heartbeat-001",
        "plan_artifact": "docs/GOVERNANCE_HEARTBEAT_001.md",
        "seed_plan_artifact": "docs/GOVERNANCE_CANON_SEED_PLAN.md",
        "artifact_truth_contract": "docs/ARTIFACT_TRUTH_CONTRACT.md",
        "runtime_truth_snapshot": "public/runtime/runtime_truth_snapshot.json",
        "related_prs": [299, 300, 301, 302],
        "canonical_change": False,
        "promotion": False,
        "boundary": "Governance history only; does not create canon lineage or promote canon-0001.",
    }


def write_heartbeat(*, governance_log_path: Path = DEFAULT_GOVERNANCE_LOG, receipt_path: Path = DEFAULT_RECEIPT) -> Dict[str, Any]:
    governance_log_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)

    log = GovernanceLog(governance_log_path)
    record = log.append(
        event_type="governance_orientation",
        session_id="governance-heartbeat-001",
        previous_mode="DryDock",
        new_mode="Observation",
        allowed=True,
        reason="First lawful governance heartbeat after artifact truth and capability registry reconciliation.",
        requested_action="seed governance heartbeat 001",
        artifact_delta={
            "summary": "Artifact truth reconciliation and capability registry cleanup completed; runtime truth reports capability_registry.valid=true.",
            "canon_deferred": True,
        },
        canonical_change=False,
        validation_reference="public/runtime/runtime_truth_snapshot.json",
        metadata=build_heartbeat_metadata(),
    )
    verification = log.verify_chain()
    receipt = {
        "schema_version": "governance-heartbeat-receipt-v0.1",
        "created_at": utc_now(),
        "record": record,
        "verification": verification,
        "authority_boundary": "Receipt records governance history only; it does not authorize action, mutate canon, or promote canonical state.",
    }
    with receipt_path.open("w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append Governance Heartbeat 001 and write a verification receipt.")
    parser.add_argument("--governance-log", default=str(DEFAULT_GOVERNANCE_LOG))
    parser.add_argument("--receipt", default=str(DEFAULT_RECEIPT))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    out = write_heartbeat(governance_log_path=Path(args.governance_log), receipt_path=Path(args.receipt))
    print(json.dumps(out, indent=2))
