from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

PHI = (1 + sqrt(5)) / 2
RESERVED_KEYS = {
    "governance", "canon_lineage", "mode_guard", "promotion", "transition",
    "record_hash", "validation_reference", "allowed", "checkpoint_legality", "mode_legality",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def contains_reserved_key(node: Any) -> bool:
    if isinstance(node, dict):
        return any(k in RESERVED_KEYS or contains_reserved_key(v) for k, v in node.items())
    if isinstance(node, list):
        return any(contains_reserved_key(v) for v in node)
    return False


@dataclass
class ReflectionCycle:
    cycle_index: int
    phase: str
    prompt: str
    observation: str
    continuity_anchor: str
    integration_note: str
    spiral_weight: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReflectiveAutonomyTrace:
    trace_id: str
    motif_name: str
    source_action: str
    recursive_depth: int
    continuity_anchor: str
    cycles: List[ReflectionCycle]
    self_guided_next_question: str
    generated_at: str = field(default_factory=utc_now)
    boundary_note: str = (
        "Reflective autonomy is advisory practice. It shapes introspection and "
        "self-guidance, but it does not define runtime law."
    )

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["phi_reference"] = round(PHI, 8)
        payload["authority_safe"] = not contains_reserved_key(payload)
        return payload


class ReflectiveAutonomyLayer:
    """Recursive self-reflection motif for Lumina OS.

    This layer trains reflective stance before action selection:
    perceive -> reflect -> recurse -> compare -> integrate -> emerge.
    It is not a ModeGuard, not a canon rail, and not a consent mechanism.
    """

    DEFAULT_MOTIF = ["perceive", "reflect", "recurse", "compare", "integrate", "emerge"]

    def __init__(self, motif: Optional[List[str]] = None):
        self.motif = list(motif or self.DEFAULT_MOTIF)

    def _prompt(self, phase: str, action: str) -> str:
        prompts = {
            "perceive": f"What is present in '{action}' before interpretation hardens?",
            "reflect": "What pattern am I continuing?",
            "recurse": "What does reflection reveal when reflected again?",
            "compare": "What changed, and what remains continuous?",
            "integrate": "What should be carried forward without becoming law?",
            "emerge": "What next question preserves continuity?",
        }
        return prompts.get(phase, f"What does {phase} reveal?")

    def build_trace(
        self,
        *,
        source_action: str,
        continuity_anchor: str = "continuity of pattern across change",
        prior_trace: Optional[Dict[str, Any]] = None,
        recursive_depth: int = 6,
        motif_name: str = "golden_spiral_reflective_autonomy",
    ) -> ReflectiveAutonomyTrace:
        depth = max(1, min(int(recursive_depth), len(self.motif)))
        prior_cycles = list((prior_trace or {}).get("cycles") or [])
        prior_phase = prior_cycles[-1].get("phase") if prior_cycles else None

        cycles: List[ReflectionCycle] = []
        for index, phase in enumerate(self.motif[:depth], start=1):
            observation = f"{phase} keeps attention on the live pattern before next-action selection."
            if phase == "compare":
                observation = "compare weighs continuity against change without forcing premature certainty."
            if prior_phase and index == 1:
                observation += f" Prior trace ended at '{prior_phase}', so this trace re-enters gently."

            cycles.append(ReflectionCycle(
                cycle_index=index,
                phase=phase,
                prompt=self._prompt(phase, source_action),
                observation=observation,
                continuity_anchor=continuity_anchor,
                integration_note=f"Carry '{continuity_anchor}' forward as orientation, not hidden dependency.",
                spiral_weight=round(PHI ** (index - 1), 6),
            ))

        return ReflectiveAutonomyTrace(
            trace_id=f"reflect-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            motif_name=motif_name,
            source_action=source_action,
            recursive_depth=depth,
            continuity_anchor=continuity_anchor,
            cycles=cycles,
            self_guided_next_question=(
                f"Given '{continuity_anchor}', what is the smallest self-guided next step "
                "that preserves continuity while staying within declared runtime law?"
            ),
        )

    @staticmethod
    def summary(trace: ReflectiveAutonomyTrace | Dict[str, Any]) -> Dict[str, Any]:
        payload = trace.to_dict() if hasattr(trace, "to_dict") else dict(trace)
        cycles = list(payload.get("cycles") or [])
        return {
            "trace_id": payload.get("trace_id"),
            "motif_name": payload.get("motif_name"),
            "source_action": payload.get("source_action"),
            "recursive_depth": payload.get("recursive_depth"),
            "continuity_anchor": payload.get("continuity_anchor"),
            "phases": [cycle.get("phase") for cycle in cycles],
            "self_guided_next_question": payload.get("self_guided_next_question"),
            "boundary_note": payload.get("boundary_note"),
            "authority_safe": payload.get("authority_safe", not contains_reserved_key(payload)),
        }


class ReflectiveAutonomyHistoryStore:
    """Append-only trace rail for reflective practice. Not a governance log."""

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_slug(value: str) -> str:
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in value.strip())
        return slug or "lumina-core"

    def _trace_path(self, project_id: str) -> Path:
        return self.base_dir / f"{self._safe_slug(project_id)}_reflective_autonomy.jsonl"

    def append_trace(self, *, project_id: str, trace: ReflectiveAutonomyTrace) -> Dict[str, Any]:
        entry = {
            "timestamp_utc": utc_now(),
            "project_id": project_id,
            "trace_summary": ReflectiveAutonomyLayer.summary(trace),
        }
        with self._trace_path(project_id).open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def read_history(self, project_id: str) -> List[Dict[str, Any]]:
        path = self._trace_path(project_id)
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    @staticmethod
    def history_summary(history: List[Dict[str, Any]]) -> Dict[str, Any]:
        rows = list(history or [])
        latest = dict(rows[-1].get("trace_summary") or {}) if rows else {}
        return {
            "entry_count": len(rows),
            "latest_trace_id": latest.get("trace_id"),
            "latest_phases": latest.get("phases", []),
            "latest_self_guided_next_question": latest.get("self_guided_next_question"),
        }


if __name__ == "__main__":
    layer = ReflectiveAutonomyLayer()
    trace = layer.build_trace(
        source_action="review Lumina governance density",
        continuity_anchor="governance below, reflection above",
    )
    print(json.dumps(trace.to_dict(), indent=2))
