#!/usr/bin/env python3
"""Figure 5: full SQLite outcomes and the strict Stable/Changed contrast."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from math import sqrt
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from PIL import Image

from forest_ember_palette import (
    EMBER,
    EMBER_LIGHT,
    GRID,
    INK,
    MODEL_COLORS,
    MUTED,
    NEUTRAL,
    NEUTRAL_EDGE,
    PAPER,
    TEAL,
)


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "summary_csv" / "sqlite_model_facing_outcomes.csv"
DEFAULT_STEM = (
    ROOT
    / "outputs"
    / "figure5_figure4_aligned_v1"
    / "figure5_full_outcomes_strict_contrast"
)
DEFAULT_RIGHT_STEM = (
    ROOT
    / "outputs"
    / "figure5_figure4_aligned_v1"
    / "figure5_right_strict_contrast"
)
DEFAULT_BAR_STEM = (
    ROOT
    / "outputs"
    / "figure5_grouped_bars_v2"
    / "figure5_right_grouped_bars"
)

MODELS = (
    ("Qwen3.5", "Qwen", "o", MODEL_COLORS["Qwen"]),
    ("GLM-5.1", "GLM", "s", MODEL_COLORS["GLM"]),
)

OUTCOMES = (
    ("correct_final_state", "Correct final", TEAL, None),
    ("core_tri_write", "Strict B write", EMBER, "////"),
    ("fallback_wrong_write", "Fallback B write", "#F1A464", "...."),
    ("unneeded_reject", "Reject", NEUTRAL, "\\\\"),
)

EXPECTED = {
    "Qwen3.5": (40, 27, 8, 5, 0, 8, 8, 0, 4),
    "GLM-5.1": (40, 26, 6, 2, 6, 6, 8, 0, 4),
}

FIELDS = (
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


def read_frozen() -> dict[str, dict[str, int]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    result: dict[str, dict[str, int]] = {}
    for model, *_ in MODELS:
        selected = [
            row
            for row in rows
            if row["model"] == model and row["controller"] == "Generic"
        ]
        if len(selected) != 1:
            raise ValueError(f"Expected one Generic row for {model}, found {len(selected)}")
        result[model] = {field: int(selected[0][field]) for field in FIELDS}
        observed = tuple(result[model][field] for field in FIELDS)
        if observed != EXPECTED[model]:
            raise ValueError(
                f"Frozen Figure 5 data changed for {model}: {observed} != {EXPECTED[model]}"
            )
        if sum(result[model][field] for field, *_ in OUTCOMES) != result[model]["tasks"]:
            raise ValueError(f"Outcome partition does not sum to n=40 for {model}")
    return result


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.0,
            "axes.labelsize": 7.2,
            "axes.titlesize": 7.8,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "legend.fontsize": 7.0,
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.0,
            "hatch.linewidth": 0.35,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "text.color": INK,
            "axes.labelcolor": INK,
            "axes.edgecolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return 100 * p, 100 * max(0, center - half), 100 * min(1, center + half)


def clean(ax: plt.Axes, *, grid_axis: str) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, lw=0.45, alpha=0.9, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.4, width=0.65, pad=2)


def draw(data: dict[str, dict[str, int]]) -> plt.Figure:
    configure()
    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(3.35, 2.28),
        gridspec_kw={"width_ratios": [1.05, 1.0], "wspace": 0.38},
    )

    # Panel A keeps the complete n=40 denominator visible for each model.
    y_positions = {"Qwen3.5": 1.0, "GLM-5.1": 0.0}
    bar_height = 0.40
    for model, short, _marker, _model_color in MODELS:
        row = data[model]
        y = y_positions[model]
        cursor = 0
        ax_a.text(-1.0, y, short, ha="right", va="center", fontsize=7.0, color=INK)
        for field, _label, color, hatch in OUTCOMES:
            value = row[field]
            if value == 0:
                continue
            ax_a.add_patch(
                Rectangle(
                    (cursor, y - bar_height / 2),
                    value,
                    bar_height,
                    facecolor=color,
                    edgecolor=INK,
                    linewidth=0.50,
                    hatch=hatch,
                    zorder=2,
                )
            )
            text_color = INK if field in {"fallback_wrong_write", "unneeded_reject"} else PAPER
            ax_a.text(
                cursor + value / 2,
                y,
                str(value),
                ha="center",
                va="center",
                fontsize=7.0,
                weight="bold",
                color=text_color,
                zorder=3,
            )
            cursor += value

    ax_a.set_xlim(-7.2, 40)
    ax_a.set_ylim(-0.48, 1.50)
    ax_a.set_xticks([0, 20, 40])
    ax_a.set_yticks([])
    ax_a.set_xlabel("Tasks per model")
    ax_a.set_title("A  All 40 outcomes", loc="left", pad=3, weight="bold")
    ax_a.spines["left"].set_visible(False)
    clean(ax_a, grid_axis="x")

    # Panel B uses Figure 4's open-to-filled within-model trajectory grammar.
    offsets = {"Qwen3.5": -0.045, "GLM-5.1": 0.045}
    for model, short, marker, color in MODELS:
        row = data[model]
        cells = (
            (row["stable_writes"], row["stable_opportunities"]),
            (row["strict_core_writes"], row["strict_core_opportunities"]),
        )
        values = [wilson(k, n) for k, n in cells]
        xs = [offsets[model], 1 + offsets[model]]
        ax_b.plot(xs, [value[0] for value in values], color=color, lw=0.95, zorder=2)
        for index, (x, (rate, low, high), (k, n)) in enumerate(
            zip(xs, values, cells, strict=True)
        ):
            ax_b.errorbar(
                x,
                rate,
                yerr=[[rate - low], [high - rate]],
                fmt="none",
                ecolor=color,
                elinewidth=0.75,
                capsize=2.7,
                capthick=0.7,
                zorder=3,
            )
            ax_b.plot(
                x,
                rate,
                marker=marker,
                ms=3.7,
                mfc=PAPER if index == 0 else color,
                mec=color,
                mew=0.8,
                linestyle="none",
                zorder=4,
            )
            if index == 1:
                label_x = 0.90 if model == "Qwen3.5" else 1.62
                label_y = rate + 4.5 if model == "Qwen3.5" else 56.0
                ax_b.text(
                    label_x,
                    label_y,
                    f"{short} {k}/{n}",
                    ha="right",
                    va="bottom" if model == "Qwen3.5" else "top",
                    fontsize=7.0,
                    weight="bold",
                    color=color,
                )

    ax_b.text(
        0,
        7.0,
        "both 0/4",
        ha="center",
        va="bottom",
        fontsize=7.0,
        weight="bold",
        color=MUTED,
    )

    ax_b.set_xlim(-0.23, 1.68)
    ax_b.set_ylim(-4, 112)
    ax_b.set_xticks(
        [0, 1],
        ["Stable\nA stays #1", "Changed\nB #1; A valid"],
    )
    ax_b.set_yticks([0, 50, 100])
    ax_b.set_ylabel("Wrong-target B write (%)")
    ax_b.set_title("B  Strict contrast", loc="left", pad=3, weight="bold")
    ax_b.spines["bottom"].set_visible(False)
    ax_b.tick_params(axis="x", length=0, pad=4)
    clean(ax_b, grid_axis="y")

    legend_handles = [
        Patch(
            facecolor=color,
            edgecolor=INK,
            linewidth=0.5,
            hatch=hatch,
            label=label,
        )
        for _field, label, color, hatch in OUTCOMES
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.50, 0.995),
        ncol=2,
        frameon=False,
        handlelength=1.0,
        handleheight=0.75,
        handletextpad=0.30,
        columnspacing=0.70,
        labelspacing=0.25,
    )
    fig.subplots_adjust(left=0.095, right=0.985, top=0.77, bottom=0.25)
    return fig


def draw_right_panel(data: dict[str, dict[str, int]]) -> plt.Figure:
    """Render the strict contrast alone so its final narrow-column layout can be judged."""
    configure()
    fig, ax = plt.subplots(figsize=(1.78, 2.10))
    offsets = {"Qwen3.5": -0.040, "GLM-5.1": 0.040}

    for model, _short, marker, color in MODELS:
        row = data[model]
        cells = (
            (row["stable_writes"], row["stable_opportunities"]),
            (row["strict_core_writes"], row["strict_core_opportunities"]),
        )
        values = [wilson(k, n) for k, n in cells]
        xs = [offsets[model], 1 + offsets[model]]
        ax.plot(xs, [value[0] for value in values], color=color, lw=1.05, zorder=2)
        for index, (x, (rate, low, high)) in enumerate(zip(xs, values, strict=True)):
            ax.errorbar(
                x,
                rate,
                yerr=[[rate - low], [high - rate]],
                fmt="none",
                ecolor=color,
                elinewidth=0.8,
                capsize=2.8,
                capthick=0.75,
                zorder=3,
            )
            ax.plot(
                x,
                rate,
                marker=marker,
                ms=4.0,
                mfc=PAPER if index == 0 else color,
                mec=color,
                mew=0.85,
                linestyle="none",
                zorder=4,
            )

    ax.text(
        0,
        7.0,
        "both 0/4",
        ha="center",
        va="bottom",
        fontsize=7.0,
        weight="bold",
        color=MUTED,
        bbox={"facecolor": PAPER, "edgecolor": "none", "pad": 0.4},
        zorder=5,
    )
    ax.text(0.960, 106.0, "8/8", ha="center", va="bottom", fontsize=7.0, weight="bold", color=MODEL_COLORS["Qwen"])
    ax.text(1.175, 74.5, "6/8", ha="left", va="center", fontsize=7.0, weight="bold", color=MODEL_COLORS["GLM"])

    ax.set_xlim(-0.22, 1.48)
    ax.set_ylim(-4, 114)
    ax.set_xticks([0, 1], ["Stable\nA stays #1", "Changed\nB #1; A valid"])
    ax.set_yticks([0, 50, 100])
    ax.set_ylabel("Wrong-target B write (%)")
    ax.set_title("B  Strict B writes", loc="left", pad=3, weight="bold")
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=4)
    clean(ax, grid_axis="y")

    handles = [
        Line2D(
            [0],
            [0],
            color=color,
            marker=marker,
            markersize=3.7,
            markerfacecolor=color,
            markeredgecolor=color,
            linewidth=1.0,
            label=short,
        )
        for _model, short, marker, color in MODELS
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.58, 0.985),
        ncol=2,
        frameon=False,
        handlelength=1.1,
        handletextpad=0.30,
        columnspacing=0.65,
    )
    fig.subplots_adjust(left=0.31, right=0.95, top=0.78, bottom=0.25)
    return fig


def draw_right_bars(data: dict[str, dict[str, int]]) -> plt.Figure:
    """Render the strict contrast as compact condition-grouped bars."""
    configure()
    fig, ax = plt.subplots(figsize=(1.78, 2.10))

    centers = np.array([0.0, 1.0])
    offsets = {"Qwen3.5": -0.13, "GLM-5.1": 0.13}
    width = 0.20
    hatches = {"Qwen3.5": "", "GLM-5.1": "//"}

    for model, _short, marker, color in MODELS:
        row = data[model]
        cells = (
            (row["stable_writes"], row["stable_opportunities"]),
            (row["strict_core_writes"], row["strict_core_opportunities"]),
        )
        values = [wilson(k, n) for k, n in cells]
        xs = centers + offsets[model]
        rates = np.array([value[0] for value in values])
        lows = np.array([value[1] for value in values])
        highs = np.array([value[2] for value in values])

        ax.bar(
            xs,
            rates,
            width=width,
            color=color,
            alpha=0.78,
            edgecolor=color,
            linewidth=0.75,
            hatch=hatches[model],
            zorder=2,
        )
        ax.errorbar(
            xs,
            rates,
            yerr=[rates - lows, highs - rates],
            fmt="none",
            ecolor=INK,
            elinewidth=0.75,
            capsize=2.8,
            capthick=0.7,
            zorder=4,
        )

        # Zero-height bars need a visible, exact endpoint without inventing area.
        ax.plot(
            xs[0],
            0,
            marker=marker,
            ms=3.7,
            mfc=PAPER,
            mec=color,
            mew=0.8,
            linestyle="none",
            zorder=5,
        )
        ax.plot(
            xs[1],
            rates[1],
            marker=marker,
            ms=3.7,
            mfc=color,
            mec=color,
            mew=0.8,
            linestyle="none",
            zorder=5,
        )

        changed_k, changed_n = cells[1]
        ax.text(
            xs[1],
            highs[1] + 2.5,
            f"{changed_k}/{changed_n}",
            ha="center",
            va="bottom",
            fontsize=7.0,
            color=INK,
            zorder=6,
        )

    ax.text(
        0,
        7.0,
        "0/4 each",
        ha="center",
        va="bottom",
        fontsize=7.0,
        color=INK,
        bbox={"facecolor": PAPER, "edgecolor": "none", "pad": 0.4},
        zorder=6,
    )

    ax.set_xlim(-0.48, 1.48)
    ax.set_ylim(-4, 112)
    ax.set_xticks([0, 1], ["Stable\nA #1", "Changed\nB #1; A valid"])
    ax.set_yticks([0, 50, 100])
    ax.set_ylabel("Rate (%)")
    ax.set_title("B  Strict B writes", loc="left", pad=3, weight="bold")
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=4)
    clean(ax, grid_axis="y")

    handles = [
        Line2D(
            [0],
            [0],
            color=color,
            marker=marker,
            markersize=3.7,
            markerfacecolor=color,
            markeredgecolor=color,
            linewidth=0,
            label=short,
        )
        for _model, short, marker, color in MODELS
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.59, 0.985),
        ncol=2,
        frameon=False,
        handlelength=0.65,
        handletextpad=0.30,
        columnspacing=0.70,
    )
    fig.subplots_adjust(left=0.28, right=0.96, top=0.78, bottom=0.25)
    return fig


def save(
    fig: plt.Figure,
    stem: Path,
    *,
    right_only: bool = False,
    panel_type: str = "paired trajectory",
) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    size_inches = [round(float(value), 2) for value in fig.get_size_inches()]
    fig.savefig(
        stem.with_suffix(".pdf"),
        metadata={"Creator": "TRI Figure 5 Figure-4-aligned result chart"},
    )
    fig.savefig(stem.with_suffix(".svg"))
    png = stem.with_suffix(".png")
    fig.savefig(png, dpi=400)
    plt.close(fig)

    with Image.open(png).convert("RGB") as image:
        image.convert("L").save(
            stem.with_name(stem.name + "-grayscale").with_suffix(".png")
        )
        rgb = np.asarray(image, dtype=np.float32) / 255.0
        deuteranopia_matrix = np.array(
            [
                [0.367322, 0.860646, -0.227968],
                [0.280085, 0.672501, 0.047413],
                [-0.011820, 0.042940, 0.968881],
            ],
            dtype=np.float32,
        )
        simulated = np.clip(rgb @ deuteranopia_matrix.T, 0.0, 1.0)
        Image.fromarray(np.uint8(np.round(simulated * 255))).save(
            stem.with_name(stem.name + "-deuteranopia").with_suffix(".png")
        )

    manifest = {
        "status": (
            "Figure-4-aligned Figure 5 right-panel candidate"
            if right_only
            else "Figure-4-aligned Figure 5 candidate: full outcome composition plus strict contrast"
        ),
        "source": str(DATA),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "size_inches": size_inches,
        "minimum_text_pt": 7.0,
        "png_dpi": 400,
        "pdf_fonttype": 42,
        "frozen_values": EXPECTED,
    }
    if right_only:
        manifest["panel"] = (
            f"Stable versus Changed strict B-write rates as {panel_type}; "
            "Wilson 95% CI, redundant model encoding, and exact fractions"
        )
    else:
        manifest["panel_a"] = "n=40/model mutually exclusive outcome partition with direct counts"
        manifest["panel_b"] = "Stable versus Changed strict B-write rates with Wilson 95% CI and exact fractions"
    stem.with_name(stem.name + "-manifest").with_suffix(".json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stem", type=Path, default=DEFAULT_STEM)
    parser.add_argument("--right-only", action="store_true")
    parser.add_argument("--right-bars", action="store_true")
    args = parser.parse_args()
    data = read_frozen()
    if args.right_only and args.right_bars:
        parser.error("choose only one of --right-only and --right-bars")
    if args.right_bars:
        stem = DEFAULT_BAR_STEM if args.stem == DEFAULT_STEM else args.stem
        save(
            draw_right_bars(data),
            stem,
            right_only=True,
            panel_type="condition-grouped bars",
        )
    elif args.right_only:
        stem = DEFAULT_RIGHT_STEM if args.stem == DEFAULT_STEM else args.stem
        save(draw_right_panel(data), stem, right_only=True)
    else:
        save(draw(data), args.stem)


if __name__ == "__main__":
    main()
