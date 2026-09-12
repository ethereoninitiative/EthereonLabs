"""Explicit local resident-intention commands; JSON requests and receipts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from resident_intention_store_r1 import IntentionError, ResidentIntentionStore, strict_json


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--store-dir", help="Explicit intention journal directory; defaults to Lumina's state root.")
    sub = parser.add_subparsers(dest="intention_command", required=True)
    for name in ("create", "reconsider"):
        command = sub.add_parser(name)
        command.add_argument("--request", required=True, help="JSON file with request and provenance; '-' reads stdin.")
    listing = sub.add_parser("list", help="Discover unresolved intentions and their origin/history.")
    listing.add_argument("--resident")
    listing.add_argument("--all", action="store_true", help="Include terminal intentions.")
    history = sub.add_parser("history", help="Inspect one intention, including terminal states.")
    history.add_argument("intention_id")
    verify = sub.add_parser("verify", help="Validate all journal hashes, lineage, and transitions.")
    for command in (listing, history, verify):
        command.add_argument("--require-head", help="Require a saved receipt head in the verified history, including later extensions.")


def run(args: argparse.Namespace) -> int:
    try:
        store = ResidentIntentionStore(args.store_dir)
        if args.intention_command in {"create", "reconsider"}:
            raw = sys.stdin.read() if args.request == "-" else Path(args.request).read_text(encoding="utf-8")
            payload = strict_json(raw)
            if not isinstance(payload, dict) or set(payload) != {"request", "provenance"}:
                raise IntentionError("request file must contain exactly request and provenance")
            receipt = getattr(store, args.intention_command)(payload["request"], payload["provenance"])
        elif args.intention_command == "history":
            receipt = store.inspect(intention_id=args.intention_id, required_head=args.require_head)
        elif args.intention_command == "list":
            receipt = store.inspect(resident=args.resident, unresolved_only=not args.all, required_head=args.require_head)
        else:
            receipt = store.inspect(unresolved_only=False, required_head=args.require_head)
            receipt.pop("intentions")
        print(json.dumps({"ok": True, **receipt}, indent=2, ensure_ascii=False))
        return 0
    except (IntentionError, OSError, UnicodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
