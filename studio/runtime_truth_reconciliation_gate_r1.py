from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple
import json
import sys


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or ((parent / "LuminaOS").exists() and (parent / "public").exists()):
            return parent
    return Path.cwd()


ROOT = repo_root()
RUNTIME_DIR = ROOT / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from governance_integrity_r1 import GovernanceIntegrityChain  # noqa: E402
from canon_lineage_store_r1 import CanonLineageStore  # noqa: E402


EXPECTED_LATEST_SCHEMA = "lumina-runtime-ui-cycle-v0.4"
PATHS = {
    "governance_chain": ROOT / "artifacts/runtime_truth/current/governance_chain_0001.jsonl",
    "canon_lineage": ROOT / "artifacts/runtime_truth/current/canon_lineage_0001.jsonl",
    "promotion_receipt": ROOT / "artifacts/runtime_truth/current/promotion_receipt_0001.json",
    "post_promotion": ROOT / "artifacts/runtime_truth/current/post_promotion_verification_0001.json",
    "public_snapshot": ROOT / "public/runtime/runtime_truth_snapshot.json",
    "latest_cycle": ROOT / "public/runtime/latest_cycle.json",
    "history_index": ROOT / "public/runtime/history/index.json",
    "capability_registry": RUNTIME_DIR / "capability_registry_r1.json",
    "active_runtime_index": ROOT / "LuminaOS/bootstrap/Ship_of_Ethereon_V2/ACTIVE_RUNTIME_INDEX.md",
    "seed_plan": ROOT / "docs/GOVERNANCE_CANON_SEED_PLAN.md",
}


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def read_json_list(path: Path) -> list[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, list):
        raise ValueError(f"expected JSON list: {path}")
    return [item for item in payload if isinstance(item, dict)]


def contains_absolute_workspace_path(node: Any) -> bool:
    if isinstance(node, dict):
        return any(contains_absolute_workspace_path(value) for value in node.values())
    if isinstance(node, list):
        return any(contains_absolute_workspace_path(value) for value in node)
    if isinstance(node, str):
        return "/home/runner/" in node or "/workspace/" in node
    return False


def public_history_receipt_path(entry: Dict[str, Any]) -> Path | None:
    file_reference = entry.get("file")
    if not isinstance(file_reference, str) or not file_reference.startswith("/runtime/history/"):
        return None
    candidate = (ROOT / "public" / file_reference.lstrip("/")).resolve()
    try:
        candidate.relative_to((ROOT / "public").resolve())
    except ValueError:
        return None
    return candidate


