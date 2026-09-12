"""Meaning recall, revocation, source grounding, and process-transfer trials."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

try:
    from .lumina_meaning_evidence_r1 import capture_evidence, MAX_EVIDENCE_BYTES
    from .lumina_meaning_metabolism_layer_r1 import MeaningAssimilationLedger, MeaningMetabolismLayer, record_digest
    from .runtime_runner_r1_merged import RuntimeRunner
except ImportError:
    from lumina_meaning_evidence_r1 import capture_evidence, MAX_EVIDENCE_BYTES
    from lumina_meaning_metabolism_layer_r1 import MeaningAssimilationLedger, MeaningMetabolismLayer, record_digest
    from runtime_runner_r1_merged import RuntimeRunner

BOOT = Path(__file__).resolve().parents[1]
PROJECT = "lumina-os"


class MeaningRecallTrials(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="lumina-meaning-recall-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.base = self.root / "runner"
        self.sources = self.root / "sources"
        self.sources.mkdir()
        self.source = self.sources / "observation.txt"
        self.source.write_text("Return probe: restored references need verification.\n", encoding="utf-8")
        self.layer = MeaningMetabolismLayer()
        self.ledger = MeaningAssimilationLedger(self.base / "meaning_memory", create=False)
        self.record = self.layer.assimilate(
            source_event="A return probe found a stale reference.",
            felt_meaning="Orientation depends on checking the reference after return.",
            changed_assumption="Preserved references may no longer resolve.",
            future_behavior="Check the restored reference before using it.",
            source_evidence=[capture_evidence(source_root=self.sources, relative_path="observation.txt")],
        )

    def retain(self):
        self.ledger.append_record(project_id=PROJECT, record=self.record)
        self.ledger.append_review(project_id=PROJECT, review=self.layer.review(
            record=self.record, still_holds=True, revision_note="The preserved probe supports this bounded check.",
        ))

    def recall(self):
        return self.ledger.recall(PROJECT, source_root=self.sources)

    def reason(self):
        result = self.recall()
        self.assertEqual(result["guidance_seeds"], [])
        return result["withheld"][0]["reason"]

    def test_missing_memory_is_read_only(self):
        self.assertEqual(self.recall()["status"], "empty")
        self.assertFalse(self.base.exists())

    def test_unreviewed_candidate_cannot_become_guidance(self):
        self.ledger.append_record(project_id=PROJECT, record=self.record)
        self.assertEqual(self.reason(), "review_required")

    def test_reviewed_recall_is_attributable_and_read_only(self):
        self.retain()
        before = self.ledger._ledger_path(PROJECT).read_bytes()
        first = self.recall()
        second = self.recall()
        self.assertEqual(first["guidance_seeds"], second["guidance_seeds"])
        seed = first["guidance_seeds"][0]
        self.assertEqual(seed["future_behavior"], self.record.future_behavior)
        self.assertEqual(seed["source_record_digest"], record_digest(self.record.to_dict()))
        self.assertEqual(seed["eligibility"], "reviewed_source_matches")
        self.assertNotIn("source_text", json.dumps(first))
        self.assertEqual(before, self.ledger._ledger_path(PROJECT).read_bytes())
        self.assertEqual(self.ledger.read_entries(PROJECT)[0]["record"]["source_evidence"][0]["source_text"], self.source.read_text())

    def test_changed_source_withheld_and_original_preserved(self):
        self.retain()
        original = self.ledger._ledger_path(PROJECT).read_bytes()
        self.source.write_text("Probe superseded: reference removed.\n")
        self.assertEqual(self.reason(), "source_changed")
        self.assertEqual(original, self.ledger._ledger_path(PROJECT).read_bytes())

    def test_missing_source_and_missing_root_withheld(self):
        self.retain()
        without_root = self.ledger.recall(PROJECT)
        self.assertEqual(without_root["withheld"][0]["reason"], "source_root_required")
        self.source.unlink()
        self.assertEqual(self.reason(), "source_unavailable")

    def test_revocation_survives_later_positive_review_and_clock_skew(self):
        self.retain()
        for holds, timestamp in ((False, "2030-01-01T00:00:00+00:00"), (True, "2020-01-01T00:00:00+00:00")):
            review = self.layer.review(record=self.record, still_holds=holds, revision_note="Explicit lifecycle test.")
            review.reviewed_at = timestamp
            self.ledger.append_review(project_id=PROJECT, review=review)
        self.assertEqual(self.reason(), "revoked")
        entries = self.ledger.read_entries(PROJECT)
        self.assertEqual(len(entries), 4)
        summary = self.ledger.summary(entries, source_root=self.sources)
        self.assertIsNone(summary["latest_future_behavior"])
        self.assertEqual(summary["latest_record_id"], self.record.assimilation_id)

    def test_boolean_coercion_cannot_turn_false_into_true(self):
        for value in ("false", "true", 0, 1, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.layer.review(record=self.record, still_holds=value, revision_note="Should fail.")

    def test_expired_review_requires_new_candidate(self):
        self.record.review_after = "2026-09-11"
        self.retain()
        result = self.ledger.recall(PROJECT, source_root=self.sources, now=datetime(2026, 9, 11, tzinfo=timezone.utc))
        self.assertEqual(result["withheld"][0]["reason"], "review_due")

    def test_evidence_count_does_not_substitute_for_sources(self):
        self.record.source_evidence = []
        self.record.evidence_count = 999
        self.retain()
        self.assertEqual(self.reason(), "evidence_missing")

    def test_legacy_history_is_preserved_but_requires_bound_review(self):
        self.retain()
        entries = self.ledger.read_entries(PROJECT)
        entries[0]["record"].pop("source_evidence")
        entries[0]["record"]["schema_version"] = "meaning_assimilation_record_r1"
        entries[1]["review"].pop("source_record_digest")
        entries[1]["review"]["schema_version"] = "meaning_assimilation_review_r1"
        path = self.ledger._ledger_path(PROJECT)
        path.write_text("".join(json.dumps(row) + "\n" for row in entries))
        before = path.read_bytes()
        self.assertEqual(self.reason(), "review_required")
        self.assertEqual(before, path.read_bytes())
        entries[1]["review"]["still_holds"] = False
        path.write_text("".join(json.dumps(row) + "\n" for row in entries))
        self.assertEqual(self.reason(), "revoked")

    def test_mismatched_review_and_duplicate_id_rejected_before_write(self):
        self.retain()
        before = self.ledger._ledger_path(PROJECT).read_bytes()
        with self.assertRaises(ValueError):
            self.ledger.append_record(project_id=PROJECT, record=self.record)
        changed = deepcopy(self.record)
        changed.future_behavior = "Different advice."
        with self.assertRaises(ValueError):
            self.ledger.append_review(project_id=PROJECT, review=self.layer.review(record=changed, still_holds=True, revision_note="Wrong content."))
        self.assertEqual(before, self.ledger._ledger_path(PROJECT).read_bytes())

    def test_corrupt_or_ambiguous_history_yields_no_guidance(self):
        self.retain()
        path = self.ledger._ledger_path(PROJECT)
        good = path.read_text()
        variants = [good[:-1], good + "{broken\n", good + good.splitlines()[0] + "\n",
                    good.replace('"still_holds": true', '"still_holds": false, "still_holds": true'),
                    good.replace('"still_holds": true', '"still_holds": "false"'),
                    good.replace('"meaning_assimilation_record_r2"', '"meaning_assimilation_record_r99"'),
                    good.replace('"project_id": "lumina-os"', '"project_id": "other-project"'),
                    good.replace('"sha256": "', '"sha256": "0'),
                    "\n".join(reversed(good.splitlines())) + "\n"]
        for index, data in enumerate(variants):
            with self.subTest(index=index):
                path.write_text(data)
                result = self.recall()
                self.assertEqual(result["status"], "invalid")
                self.assertEqual(result["guidance_seeds"], [])

    def test_project_scope_cannot_alias_or_leak(self):
        self.retain()
        self.assertEqual(self.ledger.recall("other-project", source_root=self.sources)["guidance_seeds"], [])
        for identifier in ("lumina/os", "lumina os", "../lumina-os", "", "a" * 81):
            with self.subTest(identifier=identifier):
                self.assertEqual(self.ledger.recall(identifier, source_root=self.sources)["status"], "invalid")

    def test_source_capture_rejects_escape_and_oversize(self):
        for path in ("../outside.txt", "/outside.txt", "C:\\outside.txt", "./observation.txt"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                capture_evidence(source_root=self.sources, relative_path=path)
        outside = self.root / "outside.txt"
        outside.write_text("outside")
        (self.sources / "escape.txt").symlink_to(outside)
        with self.assertRaises(ValueError):
            capture_evidence(source_root=self.sources, relative_path="escape.txt")
        self.source.write_bytes(b"x" * (MAX_EVIDENCE_BYTES + 1))
        with self.assertRaises(ValueError):
            capture_evidence(source_root=self.sources, relative_path="observation.txt")

    def test_portable_recall_in_fresh_process_and_relocated_source_root(self):
        self.retain()
        before = self.recall()["guidance_seeds"]
        target = self.root / "replacement-vessel"
        shutil.copytree(self.base, target / "runner")
        shutil.copytree(self.sources, target / "sources")
        self.source.unlink()  # Successful recall must not depend on the old vessel.
        process = subprocess.run([
            sys.executable, str(BOOT / "bin" / "lumina"), "memory", "recall", "--project-id", PROJECT,
            "--base-dir", str(target / "runner"), "--source-root", str(target / "sources"),
        ], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(process.stdout)["guidance_seeds"], before)
        imported = MeaningAssimilationLedger(target / "runner" / "meaning_memory", create=False)
        self.assertEqual(imported.read_entries(PROJECT), self.ledger.read_entries(PROJECT))

    def run_context(self, runner, overrides=None):
        result = runner.run_cycle(current_mode="Continuity", target_mode="Observation", action_type="audit",
                                  project_id=PROJECT, requested_action="inspect_memory_return",
                                  meaning_source_root=self.sources, context_bundle_overrides=overrides)
        self.assertFalse(result.halted, result.halt_reason)
        path = runner.context_builder.output_dir / f"{result.context_bundle_id}.json"
        return json.loads(path.read_text()), result

    def test_runtime_recomputes_recall_after_reset_and_revocation(self):
        self.retain()
        first, before = self.run_context(RuntimeRunner(base_dir=self.base, seed_committed_canon=False))
        self.assertEqual(len(first["memory_context"]["meaning_recall"]["guidance_seeds"]), 1)
        self.ledger.append_review(project_id=PROJECT, review=self.layer.review(record=self.record, still_holds=False, revision_note="Revoke stale interpretation."))
        second, after = self.run_context(RuntimeRunner(base_dir=self.base, seed_committed_canon=False),
                                         {"memory_context": first["memory_context"]})
        recalled = second["memory_context"]["meaning_recall"]
        self.assertEqual(recalled["guidance_seeds"], [])
        self.assertEqual(recalled["withheld"][0]["reason"], "revoked")
        self.assertEqual(before.exposed_capabilities, after.exposed_capabilities)
        self.assertEqual(before.governance["transition"]["allowed"], after.governance["transition"]["allowed"])

    def test_adapter_paths_inherit_grounded_projection(self):
        from runtime_runner_psi42_v18_adapter_r1 import RuntimeRunner as DefaultRunner
        from runtime_runner_self_guided_bridge_r1 import SelfGuidedReturnHostRuntimeRunner
        self.retain()
        for cls in (DefaultRunner, SelfGuidedReturnHostRuntimeRunner):
            with self.subTest(runner=cls.__name__):
                bundle, _ = self.run_context(cls(base_dir=self.base, seed_committed_canon=False))
                self.assertEqual(bundle["memory_context"]["meaning_recall"]["guidance_seeds"][0]["assimilation_id"], self.record.assimilation_id)

    def test_cli_curation_checks_sources_and_blocks_reactivation(self):
        candidate = self.root / "candidate.json"
        candidate.write_text(json.dumps({key: getattr(self.record, key) for key in
            ("source_event", "felt_meaning", "changed_assumption", "future_behavior")}))
        def command(verb, *options):
            result = subprocess.run([sys.executable, str(BOOT / "bin" / "lumina"), "memory", verb,
                "--project-id", PROJECT, "--base-dir", str(self.base), "--source-root", str(self.sources), *options],
                capture_output=True, text=True)
            return result.returncode, json.loads(result.stdout)
        code, created = command("record", "--candidate", str(candidate), "--evidence", "observation.txt")
        self.assertEqual(code, 0)
        identifier = created["record"]["assimilation_id"]
        self.assertEqual(command("review", "--id", identifier, "--decision", "retain", "--note", "Supported by probe.")[0], 0)
        self.assertEqual(command("review", "--id", identifier, "--decision", "revoke", "--note", "Interpretation withdrawn.")[0], 0)
        self.assertEqual(command("review", "--id", identifier, "--decision", "retain", "--note", "Try to reactivate.")[0], 1)
        self.assertEqual(self.reason(), "revoked")


if __name__ == "__main__":
    unittest.main(verbosity=2)
