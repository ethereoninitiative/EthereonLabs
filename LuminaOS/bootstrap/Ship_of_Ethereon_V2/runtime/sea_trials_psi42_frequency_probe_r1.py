"""Sea trial for the bounded Psi-42 frequency-domain probe.

The trial uses a deterministic synthetic signal containing the declared
432/528/963 Hz components, then verifies that removing one component suppresses
only that measured component. This is a signal-measurement test, not a
continuity, consciousness, or authority test.
"""

from __future__ import annotations

import json
import math
import random
from typing import Dict

from psi42_frequency_probe_r1 import (
    DEFAULT_HARMONIC_FREQUENCIES_HZ,
    AUTHORITY_BOUNDARY,
    FrequencyDomainProbeR1,
    FrequencyProbeConfig,
)

SAMPLE_RATE_HZ = 4096.0
SAMPLE_COUNT = 4096
NOISE_SEED = 42
TARGET_AMPLITUDES = {
    432.0: 0.70,
    528.0: 0.50,
    963.0: 0.30,
}


def _synthetic_signal(amplitudes: Dict[float, float], noise_amplitude: float = 0.0) -> list[float]:
    rng = random.Random(NOISE_SEED)
    samples: list[float] = []
    for index in range(SAMPLE_COUNT):
        time_s = index / SAMPLE_RATE_HZ
        value = sum(
            amplitude * math.sin(2.0 * math.pi * frequency_hz * time_s)
            for frequency_hz, amplitude in amplitudes.items()
        )
        if noise_amplitude:
            value += noise_amplitude * rng.uniform(-1.0, 1.0)
        samples.append(value)
    return samples


def _amplitudes(receipt: dict[str, object]) -> dict[float, float]:
    measurements = receipt["measurements"]
    return {
        float(measurement["frequency_hz"]): float(measurement["amplitude"])
        for measurement in measurements
    }


def run() -> dict[str, object]:
    config = FrequencyProbeConfig(
        sample_rate_hz=SAMPLE_RATE_HZ,
        harmonic_frequencies_hz=DEFAULT_HARMONIC_FREQUENCIES_HZ,
    )
    probe = FrequencyDomainProbeR1(config)

    full_signal = _synthetic_signal(TARGET_AMPLITUDES, noise_amplitude=0.01)
    full_receipt = probe.analyze(full_signal)
    full_amplitudes = _amplitudes(full_receipt)

    assert full_amplitudes[432.0] > full_amplitudes[528.0] > full_amplitudes[963.0]
    assert full_amplitudes[432.0] > 0.55
    assert full_amplitudes[528.0] > 0.35
    assert full_amplitudes[963.0] > 0.15

    control_signal = _synthetic_signal({432.0: 0.70, 963.0: 0.30})
    control_receipt = probe.analyze(control_signal)
    control_amplitudes = _amplitudes(control_receipt)
    assert control_amplitudes[528.0] < 0.05

    return {
        "suite": "Psi-42 Frequency-Domain Probe R1",
        "passed": True,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "target_frequencies_hz": list(DEFAULT_HARMONIC_FREQUENCIES_HZ),
        "full_signal_amplitudes": full_amplitudes,
        "control_signal_amplitudes": control_amplitudes,
        "suppressed_frequency_hz": 528.0,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
