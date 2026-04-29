"""
rse_critical_regime.py

Deeper test of the phi-uniqueness claim.

Finding from baseline simulation:
    At damping = phi, all rotation constants converge equivalently because
    the power-law decay overwhelms the rotation's role.

Hypothesis:
    Phi's uniqueness should become visible as damping approaches 1 from above
    (the boundary of absolute convergence). In that critical regime, the
    uniformity of angular sampling matters more: rational rotations should show
    structured residue, while phi should remain cleanly distributed.
"""

import numpy as np

from rse_simulation import (
    PHI,
    ObserverOperator,
    convergence_diagnostics,
    gaussian_wavepacket_samples,
    rse_partial_sums,
)


def uniformity_of_angular_sampling(rotation: float, N: int = 2000) -> dict:
    """Measure how uniformly a rotation constant samples the unit circle."""

    angles = (2 * np.pi * rotation * np.arange(1, N + 1)) % (2 * np.pi)
    bins = np.linspace(0, 2 * np.pi, 37)
    counts, _ = np.histogram(angles, bins=bins)
    sorted_angles = np.sort(angles)
    gaps = np.diff(np.concatenate([[0], sorted_angles, [2 * np.pi]]))

    return {
        "max_gap": float(np.max(gaps)),
        "bin_std": float(np.std(counts)),
        "mean_bin_count": float(np.mean(counts)),
    }


def critical_damping_sweep(
    psi: np.ndarray,
    observer: ObserverOperator,
    damping_values: list[float],
    rotation_candidates: list[tuple[str, float]],
    N: int = 5000,
) -> dict:
    """At each damping level, test every rotation candidate."""

    results = {}
    for damping in damping_values:
        row = {}
        for label, rotation in rotation_candidates:
            partials = rse_partial_sums(
                psi,
                observer,
                rotation=rotation,
                damping=damping,
                N=N,
            )
            diag = convergence_diagnostics(partials)
            row[label] = diag["tail_radius"]
        results[damping] = row
    return results


if __name__ == "__main__":
    print("=" * 72)
    print(" RSE CRITICAL-REGIME PROBE — where does phi actually matter?")
    print("=" * 72)
    print()

    print("-" * 72)
    print("PART A: Pre-damping — angular sampling uniformity over N=2000 steps")
    print("-" * 72)

    candidates = [
        ("1/2 (rational)", 0.5),
        ("1/3 (rational)", 1 / 3),
        ("1/7 (rational)", 1 / 7),
        ("sqrt(2) (algebraic)", np.sqrt(2)),
        ("e (transcendental)", np.e),
        ("pi (transcendental)", np.pi),
        ("phi (noble)", PHI),
    ]

    print(f" {'constant':<28} {'max gap':>12} {'bin std':>12}")
    for label, rotation in candidates:
        u = uniformity_of_angular_sampling(rotation)
        print(f" {label:<28} {u['max_gap']:>12.4f} {u['bin_std']:>12.4f}")

    print()
    print(" Uniform ideal over 2000 samples in 36 bins: bin count ~55, low std.")
    print(" Max gap for perfectly uniform sampling on circle: ~2pi/N.")
    print()

    print("-" * 72)
    print("PART B: Tail radius across damping x rotation")
    print("-" * 72)

    psi = gaussian_wavepacket_samples(n_samples=256)
    observer = ObserverOperator(F=0.7 + 0.3j, A=0.2 - 0.1j)
    dampings = [1.01, 1.05, 1.10, 1.25, PHI, 2.00]
    sweep = critical_damping_sweep(psi, observer, dampings, candidates, N=5000)

    header = f" {'damping':<10}"
    for label, _ in candidates:
        header += f" {label[:10]:>11}"
    print(header)

    for damping in dampings:
        row = f" {damping:<10.4f}"
        for label, _ in candidates:
            val = sweep[damping][label]
            row += f" {val:>11.2e}"
        print(row)

    print()
    print("-" * 72)
    print("READ: Look for the damping regime where phi's column diverges")
    print("favorably from rational columns. That is where the")
    print("irrationality argument actually bites.")
    print("-" * 72)
