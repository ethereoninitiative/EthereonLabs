from continuity_index_r1 import compute_continuity_index
from psi42_signal_adapter_r1 import Psi42SignalAdapter
from recursive_reflection_layer_r1 import RecursiveReflectionLayer


def run_full_stack_sea_trial():
    psi42 = Psi42SignalAdapter()
    reflection_layer = RecursiveReflectionLayer()
    signal_history = []

    inputs = [
        "stabilize luminous threads in the chamber",
        "increase resonance in the chamber",
        "observe system coherence",
    ]

    for raw_input in inputs:
        capture = psi42.capture_signal(raw_input, context={"mode": "Observation", "trial": "integrated_loop_r1"})
        reflection = reflection_layer.reflect(
            raw_input,
            mode="Observation",
            constraints=["no_overclaim"],
            prior_stance={
                "psi42_capture_alignment": capture.alignment_score,
                "psi42_capture_drift": capture.drift_score,
            },
        )
        emit = psi42.emit_signal(
            "processed",
            capture_receipt=capture,
            reflection=reflection.to_dict(),
        )
        signal_history.append(capture.to_dict())
        signal_history.append(emit.to_dict())

    continuity = compute_continuity_index(signal_history)
    snapshot = {
        "schema_version": "lumina_integrated_loop_snapshot_r1",
        "authority_boundary": "display and diagnostic snapshot only; does not authorize action",
        "signals": signal_history,
        "continuity": continuity.to_dict(),
    }

    print(snapshot)
    return snapshot


if __name__ == "__main__":
    run_full_stack_sea_trial()
