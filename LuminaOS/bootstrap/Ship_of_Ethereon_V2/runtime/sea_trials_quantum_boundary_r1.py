from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import importlib.util
import json
import shutil

try:
    from .psi42_transceiver_v1_6 import (
        Config as Psi42Config,
        INSTRUMENT_CLASS,
        LITERAL_QUANTUM_HARDWARE_CLAIM,
        ResonanceTransceiverV16,
    )
except Exception:
    from psi42_transceiver_v1_6 import (
        Config as Psi42Config,
        INSTRUMENT_CLASS,
        LITERAL_QUANTUM_HARDWARE_CLAIM,
        ResonanceTransceiverV16,
    )


BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / "_runtime_state" / "sea_trials_quantum_boundary_r1"
REGISTRY_PATH = BASE_DIR / "quantum_concepts_registry_r1.json"
BRANCH_MODEL_PATH = BASE_DIR / "branch_resolution_model_r1.json"


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_registry(registry: Dict[str, Any]) -> Dict[str, Any]:
    designation = registry.get("formal_designations", {}).get("psi42_transceiver_v16", {})
    terms = {item.get("term"): item for item in registry.get("terms", [])}
    checks = {
        "registry_active": registry.get("status") == "active-boundary-registry",
        "psi42_designation_matches": designation.get("instrument_class") == "quantum-inspired classical signal transceiver",
        "psi42_literal_quantum_false": designation.get("literal_quantum_hardware_claim") is False,
        "superposition_prefers_branch_ensemble": terms.get("superposition", {}).get("preferred_runtime_term") == "branch_ensemble",
        "collapse_prefers_resolution": terms.get("collapse", {}).get("preferred_runtime_term") == "resolution",
        "coherence_requires_namespace": terms.get("coherence", {}).get("preferred_runtime_term") == "namespaced_coherence",
        "decoherence_defined": terms.get("decoherence", {}).get("preferred_runtime_term") == "decoherence_index",
    }
    return {"passed": all(checks.values()), "checks": checks}


def check_branch_model(model: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "model_active": model.get("status") == "active-advisory-model",
        "quantum_claim_false": model.get("quantum_claim") is False,
        "superposition_alias_replaced": model.get("preferred_terms", {}).get("superposition_state") == "branch_ensemble",
        "collapse_alias_replaced": model.get("preferred_terms", {}).get("collapse_rule") == "resolution_rule",
        "basis_has_consent": "human_consent" in model.get("default_measurement_basis", {}),
        "halt_conditions_include_symbolic_leakage": "symbolic_dependency_leakage_detected" in model.get("resolution_rule", {}).get("halt_conditions", []),
    }
    return {"passed": all(checks.values()), "checks": checks}


def check_psi42_output() -> Dict[str, Any]:
    if STATE_DIR.exists():
        shutil.rmtree(STATE_DIR)
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    rt = ResonanceTransceiverV16(Psi42Config(output_dir=str(STATE_DIR), language_mode="neutral"))
    result = rt.run("QUANTUM BOUNDARY SEA TRIAL", {"CONTINUITY": 0.8, "BOUNDARY": 1.0})

    pulse_path = Path(result["paths"]["pulse_path"])
    pulse = read_json(pulse_path)

    metrics = result.get("metrics", {})
    checks = {
        "instrument_class_constant_matches": INSTRUMENT_CLASS == "quantum-inspired classical signal transceiver",
        "literal_quantum_claim_false": LITERAL_QUANTUM_HARDWARE_CLAIM is False,
        "result_instrument_class_matches": result.get("instrument_class") == INSTRUMENT_CLASS,
        "pulse_instrument_class_matches": pulse.get("instrument_class") == INSTRUMENT_CLASS,
        "measurement_basis_present": isinstance(result.get("measurement_basis"), dict) and "human_consent" in result.get("measurement_basis", {}),
        "signal_coherence_present": "signal_coherence" in metrics,
        "continuity_coherence_present": "continuity_coherence" in metrics,
        "conceptual_coherence_present": "conceptual_coherence" in metrics,
        "governance_coherence_present": "governance_coherence" in metrics,
        "decoherence_index_present": "decoherence_index" in metrics,
        "pulse_decoherence_present": "decoherence_index" in pulse,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "result_summary": {
            "run_id": result.get("run_id"),
            "instrument_class": result.get("instrument_class"),
            "metrics": metrics,
            "pulse_path": str(pulse_path),
        },
    }


def main() -> Dict[str, Any]:
    registry = read_json(REGISTRY_PATH)
    branch_model = read_json(BRANCH_MODEL_PATH)

    results: List[Dict[str, Any]] = [
        {"trial_name": "quantum_concepts_registry", **check_registry(registry)},
        {"trial_name": "branch_resolution_model", **check_branch_model(branch_model)},
        {"trial_name": "psi42_output_contract", **check_psi42_output()},
    ]

    summary = {
        "suite": "Sea Trials Quantum Boundary r1",
        "passed": all(item.get("passed") for item in results),
        "results": results,
        "registry_path": str(REGISTRY_PATH),
        "branch_model_path": str(BRANCH_MODEL_PATH),
        "state_dir": str(STATE_DIR),
    }

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = STATE_DIR / "sea_trials_quantum_boundary_r1_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    summary["summary_path"] = str(summary_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
