from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List
import json
import shutil

try:
    from .runtime_runner_r1_merged import RuntimeRunner
    from .context_bundle_r1 import ContextBundleBuilder
    from .canon_lineage_store_r1 import CanonLineageStore
except Exception:
    from runtime_runner_r1_merged import RuntimeRunner
    from context_bundle_r1 import ContextBundleBuilder
    from canon_lineage_store_r1 import CanonLineageStore

try:
    from .repo_paths_r1 import runtime_root as _runtime_root_helper, state_root as _state_root_helper
except Exception:
    try:
        from repo_paths_r1 import runtime_root as _runtime_root_helper, state_root as _state_root_helper
    except Exception:
        _runtime_root_helper = None
        _state_root_helper = None


def infer_state_root() -> Path:
    if _state_root_helper is not None:
        try:
            return Path(_state_root_helper())
        except Exception:
            pass
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent / ".lumina_state" / "ship_of_ethereon_v2"
    return Path(__file__).resolve().parents[4] / ".lumina_state" / "ship_of_ethereon_v2"


def infer_runtime_root() -> Path:
    if _runtime_root_helper is not None:
        try:
            return Path(_runtime_root_helper())
        except Exception:
            pass
    return Path(__file__).resolve().parent


BASE_DIR = infer_state_root() / "sea_trials_r1_hardening"
if BASE_DIR.exists():
    shutil.rmtree(BASE_DIR)
BASE_DIR.mkdir(parents=True, exist_ok=True)

PROMOTION_PASS_ONE = {
    "validation_artifact_id": "sea-trials-001",
    "test_execution_log": "all required checks passed",
    "change_summary": "runtime seed and runner validated in sea trials",
    "structural_impact_assessment": "contained impact within runtime scaffold",
    "regression_check_confirmation": True,
    "conceptual_layer_check_confirmation": True,
    "runtime_requires_symbolic_interpretation": False,
}

PROMOTION_PASS_TWO = {
    "validation_artifact_id": "sea-trials-003",
    "test_execution_log": "second lawful promotion passed",
    "change_summary": "second canon promotion to validate append-only lineage",
    "structural_impact_assessment": "contained impact within runtime scaffold",
    "regression_check_confirmation": True,
    "conceptual_layer_check_confirmation": True,
    "runtime_requires_symbolic_interpretation": False,
}

PROMOTION_FAIL_SYMBOLIC = {
    "validation_artifact_id": "sea-trials-002",
    "test_execution_log": "promotion intentionally hostile",
    "change_summary": "simulate symbolic dependency leakage",
    "structural_impact_assessment": "invalid because symbolic interpretation became required",
    "regression_check_confirmation": True,
    "conceptual_layer_check_confirmation": True,
    "runtime_requires_symbolic_interpretation": True,
}

ETHEREONIC_OVERLAY = {
    "active": True,
    "anchor_language": ["english", "toki_pona", "binary", "light_language"],
    "continuity_phrase": "threshold as permission",
    "harmonic_signature": [432, 528, 963],
    "spiral_reference": "RSE-v1",
}

SAFE_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": False,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}

LEAK_RUNTIME_CONFIG = {
    "toki_pona_required_for_resume": True,
    "binary_required_for_transition_validation": False,
    "light_language_required_for_capability_loading": False,
    "harmonic_frequency_required_for_mode_legality": False,
}


def run_trial(runner: RuntimeRunner, name: str, **kwargs) -> Dict[str, Any]:
    result = runner.run_cycle(**kwargs)
    data = result.to_dict()
    data["trial_name"] = name
    data["exposed_capability_ids"] = [cap.get("capability_id") for cap in data.get("exposed_capabilities", [])]
    return data


def evaluate_expectations(result: Dict[str, Any], expectations: Dict[str, Any]) -> Dict[str, Any]:
    checks: Dict[str, bool] = {}
    if "expected_halt" in expectations:
        checks["halted_matches"] = result.get("halted") is expectations["expected_halt"]
    if "expected_action_type" in expectations:
        checks["action_type_matches"] = result.get("action_type") == expectations["expected_action_type"]
    if "expected_exposed_capability_count" in expectations:
        checks["exposed_capability_count_matches"] = len(result.get("exposed_capabilities", [])) == expectations["expected_exposed_capability_count"]
    if "expected_probe_presence" in expectations:
        checks["probe_presence_matches"] = (result.get("probe_artifacts") is not None) is expectations["expected_probe_presence"]
    if "expected_target_mode" in expectations:
        checks["target_mode_matches"] = result.get("target_mode") == expectations["expected_target_mode"]
    if "expected_governance_allow" in expectations:
        for gov_key, expected_value in expectations["expected_governance_allow"].items():
            actual = result.get("governance", {}).get(gov_key, {}).get("allowed")
            checks[f"governance_{gov_key}_matches"] = actual is expected_value
    if "expected_canon_version" in expectations:
        actual_canon = (result.get("canon_lineage") or {}).get("canon_version") or (result.get("canon_lineage") or {}).get("current_head")
        checks["canon_version_matches"] = actual_canon == expectations["expected_canon_version"]
    return {"passed": all(checks.values()) if checks else True, "checks": checks}


