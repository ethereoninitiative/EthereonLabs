from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from .lumina_continuation_action_r1 import normalize_continuation_action
except Exception:
    from lumina_continuation_action_r1 import normalize_continuation_action


FORBIDDEN_AUTHORITY_KEYS = {
    "governance",
    "canon_lineage",
    "mode_guard",
    "promotion",
    "transition",
    "record_hash",
    "validation_reference",
    "allowed",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SelfGuidanceAdvisory:
    project_id: str
    guidance_strategy: str
    recommended_next_action: str
    confidence_label: str
    confidence_score: float
    reasoning_brief: str
    signals: Dict[str, Any] = field(default_factory=dict)
    boundary_note: str = (
        "Advisory only. May recommend what to surface or attempt next, "
        "but may not define governance law, canon lineage, checkpoint legality, or mode legality."
    )
    generated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["authority_safe"] = not any(key in payload for key in FORBIDDEN_AUTHORITY_KEYS)
        return payload


class LuminaSelfGuidanceSteward:
    """
    Advisory steward for repo-native Lumina return / host surfaces.

    It reads project-return memory, bounded host state, working stance,
    and checkpoint-linked recommendation history, then emits a non-governing next-step recommendation.
    """

    @staticmethod
    def _latest_restore_view(resolved_project_return: Dict[str, Any]) -> Dict[str, Any]:
        if "latest_restore" in resolved_project_return:
            return dict(resolved_project_return.get("latest_restore") or {})
        return dict(resolved_project_return or {})

    @staticmethod
    def _history_signals(guidance_history: Optional[List[Dict[str, Any]]], candidate_recommendation: str) -> Dict[str, Any]:
        rows = list(guidance_history or [])
        recent = rows[-3:]
        recent_recommendations = [
            normalize_continuation_action(row.get("recommended_next_action"))
            for row in recent
            if row.get("recommended_next_action")
        ]
        canonical_candidate = normalize_continuation_action(candidate_recommendation)
        alignment_count = sum(
            1
            for row in rows
            if normalize_continuation_action(row.get("recommended_next_action")) == canonical_candidate
        )
        latest_recommendation = recent_recommendations[-1] if recent_recommendations else None
        return {
            "history_entry_count": len(rows),
            "history_recent_recommendations": recent_recommendations,
            "history_alignment_count": alignment_count,
            "history_latest_recommendation": latest_recommendation,
            "history_aligned": alignment_count > 0 and latest_recommendation == candidate_recommendation,
        }

    def advise(
        self,
        *,
        project_id: str,
        requested_action: str,
        current_mode: str,
        target_mode: str,
        resolved_project_return: Optional[Dict[str, Any]] = None,
        resolved_host_bundle: Optional[Dict[str, Any]] = None,
        working_stance: Optional[Dict[str, Any]] = None,
        guidance_history: Optional[List[Dict[str, Any]]] = None,
    ) -> SelfGuidanceAdvisory:
        resolved_project_return = dict(resolved_project_return or {})
        resolved_host_bundle = dict(resolved_host_bundle or {})
        working_stance = dict(working_stance or {})
        guidance_history = list(guidance_history or [])

        latest_restore = self._latest_restore_view(resolved_project_return)
        host_bundle = dict(resolved_host_bundle or {})

        pending_next_action_raw = latest_restore.get("pending_next_action")
        pending_next_action = (
            normalize_continuation_action(pending_next_action_raw)
            if pending_next_action_raw
            else None
        )
        focus_target = (
            working_stance.get("focus_target")
            or host_bundle.get("focus_target")
            or requested_action
        )
        linked_host_bundle = latest_restore.get("linked_host_bundle")
        open_panels = list(working_stance.get("open_panels") or host_bundle.get("panel_ids") or [])
        pinned_tools = list(working_stance.get("pinned_tools") or host_bundle.get("pinned_tool_ids") or [])
        reference_ids = list(working_stance.get("reference_ids") or host_bundle.get("reference_ids") or [])

        if pending_next_action:
            recommended = str(pending_next_action)
            history = self._history_signals(guidance_history, recommended)
            if history["history_aligned"]:
                strategy = "pending_next_action_history_aligned"
                confidence_label = "very_high"
                confidence_score = 0.97
                reasoning = (
                    "Project return already carries a pending next action, and accumulated checkpoint history "
                    "reinforces the same recommendation."
                )
            else:
                strategy = "pending_next_action"
                confidence_label = "high"
                confidence_score = 0.93
                reasoning = (
                    "Project return already carries a pending next action, so the steward surfaces that "
                    "instead of guessing from weaker workspace signals."
                )
        elif linked_host_bundle and focus_target:
            recommended = f"continue::{focus_target}"
            history = self._history_signals(guidance_history, recommended)
            if history["history_aligned"]:
                strategy = "host_focus_history_aligned"
                confidence_label = "medium_high"
                confidence_score = 0.86
                reasoning = (
                    "A linked host bundle exposes a bounded focus target, and recent checkpoint history aligns "
                    "with continuing that scoped surface."
                )
            else:
                strategy = "host_focus_resume"
                confidence_label = "medium_high"
                confidence_score = 0.81
                reasoning = (
                    "A linked host bundle exists and exposes a bounded focus target, so the steward recommends "
                    "continuing from that scoped working surface."
                )
        elif focus_target:
            recommended = f"continue::{focus_target}"
            history = self._history_signals(guidance_history, recommended)
            if history["history_aligned"]:
                strategy = "focus_target_history_aligned"
                confidence_label = "medium"
                confidence_score = 0.78
                reasoning = (
                    "No explicit pending action was captured, but current focus and recent checkpoint history "
                    "align on the same continuation target."
                )
            else:
                strategy = "focus_target_resume"
                confidence_label = "medium"
                confidence_score = 0.72
                reasoning = (
                    "No explicit pending action was captured, so the steward falls back to the best available "
                    "focus target from working stance / host state."
                )
        else:
            recommended = f"continue::{requested_action}"
            history = self._history_signals(guidance_history, recommended)
            if history["history_aligned"]:
                strategy = "requested_action_history_aligned"
                confidence_label = "medium"
                confidence_score = 0.67
                reasoning = (
                    "The steward found no stronger live cues, but accumulated checkpoint history repeats the same "
                    "requested-action continuation path."
                )
            else:
                strategy = "requested_action_fallback"
                confidence_label = "low_medium"
                confidence_score = 0.58
                reasoning = (
                    "The steward found no stronger project-return or host cues, so it falls back to the current "
                    "requested action without claiming authority."
                )

        signals = {
            "requested_action": requested_action,
            "current_mode": current_mode,
            "target_mode": target_mode,
            "pending_next_action": pending_next_action,
            "pending_next_action_raw": pending_next_action_raw,
            "pending_next_action_normalized": bool(
                pending_next_action_raw
                and str(pending_next_action_raw).strip() != pending_next_action
            ),
            "focus_target": focus_target,
            "linked_host_bundle": linked_host_bundle,
            "open_panels": open_panels,
            "pinned_tools": pinned_tools,
            "reference_ids": reference_ids,
            "return_strategy": resolved_project_return.get("return_strategy"),
            **history,
        }

        return SelfGuidanceAdvisory(
            project_id=project_id,
            guidance_strategy=strategy,
            recommended_next_action=recommended,
            confidence_label=confidence_label,
            confidence_score=confidence_score,
            reasoning_brief=reasoning,
            signals=signals,
        )

    @staticmethod
    def advisory_summary(advisory: SelfGuidanceAdvisory) -> Dict[str, Any]:
        payload = advisory.to_dict()
        return {
            "project_id": payload["project_id"],
            "guidance_strategy": payload["guidance_strategy"],
            "recommended_next_action": payload["recommended_next_action"],
            "confidence_label": payload["confidence_label"],
            "confidence_score": payload["confidence_score"],
            "reasoning_brief": payload["reasoning_brief"],
            "boundary_note": payload["boundary_note"],
            "history_entry_count": payload.get("signals", {}).get("history_entry_count", 0),
            "history_alignment_count": payload.get("signals", {}).get("history_alignment_count", 0),
            "history_recent_recommendations": payload.get("signals", {}).get("history_recent_recommendations", []),
        }
