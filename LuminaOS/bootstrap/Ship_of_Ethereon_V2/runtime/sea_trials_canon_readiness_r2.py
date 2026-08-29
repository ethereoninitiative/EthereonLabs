from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import copy
import hashlib
import json
import subprocess
import tempfile

try:
    from .canon_lineage_store_r1 import CanonLineageStore
    from .governance_integrity_r1 import GovernanceIntegrityChain
    from .post_promotion_verifier_r1 import run as run_post_promotion_verifier
    from .repo_paths_r1 import repo_root
    from .runtime_runner_r1_merged import RuntimeRunner
except Exception:
    from canon_lineage_store_r1 import CanonLineageStore
    from governance_integrity_r1 import GovernanceIntegrityChain
    from post_promotion_verifier_r1 import run as run_post_promotion_verifier
    from repo_paths_r1 import repo_root
    from runtime_runner_r1_merged import RuntimeRunner


ARTIFACT_DIR_REL = Path("artifacts/runtime_truth/current")
GOVERNANCE_REL = ARTIFACT_DIR_REL / "governance_chain_0001.jsonl"
CANON_REL = ARTIFACT_DIR_REL / "canon_lineage_0001.jsonl"
PROMOTION_REL = ARTIFACT_DIR_REL / "promotion_receipt_0001.json"
POST_PROMOTION_REL = ARTIFACT_DIR_REL / "post_promotion_verification_0001.json"
SEA_TRIAL_REL = ARTIFACT_DIR_REL / "sea_trial_genesis_governance_r1_receipt.json"
RECEIPT_DIR_REL = Path(".lumina_state/ship_of_ethereon_v2/sea_trials_canon_readiness_r2")
RECEIPT_REL = RECEIPT_DIR_REL / "sea_trials_canon_readiness_r2_receipt.json"

PROMOTION_PAYLOAD = {
    "validation_artifact_id": "canon-readiness-r2-isolated-promotion",
    "test_execution_log": "isolated valid promotion candidate",
    "change_summary": "verify canon-readiness evidence linkage without changing committed canon",
    "structural_impact_assessment": "isolated sea-trial state only",
    "regression_check_confirmation": True,
    "conceptual_layer_check_confirmation": True,
    "runtime_requires_symbolic_interpretation": False,
}

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}

