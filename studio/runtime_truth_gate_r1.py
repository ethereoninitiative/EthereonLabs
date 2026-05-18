from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple
import json
import sys


REQUIRED_RUNTIME_TRUTH_FILES = [
    "artifacts/runtime_truth/known_uncertainties.json",
    "public/runtime/runtime_truth_snapshot.json",
    "public/runtime/latest_cycle.json",
]

FORBIDDEN_AMBIGUOUS_KEYS = [
    "symbolic_dependency"
]

REQUIRED_SYMBOLIC_BOUNDARY = {
    "symbolic_context_present": True,
    "symbolic_dependency_allowed": False,
}


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent
    return Path.cwd()


def read_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def scan_for_key(node, key: str, path: str = "$", hits: List[str] | None = None) -> List[str]:
    hits = hits if hits is not None else []
    if isinstance(node, dict):
        for k, v in node.items():
            child_path = f"{path}.{k}"
            if k == key:
                hits.append(child_path)
            scan_for_key(v, key, child_path, hits)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            scan_for_key(item, key, f"{path}[{idx}]", hits)
    return hits


def validate_known_uncertainties(root: Path) -> List[str]:
    errors: List[str] = []
    path = root / "artifacts/runtime_truth/known_uncertainties.json"
    payload = read_json(path)
    uncertainties = payload.get("uncertainties", [])
    if not uncertainties:
        errors.append("known_uncertainties.json must contain at least one uncertainty")
    for item in uncertainties:
        for field in ["id", "area", "status", "statement", "needed_evidence"]:
            if not item.get(field):
                errors.append(f"known uncertainty missing {field}: {item}")
    return errors


def validate_symbolic_boundary(payload: Dict, label: str) -> List[str]:
    errors: List[str] = []
    for key in FORBIDDEN_AMBIGUOUS_KEYS:
        hits = scan_for_key(payload, key)
        if hits:
            errors.append(f"{label} contains ambiguous forbidden key {key} at {hits}")

    boundary = None
    runtime_truth = payload.get("runtime_truth") if isinstance(payload, dict) else None
    if isinstance(runtime_truth, dict):
        boundary = runtime_truth.get("symbolic_boundary")
    if boundary is None and "symbolic_boundary" in payload:
        boundary = payload.get("symbolic_boundary")

    if isinstance(boundary, dict):
        for key, expected in REQUIRED_SYMBOLIC_BOUNDARY.items():
            if boundary.get(key) is not expected:
                errors.append(f"{label} symbolic boundary {key} expected {expected}, got {boundary.get(key)}")
    else:
        errors.append(f"{label} missing symbolic_boundary block")
    return errors


def validate_required_files(root: Path) -> List[str]:
    errors: List[str] = []
    for rel in REQUIRED_RUNTIME_TRUTH_FILES:
        if not (root / rel).exists():
            errors.append(f"missing required runtime truth file: {rel}")
    return errors


def run_gate() -> Tuple[bool, List[str]]:
    root = repo_root()
    errors: List[str] = []
    errors.extend(validate_required_files(root))
    if errors:
        return False, errors

    errors.extend(validate_known_uncertainties(root))
    for rel in ["public/runtime/runtime_truth_snapshot.json", "public/runtime/latest_cycle.json"]:
        errors.extend(validate_symbolic_boundary(read_json(root / rel), rel))

    return not errors, errors


if __name__ == "__main__":
    ok, errors = run_gate()
    if ok:
        print(json.dumps({"status": "pass", "errors": []}, indent=2))
        sys.exit(0)
    print(json.dumps({"status": "fail", "errors": errors}, indent=2))
    sys.exit(1)
