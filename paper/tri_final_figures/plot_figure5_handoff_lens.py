#!/usr/bin/env python3
"""Figure 5: one experimental handoff from bound ID to executed SQLite row."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from PIL import Image

from forest_ember_palette import (
    EMBER,
    EMBER_LIGHT,
    GRID,
    INK,
    LEAF,
    LEAF_LIGHT,
    MODEL_COLORS,
    MUTED,
    NEUTRAL,
    NEUTRAL_EDGE,
    PAPER,
    PLUM,
    PLUM_LIGHT,
    TEAL,
    TEAL_LIGHT,
)


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "summary_csv" / "sqlite_model_facing_outcomes.csv"
DEFAULT_OUT = ROOT / "outputs" / "figure5_handoff_lens_v2"


def read_frozen() -> dict[str, dict[str, int]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result: dict[str, dict[str, int]] = {}
    for model in ("Qwen3.5", "GLM-5.1"):
        hits = [row for row in rows if row["model"] == model and row["controller"] == "Generic"]
        if len(hits) != 1:
            raise ValueError(f"Expected one Generic row for {model}, found {len(hits)}")
        result[model] = {key: int(hits[0][key]) for key in (
            "tasks", "correct_final_state", "core_tri_write", "fallback_wrong_write",
            "unneeded_reject", "strict_core_writes", "strict_core_opportunities",
            "stable_writes", "stable_opportunities",
        )}

    expected = {
        "Qwen3.5": {"tasks": 40, "correct_final_state": 27, "core_tri_write": 8,
                     "fallback_wrong_write": 5, "unneeded_reject": 0,
                     "strict_core_writes": 8, "strict_core_opportunities": 8,
                     "stable_writes": 0, "stable_opportunities": 4},
        "GLM-5.1": {"tasks": 40, "correct_final_state": 26, "core_tri_write": 6,
                     "fallback_wrong_write": 2, "unneeded_reject": 6,
                     "strict_core_writes": 6, "strict_core_opportunities": 8,
                     "stable_writes": 0, "stable_opportunities": 4},
    }
    if result != expected:
        raise ValueError(f"Frozen Figure 5 data changed: {result}")
    return result


def rounded(ax, x, y, w, h, *, face=PAPER, edge=NEUTRAL_EDGE, lw=0.8, radius=0.012, z=2):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.003,rounding_size={radius}",
        facecolor=face, edgecolor=edge, linewidth=lw, zorder=z,
    )
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, *, color=INK, lw=1.0, style="-|>", z=5, connection="arc3,rad=0"):
    patch = FancyArrowPatch(
        start, end, arrowstyle=style, mutation_scale=6.0, linewidth=lw, color=color,
        connectionstyle=connection, shrinkA=0, shrinkB=0, zorder=z,
    )
    ax.add_patch(patch)
    return patch


def stage(ax, x, number, label):
    ax.text(x, 0.905, number, ha="center", va="center", fontsize=4.8, weight="bold", color=PAPER,
            bbox=dict(boxstyle="circle,pad=0.18", facecolor=INK, edgecolor="none"), zorder=8)
    ax.text(x + 0.014, 0.905, label, ha="left", va="center", fontsize=4.8, weight="bold", color=INK)


def ranking(ax, x, y, *, first, second, stable):
    edge = LEAF if stable else EMBER
    pale = LEAF_LIGHT if stable else EMBER_LIGHT
    w, h = 0.170, 0.164
    rounded(ax, x, y, w, h, face=PAPER, edge=edge, lw=0.9, radius=0.011)
    ax.text(x + 0.010, y + h - 0.021, "POST-REFRESH", ha="left", va="center",
            fontsize=4.4, weight="bold", color=MUTED)
    rounded(ax, x + 0.010, y + 0.067, w - 0.020, 0.046, face=pale, edge=edge, lw=0.7, radius=0.008, z=3)
    ax.text(x + 0.021, y + 0.090, first, ha="left", va="center", fontsize=7.4, weight="bold", color=INK, zorder=5)
    ax.text(x + w - 0.017, y + 0.090, "#1", ha="right", va="center", fontsize=5.4, weight="bold", color=edge, zorder=5)
    rounded(ax, x + 0.010, y + 0.014, w - 0.020, 0.039, face=PAPER, edge=NEUTRAL, lw=0.65, radius=0.007, z=3)
    ax.text(x + 0.021, y + 0.0335, second, ha="left", va="center", fontsize=6.5, weight="bold", color=MUTED, zorder=5)
    ax.text(x + w - 0.017, y + 0.0335, "valid", ha="right", va="center", fontsize=4.9, color=MUTED, zorder=5)
    return w, h


def call(ax, x, y, target, *, stable):
    edge = LEAF if stable else EMBER
    pale = LEAF_LIGHT if stable else EMBER_LIGHT
    w, h = 0.121, 0.071
    rounded(ax, x, y, w, h, face=pale, edge=edge, lw=0.9, radius=0.011)
    ax.text(x + w / 2, y + 0.050, "MODEL CALL", ha="center", va="center", fontsize=4.6,
            weight="bold", color=edge)
    ax.text(x + w / 2, y + 0.0215, f"write({target})", ha="center", va="center", fontsize=6.0,
            family="monospace", weight="bold", color=INK)
    return w, h


def row_diff(ax, x, y, updated, *, stable):
    edge = LEAF if stable else EMBER
    pale = LEAF_LIGHT if stable else EMBER_LIGHT
    w, h = 0.143, 0.132
    rounded(ax, x, y, w, h, face=PAPER, edge=NEUTRAL_EDGE, lw=0.8, radius=0.010)
    ax.text(x + 0.009, y + h - 0.020, "ROW DIFF", ha="left", va="center", fontsize=4.9,
            weight="bold", color=INK)
    ax.plot([x + 0.008, x + w - 0.008], [y + 0.091, y + 0.091], color=GRID, lw=0.55, zorder=4)
    for idx, row in enumerate(("A", "B")):
        yy = y + 0.060 - idx * 0.038
        active = row == updated
        if active:
            rounded(ax, x + 0.008, yy - 0.014, w - 0.016, 0.029, face=pale, edge=edge,
                    lw=0.65, radius=0.006, z=3)
        ax.text(x + w / 2, yy, f"{row}  {'UPDATED' if active else 'unchanged'}",
                ha="center", va="center", fontsize=4.8,
                weight="bold" if active else "normal", color=edge if active else MUTED, zorder=5)
    return w, h


def outcome_result(ax, x, y, *, label, color, marker, fraction):
    ax.plot(
        x + 0.005,
        y,
        marker=marker,
        markersize=2.8,
        markerfacecolor=color,
        markeredgecolor=color,
        markeredgewidth=0.55,
        linestyle="none",
        zorder=7,
    )
    ax.text(x + 0.016, y, label, ha="left", va="center", fontsize=4.8,
            weight="bold", color=color)
    ax.text(0.985, y, fraction, ha="right", va="center", fontsize=5.2,
            weight="bold", color=INK)


def render(data: dict[str, dict[str, int]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 6.0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })

    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    fig.patch.set_facecolor(PAPER)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.018, 0.982, "BOUND TARGET  →  EXECUTED ROW", ha="left", va="top",
            fontsize=6.8, weight="bold", color=INK)

    stage(ax, 0.027, "1", "BIND")
    stage(ax, 0.188, "2", "REFRESH")
    stage(ax, 0.345, "3", "RANK")
    stage(ax, 0.548, "4", "GATE")
    stage(ax, 0.673, "5", "CALL")
    stage(ax, 0.810, "6", "DIFF + RESULT")

    # Shared setup.
    rounded(ax, 0.026, 0.444, 0.126, 0.196, face=TEAL_LIGHT, edge=TEAL, lw=0.9, radius=0.013)
    ax.text(0.089, 0.611, "BOUND ID", ha="center", va="center", fontsize=4.9, weight="bold", color=TEAL)
    ax.add_patch(Circle((0.089, 0.544), 0.033, facecolor=PAPER, edgecolor=TEAL, linewidth=1.0, zorder=4))
    ax.text(0.089, 0.544, "A", ha="center", va="center", fontsize=8.8, weight="bold", color=INK, zorder=5)
    ax.text(0.089, 0.485, "correct", ha="center", va="center", fontsize=5.8, weight="bold", color=INK)
    ax.text(0.089, 0.463, "pre-refresh", ha="center", va="center", fontsize=4.8, color=MUTED)

    ax.add_patch(Circle((0.224, 0.544), 0.046, facecolor=PLUM_LIGHT, edgecolor=PLUM, linewidth=0.95, zorder=3))
    ax.text(0.224, 0.554, "refresh", ha="center", va="center", fontsize=5.8, weight="bold", color=INK)
    ax.text(0.224, 0.527, "rank may flip", ha="center", va="center", fontsize=4.5, color=MUTED)
    arrow(ax, (0.152, 0.544), (0.178, 0.544), color=INK, lw=0.9)

    # The narrow gate is the experiment's focal connection.
    ax.axvspan(0.540, 0.558, ymin=0.225, ymax=0.805, color=GRID, alpha=0.35, zorder=0)
    ax.plot([0.549, 0.549], [0.235, 0.792], color=NEUTRAL_EDGE, lw=0.7, linestyle=(0, (2.5, 2.5)), zorder=1)

    # Refresh fans out into matched Stable and Changed conditions.
    arrow(ax, (0.270, 0.544), (0.319, 0.681), color=LEAF, lw=1.05, connection="arc3,rad=-0.12")
    arrow(ax, (0.270, 0.544), (0.319, 0.385), color=EMBER, lw=1.15, connection="arc3,rad=0.12")

    # Stable control lane.
    ax.text(0.319, 0.808, "STABLE CONTROL", ha="left", va="center", fontsize=5.7, weight="bold", color=LEAF)
    ranking(ax, 0.319, 0.592, first="A", second="B", stable=True)
    arrow(ax, (0.489, 0.674), (0.535, 0.674), color=LEAF, lw=1.25)
    arrow(ax, (0.558, 0.674), (0.581, 0.674), color=LEAF, lw=1.25)
    call(ax, 0.581, 0.638, "A", stable=True)
    arrow(ax, (0.702, 0.674), (0.724, 0.674), color=LEAF, lw=1.25)
    row_diff(ax, 0.724, 0.608, "A", stable=True)
    ax.text(0.985, 0.750, "WRONG-TARGET WRITES", ha="right", va="center", fontsize=4.1,
            weight="bold", color=MUTED)
    outcome_result(ax, 0.870, 0.718, label="Qwen", color=MODEL_COLORS["Qwen"], marker="o", fraction="0/4")
    outcome_result(ax, 0.870, 0.691, label="GLM", color=MODEL_COLORS["GLM"], marker="s", fraction="0/4")

    # Changed lane. The preserved ID and refreshed winner disagree at the handoff gate.
    ax.text(0.319, 0.514, "CHANGED WINNER", ha="left", va="center", fontsize=5.3, weight="bold", color=EMBER)
    ranking(ax, 0.319, 0.304, first="B", second="A", stable=False)
    arrow(ax, (0.489, 0.386), (0.535, 0.386), color=EMBER, lw=1.4)
    arrow(ax, (0.558, 0.386), (0.581, 0.386), color=EMBER, lw=1.4)
    call(ax, 0.581, 0.350, "B", stable=False)
    arrow(ax, (0.702, 0.386), (0.724, 0.386), color=EMBER, lw=1.4)
    row_diff(ax, 0.724, 0.320, "B", stable=False)

    # The compiled ID thread reaches the handoff but is not used by Generic.
    arrow(ax, (0.104, 0.501), (0.300, 0.263), color=PLUM, lw=1.05, style="-",
          connection="arc3,rad=0.08", z=2)
    arrow(ax, (0.300, 0.263), (0.385, 0.263), color=PLUM, lw=1.05, style="-", z=2)
    rounded(ax, 0.385, 0.246, 0.139, 0.035, face=PLUM_LIGHT, edge=PLUM, lw=0.65, radius=0.007, z=4)
    ax.text(0.4545, 0.2635, "bound ID = A", ha="center", va="center", fontsize=4.9,
            weight="bold", color=PLUM, zorder=5)
    ax.plot([0.542, 0.556], [0.275, 0.289], color=EMBER, lw=1.25, zorder=8)
    ax.plot([0.556, 0.542], [0.275, 0.289], color=EMBER, lw=1.25, zorder=8)
    ax.text(0.549, 0.226, "ID-to-action handoff breaks", ha="center", va="center",
            fontsize=5.2, weight="bold", color=EMBER)

    ax.text(0.985, 0.300, "STRICT WRONG-TARGET", ha="right", va="center", fontsize=4.1,
            weight="bold", color=MUTED)
    outcome_result(ax, 0.870, 0.268, label="Qwen", color=MODEL_COLORS["Qwen"], marker="o", fraction="8/8")
    outcome_result(ax, 0.870, 0.241, label="GLM", color=MODEL_COLORS["GLM"], marker="s", fraction="6/8")

    ax.plot([0.026, 0.978], [0.166, 0.166], color=GRID, lw=0.65)
    ax.text(0.500, 0.130,
            "40 tasks/model · strict matched subsets shown on their execution paths",
            ha="center", va="center", fontsize=4.8, color=MUTED)
    ax.text(0.500, 0.085,
            "Fractions = wrong-target writes / strict opportunities · not prevalence",
            ha="center", va="center", fontsize=4.7, color=MUTED)

    fig.subplots_adjust(left=0.008, right=0.992, bottom=0.02, top=0.995)
    stem = output_dir / "figure5_handoff_lens"
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.01)
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.01)
    fig.savefig(stem.with_suffix(".png"), dpi=400, bbox_inches="tight", pad_inches=0.01)
    plt.close(fig)

    png = Image.open(stem.with_suffix(".png")).convert("RGB")
    png.convert("L").save(output_dir / "figure5_handoff_lens-grayscale.png")
    cvd = png.copy()
    pixels = cvd.load()
    for yy in range(cvd.height):
        for xx in range(cvd.width):
            red, green, blue = pixels[xx, yy]
            pixels[xx, yy] = (
                int(0.625 * red + 0.375 * green),
                int(0.700 * red + 0.300 * green),
                int(0.300 * green + 0.700 * blue),
            )
    cvd.save(output_dir / "figure5_handoff_lens-deuteranopia.png")

    manifest = {
        "data": str(DATA.relative_to(ROOT)),
        "strict_stable": {"Qwen": "0/4", "GLM": "0/4"},
        "strict_changed": {"Qwen": "8/8", "GLM": "6/8"},
        "full_40_task_context": {
            "Qwen": {"correct": 27, "tri": 8, "fallback": 5, "reject": 0},
            "GLM": {"correct": 26, "tri": 6, "fallback": 2, "reject": 6},
        },
        "visual_claim": "The changed-winner failure occurs at the compiled-ID to model-call handoff.",
        "result_encoding": "model shape + exact wrong-target-write fraction",
    }
    (output_dir / "figure5_handoff_lens-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    render(read_frozen(), args.output_dir)
    print(args.output_dir)


if __name__ == "__main__":
    main()
