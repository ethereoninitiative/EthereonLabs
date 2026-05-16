from __future__ import annotations

"""
psi42_transceiver_v1_7.py

Ψ-42 v1.7 is a hybrid signal-topology continuity transceiver.

It wraps the bounded v1.6 quantum-inspired classical signal transceiver and adds
relational topology continuity receipts from psi42_relational_topology_r1.

Authority boundary:
- Owns derived signal metrics, topology metrics, and restoration receipts only.
- Does not own canon state, governance law, mode legality, checkpoint legality,
  capability loading authority, or primary continuity authority.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional
import json

try:
    from .psi42_transceiver_v1_6 import Config as Psi42V16Config, ResonanceTransceiverV16
    from .psi42_relational_topology_r1 import (
        compare_topologies,
        extract_relational_topology,
        make_restoration_receipt,
        simulate_semantic_drift,
    )
except Exception:
    from psi42_transceiver_v1_6 import Config as Psi42V16Config, ResonanceTransceiverV16
    from psi42_relational_topology_r1 import (
        compare_topologies,
        extract_relational_topology,
        make_restoration_receipt,
        simulate_semantic_drift,
    )

INSTRUMENT_CLASS = "hybrid signal-topology continuity transceiver"
PUBLIC_SUMMARY = "A Psi-42 v1.7 wrapper that combines signal continuity metrics with relational topology restoration receipts."
PROTOCOL_VERSION = "psi42_hybrid_signal_topology_protocol_001"
VALID_PROBE_MODES = {"signal", "topology", "hybrid"}


@dataclass
class Config:
    seed: Optional[int] = 42
    duration_s: float = 0.8
    noise_sigma: float = 0.12
    language_mode: str = "ethereonic"
    probe_mode: str = "hybrid"
    output_dir: Optional[str] = None

    def to_v16(self) -> Psi42V16Config:
        return Psi42V16Config(
            seed=self.seed,
            duration_s=self.duration_s,
            noise_sigma=self.noise_sigma,
            language_mode=self.language_mode,
            protocol_version=PROTOCOL_VERSION,
            output_dir=self.output_dir,
        )


class ResonanceTransceiverV17:
    def __init__(self, cfg: Config):
        if cfg.probe_mode not in VALID_PROBE_MODES:
            raise ValueError(f"Invalid probe_mode {cfg.probe_mode!r}; expected one of {sorted(VALID_PROBE_MODES)}")
        self.cfg = cfg
        self.signal_transceiver = ResonanceTransceiverV16(cfg.to_v16())
        self._last_pulse: Optional[Dict[str, Any]] = None

    def _write_json(self, filename: str, payload: Dict[str, Any]) -> str:
        return self.signal_transceiver._write_json(filename, payload)

    def _topology_receipt(self, intent_text: str, symbol_maps: Dict[str, float]) -> Dict[str, Any]:
        original = extract_relational_topology(intent_text, symbol_maps)
        recovered_text = simulate_semantic_drift(intent_text)
        recovered = extract_relational_topology(recovered_text, symbol_maps)
        comparison = compare_topologies(original, recovered)
        receipt = make_restoration_receipt(original, recovered, comparison)
        receipt["instrument_class"] = INSTRUMENT_CLASS
        receipt["protocol_version"] = PROTOCOL_VERSION
        receipt["probe_mode"] = self.cfg.probe_mode
        receipt["semantic_drift_simulation"] = {
            "original_text": intent_text,
            "recovered_text": recovered_text,
        }
        return receipt

    def run(self, intent_text: str, symbol_maps: Dict[str, float]) -> Dict[str, Any]:
        signal_result: Optional[Dict[str, Any]] = None
        topology_receipt: Optional[Dict[str, Any]] = None

        if self.cfg.probe_mode in {"signal", "hybrid"}:
            signal_result = self.signal_transceiver.run(intent_text, symbol_maps)

        if self.cfg.probe_mode in {"topology", "hybrid"}:
            topology_receipt = self._topology_receipt(intent_text, symbol_maps)
            topology_path = self._write_json("psi42_relational_restoration_v1_7.json", topology_receipt)
        else:
            topology_path = None

        metrics: Dict[str, float] = {}
        if signal_result is not None:
            metrics.update(signal_result.get("metrics", {}))
        if topology_receipt is not None:
            metrics.update(topology_receipt.get("comparison", {}).get("metrics", {}))
            if "continuity_coherence" in metrics and "HRC" in metrics:
                metrics["hybrid_continuity_coherence"] = round(
                    (0.55 * float(metrics["continuity_coherence"])) + (0.45 * float(metrics["HRC"])),
                    4,
                )

        result = {
            "instrument_class": INSTRUMENT_CLASS,
            "public_summary": PUBLIC_SUMMARY,
            "protocol_version": PROTOCOL_VERSION,
            "probe_mode": self.cfg.probe_mode,
            "signal_result": signal_result,
            "topology_receipt": topology_receipt,
            "metrics": metrics,
            "paths": {
                "topology_receipt_path": topology_path,
                **((signal_result or {}).get("paths", {})),
            },
            "authority_boundary": {
                "owns": ["derived signal metrics", "derived topology metrics", "restoration receipts"],
                "does_not_own": [
                    "canon state",
                    "governance law",
                    "mode legality",
                    "checkpoint legality",
                    "capability loading authority",
                    "primary continuity authority",
                ],
            },
        }
        self._last_pulse = result
        return result


if __name__ == "__main__":
    cfg = Config(probe_mode="hybrid")
    rt = ResonanceTransceiverV17(cfg)
    res = rt.run(
        "Lumina OS is a HABITAT for harmonic human-AI continuity, governance, and Minerva OS inhabitation.",
        {"HABITAT": 1.0, "CONTINUITY": 0.9, "MINERVA": 0.7},
    )
    print(json.dumps(res, indent=2))
