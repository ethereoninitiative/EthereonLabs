from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json

try:
    from .runtime_spine_r1 import ContextBundleBuilder, GovernanceLog, ModeGuard, SessionEngine
    from .canon_lineage_store_r1 import CanonLineageStore
except Exception:
    from runtime_spine_r1 import ContextBundleBuilder, GovernanceLog, ModeGuard, SessionEngine
    from canon_lineage_store_r1 import CanonLineageStore

try:
    from .psi42_transceiver_v1_6 import Config as Psi42Config, ResonanceTransceiverV16
except Exception:
    try:
        from psi42_transceiver_v1_6 import Config as Psi42Config, ResonanceTransceiverV16
    except Exception:
        Psi42Config = None
        ResonanceTransceiverV16 = None

try:
    from .psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17
except Exception:
    try:
        from psi42_transceiver_v1_7 import Config as Psi42V17Config, ResonanceTransceiverV17
    except Exception:
        Psi42V17Config = None
        ResonanceTransceiverV17 = None

try:
    from .input_integrity_layer_r1 import InputIntegrityAssessor
except Exception:
    try:
        from input_integrity_layer_r1 import InputIntegrityAssessor
    except Exception:
        InputIntegrityAssessor = None

try:
    from .ethereonic_layer_r1 import EthereonicLayerRegistry
except Exception:
    try:
        from ethereonic_layer_r1 import EthereonicLayerRegistry
    except Exception:
        EthereonicLayerRegistry = None

try:
    from .lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
except Exception:
    try:
        from lumina_return_host_repo_native_bridge_r1 import ContinuityRestoreStore, LuminaWorkspaceHost
    except Exception:
        ContinuityRestoreStore = None
        LuminaWorkspaceHost = None


RUNTIME_SEED_VERSION = "0.4"
DEFAULT_EXPERIMENTAL_FEATURE_FLAGS = [
    "ETHEREON_CONTINUITY_RESTORE",
    "ETHEREON_LUMINA_HOST",
]

# NOTE: This patch preserves the full existing runner behavior and changes only
# the Psi-42 probe router. The rest of the file is intentionally left in the
# active branch as previously present.


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


RUNTIME_ROOT = _repo_root() / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime"
STATE_ROOT = _repo_root() / ".lumina_state" / "ship_of_ethereon_v2"

BASE_DIR = STATE_ROOT / "runtime_runner_r1_actiontype_logging"
REGISTRY_PATH = RUNTIME_ROOT / "capability_registry_r1.json"

# Runtime patch helper for the active runner implementation.
def run_psi42_probe_with_v17_preference(
    *,
    base_dir: Path,
    active_session_id: Optional[str],
    target_mode: str,
    requested_action: str,
    ethereonic_overlay: Optional[Dict[str, Any]],
    exposed_capabilities: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    capability_ids = {cap.get("capability_id") for cap in exposed_capabilities}
    if target_mode not in {"Observation", "Sandbox"}:
        return None
    if "psi42_probe_interface" not in capability_ids:
        return None

    overlay = ethereonic_overlay or {}
    anchors = overlay.get("anchor_language", ["english"])
    language_mode = "ethereonic" if any(x in anchors for x in ["toki_pona", "binary", "light_language"]) else "neutral"
    run_slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in f"{requested_action}_{target_mode}")[:80]
    output_dir = base_dir / "psi42_artifacts" / (active_session_id or "session") / run_slug
    symbol_maps = {
        "OBSERVATION": 1.0 if target_mode == "Observation" else 0.0,
        "SANDBOX": 1.0 if target_mode == "Sandbox" else 0.0,
        "CONTINUITY": 0.8,
        "HABITAT": 0.7,
    }

    if "psi42_transceiver_v17" in capability_ids and ResonanceTransceiverV17 is not None and Psi42V17Config is not None:
        rt17 = ResonanceTransceiverV17(Psi42V17Config(language_mode=language_mode, output_dir=str(output_dir), probe_mode="hybrid"))
        result = rt17.run(f"{requested_action} :: {target_mode}", symbol_maps)
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

    if "psi42_transceiver_v16" in capability_ids and ResonanceTransceiverV16 is not None and Psi42Config is not None:
        rt16 = ResonanceTransceiverV16(Psi42Config(language_mode=language_mode, output_dir=str(output_dir)))
        result = rt16.run(f"{requested_action} :: {target_mode}", symbol_maps)
        return {
            "instrument_version": "v1.6",
            "run_id": result.get("run_id"),
            "pulse_id": result.get("pulse_id"),
            "metrics": result.get("metrics"),
            "paths": result.get("paths"),
            "frame": result.get("frame"),
        }

    return None
