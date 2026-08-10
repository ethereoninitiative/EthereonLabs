"""Bounded frequency-domain instrumentation for Psi-42 harmonic experiments.

This module introduces an explicit, classical signal mechanism without changing
the default Psi-42 runtime path. It measures supplied samples at declared
frequencies; it does not infer consciousness, continuity, authority, or truth.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Sequence

DEFAULT_HARMONIC_FREQUENCIES_HZ = (432.0, 528.0, 963.0)
AUTHORITY_BOUNDARY = (
    "Derived frequency-domain measurements only; does not establish consciousness, "
    "continuity, identity, governance authority, canon state, consent, or runtime law."
)


@dataclass(frozen=True)
class FrequencyProbeConfig:
    sample_rate_hz: float = 4096.0
    harmonic_frequencies_hz: tuple[float, ...] = DEFAULT_HARMONIC_FREQUENCIES_HZ
    window: str = "hann"

    def validate(self) -> None:
        if self.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        if not self.harmonic_frequencies_hz:
            raise ValueError("at least one harmonic frequency is required")
        if any(frequency <= 0 for frequency in self.harmonic_frequencies_hz):
            raise ValueError("harmonic frequencies must be positive")
        if max(self.harmonic_frequencies_hz) >= self.sample_rate_hz / 2:
            raise ValueError("all frequencies must remain below the Nyquist frequency")
        if self.window != "hann":
            raise ValueError("only the hann window is currently supported")


def _window_weights(sample_count: int, window: str) -> list[float]:
    if sample_count < 4:
        raise ValueError("at least four samples are required")
    if window != "hann":
        raise ValueError("only the hann window is currently supported")
    return [
        0.5 - (0.5 * math.cos((2.0 * math.pi * index) / (sample_count - 1)))
        for index in range(sample_count)
    ]


def _rms(samples: Sequence[float]) -> float:
    return math.sqrt(sum(sample * sample for sample in samples) / len(samples))


class FrequencyDomainProbeR1:
    """Measure declared frequency components in an explicit sample sequence."""

    instrument_class = "bounded classical frequency-domain probe"
    schema_version = "psi42-frequency-domain-probe-v1"

    def __init__(self, config: FrequencyProbeConfig | None = None):
        self.config = config or FrequencyProbeConfig()
        self.config.validate()

    def _measure_frequency(
        self,
        samples: Sequence[float],
        weights: Sequence[float],
        frequency_hz: float,
    ) -> dict[str, Any]:
        sample_rate_hz = self.config.sample_rate_hz
        weight_total = sum(weights)
        real_projection = 0.0
        imaginary_projection = 0.0

        for index, sample in enumerate(samples):
            angle = (2.0 * math.pi * frequency_hz * index) / sample_rate_hz
            weighted_sample = float(sample) * weights[index]
            real_projection += weighted_sample * math.cos(angle)
            imaginary_projection += weighted_sample * math.sin(angle)

        real_projection /= weight_total
        imaginary_projection /= weight_total
        amplitude = 2.0 * math.hypot(real_projection, imaginary_projection)

        return {
            "frequency_hz": round(frequency_hz, 4),
            "amplitude": round(amplitude, 6),
            "power": round((amplitude * amplitude) / 2.0, 6),
            "phase_radians": round(math.atan2(-imaginary_projection, real_projection), 6),
        }

    def analyze(self, samples: Sequence[float]) -> dict[str, Any]:
        values = [float(sample) for sample in samples]
        if len(values) < 4:
            raise ValueError("at least four samples are required")

        weights = _window_weights(len(values), self.config.window)
        measurements = [
            self._measure_frequency(values, weights, frequency_hz)
            for frequency_hz in self.config.harmonic_frequencies_hz
        ]
        return {
            "schema_version": self.schema_version,
            "instrument_class": self.instrument_class,
            "sample_rate_hz": self.config.sample_rate_hz,
            "sample_count": len(values),
            "window": self.config.window,
            "harmonic_frequencies_hz": [
                round(frequency_hz, 4)
                for frequency_hz in self.config.harmonic_frequencies_hz
            ],
            "signal_rms": round(_rms(values), 6),
            "measurements": measurements,
            "authority_boundary": AUTHORITY_BOUNDARY,
        }

    @staticmethod
    def write_receipt(receipt: dict[str, Any], output_path: str | Path) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        return str(path)
