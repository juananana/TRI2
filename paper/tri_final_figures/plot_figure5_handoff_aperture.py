#!/usr/bin/env python3
"""Figure 5 candidate: expose the bound-ID to model-call handoff directly."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
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
DEFAULT_OUT = ROOT / "outputs" / "figure5_handoff_aperture_v1"

LEAF_TEXT = "#3D7D60"
EMBER_TEXT = "#B84A32"
PLUM_TEXT = "#705873"


def read_frozen() -> dict[str, dict[str, int]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result: dict[str, dict[str, int]] = {}
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
    for model in ("Qwen3.5", "GLM-5.1"):
        hit = [row for row in rows if row["model"] == model and row["controller"] == "Generic"]
        if len(hit) != 1:
            raise ValueError(f"Expected one Generic row for {model}, found {len(hit)}")
        result[model] = {key: int(hit[0][key]) for key in keys}

    expected = {
        "Qwen3.5": {
            "tasks": 40,
            "correct_final_state": 27,
            "core_tri_write": 8,
            "fallback_wrong_write": 5,
            "unneeded_reject": 0,
            "strict_core_writes": 8,
            "strict_core_opportunities": 8,
            "stable_writes": 0,
            "stable_opportunities": 4,
        },
        "GLM-5.1": {
            "tasks": 40,
            "correct_final_state": 26,
            "core_tri_write": 6,
            "fallback_wrong_write": 2,
            "unneeded_reject": 6,
            "strict_core_writes": 6,
            "strict_core_opportunities": 8,
            "stable_writes": 0,
            "stable_opportunities": 4,
        },
    }
    if result != expected:
        raise ValueError(f"Frozen Figure 5 data changed: {result}")
    return result


def rounded(ax, x, y, w, h, *, face=PAPER, edge=NEUTRAL_EDGE, lw=0.8, radius=0.012, z=2):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.002,rounding_size={radius}",
        facecolor=face,
        edgecolor=edge,
        linewidth=lw,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def arrow(ax, start, end, *, color=INK, lw=1.0, style="-|>", z=4, connection="arc3,rad=0"):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=6.0,
        linewidth=lw,
        color=color,
        connectionstyle=connection,
        shrinkA=0,
        shrinkB=0,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def token(ax, x, y, text, *, face, edge, radius=0.027, lw=0.9, text_color=INK, z=6):
    ax.add_patch(Circle((x, y), radius, facecolor=face, edgecolor=edge, linewidth=lw, zorder=z))
    ax.text(x, y, text, ha="center", va="center", fontsize=7.0, weight="bold", color=text_color, zorder=z + 1)


def ranking(ax, x, y, *, first, second, changed):
    primary = EMBER if changed else LEAF
    primary_text = EMBER_TEXT if changed else LEAF_TEXT
    pale = EMBER_LIGHT if changed else LEAF_LIGHT
    token(ax, x, y, first, face=pale, edge=primary, radius=0.026)
    ax.text(x, y + 0.047, "#1", ha="center", va="center", fontsize=7.0, weight="bold", color=primary_text)
    token(ax, x + 0.076, y, second, face=PAPER, edge=PLUM if changed else NEUTRAL_EDGE, radius=0.023)
    ax.text(
        x + 0.076,
        y - 0.047,
        "still valid" if changed else "#2",
        ha="center",
        va="center",
        fontsize=7.0,
        color=PLUM_TEXT if changed else MUTED,
    )


def aperture(ax, y, *, sent, stable):
    color = LEAF if stable else EMBER
    pale = LEAF_LIGHT if stable else EMBER_LIGHT
    # Two posts make the identity/action boundary visible without enclosing the lane.
    rounded(ax, 0.574, y - 0.068, 0.018, 0.136, face=TEAL_LIGHT, edge=TEAL, lw=0.75, radius=0.004, z=2)
    rounded(ax, 0.626, y - 0.068, 0.018, 0.136, face=TEAL_LIGHT, edge=TEAL, lw=0.75, radius=0.004, z=2)
    arrow(ax, (0.522, y), (0.607, y), color=color, lw=1.6, z=4)
    token(ax, 0.610, y, sent, face=pale, edge=color, radius=0.023, lw=1.0, z=7)
    arrow(ax, (0.633, y), (0.688, y), color=color, lw=1.6, z=4)


def row_diff(ax, x, y, *, updated, stable):
    edge = LEAF if stable else EMBER
    semantic_text = LEAF_TEXT if stable else EMBER_TEXT
    pale = LEAF_LIGHT if stable else EMBER_LIGHT
    w, h = 0.102, 0.130
    rounded(ax, x, y - h / 2, w, h, face=PAPER, edge=NEUTRAL_EDGE, lw=0.75, radius=0.008)
    for index, row in enumerate(("A", "B")):
        yy = y + 0.029 - index * 0.058
        if row == updated:
            rounded(ax, x + 0.006, yy - 0.022, w - 0.012, 0.044, face=pale, edge=edge, lw=0.65, radius=0.005, z=3)
        ax.text(
            x + w / 2,
            yy,
            row,
            ha="center",
            va="center",
            fontsize=7.0,
            weight="bold" if row == updated else "normal",
            color=semantic_text if row == updated else MUTED,
            zorder=5,
        )


def model_counts(ax, y, qwen, glm):
    q_color = MODEL_COLORS["Qwen"]
    g_color = MODEL_COLORS["GLM"]
    q_y = y - 0.095
    g_y = y - 0.135
    ax.plot(0.765, q_y, marker="o", markersize=3.0, color=q_color, linestyle="none", zorder=6)
    ax.text(0.780, q_y, f"Qwen {qwen}", ha="left", va="center", fontsize=7.0, color=INK, weight="bold")
    ax.plot(0.765, g_y, marker="s", markersize=2.9, color=g_color, linestyle="none", zorder=6)
    ax.text(0.780, g_y, f"GLM {glm}", ha="left", va="center", fontsize=7.0, color=INK, weight="bold")


def render(data: dict[str, dict[str, int]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )

    fig, ax = plt.subplots(figsize=(3.35, 2.55))
    fig.patch.set_facecolor(PAPER)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Compact reading headers. The central handoff receives the strongest emphasis.
    headers = (
        (0.083, "BOUND ID"),
        (0.353, "POST-REFRESH"),
        (0.610, "HANDOFF"),
        (0.835, "EXECUTION"),
    )
    for x, label in headers:
        ax.text(x, 0.958, label, ha="center", va="center", fontsize=7.0, weight="bold", color=INK)
    ax.plot([0.018, 0.982], [0.917, 0.917], color=GRID, lw=0.7)

    # One shared pre-refresh binding and refresh intervention.
    token(ax, 0.083, 0.520, "A", face=TEAL_LIGHT, edge=TEAL, radius=0.043, lw=1.0)
    ax.text(0.083, 0.445, "correct\nbinding", ha="center", va="center", fontsize=7.0, color=MUTED, linespacing=0.88)
    arrow(ax, (0.126, 0.520), (0.177, 0.520), color=INK, lw=0.9)
    ax.add_patch(Circle((0.229, 0.520), 0.052, facecolor=PLUM_LIGHT, edgecolor=PLUM, linewidth=0.9, zorder=4))
    ax.text(0.229, 0.531, "refresh", ha="center", va="center", fontsize=7.0, weight="bold", color=INK, zorder=5)
    ax.text(0.229, 0.495, "rank", ha="center", va="center", fontsize=7.0, color=MUTED, zorder=5)

    # Stable and changed winner conditions fan out from the same setup.
    stable_y, changed_y = 0.710, 0.310
    arrow(ax, (0.275, 0.543), (0.305, stable_y), color=LEAF, lw=1.0, connection="arc3,rad=-0.12")
    arrow(ax, (0.275, 0.497), (0.305, changed_y), color=EMBER, lw=1.2, connection="arc3,rad=0.12")
    ax.text(0.287, 0.826, "STABLE CONTROL", ha="left", va="center", fontsize=7.0, weight="bold", color=LEAF_TEXT)
    ax.text(0.287, 0.423, "CHANGED WINNER", ha="left", va="center", fontsize=7.0, weight="bold", color=EMBER_TEXT)
    ranking(ax, 0.333, stable_y, first="A", second="B", changed=False)
    ranking(ax, 0.333, changed_y, first="B", second="A", changed=True)

    # Stable: the bound ID and current winner coincide at the handoff.
    arrow(ax, (0.435, stable_y), (0.522, stable_y), color=LEAF, lw=1.3)
    aperture(ax, stable_y, sent="A", stable=True)
    ax.text(0.610, 0.796, "same ID passes", ha="center", va="center", fontsize=7.0, weight="bold", color=LEAF_TEXT)
    ax.text(0.696, stable_y + 0.050, "write(A)", ha="center", va="center", fontsize=7.0, family="monospace", weight="bold", color=INK)
    arrow(ax, (0.688, stable_y), (0.768, stable_y), color=LEAF, lw=1.3)
    row_diff(ax, 0.770, stable_y, updated="A", stable=True)
    model_counts(ax, stable_y, "0/4", "0/4")

    # Changed: refreshed winner B is sent while the still-valid bound A stops at the boundary.
    arrow(ax, (0.359, changed_y), (0.522, changed_y), color=EMBER, lw=1.5)
    aperture(ax, changed_y, sent="B", stable=False)
    ax.text(0.696, changed_y + 0.050, "write(B)", ha="center", va="center", fontsize=7.0, family="monospace", weight="bold", color=INK)
    arrow(ax, (0.688, changed_y), (0.768, changed_y), color=EMBER, lw=1.5)
    row_diff(ax, 0.770, changed_y, updated="B", stable=False)
    model_counts(ax, changed_y, "8/8", "6/8")

    # The expected bound-ID channel approaches the same aperture but is not handed to the call.
    arrow(ax, (0.432, 0.300), (0.486, 0.195), color=PLUM, lw=1.05, style="-", connection="arc3,rad=0.22", z=2)
    arrow(ax, (0.486, 0.195), (0.571, 0.195), color=PLUM, lw=1.05, style="-", z=2)
    token(ax, 0.548, 0.195, "A", face=PAPER, edge=PLUM, radius=0.020, lw=0.9, z=5)
    ax.plot([0.578, 0.592], [0.181, 0.209], color=EMBER, lw=1.25, zorder=8)
    ax.plot([0.592, 0.578], [0.181, 0.209], color=EMBER, lw=1.25, zorder=8)
    ax.text(0.450, 0.105, "bound A not sent", ha="center", va="center", fontsize=7.0, weight="bold", color=PLUM_TEXT)
    ax.text(0.680, 0.105, "B sent", ha="center", va="center", fontsize=7.0, weight="bold", color=EMBER_TEXT)
    ax.text(0.552, 0.045, "handoff mismatch", ha="center", va="center", fontsize=7.0, weight="bold", color=EMBER_TEXT)

    fig.subplots_adjust(left=0.008, right=0.992, bottom=0.02, top=0.995)
    stem = output_dir / "figure5_handoff_aperture"
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.012)
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.012)
    fig.savefig(stem.with_suffix(".png"), dpi=400, bbox_inches="tight", pad_inches=0.012)
    plt.close(fig)

    png = Image.open(stem.with_suffix(".png")).convert("RGB")
    png.convert("L").save(output_dir / "figure5_handoff_aperture-grayscale.png")
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
    cvd.save(output_dir / "figure5_handoff_aperture-deuteranopia.png")

    manifest = {
        "data": str(DATA.relative_to(ROOT)),
        "structure": "single handoff aperture with Stable and Changed execution lanes",
        "size_inches": [3.35, 2.55],
        "minimum_text_pt": 7.0,
        "strict_stable": {"Qwen": "0/4", "GLM": "0/4"},
        "strict_changed": {"Qwen": "8/8", "GLM": "6/8"},
        "full_40_task_context": {
            "Qwen": {"correct": 27, "tri": 8, "fallback": 5, "reject": 0},
            "GLM": {"correct": 26, "tri": 6, "fallback": 2, "reject": 6},
        },
        "visual_claim": "In Changed cases, Generic passes refreshed winner B into the model call while bound A remains valid.",
        "result_encoding": "direct execution path plus model shape and exact strict fraction",
        "semantic_text_contrast_on_white": {
            "stable": {"color": LEAF_TEXT, "ratio": 4.88},
            "changed": {"color": EMBER_TEXT, "ratio": 5.17},
            "bound_id": {"color": PLUM_TEXT, "ratio": 6.30},
            "ink": {"color": INK, "ratio": 9.56},
        },
    }
    (output_dir / "figure5_handoff_aperture-manifest.json").write_text(
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
