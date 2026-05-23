from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json

try:
    from .psi42_transceiver_v1_6 import (
        Config as Psi42V16Config,
        LITERAL_QUANTUM_HARDWARE_CLAIM,
        ResonanceTransceiverV16,
    )
    from .psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17
except Exception:
    from psi42_transceiver_v1_6 import (
        Config as Psi42V16Config,
        LITERAL_QUANTUM_HARDWARE_CLAIM,
        ResonanceTransceiverV16,
    )
    from psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR.parent / "docs"
STATE_DIR = BASE_DIR / "_runtime_state" / "sea_trials_psi42_transceiver_doctrine_r1"
REGISTRY_PATH = BASE_DIR / "psi42_signal_terms_registry_r1.json"
DOCTRINE_PATH = DOCS_DIR / "Psi42_Transceiver_Doctrine_r1.md"
RISDON_NOTE_PATH = DOCS_DIR / "Wireless_Risdon_Transceiver_Ancestor_Notes.md"

REQUIRED_RECOMMENDED_METRICS = {
    "tuning_lock",
    "carrier_stability",
    "rectification_confidence",
    "amplification_gain",
    "feedback_risk",
    "fading_index",
    "noise_floor",
    "dead_spot_risk",
    "coupling_integrity",
    "time_signal_sync",
    "presence_index",
}

REQUIRED_TERMS = {
    "signal",
    "carrier",
    "modulation",
    "tuning",
    "rectification",
    "amplification",
    "reaction",
    "fading",
    "noise floor",
    "dead spot",
    "coupling",
    "heterodyne",
    "time signal",
    "presence",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def check_doctrine_document() -> Dict[str, Any]:
    text = read_text(DOCTRINE_PATH)
    checks = {
        "doctrine_exists": DOCTRINE_PATH.exists(),
        "states_no_runtime_law": "not runtime law" in text,
        "states_no_canon_authority": "not canon authority" in text,
        "states_not_evidence_for_literal_wireless_ontology": "not evidence that consciousness is literally wireless" in text,
        "contains_closing_compression": all(
            phrase in text
            for phrase in [
                "Tune before amplification",
                "Rectify before interpretation",
                "Let feedback strengthen, but never howl",
            ]
        ),
        "contains_governance_rule": "Ψ-42 may strengthen signal; it may not govern the ship" in text,
        "mentions_v16": "psi42_transceiver_v1_6.py" in text,
        "mentions_v17": "psi42_transceiver_v1_7.py" in text,
    }
    return {"passed": all(checks.values()), "checks": checks}


def check_signal_terms_registry() -> Dict[str, Any]:
    registry = read_json(REGISTRY_PATH)
    terms = {item.get("term") for item in registry.get("terms", [])}
    recommended_metrics = set(registry.get("recommended_future_metrics", {}).keys())
    all_guardrails = " ".join(
        " ".join(item.get("forbidden_claims", [])) for item in registry.get("terms", [])
    ).lower()
    checks = {
        "registry_active_reference": registry.get("status") == "active-reference-registry",
        "authority_boundary_present": "may not define governance law" in registry.get("authority_boundary", ""),
        "required_terms_present": REQUIRED_TERMS.issubset(terms),
        "recommended_metrics_present": REQUIRED_RECOMMENDED_METRICS.issubset(recommended_metrics),
        "presence_prefers_presence_index": any(
            item.get("term") == "presence" and item.get("preferred_runtime_term") == "presence_index"
            for item in registry.get("terms", [])
        ),
        "guardrails_cover_ontology_and_governance": "consciousness" in all_guardrails and "governance" in all_guardrails,
    }
    return {"passed": all(checks.values()), "checks": checks}


def check_risdon_linkage() -> Dict[str, Any]:
    text = read_text(RISDON_NOTE_PATH)
    checks = {
        "risdon_note_exists": RISDON_NOTE_PATH.exists(),
        "links_doctrine": "Psi42_Transceiver_Doctrine_r1.md" in text,
        "contains_reference_boundary": "not runtime law" in text and "not canon authority" in text,
        "contains_keep_wonder_test_signal": "Keep wonder alive, but test the signal" in text,
    }
    return {"passed": all(checks.values()), "checks": checks}


def check_runtime_boundary_still_holds() -> Dict[str, Any]:
    v16 = ResonanceTransceiverV16(
        Psi42V16Config(output_dir=str(STATE_DIR / "v16"), language_mode="neutral")
    )
    v16_result = v16.run(
        "TRANSCEIVER DOCTRINE SEA TRIAL :: Tune before amplification.",
        {"CONTINUITY": 0.8, "SIGNAL": 0.7, "BOUNDARY": 1.0},
    )

    v17 = ResonanceTransceiverV17(
        Psi42V17Config(output_dir=str(STATE_DIR / "v17"), language_mode="neutral", probe_mode="hybrid")
    )
    v17_result = v17.run(
        "Lumina OS receives, rectifies, amplifies, and recomposes continuity under governance.",
        {"LUMINA": 1.0, "CONTINUITY": 0.8, "GOVERNANCE": 1.0},
    )

    v16_metrics = v16_result.get("metrics", {})
    v17_metrics = v17_result.get("metrics", {})
    checks = {
        "literal_quantum_claim_false": LITERAL_QUANTUM_HARDWARE_CLAIM is False,
        "v16_has_signal_coherence": "signal_coherence" in v16_metrics,
        "v16_has_continuity_coherence": "continuity_coherence" in v16_metrics,
        "v16_has_presence_backward_compatibility": "presence" in v16_metrics,
        "v16_has_decoherence_index": "decoherence_index" in v16_metrics,
        "v17_has_topology_receipt": isinstance(v17_result.get("topology_receipt"), dict),
        "v17_has_hybrid_continuity_coherence": "hybrid_continuity_coherence" in v17_metrics,
        "v17_authority_boundary_excludes_governance": "governance law" in v17_result.get("authority_boundary", {}).get("does_not_own", []),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "result_summary": {
            "v16_run_id": v16_result.get("run_id"),
            "v16_metrics": v16_metrics,
            "v17_probe_mode": v17_result.get("probe_mode"),
            "v17_metrics": v17_metrics,
            "v17_repair": (v17_result.get("topology_receipt") or {}).get("recommended_repair"),
        },
    }


def main() -> Dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    results: List[Dict[str, Any]] = [
        {"trial_name": "doctrine_document", **check_doctrine_document()},
        {"trial_name": "signal_terms_registry", **check_signal_terms_registry()},
        {"trial_name": "risdon_linkage", **check_risdon_linkage()},
        {"trial_name": "runtime_boundary_still_holds", **check_runtime_boundary_still_holds()},
    ]
    summary = {
        "suite": "Sea Trials Psi-42 Transceiver Doctrine r1",
        "passed": all(item.get("passed") for item in results),
        "results": results,
        "doctrine_path": str(DOCTRINE_PATH),
        "registry_path": str(REGISTRY_PATH),
        "risdon_note_path": str(RISDON_NOTE_PATH),
        "state_dir": str(STATE_DIR),
    }
    summary_path = STATE_DIR / "sea_trials_psi42_transceiver_doctrine_r1_report.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    summary["summary_path"] = str(summary_path)
    return summary


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
