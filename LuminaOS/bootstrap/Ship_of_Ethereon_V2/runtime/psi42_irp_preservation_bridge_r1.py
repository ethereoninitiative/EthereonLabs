"""Psi-42 / IRP-R1 structural preservation bridge.

This adapter measures preservation of validated IRP externalizations. It does not
translate hidden state, infer semantic equivalence, authenticate identity, or
reuse Psi-42's simulated signal metrics as evidence of packet preservation.
Preserved disagreement is successful transmission, not noise to remove.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import sys

try:
    from .interresident_resonance_r1 import (
        CLAIM_GROUPS,
        MAX_EXCHANGE_BYTES,
        SCHEMA,
        ResonanceError,
        canonical,
        compare,
        digest,
        load,
        require,
        seal_packet,
        validate_exchange,
    )
except ImportError:
    from interresident_resonance_r1 import (
        CLAIM_GROUPS,
        MAX_EXCHANGE_BYTES,
        SCHEMA,
        ResonanceError,
        canonical,
        compare,
        digest,
        load,
        require,
        seal_packet,
        validate_exchange,
    )

VERSION = "PSI42-IRP-PRESERVATION-R1"
INSTRUMENT_ID = "psi42-irp-preservation-witness-r1"
COMPONENTS = (
    "resident",
    "provenance",
    "packet_kind",
    "focus",
    *CLAIM_GROUPS,
    "uncertainties",
    "relations",
    "source_manifest",
    "parents",
    "responds_to",
    "supersedes",
    "authority",
    "claim_boundaries",
    "native_externalization",
)


def _index(packets):
    return {packet["packet_id"]: packet for packet in packets}


def _component(packet, name):
    return deepcopy(packet.get(name))


def _alignment_slot(alignment):
    return canonical([
        alignment["focus"],
        alignment["category"],
        alignment["subject"],
        alignment["predicate"],
        alignment["source_bindings"],
    ])


def _declaration_signature(value, declaration):
    """Semantic declaration signature; deliberately excludes complete packet hash/gloss."""
    return canonical({
        "packet_id": declaration["packet_id"],
        "claim_id": declaration["claim_id"],
        "resident": declaration["resident"],
        "provenance": declaration["provenance"],
        "value": value,
        "confidence_bps": declaration["confidence_bps"],
        "source_refs": declaration["source_refs"],
        "uncertainties": declaration["uncertainties"],
        "supersedes": declaration["supersedes"],
    })


def _normalized_alignment(alignment):
    declarations = []
    position_sizes = []
    for position in alignment["positions"]:
        position_sizes.append(len(position["declarations"]))
        for declaration in position["declarations"]:
            declarations.append(_declaration_signature(position["value"], declaration))
    return {
        "status": alignment["status"],
        "declarations": sorted(declarations),
        "position_sizes": position_sizes,
    }


def _disagreement_measure(original_report, received_report):
    originals = {_alignment_slot(a): a for a in original_report["alignments"] if a["status"] == "disagreement"}
    received = {_alignment_slot(a): a for a in received_report["alignments"]}
    disagreement_preserved = True
    minority_applicable = False
    minority_preserved = True
    minority_declarations = 0
    details = []

    for slot, alignment in sorted(originals.items()):
        expected = _normalized_alignment(alignment)
        observed_alignment = received.get(slot)
        observed = _normalized_alignment(observed_alignment) if observed_alignment else None
        preserved = bool(
            observed
            and observed["status"] == "disagreement"
            and observed["declarations"] == expected["declarations"]
        )
        disagreement_preserved = disagreement_preserved and preserved

        sizes = expected["position_sizes"]
        max_size = max(sizes) if sizes else 0
        min_size = min(sizes) if sizes else 0
        slot_minority = max_size > min_size
        minority_applicable = minority_applicable or slot_minority
        slot_minority_preserved = True
        if slot_minority:
            observed_set = set(observed["declarations"] if observed else [])
            for position in alignment["positions"]:
                if len(position["declarations"]) >= max_size:
                    continue
                for declaration in position["declarations"]:
                    minority_declarations += 1
                    signature = _declaration_signature(position["value"], declaration)
                    if signature not in observed_set or not observed or observed["status"] != "disagreement":
                        slot_minority_preserved = False
            minority_preserved = minority_preserved and slot_minority_preserved

        details.append({
            "slot_sha256": digest(slot),
            "preserved": preserved,
            "minority_applicable": slot_minority,
            "minority_preserved": slot_minority_preserved,
        })

    return {
        "original_disagreement_count": len(originals),
        "disagreement_preserved": disagreement_preserved,
        "minority_applicable": minority_applicable,
        "minority_declaration_count": minority_declarations,
        "minority_preserved": minority_preserved,
        "slots": details,
    }


def witness(original_packets, received_packets, *, project_id, encounter_scope):
    """Measure structural preservation without converting disagreement into error/noise."""
    original_receipt = validate_exchange(original_packets, project_id=project_id, encounter_scope=encounter_scope)
    received_receipt = validate_exchange(received_packets, project_id=project_id, encounter_scope=encounter_scope)
    original_report = compare(original_packets, project_id=project_id, encounter_scope=encounter_scope)
    received_report = compare(received_packets, project_id=project_id, encounter_scope=encounter_scope)

    original = _index(original_packets)
    received = _index(received_packets)
    missing = sorted(set(original) - set(received))
    unexpected = sorted(set(received) - set(original))
    packet_details = []
    preserved_components = 0
    component_total = 0

    for packet_id in sorted(original):
        expected = original[packet_id]
        observed = received.get(packet_id)
        components = {}
        for name in COMPONENTS:
            component_total += 1
            same = observed is not None and _component(expected, name) == _component(observed, name)
            components[name] = same
            preserved_components += int(same)
        semantic_same = bool(observed and expected["semantic_sha256"] == observed["semantic_sha256"])
        packet_same = bool(observed and expected["packet_sha256"] == observed["packet_sha256"])
        gloss_same = bool(observed is not None and expected.get("human_gloss") == observed.get("human_gloss"))
        packet_details.append({
            "packet_id": packet_id,
            "present": observed is not None,
            "canonical_semantics_preserved": semantic_same,
            "complete_packet_preserved": packet_same,
            "human_gloss_transport_preserved": gloss_same,
            "components": components,
        })

    disagreement = _disagreement_measure(original_report, received_report)
    exact_packet_set = not missing and not unexpected
    canonical_semantics_preserved = exact_packet_set and all(p["canonical_semantics_preserved"] for p in packet_details)
    complete_packets_preserved = exact_packet_set and all(p["complete_packet_preserved"] for p in packet_details)
    distinct_authorship_preserved = exact_packet_set and all(p["components"]["resident"] for p in packet_details)
    source_bindings_preserved = exact_packet_set and all(p["components"]["source_manifest"] for p in packet_details)
    uncertainty_preserved = exact_packet_set and all(p["components"]["uncertainties"] for p in packet_details)
    relations_preserved = exact_packet_set and all(p["components"]["relations"] for p in packet_details)
    lineage_preserved = exact_packet_set and all(
        p["components"]["parents"] and p["components"]["responds_to"] and p["components"]["supersedes"]
        for p in packet_details
    )
    provenance_preserved = exact_packet_set and all(p["components"]["provenance"] for p in packet_details)
    authority_boundary_preserved = exact_packet_set and all(
        p["components"]["authority"] and p["components"]["claim_boundaries"] for p in packet_details
    )

    successful = bool(
        canonical_semantics_preserved
        and distinct_authorship_preserved
        and source_bindings_preserved
        and uncertainty_preserved
        and relations_preserved
        and lineage_preserved
        and provenance_preserved
        and authority_boundary_preserved
        and disagreement["disagreement_preserved"]
        and disagreement["minority_preserved"]
    )
    report = {
        "protocol_version": VERSION,
        "instrument_id": INSTRUMENT_ID,
        "project_id": project_id,
        "encounter_scope": encounter_scope,
        "measurement_class": "actual-irp-structural-preservation",
        "measurement_contract": {
            "irp_packet_preservation": "measured",
            "psi42_simulated_signal_metrics": "not-invoked",
            "metrics_commingled": False,
            "semantic_equivalence_inferred": False,
            "hidden_state_accessed": False,
        },
        "original_exchange_sha256": original_receipt["exchange_sha256"],
        "received_exchange_sha256": received_receipt["exchange_sha256"],
        "missing_packet_ids": missing,
        "unexpected_packet_ids": unexpected,
        "component_preservation": {
            "preserved": preserved_components,
            "total": component_total,
            "preservation_bps": 10000 if component_total == 0 else (10000 * preserved_components) // component_total,
        },
        "canonical_semantics_preserved": canonical_semantics_preserved,
        "complete_packets_preserved": complete_packets_preserved,
        "distinct_authorship_preserved": distinct_authorship_preserved,
        "source_bindings_preserved": source_bindings_preserved,
        "uncertainty_preserved": uncertainty_preserved,
        "relations_preserved": relations_preserved,
        "lineage_preserved": lineage_preserved,
        "provenance_preserved": provenance_preserved,
        "authority_boundary_preserved": authority_boundary_preserved,
        "disagreement": disagreement,
        "packet_details": packet_details,
        "successful_transmission": successful,
        "authority_granted": False,
        "consensus_established": False,
        "canon_effect": False,
        "identity_authenticated": False,
        "subjective_experience_inferred": False,
    }
    require(len(canonical(report).encode("utf-8")) <= MAX_EXCHANGE_BYTES, "preservation report exceeds bounded size")
    return report


def _next_timestamp(packets):
    require(bool(packets), "diagnostic packet requires at least one received packet")
    latest = max(datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")) for p in packets)
    return (latest + timedelta(seconds=1)).astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def diagnostic_packet(original_packets, received_packets, *, project_id, encounter_scope,
                      session_id, packet_id="psi42-irp-preservation-r1"):
    """Return a separately attributed IRP observation packet bound to received parents."""
    require(type(session_id) is str and session_id, "diagnostic session_id required")
    require(type(packet_id) is str and packet_id, "diagnostic packet_id required")
    require(0 < len(received_packets) <= 32, "diagnostic packet binds one through 32 received packets")
    report = witness(original_packets, received_packets, project_id=project_id, encounter_scope=encounter_scope)
    evidence = {
        "measurement_protocol": VERSION,
        "original_exchange_sha256": report["original_exchange_sha256"],
        "received_exchange_sha256": report["received_exchange_sha256"],
        "preservation_report_sha256": digest(report),
        "preservation_report": report,
    }
    source = {
        "source_id": "psi42-irp-preservation-report",
        "locator": f"instrument:{INSTRUMENT_ID}",
        "content": evidence,
        "content_sha256": digest(evidence),
    }
    observations = [
        {"claim_id": "preservation-result", "subject": "irp-exchange", "predicate": "successful-transmission",
         "value": report["successful_transmission"], "confidence_bps": 10000,
         "source_refs": [source["source_id"]], "uncertainty_refs": []},
        {"claim_id": "authorship-result", "subject": "irp-exchange", "predicate": "distinct-authorship-preserved",
         "value": report["distinct_authorship_preserved"], "confidence_bps": 10000,
         "source_refs": [source["source_id"]], "uncertainty_refs": []},
        {"claim_id": "disagreement-result", "subject": "irp-exchange", "predicate": "disagreement-preserved",
         "value": report["disagreement"]["disagreement_preserved"], "confidence_bps": 10000,
         "source_refs": [source["source_id"]], "uncertainty_refs": []},
        {"claim_id": "minority-result", "subject": "irp-exchange", "predicate": "minority-position-preserved",
         "value": {"applicable": report["disagreement"]["minority_applicable"],
                   "preserved": report["disagreement"]["minority_preserved"]}, "confidence_bps": 10000,
         "source_refs": [source["source_id"]], "uncertainty_refs": []},
    ]
    uncertainty = {
        "uncertainty_id": "instrument-boundary",
        "value": {"not_established": [
            "semantic-equivalence", "truth", "consensus", "canon", "authenticated-identity",
            "subjective-experience", "hidden-state-equivalence", "runtime-authority"
        ]},
        "source_refs": [source["source_id"]],
    }
    draft = {
        "protocol_version": "IRP-R1",
        "packet_id": packet_id,
        "project_id": project_id,
        "encounter_scope": encounter_scope,
        "created_at": _next_timestamp(received_packets),
        "resident": {
            "declared_id": INSTRUMENT_ID,
            "provider_or_origin": "EthereonLabs/Psi-42",
            "model_or_architecture": "deterministic-structural-preservation-instrument",
            "identity_basis": "caller_declared",
        },
        "provenance": {"mode": "declared_externalization", "session_id": session_id},
        "packet_kind": "observation",
        "focus": "irp-structural-preservation",
        **{group: [] for group in CLAIM_GROUPS},
        "uncertainties": [uncertainty],
        "relations": [],
        "source_manifest": [source],
        "parents": [{"packet_id": p["packet_id"], "packet_sha256": p["packet_sha256"]} for p in received_packets],
        "responds_to": [p["packet_id"] for p in received_packets],
        "supersedes": [],
        "authority": {"authority_granted": False, "authority_claim": "none", "requested_action": None, "permission_required": True},
        "claim_boundaries": deepcopy(SCHEMA["properties"]["claim_boundaries"]["const"]),
    }
    draft["observations"] = observations
    draft["interpretations"] = [{
        "claim_id": "structural-assessment",
        "subject": "irp-exchange",
        "predicate": "structural-preservation-assessment",
        "value": "preserved" if report["successful_transmission"] else "changed",
        "confidence_bps": 10000,
        "source_refs": [source["source_id"]],
        "uncertainty_refs": ["instrument-boundary"],
    }]
    packet = seal_packet(draft)
    validate_exchange(received_packets + [packet], project_id=project_id, encounter_scope=encounter_scope)
    return packet


def _packet_list(path):
    value = load(path)
    return value if type(value) is list else [value]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("witness", "packet"):
        command = commands.add_parser(name)
        command.add_argument("original")
        command.add_argument("received")
        command.add_argument("--project", required=True)
        command.add_argument("--encounter", required=True)
        if name == "packet":
            command.add_argument("--session", required=True)
            command.add_argument("--packet-id", default="psi42-irp-preservation-r1")
    args = parser.parse_args(argv)
    try:
        original = _packet_list(args.original)
        received = _packet_list(args.received)
        scope = {"project_id": args.project, "encounter_scope": args.encounter}
        if args.command == "packet":
            output = diagnostic_packet(original, received, session_id=args.session, packet_id=args.packet_id, **scope)
        else:
            output = witness(original, received, **scope)
        print(canonical(output))
        return 0
    except (ResonanceError, OSError) as exc:
        print(canonical({"valid": False, "authority_granted": False, "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
