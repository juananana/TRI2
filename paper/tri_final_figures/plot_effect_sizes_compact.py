#!/usr/bin/env python3
"""Compact single-column forest plot for TRI decision-visibility effects."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt


DEFAULT_DATA = Path(
    "./paper/tri_final_figures/"
    "data/summary_csv/revision_decision_visible_gains.csv"
)
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "fig_decision_visibility_effect_sizes_compact"

INK = "#253238"
MUTED = "#59676D"
GRID = "#C7D0D4"
TEAL = "#1F6F78"
MARKERS = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}
MODEL_LABELS = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM", "DeepSeek": "DeepSeek"}


def load(path: Path) -> dict[tuple[str, str, str], dict[str, float]]:
    rows = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows[(row["audit_id"], row["model"], row["metric"])] = {
                "value": float(row["difference_pp"]),
                "low": float(row["ci95_low_pp"]),
                "high": float(row["ci95_high_pp"]),
            }
    return rows


def compact_interval(value: float, low: float, high: float) -> str:
    return f"{value:+.1f}\n[{low:.0f},{high:.0f}]"


def draw(data: dict[tuple[str, str, str], dict[str, float]], output: Path) -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7.0,
            "axes.titlesize": 7.3,
            "xtick.labelsize": 6.3,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
        }
    )

    groups = [
        ("revision_full_diagnostic", "Authored", ["Qwen3.5", "GLM-5.1"]),
        ("revision_human_rewrite", "Rewrite (3 pairs)", ["Qwen3.5", "GLM-5.1"]),
        ("revision_source_grounded", "Source-derived", ["Qwen3.5", "GLM-5.1", "DeepSeek"]),
    ]
    y_positions = [6.00, 5.23, 4.03, 3.26, 2.06, 1.29, 0.52]
    rows = []
    index = 0
    for audit, group, models in groups:
        for model in models:
            rows.append((y_positions[index], audit, group, model))
            index += 1

    fig = plt.figure(figsize=(3.25, 2.34))
    grid = fig.add_gridspec(1, 3, width_ratios=[1.32, 1.67, 1.50], wspace=0.09)
    label_ax = fig.add_subplot(grid[0])
    axes = [fig.add_subplot(grid[1]), fig.add_subplot(grid[2])]

    for ax in (label_ax, *axes):
        ax.set_ylim(0.10, 6.64)

    label_ax.axis("off")
    for y, _, _, model in rows:
        label_ax.scatter(0.09, y, s=22, marker=MARKERS[model], facecolor=TEAL,
                         edgecolor=INK, linewidth=0.45, clip_on=False)
        label_ax.text(0.21, y, MODEL_LABELS[model], ha="left", va="center", fontsize=6.7)
    for y, label in ((6.49, "Authored"), (4.52, "Rewrite (3 pairs)"), (2.55, "Source-derived")):
        label_ax.text(0.00, y, label, ha="left", va="bottom", fontsize=6.7,
                      weight="semibold", color=MUTED)
    label_ax.set_xlim(0, 1)

    metrics = [
        ("changed_pairacc", "PairAcc $\\Delta$ (pp)", (-20, 108), [-20, 0, 40, 80]),
        ("actionable_e2e", "E2E $\\Delta$ (pp)", (-20, 66), [-20, 0, 20, 40]),
    ]
    for ax, (metric, title, xlim, ticks) in zip(axes, metrics):
        ax.axvline(0, color=INK, linewidth=0.75, zorder=1)
        ax.set_xlim(*xlim)
        ax.set_xticks(ticks)
        ax.set_yticks([])
        ax.set_title(title, pad=3, weight="semibold")
        ax.grid(axis="x", color=GRID, linewidth=0.4, alpha=0.55)
        ax.set_axisbelow(True)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        for separator in (4.64, 2.67):
            ax.axhline(separator, color=GRID, linestyle=(0, (3, 3)), linewidth=0.55)

        for y, audit, _, model in rows:
            row = data[(audit, model, metric)]
            value, low, high = row["value"], row["low"], row["high"]
            ax.errorbar(
                value,
                y,
                xerr=[[value - low], [high - value]],
                fmt=MARKERS[model],
                markersize=4.0,
                markerfacecolor=TEAL,
                markeredgecolor=INK,
                markeredgewidth=0.45,
                ecolor=MUTED,
                elinewidth=0.65,
                capsize=1.8,
                zorder=3,
            )
            ax.text(
                xlim[1] - 1.0,
                y,
                compact_interval(value, low, high),
                ha="right",
                va="center",
                fontsize=5.5,
                linespacing=0.83,
                color=INK,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.88, pad=0.10),
            )

    fig.subplots_adjust(left=0.015, right=0.995, top=0.94, bottom=0.12)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.02)
    fig.savefig(output.with_suffix(".png"), dpi=400, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(output.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    draw(load(args.data), args.output)


if __name__ == "__main__":
    main()
