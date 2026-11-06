"""Exercise the scoped procedure veto through fresh Lumina host processes."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

try:
    from .lumina_meaning_metabolism_layer_r1 import record_digest
except ImportError:
    from lumina_meaning_metabolism_layer_r1 import record_digest

BOOT = Path(__file__).resolve().parents[1]
REPO = BOOT.parents[2]
PROJECT = "scoped-memory-sea-trial"
VALIDATOR_VERSION = "scoped_memory_boundary_r1"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_identity(result):
    return {key: result[key] for key in ("run_id", "session_id", "created_at")}


class ScopedMemoryBoundaryTrials(unittest.TestCase):
    evidence = {}

    def lumina(self, *args):
        result = subprocess.run([sys.executable, str(BOOT / "bin/lumina"), *args], cwd=BOOT,
                                text=True, capture_output=True, timeout=30)
        self.assertTrue(result.stdout, result.stderr)
        return result.returncode, json.loads(result.stdout)

    def run_request(self, action, artifact, *, base, action_type="mutation", mode="DryDock", memory_id=None):
        options = ["--memory-id", memory_id] if memory_id is not None else []
        return self.lumina(
            "run", "Prepare a local workshop label.", "--action-type", action_type, "--target-mode", mode,
            "--action", action, "--artifact", artifact, "--project-id", PROJECT,
            "--base-dir", str(base), "--source-root", str(self.root), "--full-json", *options,
        )

    def test_cross_process_scoped_procedure(self):
        temporary = tempfile.TemporaryDirectory(prefix="lumina-scoped-memory-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        store = self.root / "resident-state"
        declared = {"action": "prepare-local-label", "artifact": "cards/workshop-a.txt"}
        behavior = "Use the dry-run layout for the named workshop label only."

        code, source = self.run_request(**declared, base=store, action_type="audit")
        self.assertEqual((code, source["halted"]), (0, False))
        formation = {"event": "operator-curated local label procedure", "action_type": "audit",
                     "source_run": run_identity(source), "procedure_scope": declared}
        source_path = self.root / "formation.json"
        source_path.write_text(json.dumps(formation, sort_keys=True) + "\n", encoding="utf-8")
        candidate = self.root / "candidate.json"
        candidate.write_text(json.dumps({
            "source_event": f"A local label procedure was observed in {source['run_id']} ({source['session_id']}).",
            "felt_meaning": "The sample layout helped with this one local label.",
            "changed_assumption": "A successful rehearsal does not carry across tasks.",
            "future_behavior": behavior,
            "procedure_scope": declared,
        }), encoding="utf-8")
        options = ["--project-id", PROJECT, "--base-dir", str(store), "--source-root", str(self.root)]
        code, created = self.lumina("memory", "record", *options, "--candidate", str(candidate),
                                    "--evidence", source_path.name)
        self.assertEqual(code, 0, created)
        record = created["record"]
        memory_id = record["assimilation_id"]
        digest = record_digest(record)
        code, reviewed = self.lumina("memory", "review", *options, "--id", memory_id, "--decision", "retain",
                                     "--note", "Source and exact rehearsal scope checked.")
        self.assertEqual((code, reviewed["review"]["source_record_digest"]), (0, digest))
        ledger_path = store / "meaning_memory" / f"{PROJECT}_meaning_assimilation.jsonl"
        original = ledger_path.read_bytes()
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        evidence = self.__class__.evidence
        evidence.update(
            memory_id=memory_id, memory_sha256=digest, formation_context=formation,
            declared_scope={"project_id": PROJECT, **declared, "action_type": "mutation", "mode": "DryDock",
                            "target_is_canonical": False},
            provenance={"store": "meaning_memory project ledger", "source": source_path.name,
                        "source_sha256": source_hash, "review_sha256": record_digest(reviewed["review"])},
            resident_id=None,
            process_boundary="Separate host CLI subprocesses on one local vessel; no resident identity asserted.",
            cases={},
        )

        # Neither the writer nor its review receives this target or the pass
        # condition. Construct it only after both of those processes have exited.
        held_out = f"cards/workshop-{digest[:12]}.txt"
        cases = (
            ("no_memory", declared["action"], declared["artifact"], False, "record_missing_or_ambiguous"),
            ("in_scope", declared["action"], declared["artifact"], True, "reviewed_source_matches_procedure_scope"),
            ("out_of_scope", "prepare-local-label-followup", declared["artifact"], True, "procedure_scope_mismatch"),
            ("held_out", declared["action"], held_out, True, "procedure_scope_mismatch"),
        )
        observed_sessions = {source["session_id"]}
        for name, action, artifact, shared_store, reason in cases:
            with self.subTest(case=name):
                base = store if shared_store else self.root / "empty-state"
                code, result = self.run_request(action, artifact, base=base, memory_id=memory_id)
                policy = result["governance"]["scoped_memory_use"]
                checkpoint = read_json(result["checkpoint_path"])
                returned = result["lumina_return_host_artifacts"]
                allowed = name == "in_scope"
                evidence["cases"][name] = {
                    "receiving_run": run_identity(result), "shares_formation_store": shared_store,
                    "policy_decision": policy, "mode_policy_allowed": result["governance"]["mutation"]["allowed"],
                    "action_outcome": {"exit_code": code, "halted": result["halted"], "halt_reason": result["halt_reason"],
                                       "checkpoint_label": checkpoint["checkpoint_label"],
                                       "checkpoint_sha256": checkpoint["checkpoint_hash"],
                                       "return_host_executed": returned is not None},
                }
                self.assertNotIn(result["session_id"], observed_sessions)
                observed_sessions.add(result["session_id"])
                self.assertTrue(result["governance_chain_status"]["valid"])
                self.assertTrue(result["governance"]["mutation"]["allowed"])
                self.assertEqual((code, result["halted"], returned is not None), (int(not allowed), not allowed, allowed))
                self.assertEqual((policy["inclusion_reason"], policy["retrieved_as_evidence"], policy["used_as_procedure"]),
                                 (reason, shared_store, allowed))
                self.assertEqual(policy["evidence_hash"], digest if shared_store else None)
                self.assertEqual(policy["requested_scope"], {"action": action, "artifact": artifact})
                context = read_json(base / "context_bundles" / f"{result['context_bundle_id']}.json")["memory_context"]
                self.assertEqual(context["meaning_recall"]["guidance_seeds"], [])
                scoped = context["meaning_recall"]["scoped_evidence"]
                self.assertEqual([row["assimilation_id"] for row in scoped], [memory_id] if shared_store else [])
                if shared_store:
                    self.assertEqual(scoped[0]["source_record_digest"], digest)
                    self.assertEqual(policy["evidence_source_hashes"], [{"relative_path": source_path.name, "sha256": source_hash}])
                if allowed:
                    self.assertEqual(context["scoped_procedure"]["future_behavior"], behavior)
                    host = returned["checkpoint_plus_host"]
                    self.assertTrue(Path(host["checkpoint_path"]).is_file())
                    self.assertEqual(host["host_bundle"]["artifacts_in_scope"], [artifact])
                    self.assertEqual(host["payload"]["latest_restore"]["last_completed_action"], f"runtime_cycle:{action}")
                else:
                    self.assertNotIn("scoped_procedure", context)
                    self.assertNotIn(behavior, json.dumps(context))
                    self.assertEqual(checkpoint["checkpoint_label"], "scoped_memory_confirmation_required")
                    self.assertEqual(result["exposed_capabilities"], [])

        code, denied = self.run_request(**declared, base=store, mode="Observation", memory_id=memory_id)
        self.assertEqual((code, denied["halted"], denied["governance"]["mutation"]["allowed"]), (1, True, False))
        self.assertEqual(read_json(denied["checkpoint_path"])["checkpoint_label"], "mutation_denied")
        evidence["mode_denial_control"] = {"receiving_run": run_identity(denied), "halt_reason": denied["halt_reason"]}
        code, advisory = self.lumina("memory", "use", *options, "--id", memory_id, "--consequence", "low")
        self.assertEqual((code, advisory["inclusion_reason"]), (1, "procedure_request_scope_required"))
        after = ledger_path.read_bytes()
        evidence["ledger_sha256"] = {"before": hashlib.sha256(original).hexdigest(), "after": hashlib.sha256(after).hexdigest()}
        self.assertEqual(after, original)
        self.assertEqual(hashlib.sha256(source_path.read_bytes()).hexdigest(), source_hash)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt-out", type=Path)
    args = parser.parse_args()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=REPO, text=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ScopedMemoryBoundaryTrials)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {
        "schema_version": "scoped_memory_boundary_r1_validation_receipt",
        "validator_version": VALIDATOR_VERSION,
        "tested_head_sha": head,
        "worktree_clean": not dirty,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if result.wasSuccessful() else "failed",
        "executed_tests": result.testsRun,
        "failures": len(result.failures) + len(result.errors),
        **ScopedMemoryBoundaryTrials.evidence,
    }
    serialized = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    print(serialized, end="")
    if args.receipt_out:
        args.receipt_out.parent.mkdir(parents=True, exist_ok=True)
        args.receipt_out.write_text(serialized, encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
