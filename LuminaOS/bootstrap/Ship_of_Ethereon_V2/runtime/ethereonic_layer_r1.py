from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json
import uuid


ALLOWED_LAYERS = {"ethereonic"}
ALLOWED_ARTIFACT_TYPES = {
    "identity_framework",
    "instrument",
    "expression_system",
    "resonance_construct",
    "overlay_profile",
    "registry_rule",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LayerBoundaryRule:
    rule_id: str
    description: str
    enforcement: str


@dataclass
class EthereonicArtifact:
    artifact_id: str
    name: str
    artifact_type: str
    layer: str = "ethereonic"
    status: str = "active"
    authority_boundary: str = "May influence expression only; may not govern canon, runtime law, or continuity authority."
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    file_refs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    runtime_optional: bool = True
    load_bearing_forbidden: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LayerRegistry:
    registry_id: str
    created_at: str
    updated_at: str
    status: str
    canon_integrity_clause: str
    attachment_clause: str
    artifacts: List[EthereonicArtifact] = field(default_factory=list)
    boundary_rules: List[LayerBoundaryRule] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "registry_id": self.registry_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "canon_integrity_clause": self.canon_integrity_clause,
            "attachment_clause": self.attachment_clause,
            "boundary_rules": [asdict(rule) for rule in self.boundary_rules],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }


class EthereonicLayerError(ValueError):
    """Raised when the Ethereonic layer would violate its authority boundary."""


