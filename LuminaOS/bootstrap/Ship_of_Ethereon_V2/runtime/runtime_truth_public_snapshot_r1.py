from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json

if __package__:
    from .runtime_truth_observation_cycle_r1 import run_runtime_truth_observation_cycle, infer_repo_root
else:
    from runtime_truth_observation_cycle_r1 import run_runtime_truth_observation_cycle, infer_repo_root


REPO_ROOT = infer_repo_root()
PUBLIC_RUNTIME_DIR = REPO_ROOT / "public" / "runtime"
LATEST_CYCLE_PATH = PUBLIC_RUNTIME_DIR / "latest_cycle.json"
SNAPSHOT_PATH = PUBLIC_RUNTIME_DIR / "runtime_truth_snapshot.json"
LATEST_CYCLE_SCHEMA_VERSION = "lumina-runtime-ui-cycle-v0.4"


def repo_relative_path(path: str | Path) -> str:
    resolved = Path(path).resolve()
    root = REPO_ROOT.resolve()
    try:
        return str(resolved.relative_to(root))
    except ValueError:
        return str(path)


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return str(path)


def _normalize_latest_cycle_contract(latest: Dict[str, Any], runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(latest)
    normalized["schema_version"] = LATEST_CYCLE_SCHEMA_VERSION
    governance = dict(normalized.get("governance", {}))
    governance.pop("symbolic_dependency", None)
    governance.pop("ethereonic_attachment", None)
    symbolic_boundary = runtime_truth.get("symbolic_boundary", {})
    governance["symbolic_context_present"] = symbolic_boundary.get("symbolic_context_present", True)
    governance["symbolic_dependency_allowed"] = symbolic_boundary.get("symbolic_dependency_allowed", False)
    normalized["governance"] = governance
    normalized["runtime_truth"] = runtime_truth
    normalized.setdefault(
        "authority_boundary",
        "Display receipt only; does not authorize action, alter governance, mutate canon, change mode legality, expose capabilities, or execute tools.",
    )
    return normalized


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
    latest_path = Path(latest_cycle_path) if latest_cycle_path else LATEST_CYCLE_PATH
    out_path = Path(snapshot_path) if snapshot_path else SNAPSHOT_PATH

    observation = run_runtime_truth_observation_cycle()
    artifact_map = observation.get("artifacts", {})
    runtime_truth = _truth_payload_from_artifacts(artifact_map)

    latest = _read_json(latest_path)
    public_snapshot = {
        "schema_version": "lumina-runtime-truth-public-snapshot-v0.1",
        "source_latest_cycle": repo_relative_path(latest_path),
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
        _write_json(latest_path, _normalize_latest_cycle_contract(latest, runtime_truth))

    return public_snapshot


if __name__ == "__main__":
    print(json.dumps(build_public_runtime_truth_snapshot(), indent=2))