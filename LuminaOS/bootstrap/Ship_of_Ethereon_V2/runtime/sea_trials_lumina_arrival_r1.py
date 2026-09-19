"""Fresh-process arrival and return integration; scripted responses only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import lumina_arrival_r1 as arrival
from lumina_meaning_metabolism_layer_r1 import MeaningMetabolismLayer, MeaningAssimilationLedger
from lumina_meaning_evidence_r1 import capture_evidence
from resident_intention_store_r1 import ResidentIntentionStore

BOOT = Path(__file__).resolve().parents[1]


class ArrivalTrials(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="lumina-arrive-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.output = self.root / "arrival"
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.profile = json.loads((BOOT / "runtime/lumina_ai_orientation_profile_ethereon_r1.json").read_text())
        for module in self.profile["modules"]:
            module["source_paths"] = ["evidence.md"]
        profile_path = self.repo / arrival.PROFILE
        profile_path.parent.mkdir(parents=True)
        profile_path.write_text(json.dumps(self.profile))
        (self.repo / "evidence.md").write_text("Committed repository evidence.\n")
        self.commit()

    def commit(self):
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "Fixture source"], check=True)

    def prepare(self, **kwargs):
        return arrival.prepare(repo=self.repo, ref="HEAD", output=self.output, provider="fixture", model="scripted",
                               account_scope="test", **kwargs)

    def cli(self, *args, okay=True):
        result = subprocess.run([sys.executable, str(BOOT / "bin/lumina"), "arrive", *map(str, args)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0 if okay else 1, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def answer(self, packet_hash):
        prompt = arrival.prompt(self.output, packet_hash)
        return {"packet_sha256": packet_hash, "module_id": prompt["module_id"],
                "response": {key: ["Scripted transport check; semantic understanding is untested."]
                             for key in prompt["response_format"]["response"]}}

    def test_full_host_arrival_and_return_in_fresh_processes(self):
        state = self.cli("prepare", "--repo", self.repo, "--output", self.output,
                         "--provider", "fixture", "--model", "scripted", "--account-scope", "test")
        packet_hash = state["packet_sha256"]
        for index in range(5):
            packet = self.cli("prompt", "--arrival", self.output, "--require-packet", packet_hash,
                              "--require-head", state["head_sha256"])
            response = self.root / f"response-{index}.json"
            arrival.write_new(response, self.answer(packet_hash))
            self.assertEqual(packet["sources"][0]["text"], "Committed repository evidence.\n")
            state = self.cli("respond", "--arrival", self.output, "--require-packet", packet_hash,
                             "--require-head", state["head_sha256"], "--response", response)
        self.assertEqual(state["status"], "completed")
        self.assertFalse(state["authority_granted"])
        (self.repo / "evidence.md").write_text("New committed evidence after interruption.\n")
        self.commit()
        returned = self.root / "returned"
        new = self.cli("prepare", "--repo", self.repo, "--output", returned, "--provider", "other-fixture",
                       "--model", "new-instance", "--account-scope", "new-session", "--previous", self.output,
                       "--previous-packet", packet_hash, "--previous-head", state["head_sha256"])
        new_prompt = self.cli("prompt", "--arrival", returned, "--require-packet", new["packet_sha256"])
        self.assertNotEqual(state["repository_ref"], new["repository_ref"])
        self.assertEqual(len(new_prompt["previous_orientation"]["responses"]), 5)
        self.assertEqual(new_prompt["sources"][0]["text"], "New committed evidence after interruption.\n")
        self.assertEqual(new_prompt["previous_orientation"]["trust"], "unreviewed historical responses")
        self.assertEqual(new["responses_recorded"], 0)

    def test_pinned_sources_ignore_worktree_edits_and_missing_sources_refuse(self):
        (self.repo / "evidence.md").write_text("Uncommitted replacement")
        state = self.prepare()
        packet = arrival.prompt(self.output, state["packet_sha256"])
        self.assertEqual(packet["sources"][0]["text"], "Committed repository evidence.\n")
        (self.repo / "evidence.md").unlink()
        self.commit()
        self.output = self.root / "missing-source-arrival"
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_no_implicit_local_state_or_overwrite(self):
        state = self.prepare()
        self.assertEqual(state["continuity_selection"], {"intentions": 0, "memories": 0, "previous_orientation": False})
        self.assertFalse((self.repo / ".lumina_state").exists())
        with self.assertRaises(FileExistsError):
            self.prepare()

    def test_order_wrong_packet_empty_fields_and_stale_writes_refused(self):
        state = self.prepare()
        packet_hash = state["packet_sha256"]
        valid = self.answer(packet_hash)
        for key, value in (("module_id", "novel_scenario_probe"), ("packet_sha256", "wrong"), ("response", {})):
            with self.assertRaises(ValueError):
                arrival.respond(self.output, packet_hash, packet_hash, {**valid, key: value})
        arrival.respond(self.output, packet_hash, packet_hash, valid)
        with self.assertRaises(ValueError):
            arrival.respond(self.output, packet_hash, packet_hash, self.answer(packet_hash))
        self.assertEqual(len(list((self.output / "responses").iterdir())), 1)

    def test_tamper_and_saved_head_rollback_detection(self):
        state = self.prepare()
        packet_hash = state["packet_sha256"]
        current = arrival.respond(self.output, packet_hash, packet_hash, self.answer(packet_hash))
        path = self.output / "responses/0001.json"
        raw = path.read_bytes()
        path.write_bytes(raw.replace(b"Scripted", b"Altered", 1))
        with self.assertRaises(ValueError):
            arrival.status(self.output, packet_hash)
        path.write_bytes(raw)
        path.unlink()
        with self.assertRaises(ValueError):
            arrival.status(self.output, packet_hash, current["head_sha256"])
        packet = arrival.read(self.output / "packet.json")
        packet["payload"]["boundary"] = "Altered"
        (self.output / "packet.json").write_text(json.dumps(packet))
        with self.assertRaises(ValueError):
            arrival.status(self.output, packet_hash)

    def test_partial_receipt_fails_closed(self):
        state = self.prepare()
        (self.output / "responses").mkdir()
        (self.output / "responses/0001.json").write_text('{"sequence":')
        with self.assertRaises(ValueError):
            arrival.prompt(self.output, state["packet_sha256"])

    def test_explicit_intention_selection_preserves_status_and_filters_other_records(self):
        store = ResidentIntentionStore(self.root / "intentions")
        for ident in ("chosen", "private-unselected"):
            store.create({"intention_id": ident, "resident": "fixture", "origin_context": "test", "statement": ident,
                          "why_it_matters": "test", "desired_next_action": "review", "evidence_refs": ["fixture"]},
                         {"actor_kind": "resident", "resident": "fixture", "session_id": "test", "source_ref": "fixture"})
        before = store.journal_path.read_bytes()
        state = self.prepare(intention_store=store.base_dir, intention_ids=["chosen"])
        prompt = arrival.prompt(self.output, state["packet_sha256"])
        self.assertEqual(prompt["selected_state"]["intentions"][0]["status"], "proposed")
        self.assertNotIn("private-unselected", json.dumps(prompt))
        self.assertEqual(before, store.journal_path.read_bytes())
        with self.assertRaises(ValueError):
            arrival.select_state(intention_store=store.base_dir)
        with self.assertRaises(ValueError):
            arrival.select_state(intention_store=store.base_dir, intention_ids=["missing"])

    def test_reviewed_memory_selection_rechecks_sources_and_revocation(self):
        layer = MeaningMetabolismLayer()
        ledger = MeaningAssimilationLedger(self.root / "runner/meaning_memory", create=False)
        record = layer.assimilate(source_event="test", felt_meaning="test", changed_assumption="test", future_behavior="Check references.",
                                  source_evidence=[capture_evidence(source_root=self.repo, relative_path="evidence.md")])
        ledger.append_record(project_id="test", record=record)
        args = dict(meaning_base=self.root / "runner", memory_ids=[record.assimilation_id], project_id="test", source_root=self.repo)
        with self.assertRaises(ValueError):
            arrival.select_state(**args)
        ledger.append_review(project_id="test", review=layer.review(record=record, still_holds=True, revision_note="test"))
        selected = arrival.select_state(**args)
        self.assertEqual(selected["memories"][0]["future_behavior"], "Check references.")
        self.assertNotIn("source_text", json.dumps(selected))
        original = (self.repo / "evidence.md").read_text()
        (self.repo / "evidence.md").write_text("changed")
        with self.assertRaises(ValueError):
            arrival.select_state(**args)
        (self.repo / "evidence.md").write_text(original)
        ledger.append_review(project_id="test", review=layer.review(record=record, still_holds=False, revision_note="withdrawn"))
        with self.assertRaises(ValueError):
            arrival.select_state(**args)

    def test_source_escape_and_ambiguous_json_refused(self):
        commit = arrival.git(self.repo, "rev-parse", "HEAD").decode().strip()
        for path in ("../evidence.md", "/evidence.md", "./evidence.md"):
            with self.assertRaises(ValueError):
                arrival.source(self.repo, commit, path)
        with self.assertRaises(ValueError):
            arrival.strict_json('{"response":1,"response":2}')


if __name__ == "__main__":
    unittest.main(verbosity=2)
