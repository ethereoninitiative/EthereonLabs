from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    from .runtime_truth_observation_cycle_r1 import run_runtime_truth_observation_cycle, infer_repo_root
except Exception:
    from runtime_truth_observation_cycle_r1 import run_runtime_truth_observation_cycle, infer_repo_root


REPO_ROOT = infer_repo_root()
PUBLIC_RUNTIME_DIR = REPO_ROOT / "public" / "runtime"
LATEST_CYCLE_PATH = PUBLIC_RUNTIME_DIR / "latest_cycle.json"
SNAPSHOT_PATH = PUBLIC_RUNTIME_DIR / "runtime_truth_snapshot.json"
PUBLIC_HISTORY_DIR = PUBLIC_RUNTIME_DIR / "history"
PUBLIC_HISTORY_INDEX = PUBLIC_HISTORY_DIR / "index.json"
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "runtime_truth" / "current"
POST_PROMOTION_PATH = ARTIFACT_DIR / "post_promotion_verification_0001.json"
PROMOTION_RECEIPT_PATH = ARTIFACT_DIR / "promotion_receipt_0001.json"
GOVERNANCE_CHAIN_PATH = ARTIFACT_DIR / "governance_chain_0001.jsonl"
CANON_LINEAGE_PATH = ARTIFACT_DIR / "canon_lineage_0001.jsonl"
LATEST_CYCLE_SCHEMA_VERSION = "lumina-runtime-ui-cycle-v0.4"
PUBLIC_SNAPSHOT_SCHEMA_VERSION = "lumina-runtime-truth-public-snapshot-v0.2"
PUBLIC_HISTORY_LIMIT = 25


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload if isinstance(payload, dict) else {}