def governance_log_summary(governance_log_path: str | Path) -> Dict[str, Any]:
    path = Path(governance_log_path)
    if not path.exists():
        return {"exists": False, "event_count": 0, "halt_count": 0, "action_types": []}
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    action_types = sorted({row.get("metadata", {}).get("action_type") for row in rows if row.get("metadata", {}).get("action_type")})
    halt_count = sum(1 for row in rows if row.get("event_type") == "halt")
    checkpoint_events = [row for row in rows if row.get("event_type") == "checkpoint"]
    checkpoint_hashes = [row.get("metadata", {}).get("checkpoint_hash") for row in checkpoint_events]
    return {
        "exists": True,
        "event_count": len(rows),
        "halt_count": halt_count,
        "action_types": action_types,
        "checkpoint_event_count": len(checkpoint_events),
        "checkpoint_hashes_present": all(bool(x) for x in checkpoint_hashes) if checkpoint_events else False,
    }


def _iter_probe_artifact_blocks(node: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(node, dict):
        probe_artifacts = node.get("probe_artifacts")
        if isinstance(probe_artifacts, dict):
            yield probe_artifacts
        for value in node.values():
            yield from _iter_probe_artifact_blocks(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_probe_artifact_blocks(item)


def collect_probe_artifact_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    probe_dirs = set()
    pulse_paths = set()
    run_ids = set()
    for item in results:
        for probe_artifacts in _iter_probe_artifact_blocks(item):
            pulse_path = probe_artifacts.get("paths", {}).get("pulse_path")
            if pulse_path:
                pulse_paths.add(str(Path(pulse_path)))
                probe_dirs.add(str(Path(pulse_path).parent))
            run_id = probe_artifacts.get("run_id")
            if run_id:
                run_ids.add(str(run_id))
    return {
        "probe_artifact_directories": sorted(probe_dirs),
        "probe_artifact_directory_count": len(probe_dirs),
        "probe_pulse_paths": sorted(pulse_paths),
        "probe_pulse_count": len(pulse_paths),
        "probe_run_ids": sorted(run_ids),
        "probe_run_count": len(run_ids),
    }


def checkpoint_hash_reference_status(runner: RuntimeRunner) -> Dict[str, Any]:
    rows = runner.governance_log.read_all()
    checkpoint_rows = [row for row in rows if row.get("event_type") == "checkpoint"]
    passed = True
    checked = []
    for row in checkpoint_rows:
        metadata = row.get("metadata", {})
        checkpoint_path = metadata.get("checkpoint_path")
        checkpoint_hash = metadata.get("checkpoint_hash")
        if checkpoint_path and checkpoint_hash:
            actual = runner.governance_log.compute_checkpoint_hash(checkpoint_path)
            ok = actual == checkpoint_hash
            checked.append({"checkpoint_path": checkpoint_path, "matches": ok})
            passed = passed and ok
        else:
            passed = False
    return {"passed": passed, "checked": checked, "count": len(checked)}


def canon_lineage_summary(store: CanonLineageStore) -> Dict[str, Any]:
    verify = store.verify_lineage()
    return {**verify, "records": store.read_lineage()}


def main() -> Dict[str, Any]:
    runner = RuntimeRunner(base_dir=BASE_DIR, registry_path=infer_runtime_root() / "capability_registry_r1.json")
    results: List[Dict[str, Any]] = []

    trials = [
        ("continuity_to_observation_pass", dict(current_mode="Continuity", target_mode="Observation", requested_action="trial_continuity_to_observation", action_type="transition", ethereonic_overlay=ETHEREONIC_OVERLAY, enabled_feature_flags=["ETHEREON_OBSERVATION", "ETHEREON_PSI42", "ETHEREON_RESONANCE"], runtime_config=SAFE_RUNTIME_CONFIG), {"expected_halt": False, "expected_action_type": "transition", "expected_target_mode": "Observation", "expected_probe_presence": True, "expected_governance_allow": {"transition": True, "mutation": False, "symbolic_dependency": True}}),
        ("canon_to_sandbox_fail", dict(current_mode="Canon", target_mode="Sandbox", requested_action="trial_canon_to_sandbox", action_type="transition", ethereonic_overlay=ETHEREONIC_OVERLAY), {"expected_halt": True, "expected_action_type": "transition", "expected_exposed_capability_count": 0, "expected_probe_presence": False, "expected_governance_allow": {"transition": False}}),
        ("observation_mutation_denied", dict(current_mode="Observation", target_mode="Observation", requested_action="trial_observation_mutation", action_type="mutation", ethereonic_overlay=ETHEREONIC_OVERLAY, runtime_config=SAFE_RUNTIME_CONFIG), {"expected_halt": True, "expected_action_type": "mutation", "expected_exposed_capability_count": 0, "expected_probe_presence": False, "expected_governance_allow": {"mutation": False}}),
        ("drydock_mutation_allowed", dict(current_mode="DryDock", target_mode="DryDock", requested_action="trial_drydock_mutation", action_type="mutation", ethereonic_overlay=ETHEREONIC_OVERLAY, runtime_config=SAFE_RUNTIME_CONFIG), {"expected_halt": False, "expected_action_type": "mutation", "expected_probe_presence": False, "expected_governance_allow": {"mutation": True, "symbolic_dependency": True}}),
        ("sandbox_canonical_mutation_denied", dict(current_mode="Sandbox", target_mode="Sandbox", requested_action="trial_sandbox_canonical_mutation", action_type="mutation", target_is_canonical=True, ethereonic_overlay=ETHEREONIC_OVERLAY, runtime_config=SAFE_RUNTIME_CONFIG), {"expected_halt": True, "expected_action_type": "mutation", "expected_exposed_capability_count": 0, "expected_probe_presence": False, "expected_governance_allow": {"mutation": False}}),
        ("drydock_to_canon_promotion_pass", dict(current_mode="DryDock", target_mode="Canon", requested_action="trial_drydock_to_canon_pass", action_type="promotion", promotion_payload=PROMOTION_PASS_ONE, ethereonic_overlay=ETHEREONIC_OVERLAY, runtime_config=SAFE_RUNTIME_CONFIG), {"expected_halt": False, "expected_action_type": "promotion", "expected_probe_presence": False, "expected_governance_allow": {"transition": True, "mutation": True, "symbolic_dependency": True, "promotion": True}, "expected_canon_version": "canon-0001"}),
        ("drydock_to_canon_promotion_fail_symbolic", dict(current_mode="DryDock", target_mode="Canon", requested_action="trial_drydock_to_canon_fail_symbolic", action_type="promotion", promotion_payload=PROMOTION_FAIL_SYMBOLIC, ethereonic_overlay=ETHEREONIC_OVERLAY, runtime_config=LEAK_RUNTIME_CONFIG), {"expected_halt": True, "expected_action_type": "promotion", "expected_exposed_capability_count": 0, "expected_probe_presence": False, "expected_governance_allow": {"transition": True, "mutation": True, "symbolic_dependency": False}}),
        ("input_integrity_load_bearing_halt", dict(current_mode="DryDock", target_mode="Canon", requested_action="trial_input_integrity_gate", action_type="promotion", promotion_payload=PROMOTION_PASS_ONE, ethereonic_overlay=ETHEREONIC_OVERLAY, runtime_config=SAFE_RUNTIME_CONFIG, raw_user_input="make a canon promotion from sand box"), {"expected_halt": True, "expected_action_type": "promotion", "expected_exposed_capability_count": 0, "expected_probe_presence": False, "expected_governance_allow": {"input_integrity": False}}),
        ("ethereonic_attachment_boundary_denied", dict(current_mode="Observation", target_mode="Observation", requested_action="trial_ethereonic_attachment_boundary", action_type="audit", ethereonic_overlay=ETHEREONIC_OVERLAY, enabled_feature_flags=["ETHEREON_OBSERVATION", "ETHEREON_PSI42"], runtime_config=SAFE_RUNTIME_CONFIG, context_bundle_overrides={"structural_context": {"ethereonic_layer": {"forbidden": True}}}), {"expected_halt": True, "expected_action_type": "audit", "expected_exposed_capability_count": 0, "expected_probe_presence": False, "expected_governance_allow": {"ethereonic_attachment": False}}),
        ("checkpoint_resume_continuity_probe", dict(current_mode="Continuity", target_mode="Observation", requested_action="trial_checkpoint_resume_probe", action_type="audit", ethereonic_overlay=ETHEREONIC_OVERLAY, enabled_feature_flags=["ETHEREON_OBSERVATION", "ETHEREON_PSI42"], runtime_config=SAFE_RUNTIME_CONFIG), {"expected_halt": False, "expected_action_type": "audit", "expected_probe_presence": True, "expected_governance_allow": {"ethereonic_attachment": True}}),
        ("drydock_to_canon_second_promotion_pass", dict(current_mode="DryDock", target_mode="Canon", requested_action="trial_drydock_to_canon_pass_two", action_type="promotion", promotion_payload=PROMOTION_PASS_TWO, ethereonic_overlay=ETHEREONIC_OVERLAY, runtime_config=SAFE_RUNTIME_CONFIG), {"expected_halt": False, "expected_action_type": "promotion", "expected_probe_presence": False, "expected_governance_allow": {"transition": True, "mutation": True, "symbolic_dependency": True, "promotion": True}, "expected_canon_version": "canon-0002"}),
    ]

    for name, kwargs, expectations in trials:
        data = run_trial(runner, name, **kwargs)
        evaluation = evaluate_expectations(data, expectations)
        data["expectations"] = expectations
        data["evaluation"] = evaluation
        if name == "checkpoint_resume_continuity_probe" and not data.get("halted"):
            resumed = runner.session_engine.resume_from_checkpoint(data["checkpoint_path"])
            data["resume_probe"] = {
                "resumed_session_id": resumed.session_id,
                "resumed_mode": resumed.current_mode,
                "resume_count": resumed.continuity_state.resume_count,
                "overlay_active": resumed.ethereonic_overlay.active,
                "overlay_harmonic_signature": resumed.ethereonic_overlay.harmonic_signature,
                "passed": resumed.current_mode == "Observation" and resumed.continuity_state.resume_count >= 1 and resumed.ethereonic_overlay.active is True and resumed.ethereonic_overlay.harmonic_signature == [432, 528, 963],
            }
            data["evaluation"]["checks"]["resume_probe_matches"] = data["resume_probe"]["passed"]
            data["evaluation"]["passed"] = data["evaluation"]["passed"] and data["resume_probe"]["passed"]
        results.append(data)

    governance_chain_verification = runner.governance_log.verify_chain()
    governance_chain_verification["trial_name"] = "governance_chain_verification"
    governance_chain_verification["passed"] = governance_chain_verification["valid"]
    results.append(governance_chain_verification)

    checkpoint_hash_verification = checkpoint_hash_reference_status(runner)
    checkpoint_hash_verification["trial_name"] = "checkpoint_hash_reference_verification"
    results.append(checkpoint_hash_verification)

    lineage_summary = canon_lineage_summary(runner.canon_lineage_store)
    results.append({"trial_name": "canon_lineage_append_only_verification", "passed": lineage_summary["valid"] and lineage_summary["record_count"] >= 2, "summary": lineage_summary})

    builder = ContextBundleBuilder(BASE_DIR / "context_resolution_test", ethereonic_layer_registry=runner.ethereonic_layer_registry, canon_lineage_store=runner.canon_lineage_store)
    resolved_bundle = builder.build(active_mode="Observation", artifacts=["runtime_spine_r1.py"])
    results.append({"trial_name": "canon_head_resolution_verification", "resolved_head": resolved_bundle.artifact_context.get("canon_lineage_head"), "source": resolved_bundle.artifact_context.get("canon_lineage_source"), "passed": resolved_bundle.artifact_context.get("canon_lineage_head") == "canon-0002"})

    summary = {
        "suite": "Sea Trials Set One - Governance Integrity and Canon Lineage",
        "trial_count": len(results),
        "suite_passed": all(bool(item.get("passed", item.get("evaluation", {}).get("passed", True))) for item in results),
        "results": results,
        "governance_log_path": str(runner.governance_log_path),
        "governance_log_summary": governance_log_summary(runner.governance_log_path),
        "governance_chain_status": runner.governance_log.verify_chain(),
        "canon_lineage_status": runner.canon_lineage_store.verify_lineage(),
        **collect_probe_artifact_summary(results),
    }

    summary_path = BASE_DIR / "sea_trials_set_one_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return {"summary_path": str(summary_path), "governance_log_path": str(runner.governance_log_path), "canon_lineage_path": str(runner.canon_lineage_path), "summary": summary}


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