LEAK_RUNTIME_CONFIG = {
    **SAFE_RUNTIME_CONFIG,
    "toki_pona_required_for_resume": True,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def current_head(root: Path) -> Optional[str]:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = completed.stdout.strip()
    return value or None


def bind_validation_artifact(root: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    repository_head = current_head(root)
    if not repository_head:
        raise RuntimeError("promotion validation artifact requires a Git repository HEAD")
    artifact_path = root / RECEIPT_DIR_REL / "isolated_promotion_validation.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(
            {
                "artifact_id": payload["validation_artifact_id"],
                "repository_head": repository_head,
                "passed": True,
                "authority_scope": "isolated_sea_trial_only",
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return {
        **payload,
        "validation_artifact_path": artifact_path.relative_to(root).as_posix(),
        "validation_artifact_sha256": hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
        "candidate_commit_sha": repository_head,
    }


def verify_committed_evidence(root: Path) -> Dict[str, Any]:
    paths = {
        "governance_chain": root / GOVERNANCE_REL,
        "canon_lineage": root / CANON_REL,
        "promotion_receipt": root / PROMOTION_REL,
        "post_promotion_verification": root / POST_PROMOTION_REL,
        "sea_trial_receipt": root / SEA_TRIAL_REL,
    }
    existence = {name: path.is_file() for name, path in paths.items()}
    if not all(existence.values()):
        return {
            "passed": False,
            "existence": existence,
            "reason": "one or more committed promotion artifacts are missing",
        }

    governance_path = paths["governance_chain"]
    canon_path = paths["canon_lineage"]
    promotion = read_json(paths["promotion_receipt"])
    post_promotion = read_json(paths["post_promotion_verification"])
    sea_trial = read_json(paths["sea_trial_receipt"])
    governance_rows = read_jsonl(governance_path)
    canon_rows = read_jsonl(canon_path)

    governance_verification = GovernanceIntegrityChain(governance_path).verify_chain()
    canon_verification = CanonLineageStore(canon_path).verify_lineage()
    governance = governance_rows[0] if len(governance_rows) == 1 else {}
    canon = canon_rows[0] if len(canon_rows) == 1 else {}
    promotion_payload = promotion.get("promotion_payload")
    if not isinstance(promotion_payload, dict):
        promotion_payload = {}

    evidence_paths = {
        "governance_chain": promotion_payload.get("governance_evidence_path"),
        "canon_lineage": promotion_payload.get("canon_lineage_path"),
        "validation_reference": promotion_payload.get("validation_reference"),
    }
    relative_evidence_paths = {
        name: isinstance(value, str) and not Path(value).is_absolute() and (root / value).is_file()
        for name, value in evidence_paths.items()
    }

    checks = {
        "all_promotion_artifacts_exist": all(existence.values()),
        "evidence_paths_exist_and_are_relative": all(relative_evidence_paths.values()),
        "governance_chain_valid": governance_verification.get("valid") is True,
        "governance_event_count_is_1": governance_verification.get("event_count") == 1,
        "canon_lineage_valid": canon_verification.get("valid") is True,
        "canon_record_count_is_1": canon_verification.get("record_count") == 1,
        "canon_head_is_canon_0001": canon_verification.get("current_head") == "canon-0001",
        "promotion_valid": promotion.get("valid") is True,
        "promotion_passed": promotion.get("passed") is True,
        "post_promotion_verifier_passed": post_promotion.get("passed") is True,
        "genesis_sea_trial_passed": sea_trial.get("passed") is True,
        "promotion_payload_hash_linked": promotion.get("promotion_payload_hash")
        == sha256_text(canonical_json(promotion_payload)),
        "governance_hash_linked": promotion.get("governance_event_hash") == governance.get("record_hash") == canon.get("governance_event_hash"),
        "canon_hash_linked": promotion.get("canon_lineage_hash") == canon.get("lineage_record_hash"),
        "lineage_payload_hash_linked": canon.get("promotion_payload_hash") == promotion.get("promotion_payload_hash"),
        "validation_reference_linked": (
            governance.get("validation_reference")
            == canon.get("validation_artifact_reference")
            == promotion_payload.get("validation_reference")
        ),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "governance_verification": governance_verification,
        "canon_verification": canon_verification,
        "evidence_paths": evidence_paths,
        "promotion_id": promotion.get("promotion_id"),
        "canon_head": canon_verification.get("current_head"),
    }


def verify_tamper_detection(root: Path) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="canon-readiness-r2-tamper-") as temp_dir:
        temp = Path(temp_dir)
        tampered_governance = temp / "governance.jsonl"
        tampered_canon = temp / "canon.jsonl"

        governance_rows = read_jsonl(root / GOVERNANCE_REL)
        canon_rows = read_jsonl(root / CANON_REL)
        governance_rows[0]["reason"] = f"{governance_rows[0].get('reason', '')} [tampered]"
        canon_rows[0]["canon_commit_summary"] = f"{canon_rows[0].get('canon_commit_summary', '')} [tampered]"
        write_jsonl(tampered_governance, governance_rows)
        write_jsonl(tampered_canon, canon_rows)

        governance_result = GovernanceIntegrityChain(tampered_governance).verify_chain()
        canon_result = CanonLineageStore(tampered_canon).verify_lineage()
        checks = {
            "governance_mutation_detected": governance_result.get("valid") is False,
            "canon_mutation_detected": canon_result.get("valid") is False,
        }
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "governance_result": governance_result,
            "canon_result": canon_result,
        }


def run_isolated_runner_trial(runtime_root_path: Path, base_dir: Path, **kwargs: Any) -> Dict[str, Any]:
    runner = RuntimeRunner(base_dir=base_dir, registry_path=runtime_root_path / "capability_registry_r1.json")
    result = runner.run_cycle(**kwargs).to_dict()
    result["lineage_status"] = runner.canon_lineage_store.verify_lineage()
    result["governance_status"] = runner.governance_log.verify_chain()
    return result


def verify_runtime_rejections(root: Path) -> Dict[str, Any]:
    runtime_dir = root / "LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime"
    valid_payload = bind_validation_artifact(root, copy.deepcopy(PROMOTION_PAYLOAD))
    with tempfile.TemporaryDirectory(prefix="canon-readiness-r2-runtime-") as temp_dir:
        temp = Path(temp_dir)
        malformed = run_isolated_runner_trial(
            runtime_dir,
            temp / "malformed-input",
            current_mode="DryDock",
            target_mode="Canon",
            requested_action="canon_readiness_r2_malformed_input",
            action_type="promotion",
            promotion_payload=copy.deepcopy(valid_payload),
            raw_user_input="make a canon promotion from sand box",
        )
        malformed_integrity = malformed.get("governance", {}).get("input_integrity", {})
        malformed_lineage = malformed.get("lineage_status", {})

        symbolic = run_isolated_runner_trial(
            runtime_dir,
            temp / "symbolic-dependency",
            current_mode="DryDock",
            target_mode="Canon",
            requested_action="canon_readiness_r2_symbolic_dependency",
            action_type="promotion",
            promotion_payload=copy.deepcopy(valid_payload),
            runtime_config=LEAK_RUNTIME_CONFIG,
        )
        symbolic_gate = symbolic.get("governance", {}).get("symbolic_dependency", {})
        symbolic_lineage = symbolic.get("lineage_status", {})

        safe = run_isolated_runner_trial(
            runtime_dir,
            temp / "safe-promotion",
            current_mode="DryDock",
            target_mode="Canon",
            requested_action="canon_readiness_r2_safe_promotion",
            action_type="promotion",
            promotion_payload=copy.deepcopy(valid_payload),
            runtime_config=SAFE_RUNTIME_CONFIG,
        )
        safe_lineage = safe.get("lineage_status", {})

        missing_artifact_payload = copy.deepcopy(valid_payload)
        missing_artifact_payload["validation_artifact_path"] = ".lumina_state/definitely-missing-validation.json"
        missing_artifact = run_isolated_runner_trial(
            runtime_dir,
            temp / "missing-artifact",
            current_mode="DryDock",
            target_mode="Canon",
            requested_action="canon_readiness_r2_missing_artifact",
            action_type="promotion",
            promotion_payload=missing_artifact_payload,
            runtime_config=SAFE_RUNTIME_CONFIG,
        )

        false_regression_payload = copy.deepcopy(valid_payload)
        false_regression_payload["regression_check_confirmation"] = False
        false_regression = run_isolated_runner_trial(
            runtime_dir,
            temp / "false-regression",
            current_mode="DryDock",
            target_mode="Canon",
            requested_action="canon_readiness_r2_false_regression",
            action_type="promotion",
            promotion_payload=false_regression_payload,
            runtime_config=SAFE_RUNTIME_CONFIG,
        )

        empty_evidence_payload = copy.deepcopy(valid_payload)
        empty_evidence_payload["test_execution_log"] = ""
        empty_evidence = run_isolated_runner_trial(
            runtime_dir,
            temp / "empty-evidence",
            current_mode="DryDock",
            target_mode="Canon",
            requested_action="canon_readiness_r2_empty_evidence",
            action_type="promotion",
            promotion_payload=empty_evidence_payload,
            runtime_config=SAFE_RUNTIME_CONFIG,
        )

        hash_mismatch_payload = copy.deepcopy(valid_payload)
        hash_mismatch_payload["validation_artifact_sha256"] = "0" * 64
        hash_mismatch = run_isolated_runner_trial(
            runtime_dir,
            temp / "hash-mismatch",
            current_mode="DryDock",
            target_mode="Canon",
            requested_action="canon_readiness_r2_hash_mismatch",
            action_type="promotion",
            promotion_payload=hash_mismatch_payload,
            runtime_config=SAFE_RUNTIME_CONFIG,
        )

        candidate_mismatch_payload = copy.deepcopy(valid_payload)
        candidate_mismatch_payload["candidate_commit_sha"] = "0" * 40
        candidate_mismatch = run_isolated_runner_trial(
            runtime_dir,
            temp / "candidate-mismatch",
            current_mode="DryDock",
            target_mode="Canon",
            requested_action="canon_readiness_r2_candidate_mismatch",
            action_type="promotion",
            promotion_payload=candidate_mismatch_payload,
            runtime_config=SAFE_RUNTIME_CONFIG,
        )

        malformed_type = run_isolated_runner_trial(
            runtime_dir,
            temp / "malformed-type",
            current_mode="DryDock",
            target_mode="Canon",
            requested_action="canon_readiness_r2_malformed_type",
            action_type="promotion",
            promotion_payload=copy.deepcopy(valid_payload),
            runtime_config=SAFE_RUNTIME_CONFIG,
            raw_user_input={"unexpected": "object"},
        )

        checks = {
            "malformed_input_halted": malformed.get("halted") is True,
            "malformed_input_gate_denied": malformed_integrity.get("allowed") is False,
            "malformed_input_did_not_promote": malformed_lineage.get("record_count") == 0,
            "symbolic_dependency_halted": symbolic.get("halted") is True,
            "symbolic_dependency_gate_denied": symbolic_gate.get("allowed") is False,
            "symbolic_dependency_did_not_promote": symbolic_lineage.get("record_count") == 0,
            "safe_candidate_promoted_in_isolation": safe.get("halted") is False and safe_lineage.get("current_head") == "canon-0001",
            "safe_governance_chain_valid": safe.get("governance_status", {}).get("valid") is True,
            "missing_validation_artifact_halted": missing_artifact.get("halted") is True,
            "false_regression_confirmation_halted": false_regression.get("halted") is True,
            "empty_test_evidence_halted": empty_evidence.get("halted") is True,
            "validation_hash_mismatch_halted": hash_mismatch.get("halted") is True,
            "candidate_commit_mismatch_halted": candidate_mismatch.get("halted") is True,
            "malformed_input_type_halted": malformed_type.get("halted") is True,
        }
        return {
            "passed": all(checks.values()),
            "checks": checks,
            "malformed_input": {
                "halted": malformed.get("halted"),
                "governance": malformed.get("governance", {}),
                "lineage_status": malformed_lineage,
            },
            "symbolic_dependency": {
                "halted": symbolic.get("halted"),
                "governance": symbolic.get("governance", {}),
                "lineage_status": symbolic_lineage,
            },
            "safe_promotion": {
                "halted": safe.get("halted"),
                "lineage_status": safe_lineage,
            },
            "fail_closed_probes": {
                "missing_validation_artifact": {"halted": missing_artifact.get("halted"), "reason": missing_artifact.get("halt_reason")},
                "false_regression_confirmation": {"halted": false_regression.get("halted"), "reason": false_regression.get("halt_reason")},
                "empty_test_evidence": {"halted": empty_evidence.get("halted"), "reason": empty_evidence.get("halt_reason")},
                "validation_hash_mismatch": {"halted": hash_mismatch.get("halted"), "reason": hash_mismatch.get("halt_reason")},
                "candidate_commit_mismatch": {"halted": candidate_mismatch.get("halted"), "reason": candidate_mismatch.get("halt_reason")},
                "malformed_input_type": {"halted": malformed_type.get("halted"), "reason": malformed_type.get("halt_reason")},
            },
        }


def main() -> Dict[str, Any]:
    root = repo_root()
    head = current_head(root)
    if not head:
        raise RuntimeError("canon-readiness R2 requires a Git repository HEAD")

    committed_evidence = verify_committed_evidence(root)
    tamper_detection = verify_tamper_detection(root) if committed_evidence.get("passed") else {"passed": False, "reason": "committed evidence failed"}
    runtime_rejections = verify_runtime_rejections(root) if committed_evidence.get("passed") else {"passed": False, "reason": "committed evidence failed"}

    # Execute the existing post-promotion verifier as a live check; the committed
    # R1 artifacts remain the authority, while this trial tests their linkage.
    post_promotion_execution = run_post_promotion_verifier()
    checks = {
        "committed_evidence": committed_evidence.get("passed") is True,
        "tamper_detection": tamper_detection.get("passed") is True,
        "runtime_rejections": runtime_rejections.get("passed") is True,
        "post_promotion_execution": post_promotion_execution.get("passed") is True,
    }
    summary = {
        "generated_at": utc_now(),
        "trial_name": "sea_trials_canon_readiness_r2",
        "repository": "ethereoninitiative/EthereonLabs",
        "repository_head": head,
        "passed": all(checks.values()),
        "checks": checks,
        "committed_evidence": committed_evidence,
        "tamper_detection": tamper_detection,
        "runtime_rejections": runtime_rejections,
        "post_promotion_execution": post_promotion_execution,
        "authority_boundary": "Readiness evidence only; does not promote canon or mutate committed authority.",
        "evidence_paths": {
            "governance_chain": GOVERNANCE_REL.as_posix(),
            "canon_lineage": CANON_REL.as_posix(),
            "promotion_receipt": PROMOTION_REL.as_posix(),
            "post_promotion_verification": POST_PROMOTION_REL.as_posix(),
            "sea_trial_receipt": SEA_TRIAL_REL.as_posix(),
        },
    }
    receipt_path = root / RECEIPT_REL
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with receipt_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    summary["receipt_path"] = receipt_path.relative_to(root).as_posix()
    return summary


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
    if not result.get("passed"):
        raise SystemExit(1)
