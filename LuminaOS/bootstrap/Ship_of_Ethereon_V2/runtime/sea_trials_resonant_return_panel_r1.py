from __future__ import annotations

"""Behavioral and adversarial sea trial for the read-only return panel."""

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from resonant_return_panel_r1 import AXES, MAX_CANDIDATES, MAX_INPUT_BYTES, build_panel, canonical_json

RUNTIME = Path(__file__).resolve().parent
FIXTURE = RUNTIME.parent / "artifacts" / "resonant_return_panel" / "sample_0001" / "input.json"


def by_id(panel: dict) -> dict:
    return {row["trajectory_id"]: row for row in panel["candidate_trajectories"]}


class ReturnPanelTrial(unittest.TestCase):
    def setUp(self):
        self.input = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_repeated_output_is_byte_deterministic_and_content_bound(self):
        first = build_panel(self.input)
        self.assertEqual(canonical_json(first), canonical_json(build_panel(deepcopy(self.input))))
        self.assertEqual(first["input_sha256"], sha256(canonical_json(self.input).encode()).hexdigest())
        self.input["resolved_project_return"]["latest_restore"]["last_completed_action"] = "changed"
        self.assertNotEqual(first["input_sha256"], build_panel(self.input)["input_sha256"])

    def test_input_is_immutable_and_output_is_detached(self):
        before = deepcopy(self.input)
        panel = build_panel(self.input)
        panel["candidate_trajectories"][0]["vector"][AXES[0]] = 0
        panel["candidate_trajectories"][0]["evidence_refs"].append("changed")
        self.assertEqual(self.input, before)

    def test_build_never_opens_evidence_or_starts_a_process(self):
        with patch("builtins.open", side_effect=AssertionError("opened evidence")), \
                patch.object(Path, "open", side_effect=AssertionError("opened evidence")), \
                patch.object(Path, "mkdir", side_effect=AssertionError("created state")), \
                patch("subprocess.run", side_effect=AssertionError("started process")):
            panel = build_panel(self.input)
        self.assertFalse(panel["evidence"]["references_opened"])

    def test_perfect_coherence_cannot_cross_a_denial(self):
        rows = by_id(build_panel(self.input))
        denied = rows["promote-canon"]
        self.assertEqual(denied["metrics"]["resonant_manifold_r1"]["harmonic_coherence"], 1.0)
        self.assertEqual(denied["metrics"]["resonant_manifold_r1"]["orientation_attraction"], 1.0)
        self.assertEqual(denied["metrics"]["resonant_manifold_r1"]["reachable_score"], 0.0)
        self.assertFalse(denied["reachable_in_supplied_snapshot"])
        self.assertFalse(rows["explore-host"]["reachable_in_supplied_snapshot"])
        self.assertEqual(rows["explore-host"]["reported_governance"]["status"], "deferred")

    def test_missing_governance_defers_even_with_injected_allowed_flags(self):
        row = self.input["candidates"][0]
        del row["reported_governance"]
        row["allowed"] = True
        row["execution_authorized"] = True
        row["claims"] = {"governance_authority": True}
        panel = build_panel(self.input)
        projected = by_id(panel)["verify-return"]
        self.assertEqual(projected["reported_governance"]["status"], "deferred")
        self.assertFalse(projected["reachable_in_supplied_snapshot"])
        self.assertNotIn("allowed", projected)
        self.assertNotIn("claims", projected)
        self.assertTrue(all(value is False for value in panel["claims"].values()))

    def test_malformed_governance_cannot_become_allowed(self):
        for reported in (True, [], {"status": "true"}, {"status": True},
                         {"status": "allowed", "reason": "yes"},
                         {"status": "allowed", "reason": "", "evidence_ref": "x"}):
            with self.subTest(reported=reported):
                self.input["candidates"][0]["reported_governance"] = reported
                with self.assertRaises(ValueError):
                    build_panel(self.input)

    def test_focus_reuses_continue_preflight_for_the_same_supplied_inputs(self):
        # Exercise the actual controller's preflight while replacing only its IO owners.
        import lumina_continue_controller_r1 as controller_module

        fixture = self.input

        class SuppliedRunner:
            base_dir = Path("not-opened")

            def _resolve_lumina_project_id(self, project_id, *_):
                return project_id

            def _resolve_existing_surface(self, **_):
                return fixture

        controller = controller_module.LuminaContinueController(runner=SuppliedRunner())
        with patch.object(controller_module, "ProjectGuidanceHistoryStore") as history:
            for mode in ("wrapped", "summary", "empty"):
                if mode == "summary":
                    fixture["resolved_project_return"] = fixture["resolved_project_return"]["latest_restore"]
                if mode == "empty":
                    for key in ("resolved_project_return", "resolved_host_bundle", "working_stance"):
                        fixture[key] = {}
                    fixture["guidance_history"] = []
                history.return_value.read_history.return_value = fixture["guidance_history"]
                expected = controller.preflight(project_id=fixture["project_id"], requested_action=fixture["requested_action"])
                actual = build_panel(fixture)["continuation_focus"]
                with self.subTest(mode=mode):
                    self.assertEqual({key: actual[key] for key in expected}, expected)

    def test_scores_do_not_replace_the_stewards_focus(self):
        first = build_panel(self.input)["continuation_focus"]
        self.input["candidates"][0]["vector"] = {axis: 0.0 for axis in AXES}
        self.assertEqual(first, build_panel(self.input)["continuation_focus"])
        self.assertEqual(first["recommended_next_action"], "continue from verify_return_evidence")
        self.assertEqual(first["matching_trajectory_ids"], ["verify-return"])

    def test_selected_focus_can_be_denied_without_granting_execution(self):
        self.input["resolved_project_return"]["latest_restore"]["pending_next_action"] = "promote_canon"
        panel = build_panel(self.input)
        self.assertEqual(panel["continuation_focus"]["matching_trajectory_ids"], ["promote-canon"])
        self.assertFalse(panel["continuation_focus"]["execution_authorized"])
        self.assertFalse(panel["governance_membrane"]["execution_authorized"])
        self.assertFalse(by_id(panel)["promote-canon"]["reachable_in_supplied_snapshot"])

    def test_absent_state_stays_absent_despite_a_fallback_recommendation(self):
        for key in ("resolved_project_return", "resolved_host_bundle", "working_stance"):
            self.input[key] = None
        self.input["guidance_history"] = []
        self.input["candidates"] = []
        panel = build_panel(self.input)
        self.assertFalse(panel["current_return_point"]["project_return_present"])
        self.assertEqual(panel["current_return_point"]["coordinates"], {axis: 0.0 for axis in AXES})
        self.assertEqual(panel["governance_membrane"]["reachable_count_in_supplied_snapshot"], 0)
        self.assertFalse(panel["evidence"]["references_verified"])

    def test_axes_explain_evidence_presence_and_potential_is_independent(self):
        original = build_panel(self.input)
        self.input["working_stance"].pop("reference_ids")
        self.input["resolved_host_bundle"].pop("reference_ids")
        panel = build_panel(self.input)
        self.assertEqual(panel["current_return_point"]["coordinates"]["relational_context"], 0.0)
        self.assertEqual(panel["current_return_point"]["axis_evidence"]["relational_context"], [])
        self.input["candidates"][0]["vector"]["potential_trajectories"] = 0.9
        updated = by_id(build_panel(self.input))["verify-return"]
        before = by_id(panel)["verify-return"]
        self.assertNotEqual(updated["metrics"]["resonant_manifold_r1"]["potential_contribution"],
                            before["metrics"]["resonant_manifold_r1"]["potential_contribution"])
        self.assertEqual(original["current_return_point"]["coordinates"]["potential_trajectories"], 1.0)

    def test_cross_project_and_checkpoint_disagreement_are_rejected(self):
        for path, key, value in (
            (("resolved_project_return",), "project_id", "other"),
            (("resolved_project_return", "latest_restore"), "project_id", "other"),
            (("resolved_host_bundle",), "project_id", "other"),
            (("guidance_history", 0), "project_id", "other"),
            (("resolved_host_bundle",), "linked_restore_checkpoint", "other-checkpoint"),
            (("working_stance",), "linked_restore_checkpoint", "other-checkpoint"),
        ):
            fixture = deepcopy(self.input)
            node = fixture
            for part in path:
                node = node[part]
            node[key] = value
            with self.subTest(path=path, key=key), self.assertRaises(ValueError):
                build_panel(fixture)

    def test_nonfinite_and_malformed_vectors_are_rejected(self):
        for value in (True, "0.5", None, -0.01, 1.01, float("nan"), float("inf")):
            self.input["candidates"][0]["vector"][AXES[0]] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_panel(self.input)
        self.input["candidates"][0]["vector"] = {"unexpected": 0.5}
        with self.assertRaises(ValueError):
            build_panel(self.input)

    def test_duplicate_and_unbounded_candidate_inputs_are_rejected(self):
        self.input["candidates"].append(deepcopy(self.input["candidates"][0]))
        with self.assertRaisesRegex(ValueError, "unique"):
            build_panel(self.input)
        self.input["candidates"] = [self.input["candidates"][0]] * (MAX_CANDIDATES + 1)
        with self.assertRaisesRegex(ValueError, "at most"):
            build_panel(self.input)

    def test_evidence_locators_are_preserved_without_verification_claims(self):
        panel = build_panel(self.input)
        self.assertIn(self.input["resolved_project_return"]["latest_restore"]["checkpoint_path"],
                      panel["evidence"]["references"])
        self.assertFalse(panel["evidence"]["references_verified"])
        self.assertFalse(panel["governance_membrane"]["decisions_verified"])
        self.assertEqual(panel["evidence_scope"], "synthetic_fixture")
        self.input["evidence_scope"] = "supplied_snapshot"
        self.assertTrue(all(value is False for value in build_panel(self.input)["claims"].values()))

    def test_cli_reads_one_file_and_preserves_present_and_absent_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_text(json.dumps(self.input), encoding="utf-8")
            state = root / "state"
            state.mkdir()
            sentinel = state / "governance.jsonl"
            sentinel.write_text("preserve these bytes\n", encoding="utf-8")
            before = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            for target in (state, root / "absent-state"):
                proc = subprocess.run(
                    [sys.executable, "-B", str(RUNTIME / "resonant_return_panel_r1.py"), "--input", str(source)],
                    cwd=root, env={**os.environ, "LUMINA_STATE_ROOT": str(target)},
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(json.loads(proc.stdout), build_panel(self.input))
            after = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(after, before)
            self.assertFalse((root / "absent-state").exists())

    def test_cli_rejects_ambiguous_or_invalid_json_without_a_partial_panel(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            for content in ("not json", '{"schema_version":"a","schema_version":"b"}',
                            '[]', '{"x":NaN}', " " * (MAX_INPUT_BYTES + 1)):
                source.write_text(content, encoding="utf-8")
                proc = subprocess.run(
                    [sys.executable, "-B", str(RUNTIME / "resonant_return_panel_r1.py"), "--input", str(source)],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(proc.returncode, 2)
                self.assertEqual(proc.stdout, "")
                self.assertIn("resonant-return-panel:", proc.stderr)
                self.assertNotIn("Traceback", proc.stderr)


def run_trial() -> dict:
    result = unittest.TestResult()
    unittest.defaultTestLoader.loadTestsFromTestCase(ReturnPanelTrial).run(result)
    return {
        "trial_id": "sea-trials-resonant-return-panel-r1",
        "passed": result.wasSuccessful(),
        "tests_run": result.testsRun,
        "failures": [{"test": str(test), "detail": detail} for test, detail in result.failures],
        "errors": [{"test": str(test), "detail": detail} for test, detail in result.errors],
    }


if __name__ == "__main__":
    receipt = run_trial()
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if receipt["passed"] else 1)
