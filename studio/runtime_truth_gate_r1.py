from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple
import json
import subprocess
import sys


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent
    return Path.cwd()


ROOT = repo_root()
RUNTIME_DIR = ROOT / "LuminaOS" / "bootstrap" / "Ship_of_Ethereon_V2" / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from runtime_truth_public_snapshot_r1 import build_public_runtime_truth_snapshot  # noqa: E402
from runtime_truth_reconciliation_gate_r1 import run_gate as run_reconciliation_gate  # noqa: E402


REQUIRED_RUNTIME_TRUTH_FILES = [
    "artifacts/runtime_truth/known_uncertainties.json",
    "public/runtime/runtime_truth_snapshot.json",
    "public/runtime/latest_cycle.json",
]

FORBIDDEN_AMBIGUOUS_KEYS = ["symbolic_dependency"]
REQUIRED_SYMBOLIC_BOUNDARY = {
    "symbolic_context_present": True,
    "symbolic_dependency_allowed": False,
}


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
    payload = read_json(root / "artifacts/runtime_truth/known_uncertainties.json")
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

    runtime_truth = payload.get("runtime_truth") if isinstance(payload, dict) else None
    boundary = runtime_truth.get("symbolic_boundary") if isinstance(runtime_truth, dict) else payload.get("symbolic_boundary")
    if isinstance(boundary, dict):
        for key, expected in REQUIRED_SYMBOLIC_BOUNDARY.items():
            if boundary.get(key) is not expected:
                errors.append(f"{label} symbolic boundary {key} expected {expected}, got {boundary.get(key)}")
    else:
        errors.append(f"{label} missing symbolic_boundary block")
    return errors


def validate_required_files(root: Path) -> List[str]:
    return [
        f"missing required runtime truth file: {rel}"
        for rel in REQUIRED_RUNTIME_TRUTH_FILES
        if not (root / rel).exists()
    ]


def validate_host_smoke(root: Path) -> List[str]:
    script = root / "LuminaOS/bootstrap/Ship_of_Ethereon_V2/install/lumina_doctor_ci_r1.py"
    if not script.exists():
        return [f"missing CI doctor: {script.relative_to(root)}"]
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(root / "LuminaOS/bootstrap/Ship_of_Ethereon_V2"),
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return []
    detail = proc.stderr.strip() or proc.stdout.strip()
    return [f"fresh-state host smoke failed: {detail[-1200:]}"]


def run_gate() -> Tuple[bool, List[str]]:
    root = ROOT
    errors: List[str] = []
    errors.extend(validate_required_files(root))
    if errors:
        return False, errors

    try:
        build_public_runtime_truth_snapshot()
    except Exception as exc:
        errors.append(f"runtime truth refresh failed: {exc}")
        return False, errors

    errors.extend(validate_known_uncertainties(root))
    for rel in ["public/runtime/runtime_truth_snapshot.json", "public/runtime/latest_cycle.json"]:
        errors.extend(validate_symbolic_boundary(read_json(root / rel), rel))

    reconciliation_ok, reconciliation_checks, _ = run_reconciliation_gate()
    if not reconciliation_ok:
        failed = [name for name, passed in reconciliation_checks.items() if not passed]
        errors.append(f"runtime truth reconciliation failed: {', '.join(failed)}")

    errors.extend(validate_host_smoke(root))
    return not errors, errors


if __name__ == "__main__":
    ok, errors = run_gate()
    print(json.dumps({"status": "pass" if ok else "fail", "errors": errors}, indent=2))
    raise SystemExit(0 if ok else 1)
