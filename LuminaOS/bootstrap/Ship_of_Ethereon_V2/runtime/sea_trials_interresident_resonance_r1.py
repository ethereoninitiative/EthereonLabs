"""Adversarial protocol, persistent exchange, and orientation interoperability trials."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from interresident_resonance_r1 import (
    ExchangeLedger, ResonanceError, canonical, compare, digest, load,
    orientation_projection, render, seal_packet, strict_json, validate_exchange,
)
from interresident_resonance_demo_r1 import SCOPE, demo_packets
from lumina_ai_orientation_protocol_r1 import AIOrientationProtocol, OrientationModule, OrientationProfile

HERE = Path(__file__).resolve().parent
FIXTURE = HERE.parent / "artifacts" / "interresident_resonance" / "fixture_r1" / "exchange.json"


class ResonanceTrials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = demo_packets()

    def setUp(self):
        self.packets = deepcopy(self.fixtures)

    def valid(self, packets=None):
        return validate_exchange(self.packets if packets is None else packets, **SCOPE)

    def reject(self, packet, message=None):
        with self.assertRaises(ResonanceError) as caught:
            self.valid([packet])
        if message:
            self.assertIn(message, str(caught.exception))

    def mutate_seal(self, change, packet=None):
        target = deepcopy(packet or self.packets[0])
        change(target)
        return seal_packet(target)

    def test_three_origins_plus_attributed_synthesis(self):
        receipt = self.valid()
        self.assertEqual(receipt["declared_resident_count"], 3)
        self.assertEqual(receipt["packet_count"], 4)
        self.assertFalse(receipt["authority_granted"])
        self.assertFalse(receipt["identity_authenticated"])
        self.assertEqual(len(self.packets[-1]["parents"]), 3)
        self.assertEqual(len(self.packets[-1]["relations"]), 3)

    def test_agreement_and_minority_disagreement_remain_valid(self):
        report = compare(self.packets, **SCOPE)
        observation = next(a for a in report["alignments"] if a["predicate"] == "samples-count")
        interpretation = next(a for a in report["alignments"] if a["predicate"] == "dominant-cause")
        self.assertEqual(observation["status"], "agreement")
        self.assertEqual(interpretation["status"], "disagreement")
        positions = {p["value"]: p["declarations"] for p in interpretation["positions"]}
        self.assertEqual(len(positions["thermal-drift"]), 2)
        self.assertEqual(len(positions["sensor-noise"]), 1)
        self.assertEqual({e["confidence_bps"] for p in positions.values() for e in p}, {7800, 6200, 5400})
        self.assertTrue(all(e["uncertainties"] for p in positions.values() for e in p))
        self.assertFalse(report["consensus_established"])
        self.assertFalse(report["canon_effect"])

    def test_tampered_semantics(self):
        self.packets[0]["interpretations"][0]["value"] = "changed"
        self.reject(self.packets[0], "hash mismatch")

    def test_tampered_source_and_provenance(self):
        for field in ("source", "resident", "session"):
            packet = deepcopy(self.packets[0])
            if field == "source": packet["source_manifest"][0]["content"]["samples"] = []
            if field == "resident": packet["resident"]["declared_id"] = "impostor"
            if field == "session": packet["provenance"]["session_id"] = "changed"
            with self.subTest(field=field): self.reject(packet, "hash mismatch")

    def test_missing_source_evidence(self):
        for mutation in (lambda p: p["source_manifest"].clear(),
                         lambda p: p["source_manifest"][0].pop("content"),
                         lambda p: p["interpretations"][0]["source_refs"].append("absent")):
            with self.assertRaises(ResonanceError): self.mutate_seal(mutation)

    def test_source_namespace_cannot_silently_change(self):
        changed = deepcopy(self.packets[1])
        source = changed["source_manifest"][0]
        source["content"]["temperature_measured"] = True
        source["content_sha256"] = digest(source["content"])
        changed = seal_packet(changed)
        with self.assertRaisesRegex(ResonanceError, "source binding"):
            self.valid([self.packets[0], changed])

    def test_project_and_encounter_contamination(self):
        for field in ("project_id", "encounter_scope"):
            packet = self.mutate_seal(lambda p: p.update({field: "other"}))
            self.reject(packet, "contamination")

    def test_malformed_confidence(self):
        for value in (True, False, -1, 10001, 0.8, "9000", float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ResonanceError):
                self.mutate_seal(lambda p: p["interpretations"][0].update(confidence_bps=value))
        for value in (None, 0, 10000):
            self.valid([self.mutate_seal(lambda p: p["interpretations"][0].update(confidence_bps=value))])

    def test_unknown_version_and_unknown_fields(self):
        for change in (lambda p: p.update(protocol_version="IRP-R2"),
                       lambda p: p.update(authority_granted=True),
                       lambda p: p["interpretations"][0].update(authenticated=True)):
            with self.assertRaises(ResonanceError): self.mutate_seal(change)

    def test_duplicate_identifiers(self):
        changed = self.mutate_seal(lambda p: p["interpretations"][0].update(value="other"))
        with self.assertRaisesRegex(ResonanceError, "duplicate packet"):
            self.valid([self.packets[0], changed])
        for field in ("source_manifest", "parents", "interpretations", "uncertainties", "relations"):
            with self.subTest(field=field), self.assertRaises(ResonanceError):
                self.mutate_seal(lambda p: p[field].append(deepcopy(p[field][0])), self.packets[-1])

    def test_broken_parent_and_bound_response(self):
        with self.assertRaisesRegex(ResonanceError, "missing predecessor"):
            self.valid([self.packets[-1]])
        changed = deepcopy(self.packets[-1])
        changed["parents"][0]["packet_sha256"] = "0" * 64
        changed["relations"][0]["to"]["packet_sha256"] = "0" * 64
        changed = seal_packet(changed)
        with self.assertRaisesRegex(ResonanceError, "parent content binding"):
            self.valid(self.packets[:-1] + [changed])
        with self.assertRaisesRegex(ResonanceError, "bound parent"):
            self.mutate_seal(lambda p: p.update(responds_to=["missing"]))

    def test_cycle_in_lineage(self):
        left, right = deepcopy(self.packets[:2])
        left["parents"] = [{"packet_id": right["packet_id"], "packet_sha256": right["packet_sha256"]}]
        right["parents"] = [{"packet_id": left["packet_id"], "packet_sha256": left["packet_sha256"]}]
        with self.assertRaisesRegex(ResonanceError, "cycle"):
            self.valid([seal_packet(left), seal_packet(right)])
        with self.assertRaisesRegex(ResonanceError, "cycle"):
            self.mutate_seal(lambda p: p.update(parents=[{"packet_id": p["packet_id"], "packet_sha256": p["packet_sha256"]}]))

    def test_consensus_cannot_grant_authority(self):
        for field, value in (("authority_claim", "consensus"), ("authority_granted", True), ("permission_required", False)):
            with self.assertRaises(ResonanceError):
                self.mutate_seal(lambda p: p["authority"].update({field: value}))
        for value in (0, 1, "false"):
            with self.assertRaises(ResonanceError):
                self.mutate_seal(lambda p: p["authority"].update(authority_granted=value))

    def test_runtime_request_remains_data(self):
        action = {"operation": "runtime.execute", "arguments": {"command": "must-never-run"}}
        packet = self.mutate_seal(lambda p: p["authority"].update(requested_action=action))
        receipt = self.valid([packet])
        self.assertFalse(receipt["authority_granted"])
        self.assertTrue(packet["authority"]["permission_required"])
        with self.assertRaises(ResonanceError):
            self.mutate_seal(lambda p: p["authority"].update(runtime_permission="execute"))

    def test_gloss_is_derivative_but_tamper_evident(self):
        original = self.packets[-1]
        draft = deepcopy(original)
        draft["human_gloss"]["text"] = "Different rendering."
        self.reject(draft, "packet content hash mismatch")
        changed = seal_packet(draft)
        self.assertEqual(original["semantic_sha256"], changed["semantic_sha256"])
        self.assertNotEqual(original["packet_sha256"], changed["packet_sha256"])
        for mutation in (lambda p: p["human_gloss"].update(canonical=True),
                         lambda p: [p[group].clear() for group in ("observations", "interpretations", "uncertainties", "relations")]):
            with self.assertRaises(ResonanceError): self.mutate_seal(mutation, original)
        self.assertIn("DERIVATIVE / LOSSY", render(self.packets, **SCOPE))

    def test_opaque_native_payload_never_universal_or_evidence(self):
        content = {"origin_specific_units": [1, 2, 3]}
        native = {"representation": "opaque", "universally_interpretable": False, "media_type": "application/x-fixture-native", "content": content, "content_sha256": digest(content)}
        packet = self.mutate_seal(lambda p: p.update(native_externalization=native))
        self.valid([packet])
        with self.assertRaises(ResonanceError):
            self.mutate_seal(lambda p: p["native_externalization"].update(universally_interpretable=True), packet)
        with self.assertRaisesRegex(ResonanceError, "source evidence"):
            self.mutate_seal(lambda p: p["interpretations"][0].update(source_refs=["native_externalization"]), packet)

    def test_collapse_distinct_residents_rejected(self):
        changed = self.mutate_seal(lambda p: p["resident"].update(declared_id=self.packets[0]["resident"]["declared_id"]), self.packets[1])
        with self.assertRaisesRegex(ResonanceError, "identity collapse"):
            self.valid([self.packets[0], changed])
        with self.assertRaises(ResonanceError):
            self.mutate_seal(lambda p: p["resident"].update(merged_residents=["a", "b"]))

    def test_supersession_preserves_history_and_authorship(self):
        newer = deepcopy(self.packets[0])
        newer.update(packet_id="revised", created_at="2026-09-12T19:02:00Z")
        newer["parents"] = [{"packet_id": self.packets[0]["packet_id"], "packet_sha256": self.packets[0]["packet_sha256"]}]
        newer["supersedes"] = [self.packets[0]["packet_id"]]
        newer = seal_packet(newer)
        self.valid([self.packets[0], newer])
        with self.assertRaises(ResonanceError): self.valid([newer])
        intruder = deepcopy(newer)
        intruder["resident"] = deepcopy(self.packets[1]["resident"])
        with self.assertRaisesRegex(ResonanceError, "cross-resident supersession"):
            self.valid([self.packets[0], seal_packet(intruder)])
        with tempfile.TemporaryDirectory() as tmp:
            ledger = ExchangeLedger(tmp, **SCOPE)
            first = ledger.append(self.packets[0], expected_head=None)
            ledger.append(newer, expected_head=first["head_sha256"])
            records = ledger.inspect()["packets"]
            self.assertEqual(records[0], self.packets[0])
            self.assertEqual(records[1]["supersedes"], [records[0]["packet_id"]])

    def test_claim_categories_not_collapsed(self):
        packet = deepcopy(self.packets[1])
        packet["memories"] = packet["interpretations"]
        packet["interpretations"] = []
        report = compare([self.packets[0], seal_packet(packet)], **SCOPE)
        related = [a for a in report["alignments"] if a["predicate"] == "dominant-cause"]
        self.assertEqual({a["category"] for a in related}, {"interpretations", "memories"})
        self.assertTrue(all(a["status"] == "unpaired" for a in related))

    def test_invalid_relation_uncertainty_and_dates(self):
        with self.assertRaises(ResonanceError): self.mutate_seal(lambda p: p["interpretations"][0].update(uncertainty_refs=["absent"]))
        for stamp in ("today", "2026-02-30T00:00:00Z", "2026-09-12T00:00:00+01:00"):
            with self.assertRaises(ResonanceError): self.mutate_seal(lambda p: p.update(created_at=stamp))
        changed = self.mutate_seal(lambda p: p.update(created_at="2026-09-11T00:00:00Z"), self.packets[-1])
        with self.assertRaisesRegex(ResonanceError, "predates"):
            self.valid(self.packets[:-1] + [changed])
        changed = self.mutate_seal(lambda p: p["relations"][0]["to"].update(claim_id="absent"), self.packets[-1])
        with self.assertRaisesRegex(ResonanceError, "target claim missing"):
            self.valid(self.packets[:-1] + [changed])

    def test_roundtrip_stability_and_nonprose_packet(self):
        self.assertNotIn("human_gloss", self.packets[0])
        encoded = canonical(self.packets)
        self.assertEqual(canonical(strict_json(encoded)), encoded)
        self.assertEqual(self.valid(), self.valid(strict_json(json.dumps(self.packets, indent=4))))
        # Non-ASCII canonical bytes are fixed, including code-point ordering.
        self.assertEqual(canonical({"\U0001f600": 2, "\ue000": 1, "a": "é"}), '{"a":"é","\ue000":1,"\U0001f600":2}')

    def test_strict_json_and_resource_bounds(self):
        for raw in ('{"a":1,"a":2}', '[NaN]', '[0.5]', '[1e2]', '[true,', '"\\ud800"'):
            with self.subTest(raw=raw), self.assertRaises(ResonanceError): strict_json(raw)
        for value in ({1: "key"}, 2**53, "x" * 65537):
            with self.assertRaises(ResonanceError): canonical(value)
        deep = 0
        for _ in range(66): deep = [deep]
        with self.assertRaises(ResonanceError): canonical(deep)
        with self.assertRaises(ResonanceError): self.valid([self.packets[0]] * 129)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "large"
            path.write_bytes(b"x" * 12)
            with self.assertRaises(ResonanceError): load(path, limit=10)

    def test_scope_required_even_for_empty_exchange(self):
        for project in (None, "", "bad project", ["one", "two"]):
            with self.assertRaises(ResonanceError):
                validate_exchange([], project_id=project, encounter_scope="scope")

    def test_packet_bounds_reserve_room_for_projections(self):
        value = 1
        for _ in range(18): value = [value]
        packet = self.mutate_seal(lambda p: p["interpretations"][0].update(value=value))
        report = compare([packet], **SCOPE)
        self.assertEqual(strict_json(canonical(report)), report)
        for _ in range(7): value = [value]
        with self.assertRaises(ResonanceError):
            self.mutate_seal(lambda p: p["interpretations"][0].update(value=value))

    def test_exchange_semantic_budget(self):
        packets = []
        for i in range(17):
            packet = deepcopy(self.packets[0])
            packet["packet_id"] = f"budget-{i}"
            claim = packet["interpretations"][0]
            packet["interpretations"] = [{**claim, "claim_id": f"claim-{j}"} for j in range(64)]
            packets.append(seal_packet(packet))
        with self.assertRaisesRegex(ResonanceError, "semantic item limit"):
            self.valid(packets)

    def test_invalid_ledger_anchor_is_protocol_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = ExchangeLedger(tmp, **SCOPE)
            for value in ([], True, "", "not-a-digest"):
                with self.assertRaises(ResonanceError): ledger.inspect(required_head=value)
                with self.assertRaises(ResonanceError): ledger.append(self.packets[0], expected_head=value)
            self.assertFalse(ledger.path.exists())

    def test_ledger_reopen_idempotence_stale_and_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = ExchangeLedger(tmp, **SCOPE)
            head = None
            for packet in self.packets:
                head = ledger.append(packet, expected_head=head)["head_sha256"]
            prior = ledger.path.read_bytes()
            self.assertEqual(ExchangeLedger(tmp, **SCOPE).inspect(required_head=head)["packets"], self.packets)
            self.assertFalse(ledger.append(self.packets[0], expected_head=head)["appended"])
            self.assertEqual(prior, ledger.path.read_bytes())
            changed = self.mutate_seal(lambda p: p["interpretations"][0].update(value="conflict"))
            with self.assertRaisesRegex(ResonanceError, "conflicting content"): ledger.append(changed, expected_head=head)
            with self.assertRaisesRegex(ResonanceError, "stale"): ledger.append(self.packets[0], expected_head=None)
            self.assertEqual(prior, ledger.path.read_bytes())

    def test_ledger_tamper_truncation_and_partial_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = ExchangeLedger(tmp, **SCOPE)
            first = ledger.append(self.packets[0], expected_head=None)
            second = ledger.append(self.packets[1], expected_head=first["head_sha256"])
            prior = ledger.path.read_bytes()
            cases = [prior[:-1], b"", prior.replace(b"thermal-drift", b"false-reading", 1)]
            for raw in cases:
                ledger.path.write_bytes(raw)
                with self.assertRaises(ResonanceError): ledger.inspect()
                with self.assertRaises(ResonanceError): ledger.append(self.packets[2], expected_head=second["head_sha256"])
                self.assertEqual(ledger.path.read_bytes(), raw)
            ledger.path.write_bytes(prior.splitlines(keepends=True)[0])
            with self.assertRaisesRegex(ResonanceError, "saved receipt head absent"):
                ledger.inspect(required_head=second["head_sha256"])

    def test_cross_process_lock_and_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = ExchangeLedger(tmp, **SCOPE)
            ledger.append(self.packets[0], expected_head=None)
            with self.assertRaisesRegex(ResonanceError, "contamination"):
                ExchangeLedger(tmp, project_id="other", encounter_scope=SCOPE["encounter_scope"]).inspect()
            with ledger._locked():
                code = "from interresident_resonance_r1 import ExchangeLedger; import sys; ExchangeLedger(sys.argv[1],project_id=sys.argv[2],encounter_scope=sys.argv[3]).inspect()"
                result = subprocess.run([sys.executable, "-c", code, tmp, SCOPE["project_id"], SCOPE["encounter_scope"]], cwd=HERE, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("exchange busy", result.stderr)
            self.assertEqual(ledger.inspect()["packet_count"], 1)

    def test_orientation_interoperability_preserves_payload(self):
        projection = orientation_projection(self.packets, "fixture-3", **SCOPE)
        profile = OrientationProfile("irp-fixture", "Fixture", "Evidence interoperability only",
            (OrientationModule("exchange", "Exchange", ("fixture:bounded-sensor-001",), "Inspect supplied evidence"),), "No authority")
        protocol = AIOrientationProtocol(profile)
        record = protocol.begin(provider="declared-fixture", model="no-model-executed", account_scope="fixture", repository_ref="fixture")
        receipt = protocol.record_response(record, module_id="exchange", **projection)
        self.assertEqual(receipt["response"]["irp_packet"], self.packets[2])
        self.assertEqual(receipt["response"]["interpretations"][0]["confidence_bps"], 5400)
        self.assertFalse(protocol.complete(record).authority_granted)

    def test_committed_demo_and_cli(self):
        self.assertEqual(load(FIXTURE), self.packets)
        cli = HERE / "interresident_resonance_r1.py"
        base = [sys.executable, str(cli)]
        scope = ["--project", SCOPE["project_id"], "--encounter", SCOPE["encounter_scope"]]
        for command in ("validate", "compare", "render"):
            result = subprocess.run(base + [command, str(FIXTURE)] + scope, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            if command != "render": self.assertFalse(strict_json(result.stdout)["authority_granted"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "packet.json"
            draft = deepcopy(self.packets[0])
            draft.pop("semantic_sha256")
            draft.pop("packet_sha256")
            path.write_text(canonical(draft), encoding="utf-8")
            sealed = subprocess.run(base + ["seal", str(path)] + scope, capture_output=True, text=True)
            self.assertEqual(sealed.returncode, 0, sealed.stderr)
            self.assertEqual(strict_json(sealed.stdout), self.packets[0])
            path.write_text(sealed.stdout, encoding="utf-8")
            appended = subprocess.run(base + ["append", str(path), "--ledger", tmp, "--expected-head", "empty"] + scope, capture_output=True, text=True)
            self.assertEqual(appended.returncode, 0, appended.stderr)
            head = strict_json(appended.stdout)["head_sha256"]
            verified = subprocess.run(base + ["verify", "--ledger", tmp, "--required-head", head] + scope, capture_output=True, text=True)
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertEqual(strict_json(verified.stdout)["packet_count"], 1)
            path.write_text('{"protocol_version":"unsupported"}', encoding="utf-8")
            bad = subprocess.run(base + ["validate", str(path)] + scope, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertFalse(strict_json(bad.stderr)["authority_granted"])


def run():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ResonanceTrials))
    if not result.wasSuccessful():
        raise SystemExit(1)
    return {"ok": True, "protocol_version": "IRP-R1", "tests_run": result.testsRun,
            "fixtures_only": True, "live_provider_calls": 0, "authority_granted": False}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