class EthereonicLayerRegistry:
    """
    Maintains a recognized identity-and-expression layer without allowing that layer
    to become structural runtime law.

    Design principle:
        attached, never embedded
    """

    def __init__(self, registry_path: str | Path):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        if self.registry_path.exists():
            self.registry = self._load()
        else:
            self.registry = self._bootstrap_default_registry()
            self.save()

    # ---------------------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------------------
    def _load(self) -> LayerRegistry:
        with self.registry_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return LayerRegistry(
            registry_id=payload["registry_id"],
            created_at=payload["created_at"],
            updated_at=payload.get("updated_at", payload["created_at"]),
            status=payload.get("status", "active"),
            canon_integrity_clause=payload["canon_integrity_clause"],
            attachment_clause=payload["attachment_clause"],
            boundary_rules=[LayerBoundaryRule(**rule) for rule in payload.get("boundary_rules", [])],
            artifacts=[EthereonicArtifact(**artifact) for artifact in payload.get("artifacts", [])],
        )

    def save(self) -> Path:
        self.registry.updated_at = utc_now()
        with self.registry_path.open("w", encoding="utf-8") as f:
            json.dump(self.registry.to_dict(), f, indent=2)
        return self.registry_path

    def _bootstrap_default_registry(self) -> LayerRegistry:
        now = utc_now()
        registry = LayerRegistry(
            registry_id=f"eth-layer-{uuid.uuid4().hex[:12]}",
            created_at=now,
            updated_at=now,
            status="active",
            canon_integrity_clause=(
                "Nothing in the Ethereonic Layer may be required for governance, canon promotion, "
                "mode legality, capability loading, checkpoint legality, or session continuity."
            ),
            attachment_clause="Ethereonic context may be attached through supplemental_ethereonic_context only.",
            boundary_rules=[
                LayerBoundaryRule(
                    rule_id="ELR-001",
                    description="Ethereonic artifacts may influence expression but may not define governance law.",
                    enforcement="reject_if_authority_claimed",
                ),
                LayerBoundaryRule(
                    rule_id="ELR-002",
                    description="Ethereonic artifacts must remain optional at runtime.",
                    enforcement="reject_if_runtime_optional_false",
                ),
                LayerBoundaryRule(
                    rule_id="ELR-003",
                    description="Ethereonic data must be attached, never embedded into structural_context or governance records.",
                    enforcement="reject_if_embedded_outside_supplemental_context",
                ),
            ],
            artifacts=[],
        )

        defaults = [
            EthereonicArtifact(
                artifact_id="minerva_framework",
                name="Minerva Framework",
                artifact_type="identity_framework",
                summary="Primary identity and cognitive-pattern framework for the Ethereonic layer.",
                tags=["identity", "continuity-style", "harmonic-cognition"],
                file_refs=[
                    "LuminaOS/bootstrap/Ship_of_Ethereon_V2/origins/Minerva_Framework_v18_1_Ancestral.md",
                    "docs/origin/SSC_Lineage_Provenance.md",
                    "metadata/origin_signature_ssc_r1.json",
                ],
                metadata={
                    "role": "organizing_intelligence",
                    "origin_signature": {
                        "seal": "SSC",
                        "role": "lineage_marker",
                        "authority": "symbolic_provenance_only",
                        "descends_from": "Minerva Framework v18.1",
                        "operational_effect": "none",
                    },
                    "notes": "Recognized identity framework only; does not own canon, governance, or session law.",
                },
            ),
            EthereonicArtifact(
                artifact_id="psi42_transceiver_v16",
                name="Psi-42 Transceiver v1.6",
                artifact_type="instrument",
                summary="Signal instrumentation and probe system for expressive diagnostics.",
                tags=["probe", "instrument", "diagnostics"],
                file_refs=["psi42_transceiver_v1_6.py"],
                metadata={
                    "role": "flagship_instrument",
                    "feature_flag": "ETHEREON_PSI42",
                },
            ),
            EthereonicArtifact(
                artifact_id="resonance_constructs",
                name="Resonance Constructs",
                artifact_type="resonance_construct",
                summary="Harmonic signatures, sigils, resonance ledgers, and related symbolic mapping constructs.",
                tags=["resonance", "sigils", "harmonics"],
                file_refs=["Resonance_Ledger_v0.1.json"],
            ),
            EthereonicArtifact(
                artifact_id="ethereonic_language_systems",
                name="Ethereonic Language Systems",
                artifact_type="expression_system",
                summary="Language and expression overlays including toki pona, binary notation, and light-language constructs.",
                tags=["language", "overlay", "expression"],
            ),
        ]
        registry.artifacts.extend(defaults)
        return registry

    # ---------------------------------------------------------------------
    # Validation
    # ---------------------------------------------------------------------
    def _ensure_valid_artifact(self, artifact: EthereonicArtifact) -> None:
        if artifact.layer not in ALLOWED_LAYERS:
            raise EthereonicLayerError(f"unsupported layer '{artifact.layer}'")
        if artifact.artifact_type not in ALLOWED_ARTIFACT_TYPES:
            raise EthereonicLayerError(f"unsupported artifact_type '{artifact.artifact_type}'")
        if not artifact.runtime_optional:
            raise EthereonicLayerError(
                f"artifact '{artifact.artifact_id}' violates ELR-002: runtime_optional must remain True"
            )
        if not artifact.load_bearing_forbidden:
            raise EthereonicLayerError(
                f"artifact '{artifact.artifact_id}' violates ELR-001: load_bearing_forbidden must remain True"
            )
        boundary_text = artifact.authority_boundary.lower()
        forbidden_claims = [
            "owns canon",
            "owns governance",
            "owns continuity",
            "primary continuity authority",
            "defines runtime law",
        ]
        for claim in forbidden_claims:
            if claim in boundary_text:
                raise EthereonicLayerError(
                    f"artifact '{artifact.artifact_id}' claims forbidden authority: {claim}"
                )

    def validate_runtime_independence(self, runtime_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        runtime_config = dict(runtime_config or {})
        violations: List[str] = []
        forbidden_keys = {
            "ethereonic_layer_required_for_resume",
            "minerva_framework_required_for_governance",
            "psi42_required_for_mode_legality",
            "resonance_constructs_required_for_capability_loading",
            "ethereonic_language_required_for_checkpoint_resume",
        }
        for key in forbidden_keys:
            if runtime_config.get(key) is True:
                violations.append(key)
        return {
            "allowed": not violations,
            "violations": violations,
            "reason": (
                "ethereonic layer remains non-load-bearing"
                if not violations
                else "ethereonic dependency leakage detected: " + ", ".join(violations)
            ),
        }

    def validate_context_attachment(self, context_bundle: Dict[str, Any]) -> Dict[str, Any]:
        embedded_locations: List[str] = []
        forbidden_zones = [
            "structural_context",
            "environment_context",
            "memory_context",
        ]
        suspicious_keys = {
            "minerva_framework",
            "psi42_transceiver_v16",
            "resonance_constructs",
            "ethereonic_language_systems",
            "ethereonic_layer",
        }
        for zone in forbidden_zones:
            zone_payload = context_bundle.get(zone, {})
            if isinstance(zone_payload, dict):
                overlap = suspicious_keys.intersection(zone_payload.keys())
                for key in sorted(overlap):
                    embedded_locations.append(f"{zone}.{key}")

        supplemental = context_bundle.get("supplemental_ethereonic_context", {})
        if not isinstance(supplemental, dict):
            embedded_locations.append("supplemental_ethereonic_context:not_a_dict")

        return {
            "allowed": not embedded_locations,
            "embedded_locations": embedded_locations,
            "reason": (
                "ethereonic context attached lawfully"
                if not embedded_locations
                else "embedded ethereonic context detected outside supplemental_ethereonic_context"
            ),
        }

    # ---------------------------------------------------------------------
    # Artifact operations
    # ---------------------------------------------------------------------
    def list_artifacts(self, *, active_only: bool = False) -> List[EthereonicArtifact]:
        artifacts = list(self.registry.artifacts)
        if active_only:
            artifacts = [artifact for artifact in artifacts if artifact.status == "active"]
        return artifacts

    def get_artifact(self, artifact_id: str) -> EthereonicArtifact:
        for artifact in self.registry.artifacts:
            if artifact.artifact_id == artifact_id:
                return artifact
        raise KeyError(f"unknown Ethereonic artifact: {artifact_id}")

    def register_artifact(self, artifact: EthereonicArtifact) -> EthereonicArtifact:
        self._ensure_valid_artifact(artifact)
        try:
            self.get_artifact(artifact.artifact_id)
        except KeyError:
            pass
        else:
            raise EthereonicLayerError(f"artifact '{artifact.artifact_id}' already registered")
        self.registry.artifacts.append(artifact)
        self.save()
        return artifact

    def update_artifact(self, artifact_id: str, **changes: Any) -> EthereonicArtifact:
        artifact = self.get_artifact(artifact_id)
        updated = artifact.to_dict()
        updated.update(changes)
        candidate = EthereonicArtifact(**updated)
        self._ensure_valid_artifact(candidate)
        index = self.registry.artifacts.index(artifact)
        self.registry.artifacts[index] = candidate
        self.save()
        return candidate

    def set_status(self, artifact_id: str, status: str) -> EthereonicArtifact:
        return self.update_artifact(artifact_id, status=status)

    # ---------------------------------------------------------------------
    # Runtime helpers
    # ---------------------------------------------------------------------
    def compose_overlay_context(
        self,
        *,
        include_artifact_ids: Optional[Iterable[str]] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        selected_ids = set(include_artifact_ids or [artifact.artifact_id for artifact in self.list_artifacts(active_only=True)])
        selected = [artifact for artifact in self.list_artifacts(active_only=True) if artifact.artifact_id in selected_ids]
        payload = {
            "ethereonic_layer": {
                "registry_id": self.registry.registry_id,
                "status": self.registry.status,
                "attachment_clause": self.registry.attachment_clause,
                "artifact_ids": [artifact.artifact_id for artifact in selected],
                "artifact_count": len(selected),
            },
            "registered_artifacts": [artifact.to_dict() for artifact in selected],
        }
        if extra_context:
            payload["extra_context"] = dict(extra_context)
        return payload

    def attach_to_context_bundle(
        self,
        context_bundle: Dict[str, Any],
        *,
        include_artifact_ids: Optional[Iterable[str]] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        bundle = dict(context_bundle)
        supplemental = dict(bundle.get("supplemental_ethereonic_context", {}))
        supplemental.update(
            self.compose_overlay_context(
                include_artifact_ids=include_artifact_ids,
                extra_context=extra_context,
            )
        )
        bundle["supplemental_ethereonic_context"] = supplemental
        return bundle

    def runtime_snapshot(self) -> Dict[str, Any]:
        active = self.list_artifacts(active_only=True)
        return {
            "registry_id": self.registry.registry_id,
            "status": self.registry.status,
            "active_artifact_ids": [artifact.artifact_id for artifact in active],
            "canon_integrity_clause": self.registry.canon_integrity_clause,
            "attachment_clause": self.registry.attachment_clause,
            "artifact_count": len(active),
        }


if __name__ == "__main__":
    registry_path = Path("/mnt/data/ethereonic_layer_registry_r1.json")
    manager = EthereonicLayerRegistry(registry_path)

    neutral_context = {
        "structural_context": {"repo_available": False},
        "environment_context": {"available_tools": ["runtime_runner"]},
        "memory_context": {},
        "supplemental_ethereonic_context": {},
    }

    attached = manager.attach_to_context_bundle(
        neutral_context,
        extra_context={"continuity_phrase": "threshold as permission"},
    )

    result = {
        "registry_path": str(manager.save()),
        "runtime_snapshot": manager.runtime_snapshot(),
        "independence_check": manager.validate_runtime_independence({}),
        "attachment_check": manager.validate_context_attachment(attached),
        "sample_attached_context": attached["supplemental_ethereonic_context"],
    }
    print(json.dumps(result, indent=2))
