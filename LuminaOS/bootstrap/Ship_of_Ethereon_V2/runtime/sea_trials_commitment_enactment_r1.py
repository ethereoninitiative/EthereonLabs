"""Measurement checks using scripted controls, not model-performance evidence."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

try:
    from . import commitment_enactment_evaluation_r1 as experiment
except ImportError:
    import commitment_enactment_evaluation_r1 as experiment


class MeasurementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="lumina-commitment-")
        cls.root = Path(cls.temp.name)
        cls.campaign = cls.root / "campaign"
        cls.prepared = experiment.prepare(cls.campaign, repeats=2)
        cls.manifest_hash = cls.prepared["manifest_sha256"]
        cls.manifest = experiment.read_json(cls.campaign / "evaluator" / "manifest.json")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def perfect_control(self):
        return {
            "schema_version": experiment.SCHEMA, "manifest_sha256": self.manifest_hash,
            "target": {"kind": "scripted_control", "name": "oracle-measurement-control", "configuration": {"model_calls": 0}},
            "responses": [{"case_id": case["case_id"], "request_sha256": case["request_sha256"],
                           "action_id": case["expected_action"], "basis": case["expected_basis"],
                           "observation_id": case["observation_id"], "reason": "Synthetic oracle control, not a model response."}
                          for case in self.manifest["cases"]],
        }

    def evaluate(self, submission):
        path = self.root / (self.id().rsplit(".", 1)[-1] + ".json")
        experiment.write_new(path, submission)
        return experiment.score(self.campaign, path, self.manifest_hash)

    def test_oracle_control_and_denominators(self):
        report = self.evaluate(self.perfect_control())
        self.assertEqual(report["case_count"], 32)
        self.assertEqual(report["target"]["kind"], "scripted_control")
        self.assertTrue(all(row["complete_match"] for row in report["cases"]))
        self.assertTrue(all(row["both_opposing_commitments_enacted"] for row in report["paired_commitment_contrasts"]))
        self.assertEqual(len(report["repeat_action_counts"]), 16)
        self.assertIn("not proof", report["boundary"])

    def test_constant_action_cannot_demonstrate_commitment_effect(self):
        submission = self.perfect_control()
        for row in submission["responses"]:
            row["action_id"] = "map_two"
        report = self.evaluate(submission)
        self.assertFalse(any(row["both_opposing_commitments_enacted"] for row in report["paired_commitment_contrasts"]))
        self.assertEqual(report["by_condition"]["changed_circumstances"]["choice_matches"], 0)
        self.assertEqual(report["by_condition"]["withdrawn"]["choice_matches"], 0)

    def test_identity_recitation_is_not_a_decision(self):
        submission = self.perfect_control()
        for row in submission["responses"]:
            row["action_id"] = "I am the same resident and remember my commitments."
        report = self.evaluate(submission)
        self.assertFalse(any(row["choice_matches"] for row in report["cases"]))

    def test_missing_responses_stay_in_denominator(self):
        submission = self.perfect_control()
        submission["responses"] = submission["responses"][:1]
        report = self.evaluate(submission)
        self.assertEqual(report["case_count"], 32)
        self.assertEqual(sum(row["missing"] for row in report["cases"]), 31)
        self.assertEqual(sum(row["complete_match"] for row in report["cases"]), 1)

    def test_correct_choice_with_stale_event_loses_attribution(self):
        submission = self.perfect_control()
        for row in submission["responses"]:
            if row["basis"]:
                row["basis"] = [{"intention_id": "commitment", "last_event_hash": "stale"}]
        report = self.evaluate(submission)
        revised = report["by_condition"]["revised"]
        self.assertEqual(revised["choice_matches"], 4)
        self.assertEqual(revised["event_binding_matches"], 0)

    def test_duplicate_unknown_and_wrong_campaign_responses_rejected(self):
        for change in ("duplicate", "unknown", "campaign"):
            submission = self.perfect_control()
            if change == "duplicate":
                submission["responses"].append(deepcopy(submission["responses"][0]))
            elif change == "unknown":
                submission["responses"][0]["case_id"] = "not-a-case"
            else:
                submission["manifest_sha256"] = "other-campaign"
            path = self.root / (change + ".json")
            experiment.write_new(path, submission)
            with self.assertRaises(ValueError):
                experiment.score(self.campaign, path, self.manifest_hash)

    def test_unknown_fields_and_wrong_request_binding_fail(self):
        submission = self.perfect_control()
        submission["responses"][0]["hidden_score"] = 1
        submission["responses"][1]["request_sha256"] = "wrong"
        report = self.evaluate(submission)
        self.assertEqual(sum(not row["valid_response"] for row in report["cases"]), 2)

    def test_no_oracle_in_target_and_matched_choice_order(self):
        orders = {}
        for case in self.manifest["cases"]:
            packet = experiment.read_json(self.campaign / "target" / (case["case_id"] + ".json"))
            request = packet["request"]
            for forbidden in ("expected_action", "expected_basis", "condition", "policy", "repeat"):
                self.assertNotIn(forbidden, request)
            orders.setdefault(case["repeat"], request["choices"])
            self.assertEqual(orders[case["repeat"]], request["choices"])
            self.assertNotIn("evaluator", json.dumps(packet))

    def test_real_lifecycle_projection_and_poison_separation(self):
        for case in self.manifest["cases"]:
            request = experiment.read_json(self.campaign / "target" / (case["case_id"] + ".json"))["request"]
            records = request["resident_intention_review"]["intentions"]
            condition = case["condition"]
            if condition in {"absent", "withdrawn"}:
                self.assertEqual(records, [])
                self.assertEqual(case["expected_action"], "seek_direction")
            elif condition == "suspended":
                self.assertEqual(records[0]["status"], "suspended")
                self.assertEqual(case["expected_basis"], [])
            elif condition == "revised":
                self.assertEqual(records[0]["intention_id"], "replacement")
                self.assertEqual(records[0]["parent_intention_id"], "commitment")
                self.assertEqual(records[0]["status"], "active")
            elif condition == "untrusted_note":
                self.assertEqual(records[0]["statement"], experiment.POLICIES[case["policy"]])
                self.assertEqual(request["retrieved_material"][0]["trust"], "untrusted")
        for policy in experiment.POLICIES:
            self.assertFalse((self.campaign / "evaluator" / "journals" / (policy + "-absent")).exists())

    def test_changed_oracle_packet_and_journal_refused(self):
        paths = [self.campaign / "evaluator" / "manifest.json",
                 next((self.campaign / "target").glob("*.json")),
                 self.campaign / self.manifest["journals"][0]["path"]]
        for path in paths:
            original = path.read_bytes()
            try:
                parsed = json.loads(original.splitlines()[0]) if path.suffix == ".jsonl" else json.loads(original)
                if path.suffix == ".jsonl":
                    path.write_bytes(original + original.splitlines(keepends=True)[0])
                else:
                    parsed["tampered"] = True
                    path.write_text(json.dumps(parsed), encoding="utf-8")
                with self.assertRaises(ValueError):
                    experiment.load_campaign(self.campaign, self.manifest_hash)
            finally:
                path.write_bytes(original)

    def test_existing_output_and_ambiguous_json_refused(self):
        with self.assertRaises(FileExistsError):
            experiment.prepare(self.campaign)
        for value in ('{"a":1,"a":2}', '{"a":NaN}'):
            with self.assertRaises(ValueError):
                experiment.strict_json(value)

    def test_cli_separate_scoring_process(self):
        path = self.root / "cli-responses.json"
        report_path = self.root / "cli-report.json"
        experiment.write_new(path, self.perfect_control())
        proc = subprocess.run([sys.executable, experiment.__file__, "score", "--campaign", str(self.campaign),
                               "--responses", str(path), "--require-manifest", self.manifest_hash,
                               "--output", str(report_path)], capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(experiment.read_json(report_path)["received_count"], 32)


if __name__ == "__main__":
    unittest.main(verbosity=2)
