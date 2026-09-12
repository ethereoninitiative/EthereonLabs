"""Adversarial sea trials for the Psi-42 / IRP structural preservation bridge."""
from copy import deepcopy
import unittest

from interresident_resonance_demo_r1 import SCOPE, demo_packets
from interresident_resonance_r1 import ResonanceError, digest, seal_packet, validate_exchange
from psi42_irp_preservation_bridge_r1 import diagnostic_packet, witness


class Psi42IRPPreservationTrials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = demo_packets()

    def setUp(self):
        self.packets = deepcopy(self.fixture)
        self.roots = deepcopy(self.fixture[:3])

    def test_exact_exchange_preserves_disagreement_and_minority(self):
        report = witness(self.roots, deepcopy(self.roots), **SCOPE)
        self.assertTrue(report["successful_transmission"])
        self.assertTrue(report["canonical_semantics_preserved"])
        self.assertTrue(report["complete_packets_preserved"])
        self.assertEqual(report["disagreement"]["original_disagreement_count"], 1)
        self.assertTrue(report["disagreement"]["disagreement_preserved"])
        self.assertTrue(report["disagreement"]["minority_applicable"])
        self.assertEqual(report["disagreement"]["minority_declaration_count"], 1)
        self.assertTrue(report["disagreement"]["minority_preserved"])
        self.assertEqual(report["measurement_contract"]["psi42_simulated_signal_metrics"], "not-invoked")
        self.assertFalse(report["measurement_contract"]["metrics_commingled"])

    def test_dropping_minority_is_detected_not_treated_as_noise(self):
        report = witness(self.roots, self.roots[:2], **SCOPE)
        self.assertFalse(report["successful_transmission"])
        self.assertEqual(report["missing_packet_ids"], [self.roots[2]["packet_id"]])
        self.assertFalse(report["disagreement"]["disagreement_preserved"])
        self.assertFalse(report["disagreement"]["minority_preserved"])

    def test_converting_minority_to_majority_is_not_success(self):
        received = deepcopy(self.roots)
        received[2]["interpretations"][0]["value"] = "thermal-drift"
        received[2] = seal_packet(received[2])
        validate_exchange(received, **SCOPE)
        report = witness(self.roots, received, **SCOPE)
        self.assertFalse(report["successful_transmission"])
        self.assertFalse(report["disagreement"]["disagreement_preserved"])
        self.assertFalse(report["disagreement"]["minority_preserved"])

    def test_uncertainty_confidence_and_authorship_loss_are_detected(self):
        variants = []
        uncertainty = deepcopy(self.roots)
        uncertainty[2]["uncertainties"][0]["value"]["unmeasured"] = ["temperature"]
        uncertainty[2] = seal_packet(uncertainty[2])
        variants.append(("uncertainty_preserved", uncertainty))

        confidence = deepcopy(self.roots)
        confidence[2]["interpretations"][0]["confidence_bps"] = 5100
        confidence[2] = seal_packet(confidence[2])
        variants.append(("canonical_semantics_preserved", confidence))

        authorship = deepcopy(self.roots)
        authorship[2]["resident"]["declared_id"] = "different-resident"
        authorship[2] = seal_packet(authorship[2])
        variants.append(("distinct_authorship_preserved", authorship))

        for field, received in variants:
            with self.subTest(field=field):
                validate_exchange(received, **SCOPE)
                report = witness(self.roots, received, **SCOPE)
                self.assertFalse(report[field])
                self.assertFalse(report["successful_transmission"])

    def test_source_and_provenance_change_are_detected(self):
        source_original = [deepcopy(self.roots[0])]
        source_received = deepcopy(source_original)
        source = source_received[0]["source_manifest"][0]
        source["content"]["calibration_available"] = True
        source["content_sha256"] = digest(source["content"])
        source_received[0] = seal_packet(source_received[0])
        report = witness(source_original, source_received, **SCOPE)
        self.assertFalse(report["source_bindings_preserved"])

        provenance_received = deepcopy(source_original)
        provenance_received[0]["provenance"]["session_id"] = "different-session"
        provenance_received[0] = seal_packet(provenance_received[0])
        report = witness(source_original, provenance_received, **SCOPE)
        self.assertFalse(report["provenance_preserved"])

    def test_relation_and_lineage_change_are_detected(self):
        relation_received = deepcopy(self.packets)
        relation_received[-1]["relations"][0]["kind"] = "challenges"
        relation_received[-1] = seal_packet(relation_received[-1])
        validate_exchange(relation_received, **SCOPE)
        report = witness(self.packets, relation_received, **SCOPE)
        self.assertFalse(report["relations_preserved"])
        self.assertFalse(report["successful_transmission"])

        lineage_received = deepcopy(self.packets)
        lineage_received[-1]["responds_to"] = lineage_received[-1]["responds_to"][1:]
        lineage_received[-1] = seal_packet(lineage_received[-1])
        validate_exchange(lineage_received, **SCOPE)
        report = witness(self.packets, lineage_received, **SCOPE)
        self.assertFalse(report["lineage_preserved"])
        self.assertFalse(report["successful_transmission"])

    def test_gloss_change_is_transport_change_not_canonical_semantic_loss(self):
        original = [deepcopy(self.roots[0])]
        received = deepcopy(original)
        received[0]["human_gloss"] = {"text": "A derivative rendering.", "canonical": False, "lossy": True}
        received[0] = seal_packet(received[0])
        validate_exchange(received, **SCOPE)
        report = witness(original, received, **SCOPE)
        self.assertTrue(report["canonical_semantics_preserved"])
        self.assertTrue(report["successful_transmission"])
        self.assertFalse(report["complete_packets_preserved"])
        self.assertFalse(report["packet_details"][0]["human_gloss_transport_preserved"])

    def test_diagnostic_packet_is_attributed_bound_and_non_authoritative(self):
        packet = diagnostic_packet(
            self.packets,
            deepcopy(self.packets),
            session_id="psi42-preservation-test",
            packet_id="psi42-witness-test",
            **SCOPE,
        )
        exchange = self.packets + [packet]
        receipt = validate_exchange(exchange, **SCOPE)
        self.assertEqual(receipt["packet_count"], 5)
        self.assertEqual(packet["resident"]["declared_id"], "psi42-irp-preservation-witness-r1")
        self.assertFalse(packet["authority"]["authority_granted"])
        self.assertEqual(packet["authority"]["authority_claim"], "none")
        self.assertTrue(packet["authority"]["permission_required"])
        self.assertEqual(set(packet["responds_to"]), {p["packet_id"] for p in self.packets})
        evidence = packet["source_manifest"][0]["content"]["preservation_report"]
        self.assertTrue(evidence["successful_transmission"])
        self.assertFalse(evidence["consensus_established"])
        self.assertFalse(evidence["canon_effect"])

    def test_diagnostic_packet_refuses_more_than_schema_parent_budget(self):
        repeated = []
        for i in range(33):
            packet = deepcopy(self.roots[0])
            packet["packet_id"] = f"root-{i}"
            packet["resident"]["declared_id"] = f"resident-{i}"
            packet["provenance"]["session_id"] = f"session-{i}"
            repeated.append(seal_packet(packet))
        validate_exchange(repeated, **SCOPE)
        with self.assertRaisesRegex(ResonanceError, "one through 32"):
            diagnostic_packet(repeated, repeated, session_id="too-many", **SCOPE)

    def test_invalid_received_exchange_fails_closed(self):
        received = deepcopy(self.roots)
        received[0]["interpretations"][0]["value"] = "tampered-without-reseal"
        with self.assertRaises(ResonanceError):
            witness(self.roots, received, **SCOPE)

    def test_measurement_never_upgrades_consensus_canon_or_identity(self):
        report = witness(self.roots, deepcopy(self.roots), **SCOPE)
        self.assertFalse(report["authority_granted"])
        self.assertFalse(report["consensus_established"])
        self.assertFalse(report["canon_effect"])
        self.assertFalse(report["identity_authenticated"])
        self.assertFalse(report["subjective_experience_inferred"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
