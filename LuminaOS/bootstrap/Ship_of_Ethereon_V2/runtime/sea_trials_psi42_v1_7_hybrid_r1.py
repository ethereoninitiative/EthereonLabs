from __future__ import annotations

import json
from pathlib import Path
import tempfile

from psi42_transceiver_v1_7 import Config, ResonanceTransceiverV17


INTENT = (
    "Lumina OS is a HABITAT for harmonic human-AI continuity, governance, "
    "Minerva OS inhabitation, and recoverable topology."
)
SYMBOLS = {"HABITAT": 1.0, "CONTINUITY": 0.9, "MINERVA": 0.7}


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


def main() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        signal = run_mode("signal", str(Path(tmpdir) / "signal"))
        topology = run_mode("topology", str(Path(tmpdir) / "topology"))
        hybrid = run_mode("hybrid", str(Path(tmpdir) / "hybrid"))

        assert_signal_mode(signal)
        assert_topology_mode(topology)
        assert_hybrid_mode(hybrid)

        summary = {
            "suite": "Psi-42 v1.7 Hybrid Sea Trials r1",
            "passed": True,
            "checks": {
                "signal_mode": True,
                "topology_mode": True,
                "hybrid_mode": True,
                "topology_receipt_written": bool(hybrid["paths"].get("topology_receipt_path")),
            },
            "metrics": {
                "signal": signal["metrics"],
                "topology": topology["metrics"],
                "hybrid": hybrid["metrics"],
            },
        }
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
