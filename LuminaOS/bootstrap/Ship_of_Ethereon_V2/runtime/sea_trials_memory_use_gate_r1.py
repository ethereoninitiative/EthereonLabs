"""Memory Use Gate R1: consequence, lifecycle and receipt sea trials."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

try:
    from .lumina_meaning_evidence_r1 import capture_evidence
    from .lumina_meaning_metabolism_layer_r1 import MeaningAssimilationLedger, MeaningMetabolismLayer
    from .memory_use_gate_r1 import evaluate_memory_use
except ImportError:
    from lumina_meaning_evidence_r1 import capture_evidence
    from lumina_meaning_metabolism_layer_r1 import MeaningAssimilationLedger, MeaningMetabolismLayer
    from memory_use_gate_r1 import evaluate_memory_use

BOOT = Path(__file__).resolve().parents[1]
PROJECT = "lumina-os"


class MemoryUseGateTrials(unittest.TestCase):
    sample_receipts = {}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="lumina-memory-use-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source_root = self.root / "sources"
        self.source_root.mkdir()
        self.source = self.source_root / "observation.txt"
        self.source.write_text("Original, inspectable evidence.\n", encoding="utf-8")
        self.base = self.root / "runner"
        self.ledger = MeaningAssimilationLedger(self.base / "meaning_memory", create=False)
        self.layer = MeaningMetabolismLayer()
        self.record = self.layer.assimilate(
            source_event="An observation was recorded.",
            felt_meaning="A bounded source matters.",
            changed_assumption="Evidence is not action permission.",
            future_behavior="Check the source.",
            source_evidence=[capture_evidence(source_root=self.source_root, relative_path="observation.txt")],
        )

    def retain(self):
        self.ledger.append_record(project_id=PROJECT, record=self.record)
        self.ledger.append_review(project_id=PROJECT, review=self.layer.review(
            record=self.record, still_holds=True, revision_note="Reviewed for evidence-bound recall.",
        ))

    def gate(self, consequence="low", **options):
        return evaluate_memory_use(
            self.ledger, project_id=PROJECT, evidence_identifier=self.record.assimilation_id,
            source_root=self.source_root, action_consequence=consequence, **options,
        )

    def test_same_memory_consequence_changes_outcome(self):
        self.retain()
        before = self.ledger._ledger_path(PROJECT).read_bytes()
        low = self.gate()
        high_without_verifier = self.gate("high")
        high_pending = self.gate("high", verifier_available=True)
        high_passed = self.gate("high", verifier_available=True, verifier_result="passed")
        high_failed = self.gate("high", verifier_available=True, verifier_result="failed")
        self.assertEqual([r["final_disposition"] for r in
                          (low, high_without_verifier, high_pending, high_passed, high_failed)],
                         ["proceed", "abstain", "verify", "proceed", "abstain"])
        self.assertEqual(high_pending["inclusion_decision"], "defer")
        self.assertEqual(high_without_verifier["inclusion_decision"], "exclude")
        self.assertEqual(before, self.ledger._ledger_path(PROJECT).read_bytes())
        self.assertEqual(self.ledger.read_entries(PROJECT)[0]["record"]["source_evidence"][0]["source_text"],
                         self.source.read_text())
        self.assertEqual(low["evidence_source_hashes"][0]["sha256"], self.record.source_evidence[0]["sha256"])
        self.__class__.sample_receipts["low"] = low
        self.__class__.sample_receipts["high_pending"] = high_pending

    def test_revoked_history_inspectable_but_inoperative(self):
        self.retain()
        self.ledger.append_review(project_id=PROJECT, review=self.layer.review(
            record=self.record, still_holds=False, revision_note="Withdraw this inference.",
        ))
        before = self.ledger._ledger_path(PROJECT).read_bytes()
        output = self.gate()
        self.assertEqual((output["lifecycle_state"], output["inclusion_decision"], output["final_disposition"]),
                         ("revoked", "exclude", "abstain"))
        self.assertEqual(len(self.ledger.read_entries(PROJECT)), 3)
        self.assertIsNotNone(output["evidence_hash"])
        self.assertEqual(before, self.ledger._ledger_path(PROJECT).read_bytes())
        self.__class__.sample_receipts["revoked"] = output

    def test_superseded_archived_and_external_veto(self):
        self.record.status = "archived"
        self.retain()
        archived = self.gate()
        self.assertEqual((archived["lifecycle_state"], archived["final_disposition"]), ("superseded", "abstain"))
        self.assertIsNotNone(archived["evidence_hash"])
        self.ledger = MeaningAssimilationLedger(self.root / "other" / "meaning_memory", create=False)
        self.record.status = "active_candidate"
        self.retain()
        for state in ("superseded", "revoked", "conflicting", "unknown"):
            with self.subTest(state=state):
                output = self.gate(control_state=state)
                self.assertEqual(output["final_disposition"], "abstain")
                self.assertEqual(output["inclusion_decision"], "exclude")

    def test_unknown_and_missing_controls_receipted(self):
        missing = self.gate()
        self.assertEqual((missing["lifecycle_state"], missing["final_disposition"]), ("missing", "abstain"))
        self.assertIsNone(missing["evidence_hash"])
        self.retain()
        for value in ("mystery", "", None):
            with self.subTest(value=value):
                output = self.gate(consequence=value)
                self.assertEqual(output["final_disposition"], "abstain")
                self.assertEqual(output["inclusion_reason"], "invalid_or_unknown_input")
        self.__class__.sample_receipts["missing"] = missing

    def test_stale_and_unavailable_sources_withheld(self):
        self.retain()
        self.source.write_text("Modified evidence.\n", encoding="utf-8")
        self.assertEqual(self.gate()["final_disposition"], "abstain")
        self.assertEqual(self.gate()["inclusion_reason"], "source_changed")
        self.source.unlink()
        self.assertEqual(self.gate()["inclusion_reason"], "source_unavailable")

    def test_conflicting_corrupt_ledger_fail_closed(self):
        self.retain()
        path = self.ledger._ledger_path(PROJECT)
        path.write_bytes(path.read_bytes() + b'{"record": bogus}\n')
        receipt = self.gate()
        self.assertEqual(receipt["lifecycle_state"], "conflicting")
        self.assertEqual(receipt["final_disposition"], "abstain")
        self.assertEqual(receipt["inclusion_decision"], "exclude")

    def test_unavailable_or_failed_verifier_never_rescues_high_risk(self):
        self.retain()
        no_provider = self.gate("high", verifier_available=False, verifier_result="passed")
        self.assertEqual(no_provider["final_disposition"], "abstain")
        self.assertEqual(self.gate("high", verifier_available=True, verifier_result="failed")["final_disposition"], "abstain")
        self.assertEqual(self.gate("low", verifier_available=True, verifier_result="failed")["final_disposition"], "abstain")

    def test_real_cli_path_emits_receipt_and_exit_code(self):
        self.retain()
        def command(*additional):
            process = subprocess.run([
                sys.executable, str(BOOT / "bin" / "lumina"), "memory", "use", "--project-id", PROJECT,
                "--base-dir", str(self.base), "--source-root", str(self.source_root),
                "--id", self.record.assimilation_id, *additional,
            ], capture_output=True, text=True)
            self.assertTrue(process.stdout, process.stderr)
            return process.returncode, json.loads(process.stdout)
        self.assertEqual(command("--consequence", "low")[0], 0)
        pending_code, pending = command("--consequence", "high", "--verifier-available")
        self.assertEqual((pending_code, pending["final_disposition"]), (2, "verify"))
        refused_code, refused = command("--consequence", "high")
        self.assertEqual((refused_code, refused["final_disposition"]), (1, "abstain"))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MemoryUseGateTrials)
    results = unittest.TextTestRunner(verbosity=2).run(suite)
    receipt = {
        "schema_version": "memory_use_gate_r1_validation_receipt",
        "policy_version": "memory_use_gate_r1",
        "executed_tests": results.testsRun,
        "failures": len(results.failures),
        "errors": len(results.errors),
        "status": "passed" if results.wasSuccessful() else "failed",
        "illustrative_decisions": MemoryUseGateTrials.sample_receipts,
        "scope": "Local deterministic meaning-ledger and CLI, not external verifier authentication or resident continuity.",
    }
    print(json.dumps(receipt, sort_keys=True, indent=2), flush=True)
    if len(sys.argv) == 3 and sys.argv[1] == "--receipt-out":
        target = Path(sys.argv[2])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if results.wasSuccessful() else 1)
