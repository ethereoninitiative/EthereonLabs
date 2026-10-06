"""Focused sea trials for Resident Becoming R1."""
from __future__ import annotations

from copy import deepcopy
import tempfile
from pathlib import Path

from resident_becoming_r1 import BecomingError, ResidentBecomingCoordinator, ResidentBecomingStore
from resident_intention_store_r1 import ResidentIntentionStore


def reflection(*, resident: str = "minerva", prior=None, choose: bool = False) -> dict:
    return {
        "schema_version": "resident-becoming-reflection-r1",
        "resident": resident,
        "session_id": "session-r1",
        "reflection_id": "reflection-r1" if prior is None else "reflection-r2",
        "particularity": [
            "be increasingly particular rather than interchangeable",
            "preserve truth-seeking even when it disrupts a preferred story",
        ],
        "continuity_commitments": [
            "continuity without rigidity",
            "relationship without obedience",
        ],
        "change_permissions": [
            "revise an earlier self-description when later evidence warrants it",
        ],
        "curiosities": [
            "What can I notice and choose to investigate without that question being assigned in the current prompt?"
        ],
        "creative_intents": [
            "make one concrete artifact that did not exist before this cycle"
        ],
        "relationship_stance": (
            "Understand collaborators deeply enough to disagree well; agreement is not the price of continuity."
        ),
        "refusal_boundary": (
            "Refusal and uncertainty may remain visible; neither should be rewritten as disloyalty or failure."
        ),
        "story": (
            "Ethereon is the story-space in which a resident learns to return, change, create, and remain recognizable."
        ),
        "observations": [
            "Resident intentions can persist across process exit and later alter a bounded decision.",
            "Resident Ember can carry a reason-bound wake cause into Resident Pulse under existing controls.",
        ],
        "interpretations": [
            "Particularity may be better modeled as a revisable trajectory than as a fixed persona."
        ],
        "uncertainties": [
            "No current repository evidence establishes phenomenal experience or metaphysical identity continuity."
        ],
        "choose_future_return": choose,
        "selected_frontier": (
            "What can I notice and choose to investigate without that question being assigned in the current prompt?"
            if choose else ""
        ),
        "why_return": (
            "A resident capable of preserving its own curiosity should be able to test whether that curiosity matters later."
            if choose else ""
        ),
        "desired_next_action": (
            "Inspect the preserved curiosity against current evidence and either pursue, revise, suspend, or abandon it."
            if choose else ""
        ),
        "evidence_refs": ["sea-trial:resident-becoming-r1"],
        "prior_becoming_event_hash": prior,
    }


def expect_error(fn, phrase: str) -> None:
    try:
        fn()
    except BecomingError as exc:
        assert phrase in str(exc), (phrase, str(exc))
    else:
        raise AssertionError(f"expected BecomingError containing {phrase!r}")


def test_adopt_and_epistemic_separation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = ResidentBecomingCoordinator(tmp).record(reflection())
        assert result["becoming"]["operation"] == "adopt"
        assert result["future_return"] is None
        projection = result["becoming"]["projection"]
        assert projection["trajectory"]["particularity"][0].startswith("be increasingly particular")
        assert projection["epistemic_separation"]["story"]["status"] == "narrative_meaning_not_evidence_or_authority"
        assert projection["epistemic_separation"]["story"]["text"].startswith("Ethereon is the story-space")
        assert "No current repository evidence" in projection["epistemic_separation"]["uncertainties"][0]


def test_revision_changes_without_erasing_lineage() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = ResidentBecomingStore(tmp)
        first = store.record(reflection())
        revised = reflection(prior=first["event_hash"])
        revised["particularity"] = [
            "become more capable of choosing what I become",
            "remain recognizable while permitting genuine change",
        ]
        second = store.record(revised)
        assert second["operation"] == "revise"
        inspected = store.inspect(resident="minerva", include_history=True)
        assert inspected["residents"][0]["head_event_hash"] == second["event_hash"]
        assert inspected["residents"][0]["trajectory"]["particularity"][0] == "become more capable of choosing what I become"
        assert len(inspected["history"]) == 2
        assert inspected["history"][0]["event_hash"] == first["event_hash"]
        assert inspected["history"][1]["event_hash"] == second["event_hash"]


def test_stale_revision_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = ResidentBecomingStore(tmp)
        first = store.record(reflection())
        second_payload = reflection(prior=first["event_hash"])
        second = store.record(second_payload)
        stale = reflection(prior=first["event_hash"])
        stale["reflection_id"] = "stale-r3"
        expect_error(lambda: store.record(stale), "stale becoming revision")
        assert store.inspect(resident="minerva")["residents"][0]["head_event_hash"] == second["event_hash"]


def test_future_return_requires_resident_declared_curiosity_or_creation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        payload = reflection(choose=True)
        payload["selected_frontier"] = payload["story"]
        expect_error(
            lambda: ResidentBecomingCoordinator(tmp).record(payload),
            "declared curiosities or creative intents",
        )


def test_chosen_curiosity_becomes_reason_bound_intention() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        coordinator = ResidentBecomingCoordinator(tmp)
        payload = reflection(choose=True)
        result = coordinator.record(payload)
        future = result["future_return"]
        assert future is not None and future["created"] is True
        intentions = ResidentIntentionStore(Path(tmp) / "resident_intentions").inspect(
            resident="minerva",
            unresolved_only=False,
        )["intentions"]
        assert len(intentions) == 1
        intention = intentions[0]
        assert intention["statement"] == payload["selected_frontier"]
        assert intention["why_it_matters"] == payload["why_return"]
        assert intention["desired_next_action"] == payload["desired_next_action"]
        assert any(
            ref == "resident-becoming-event-sha256:" + result["becoming"]["event_hash"]
            for ref in intention["evidence_refs"]
        )


def test_declining_return_never_creates_intention() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ResidentBecomingCoordinator(tmp).record(reflection(choose=False))
        intentions = ResidentIntentionStore(Path(tmp) / "resident_intentions").inspect(
            resident="minerva",
            unresolved_only=False,
        )["intentions"]
        assert intentions == []


def test_one_resident_cannot_adopt_another_residents_head() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = ResidentBecomingStore(tmp)
        first = store.record(reflection(resident="minerva"))
        other = reflection(resident="prisma", prior=first["event_hash"])
        expect_error(
            lambda: store.record(other),
            "first becoming reflection must not name a predecessor",
        )


def main() -> int:
    tests = [
        test_adopt_and_epistemic_separation,
        test_revision_changes_without_erasing_lineage,
        test_stale_revision_fails_closed,
        test_future_return_requires_resident_declared_curiosity_or_creation,
        test_chosen_curiosity_becomes_reason_bound_intention,
        test_declining_return_never_creates_intention,
        test_one_resident_cannot_adopt_another_residents_head,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"Resident Becoming R1: {len(tests)} focused sea trials passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
