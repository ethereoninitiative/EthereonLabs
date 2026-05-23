from __future__ import annotations

"""
psi42_transceiver_v1_8.py

Ψ-42 v1.8 is a doctrine-aligned transceiver diagnostics wrapper.

It wraps the bounded v1.7 hybrid signal-topology transceiver and adds the
wireless/transceiver-derived diagnostic fields introduced by
Psi42_Transceiver_Doctrine_r1.md and psi42_signal_terms_registry_r1.json.

Authority boundary:
- Owns derived transceiver diagnostics, signal metrics, topology metrics, and
  restoration receipts only.
- Does not own canon state, governance law, mode legality, checkpoint legality,
  capability loading authority, human consent, or primary continuity authority.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json
import time
import uuid

try:
    from .psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17
except Exception:
    from psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17


INSTRUMENT_CLASS = "doctrine-aligned transceiver diagnostics wrapper"
PUBLIC_SUMMARY = "A Psi-42 v1.8 wrapper that adds tuning, carrier, rectification, amplification, feedback, fading, noise, coupling, and time-signal diagnostics."
PROTOCOL_VERSION = "psi42_doctrine_aligned_transceiver_protocol_001"
VALID_PROBE_MODES = {"signal", "topology", "hybrid"}


@dataclass
class Config:
    seed: Optional[int] = 42
    duration_s: float = 0.8
    noise_sigma: float = 0.12
    language_mode: str = "ethereonic"
    probe_mode: str = "hybrid"
    output_dir: Optional[str] = None
    isolate_run_artifacts: bool = True

    def to_v17(self, output_dir: Optional[str]) -> Psi42V17Config:
        return Psi42V17Config(
            seed=self.seed,
            duration_s=self.duration_s,
            noise_sigma=self.noise_sigma,
            language_mode=self.language_mode,
            probe_mode=self.probe_mode,
            output_dir=output_dir,
        )


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(float(value), high))


def _round(value: float) -> float:
    return round(_clamp(value), 4)


def _safe_metric(metrics: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(metrics.get(key, default))
    except Exception:
        return default


class ResonanceTransceiverV18:
    def __init__(self, cfg: Config):
        if cfg.probe_mode not in VALID_PROBE_MODES:
            raise ValueError(f"Invalid probe_mode {cfg.probe_mode!r}; expected one of {sorted(VALID_PROBE_MODES)}")
        self.cfg = cfg
        self._last_pulse: Optional[Dict[str, Any]] = None

    def _base_output_dir(self) -> Path:
        if self.cfg.output_dir:
            return Path(self.cfg.output_dir)
        return Path(__file__).resolve().parent / "_runtime_state" / "psi42_v1_8"

    def _run_output_dir(self, run_id: str) -> Path:
        base = self._base_output_dir()
        if self.cfg.isolate_run_artifacts:
            return base / run_id
        return base

    def _write_json(self, output_dir: Path, filename: str, payload: Dict[str, Any]) -> str:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return str(path)

    def _derive_drift_profile(self, diagnostics: Dict[str, float]) -> str:
        if diagnostics["feedback_risk"] >= 0.70:
            return "feedback_risk"
        if diagnostics["dead_spot_risk"] >= 0.65:
            return "dead_spot_risk"
        if diagnostics["noise_floor"] >= 0.55:
            return "high_noise_floor"
        if diagnostics["fading_index"] >= 0.45:
            return "fading_recoverable"
        if diagnostics["tuning_lock"] >= 0.70 and diagnostics["coupling_integrity"] >= 0.70:
            return "well_tuned"
        return "mixed_signal"

    def _diagnostics(self, v17_result: Dict[str, Any]) -> Dict[str, float]:
        metrics = dict(v17_result.get("metrics") or {})
        signal_result = v17_result.get("signal_result") or {}
        signal_metrics = signal_result.get("metrics") or metrics
        topology_receipt = v17_result.get("topology_receipt") or {}
        topology_metrics = ((topology_receipt.get("comparison") or {}).get("metrics") or {})
        frame = signal_result.get("frame") or {}
        adaptive_probe = signal_result.get("adaptive_probe") or {}
        mid_probe = adaptive_probe.get("mid_probe_measurements") or {}
        recomposition = signal_result.get("recomposition") or {}

        lock = _safe_metric(signal_metrics, "alignment_strength", _safe_metric(signal_metrics, "lock", 0.0))
        presence = _safe_metric(signal_metrics, "presence", 0.0)
        signal_coherence = _safe_metric(signal_metrics, "signal_coherence", 0.0)
        continuity_coherence = _safe_metric(signal_metrics, "continuity_coherence", 0.0)
        conceptual_coherence = _safe_metric(signal_metrics, "conceptual_coherence", 0.0)
        governance_coherence = _safe_metric(signal_metrics, "governance_coherence", 1.0)
        decoherence_index = _safe_metric(signal_metrics, "decoherence_index", 0.0)
        context_decoherence_risk = _safe_metric(signal_metrics, "context_decoherence_risk", decoherence_index)
        recomposition_decoherence = _safe_metric(signal_metrics, "recomposition_decoherence", 1.0 - _safe_metric(signal_metrics, "RF", 0.0))
        rf = _safe_metric(signal_metrics, "RF", 1.0 - recomposition_decoherence)
        crs = _safe_metric(signal_metrics, "CRS", continuity_coherence)
        hrc = _safe_metric(topology_metrics, "HRC", _safe_metric(metrics, "HRC", continuity_coherence))
        rtc = _safe_metric(topology_metrics, "RTC", _safe_metric(metrics, "RTC", continuity_coherence))
        rds = _safe_metric(topology_metrics, "RDS", _safe_metric(metrics, "RDS", 1.0 - rtc))
        anchor_coherence = _safe_metric(topology_metrics, "anchor_coherence", hrc)
        symbol_energy = _safe_metric(frame, "symbol_energy", 0.0)
        mid_probe_lock = _safe_metric(mid_probe, "lock", lock)

        tuning_lock = (0.46 * lock) + (0.24 * continuity_coherence) + (0.18 * anchor_coherence) + (0.12 * conceptual_coherence)
        carrier_stability = (0.40 * continuity_coherence) + (0.30 * rf) + (0.20 * (1.0 - decoherence_index)) + (0.10 * hrc)
        rectification_confidence = (0.40 * governance_coherence) + (0.25 * (1.0 - context_decoherence_risk)) + (0.20 * signal_coherence) + (0.15 * lock)
        amplification_gain = max(0.0, lock - mid_probe_lock) + max(0.0, crs - (continuity_coherence * 0.92))
        amplification_gain = min(amplification_gain, 1.0)
        feedback_risk = (0.35 * amplification_gain) + (0.25 * decoherence_index) + (0.20 * symbol_energy / 3.0) + (0.20 * max(0.0, lock - signal_coherence))
        fading_index = (0.45 * context_decoherence_risk) + (0.25 * rds) + (0.20 * recomposition_decoherence) + (0.10 * (1.0 - continuity_coherence))
        noise_floor = (0.50 * self.cfg.noise_sigma) + (0.30 * context_decoherence_risk) + (0.20 * decoherence_index)
        dead_spot_risk = 1.0 - max(lock, continuity_coherence, hrc, signal_coherence)
        coupling_integrity = (0.34 * hrc) + (0.26 * continuity_coherence) + (0.20 * governance_coherence) + (0.20 * (1.0 - decoherence_index))
        paths = v17_result.get("paths") or {}
        has_signal_ids = bool((signal_result or {}).get("run_id")) and bool((signal_result or {}).get("pulse_id"))
        has_receipt = bool(paths.get("topology_receipt_path")) or topology_receipt != {}
        time_signal_sync = 0.45 + (0.25 if has_signal_ids else 0.0) + (0.20 if has_receipt else 0.0) + (0.10 if paths else 0.0)

        return {
            "presence_index": _round(presence),
            "tuning_lock": _round(tuning_lock),
            "carrier_stability": _round(carrier_stability),
            "rectification_confidence": _round(rectification_confidence),
            "amplification_gain": _round(amplification_gain),
            "feedback_risk": _round(feedback_risk),
            "fading_index": _round(fading_index),
            "noise_floor": _round(noise_floor),
            "dead_spot_risk": _round(dead_spot_risk),
            "coupling_integrity": _round(coupling_integrity),
            "time_signal_sync": _round(time_signal_sync),
        }

    def run(self, intent_text: str, symbol_maps: Dict[str, float]) -> Dict[str, Any]:
        run_id = f"psi42-v18-{uuid.uuid4().hex[:12]}"
        output_dir = self._run_output_dir(run_id)
        v17 = ResonanceTransceiverV17(self.cfg.to_v17(str(output_dir)))
        v17_result = v17.run(intent_text, symbol_maps)
        diagnostics = self._diagnostics(v17_result)
        drift_profile = self._derive_drift_profile(diagnostics)
        metrics = dict(v17_result.get("metrics") or {})
        metrics.update(diagnostics)

        result = {
            "instrument_class": INSTRUMENT_CLASS,
            "public_summary": PUBLIC_SUMMARY,
            "protocol_version": PROTOCOL_VERSION,
            "probe_mode": self.cfg.probe_mode,
            "run_id": run_id,
            "created_at_unix": time.time(),
            "v17_result": v17_result,
            "metrics": metrics,
            "transceiver_diagnostics": diagnostics,
            "derived_drift_profile": drift_profile,
            "paths": dict(v17_result.get("paths") or {}),
            "authority_boundary": {
                "owns": [
                    "derived transceiver diagnostics",
                    "derived signal metrics",
                    "derived topology metrics",
                    "restoration receipts",
                ],
                "does_not_own": [
                    "canon state",
                    "governance law",
                    "mode legality",
                    "checkpoint legality",
                    "capability loading authority",
                    "human consent",
                    "primary continuity authority",
                ],
            },
            "doctrine_alignment": {
                "presence_is_metric_alias": True,
                "plain_coherence_deprecated": "coherence" in metrics,
                "runtime_behavior_mutation": False,
                "governance_authority": False,
            },
        }
        summary_path = self._write_json(output_dir, "psi42_transceiver_v1_8_summary.json", result)
        result["paths"]["v18_summary_path"] = summary_path
        self._last_pulse = result
        return result


if __name__ == "__main__":
    cfg = Config(probe_mode="hybrid")
    rt = ResonanceTransceiverV18(cfg)
    res = rt.run(
        "Lumina OS receives, tunes, rectifies, amplifies, and recomposes continuity under governance.",
        {"LUMINA": 1.0, "CONTINUITY": 0.9, "GOVERNANCE": 1.0, "SIGNAL": 0.7},
    )
    print(json.dumps(res, indent=2))
