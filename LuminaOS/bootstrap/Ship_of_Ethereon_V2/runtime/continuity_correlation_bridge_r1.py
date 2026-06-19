from __future__ import annotations

"""Continuity Correlation Runtime Bridge R1.

Attaches the existing Lumina continuity-correlation envelope to runtime receipts
and optionally docks a receipt copy into the active Harbor session.

This bridge carries identity context only. It does not grant governance, canon,
checkpoint, mode, or capability authority.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    from .continuity_correlation_r1 import create_correlation
except Exception:
    from continuity_correlation_r1 import create_correlation


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _write_json(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    return path


def resolve_active_harbor_session_root(state_root: Path) -> Optional[Path]:
    marker = _read_json(state_root / "active_session.json")
    raw = marker.get("session_root")
    if not raw:
        return None
    root = Path(str(raw))
    return root if root.exists() else None


def attach_correlation(
    receipt: Dict[str, Any],
    *,
    state_root: Path,
    runtime_session_id: Optional[str] = None,
    restore_session_id: Optional[str] = None,
    host_session_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    envelope = create_correlation(
        state_root=state_root,
        runtime_session_id=runtime_session_id,
        restore_session_id=restore_session_id,
        host_session_id=host_session_id,
        correlation_id=correlation_id,
    )
    output = dict(receipt)
    output["continuity_correlation"] = envelope.to_dict()
    return output


def dock_receipt(
    receipt: Dict[str, Any],
    *,
    state_root: Path,
    filename: str,
) -> Optional[Path]:
    session_root = resolve_active_harbor_session_root(state_root)
    if session_root is None:
        return None
    safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in filename)
    if not safe_name.endswith(".json"):
        safe_name += ".json"
    return _write_json(session_root / "receipts" / safe_name, receipt)


def bridge_runtime_receipt(
    receipt: Dict[str, Any],
    *,
    state_root: Path,
    runtime_session_id: Optional[str] = None,
    restore_session_id: Optional[str] = None,
    host_session_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    dock_filename: Optional[str] = None,
) -> Dict[str, Any]:
    bridged = attach_correlation(
        receipt,
        state_root=state_root,
        runtime_session_id=runtime_session_id,
        restore_session_id=restore_session_id,
        host_session_id=host_session_id,
        correlation_id=correlation_id,
    )
    docked_path = None
    if dock_filename:
        docked_path = dock_receipt(bridged, state_root=state_root, filename=dock_filename)
    result = dict(bridged)
    result["continuity_correlation_bridge"] = {
        "schema_version": "continuity-correlation-runtime-bridge-r1",
        "docked_receipt_path": str(docked_path) if docked_path else None,
        "authority_boundary": (
            "Bridge attaches and docks identity context only; runtime governance remains authoritative."
        ),
    }
    return result
