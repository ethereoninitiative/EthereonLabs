from __future__ import annotations

"""Resonant Manifold R1.

A bounded classical state-space model inspired by higher-dimensional,
quantum-adjacent, harmonic, and magnetic concepts.

The manifold does not claim literal access to a fifth physical dimension,
quantum hardware, or hidden physical fields. It models five independently
represented computational axes:

1. instantiated state
2. continuity history
3. relational context
4. orientation field
5. potential trajectories

Ownership boundary:
- owns derived manifold coordinates, coherence scores, attractor ranking,
  and lawful-reachability summaries;
- may read approved state, history, relation, orientation, possibility, and
  governance-filter inputs;
- does not own governance law, canon state, mode legality, checkpoint
  legality, capability authority, or primary continuity truth.
"""

from dataclasses import asdict, dataclass
from math import sqrt
from typing import Any, Dict, Iterable, List, Mapping, Sequence

MODEL_ID = "resonant-manifold-r1"
MODEL_CLASS = "higher-dimensional-inspired classical state-space model"
LITERAL_FIFTH_DIMENSION_CLAIM = False
LITERAL_QUANTUM_HARDWARE_CLAIM = False

AXES = (
    "instantiated_state",
    "continuity_history",
    "relational_context",
    "orientation_field",
    "potential_trajectories",
)


@dataclass(frozen=True)
class ManifoldPoint:
    instantiated_state: float
    continuity_history: float
    relational_context: float
    orientation_field: float
    potential_trajectories: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class PotentialTrajectory:
    trajectory_id: str
    label: str
    vector: ManifoldPoint
    allowed: bool = True
    governance_reason: str = "allowed"

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["vector"] = self.vector.to_dict()
        return payload


def _bounded(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return round(max(0.0, min(number, 1.0)), 6)


def point(payload: Mapping[str, Any]) -> ManifoldPoint:
    """Normalize an arbitrary mapping into one bounded manifold point."""
    return ManifoldPoint(**{axis: _bounded(payload.get(axis, 0.0)) for axis in AXES})


def _values(item: ManifoldPoint) -> List[float]:
    return [getattr(item, axis) for axis in AXES]


def harmonic_coherence(left: ManifoldPoint, right: ManifoldPoint) -> float:
    """Cosine coherence across all five represented axes."""
    a = _values(left)
    b = _values(right)
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sqrt(sum(x * x for x in a))
    mag_b = sqrt(sum(y * y for y in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return round(max(0.0, min(dot / (mag_a * mag_b), 1.0)), 6)


def orientation_attraction(current: ManifoldPoint, candidate: ManifoldPoint) -> float:
    """Magnetic-style attraction score emphasizing orientation and continuity.

    This is a computational analogy, not a claim of literal magnetism.
    """
    coherence = harmonic_coherence(current, candidate)
    orientation_match = 1.0 - abs(current.orientation_field - candidate.orientation_field)
    continuity_match = 1.0 - abs(current.continuity_history - candidate.continuity_history)
    persistence = (orientation_match * 0.45) + (continuity_match * 0.30) + (coherence * 0.25)
    return round(max(0.0, min(persistence, 1.0)), 6)


def potential_contribution(item: ManifoldPoint) -> float:
    """Report the fifth axis contribution as a separately observable value."""
    first_four_mean = sum(_values(item)[:4]) / 4.0
    return round(item.potential_trajectories - first_four_mean, 6)


def governance_filter(
    trajectories: Iterable[PotentialTrajectory],
    denied_ids: Sequence[str] = (),
) -> List[PotentialTrajectory]:
    """Apply caller-supplied governance decisions without inventing authority."""
    denied = set(denied_ids)
    filtered: List[PotentialTrajectory] = []
    for trajectory in trajectories:
        if trajectory.trajectory_id in denied:
            filtered.append(
                PotentialTrajectory(
                    trajectory_id=trajectory.trajectory_id,
                    label=trajectory.label,
                    vector=trajectory.vector,
                    allowed=False,
                    governance_reason="denied_by_external_governance_filter",
                )
            )
        else:
            filtered.append(trajectory)
    return filtered


def rank_trajectories(
    current: ManifoldPoint,
    trajectories: Iterable[PotentialTrajectory],
) -> List[Dict[str, Any]]:
    """Rank allowed trajectories by harmonic and magnetic-style measures."""
    ranked: List[Dict[str, Any]] = []
    for trajectory in trajectories:
        coherence = harmonic_coherence(current, trajectory.vector)
        attraction = orientation_attraction(current, trajectory.vector)
        reachable_score = round((coherence * 0.55) + (attraction * 0.45), 6) if trajectory.allowed else 0.0
        ranked.append(
            {
                **trajectory.to_dict(),
                "harmonic_coherence": coherence,
                "orientation_attraction": attraction,
                "potential_contribution": potential_contribution(trajectory.vector),
                "reachable_score": reachable_score,
            }
        )
    return sorted(ranked, key=lambda item: item["reachable_score"], reverse=True)


def manifold_snapshot(
    current: ManifoldPoint,
    trajectories: Iterable[PotentialTrajectory],
    denied_ids: Sequence[str] = (),
) -> Dict[str, Any]:
    governed = governance_filter(trajectories, denied_ids=denied_ids)
    ranked = rank_trajectories(current, governed)
    return {
        "model_id": MODEL_ID,
        "model_class": MODEL_CLASS,
        "literal_fifth_dimension_claim": LITERAL_FIFTH_DIMENSION_CLAIM,
        "literal_quantum_hardware_claim": LITERAL_QUANTUM_HARDWARE_CLAIM,
        "axes": list(AXES),
        "current_point": current.to_dict(),
        "potential_axis_contribution": potential_contribution(current),
        "ranked_trajectories": ranked,
        "lawful_reachable_count": sum(1 for item in ranked if item["allowed"]),
        "authority_boundary": (
            "The Resonant Manifold derives state-space measures only. "
            "External governance remains authoritative for legality and permission."
        ),
    }
