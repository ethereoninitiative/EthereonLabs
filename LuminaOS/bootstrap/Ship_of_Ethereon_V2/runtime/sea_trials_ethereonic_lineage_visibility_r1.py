from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict
import json

try:
    from .ethereonic_layer_r1 import EthereonicLayerRegistry
except Exception:
    from ethereonic_layer_r1 import EthereonicLayerRegistry


REQUIRED_FILE_REFS = [
    "LuminaOS/bootstrap/Ship_of_Ethereon_V2/origins/Minerva_Framework_v18_1_Ancestral.md",
    "docs/origin/SSC_Lineage_Provenance.md",
    "metadata/origin_signature_ssc_r1.json",
]

EXPECTED_ORIGIN_SIGNATURE = {
    "seal": "SSC",
    "role": "lineage_marker",
    "authority": "symbolic_provenance_only",
    "descends_from": "Minerva Framework v18.1",
    "operational_effect": "none",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def run_trial() -> Dict[str, Any]:
    root = repo_root()
    with TemporaryDirectory(prefix="ethereonic-lineage-") as tmp:
        registry_path = Path(tmp) / "ethereonic_layer_registry_r1.json"
        manager = EthereonicLayerRegistry(registry_path)
        artifact = manager.get_artifact("minerva_framework")

        checks = {
            "registry_is_runtime_generated_state": manager.registry_path == registry_path,
            "registry_file_was_generated": registry_path.exists(),
            "ancestral_refs_match": artifact.file_refs == REQUIRED_FILE_REFS,
            "ancestral_refs_exist": all((root / ref).exists() for ref in REQUIRED_FILE_REFS),
            "origin_signature_matches": artifact.metadata.get("origin_signature") == EXPECTED_ORIGIN_SIGNATURE,
            "runtime_optional": artifact.runtime_optional is True,
            "load_bearing_forbidden": artifact.load_bearing_forbidden is True,
            "safe_config_remains_allowed": manager.validate_runtime_independence({}).get("allowed") is True,
            "hidden_governance_dependency_is_rejected": manager.validate_runtime_independence(
                {"minerva_framework_required_for_governance": True}
            ).get("allowed") is False,
        }

        return {
            "trial": "ethereonic_lineage_visibility_r1",
            "passed": all(checks.values()),
            "checks": checks,
            "registry_path": str(registry_path),
            "artifact": artifact.to_dict(),
            "authority_boundary": (
                "Origin lineage is inspectable context only. It does not grant governance, canon, "
                "checkpoint, mode, capability, or continuity authority."
            ),
        }


if __name__ == "__main__":
    result = run_trial()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