def run_gate() -> Tuple[bool, Dict[str, bool], Dict[str, Any]]:
    missing = [name for name, path in PATHS.items() if not path.exists()]
    if missing:
        return False, {f"required_{name}_exists": False for name in missing}, {"missing": missing}

    governance = GovernanceIntegrityChain(PATHS["governance_chain"]).verify_chain()
    canon = CanonLineageStore(PATHS["canon_lineage"]).verify_lineage()
    promotion = read_json(PATHS["promotion_receipt"])
    post = read_json(PATHS["post_promotion"])
    snapshot = read_json(PATHS["public_snapshot"])
    latest = read_json(PATHS["latest_cycle"])
    history_index = read_json_list(PATHS["history_index"])
    registry = read_json(PATHS["capability_registry"])
    index_text = PATHS["active_runtime_index"].read_text(encoding="utf-8")
    seed_text = PATHS["seed_plan"].read_text(encoding="utf-8")

    latest_history_entry = history_index[0] if history_index else {}
    history_receipt_path = public_history_receipt_path(latest_history_entry)
    history_receipt_exists = history_receipt_path is not None and history_receipt_path.exists()
    history_receipt = read_json(history_receipt_path) if history_receipt_exists and history_receipt_path else {}

    truth = snapshot.get("runtime_truth", {}) or {}
    public_governance = truth.get("governance_chain", {}) or {}
    public_canon = truth.get("canon_lineage", {}) or {}
    committed = truth.get("committed_authority", {}) or {}
    observed = truth.get("observed_runtime_state", {}) or {}
    scope = snapshot.get("runtime_truth_scope", {}) or {}
    latest_truth = latest.get("runtime_truth", {}) or {}
    latest_scope = latest.get("runtime_truth_scope", {}) or {}
    latest_canon = latest.get("canon", {}) or {}

    capability_count = len([item for item in registry.get("capabilities", []) if isinstance(item, dict)])
    symbolic_violation = (promotion.get("promotion_payload") or {}).get("symbolic_dependency_violation")

    checks = {
        "governance_chain_valid": governance.get("valid") is True,
        "governance_event_count_positive": int(governance.get("event_count") or 0) > 0,
        "canon_lineage_valid": canon.get("valid") is True,
        "canon_head_present": bool(canon.get("current_head")),
        "promotion_passed": promotion.get("passed") is True and promotion.get("valid") is True,
        "promotion_has_no_symbolic_dependency": symbolic_violation is False,
        "post_promotion_verification_passed": post.get("passed") is True and post.get("valid") is True,
        "public_governance_matches_committed": (
            public_governance.get("valid") == governance.get("valid")
            and public_governance.get("event_count") == governance.get("event_count")
        ),
        "public_canon_matches_committed": (
            public_canon.get("valid") == canon.get("valid")
            and public_canon.get("record_count") == canon.get("record_count")
            and public_canon.get("current_head") == canon.get("current_head")
        ),
        "committed_authority_scope_present": committed.get("scope") == "committed_runtime_truth_evidence",
        "observation_scope_is_explicit": (
            observed.get("scope") == "ephemeral_observation_state"
            and observed.get("does_not_override_committed_authority") is True
        ),
        "snapshot_scope_prevents_override": scope.get("does_not_override_committed_authority") is True,
        "latest_scope_prevents_override": latest_scope.get("does_not_override_committed_authority") is True,
        "latest_cycle_schema_is_current": latest.get("schema_version") == EXPECTED_LATEST_SCHEMA,
        "latest_canon_matches_committed": (
            latest_canon.get("current_head") == canon.get("current_head")
            and latest_canon.get("record_count") == canon.get("record_count")
            and latest_canon.get("valid") == canon.get("valid")
        ),
        "latest_runtime_truth_matches_snapshot": (
            (latest_truth.get("canon_lineage") or {}).get("current_head") == canon.get("current_head")
            and (latest_truth.get("governance_chain") or {}).get("event_count") == governance.get("event_count")
        ),
        "snapshot_source_run_matches_latest": snapshot.get("latest_cycle_run_id") == latest.get("run_id"),
        "snapshot_source_timestamp_matches_latest": snapshot.get("latest_cycle_timestamp") == latest.get("timestamp"),
        "history_index_not_empty": bool(history_index),
        "history_index_latest_run_matches_latest": latest_history_entry.get("run_id") == latest.get("run_id"),
        "history_index_latest_timestamp_matches_latest": latest_history_entry.get("timestamp") == latest.get("timestamp"),
        "history_receipt_path_is_valid": history_receipt_path is not None,
        "history_receipt_exists": history_receipt_exists,
        "history_receipt_run_matches_latest": history_receipt.get("run_id") == latest.get("run_id"),
        "history_receipt_timestamp_matches_latest": history_receipt.get("timestamp") == latest.get("timestamp"),
        "history_receipt_schema_matches_latest": history_receipt.get("schema_version") == latest.get("schema_version"),
        "history_receipt_canon_matches_latest": history_receipt.get("canon") == latest.get("canon"),
        "history_receipt_scope_matches_latest": history_receipt.get("runtime_truth_scope") == latest.get("runtime_truth_scope"),
        "history_receipt_runtime_truth_matches_latest": history_receipt.get("runtime_truth") == latest.get("runtime_truth"),
        "history_receipt_probe_version_matches_latest": (
            (history_receipt.get("probe") or {}).get("instrument_version")
            == (latest.get("probe") or {}).get("instrument_version")
        ),
        "capability_count_matches_registry": (truth.get("capability_registry") or {}).get("capability_count") == capability_count,
        "public_artifacts_are_repo_relative": not contains_absolute_workspace_path(snapshot),
        "latest_cycle_is_repo_relative": not contains_absolute_workspace_path(latest),
        "history_receipt_is_repo_relative": not contains_absolute_workspace_path(history_receipt),
        "active_index_names_reconciliation_gate": "runtime_truth_reconciliation_gate_r1.py" in index_text,
        "active_index_names_v18": "psi42_transceiver_v1_8.py" in index_text,
        "active_index_names_correlation": "continuity_correlation" in index_text,
        "active_index_names_resonant_manifold": "resonant_manifold_r1.py" in index_text,
        "active_index_names_living_framework": "living_framework_chamber_r1.py" in index_text,
        "seed_plan_records_canon_0001_as_established": "canon-0001 is established" in seed_text,
    }

    details = {
        "governance": governance,
        "canon": canon,
        "public_scope": scope,
        "observed_scope": observed.get("scope"),
        "capability_count": capability_count,
        "latest_run_id": latest.get("run_id"),
        "snapshot_source_run_id": snapshot.get("latest_cycle_run_id"),
        "history_index_run_id": latest_history_entry.get("run_id"),
        "history_receipt_path": str(history_receipt_path) if history_receipt_path else None,
        "history_receipt_run_id": history_receipt.get("run_id"),
    }
    return all(checks.values()), checks, details


if __name__ == "__main__":
    ok, checks, details = run_gate()
    print(json.dumps({"status": "pass" if ok else "fail", "checks": checks, "details": details}, indent=2))
    raise SystemExit(0 if ok else 1)
