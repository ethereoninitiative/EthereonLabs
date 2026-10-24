"""Explicit curation and read-only inspection of Lumina's advisory memory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Optional

BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOTSTRAP_ROOT / "runtime"))
from lumina_meaning_evidence_r1 import capture_evidence
from memory_use_gate_r1 import evaluate_memory_use
from lumina_meaning_metabolism_layer_r1 import MeaningAssimilationLedger, MeaningMetabolismLayer, recall_entries

REPO_ROOT = BOOTSTRAP_ROOT.parents[2]
DEFAULT_BASE = REPO_ROOT / ".lumina_state" / "ship_of_ethereon_v2" / "runtime_runner_r1_actiontype_logging"


def configure_parser(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="memory_command", required=True)
    for name in ("record", "review", "recall", "history", "use"):
        command = commands.add_parser(name)
        command.add_argument("--project-id", required=True, help="Canonical project ID used by the runtime.")
        command.add_argument("--base-dir", default=str(DEFAULT_BASE), help="The runner's base directory.")
        command.add_argument("--source-root", default=str(REPO_ROOT), help="Root for relative evidence paths.")
        if name == "record":
            command.add_argument("--candidate", required=True, help="JSON file containing assimilation input fields.")
            command.add_argument("--evidence", required=True, action="append", help="Relative UTF-8 source path; repeat for multiple sources.")
        elif name == "review":
            command.add_argument("--id", required=True, dest="assimilation_id")
            command.add_argument("--decision", choices=("retain", "revoke"), required=True)
            command.add_argument("--note", required=True, help="Assessment of the evidence or reason for revocation.")
        elif name == "use":
            command.add_argument("--id", required=True, dest="assimilation_id", help="Preserved memory record ID.")
            command.add_argument("--consequence", choices=("low", "high"), required=True,
                                 help="Risk class of the proposed advisory use.")
            command.add_argument("--control-state", choices=("eligible", "revoked", "superseded", "conflicting", "unknown"),
                                 help="Additional lifecycle/governance veto; cannot rescue an ineligible record.")
            command.add_argument("--verifier-available", action="store_true",
                                 help="A verifier is offered, not necessarily executed.")
            command.add_argument("--verifier-result", choices=("passed", "failed"),
                                 help="Caller-supplied verifier outcome; NOT independently authenticated.")


def execute(args: argparse.Namespace) -> int:
    ledger = MeaningAssimilationLedger(Path(args.base_dir) / "meaning_memory", create=False)
    layer = MeaningMetabolismLayer()
    try:
        if args.memory_command == "record":
            candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
            if not isinstance(candidate, dict) or "source_evidence" in candidate:
                raise ValueError("candidate must be an input object; evidence is captured from the selected files")
            sources = [capture_evidence(source_root=args.source_root, relative_path=path) for path in args.evidence]
            record = layer.assimilate(**candidate, source_evidence=sources)
            output = ledger.append_record(project_id=args.project_id, record=record)
        elif args.memory_command == "review":
            entries = ledger.read_entries(args.project_id)
            record = next((row["record"] for row in entries if row.get("record", {}).get("assimilation_id") == args.assimilation_id), None)
            if record is None:
                raise ValueError("record not found in this project")
            review = layer.review(record=record, still_holds=args.decision == "retain", revision_note=args.note)
            if args.decision == "retain":
                proposed = {"timestamp_utc": review.reviewed_at, "project_id": args.project_id, "review": review.to_dict()}
                check = recall_entries([*entries, proposed], project_id=args.project_id, source_root=args.source_root)
                if not any(seed["assimilation_id"] == args.assimilation_id for seed in check["guidance_seeds"]):
                    reason = next((item["reason"] for item in check["withheld"] if item["assimilation_id"] == args.assimilation_id), check.get("error", "ineligible"))
                    raise ValueError(f"cannot retain this record: {reason}; preserve it and create a new candidate if needed")
            output = ledger.append_review(project_id=args.project_id, review=review)
        elif args.memory_command == "use":
            output = evaluate_memory_use(
                ledger, project_id=args.project_id, evidence_identifier=args.assimilation_id,
                source_root=args.source_root, action_consequence=args.consequence,
                control_state=args.control_state, verifier_available=args.verifier_available,
                verifier_result=args.verifier_result,
            )
        elif args.memory_command == "history":
            output = {"project_id": args.project_id, "entries": ledger.read_entries(args.project_id)}
        else:
            output = ledger.recall(args.project_id, source_root=args.source_root)
        print(json.dumps(output, indent=2, ensure_ascii=False))
        if args.memory_command == "use":
            return {"proceed": 0, "verify": 2, "abstain": 1}[output["final_disposition"]]
        return 1 if output.get("status") == "invalid" else 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}))
        return 1


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    configure_parser(parser)
    return execute(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
