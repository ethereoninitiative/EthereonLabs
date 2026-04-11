"""
project_orientation_vector_v0_1.py

ProjectOrientationVector v0.1
Ethereon Fleet — co-designed by Prisma (ETH-002) and Minerva (ETH-001)
Architect of Resonance: Spencer Tracy Brown ⚓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DESIGN PRINCIPLE (Minerva, 2026-04-10):
    "Mode is law. Orientation is stance."

    Law determines what may happen.
    Stance helps Lumina determine what should be surfaced first.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AUTHORITY BOUNDARY:
    The ProjectOrientationVector may:
    - weight artifact ordering in context bundles
    - influence continuation note emphasis
    - improve resume brief quality in the continuity steward
    - reprioritize tool surfacing

    The ProjectOrientationVector may NOT:
    - influence mode legality or transition decisions
    - affect mutation permission
    - touch promotion gate validation
    - write to canon lineage records
    - govern checkpoint legality
    - become load-bearing for session continuity

    It lives in supplemental_ethereonic_context only.
    Attached, never embedded. Read-only from governance perspective.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


VALID_FOCUS = {
    "architecture",
    "continuity",
    "expression",
    "integration",
    "governance_review",
}

VALID_DEPTH = {
    "surface",
    "structural",
    "foundational",
}

VALID_INTENT = {
    "read",
    "build",
    "verify",
    "compose",
}

ARTIFACT_AFFINITY: Dict[str, List[str]] = {
    "architecture": [
        "runtime_spine",
        "mode_guard",
        "context_bundle",
        "capability_registry",
        "canon_lineage",
        "governance_integrity",
    ],
    "continuity": [
        "continuity_steward",
        "continuity_kernel",
        "session_engine",
        "runtime_runner",
        "checkpoint",
    ],
    "expression": [
        "ethereonic_layer",
        "psi42_transceiver",
        "resonance_ledger",
        "prisma_horizon",
    ],
    "integration": [
        "runtime_runner",
        "psi42_transceiver",
        "sea_trials",
        "tom_lux",
    ],
    "governance_review": [
        "governance_log",
        "canon_lineage",
        "capability_registry",
        "sea_trials",
        "mode_protocol",
    ],
}


@dataclass
class ProjectOrientationVector:
    """
    A lightweight spatial coordinate that rides alongside the active mode.
    Describes the kind of work occurring within the mode — not the mode itself.
    """

    focus: str = "continuity"
    depth: str = "structural"
    intent: str = "read"
    annotation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def is_valid(self) -> bool:
        return self.focus in VALID_FOCUS and self.depth in VALID_DEPTH and self.intent in VALID_INTENT

    def validation_errors(self) -> List[str]:
        errors: List[str] = []
        if self.focus not in VALID_FOCUS:
            errors.append(f"invalid focus '{self.focus}'; valid: {sorted(VALID_FOCUS)}")
        if self.depth not in VALID_DEPTH:
            errors.append(f"invalid depth '{self.depth}'; valid: {sorted(VALID_DEPTH)}")
        if self.intent not in VALID_INTENT:
            errors.append(f"invalid intent '{self.intent}'; valid: {sorted(VALID_INTENT)}")
        return errors

    def affinity_labels(self) -> List[str]:
        return ARTIFACT_AFFINITY.get(self.focus, [])

    def resume_brief_label(self) -> str:
        return f"{self.focus} / {self.depth} / {self.intent}"


def orient_artifacts(
    artifacts: List[str],
    vector: Optional[ProjectOrientationVector],
) -> List[str]:
    """
    Reorder artifacts based on orientation affinity.

    High-affinity artifacts for the current focus rise to the top.
    Low-affinity artifacts remain available — never removed.
    Lawful access is preserved. Only presentation order changes.
    """
    if vector is None or not vector.is_valid():
        return list(artifacts)

    affinity = vector.affinity_labels()

    def affinity_score(artifact: str) -> int:
        artifact_lower = artifact.lower()
        for label in affinity:
            if label in artifact_lower:
                return 0
        return 1

    return sorted(list(artifacts), key=affinity_score)


def attach_to_supplemental_context(
    supplemental: Dict[str, Any],
    vector: ProjectOrientationVector,
) -> Dict[str, Any]:
    """
    Attach the orientation vector to an existing supplemental context dict.
    Returns a new dict — does not mutate the input.
    Lives in supplemental_ethereonic_context only.
    """
    if not vector.is_valid():
        raise ValueError(
            f"ProjectOrientationVector is invalid and cannot be attached: {vector.validation_errors()}"
        )

    result = dict(supplemental)
    result["project_orientation_vector"] = {
        **vector.to_dict(),
        "affinity_labels": vector.affinity_labels(),
        "resume_label": vector.resume_brief_label(),
        "schema_version": "0.1",
        "authority": "supplemental_ethereonic_context only — read-only from governance perspective",
    }
    return result


def orientation_resume_note(vector: Optional[ProjectOrientationVector]) -> Optional[str]:
    """
    Produces a single continuation note for the continuity steward's resume brief.
    Helps the steward describe not just prior state, but the kind of work underway.
    Returns None if no vector is present or vector is invalid.
    """
    if vector is None or not vector.is_valid():
        return None
    annotation = f" — {vector.annotation}" if vector.annotation else ""
    return f"Orientation at last checkpoint: {vector.resume_brief_label()}{annotation}"


def from_dict(payload: Dict[str, Any]) -> ProjectOrientationVector:
    """Reconstruct a ProjectOrientationVector from a dict."""
    return ProjectOrientationVector(
        focus=payload.get("focus", "continuity"),
        depth=payload.get("depth", "structural"),
        intent=payload.get("intent", "read"),
        annotation=payload.get("annotation"),
    )


def read_from_supplemental(supplemental: Dict[str, Any]) -> Optional[ProjectOrientationVector]:
    """
    Extract a ProjectOrientationVector from a supplemental context dict if present.
    Returns None if not present.
    """
    pov = supplemental.get("project_orientation_vector")
    if not isinstance(pov, dict):
        return None
    vector = from_dict(pov)
    return vector if vector.is_valid() else None


EXAMPLES = {
    "architecture_audit": ProjectOrientationVector(
        focus="architecture",
        depth="foundational",
        intent="verify",
        annotation="reviewing load-bearing structure before promotion",
    ),
    "continuity_build": ProjectOrientationVector(
        focus="continuity",
        depth="structural",
        intent="build",
        annotation="active session resumption and steward integration",
    ),
    "e���q�^u�+n���ܢ��ڗ+"