"""
rse_spiral_figure.py
Generates the key figure for the crystalline companion paper:
the spiral attractor traced under different rotation constants,
showing that phi uniquely produces a uniformly-sampled spiral.
"""

import matplotlib.pyplot as plt
import numpy as np

from rse_simulation import (
    PHI,
    ObserverOperator,
    gaussian_wavepacket_samples,
    rse_partial_sums,
)

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def main():
    psi = gaussian_wavepacket_samples(n_samples=256)
    observer = ObserverOperator(F=0.7 + 0.3j, A=0.2 - 0.1j)

    damping = 1.15
    N = 600

    candidates = [
        ("1/2 (rational)", 0.5, "#c94545"),
        ("1/3 (rational)", 1 / 3, "#d68b42"),
        ("sqrt(2) (algebraic)", np.sqrt(2), "#d4b94a"),
        ("pi (transcendental)", np.pi, "#6ba368"),
        ("phi (noble)", PHI, "#4a7ec9"),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(15, 3.4), constrained_layout=True)
    fig.suptitle(
        "Partial sums of the RSE under varying rotation constants (damping=1.15, N=600)",
        fontsize=11,
        y=1.02,
    )

    for ax, (label, rot, color) in zip(axes, candidates):
        partials = rse_partial_sums(psi, observer, rotation=rot, damping=damping, N=N)

        ax.plot(partials.real, partials.imag, color=color, linewidth=0.6, alpha=0.9)
        ax.scatter(
            [partials.real[-1]],
            [partials.imag[-1]],
            color=color,
            s=18,
            zorder=5,
            edgecolor="black",
            linewidth=0.4,
        )

        ax.scatter([0], [0], color="black", s=4, zorder=5)
        ax.set_title(label, fontsize=9)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.2, linewidth=0.4)
        ax.axhline(0, color="gray", linewidth=0.3, alpha=0.4)
        ax.axvline(0, color="gray", linewidth=0.3, alpha=0.4)
        ax.tick_params(labelsize=7)

    plt.savefig("spiral_figure.png", dpi=180, bbox_inches="tight")
    print("Saved: spiral_figure.png")

    fig2, ax2 = plt.subplots(figsize=(7, 3.5), constrained_layout=True)
    bins = np.linspace(0, 2 * np.pi, 37)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])

    for label, rot, color in candidates:
        angles = (2 * np.pi * rot * np.arange(1, 2001)) % (2 * np.pi)
        counts, _ = np.histogram(angles, bins=bins)

        ax2.plot(
            bin_centers,
            counts,
            color=color,
            label=label,
            linewidth=1.2,
            marker="o",
            markersize=2.5,
        )

    ax2.axhline(
        2000 / 36,
        color="black",
        linestyle="--",
        linewidth=0.6,
        alpha=0.5,
        label="uniform expectation",
    )

    ax2.set_xlabel("angle (rad)")
    ax2.set_ylabel("samples per bin (N=2000, 36 bins)")
    ax2.set_title("Angular distribution of phase rotation (pre-damping)")
    ax2.legend(fontsize=7, loc="upper right")
    ax2.grid(True, alpha=0.2)

    plt.savefig("angular_coverage.png", dpi=180, bbox_inches="tight")
    print("Saved: angular_coverage.png")


if __name__ == "__main__":
    main()
