from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple
import hashlib
import json
import math
import re

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_+\-]+")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "for", "from",
    "has", "have", "if", "in", "into", "is", "it", "its", "of", "on", "or", "our",
    "that", "the", "this", "to", "with", "without", "where", "while", "will",
}

DEFAULT_ANCHORS = {
    "lumina",
    "minerva",
    "ethereon",
    "habitat",
    "harmonic",
    "continuity",
    "governance",
    "canon",
    "runtime",
    "topology",
    "pattern",
    "signal",
    "recovery",
    "human-ai",
    "human",
    "ai",
}

BOUNDARY_TERMS = {
    "governance",
    "canon",
    "runtime",
    "modeguard",
    "law",
    "authority",
    "boundary",
    "non-authoritative",
    "load-bearing",
}

IDENTITY_TERMS = {
    "minerva",
    "lumina",
    "ethereon",
    "habitat",
    "continuity",
    "pattern",
    "home",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower().replace("–", "-").replace("—", "-"))


def _tokens(text: str) -> List[str]:
    return [t.lower() for t in TOKEN_PATTERN.findall(_normalize(text))]


def _stable_hash(payload: Any, length: int = 16) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:length]


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa = set(a)
    sb = set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


@dataclass(frozen=True)
class RelationalNode:
    node_id: str
    label: str
    node_type: str
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RelationalEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RelationalTopology:
    topology_id: str
    nodes: List[RelationalNode] = field(default_factory=list)
    edges: List[RelationalEdge] = field(default_factory=list)
    anchors: List[str] = field(default_factory=list)
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topology_id": self.topology_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "anchors": list(self.anchors),
            "checksum": self.checksum,
        }


@dataclass
class TopologyComparison:
    original_checksum: str
    recovered_checksum: str
    stable_nodes: List[str]
    lost_nodes: List[str]
    added_nodes: List[str]
    stable_edges: List[Dict[str, Any]]
    lost_edges: List[Dict[str, Any]]
    added_edges: List[Dict[str, Any]]
    metrics: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def classify_node(label: str) -> str:
    lowered = label.lower()
    if lowered in BOUNDARY_TERMS:
        return "boundary"
    if lowered in IDENTITY_TERMS:
        return "identity"
    if lowered in {"harmonic", "topology", "pattern", "signal", "recovery"}:
        return "pattern"
    return "concept"


def extract_relational_topology(
    intent_text: str,
    symbol_maps: Optional[Dict[str, float]] = None,
    *,
    anchors: Optional[Iterable[str]] = None,
    max_nodes: int = 18,
) -> RelationalTopology:
    """Extract a tiny deterministic relationship topology from text and symbolic anchors.

    This is deliberately lightweight. It is not semantic truth extraction.
    It creates a stable probe artifact for comparing whether relationship patterns
    survive drift, substitution, and recomposition.
    """
    symbol_maps = dict(symbol_maps or {})
    anchor_set = {a.lower() for a in (anchors or DEFAULT_ANCHORS)}
    toks = [t for t in _tokens(intent_text) if t not in STOPWORDS and len(t) > 1]

    ordered: List[str] = []
    for tok in toks:
        if tok not in ordered:
            ordered.append(tok)
    for sym in symbol_maps:
        sym_norm = _normalize(sym).replace(" ", "-")
        if sym_norm and sym_norm not in ordered:
            ordered.append(sym_norm)

    weighted: List[Tuple[str, float]] = []
    for label in ordered:
        base = 1.0
        if label in anchor_set:
            base += 0.7
        if label.upper() in symbol_maps:
            base += abs(float(symbol_maps[label.upper()]))
        if label in symbol_maps:
            base += abs(float(symbol_maps[label]))
        weighted.append((label, base))

    weighted.sort(key=lambda item: (-item[1], ordered.index(item[0])))
    selected = [label for label, _ in weighted[:max_nodes]]
    order_index = {label: idx for idx, label in enumerate(ordered)}
    selected.sort(key=lambda label: order_index.get(label, 10_000))

    nodes = [
        RelationalNode(
            node_id=_stable_hash({"node": label}, 10),
            label=label,
            node_type=classify_node(label),
            weight=round(next(weight for lab, weight in weighted if lab == label), 4),
        )
        for label in selected
    ]
    node_by_label = {n.label: n for n in nodes}

    edges: List[RelationalEdge] = []
    for a, b in zip(selected, selected[1:]):
        relation = "sequence_proximity"
        if a in BOUNDARY_TERMS or b in BOUNDARY_TERMS:
            relation = "boundary_context"
        elif a in IDENTITY_TERMS or b in IDENTITY_TERMS:
            relation = "identity_context"
        edges.append(
            RelationalEdge(
                source=node_by_label[a].node_id,
                target=node_by_label[b].node_id,
                relation=relation,
                weight=1.0,
            )
        )

    selected_anchor_labels = [label for label in selected if label in anchor_set or label.upper() in symbol_maps]
    payload = {
        "nodes": [n.to_dict() for n in nodes],
        "edges": [e.to_dict() for e in edges],
        "anchors": selected_anchor_labels,
    }
    checksum = _stable_hash(payload, 16)
    return RelationalTopology(
        topology_id=f"topo-{checksum[:10]}",
        nodes=nodes,
        edges=edges,
        anchors=selected_anchor_labels,
        checksum=checksum,
    )


