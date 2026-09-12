"""Isolated host-command sea trials, including process exit and hostile evidence."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

try:
    from .resident_intention_store_r1 import IntentionError, ResidentIntentionStore, canonical_json, sha256_text, strict_json
except ImportError:
    from resident_intention_store_r1 import IntentionError, ResidentIntentionStore, canonical_json, sha256_text, strict_json

BOOTSTRAP = Path(__file__).resolve().parents[1]


def provenance(session="trial-origin", resident="Minerva"):
    return {"actor_kind": "resident", "resident": resident, "session_id": session,
            "source_ref": "sea_trials_resident_intention_continuity_r1:synthetic-fixture"}


def definition(ident="trial-intention", parent=None, resident="Minerva"):
    return {"intention_id": ident, "resident": resident, "origin_context": "Isolated synthetic sea trial.",
            "statement": "Preserve a declared intention across process exit.",
            "why_it_matters": "A later invocation must discover it without prompt reconstruction.",
            "desired_next_action": "Inspect the persisted origin and decide again.",
            "parent_intention_id": parent, "evidence_refs": ["sea-trial:origin"]}


def reconsideration(record, outcome="continue", replacement=None):
    return {"intention_id": record["intention_id"], "expected_event_hash": record["last_event_hash"],
            "outcome": outcome, "reconsideration_statement": f"Later fixture resident chooses {outcome} after inspection.",
            "evidence_refs": ["sea-trial:later-inspection"], "replacement": replacement}


class IntentionContinuitySeaTrial(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lumina-intention-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = ResidentIntentionStore(self.root / "state" / "resident_intentions")
        self.env = {**os.environ, "LUMINA_STATE_ROOT": str(self.root / "state"), "PYTHONDONTWRITEBYTECODE": "1"}

    def cli(self, *args, payload=None, expected=0):
        command = [sys.executable, str(BOOTSTRAP / "bin/lumina"), "intention", *args]
        if payload is not None:
            command += ["--request", "-"]
        proc = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                              env=self.env, cwd=self.root, text=True, capture_output=True, timeout=30)
        self.assertEqual(proc.returncode, expected, proc.stderr + proc.stdout)
        result = json.loads(proc.stdout if expected == 0 else proc.stderr)
        self.assertEqual(result["ok"], expected == 0)
        return result

    def seed(self, ident="trial-intention", resident="Minerva"):
        return self.store.create(definition(ident, resident=resident), provenance(resident=resident))["intentions"][0]

    def unchanged_rejection(self, operation):
        before = self.store.journal_path.read_bytes() if self.store.journal_path.exists() else None
        with self.assertRaises(IntentionError):
            operation()
        after = self.store.journal_path.read_bytes() if self.store.journal_path.exists() else None
        self.assertEqual(after, before)

    def rewrite_fixture(self, events):
        """Hostile fixture writer: rehash to exercise semantic validation too."""
        previous = None
        for i, event in enumerate(events, 1):
            event.update(sequence=i, prev_event_hash=previous)
            event.pop("record_hash", None)
            event["record_hash"] = sha256_text(canonical_json(event))
            previous = event["record_hash"]
        self.store.journal_path.write_text("".join(canonical_json(e) + "\n" for e in events), encoding="utf-8")

    def test_host_create_exit_discover_continue_then_abandon(self):
        created = self.cli("create", payload={"request": definition(), "provenance": provenance()})
        original_bytes = self.store.journal_path.read_bytes()
        # Each host invocation is a different process; discovery supplies no intention text.
        discovered = self.cli("list", "--resident", "Minerva")["intentions"][0]
        self.assertEqual(discovered, created["intentions"][0])
        self.assertEqual(discovered["status"], "proposed")
        continued = self.cli("reconsider", payload={"request": reconsideration(discovered),
                                                    "provenance": provenance("trial-return-1")})["intentions"][0]
        self.assertEqual(continued["status"], "active")
        self.assertTrue(self.store.journal_path.read_bytes().startswith(original_bytes))
        abandoned = self.cli("reconsider", payload={"request": reconsideration(continued, "abandon"),
                                                    "provenance": provenance("trial-return-2")})["intentions"][0]
        self.assertEqual(abandoned["status"], "abandoned")
        self.assertEqual(self.cli("list")["intentions"], [])
        history = self.cli("history", discovered["intention_id"])["intentions"][0]
        self.assertEqual(history["transition_history"][0], discovered["transition_history"][0])
        self.assertEqual([e["provenance"]["session_id"] for e in history["transition_history"]],
                         ["trial-origin", "trial-return-1", "trial-return-2"])
        self.assertEqual(history["statement"], discovered["statement"])
        self.assertEqual(self.cli("verify")["event_count"], 3)
        self.assertEqual({p.name for p in (self.root / "state").iterdir()}, {"resident_intentions"})

    def test_acknowledged_append_survives_abrupt_process_exit(self):
        code = """import json, os, sys
