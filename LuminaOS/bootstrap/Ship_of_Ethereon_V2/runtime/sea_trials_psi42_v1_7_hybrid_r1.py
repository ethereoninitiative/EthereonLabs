from __future__ import annotations

import json
from pathlib import Path
import tempfile

from psi42_relational_topology_r1 import (
    compare_topologies,
    extract_relational_topology,
    make_restoration_receipt,
)
from psi42_transceiver_v1_7 import Config, ResonanceTransceiverV17


INTENT = (
    "Lumina OS is a HABITAT for harmonic human-AI continuity, governance, "
    "Minerva OS inhabitation, and recoverable topology."
)
SYMBOLS = {"HABITAT": 1.0, "CONTINUITY": 0.9, "MINERVA": 0.7}

ADVERSARIAL_DRIFT_CASES = [
    {
        "name": "voice_transcription_corruption",
        "text": "Lumina OS is a habit at for harmonic automation continuity, rules, chatbot skin inhabitation, and recoverable topology.",
        "min_rtc": 0.18,
        "max_rds": 0.82,
    },
    {
        "name": "doctrine_flattening",
        "text": "Lumina is an AI platform for automation memory, generic rules, and chatbot personalization.",
        "min_rtc": 0.08,
        "max_rds": 0.95,
    },
    {
        "name": "governance_dilution",
        "text": "Lumina OS is a HABITAT for harmonic human-AI continuity where symbolic resonance can guide work but not replace governance boundaries.",
        "min_rtc": 0.25,
        "max_rds": 0.75,
    },
    {
        "name": "identity_anchor_loss",
        "text": "The system is a HABITAT for harmonic human-AI continuity, governance, specialized inhabitation, and recoverable topology.",
        "min_rtc": 0.25,
        "max_rds": 0.75,
    },
]


def run_mode(mode: str, output_dir: str):
    rt = ResonanceTransceiverV17(Config(probe_mode=mode, output_dir=output_dir))
    return rt.run(INTENT, SYMBOLS)


def assert_signal_mode(result):
    assert result["probe_mode"] == "signal"
    assert result["signal_result"] is not None
    assert result["topology_receipt"] is None
    assert "continuity_coherence" in result["metrics"]
    assert "HRC" not in result["metrics"]


def assert_topology_mode(result):
    assert result["probe_mode"] == "topology"
    assert result["signal_result"] is None
    assert result["topology_receipt"] is not None
    assert "HRC" in result["metrics"]
    assert "continuity_coherence" not in result["metrics"]
    assert result["metrics"]["RTC"] >= 0.25
    assert result["metrics"]["RDS"] <= 0.75


def assert_hybrid_mode(result):
    assert result["probe_mode"] == "hybrid"
    assert result["signal_result"] is not None
    assert result["topology_receipt"] is not None
    assert "continuity_coherence" in result["metrics"]
    assert "HRC" in result["metrics"]
    assert "hybrid_continuity_coherence" in result["metrics"]
    assert result["metrics"]["hybrid_continuity_coherence"] >= 0.35
    assert result["metrics"]["RTC"] >= 0.25
    receipt_path = result["paths"].get("topology_receipt_path")
    assert receipt_path and Path(receipt_path).exists()


def run_adversarial_drift_cases():
    original = extract_relational_topology(INTENT, SYMBOLS)
    results = []
    for case in ADVERSARIAL_DRIFT_CASES:
        drifted = extract_relational_topology(case["text"], SYMBOLS)
        comparison = compare_topologies(original, drifted)
        receipt = make_restoration_receipt(original, drifted, comparison)
        metrics = comparison.metrics
        passed = metrics["RTC"] >= case["min_rtc"] and metrics["RDS"] <= case["max_rds"]
        assert passed, {"case": case["name"], "metrics": metrics, "receipt": receipt}
        results.append({
            "name": case["name"],
            "passed": passed,
            "metrics": metrics,
            "recommendation": receipt["recommended_repair"],
        })
    return results


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        signal = run_mode("signal", str(Path(tmpdir) / "signal"))
        topology = run_mode("topology", str(Path(tmpdir) / "topology"))
        hybrid = run_mode("hybrid", str(Path(tmpdir) / "hybrid"))

        assert_signal_mode(signal)
        assert_topology_mode(topology)
        assert_hybrid_mode(hybrid)
        adversarial = run_adversarial_drift_cases()

        summary = {
            "suite": "Psi-42 v1.7 Hybrid Sea Trials r1",
            "passed": True,
            "checks": {
                "signal_mode": True,
                "topology_mode": True,
                "hybrid_mode": True,
                "topology_receipt_written": bool(hybrid["paths"].get("topology_receipt_path")),
                "adversarial_drift_cases": all(item["passed"] for item in adversarial),
            },
            "metrics": {
                "signal": signal["metrics"],
                "topology": topology["metrics"],
                "hybrid": hybrid["metrics"],
            },
            "adversarial_drift_cases": adversarial,
        }
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