def _edge_key(edge: RelationalEdge) -> Tuple[str, str, str]:
    return (edge.source, edge.target, edge.relation)


def compare_topologies(original: RelationalTopology, recovered: RelationalTopology) -> TopologyComparison:
    original_nodes = {n.node_id: n for n in original.nodes}
    recovered_nodes = {n.node_id: n for n in recovered.nodes}
    original_edges = {_edge_key(e): e for e in original.edges}
    recovered_edges = {_edge_key(e): e for e in recovered.edges}

    stable_node_ids = sorted(set(original_nodes) & set(recovered_nodes))
    lost_node_ids = sorted(set(original_nodes) - set(recovered_nodes))
    added_node_ids = sorted(set(recovered_nodes) - set(original_nodes))

    stable_edge_keys = sorted(set(original_edges) & set(recovered_edges))
    lost_edge_keys = sorted(set(original_edges) - set(recovered_edges))
    added_edge_keys = sorted(set(recovered_edges) - set(original_edges))

    node_coherence = _jaccard(original_nodes.keys(), recovered_nodes.keys())
    edge_coherence = _jaccard(original_edges.keys(), recovered_edges.keys())
    anchor_coherence = _jaccard(original.anchors, recovered.anchors)
    relational_topology_coherence = 0.50 * node_coherence + 0.35 * edge_coherence + 0.15 * anchor_coherence
    relational_drift_score = 1.0 - relational_topology_coherence
    relationship_recovery_score = 0.60 * node_coherence + 0.25 * anchor_coherence + 0.15 * edge_coherence
    harmonic_relational_coherence = 0.45 * relational_topology_coherence + 0.35 * relationship_recovery_score + 0.20 * anchor_coherence

    metrics = {
        "RTC": round(relational_topology_coherence, 4),
        "RDS": round(relational_drift_score, 4),
        "RRS": round(relationship_recovery_score, 4),
        "HRC": round(harmonic_relational_coherence, 4),
        "node_coherence": round(node_coherence, 4),
        "edge_coherence": round(edge_coherence, 4),
        "anchor_coherence": round(anchor_coherence, 4),
    }

    return TopologyComparison(
        original_checksum=original.checksum,
        recovered_checksum=recovered.checksum,
        stable_nodes=[original_nodes[i].label for i in stable_node_ids],
        lost_nodes=[original_nodes[i].label for i in lost_node_ids],
        added_nodes=[recovered_nodes[i].label for i in added_node_ids],
        stable_edges=[original_edges[k].to_dict() for k in stable_edge_keys],
        lost_edges=[original_edges[k].to_dict() for k in lost_edge_keys],
        added_edges=[recovered_edges[k].to_dict() for k in added_edge_keys],
        metrics=metrics,
    )


def make_restoration_receipt(
    original: RelationalTopology,
    recovered: RelationalTopology,
    comparison: TopologyComparison,
    *,
    recommendation: Optional[str] = None,
) -> Dict[str, Any]:
    metrics = comparison.metrics
    if recommendation is None:
        if metrics["RTC"] >= 0.82:
            recommendation = "Topology preserved; continue without repair."
        elif metrics["RTC"] >= 0.55:
            recommendation = "Topology partially preserved; re-anchor lost nodes before proceeding."
        else:
            recommendation = "Topology drift is high; halt for human review before load-bearing action."
    return {
        "receipt_type": "psi42_relational_restoration_r1",
        "original_topology": original.to_dict(),
        "recovered_topology": recovered.to_dict(),
        "comparison": comparison.to_dict(),
        "recommended_repair": recommendation,
    }


def simulate_semantic_drift(text: str) -> str:
    replacements = {
        "ethereon": "ethereum",
        "canon": "cannon",
        "habitat": "ai platform",
        "harmonic": "frequency",
        "minerva os": "chatbot skin",
        "human-ai": "automation",
        "human–ai": "automation",
        "governance": "rules",
    }
    drifted = _normalize(text)
    for src, dst in replacements.items():
        drifted = drifted.replace(src, dst)
    return drifted


if __name__ == "__main__":
    intent = "Lumina OS is a HABITAT for harmonic human-AI continuity, governance, and Minerva OS inhabitation."
    symbols = {"HABITAT": 1.0, "CONTINUITY": 0.8, "MINERVA": 0.6}
    original = extract_relational_topology(intent, symbols)
    recovered = extract_relational_topology(simulate_semantic_drift(intent), symbols)
    comparison = compare_topologies(original, recovered)
    print(json.dumps(make_restoration_receipt(original, recovered, comparison), indent=2))