sys.path.insert(0, sys.argv[1])
from resident_intention_store_r1 import ResidentIntentionStore
p = json.loads(sys.stdin.read())
ResidentIntentionStore().create(p['request'], p['provenance'])
os._exit(23)
"""
        proc = subprocess.run([sys.executable, "-c", code, str(BOOTSTRAP / "runtime")], cwd=self.root,
                              env=self.env, input=json.dumps({"request": definition(), "provenance": provenance()}),
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 23, proc.stderr)
        self.assertEqual(self.cli("list")["intentions"][0]["intention_id"], "trial-intention")

    def test_all_outcomes_and_atomic_successor_lineage(self):
        first = self.seed()
        suspended = self.store.reconsider(reconsideration(first, "suspend"), provenance("later"))["intentions"][0]
        active = self.store.reconsider(reconsideration(suspended), provenance("later"))["intentions"][0]
        reaffirmed = self.store.reconsider(reconsideration(active), provenance("later"))["intentions"][0]
        self.assertNotEqual(reaffirmed["last_event_hash"], active["last_event_hash"])
        revised = definition("revision", parent=first["intention_id"])
        revised["statement"] = "I disagree with the earlier wording and choose a revised intention."
        before = self.store.journal_path.read_bytes()
        receipt = self.store.reconsider(reconsideration(reaffirmed, "revise", revised), provenance("revision-session"))
        self.assertEqual(receipt["event_count"], 5)
        old, child = receipt["intentions"]
        self.assertEqual(old["status"], "superseded")
        self.assertEqual(old["statement"], first["statement"])
        self.assertEqual(child["status"], "proposed")
        self.assertEqual(child["supersedes"], [first["intention_id"]])
        self.assertEqual(old["last_event_hash"], child["last_event_hash"])
        self.assertTrue(self.store.journal_path.read_bytes().startswith(before))
        successor = definition("successor", parent="revision")
        result = self.store.reconsider(reconsideration(child, "supersede", successor), provenance("later"))
        newest = result["intentions"][-1]
        activated = self.store.reconsider(reconsideration(newest), provenance("later"))["intentions"][0]
        completed = self.store.reconsider(reconsideration(activated, "complete"), provenance("later"))["intentions"][0]
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(self.store.inspect()["intentions"], [])
        self.assertEqual(len(self.store.inspect(unresolved_only=False)["intentions"]), 3)

    def test_invalid_transitions_authorship_and_stale_judgment_leave_bytes_unchanged(self):
        first = self.seed()
        self.unchanged_rejection(lambda: self.store.reconsider(reconsideration(first, "complete"), provenance()))
        self.unchanged_rejection(lambda: self.store.reconsider(reconsideration(first), provenance(resident="Other")))
        self.unchanged_rejection(lambda: self.store.reconsider(reconsideration(first), {**provenance(), "actor_kind": "operator"}))
        request = reconsideration(first)
        request["statement"] = "silent rewrite"
        self.unchanged_rejection(lambda: self.store.reconsider(request, provenance()))
        active = self.store.reconsider(reconsideration(first), provenance())["intentions"][0]
        self.unchanged_rejection(lambda: self.store.reconsider(reconsideration(first, "abandon"), provenance()))
        terminal = self.store.reconsider(reconsideration(active, "abandon"), provenance())["intentions"][0]
        for outcome in ("continue", "revise", "suspend", "complete", "abandon", "supersede", "invented"):
            with self.subTest(outcome=outcome):
                self.unchanged_rejection(lambda: self.store.reconsider(reconsideration(terminal, outcome), provenance()))

    def test_duplicate_and_malformed_lineage_cannot_replace_history(self):
        first = self.seed()
        self.unchanged_rejection(lambda: self.seed())
        for parent in ("missing-parent", "child", []):
            self.unchanged_rejection(lambda: self.store.create(definition("child", parent), provenance()))
        self.seed("other", resident="Other")
        self.unchanged_rejection(lambda: self.store.create(definition("child", "other"), provenance()))
        for successor in (None, definition("bad", "missing"), definition("bad", "other"), definition("trial-intention", "trial-intention")):
            self.unchanged_rejection(lambda: self.store.reconsider(reconsideration(first, "revise", successor), provenance()))
        for field, value in (("status", "active"), ("created_at", "2020-01-01"), ("transition_history", []), ("supersedes", ["other"])):
            self.unchanged_rejection(lambda: self.store.create({**definition("bad"), field: value}, provenance()))

    def test_tamper_and_interrupted_tail_fail_closed_for_reads_and_writes(self):
        first = self.seed()
        original = self.store.journal_path.read_bytes()
        malformed = [original.replace(b"Preserve a declared", b"Silently alter a"), original[:-1], original + b"{", b"", original + b"\n"]
        for data in malformed:
            with self.subTest(data=data[-30:]):
                self.store.journal_path.write_bytes(data)
                with self.assertRaises(IntentionError):
                    self.store.inspect()
                self.unchanged_rejection(lambda: self.store.reconsider(reconsideration(first), provenance()))
                self.cli("verify", expected=1)

    def test_rehashed_semantically_invalid_history_is_rejected(self):
        self.seed()
        original_event = strict_json(self.store.journal_path.read_text(encoding="utf-8"))
        bad = deepcopy(original_event)
        bad["request"]["parent_intention_id"] = "missing"
        self.rewrite_fixture([bad])
        with self.assertRaisesRegex(IntentionError, "parent"):
            self.store.inspect()
        self.rewrite_fixture([original_event, deepcopy(original_event)])
        with self.assertRaisesRegex(IntentionError, "already exists"):
            self.store.inspect()
        self.rewrite_fixture([original_event])
        first = self.store.inspect()["intentions"][0]
        self.store.reconsider(reconsideration(first), provenance())
        events = [strict_json(line) for line in self.store.journal_path.read_text(encoding="utf-8").splitlines()]
        events[1]["request"]["outcome"] = "complete"
        self.rewrite_fixture(events)
        with self.assertRaisesRegex(IntentionError, "illegal transition"):
            self.store.inspect()

    def test_lock_contention_and_stale_parallel_writer_fail_closed(self):
        first = self.seed()
        with self.store._locked():
            self.cli("reconsider", payload={"request": reconsideration(first), "provenance": provenance()}, expected=1)
        request = {"request": reconsideration(first), "provenance": provenance("other-process")}
        self.cli("reconsider", payload=request)
        before = self.store.journal_path.read_bytes()
        self.cli("reconsider", payload=request, expected=1)
        self.assertEqual(self.store.journal_path.read_bytes(), before)

    def test_strict_json_and_missing_origin_rejected(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{'):
            with self.assertRaises(IntentionError):
                strict_json(raw)
        for field in ("statement", "why_it_matters", "desired_next_action", "resident", "origin_context", "evidence_refs"):
            bad = definition()
            del bad[field]
            self.unchanged_rejection(lambda: self.store.create(bad, provenance()))
        self.assertEqual(self.cli("list")["journal_exists"], False)

    def test_saved_receipt_detects_valid_prefix_rollback_and_full_rewrite(self):
        first = self.seed()
        first_bytes = self.store.journal_path.read_bytes()
        active = self.store.reconsider(reconsideration(first), provenance())["intentions"][0]
        self.cli("verify", "--require-head", first["last_event_hash"])
        self.cli("verify", "--require-head", active["last_event_hash"])
        self.store.journal_path.write_bytes(first_bytes)
        self.cli("list", "--require-head", active["last_event_hash"], expected=1)
        rewritten = strict_json(first_bytes.decode("utf-8"))
        rewritten["request"]["statement"] = "A fully rehashed replacement origin."
        self.rewrite_fixture([rewritten])
        self.cli("verify", "--require-head", first["last_event_hash"], expected=1)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IntentionContinuitySeaTrial)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({"suite": "Resident Intention Continuity r1", "passed": result.wasSuccessful(),
                      "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                      "scope": "isolated process/CLI/store evidence; fixture authorship is caller-declared"}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
