from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json

try:
    from .continuity_correlation_r1 import create_correlation
    from .runtime_runner_r1_merged import RuntimeRunner
except Exception:
    from continuity_correlation_r1 import create_correlation
    from runtime_runner_r1_merged import RuntimeRunner


class ContinuityCorrelationRuntimeBridge:
    """Attach typed continuity correlation to governed runtime receipts."""

    def __init__(self, *, state_root: Path, runner: Optional[RuntimeRunner] = None):
        self.state_root = Path(state_root)
        self.runner = runner or RuntimeRunner()

    def _extract_host_ids(self, payload: Dict[str, Any]) -> Dict[str, Optional[str]]:
        artifacts = payload.get("lumina_return_host_artifacts") or {}
        restore_id = None
        host_id = None
        host_payload = artifacts.get("checkpoint_plus_host") or {}
        if isinstance(host_payload, dict):
            host_id = host_payload.get("host_snapshot_id")
        restore_payload = artifacts.get("checkpoint_only") or {}
        if isinstance(restore_payload, dict):
            inner = restore_payload.get("payload") or {}
            if isinstance(inner, dict):
                restore_id = inner.get("session_id") or inner.get("restore_session_id")
        return {
            "restore_session_id": str(restore_id) if restore_id else None,
            "host_session_id": str(host_id) if host_id else None,
        }

    def _dock_receipt(self, payload: Dict[str, Any]) -> Optional[str]:
        correlation = payload.get("continuity_correlation") or {}
        harbor_session_id = correlation.get("harbor_session_id")
        project_slug = correlation.get("project_slug")
        if not harbor_session_id:
            return None
        if project_slug:
            receipts_dir = self.state_root / "projects" / project_slug / "sessions" / harbor_session_id / "receipts"
        else:
            receipts_dir = self.state_root / "sessions" / harbor_session_id / "receipts"
        receipts_dir.mkdir(parents=True, exist_ok=True)
        run_id = str(payload.get("run_id") or correlation.get("correlation_id") or "runtime-receipt")
        path = receipts_dir / f"{run_id}.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return str(path)

    def run_cycle(self, **kwargs: Any) -> Dict[str, Any]:
        result = self.runner.run_cycle(**kwargs)
        payload = result.to_dict()
        host_ids = self._extract_host_ids(payload)
        correlation = create_correlation(
            state_root=self.state_root,
            project_slug=kwargs.get("project_id"),
            runtime_session_id=payload.get("session_id"),
            restore_session_id=host_ids["restore_session_id"],
            host_session_id=host_ids["host_session_id"],
        )
        payload["continuity_correlation"] = correlation.to_dict()
        payload["harbor_receipt_path"] = self._dock_receipt(payload)
        return payload
