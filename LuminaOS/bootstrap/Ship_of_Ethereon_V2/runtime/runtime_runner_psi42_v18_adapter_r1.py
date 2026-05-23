from __future__ import annotations

"""RuntimeRunner adapter that prefers Psi-42 v1.8 when available.

This adapter avoids rewriting the core runner while giving local Studio / observe
surfaces a clean route to the doctrine-aligned v1.8 transceiver diagnostics.
It preserves the existing v1.7 and v1.6 fallbacks.
"""

from typing import Any, Dict, List, Optional

try:
    from .runtime_runner_r1_merged import RuntimeRunner as BaseRuntimeRunner, VALID_ACTION_TYPES
except Exception:
    from runtime_runner_r1_merged import RuntimeRunner as BaseRuntimeRunner, VALID_ACTION_TYPES

try:
    from .psi42_transceiver_v1_8 import Config as Psi42V18Config, ResonanceTransceiverV18
except Exception:
    try:
        from psi42_transceiver_v1_8 import Config as Psi42V18Config, ResonanceTransceiverV18
    except Exception:
        Psi42V18Config = None
        ResonanceTransceiverV18 = None

try:
    from .psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17
except Exception:
    try:
        from psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17
    except Exception:
        Psi42V17Config = None
        ResonanceTransceiverV17 = None

try:
    from .psi42_transceiver_v1_6 import Config as Psi42V16Config, ResonanceTransceiverV16
except Exception:
    try:
        from psi42_transceiver_v1_6 import Config as Psi42V16Config, ResonanceTransceiverV16
    except Exception:
        Psi42V16Config = None
        ResonanceTransceiverV16 = None


PSI42_DEFAULT_FLAGS = [
    "ETHEREON_PSI42",
    "ETHEREON_PSI42_V17",
    "ETHEREON_PSI42_V18",
    "ETHEREON_RESONANCE",
]


class RuntimeRunner(BaseRuntimeRunner):
    """RuntimeRunner variant that prefers Psi-42 v1.8 diagnostics.

    Authority remains unchanged: this adapter only changes probe routing. It does
    not alter governance law, mode legality, mutation rules, canon lineage, or
    checkpoint legality.
    """

    def _resolve_enabled_feature_flags(self, enabled_feature_flags: Optional[List[str]]) -> List[str]:
        merged = super()._resolve_enabled_feature_flags(enabled_feature_flags)
        for flag in PSI42_DEFAULT_FLAGS:
            if flag not in merged:
                merged.append(flag)
        return merged

    def _psi42_language_mode(self, ethereonic_overlay: Optional[Dict[str, Any]]) -> str:
        overlay = ethereonic_overlay or {}
        anchors = overlay.get("anchor_language", ["english"])
        return "ethereonic" if any(x in anchors for x in ["toki_pona", "binary", "light_language"]) else "neutral"

    def _psi42_symbol_maps(self, target_mode: str) -> Dict[str, float]:
        return {
            "OBSERVATION": 1.0 if target_mode == "Observation" else 0.0,
            "SANDBOX": 1.0 if target_mode == "Sandbox" else 0.0,
            "CONTINUITY": 0.8,
            "HABITAT": 0.7,
            "SIGNAL": 0.7,
            "GOVERNANCE": 0.6,
        }

    def _maybe_run_psi42_probe(
        self,
        *,
        target_mode: str,
        requested_action: str,
        ethereonic_overlay: Optional[Dict[str, Any]],
        exposed_capabilities: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        capability_ids = {cap.get("capability_id") for cap in exposed_capabilities}
        has_any_psi42 = bool(
            capability_ids
            & {
                "psi42_probe_interface",
                "psi42_transceiver_v16",
                "psi42_transceiver_v17",
                "psi42_transceiver_v18",
            }
        )
        if not has_any_psi42:
            return None
        if target_mode not in {"Observation", "Sandbox"}:
            return None

        language_mode = self._psi42_language_mode(ethereonic_overlay)
        run_slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in f"{requested_action}_{target_mode}")[:80]
        output_dir = self.base_dir / "psi42_artifacts" / (self._active_session_id or "session") / run_slug
        intent_text = f"{requested_action} :: {target_mode}"
        symbol_maps = self._psi42_symbol_maps(target_mode)

        if "psi42_transceiver_v18" in capability_ids and ResonanceTransceiverV18 is not None and Psi42V18Config is not None:
            rt = ResonanceTransceiverV18(
                Psi42V18Config(language_mode=language_mode, output_dir=str(output_dir), probe_mode="hybrid")
            )
            result = rt.run(intent_text, symbol_maps)
            v17_result = result.get("v17_result") or {}
            signal_result = v17_result.get("signal_result") or {}
            return {
                "instrument_version": "v1.8",
                "instrument_class": result.get("instrument_class"),
                "probe_mode": result.get("probe_mode"),
                "metrics": result.get("metrics"),
                "transceiver_diagnostics": result.get("transceiver_diagnostics"),
                "derived_drift_profile": result.get("derived_drift_profile"),
                "paths": result.get("paths"),
                "topology_receipt": v17_result.get("topology_receipt"),
                "signal_run_id": signal_result.get("run_id"),
                "signal_pulse_id": signal_result.get("pulse_id"),
                "run_id": result.get("run_id"),
                "authority_boundary": result.get("authority_boundary"),
                "doctrine_alignment": result.get("doctrine_alignment"),
            }

        if "psi42_transceiver_v17" in capability_ids and ResonanceTransceiverV17 is not None and Psi42V17Config is not None:
            rt = ResonanceTransceiverV17(
                Psi42V17Config(language_mode=language_mode, output_dir=str(output_dir), probe_mode="hybrid")
            )
            result = rt.run(intent_text, symbol_maps)
            return {
                "instrument_version": "v1.7",
                "instrument_class": result.get("instrument_class"),
                "probe_mode": result.get("probe_mode"),
                "metrics": result.get("metrics"),
                "paths": result.get("paths"),
                "topology_receipt": result.get("topology_receipt"),
                "signal_run_id": (result.get("signal_result") or {}).get("run_id"),
                "signal_pulse_id": (result.get("signal_result") or {}).get("pulse_id"),
                "authority_boundary": result.get("authority_boundary"),
            }

        if ResonanceTransceiverV16 is None or Psi42V16Config is None:
            return None
        rt = ResonanceTransceiverV16(Psi42V16Config(language_mode=language_mode, output_dir=str(output_dir)))
        result = rt.run(intent_text, symbol_maps)
        return {
            "instrument_version": "v1.6",
            "run_id": result.get("run_id"),
            "pulse_id": result.get("pulse_id"),
            "metrics": result.get("metrics"),
            "paths": result.get("paths"),
            "frame": result.get("frame"),
        }
