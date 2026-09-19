"""Explicit host doorway for repository orientation and subsequent return."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

BOOTSTRAP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOTSTRAP / "runtime"))
import lumina_arrival_r1 as arrival


def configure_parser(parser):
    commands = parser.add_subparsers(dest="arrival_command", required=True)
    prep = commands.add_parser("prepare", help="Snapshot pinned repository sources and explicitly selected continuity.")
    prep.add_argument("--repo", default=str(BOOTSTRAP.parents[2]), type=Path)
    prep.add_argument("--ref", default="HEAD")
    prep.add_argument("--output", required=True, type=Path)
    for name in ("provider", "model", "account-scope"):
        prep.add_argument("--" + name, required=True)
    prep.add_argument("--intention-store", type=Path)
    prep.add_argument("--intention-id", action="append", default=[], dest="intention_ids")
    prep.add_argument("--meaning-base", type=Path)
    prep.add_argument("--memory-id", action="append", default=[], dest="memory_ids")
    prep.add_argument("--project-id")
    prep.add_argument("--source-root", type=Path)
    prep.add_argument("--previous", type=Path)
    prep.add_argument("--previous-packet")
    prep.add_argument("--previous-head")
    for name in ("prompt", "respond", "status"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--arrival", required=True, type=Path)
        cmd.add_argument("--require-packet", required=True)
        cmd.add_argument("--require-head", required=name == "respond")
        if name == "respond":
            cmd.add_argument("--response", required=True, type=Path)


def execute(args):
    try:
        if args.arrival_command == "prepare":
            names = ("repo", "ref", "output", "provider", "model", "account_scope", "intention_store", "intention_ids",
                     "meaning_base", "memory_ids", "project_id", "source_root", "previous", "previous_packet", "previous_head")
            result = arrival.prepare(**{name: getattr(args, name) for name in names})
        elif args.arrival_command == "respond":
            result = arrival.respond(args.arrival, args.require_packet, args.require_head, arrival.read(args.response))
        else:
            result = getattr(arrival, args.arrival_command)(args.arrival, args.require_packet, args.require_head)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "refused", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    configure_parser(parser)
    raise SystemExit(execute(parser.parse_args()))
