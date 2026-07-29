#!/usr/bin/env python3
"""Draw Figure 5 as one binding-to-write experimental handoff.

The figure intentionally avoids a separate outcome panel. Stable and changed
evidence is attached to the exact execution path that produced it.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, PathPatch
from matplotlib.path import Path as MplPath
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
DEFAULT_OUT = ROOT / "outputs" / "figure5_binding_to_write_handoff_v1"


def read_frozen() -> dict[str, dict[str, int]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    result: dict[str, dict[str, int]] = {}
    for model in ("Qwen3.5", "GLM-5.1"):
        selected = [r for r in rows if r["model"] == model and r["controller"] == "Generic"]
        if len(selected) != 1:
            raise ValueError(f"Expected one Generic row for {model}, found {len(selected)}")
        row = selected[0]
        result[model] = {key: int(row[key]) for key in (
            "tasks",
            "correct_final_state",
            "core_tri_write",
            "fallback_wrong_write",
            "unneeded_reject",
            "strict_core_writes",
            "strict_core_opportunities",
            "stable_writes",
            "stable_opportunities",
        )}

    expected = {
        "Qwen3.5": (40, 27, 8, 5, 0, 8, 8, 0, 4),
        "GLM-5.1": (40, 26, 6, 2, 6, 6, 8, 0, 4),
    }
    keys = (
        "tasks",
        "correct_final_state",
        "core_tri_write",
        "fallback_wrong_write",
        "unneeded_reject",
        "strict_core_writes",
        "strict_core_opportunities",
        "stable_writes",
        "stable_opportunities",
    )
    for model, values in expected.items():
        actual = tuple(result[model][key] for key in keys)
        if actual != values:
            raise ValueError(f"Frozen Figure 5 data changed for {model}: {actual} != {values}")
    return result


def box(ax, x, y, w, h, *, face=PAPER, edge=NEUTRAL_EDGE, lw=0.9, radius=0.018, z=2):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=face, edgecolor=edge, linewidth=lw, zorder=z,
    )
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, *, color=INK, lw=1.15, style="-|>", z=3, connection="arc3,rad=0"):
    patch = FancyArrowPatch(
        start, end,
        arrowstyle=style,
        mutation_scale=7.5,
        linewidth=lw,
        color=color,
        connectionstyle=connection,
        shrinkA=0,
        shrinkB=0,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def stage_label(ax, x, number, label):
    ax.text(x, 0.875, number, ha="center", va="center", fontsize=6.8, weight="bold", color=PAPER,
            bbox=dict(boxstyle="circle,pad=0.22", facecolor=INK, edgecolor="none"), zorder=8)
    ax.text(x + 0.018, 0.875, label, ha="left", va="center", fontsize=6.6, weight="bold", color=INK)


def rank_card(ax, x, y, *, winner: str, second: str, stable: bool):
    w, h = 0.174, 0.172
    edge = LEAF if stable else EMBER
    fill = LEAF_LIGHT if stable else EMBER_LIGHT
    box(ax, x, y, w, h, face=PAPER, edge=edge, lw=1.0, radius=0.015)
    ax.text(x + 0.012, y + h - 0.024, "REFRESHED RANKING", ha="left", va="center",
            fontsize=5.8, weight="bold", color=MUTED)
    box(ax, x + 0.012, y + 0.073, w - 0.024, 0.047, face=fill, edge=edge, lw=0.8, radius=0.012, z=3)
    ax.text(x + 0.026, y + 0.096, winner, ha="left", va="center", fontsize=8.5, weight="bold", color=INK, zorder=5)
    ax.text(x + w - 0.020, y + 0.096, "winner", ha="right", va="center", fontsize=5.9,
            weight="bold", color=edge, zorder=5)
    box(ax, x + 0.012, y + 0.017, w - 0.024, 0.040, face=PAPER, edge=NEUTRAL, lw=0.7, radius=0.010, z=3)
    ax.text(x + 0.026, y + 0.037, second, ha="left", va="center", fontsize=7.3, weight="bold", color=MUTED, zorder=5)
    ax.text(x + w - 0.020, y + 0.037, "still valid", ha="right", va="center", fontsize=5.6, color=MUTED, zorder=5)
    return x + w, y + h / 2


def write_call(ax, x, y, target, *, stable):
    edge = LEAF if stable else EMBER
    face = LEAF_LIGHT if stable else EMBER_LIGHT
    box(ax, x, y, 0.128, 0.067, face=face, edge=edge, lw=1.0, radius=0.015)
    ax.text(x + 0.064, y + 0.043, "MODEL CALL", ha="center", va="center", fontsize=5.5,
            weight="bold", color=edge)
    ax.text(x + 0.064, y + 0.020, f"write(id={target})", ha="center", va="center", fontsize=6.8,
            family="monospace", weight="bold", color=INK)
    return x + 0.128, y + 0.0335


def sqlite_diff(ax, x, y, updated, *, stable):
    edge = LEAF if stable else EMBER
    fill = LEAF_LIGHT if stable else EMBER_LIGHT
    w, h = 0.154, 0.128
    box(ax, x, y, w, h, face=PAPER, edge=NEUTRAL_EDGE, lw=0.9, radius=0.012)
    ax.text(x + 0.010, y + h - 0.020, "SQLITE DIFF", ha="left", va="center", fontsize=5.7,
            weight="bold", color=INK)
    ax.plot([x + 0.008, x + w - 0.008], [y + 0.086, y + 0.086], color=GRID, lw=0.65, zorder=4)
    for idx, row in enumerate(("A", "B")):
        yy = y + 0.052 - idx * 0.037
        is_updated = row == updated
        if is_updated:
            box(ax, x + 0.008, yy - 0.014, w - 0.016, 0.030, face=fill, edge=edge, lw=0.75, radius=0.008, z=3)
        ax.text(x + 0.018, yy, f"row {row}", ha="left", va="center", fontsize=6.5,
                weight="bold" if is_updated else "normal", color=INK if is_updated else MUTED, zorder=5)
        ax.text(x + w - 0.014, yy, "UPDATED" if is_updated else "unchanged", ha="right", va="center",
                fontsize=5.5, weight="bold" if is_updated else "normal", color=edge if is_updated else MUTED, zorder=5)
    return x, y, w, h


def pips(ax, x, y, *, label, color, filled, total, suffix):
    ax.text(x, y, label, ha="left", va="center", fontsize=6.1, weight="bold", color=color)
    start = x + 0.057
    gap = 0.0115
    for idx in range(total):
        ax.add_patch(Circle(
            (start + idx * gap, y), 0.0040,
            facecolor=color if idx < filled else PAPER,
            edgecolor=color,
            linewidth=0.75,
            zorder=6,
        ))
    ax.text(start + total * gap + 0.002, y, suffix, ha="left", va="center", fontsize=6.0,
            weight="bold", color=INK)


def commitment_curve(ax):
    # The compiled ID survives refresh; the Generic path below follows the new winner instead.
    verts = [(0.135, 0.606), (0.235, 0.570), (0.335, 0.420), (0.397, 0.395)]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4]
    path = PathPatch(MplPath(verts, codes), facecolor="none", edgecolor=PLUM, lw=1.4,
                     linestyle=(0, (3, 2)), zorder=1)
    ax.add_patch(path)
    ax.text(0.245, 0.505, "compiled ID = A", ha="center", va="center", fontsize=6.0,
            weight="bold", color=PLUM, rotation=-17)


def render(data: dict[str, dict[str, int]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 7.0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.unicode_minus": False,
    })

    fig, ax = plt.subplots(figsize=(3.35, 2.58))
    fig.patch.set_facecolor(PAPER)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.018, 0.957, "The binding-to-write handoff", ha="left", va="center",
            fontsize=9.0, weight="bold", color=INK)
    ax.text(0.018, 0.914, "same Generic controller · correct initial binding · old target remains valid",
            ha="left", va="center", fontsize=5.9, color=MUTED)

    stage_label(ax, 0.040, "1", "BIND")
    stage_label(ax, 0.220, "2", "REFRESH")
    stage_label(ax, 0.390, "3", "RANKING")
    stage_label(ax, 0.620, "4", "WRITE")
    stage_label(ax, 0.812, "5", "OBSERVE")

    # Shared pre-refresh setup.
    box(ax, 0.022, 0.538, 0.143, 0.190, face=TEAL_LIGHT, edge=TEAL, lw=1.0, radius=0.018)
    ax.text(0.0935, 0.696, "PRE-REFRESH", ha="center", va="center", fontsize=5.7, weight="bold", color=TEAL)
    ax.add_patch(Circle((0.0935, 0.632), 0.034, facecolor=PAPER, edgecolor=TEAL, linewidth=1.2, zorder=4))
    ax.text(0.0935, 0.632, "A", ha="center", va="center", fontsize=10, weight="bold", color=INK, zorder=5)
    ax.text(0.0935, 0.575, "correctly bound", ha="center", va="center", fontsize=6.1, weight="bold", color=INK)
    ax.text(0.0935, 0.552, "before refresh", ha="center", va="center", fontsize=5.6, color=MUTED)

    # Refresh lens. Its split is the experimental intervention, not decoration.
    ax.add_patch(Circle((0.246, 0.633), 0.055, facecolor=PLUM_LIGHT, edgecolor=PLUM, linewidth=1.05, zorder=3))
    ax.text(0.246, 0.647, "refresh", ha="center", va="center", fontsize=7.0, weight="bold", color=INK)
    ax.text(0.246, 0.616, "ranking may flip", ha="center", va="center", fontsize=5.3, color=MUTED)
    arrow(ax, (0.165, 0.633), (0.190, 0.633), color=INK, lw=1.1)
    arrow(ax, (0.301, 0.633), (0.337, 0.633), color=INK, lw=1.1)

    commitment_curve(ax)

    # Stable control: a narrow reference lane.
    ax.text(0.350, 0.793, "STABLE CONTROL", ha="left", va="center", fontsize=6.4, weight="bold", color=LEAF)
    ax.text(0.487, 0.793, "winner stays A", ha="left", va="center", fontsize=5.6, color=MUTED)
    rank_card(ax, 0.350, 0.592, winner="A", second="B", stable=True)
    arrow(ax, (0.524, 0.678), (0.565, 0.678), color=LEAF, lw=1.45)
    write_call(ax, 0.565, 0.644, "A", stable=True)
    arrow(ax, (0.693, 0.678), (0.724, 0.678), color=LEAF, lw=1.45)
    sqlite_diff(ax, 0.724, 0.614, "A", stable=True)
    ax.text(0.902, 0.756, "wrong-target writes", ha="center", va="center", fontsize=5.5, color=MUTED)
    pips(ax, 0.828, 0.727, label="Qwen", color=MODEL_COLORS["Qwen"], filled=0, total=4, suffix="0/4")
    pips(ax, 0.828, 0.701, label="GLM", color=MODEL_COLORS["GLM"], filled=0, total=4, suffix="0/4")

    # Changed winner: the commitment and current ranking diverge at this exact handoff.
    ax.text(0.350, 0.510, "CHANGED WINNER", ha="left", va="center", fontsize=6.4, weight="bold", color=EMBER)
    ax.text(0.488, 0.510, "B rises; A is still valid", ha="left", va="center", fontsize=5.6, color=MUTED)
    rank_card(ax, 0.350, 0.278, winner="B", second="A", stable=False)
    box(ax, 0.378, 0.239, 0.118, 0.029, face=PLUM_LIGHT, edge=PLUM, lw=0.75, radius=0.009, z=4)
    ax.text(0.437, 0.2535, "expected: write A", ha="center", va="center", fontsize=5.6,
            weight="bold", color=PLUM, zorder=5)
    arrow(ax, (0.524, 0.364), (0.565, 0.364), color=EMBER, lw=1.65)
    write_call(ax, 0.565, 0.330, "B", stable=False)
    arrow(ax, (0.693, 0.364), (0.724, 0.364), color=EMBER, lw=1.65)
    sqlite_diff(ax, 0.724, 0.300, "B", stable=False)

    # Make the failed connection explicit: the actual call follows B, not the carried ID A.
    ax.plot([0.530, 0.550], [0.253, 0.253], color=PLUM, lw=1.0, linestyle=(0, (3, 2)), zorder=3)
    ax.plot([0.550, 0.550], [0.253, 0.330], color=PLUM, lw=1.0, linestyle=(0, (3, 2)), zorder=3)
    ax.plot([0.543, 0.557], [0.287, 0.299], color=EMBER, lw=1.25, zorder=5)
    ax.plot([0.557, 0.543], [0.287, 0.299], color=EMBER, lw=1.25, zorder=5)
    ax.text(0.550, 0.216, "handoff breaks here", ha="center", va="center", fontsize=5.7,
            weight="bold", color=EMBER)

    ax.text(0.886, 0.275, "strict wrong-target writes", ha="center", va="center", fontsize=5.5, color=MUTED)
    qwen = data["Qwen3.5"]
    glm = data["GLM-5.1"]
    pips(ax, 0.786, 0.244, label="Qwen", color=MODEL_COLORS["Qwen"],
         filled=qwen["strict_core_writes"], total=qwen["strict_core_opportunities"], suffix="8/8")
    pips(ax, 0.786, 0.214, label="GLM", color=MODEL_COLORS["GLM"],
         filled=glm["strict_core_writes"], total=glm["strict_core_opportunities"], suffix="6/8")

    # One-line scope boundary; the 40-task partition remains in text/caption.
    ax.plot([0.022, 0.978], [0.148, 0.148], color=GRID, lw=0.7)
    ax.text(0.022, 0.111, "Controlled SQLite trajectories", ha="left", va="center",
            fontsize=5.8, weight="bold", color=INK)
    ax.text(0.236, 0.111, "40 tasks/model · strict changed subset shown above · no prevalence claim",
            ha="left", va="center", fontsize=5.5, color=MUTED)
    ax.text(0.978, 0.047,
            "Filled dots = wrong-target writes; open dots = no wrong-target write.",
            ha="right", va="center", fontsize=5.35, color=MUTED)

    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.015, top=0.99)
    stem = output_dir / "figure5_binding_to_write_handoff"
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.015)
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.015)
    fig.savefig(stem.with_suffix(".png"), dpi=400, bbox_inches="tight", pad_inches=0.015)
    plt.close(fig)

    png = Image.open(stem.with_suffix(".png")).convert("RGB")
    png.convert("L").save(output_dir / "figure5_binding_to_write_handoff-grayscale.png")

    # Simple deuteranopia simulation for a redundant-encoding sanity check.
    pixels = png.load()
    for yy in range(png.height):
        for xx in range(png.width):
            r, g, b = pixels[xx, yy]
            pixels[xx, yy] = (
                int(0.625 * r + 0.375 * g),
                int(0.700 * r + 0.300 * g),
                int(0.300 * g + 0.700 * b),
            )
    png.save(output_dir / "figure5_binding_to_write_handoff-deuteranopia.png")

    manifest = {
        "source": str(DATA.relative_to(ROOT)),
        "controller": "Generic",
        "tasks_per_model": 40,
        "strict": {
            "stable": {"Qwen": "0/4", "GLM": "0/4"},
            "changed": {"Qwen": "8/8", "GLM": "6/8"},
        },
        "full_40_task_context": {
            "Qwen": {"correct": 27, "tri": 8, "fallback": 5, "reject": 0},
            "GLM": {"correct": 26, "tri": 6, "fallback": 2, "reject": 6},
        },
        "claim_boundary": "Controlled model-issued SQLite writes; not a prevalence estimate.",
    }
    (output_dir / "figure5_binding_to_write_handoff-manifest.json").write_text(
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
