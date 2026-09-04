#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from runtime_runner_r1_merged import BASE_DIR as DEFAULT_RUNTIME_BASE_DIR
from vessel_continuity_transfer_r1 import VesselContinuityTransfer, VesselTransferError


DEFAULT_SURFACE_ROOT = Path(DEFAULT_RUNTIME_BASE_DIR) / "lumina_project_surface"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Export, verify, or explicitly import one bounded Lumina project-return capsule. "
            "Transfer does not resume a session or create identity or runtime authority."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    export = subparsers.add_parser("export", help="Export the latest return state for one project.")
    export.add_argument("--project-id", required=True)
    export.add_argument("--capsule", required=True)
    export.add_argument("--source-vessel-id", required=True)
    export.add_argument(
        "--surface-root",
        default=None,
        help="Project-surface root. Defaults to the active local runtime project surface.",
    )

    verify = subparsers.add_parser("verify", help="Verify a capsule without importing it.")
    verify.add_argument("--capsule", required=True)

    import_parser = subparsers.add_parser(
        "import", help="Import a verified capsule into an empty project slot."
    )
    import_parser.add_argument("--capsule", required=True)
    import_parser.add_argument("--target-vessel-id", required=True)
    import_parser.add_argument(
        "--surface-root",
        default=None,
        help="Target project-surface root. Defaults to the active local runtime project surface.",
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "verify":
            capsule = VesselContinuityTransfer.verify_capsule(args.capsule)
            output = {
                "verified": True,
                "schema_version": capsule.get("schema_version"),
                "capsule_id": capsule.get("capsule_id"),
                "project_id": capsule.get("project_id"),
                "capsule_hash": capsule.get("capsule_hash"),
                "authority_effect": False,
                "identity_claimed": False,
            }
        else:
            configured_root = (
                Path(args.surface_root).expanduser()
                if args.surface_root
                else DEFAULT_SURFACE_ROOT
            )
            transfer = VesselContinuityTransfer(configured_root)
            if args.command == "export":
                output = transfer.export_project(
                    project_id=args.project_id,
                    capsule_path=args.capsule,
                    source_vessel_id=args.source_vessel_id,
                ).receipt
            else:
                output = transfer.import_project(
                    capsule_path=args.capsule,
                    target_vessel_id=args.target_vessel_id,
                ).receipt
        print(json.dumps(output, indent=2))
        return 0
    except (VesselTransferError, FileNotFoundError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
