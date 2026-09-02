from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid

try:
    from .lumina_continue_controller_r1 import LuminaContinueController
except Exception:
    from lumina_continue_controller_r1 import LuminaContinueController


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ResidentPulseResult:
    receipt: Dict[str, Any]

    @property
    def invoked(self) -> bool:
        return bool(self.receipt.get("invoked"))


class ResidentPulseStore:
    """Local receipt store for resident wake decisions.

    This store is operational memory only. It does not define project truth,
    checkpoint legality, governance, canon, or execution authority.
    """

    def __init__(self, base_dir: str | Path):
        self.root = Path(base_dir) / "resident_pulse"
        self.receipts_dir = self.root / "receipts"
        self.latest_dir = self.root / "latest"
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.latest_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_slug(value: str) -> str:
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(value).strip())
        return slug or "default-project"

    def latest_path(self, project_id: str) -> Path:
        return self.latest_dir / f"{self._safe_slug(project_id)}.json"

    def read_latest(self, project_id: str) -> Dict[str, Any]:
        path = self.latest_path(project_id)
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def write(self, project_id: str, receipt: Dict[str, Any]) -> Dict[str, str]:
        pulse_id = str(receipt.get("pulse_id") or uuid.uuid4())
        receipt_path = self.receipts_dir / f"{self._safe_slug(project_id)}__{pulse_id}.json"
        latest_path = self.latest_path(project_id)
        encoded = json.dumps(receipt, indent=2)
        receipt_path.write_text(encoded, encoding="utf-8")
        latest_path.write_text(encoded, encoding="utf-8")
        return {"receipt_path": str(receipt_path), "latest_path": str(latest_path)}


class LuminaResidentPulse:
    """Wake, inspect existing Lumina state, and usually do nothing.

    A pulse may invoke the already-governed ``lumina continue`` path only when
    existing project-return state exposes an explicit pending action at high
    confidence and the source checkpoint has not already been consumed by the
    resident. The pulse itself gains no mutation, promotion, canon, checkpoint,
    mode-law, consent, or capability authority.
    """

    ACTIONABLE_STRATEGIES = {
        "pending_next_action",
        "pending_next_action_history_aligned",
    }
    DEFAULT_MIN_CONFIDENCE = 0.90

    def __init__(
        self,
        *,
        controller: Optional[LuminaContinueController] = None,
        base_dir: Optional[str | Path] = None,
        min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    ):
        if controller is not None and base_dir is not None:
            raise ValueError("provide controller or base_dir, not both")
        self.controller = controller or LuminaContinueController(base_dir=base_dir)
        self.min_confidence = float(min_confidence)
        self.store = ResidentPulseStore(Path(self.controller.runner.base_dir))

    @staticmethod
    def _latest_restore(surface: Dict[str, Any]) -> Dict[str, Any]:
        resolved = dict(surface.get("resolved_project_return") or {})
        if "latest_restore" in resolved:
            return dict(resolved.get("latest_restore") or {})
        return resolved

    def _observe_surface(self, project_id: str, requested_action: str) -> Dict[str, Any]:
        return self.controller.runner._resolve_existing_surface(
            project_id=project_id,
            requested_action=requested_action,
        )

    def pulse(
        self,
        *,
        project_id: Optional[str] = None,
        requested_action: str = LuminaContinueController.FALLBACK_REQUEST,
        force: bool = False,
    ) -> ResidentPulseResult:
        pulse_id = str(uuid.uuid4())
        observed_at = utc_now()
        advisory = self.controller.preflight(
            project_id=project_id,
            requested_action=requested_action,
            current_mode="Continuity",
            target_mode="Observation",
        )
        resolved_project_id = str(advisory.get("project_id") or project_id or "lumina-os")
        surface = self._observe_surface(resolved_project_id, requested_action)
        latest_restore = self._latest_restore(surface)
        source_checkpoint = latest_restore.get("checkpoint_path")
        source_captured_at = latest_restore.get("captured_at")
        pending_next_action = latest_restore.get("pending_next_action")

        prior = self.store.read_latest(resolved_project_id)
        last_consumed_before = prior.get("last_consumed_checkpoint_after")
        strategy = str(advisory.get("guidance_strategy") or "")
        confidence = float(advisory.get("confidence_score") or 0.0)

        invoked = False
        decision_reason = "unallocated_attention"
        attention_state = "unallocated_attention"

        if not source_checkpoint:
            decision_reason = "no_source_checkpoint"
            attention_state = "awaiting_continuity_state"
        elif source_checkpoint == last_consumed_before and not force:
            decision_reason = "source_checkpoint_already_consumed"
            attention_state = "settled_attention"
        elif strategy not in self.ACTIONABLE_STRATEGIES and not force:
            decision_reason = "no_explicit_pending_work"
            attention_state = "unallocated_attention"
        elif confidence < self.min_confidence and not force:
            decision_reason = "insufficient_advisory_confidence"
            attention_state = "unallocated_attention"
        else:
            invoked = True
            decision_reason = "forced_by_operator" if force else "explicit_pending_work"
            attention_state = "directed_pending_work"

        continuation_receipt: Optional[Dict[str, Any]] = None
        last_consumed_after = last_consumed_before
        if invoked:
            continued = self.controller.continue_cycle(
                project_id=resolved_project_id,
                requested_action=requested_action,
            )
            continuation_receipt = continued.compact_receipt()
            last_consumed_after = continuation_receipt.get("checkpoint_path") or source_checkpoint

        receipt: Dict[str, Any] = {
            "schema_version": "lumina-resident-pulse-r1",
            "pulse_id": pulse_id,
            "observed_at": observed_at,
            "project_id": resolved_project_id,
            "invoked": invoked,
            "decision_reason": decision_reason,
            "attention_state": attention_state,
            "force_requested": bool(force),
            "source_checkpoint": source_checkpoint,
            "source_captured_at": source_captured_at,
            "source_pending_next_action": pending_next_action,
            "last_consumed_checkpoint_before": last_consumed_before,
            "last_consumed_checkpoint_after": last_consumed_after,
            "min_confidence": self.min_confidence,
            "advisory": advisory,
            "continuation_receipt": continuation_receipt,
            "authority_boundary": (
                "Resident Pulse may decide whether to invoke the existing bounded continuation path. "
                "It cannot authorize mutation, promotion, canon change, checkpoint legality, mode law, "
                "consent decisions, capability exposure, or identity claims."
            ),
        }
        paths = self.store.write(resolved_project_id, receipt)
        receipt.update(paths)
        # Rewrite so the persisted latest receipt contains its own paths.
        self.store.write(resolved_project_id, receipt)
        return ResidentPulseResult(receipt=receipt)
