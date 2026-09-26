from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid

try:
    from .lumina_continue_controller_r1 import LuminaContinueController
    from .resident_ember_r1 import ResidentEmberStore
except Exception:
    from lumina_continue_controller_r1 import LuminaContinueController
    from resident_ember_r1 import ResidentEmberStore


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

    def write(self, project_id: str, receipt: Dict[str, Any]) -> Dict[str, Any]:
        pulse_id = str(receipt.get("pulse_id") or uuid.uuid4())
        receipt_path = self.receipts_dir / f"{self._safe_slug(project_id)}__{pulse_id}.json"
        latest_path = self.latest_path(project_id)
        payload = dict(receipt)
        payload["receipt_path"] = str(receipt_path)
        payload["latest_path"] = str(latest_path)
        encoded = json.dumps(payload, indent=2)
        receipt_path.write_text(encoded, encoding="utf-8")
        latest_path.write_text(encoded, encoding="utf-8")
        return payload


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

    def _verify_ember_wake(self, wake_packet: Dict[str, Any]) -> Dict[str, Any]:
        required = {
            "schema_version", "resident", "intention_id", "ember_event_hash",
            "ember_sequence", "wake_cause", "drive_at_wake", "wake_threshold", "authority",
        }
        if set(wake_packet) != required:
            raise ValueError("invalid Ember wake packet fields")
        if wake_packet.get("schema_version") != "resident-ember-wake-r1":
            raise ValueError("unsupported Ember wake packet")
        ember = ResidentEmberStore(Path(self.controller.runner.base_dir))
        rows = ember.read()
        matches = [
            row for row in rows
            if row.get("event_hash") == wake_packet.get("ember_event_hash")
            and row.get("sequence") == wake_packet.get("ember_sequence")
        ]
        if len(matches) != 1:
            raise ValueError("Ember wake event is absent from verified local history")
        event = matches[0]
        if not event.get("wake_requested") or event.get("wake_cause") != "resident_inherited_drive":
            raise ValueError("Ember event is not an endogenous wake")
        for packet_key, event_key in (
            ("resident", "resident"),
            ("intention_id", "intention_id"),
            ("wake_cause", "wake_cause"),
            ("drive_at_wake", "drive_after"),
            ("wake_threshold", "wake_threshold"),
        ):
            if wake_packet.get(packet_key) != event.get(event_key):
                raise ValueError("Ember wake packet does not match verified event")
        return event

    def pulse(
        self,
        *,
        project_id: Optional[str] = None,
        requested_action: str = LuminaContinueController.FALLBACK_REQUEST,
        force: bool = False,
        ember_wake: Optional[Dict[str, Any]] = None,
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
        verified_ember_event = None
        if ember_wake is not None:
            if force:
                raise ValueError("Ember wake and operator force are mutually exclusive")
            verified_ember_event = self._verify_ember_wake(ember_wake)

        if verified_ember_event is not None:
            invoked = True
            decision_reason = "verified_ember_endogenous_wake"
            attention_state = "resident_initiated_attention"
        elif not source_checkpoint:
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
        post_continue_project_checkpoint = None
        last_consumed_after = last_consumed_before
        if invoked:
            continued = self.controller.continue_cycle(
                project_id=resolved_project_id,
                requested_action=requested_action,
            )
            continuation_receipt = continued.compact_receipt()
            post_surface = self._observe_surface(resolved_project_id, requested_action)
            post_restore = self._latest_restore(post_surface)
            post_continue_project_checkpoint = post_restore.get("checkpoint_path")
            last_consumed_after = post_continue_project_checkpoint or source_checkpoint

        receipt: Dict[str, Any] = {
            "schema_version": "lumina-resident-pulse-r1",
            "pulse_id": pulse_id,
            "observed_at": observed_at,
            "project_id": resolved_project_id,
            "invoked": invoked,
            "decision_reason": decision_reason,
            "attention_state": attention_state,
            "force_requested": bool(force),
            "ember_wake": ember_wake,
            "verified_ember_event_hash": (
                verified_ember_event.get("event_hash") if verified_ember_event is not None else None
            ),
            "source_checkpoint": source_checkpoint,
            "source_captured_at": source_captured_at,
            "source_pending_next_action": pending_next_action,
            "last_consumed_checkpoint_before": last_consumed_before,
            "last_consumed_checkpoint_after": last_consumed_after,
            "post_continue_project_checkpoint": post_continue_project_checkpoint,
            "min_confidence": self.min_confidence,
            "advisory": advisory,
            "continuation_receipt": continuation_receipt,
            "authority_boundary": (
                "Resident Pulse may decide whether to invoke the existing bounded continuation path. "
                "A verified Ember wake is an attention cause, not execution authority. Pulse cannot "
                "authorize mutation, promotion, canon change, checkpoint legality, mode law, consent "
                "decisions, capability exposure, or identity claims."
            ),
        }
        persisted = self.store.write(resolved_project_id, receipt)
        return ResidentPulseResult(receipt=persisted)
