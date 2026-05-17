from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    from .runtime_truth_observation_cycle_r1 import run_runtime_truth_observation_cycle
except Exception:
    from runtime_truth_observation_cycle_r1 import run_runtime_truth_observation_cycle


RUNTIME_ROOT = Path(__file__).resolve().parent
REPO_ROOT = RUNTIME_ROOT.parents[3] if len(RUNTIME_ROOT.parents) >= 4 else RUNTIME_ROOT
PUBLIC_RUNTIME_DIR = REPO_ROOT / "public" / "runtime"
LATEST_CYCLE_PATH = PUBLIC_RUNTIME_DIR / "latest_cycle.json"
SNAPSHOT_PATH = PUBLIC_RUNTIME_DIR / "runtime_truth_snapshot.json"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return str(path)


def _truth_payload_from_artifacts(artifact_map: Dict[str, str]) -> Dict[str, Any]:
    def read_named(name: str) -> Dict[str, Any]:
        path = artifact_map.get(name)
        return _read_json(Path(path)) if path else {}

    governance = read_named("governance_chain_verification")
    canon = read_named("canon_lineage_verification")
    capability = read_named("capability_registry_audit")
    protocol = read_named("protocol_conformance_report")
    symbolic = read_named("symbolic_dependency_contract")

    return {
        "governance_chain": {
            "status": governance.get("status", "missing"),
            "valid": governance.get("valid"),
            "event_count": governance.get("event_count"),
        },
        "canon_lineage": {
            "status": canon.get("status", "missing"),
            "valid": canon.get("valid"),
            "current_head": canon.get("current_head"),
            "record_count": canon.get("record_count"),
        },
        "protocol_conformance": {
            "status": protocol.get("status", "missing"),
            "valid": protocol.get("valid"),
            "issues": protocol.get("issues", []),
        },
        "capability_registry": {
            "status": capability.get("status", "missing"),
            "valid": capability.get("valid"),
            "capability_count": capability.get("capability_count"),
            "issues": capability.get("issues", []),
        },
        "symbolic_boundary": {
            "symbolic_context_present": symbolic.get("symbolic_context_present_allowed", True),
            "symbolic_dependency_allowed": symbolic.get("symbolic_dependency_allowed", False),
            "contract_version": symbolic.get("version", "1.0"),
        },
    }


def build_public_runtime_truth_snapshot(
    *,
    latest_cycle_path: Optional[str | Path] = None,
    snapshot_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Generate runtime truth receipts and attach their summary to public runtime JSON.

    This performs receipt ingestion only. It does not authorize actions or alter runtime law.
    """
    latest_path = Path(latest_cycle_path) if latest_cycle_path else LATEST_CYCLE_PATH
    out_path = Path(snapshot_path) if snapshot_path else SNAPSHOT_PATH

    observation = run_runtime_truth_observation_cycle()
    artifact_map = observation.get("artifacts", {})
    runtime_truth = _truth_payload_from_artifacts(artifact_map)

    latest = _read_json(latest_path)
    public_snapshot = {
        "schema_version": "lumina-runtime-truth-public-snapshot-v0.1",
        "source_latest_cycle": str(latest_path),
        "latest_cycle_run_id": latest.get("run_id"),
        "latest_cycle_timestamp": latest.get("timestamp"),
        "mode": latest.get("mode", {}),
        "action_type": latest.get("action_type"),
        "runtime_truth": runtime_truth,
        "artifact_paths": artifact_map,
        "authority_boundary": "Public runtime truth summary only; does not authorize action, alter governance, mutate canon, change mode legality, expose capabilities, or execute tools.",
    }
    _write_json(out_path, public_snapshot)

    if latest:
        latest["runtime_truth"] = runtime_truth
        latest.setdefault("authority_boundary", public_snapshot["authority_boundary"])
        _write_json(latest_path, latest)

    return public_snapshot


if __name__ == "__main__":
    print(json.dumps(build_public_runtime_truth_snapshot(), indent=2))
