#!/usr/bin/env python3
"""Compact aligned dumbbell view of TRI policy marginals and matched PairAcc."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DATA = SCRIPT_DIR / "data" / "summary_csv" / "matched_pairacc_and_marginals.csv"
LOCAL_DATA = SCRIPT_DIR / "matched_pairacc_and_marginals.csv"
DEFAULT_DATA = PROJECT_DATA if PROJECT_DATA.exists() else LOCAL_DATA
DEFAULT_OUTPUT = SCRIPT_DIR / "fig_policy_dumbbell_compact"

INK = "#253238"
MUTED = "#637177"
GRID = "#C7D0D4"
GENERIC = "#5E379D"
CTA = "#2F74B8"
LIFECYCLE = "#A45808"
FIXED = "#647178"
RULE = "#424E54"
ROW_BG = "#F5F7F7"
MARKERS = {"Qwen3.5": "o", "GLM-5.1": "s", "model-independent": "D"}


def load(path: Path) -> dict[str, dict[tuple[str, str], dict[str, float]]]:
    slices = {"all": {}, "changed_winner_core": {}}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["dataset"] != "v3" or row["slice"] not in slices:
                continue
            slices[row["slice"]][(row["model"], row["controller"])] = {
                "p": float(row["preserve_accuracy_pct"]),
                "r": float(row["reevaluate_accuracy_pct"]),
                "pair": float(row["pairacc_pct"]),
                "count": int(row["both_correct"]),
            }
    return slices


def draw(data: dict[str, dict[tuple[str, str], dict[str, float]]], output: Path) -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7.0,
            "axes.titlesize": 7.3,
            "xtick.labelsize": 6.3,
            "ytick.labelsize": 6.3,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
        }
    )

    all_rows = data["all"]
    changed = data["changed_winner_core"]
    groups = [
        {
            "name": "Fixed extremes",
            "color": FIXED,
            "rows": [
                (10.60, "Lock", "model-independent", "Always-Lock+validity"),
                (9.93, "Reeval.", "model-independent", "Always-Reevaluate"),
            ],
        },
        {
            "name": "Generic",
            "color": GENERIC,
            "rows": [(8.78, "Q", "Qwen3.5", "Generic"), (8.11, "G", "GLM-5.1", "Generic")],
        },
        {
            "name": "CTA",
            "color": CTA,
            "rows": [(6.96, "Q", "Qwen3.5", "CTA"), (6.29, "G", "GLM-5.1", "CTA")],
        },
        {
            "name": "Lifecycle-Actor",
            "color": LIFECYCLE,
            "rows": [(5.14, "Q", "Qwen3.5", "Lifecycle-free"), (4.47, "G", "GLM-5.1", "Lifecycle-free")],
        },
        {
            "name": "Lifecycle-Gated",
            "color": LIFECYCLE,
            "rows": [(3.32, "Q", "Qwen3.5", "Lifecycle-gated"), (2.65, "G", "GLM-5.1", "Lifecycle-gated")],
        },
        {
            "name": "Rule*",
            "color": RULE,
            "rows": [(1.45, "", "model-independent", "Rule v2 (post-hoc)")],
        },
    ]

    fig = plt.figure(figsize=(3.25, 3.30))
    grid = fig.add_gridspec(1, 3, width_ratios=[1.20, 1.55, 1.00], wspace=0.08)
    label_ax = fig.add_subplot(grid[0])
    marginal_ax = fig.add_subplot(grid[1])
    pair_ax = fig.add_subplot(grid[2], sharey=marginal_ax)
    axes = (label_ax, marginal_ax, pair_ax)

    for ax in axes:
        ax.set_ylim(0.85, 11.20)

    # Alternating bands and separators keep the dense rows scannable.
    separators = [9.38, 7.55, 5.73, 3.91, 2.08]
    for index, group in enumerate(groups):
        ys = [row[0] for row in group["rows"]]
        if index % 2 == 1:
            for ax in axes:
                ax.axhspan(min(ys) - 0.27, max(ys) + 0.27, color=ROW_BG, zorder=0)
    for separator in separators:
        for ax in axes:
            ax.axhline(separator, color=GRID, linestyle=(0, (3, 3)), linewidth=0.48, zorder=1)

    label_ax.set_xlim(0, 1.15)
    label_ax.axis("off")
    label_ax.text(0.00, 11.08, "Controller", fontsize=6.5, color=MUTED, weight="semibold", va="bottom")
    for group in groups:
        ys = [row[0] for row in group["rows"]]
        center = sum(ys) / len(ys)
        label_ax.text(0.00, center, group["name"], fontsize=6.4, color=INK, va="center", weight="semibold")
        for y, short, model, _ in group["rows"]:
            marker = MARKERS[model]
            label_ax.scatter(0.78, y, s=15, marker=marker, facecolor="white", edgecolor=INK, linewidth=0.55)
            label_ax.text(0.89, y, short, fontsize=5.9, color=MUTED, va="center", ha="left")

    marginal_ax.set_xlim(-4, 105)
    marginal_ax.set_xticks([0, 50, 100])
    marginal_ax.set_yticks([])
    marginal_ax.set_title("Marginals (%)", pad=4, weight="semibold")
    marginal_ax.grid(axis="x", color=GRID, linewidth=0.42, alpha=0.65)
    marginal_ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        marginal_ax.spines[spine].set_visible(False)

    pair_ax.set_xlim(-4, 138)
    pair_ax.set_xticks([0, 50, 100])
    pair_ax.set_yticks([])
    pair_ax.set_title("PairAcc (%)", pad=4, weight="semibold")
    pair_ax.grid(axis="x", color=GRID, linewidth=0.42, alpha=0.65)
    pair_ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        pair_ax.spines[spine].set_visible(False)
    pair_ax.axvline(108, color=GRID, linewidth=0.55, zorder=1)
    pair_ax.text(126, 11.08, "correct /32", fontsize=5.4, color=MUTED, ha="center", va="bottom")

    for group in groups:
        color = group["color"]
        for y, _, model, controller in group["rows"]:
            row = all_rows[(model, controller)]
            pair = changed[(model, controller)]
            marker = MARKERS[model]

            preserve_y = y + 0.13
            reevaluate_y = y - 0.13
            marginal_ax.plot([row["p"], row["r"]], [preserve_y, reevaluate_y], color=color,
                             linewidth=1.05, alpha=0.48, zorder=2)
            marginal_ax.scatter(row["p"], preserve_y, s=20, marker=marker, facecolor="white", edgecolor=color,
                                linewidth=0.95, zorder=4)
            marginal_ax.scatter(row["r"], reevaluate_y, s=20, marker=marker, facecolor=color, edgecolor=INK,
                                linewidth=0.38, zorder=5)

            pair_ax.plot([0, pair["pair"]], [y, y], color=color, linewidth=0.85, alpha=0.38, zorder=2)
            pair_ax.scatter(pair["pair"], y, s=23, marker=marker, facecolor=color, edgecolor=INK,
                            linewidth=0.45, zorder=4)
            pair_ax.text(126, y, str(int(pair["count"])), fontsize=6.0, color=INK, ha="center", va="center")

    endpoint_legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=INK,
               markersize=4.0, label="Preserve"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=INK, markeredgecolor=INK,
               markersize=4.0, label="Reevaluate"),
    ]
    marginal_ax.legend(endpoint_legend, ["Preserve", "Reevaluate"], loc="lower center",
                       bbox_to_anchor=(0.50, 1.045), ncol=2, frameon=False, fontsize=5.5,
                       handletextpad=0.25, columnspacing=0.65, borderaxespad=0)

    fig.subplots_adjust(left=0.015, right=0.995, top=0.90, bottom=0.09)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.025)
    fig.savefig(output.with_suffix(".png"), dpi=400, bbox_inches="tight", pad_inches=0.025)
    fig.savefig(output.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.025)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    draw(load(args.data), args.output)


if __name__ == "__main__":
    main()
