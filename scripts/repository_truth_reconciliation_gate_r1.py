#!/usr/bin/env python3
"""Reconcile active EthereonLabs surfaces, generated artifacts, and public claims."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "docs" / "ACTIVE_SURFACE_REGISTRY_R1.json"
RUNTIME_UI_EMITTER_PATH = ROOT / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime" / "runtime_ui_snapshot_emitter_r1.py"
RUNTIME_TRUTH_PUBLIC_SNAPSHOT_PATH = ROOT / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime" / "runtime_truth_public_snapshot_r1.py"
RUNTIME_VIEWER_PATH = ROOT / "assets" / "js" / "runtime-viewer.js"
PAGES_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "deploy-pages.yml"
PUBLIC_RUNTIME_RECEIPT_PATH = ROOT / "public" / "runtime" / "latest_cycle.json"
CURRENT_RUNTIME_UI_SCHEMA = "lumina-runtime-ui-cycle-v0.4"
CURRENT_PUBLIC_RECEIPT_URL = "/public/runtime/latest_cycle.json"
REQUIRED_SURFACE_FIELDS = {
    "surface_id",
    "name",
    "status",
    "default_wiring",
    "paths",
    "validation_paths",
    "authority_boundary",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path.relative_to(ROOT)}")
    return payload


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema_version") != "ethereon-active-surface-registry-r1":
        errors.append("active surface registry schema_version is not R1")

    surfaces = registry.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        return errors + ["active surface registry must contain surfaces"]

    seen_ids: set[str] = set()
    for index, surface in enumerate(surfaces):
        if not isinstance(surface, dict):
            errors.append(f"surface[{index}] is not an object")
            continue
        missing = sorted(REQUIRED_SURFACE_FIELDS - set(surface))
        if missing:
            errors.append(f"surface[{index}] missing fields: {', '.join(missing)}")
            continue

        surface_id = surface.get("surface_id")
        if not isinstance(surface_id, str) or not surface_id:
            errors.append(f"surface[{index}] has invalid surface_id")
        elif surface_id in seen_ids:
            errors.append(f"duplicate surface_id: {surface_id}")
        else:
            seen_ids.add(surface_id)

        if not isinstance(surface.get("authority_boundary"), str) or not surface["authority_boundary"].strip():
            errors.append(f"{surface_id or index} has empty authority_boundary")

        for field in ("paths", "validation_paths"):
            paths = surface.get(field)
            if not isinstance(paths, list):
                errors.append(f"{surface_id or index} {field} must be a list")
                continue
            for relative in paths:
                if not isinstance(relative, str) or not relative:
                    errors.append(f"{surface_id or index} contains invalid {field} entry")
                    continue
                if not (ROOT / relative).exists():
                    errors.append(f"{surface_id or index} references missing path: {relative}")

    required_ids = {
        "lumina_runtime_substrate",
        "lumina_bridge_r2",
        "lumina_ubuntu_appliance",
        "lumina_windows_desktop_r1",
        "chamber_public_surface",
        "hra_training_dataset_v0_1",
        "resonant_field_reveal_sample_0001",
        "ethereon_public_site",
    }
    missing_ids = sorted(required_ids - seen_ids)
    if missing_ids:
        errors.append(f"active surface registry missing required surfaces: {', '.join(missing_ids)}")
    return errors


def validate_claim_markers(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    markers_by_path = registry.get("claim_markers")
    if not isinstance(markers_by_path, dict) or not markers_by_path:
        return ["active surface registry must contain claim_markers"]

    for relative, markers in markers_by_path.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"claim surface is missing: {relative}")
            continue
        if not isinstance(markers, list) or not markers:
            errors.append(f"claim markers must be a non-empty list: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if not isinstance(marker, str) or marker not in text:
                errors.append(f"claim surface {relative} is missing marker: {marker!r}")
    return errors


def validate_runtime_ui_contract() -> list[str]:
    errors: list[str] = []
    required_paths = {
        "runtime UI emitter": RUNTIME_UI_EMITTER_PATH,
        "public runtime normalizer": RUNTIME_TRUTH_PUBLIC_SNAPSHOT_PATH,
        "runtime viewer": RUNTIME_VIEWER_PATH,
        "Pages deployment workflow": PAGES_WORKFLOW_PATH,
        "public runtime receipt": PUBLIC_RUNTIME_RECEIPT_PATH,
    }
    missing = [label for label, path in required_paths.items() if not path.is_file()]
    if missing:
        return [f"runtime UI contract is missing required path: {label}" for label in missing]

    emitter_text = RUNTIME_UI_EMITTER_PATH.read_text(encoding="utf-8")
    normalizer_text = RUNTIME_TRUTH_PUBLIC_SNAPSHOT_PATH.read_text(encoding="utf-8")
    viewer_text = RUNTIME_VIEWER_PATH.read_text(encoding="utf-8")
    pages_text = PAGES_WORKFLOW_PATH.read_text(encoding="utf-8")
    receipt = read_json(PUBLIC_RUNTIME_RECEIPT_PATH)

    if f'"schema_version": "{CURRENT_RUNTIME_UI_SCHEMA}"' not in emitter_text:
        errors.append(
            f"runtime UI emitter schema does not match current public contract: {CURRENT_RUNTIME_UI_SCHEMA}"
        )
    if f'LATEST_CYCLE_SCHEMA_VERSION = "{CURRENT_RUNTIME_UI_SCHEMA}"' not in normalizer_text:
        errors.append(
            f"public runtime normalizer schema does not match current public contract: {CURRENT_RUNTIME_UI_SCHEMA}"
        )
    if receipt.get("schema_version") != CURRENT_RUNTIME_UI_SCHEMA:
        errors.append(
            "public runtime receipt schema mismatch: "
            f"expected {CURRENT_RUNTIME_UI_SCHEMA!r}, got {receipt.get('schema_version')!r}"
        )
    if f"const RECEIPT_PATH = '{CURRENT_PUBLIC_RECEIPT_URL}';" not in viewer_text:
        errors.append(
            f"runtime viewer receipt path does not match deployed public artifact: {CURRENT_PUBLIC_RECEIPT_URL}"
        )
    if "uses: actions/upload-pages-artifact@v3" not in pages_text or "path: ." not in pages_text:
        errors.append("Pages deployment must publish the repository root for the current runtime viewer path contract")
    return errors


def find_surface(registry: dict[str, Any], surface_id: str) -> dict[str, Any]:
    for surface in registry.get("surfaces", []):
        if isinstance(surface, dict) and surface.get("surface_id") == surface_id:
            return surface
    raise KeyError(surface_id)


def validate_hra_receipt(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    surface = find_surface(registry, "hra_training_dataset_v0_1")
    workdir = ROOT / surface["reproducibility"]["working_directory"]
    receipt_path = workdir / "hra_training_dataset_creation_receipt_v0_1.json"
    receipt = read_json(receipt_path)

    for key in surface.get("forbidden_receipt_keys", []):
        if key in receipt:
            errors.append(f"HRA receipt contains retired claim key: {key}")

    for key, expected in surface.get("receipt_contract", {}).items():
        if receipt.get(key) != expected:
            errors.append(
                f"HRA receipt contract mismatch for {key}: expected {expected!r}, got {receipt.get(key)!r}"
            )

    if receipt.get("accepted_records_written") != 40:
        errors.append("HRA receipt must record exactly 40 accepted records")
    if receipt.get("training_authorized") is not False:
        errors.append("HRA receipt must keep training_authorized false")
    return errors


def validate_generated_artifacts(registry: dict[str, Any]) -> list[str]:
    """Regenerate declared HRA outputs in isolation and compare exact committed bytes."""
    errors: list[str] = []
    surface = find_surface(registry, "hra_training_dataset_v0_1")
    reproducibility = surface.get("reproducibility")
    if not isinstance(reproducibility, dict):
        return ["HRA surface is missing reproducibility contract"]

    source_dir = ROOT / reproducibility["working_directory"]
    generator_name = reproducibility["generator"]
    generated_artifacts = reproducibility["generated_artifacts"]

    with tempfile.TemporaryDirectory(prefix="ethereon-truth-gate-") as temporary:
        isolated = Path(temporary) / "hra"
        shutil.copytree(source_dir, isolated)
        process = subprocess.run(
            [sys.executable, generator_name],
            cwd=isolated,
            capture_output=True,
            text=True,
        )
        if process.returncode != 0:
            detail = process.stderr.strip() or process.stdout.strip()
            return [f"isolated HRA regeneration failed: {detail[-1200:]}"]

        for artifact in generated_artifacts:
            committed_path = source_dir / artifact
            regenerated_path = isolated / artifact
            if not committed_path.is_file():
                errors.append(f"declared generated artifact is missing: {committed_path.relative_to(ROOT)}")
                continue
            if not regenerated_path.is_file():
                errors.append(f"generator did not emit declared artifact: {artifact}")
                continue
            if committed_path.read_bytes() != regenerated_path.read_bytes():
                errors.append(
                    "generated artifact drift: "
                    f"{committed_path.relative_to(ROOT)} does not match isolated generator output"
                )
    return errors


def run_gate() -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not REGISTRY_PATH.is_file():
        return False, ["missing docs/ACTIVE_SURFACE_REGISTRY_R1.json"]

    try:
        registry = read_json(REGISTRY_PATH)
        errors.extend(validate_registry(registry))
        errors.extend(validate_claim_markers(registry))
        errors.extend(validate_runtime_ui_contract())
        errors.extend(validate_hra_receipt(registry))
        errors.extend(validate_generated_artifacts(registry))
    except Exception as exc:
        errors.append(f"truth reconciliation gate exception: {exc}")
    return not errors, errors


if __name__ == "__main__":
    ok, errors = run_gate()
    print(
        json.dumps(
            {
                "schema_version": "repository-truth-reconciliation-gate-r1",
                "status": "pass" if ok else "fail",
                "errors": errors,
            },
            indent=2,
        )
    )
    raise SystemExit(0 if ok else 1)
