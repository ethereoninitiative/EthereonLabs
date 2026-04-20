from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json


@dataclass
class LuminaWorkingStanceVoiceReport:
    project_id: Optional[str]
    current_mode: Optional[str]
    focus_target: Optional[str]
    active_layout_id: Optional[str]
    open_panels: List[str]
    pinned_tools: List[str]
    reference_ids: List[str]
    linked_restore_checkpoint: Optional[str]
    linked_host_bundle: Optional[str]
    utterance: str
    boundary_note: str = "Descriptive voice only. Does not define governance law, canon state, or session legality."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaWorkingStanceVoice:
    """Reads bounded runtime state and emits an honest working-stance utterance.

    This layer may describe currently available project stance.
    It may not invent hidden intent or claim governance authority.
    """

    @staticmethod
    def _read_json(path: str | Path) -> Dict[str, Any]:
        with Path(path).open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _dedupe(values: List[str]) -> List[str]:
        out: List[str] = []
        seen = set()
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            out.append(value)
        return out

    @staticmethod
    def _derive_from_session(session_payload: Dict[str, Any]) -> Dict[str, Any]:
        stance = dict(session_payload.get("working_stance") or {})
        return {
            "project_id": session_payload.get("project_id"),
            "current_mode": session_payload.get("current_mode"),
            "focus_target": stance.get("focus_target"),
            "active_layout_id": stance.get("active_layout_id"),
            "open_panels": list(stance.get("open_panels") or []),
            "pinned_tools": list(stance.get("pinned_tools") or []),
            "reference_ids": list(stance.get("reference_ids") or []),
            "linked_restore_checkpoint": stance.get("linked_restore_checkpoint"),
            "linked_host_bundle": stance.get("linked_host_bundle"),
        }

    @staticmethod
    def _merge_context(state: Dict[str, Any], context_bundle_payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not context_bundle_payload:
            return state
        artifact = dict(context_bundle_payload.get("artifact_context") or {})
        summary = dict(artifact.get("working_stance_summary") or {})
        resolved_return = dict(artifact.get("resolved_project_return") or {})
        resolved_host = dict(artifact.get("resolved_host_bundle") or {})

        merged = dict(state)
        merged["project_id"] = merged.get("project_id") or artifact.get("active_project_id")
        merged["focus_target"] = merged.get("focus_target") or summary.get("focus_target") or resolved_host.get("focus_target")
        merged["active_layout_id"] = merged.get("active_layout_id") or summary.get("active_layout_id") or resolved_host.get("active_layout_id")
        merged["open_panels"] = LuminaWorkingStanceVoice._dedupe(
            list(merged.get("open_panels") or []) + list(summary.get("open_panels") or []) + list(resolved_host.get("panel_ids") or [])
        )
        merged["pinned_tools"] = LuminaWorkingStanceVoice._dedupe(
            list(merged.get("pinned_tools") or []) + list(summary.get("pinned_tools") or []) + list(resolved_host.get("pinned_tool_ids") or [])
        )
        merged["reference_ids"] = LuminaWorkingStanceVoice._dedupe(
            list(merged.get("reference_ids") or []) + list(summary.get("reference_ids") or []) + list(resolved_host.get("reference_ids") or [])
        )
        merged["linked_restore_checkpoint"] = merged.get("linked_restore_checkpoint") or summary.get("linked_restore_checkpoint") or resolved_return.get("checkpoint_path")
        merged["linked_host_bundle"] = merged.get("linked_host_bundle") or summary.get("linked_host_bundle") or resolved_return.get("linked_host_bundle")
        return merged

    @staticmethod
    def _speak(state: Dict[str, Any]) -> str:
        fragments: List[str] = []

        project_id = state.get("project_id")
        if project_id:
            fragments.append(f"Project {project_id} is in scope.")
        else:
            fragments.append("No project id is presently in scope.")

        current_mode = state.get("current_mode")
        if current_mode:
            fragments.append(f"Current mode is {current_mode}.")

        focus_target = state.get("focus_target")
        if focus_target:
            fragments.append(f"Primary focus is {focus_target}.")
        else:
            fragments.append("No explicit focus target is recorded.")

        layout = state.get("active_layout_id")
        if layout:
            fragments.append(f"Active layout is {layout}.")

        open_panels = list(state.get("open_panels") or [])
        if open_panels:
            fragments.append(f"Open panels: {', '.join(open_panels)}.")

        pinned_tools = list(state.get("pinned_tools") or [])
        if pinned_tools:
            fragments.append(f"Pinned tools: {', '.join(pinned_tools)}.")

        reference_ids = list(state.get("reference_ids") or [])
        if reference_ids:
            fragments.append(f"References in view: {', '.join(reference_ids)}.")

        if state.get("linked_restore_checkpoint"):
            fragments.append("A linked restore checkpoint is available.")
        if state.get("linked_host_bundle"):
            fragments.append("A linked host bundle is available.")

        return " ".join(fragments)

    def report(
        self,
        *,
        session_path: str | Path,
        context_bundle_path: Optional[str | Path] = None,
    ) -> LuminaWorkingStanceVoiceReport:
        session_payload = self._read_json(session_path)
        state = self._derive_from_session(session_payload)
        context_bundle_payload = self._read_json(context_bundle_path) if context_bundle_path else None
        merged = self._merge_context(state, context_bundle_payload)
        utterance = self._speak(merged)
        return LuminaWorkingStanceVoiceReport(
            project_id=merged.get("project_id"),
            current_mode=merged.get("current_mode"),
            focus_target=merged.get("focus_target"),
            active_layout_id=merged.get("active_layout_id"),
            open_panels=list(merged.get("open_panels") or []),
            pinned_tools=list(merged.get("pinned_tools") or []),
            reference_ids=list(merged.get("reference_ids") or []),
            linked_restore_checkpoint=merged.get("linked_restore_checkpoint"),
            linked_host_bundle=merged.get("linked_host_bundle"),
            utterance=utterance,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Describe Lumina's current working stance from lawful runtime state.")
    parser.add_argument("session_path")
    parser.add_argument("--context-bundle-path", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    voice = LuminaWorkingStanceVoice()
    report = voice.report(
        session_path=args.session_path,
        context_bundle_path=args.context_bundle_path,
    )
    print(json.dumps(report.to_dict(), indent=2))
