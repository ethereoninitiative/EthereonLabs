from psi42_signal_adapter_r1 import Psi42SignalAdapter


def run_sea_trial():
    adapter = Psi42SignalAdapter()

    test_input = "stabilize luminous threads in the chamber"

    capture = adapter.capture_signal(test_input, context={"mode": "Observation"})

    output = "acknowledged; stabilizing"

    emit = adapter.emit_signal(output, capture_receipt=capture, reflection={"status": "ok"})

    print("CAPTURE:")
    for k, v in capture.to_dict().items():
        print(f"{k}: {v}")

    print("\nEMIT:")
    for k, v in emit.to_dict().items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    run_sea_trial()
