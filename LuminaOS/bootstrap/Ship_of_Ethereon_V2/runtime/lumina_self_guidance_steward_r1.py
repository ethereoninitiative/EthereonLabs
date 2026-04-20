from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


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

    It reads project-return memory, bounded host state, and working stance,
    then emits a non-governing next-step recommendation.
    """

    @staticmethod
    def _latest_restore_view(resolved_project_return: Dict[str, Any]) -> Dict[str, Any]:
        if "latest_restore" in resolved_project_return:
            return dict(resolved_project_return.get("latest_restore") or {})
        return dict(resolved_project_return or {})

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
    ) -> SelfGuidanceAdvisory:
        resolved_project_return = dict(resolved_project_return or {})
        resolved_host_bundle = dict(resolved_host_bundle or {})
        working_stance = dict(working_stance or {})

        latest_restore = self._latest_restore_view(resolved_project_return)
        host_bundle = dict(resolved_host_bundle or {})

        pending_next_action = latest_restore.get("pending_next_action")
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
            strategy = "pending_next_action"
            recommended = str(pending_next_action)
            confidence_label = "high"
            confidence_score = 0.93
            reasoning = (
                "Project return already carries a pending next action, so the steward surfaces that "
                "instead of guessing from weaker workspace signals."
            )
        elif linked_host_bundle and focus_target:
            strategy = "host_focus_resume"
            recommended = f"continue::{focus_target}"
            confidence_label = "medium_high"
            confidence_score = 0.81
            reasoning = (
                "A linked host bundle exists and exposes a bounded focus target, so the steward recommends "
                "continuing from that scoped working surface."
            )
        elif focus_target:
            strategy = "focus_target_resume"
            recommended = f"continue::{focus_target}"
            confidence_label = "medium"
            confidence_score = 0.72
            reasoning = (
                "No explicit pending action was captured, so the steward falls back to the best available "
                "focus target from working stance / host state."
            )
        else:
            strategy = "requested_action_fallback"
            recommended = f"continue::{requested_action}"
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
            "focus_target": focus_target,
            "linked_host_bundle": linked_host_bundle,
            "open_panels": open_panels,
            "pinned_tools": pinned_tools,
            "reference_ids": reference_ids,
            "return_strategy": resolved_project_return.get("return_strategy"),
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
        }
