from __future__ import annotations

"""Dimension-specific observation of field-edge loss.

This module compares declared path observations. It does not test, repair, or
authorize canonical recovery. Recovery must be proven independently by the
runtime owner that owns the referenced checkpoint or continuity state.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, Mapping


SCHEMA_VERSION = "lumina-mycelial-edge-loss-v0.1"
AUTHORITY_BOUNDARY = (
    "topology observation only; never creates governance, canon, mode, "
    "checkpoint, mutation, promotion, identity, or capability authority"
)

CANONICAL_REFERENCE = "canonical_reference"
NON_AUTHORITATIVE_ROLES = {
    "non_authoritative_context",
    "non_authoritative_diagnostic",
    "non_authoritative_projection",
}
PATH_ROLES = {CANONICAL_REFERENCE, *NON_AUTHORITATIVE_ROLES}
EDGE_FIELDS = {
    "edge_id",
    "source",
    "destination",
    "path_role",
    "available",
    "evidence_reference",
    "authority_effect",
}


@dataclass(frozen=True)
class FieldEdgeObservation:
    edge_id: str
    source: str
    destination: str
    path_role: str
    available: bool
    evidence_reference: str
    authority_effect: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _coerce_edge(value: FieldEdgeObservation | Mapping[str, Any]) -> FieldEdgeObservation:
    if isinstance(value, FieldEdgeObservation):
        edge = value
    elif isinstance(value, Mapping):
        payload = dict(value)
        missing = sorted(EDGE_FIELDS - set(payload))
        unexpected = sorted(set(payload) - EDGE_FIELDS)
        if missing:
            raise ValueError("missing edge fields: " + ", ".join(missing))
        if unexpected:
            raise ValueError("unexpected edge fields: " + ", ".join(unexpected))
        edge = FieldEdgeObservation(**payload)
    else:
        raise TypeError("field edge observation must be a mapping")

    for field_name in ("edge_id", "source", "destination", "evidence_reference"):
        value = getattr(edge, field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string")
    if edge.path_role not in PATH_ROLES:
        raise ValueError("path_role is not allowed")
    if not isinstance(edge.available, bool):
        raise ValueError("available must be boolean")
    if edge.authority_effect is not False:
        raise ValueError("field edge observations must declare authority_effect=false")
    return edge


def _index_edges(
    edges: Iterable[FieldEdgeObservation | Mapping[str, Any]],
) -> Dict[str, FieldEdgeObservation]:
    indexed: Dict[str, FieldEdgeObservation] = {}
    for value in edges:
        edge = _coerce_edge(value)
        if edge.edge_id in indexed:
            raise ValueError(f"duplicate edge_id: {edge.edge_id}")
        indexed[edge.edge_id] = edge
    return indexed


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def observe_edge_loss(
    baseline_edges: Iterable[FieldEdgeObservation | Mapping[str, Any]],
    observed_edges: Iterable[FieldEdgeObservation | Mapping[str, Any]],
) -> Dict[str, Any]:
    """Compare availability without turning topology into recovery authority."""

    baseline = _index_edges(baseline_edges)
    observed = _index_edges(observed_edges)

    immutable_fields = ("source", "destination", "path_role", "evidence_reference")
    for edge_id in sorted(set(baseline) & set(observed)):
        before = baseline[edge_id]
        after = observed[edge_id]
        changed = [
            field_name
            for field_name in immutable_fields
            if getattr(before, field_name) != getattr(after, field_name)
        ]
        if changed:
            raise ValueError(
                f"edge provenance changed for {edge_id}: " + ", ".join(changed)
            )

    baseline_available = [edge for edge in baseline.values() if edge.available]
    lost_edges = [
        edge
        for edge in baseline_available
        if edge.edge_id not in observed or not observed[edge.edge_id].available
    ]
    added_edges = [
        edge for edge_id, edge in observed.items() if edge_id not in baseline
    ]
    observed_available_baseline = [
        edge
        for edge in baseline_available
        if edge.edge_id in observed and observed[edge.edge_id].available
    ]

    baseline_canonical = [
        edge for edge in baseline_available if edge.path_role == CANONICAL_REFERENCE
    ]
    observed_canonical = [
        edge
        for edge in baseline_canonical
        if edge.edge_id in observed and observed[edge.edge_id].available
    ]
    baseline_non_authoritative = [
        edge for edge in baseline_available if edge.path_role in NON_AUTHORITATIVE_ROLES
    ]
    observed_non_authoritative = [
        edge
        for edge in baseline_non_authoritative
        if edge.edge_id in observed and observed[edge.edge_id].available
    ]
    lost_canonical = [
        edge for edge in lost_edges if edge.path_role == CANONICAL_REFERENCE
    ]
    lost_non_authoritative = [
        edge for edge in lost_edges if edge.path_role in NON_AUTHORITATIVE_ROLES
    ]

    if lost_canonical and lost_non_authoritative:
        degradation_scope = "mixed"
    elif lost_canonical:
        degradation_scope = "canonical_reference"
    elif lost_non_authoritative:
        degradation_scope = "non_authoritative_only"
    else:
        degradation_scope = "none"

    metrics = {
        "baseline_edge_count": len(baseline),
        "observed_declared_edge_count": len(observed),
        "baseline_available_edge_count": len(baseline_available),
        "observed_available_baseline_edge_count": len(observed_available_baseline),
        "edge_retention_ratio": _ratio(
            len(observed_available_baseline), len(baseline_available)
        ),
        "baseline_canonical_reference_count": len(baseline_canonical),
        "observed_canonical_reference_count": len(observed_canonical),
        "canonical_reference_availability_ratio": _ratio(
            len(observed_canonical), len(baseline_canonical)
        ),
        "baseline_non_authoritative_edge_count": len(baseline_non_authoritative),
        "observed_non_authoritative_edge_count": len(observed_non_authoritative),
        "non_authoritative_availability_ratio": _ratio(
            len(observed_non_authoritative), len(baseline_non_authoritative)
        ),
        "lost_edge_count": len(lost_edges),
        "lost_canonical_reference_count": len(lost_canonical),
        "lost_non_authoritative_edge_count": len(lost_non_authoritative),
        "added_edge_count": len(added_edges),
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "degraded" if lost_edges else "stable",
        "degradation": {
            "observed": bool(lost_edges),
            "scope": degradation_scope,
        },
        "metrics": metrics,
        "baseline_edges": [baseline[key].to_dict() for key in sorted(baseline)],
        "observed_edges": [observed[key].to_dict() for key in sorted(observed)],
        "lost_edges": [
            edge.to_dict()
            for edge in sorted(lost_edges, key=lambda row: row.edge_id)
        ],
        "added_edges": [
            edge.to_dict()
            for edge in sorted(added_edges, key=lambda row: row.edge_id)
        ],
        "canonical_recovery_claimed": False,
        "authority_effect": False,
        "authority_event_created": False,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }
