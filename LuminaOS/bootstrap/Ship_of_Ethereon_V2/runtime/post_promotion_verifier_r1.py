from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import argparse
import json
import sys


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists() or (parent / "LuminaOS").exists():
            return parent
    return Path.cwd()


REPO_ROOT = infer_repo_root()


def repo_relative_path(path: str | Path) -> str:
    resolved = Path(path).resolve()
    root = REPO_ROOT.resolve()
    try:
        return str(resolved.relative_to(root))
    except ValueError:
        return str(path)


DEFAULT_PROMOTION_RECEIPT = REPO_ROOT / "artifacts" / "runtime_truth" / "current" / "promotion_receipt.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "runtime_truth" / "current" / "post_promotion_verification.json"


def read_json(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, payload: Dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def build_post_promotion_verification(
    promotion_receipt: Dict[str, Any],
    *,
    promotion_receipt_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Build the post-promotion verifier receipt from the committed promotion receipt.

    The symbolic dependency verdict is intentionally read from the committed
    promotion receipt's payload instead of being hardcoded by this verifier.
    Missing payload data defaults to a violation so incomplete receipts fail
    closed.
    """
    symbolic_dependency_violation = bool(
        promotion_receipt.get("promotion_payload", {}).get("symbolic_dependency_violation", True)
    )

    checks = {
        "promotion_receipt_present": bool(promotion_receipt),
        "promotion_payload_present": isinstance(promotion_receipt.get("promotion_payload"), dict),
        "no_symbolic_dependency_violation": symbolic_dependency_violation is False,
    }
    payload = {
        "schema_version": "post-promotion-verification-r1",
        "generated_at": utc_now(),
        "promotion_receipt_path": repo_relative_path(promotion_receipt_path) if promotion_receipt_path else None,
        "promotion_receipt_id": promotion_receipt.get("promotion_receipt_id") or promotion_receipt.get("receipt_id"),
        "promotion_artifact": promotion_receipt.get("promotion_artifact"),
        "symbolic_dependency_violation": symbolic_dependency_violation,
        "checks": checks,
        "passed": all(checks.values()),
        "authority_boundary": "Verification receipt only; does not authorize action, mutate canon, change mode legality, expose capabilities, or execute tools.",
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a committed promotion receipt after promotion.")
    parser.add_argument("--promotion-receipt", default=str(DEFAULT_PROMOTION_RECEIPT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    receipt_path = Path(args.promotion_receipt)
    promotion_receipt = read_json(receipt_path)
    payload = build_post_promotion_verification(promotion_receipt, promotion_receipt_path=receipt_path)
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
