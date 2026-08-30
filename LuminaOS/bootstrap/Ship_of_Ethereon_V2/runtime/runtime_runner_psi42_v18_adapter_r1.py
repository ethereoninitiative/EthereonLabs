from __future__ import annotations

"""RuntimeRunner adapter for Psi-42 v1.8 and continuity correlation.

This adapter avoids rewriting the core runner while giving local Studio and
observe surfaces a clean route to doctrine-aligned Psi-42 diagnostics plus
correlated Harbor/runtime receipts.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

try:
    from .runtime_runner_r1_merged import (
        RuntimeRunner as BaseRuntimeRunner,
        RunnerResult as BaseRunnerResult,
        VALID_ACTION_TYPES,
        STATE_ROOT,
        utc_now,
    )
except Exception:
    from runtime_runner_r1_merged import (
        RuntimeRunner as BaseRuntimeRunner,
        RunnerResult as BaseRunnerResult,
        VALID_ACTION_TYPES,
        STATE_ROOT,
        utc_now,
    )

try:
    from .continuity_correlation_bridge_r1 import bridge_runtime_receipt
except Exception:
    from continuity_correlation_bridge_r1 import bridge_runtime_receipt

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


@dataclass
class RunnerResult(BaseRunnerResult):
    continuity_correlation: Optional[Dict[str, Any]] = None
    continuity_correlation_bridge: Optional[Dict[str, Any]] = None


class RuntimeRunner(BaseRuntimeRunner):
    """RuntimeRunner variant that prefers Psi-42 v1.8 and correlates receipts.

    Authority remains unchanged: this adapter changes probe routing and receipt
    context only. It does not alter governance law, mode legality, mutation
    rules, canon lineage, or checkpoint legality.
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

    @staticmethod
    def _correlation_ids(lumina_return_host_artifacts: Optional[Dict[str, Any]]) -> Dict[str, Optional[str]]:
        artifacts = lumina_return_host_artifacts or {}
        checkpoint_only = artifacts.get("checkpoint_only") or {}
        restore_payload = checkpoint_only.get("payload") or {}
        latest_restore = restore_payload.get("latest_restore") or {}
        checkpoint_plus_host = artifacts.get("checkpoint_plus_host") or {}
        host_bundle = checkpoint_plus_host.get("host_bundle") or {}
        return {
            "restore_session_id": latest_restore.get("session_id"),
            "host_session_id": host_bundle.get("host_session_id"),
        }

    def _finalize_result(
        self,
        *,
        session_id: str,
        current_mode: str,
        target_mode: str,
        requested_action: str,
        action_type: str,
        context_bundle_id: str,
        governance: Dict[str, Any],
        exposed_capabilities: List[Dict[str, Any]],
        checkpoint_path: str | Path,
        probe_artifacts: Optional[Dict[str, Any]],
        lumina_return_host_artifacts: Optional[Dict[str, Any]],
        canon_lineage: Optional[Dict[str, Any]],
    ) -> RunnerResult:
        session_path = self.session_engine.session_path(session_id)
        result = RunnerResult(
            run_id=f"run-{session_id[:12]}",
            created_at=utc_now(),
            requested_mode=current_mode,
            target_mode=target_mode,
            requested_action=requested_action,
            action_type=action_type,
            session_id=session_id,
            context_bundle_id=context_bundle_id,
            governance=governance,
            exposed_capabilities=exposed_capabilities,
            checkpoint_path=str(checkpoint_path),
            session_path=str(session_path),
            log_path="",
            governance_log_path=str(self.governance_log_path),
            governance_chain_status=self._current_chain_status(),
            canon_lineage=canon_lineage or self._current_canon_metadata(),
            probe_artifacts=probe_artifacts,
            lumina_return_host_artifacts=lumina_return_host_artifacts,
            mycelial_field_replay=self._mycelial_field_replay_for_session(session_id),
        )
        log_path = self.logs_dir / f"{result.run_id}.json"
        ids = self._correlation_ids(lumina_return_host_artifacts)
        bridged = bridge_runtime_receipt(
            result.to_dict(),
            state_root=STATE_ROOT,
            runtime_session_id=session_id,
            restore_session_id=ids["restore_session_id"],
            host_session_id=ids["host_session_id"],
            dock_filename=f"{result.run_id}.json",
        )
        result.continuity_correlation = bridged.get("continuity_correlation")
        result.continuity_correlation_bridge = bridged.get("continuity_correlation_bridge")
        result.log_path = str(log_path)
        payload = result.to_dict()
        log_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        docked_path = (result.continuity_correlation_bridge or {}).get("docked_receipt_path")
        if docked_path:
            Path(docked_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return result

    def _halted_result(self, **kwargs: Any) -> RunnerResult:
        result = super()._halted_result(**kwargs)
        payload = result.to_dict()
        if result.log_path:
            Path(result.log_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        docked_path = (getattr(result, "continuity_correlation_bridge", None) or {}).get("docked_receipt_path")
        if docked_path:
            Path(docked_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return result

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
        if not has_any_psi42 or target_mode not in {"Observation", "Sandbox"}:
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