def _read_json_list(path: Path) -> list[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _write_json(path: Path, payload: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return _repo_relative(path)


def _write_json_list(path: Path, payload: list[Dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return _repo_relative(path)


def _repo_relative(path: str | Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except Exception:
        return candidate.as_posix()


def _read_named(artifact_map: Dict[str, str], name: str) -> Dict[str, Any]:
    path_text = artifact_map.get(name)
    if not path_text:
        return {}
    path = Path(path_text)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return _read_json(path)


def _committed_authority_payload() -> Dict[str, Any]:
    post = _read_json(POST_PROMOTION_PATH)
    promotion = _read_json(PROMOTION_RECEIPT_PATH)
    governance = post.get("governance_chain_verification", {}) or {}
    canon = post.get("canon_lineage_verification", {}) or {}
    return {
        "scope": "committed_runtime_truth_evidence",
        "governance_chain": {
            "status": governance.get("status", "missing"),
            "valid": governance.get("valid"),
            "event_count": governance.get("event_count"),
            "latest_event_hash": governance.get("latest_event_hash"),
        },
        "canon_lineage": {
            "status": canon.get("status", "missing"),
            "valid": canon.get("valid"),
            "current_head": canon.get("current_head"),
            "record_count": canon.get("record_count"),
        },
        "promotion": {
            "valid": promotion.get("valid"),
            "passed": promotion.get("passed"),
            "promotion_id": promotion.get("promotion_id"),
            "symbolic_dependency_violation": (
                (promotion.get("promotion_payload") or {}).get("symbolic_dependency_violation")
            ),
        },
        "post_promotion_verification": {
            "valid": post.get("valid"),
            "passed": post.get("passed"),
            "verifier": post.get("verifier"),
        },
        "evidence_paths": {
            "governance_chain": _repo_relative(GOVERNANCE_CHAIN_PATH),
            "canon_lineage": _repo_relative(CANON_LINEAGE_PATH),
            "promotion_receipt": _repo_relative(PROMOTION_RECEIPT_PATH),
            "post_promotion_verification": _repo_relative(POST_PROMOTION_PATH),
        },
    }


def _truth_payload_from_artifacts(artifact_map: Dict[str, str]) -> Dict[str, Any]:
    observed_governance = _read_named(artifact_map, "governance_chain_verification")
    observed_canon = _read_named(artifact_map, "canon_lineage_verification")
    capability = _read_named(artifact_map, "capability_registry_audit")
    protocol = _read_named(artifact_map, "protocol_conformance_report")
    symbolic = _read_named(artifact_map, "symbolic_dependency_contract")
    committed = _committed_authority_payload()

    return {
        "governance_chain": committed["governance_chain"],
        "canon_lineage": committed["canon_lineage"],
        "committed_authority": committed,
        "observed_runtime_state": {
            "scope": "ephemeral_observation_state",
            "does_not_override_committed_authority": True,
            "governance_chain": {
                "status": observed_governance.get("status", "missing"),
                "valid": observed_governance.get("valid"),
                "event_count": observed_governance.get("event_count"),
            },
            "canon_lineage": {
                "status": observed_canon.get("status", "missing"),
                "valid": observed_canon.get("valid"),
                "current_head": observed_canon.get("current_head"),
                "record_count": observed_canon.get("record_count"),
            },
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


def _scope_payload() -> Dict[str, Any]:
    return {
        "public_projection": "committed_runtime_truth_evidence",
        "observation_receipts": "ephemeral_observation_state",
        "does_not_override_committed_authority": True,
    }


def _normalize_latest_cycle_contract(latest: Dict[str, Any], runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(latest)
    normalized["schema_version"] = LATEST_CYCLE_SCHEMA_VERSION
    governance = dict(normalized.get("governance", {}))
    governance.pop("symbolic_dependency", None)
    governance.pop("ethereonic_attachment", None)
    symbolic_boundary = runtime_truth.get("symbolic_boundary", {})
    governance["symbolic_context_present"] = symbolic_boundary.get("symbolic_context_present", True)
    governance["symbolic_dependency_allowed"] = symbolic_boundary.get("symbolic_dependency_allowed", False)
    governance["chain_valid"] = (runtime_truth.get("governance_chain") or {}).get("valid")
    normalized["governance"] = governance
    canon = runtime_truth.get("canon_lineage", {}) or {}
    normalized["canon"] = {
        "current_head": canon.get("current_head"),
        "valid": canon.get("valid"),
        "record_count": canon.get("record_count"),
    }
    normalized["runtime_truth_scope"] = _scope_payload()
    normalized["runtime_truth"] = runtime_truth
    normalized.setdefault(
        "authority_boundary",
        "Display receipt only; does not authorize action, alter governance, mutate canon, change mode legality, expose capabilities, or execute tools.",
    )
    return normalized


def _history_archive_name(snapshot: Dict[str, Any]) -> Optional[str]:
    run_id = snapshot.get("run_id")
    timestamp = snapshot.get("timestamp")
    if not run_id or not timestamp:
        return None
    safe_run = str(run_id).replace("/", "-").replace(":", "-")
    safe_timestamp = str(timestamp).replace(":", "-").replace("+", "_")
    return f"{safe_timestamp}_{safe_run}.json"


def _sync_public_history(snapshot: Dict[str, Any]) -> Optional[str]:
    archive_name = _history_archive_name(snapshot)
    if archive_name is None:
        return None

    archive_path = PUBLIC_HISTORY_DIR / archive_name
    _write_json(archive_path, snapshot)

    probe = snapshot.get("probe", {}) if isinstance(snapshot.get("probe"), dict) else {}
    status = snapshot.get("status", {}) if isinstance(snapshot.get("status"), dict) else {}
    mode = snapshot.get("mode", {}) if isinstance(snapshot.get("mode"), dict) else {}
    entry = {
        "timestamp": snapshot.get("timestamp"),
        "run_id": snapshot.get("run_id"),
        "status": status.get("label"),
        "mode": mode.get("current"),
        "file": f"/runtime/history/{archive_name}",
        "probe_instrument_version": probe.get("instrument_version"),
        "hybrid_continuity_coherence": probe.get("hybrid_continuity_coherence"),
    }

    index = _read_json_list(PUBLIC_HISTORY_INDEX)
    run_id = snapshot.get("run_id")
    index = [entry] + [item for item in index if item.get("run_id") != run_id]
    _write_json_list(PUBLIC_HISTORY_INDEX, index[:PUBLIC_HISTORY_LIMIT])
    return _repo_relative(archive_path)


def build_public_runtime_truth_snapshot(
    *,
    latest_cycle_path: Optional[str | Path] = None,
    snapshot_path: Optional[str | Path] = None,
    observation_output_dir: Optional[str | Path] = None,
) -> Dict[str, Any]:
    latest_path = Path(latest_cycle_path) if latest_cycle_path else LATEST_CYCLE_PATH
    out_path = Path(snapshot_path) if snapshot_path else SNAPSHOT_PATH

    observation = run_runtime_truth_observation_cycle(output_dir=observation_output_dir)
    artifact_map = observation.get("artifacts", {})
    runtime_truth = _truth_payload_from_artifacts(artifact_map)
    latest = _read_json(latest_path)
    normalized_latest = _normalize_latest_cycle_contract(latest, runtime_truth) if latest else {}
    history_receipt_path = None

    if normalized_latest:
        _write_json(latest_path, normalized_latest)
        if latest_path.resolve() == LATEST_CYCLE_PATH.resolve():
            history_receipt_path = _sync_public_history(normalized_latest)

    source_latest = normalized_latest or latest
    public_artifact_paths = {
        **artifact_map,
        **runtime_truth["committed_authority"]["evidence_paths"],
    }
    if history_receipt_path:
        public_artifact_paths["history_receipt"] = history_receipt_path

    public_snapshot = {
        "schema_version": PUBLIC_SNAPSHOT_SCHEMA_VERSION,
        "source_latest_cycle": _repo_relative(latest_path),
        "latest_cycle_run_id": source_latest.get("run_id"),
        "latest_cycle_timestamp": source_latest.get("timestamp"),
        "mode": source_latest.get("mode", {}),
        "action_type": source_latest.get("action_type"),
        "runtime_truth_scope": _scope_payload(),
        "runtime_truth": runtime_truth,
        "artifact_paths": public_artifact_paths,
        "authority_boundary": "Public runtime truth summary only; does not authorize action, alter governance, mutate canon, change mode legality, expose capabilities, or execute tools.",
    }
    _write_json(out_path, public_snapshot)
    return public_snapshot


if __name__ == "__main__":
    print(json.dumps(build_public_runtime_truth_snapshot(), indent=2))
