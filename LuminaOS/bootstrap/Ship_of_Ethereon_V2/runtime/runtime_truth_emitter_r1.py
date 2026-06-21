from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

try:
    from .governance_integrity_r1 import GovernanceIntegrityChain
    from .canon_lineage_store_r1 import CanonLineageStore
except Exception:
    from governance_integrity_r1 import GovernanceIntegrityChain
    from canon_lineage_store_r1 import CanonLineageStore


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or ((parent / "LuminaOS").exists() and (parent / "public").exists()):
            return parent
    return Path.cwd()


def repo_relative_path(path: str | Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(infer_repo_root().resolve()).as_posix()
    except Exception:
        return candidate.as_posix()


DEFAULT_FORBIDDEN_SYMBOLIC_DEPENDENCIES = [
    "session recovery legality",
    "mode transition legality",
    "mutation authorization",
    "promotion gating",
    "canon lineage authority",
    "checkpoint legality",
    "capability exposure",
    "governance verification",
]


class RuntimeTruthEmitter:
    """Emit audit receipts from concrete runtime state without claiming authority."""

    def __init__(
        self,
        *,
        output_dir: str | Path = "artifacts/runtime_truth/current",
        governance_log_path: Optional[str | Path] = None,
        canon_lineage_path: Optional[str | Path] = None,
        protocol_path: Optional[str | Path] = None,
        capability_registry_path: Optional[str | Path] = None,
        artifact_prefix: str = "",
        authority_scope: str = "runtime_state_observation",
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.governance_log_path = Path(governance_log_path) if governance_log_path else None
        self.canon_lineage_path = Path(canon_lineage_path) if canon_lineage_path else None
        self.protocol_path = Path(protocol_path) if protocol_path else None
        self.capability_registry_path = Path(capability_registry_path) if capability_registry_path else None
        self.artifact_prefix = artifact_prefix
        self.authority_scope = authority_scope

    def emit_all(self) -> Dict[str, Any]:
        outputs: Dict[str, Any] = {
            "generated_at": utc_now(),
            "authority_scope": self.authority_scope,
            "artifacts": {},
        }
        outputs["artifacts"]["symbolic_dependency_contract"] = self.write_symbolic_dependency_contract()
        outputs["artifacts"]["governance_chain_verification"] = self.write_governance_chain_verification()
        outputs["artifacts"]["canon_lineage_verification"] = self.write_canon_lineage_verification()
        outputs["artifacts"]["capability_registry_audit"] = self.write_capability_registry_audit()
        outputs["artifacts"]["protocol_conformance_report"] = self.write_protocol_conformance_report()
        return outputs

    def _write_json(self, filename: str, payload: Dict[str, Any]) -> str:
        path = self.output_dir / f"{self.artifact_prefix}{filename}"
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        return repo_relative_path(path)

    def write_governance_chain_verification(self) -> str:
        if not self.governance_log_path:
            payload = {
                "generated_at": utc_now(),
                "authority_scope": self.authority_scope,
                "status": "missing_input",
                "valid": None,
                "reason": "No governance_log_path supplied.",
            }
        else:
            chain = GovernanceIntegrityChain(self.governance_log_path)
            verification = chain.verify_chain()
            verification["log_path"] = repo_relative_path(self.governance_log_path)
            payload = {
                "generated_at": utc_now(),
                "authority_scope": self.authority_scope,
                "status": "verified" if self.governance_log_path.exists() else "empty_or_missing",
                **verification,
            }
        return self._write_json("governance_chain_verification.json", payload)

    def write_canon_lineage_verification(self) -> str:
        if not self.canon_lineage_path:
            payload = {
                "generated_at": utc_now(),
                "authority_scope": self.authority_scope,
                "status": "missing_input",
                "valid": None,
                "reason": "No canon_lineage_path supplied.",
            }
        else:
            store = CanonLineageStore(self.canon_lineage_path)
            verification = store.verify_lineage()
            verification["lineage_path"] = repo_relative_path(self.canon_lineage_path)
            payload = {
                "generated_at": utc_now(),
                "authority_scope": self.authority_scope,
                "status": "verified" if self.canon_lineage_path.exists() else "empty_or_missing",
                **verification,
            }
        return self._write_json("canon_lineage_verification.json", payload)

    def write_symbolic_dependency_contract(self) -> str:
        payload = {
            "version": "1.0",
            "generated_at": utc_now(),
            "authority_scope": self.authority_scope,
            "symbolic_context_present_allowed": True,
            "symbolic_dependency_allowed": False,
            "forbidden_symbolic_dependencies": DEFAULT_FORBIDDEN_SYMBOLIC_DEPENDENCIES,
            "required_runtime_semantics": {
                "symbolic_context_present": "expressive or supplemental context is attached or visible",
                "symbolic_dependency": "structural behavior requires symbolic interpretation",
                "symbolic_dependency_leakage": "symbolic interpretation becomes necessary for law, authority, or continuity",
            },
            "audit_rule": "Presence is allowed; dependency must halt or fail validation.",
        }
        return self._write_json("symbolic_dependency_contract.json", payload)

    def write_capability_registry_audit(self) -> str:
        payload: Dict[str, Any] = {
            "generated_at": utc_now(),
            "authority_scope": self.authority_scope,
            "status": "missing_input",
            "capability_count": None,
            "issues": [],
        }
        if self.capability_registry_path and self.capability_registry_path.exists():
            data = json.loads(self.capability_registry_path.read_text(encoding="utf-8"))
            capabilities = data.get("capabilities", [])
            issues: List[str] = []
            for idx, cap in enumerate(capabilities):
                cid = cap.get("capability_id", f"index_{idx}")
                if not cap.get("allowed_modes"):
                    issues.append(f"{cid}: missing allowed_modes")
                if "authority_boundary" not in cap:
                    issues.append(f"{cid}: missing authority_boundary")
                if cap.get("mutation_scope") not in {"none", "session", "artifact", "canon", "governance", None}:
                    issues.append(f"{cid}: unexpected mutation_scope {cap.get('mutation_scope')}")
            payload = {
                "generated_at": utc_now(),
                "authority_scope": self.authority_scope,
                "status": "audited",
                "registry_path": repo_relative_path(self.capability_registry_path),
                "capability_count": len(capabilities),
                "valid": not issues,
                "issues": issues,
            }
        return self._write_json("capability_registry_audit.json", payload)

    def write_protocol_conformance_report(self) -> str:
        payload: Dict[str, Any] = {
            "generated_at": utc_now(),
            "authority_scope": self.authority_scope,
            "status": "missing_input",
            "valid": None,
            "issues": [],
        }
        if self.protocol_path and self.protocol_path.exists():
            protocol = json.loads(self.protocol_path.read_text(encoding="utf-8"))
            issues: List[str] = []
            document = protocol.get("document", {})
            if document.get("version") != "1.3":
                issues.append("protocol version is not 1.3")
            observation = protocol.get("canonical_modes_extension", {}).get("Observation", {})
            if observation.get("mutation_allowed") is not False:
                issues.append("Observation mutation_allowed must be false")
            if observation.get("promotion_allowed") is not False:
                issues.append("Observation promotion_allowed must be false")
            gate = protocol.get("promotion_gate_extension", {})
            required = gate.get("additional_required_fields", [])
            if "conceptual_layer_check_confirmation" not in required:
                issues.append("promotion gate missing conceptual_layer_check_confirmation")
            payload = {
                "generated_at": utc_now(),
                "authority_scope": self.authority_scope,
                "status": "audited",
                "protocol_path": repo_relative_path(self.protocol_path),
                "valid": not issues,
                "issues": issues,
            }
        return self._write_json("protocol_conformance_report.json", payload)


if __name__ == "__main__":
    emitter = RuntimeTruthEmitter()
    print(json.dumps(emitter.emit_all(), indent=2))
