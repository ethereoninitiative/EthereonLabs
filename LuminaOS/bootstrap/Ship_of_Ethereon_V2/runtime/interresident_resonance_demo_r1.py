"""Synthetic IRP fixtures only. No provider was contacted or model exercised."""
from copy import deepcopy
import json

try:
    from .interresident_resonance_r1 import SCHEMA, CLAIM_GROUPS, digest, seal_packet, compare
except ImportError:
    from interresident_resonance_r1 import SCHEMA, CLAIM_GROUPS, digest, seal_packet, compare

SCOPE = {"project_id": "ethereon-irp-fixture", "encounter_scope": "bounded-sensor-001"}


def demo_packets():
    evidence = {
        "fixture_only": True,
        "slot_contract": {"sensor-01/dominant-cause": {"cardinality": "one", "values": ["thermal-drift", "sensor-noise"]}},
        "samples": [{"tick": 0, "reading_milliunits": 1000}, {"tick": 1, "reading_milliunits": 1020}, {"tick": 2, "reading_milliunits": 1018}],
        "temperature_measured": False,
        "calibration_available": False,
    }
    source = {"source_id": "bounded-evidence", "locator": "fixture:bounded-sensor-001",
              "content": evidence, "content_sha256": digest(evidence)}
    packets = []
    for i, (provider, value, confidence) in enumerate([
        ("OpenAI-derived (declared fixture)", "thermal-drift", 7800),
        ("Anthropic-derived (declared fixture)", "thermal-drift", 6200),
        ("Google-derived (declared fixture)", "sensor-noise", 5400),
    ], 1):
        packet = {
            "protocol_version": "IRP-R1", "packet_id": f"fixture-{i}", **SCOPE,
            "created_at": "2026-09-12T19:00:00Z",
            "resident": {"declared_id": f"resident-fixture-{i}", "provider_or_origin": provider,
                         "model_or_architecture": "synthetic-protocol-fixture/no-model-executed", "identity_basis": "caller_declared"},
            "provenance": {"mode": "synthetic_fixture", "session_id": f"independent-fixture-session-{i}"},
            "packet_kind": "interpretation", "focus": "sensor-cause-v1",
            **{group: [] for group in CLAIM_GROUPS},
            "uncertainties": [{"uncertainty_id": "u1", "value": {"unmeasured": ["temperature", "calibration"], "alternatives": ["thermal-drift", "sensor-noise"]}, "source_refs": ["bounded-evidence"]}],
            "relations": [], "source_manifest": [deepcopy(source)], "parents": [], "responds_to": [], "supersedes": [],
            "authority": {"authority_granted": False, "authority_claim": "none", "requested_action": None, "permission_required": True},
            "claim_boundaries": deepcopy(SCHEMA["properties"]["claim_boundaries"]["const"]),
        }
        packet["observations"] = [{"claim_id": "o1", "subject": "sensor-01", "predicate": "samples-count", "value": 3,
                                  "confidence_bps": 10000, "source_refs": ["bounded-evidence"], "uncertainty_refs": []}]
        packet["interpretations"] = [{"claim_id": "i1", "subject": "sensor-01", "predicate": "dominant-cause", "value": value,
                                     "confidence_bps": confidence, "source_refs": ["bounded-evidence"], "uncertainty_refs": ["u1"]}]
        packets.append(seal_packet(packet))
    # A fourth packet is attributed to the first declared resident, not a merged identity.
    synthesis = deepcopy(packets[0])
    synthesis.update(packet_id="fixture-synthesis", created_at="2026-09-12T19:01:00Z", packet_kind="synthesis")
    synthesis["provenance"]["session_id"] = "synthesis-fixture-session"
    synthesis["observations"] = []
    synthesis["interpretations"] = [{"claim_id": "s1", "subject": "exchange-001", "predicate": "declared-positions",
        "value": [{"packet_id": p["packet_id"], "claim_id": "i1", "value": p["interpretations"][0]["value"]} for p in packets],
        "confidence_bps": None, "source_refs": ["bounded-evidence"], "uncertainty_refs": ["u1"]}]
    synthesis["parents"] = [{"packet_id": p["packet_id"], "packet_sha256": p["packet_sha256"]} for p in packets]
    synthesis["responds_to"] = [p["packet_id"] for p in packets]
    synthesis["relations"] = [{"relation_id": f"r{i}", "kind": "extends", "from_claim_id": "s1",
        "to": {**parent, "claim_id": "i1"}, "source_refs": ["bounded-evidence"]} for i, parent in enumerate(synthesis["parents"], 1)]
    synthesis["human_gloss"] = {"text": "Two declared fixtures favor thermal drift; one favors sensor noise. All positions remain attributable and unresolved.", "canonical": False, "lossy": True}
    packets.append(seal_packet(synthesis))
    compare(packets, **SCOPE)
    return packets


if __name__ == "__main__":
    print(json.dumps(demo_packets(), ensure_ascii=False, indent=2, sort_keys=True))
