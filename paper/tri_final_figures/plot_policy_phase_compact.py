#!/usr/bin/env python3
"""Single-panel TRI policy phase space with an embedded high-accuracy detail view."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


DEFAULT_DATA = Path(__file__).resolve().parent / "matched_pairacc_and_marginals.csv"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "fig_resolution_policy_phase_space_singlecolumn_v3"

COLORS = {
    "ink": "#253238",
    "muted": "#637177",
    "grid": "#C4CED2",
    "generic": "#5E379D",
    "cta": "#2F74B8",
    "lifecycle": "#9A4C00",
    "rule": "#68747A",
    "purple_bg": "#EEE9F5",
    "blue_bg": "#E4EFF8",
    "orange_bg": "#F8EFE5",
    "neutral_bg": "#F3F5F5",
}
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


def point(
    ax: plt.Axes,
    row: dict[str, float],
    marker: str,
    color: str,
    *,
    open_marker: bool = False,
    size: float = 43,
    zorder: int = 5,
) -> None:
    ax.scatter(
        row["p"],
        row["r"],
        s=size,
        marker=marker,
        facecolor="white" if open_marker else color,
        edgecolor=color if open_marker else COLORS["ink"],
        linewidth=1.15 if open_marker else 0.65,
        zorder=zorder,
    )


def annotate_count(
    ax: plt.Axes,
    row: dict[str, float],
    count: int,
    offset: tuple[float, float],
    color: str = COLORS["ink"],
    fontsize: float = 5.7,
) -> None:
    ax.annotate(
        f"{count}",
        (row["p"], row["r"]),
        xytext=offset,
        textcoords="offset points",
        ha="center",
        va="center",
        fontsize=fontsize,
        color=color,
        weight="semibold",
        annotation_clip=False,
        zorder=8,
    )


def draw(data: dict[str, dict[tuple[str, str], dict[str, float]]], output: Path) -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7.2,
            "axes.labelsize": 8.2,
            "axes.titlesize": 8.8,
            "xtick.labelsize": 6.7,
            "ytick.labelsize": 6.7,
            "axes.linewidth": 0.75,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
        }
    )

    all_rows = data["all"]
    changed = data["changed_winner_core"]
    fig, ax = plt.subplots(figsize=(3.25, 3.12))

    ax.add_patch(Rectangle((0, 50), 50, 50, facecolor=COLORS["purple_bg"], edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((50, 50), 50, 50, facecolor=COLORS["blue_bg"], edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((50, 0), 50, 50, facecolor=COLORS["orange_bg"], edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((0, 0), 50, 50, facecolor=COLORS["neutral_bg"], edgecolor="none", zorder=0))
    ax.axvline(50, color=COLORS["grid"], linestyle=(0, (4, 3)), linewidth=0.75)
    ax.axhline(50, color=COLORS["grid"], linestyle=(0, (4, 3)), linewidth=0.75)

    # Main view: separated points and deterministic extremes.
    for model, offset in (("Qwen3.5", (0, -14)), ("GLM-5.1", (0, -14))):
        row = all_rows[(model, "Generic")]
        point(ax, row, MARKERS[model], COLORS["generic"])
        annotate_count(ax, row, int(changed[(model, "Generic")]["count"]), offset, COLORS["generic"])

    for controller, label, label_xy, count_offset in (
        ("Always-Reevaluate", "Always-Reeval.", (2, 86), (-8, -12)),
        ("Always-Lock+validity", "Always-Lock", (72, 29), (-9, 11)),
    ):
        row = all_rows[("model-independent", controller)]
        point(ax, row, "D", COLORS["ink"], open_marker=True, size=48)
        annotate_count(ax, row, int(changed[("model-independent", controller)]["count"]), count_offset)
        ax.text(*label_xy, label, fontsize=6.4, color=COLORS["ink"], va="center")

    ax.text(24, 57, "R > 50", ha="center", va="center", fontsize=6.6, color=COLORS["muted"])
    ax.text(76, 38, "P > 50", ha="center", va="center", fontsize=6.6, color=COLORS["muted"])

    # The upper-right cluster is expanded in place; the inset occupies only otherwise dense space.
    inset = ax.inset_axes([0.635, 0.595, 0.345, 0.365])
    inset.set_facecolor("white")
    inset.patch.set_alpha(0.96)
    for spine in inset.spines.values():
        spine.set_color(COLORS["grid"])
        spine.set_linewidth(0.65)
    inset.set_xlim(90, 101)
    inset.set_ylim(91, 101)
    inset.set_xticks([92, 96, 100])
    inset.set_yticks([92, 96, 100])
    inset.tick_params(labelsize=4.7, length=1.8, pad=1)
    inset.grid(color=COLORS["grid"], linewidth=0.35, alpha=0.55)
    inset.set_title("High-accuracy detail", fontsize=5.6, pad=2, weight="semibold")

    clustered = [
        ("Qwen3.5", "CTA", COLORS["cta"], False, (-1, -11)),
        ("GLM-5.1", "CTA", COLORS["cta"], False, (8, -10)),
        ("Qwen3.5", "Lifecycle-free", COLORS["lifecycle"], False, (-8, -10)),
        ("GLM-5.1", "Lifecycle-free", COLORS["lifecycle"], False, (0, -10)),
        ("Qwen3.5", "Lifecycle-gated", COLORS["lifecycle"], True, (-8, -10)),
        ("GLM-5.1", "Lifecycle-gated", COLORS["lifecycle"], True, (-8, -10)),
    ]
    for model, controller, color, open_marker, offset in clustered:
        row = all_rows[(model, controller)]
        point(inset, row, MARKERS[model], color, open_marker=open_marker, size=24)
        annotate_count(inset, row, int(changed[(model, controller)]["count"]), offset, color, fontsize=4.8)

    rule = all_rows[("model-independent", "Rule v2 (post-hoc)")]
    point(inset, rule, "D", COLORS["rule"], open_marker=True, size=25)
    inset.annotate(
        f"Rule* {int(changed[('model-independent', 'Rule v2 (post-hoc)')]['count'])}",
        (rule["p"], rule["r"]),
        xytext=(8, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        fontsize=4.4,
        color=COLORS["rule"],
        weight="semibold",
        annotation_clip=False,
        zorder=8,
    )

    # Compact, in-plot key. Numbers beside marks are the matched PairAcc numerator out of 32.
    key = Rectangle((2, 3), 47, 30, facecolor="white", edgecolor=COLORS["grid"], linewidth=0.6, alpha=0.95, zorder=2)
    ax.add_patch(key)
    ax.scatter(5.0, 29.0, s=16, marker="o", facecolor="white", edgecolor=COLORS["ink"], linewidth=0.6, zorder=3)
    ax.text(7.5, 29.0, "Qwen", fontsize=5.3, va="center", zorder=3)
    ax.scatter(20.5, 29.0, s=16, marker="s", facecolor="white", edgecolor=COLORS["ink"], linewidth=0.6, zorder=3)
    ax.text(23.0, 29.0, "GLM", fontsize=5.3, va="center", zorder=3)
    ax.scatter(34.0, 29.0, s=16, marker="D", facecolor="white", edgecolor=COLORS["ink"], linewidth=0.6, zorder=3)
    ax.text(36.5, 29.0, "fixed", fontsize=5.3, va="center", zorder=3)

    handles = [
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["generic"], markeredgecolor=COLORS["ink"], markersize=4.0, label="Generic"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["cta"], markeredgecolor=COLORS["ink"], markersize=4.0, label="CTA"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["lifecycle"], markeredgecolor=COLORS["ink"], markersize=4.0, label="Life-A"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="white", markeredgecolor=COLORS["lifecycle"], markersize=4.0, label="Life-G"),
    ]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.035, 0.095), ncol=2,
              frameon=False, fontsize=5.2, handletextpad=0.25, columnspacing=0.65, borderaxespad=0)
    ax.text(4.5, 7.0, "number = PairAcc / 32", fontsize=5.1, color=COLORS["muted"], zorder=3)

    ax.set_xlim(-3, 106)
    ax.set_ylim(-2, 106)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Preserve accuracy (%)", labelpad=2)
    ax.set_ylabel("Reevaluate accuracy (%)", labelpad=2)
    ax.set_title("Policy marginals with matched PairAcc", loc="left", weight="semibold", pad=4)
    ax.spines[["top", "right"]].set_visible(False)

    fig.subplots_adjust(left=0.19, right=0.985, bottom=0.15, top=0.92)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.035)
    fig.savefig(output.with_suffix(".png"), dpi=400, bbox_inches="tight", pad_inches=0.035)
    fig.savefig(output.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.035)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    draw(load(args.data), args.output)


if __name__ == "__main__":
    main()
