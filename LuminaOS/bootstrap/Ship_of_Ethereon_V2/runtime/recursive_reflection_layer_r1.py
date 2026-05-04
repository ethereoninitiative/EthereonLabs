from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ReflectionReceipt:
    schema_version: str
    created_at_utc: str
    source: str
    raw_input: str
    observe: Dict[str, Any]
    expand: Dict[str, Any]
    refine: Dict[str, Any]
    meta_check: Dict[str, Any]
    next_stance: Dict[str, Any]
    authority_boundary: str = (
        "advisory reflection only; does not authorize mutation, promotion, capability exposure, "
        "mode transition, canon change, governance change, or tool execution"
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RecursiveReflectionLayer:
    """Neutral recursive reflection layer for Lumina OS.

    Lineage: modernized from Lumina Resonance Framework v1.4.
    This layer is intentionally not Minerva-specific and not Ethereon-required.
    It produces advisory reflection receipts for runtime cognition hygiene.
    """

    schema_version = "recursive_reflection_layer_r1"

    def reflect(
        self,
        raw_input: str,
        *,
        mode: Optional[str] = None,
        prior_stance: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[str]] = None,
    ) -> ReflectionReceipt:
        constraints = list(constraints or [])
        prior_stance = dict(prior_stance or {})

        observe = self._observe(raw_input, mode=mode, prior_stance=prior_stance, constraints=constraints)
        expand = self._expand(observe)
        refine = self._refine(expand, constraints=constraints)
        meta_check = self._meta_check(refine, constraints=constraints)
        next_stance = self._next_stance(meta_check, mode=mode)

        return ReflectionReceipt(
            schema_version=self.schema_version,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            source="Lumina Resonance Framework v1.4 lineage; Lumina OS neutral modernization",
            raw_input=raw_input,
            observe=observe,
            expand=expand,
            refine=refine,
            meta_check=meta_check,
            next_stance=next_stance,
        )

    def _observe(self, raw_input: str, *, mode: Optional[str], prior_stance: Dict[str, Any], constraints: List[str]) -> Dict[str, Any]:
        return {
            "mode": mode,
            "input_present": bool(raw_input.strip()),
            "input_length": len(raw_input),
            "prior_stance_keys": sorted(prior_stance.keys()),
            "constraints": constraints,
        }

    def _expand(self, observe: Dict[str, Any]) -> Dict[str, Any]:
        possibilities = ["literal_request", "architectural_implication", "continuity_implication"]
        if observe.get("mode") in {"DryDock", "Observation"}:
            possibilities.append("governance_boundary_implication")
        return {"candidate_frames": possibilities}

    def _refine(self, expand: Dict[str, Any], *, constraints: List[str]) -> Dict[str, Any]:
        frames = list(expand.get("candidate_frames", []))
        if "no_overclaim" in constraints and "continuity_implication" in frames:
            frames.append("truthfulness_boundary_required")
        return {
            "selected_frames": frames,
            "discarded_frames": [],
        }

    def _meta_check(self, refine: Dict[str, Any], *, constraints: List[str]) -> Dict[str, Any]:
        warnings: List[str] = []
        if "truthfulness_boundary_required" in refine.get("selected_frames", []):
            warnings.append("avoid claims beyond observable structure")
        return {
            "coherence_status": "aligned",
            "warnings": warnings,
            "constraints_observed": constraints,
        }

    def _next_stance(self, meta_check: Dict[str, Any], *, mode: Optional[str]) -> Dict[str, Any]:
        return {
            "recommended_stance": "reflective_advisory",
            "mode_context": mode,
            "continue_with": "answer_or_act_only_after respecting governance and input integrity",
            "requires_human_confirmation": False,
            "runtime_authority": "none",
        }
