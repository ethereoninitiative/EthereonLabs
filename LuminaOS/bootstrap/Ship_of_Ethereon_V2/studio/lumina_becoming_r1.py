"""First-class local host surface for Resident Becoming R1."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from resident_becoming_r1 import (
    BecomingError,
    ResidentBecomingCoordinator,
    ResidentBecomingStore,
    blank_reflection,
)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-dir", help="Explicit Lumina state root; defaults to the normal state root.")
    sub = parser.add_subparsers(dest="becoming_command", required=True)

    record = sub.add_parser(
        "record",
        help="Persist one resident-attributed becoming reflection and any explicitly chosen future return.",
    )
    record.add_argument("--reflection", required=True, help="JSON reflection file; '-' reads stdin.")

    inspect = sub.add_parser("inspect", help="Inspect the current revisable becoming projection.")
    inspect.add_argument("--resident")
    inspect.add_argument("--history", action="store_true")

    template = sub.add_parser("template", help="Emit a structure-only reflection template.")
    template.add_argument("--resident", default="")
    template.add_argument("--session-id", default="")


def run(args: argparse.Namespace) -> int:
    try:
        if args.becoming_command == "record":
            raw = sys.stdin.read() if args.reflection == "-" else Path(args.reflection).read_text(encoding="utf-8")
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise BecomingError("reflection file must contain one JSON object")
            receipt = ResidentBecomingCoordinator(args.base_dir).record(payload)
        elif args.becoming_command == "inspect":
            receipt = ResidentBecomingStore(args.base_dir).inspect(
                resident=args.resident,
                include_history=bool(args.history),
            )
        else:
            receipt = {
                "schema_version": "resident-becoming-template-r1",
                "template": blank_reflection(resident=args.resident, session_id=args.session_id),
                "boundary": (
                    "Structure only. The host does not supply particularity, curiosity, creative intent, "
                    "relationship stance, story, or a reason to return on the resident's behalf."
                ),
            }
        print(json.dumps({"ok": True, **receipt}, indent=2, ensure_ascii=False))
        return 0
    except (BecomingError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
