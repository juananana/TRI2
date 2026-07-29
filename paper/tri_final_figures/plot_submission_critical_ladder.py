#!/usr/bin/env python3
"""Figure 6 candidate: one shared-scale effect ladder for the equal-call audits."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from PIL import Image

import plot_submission_critical_compact as compact


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "outputs" / "figure6_effect_ladder_v1" / "figure6_effect_ladder"

INK = "#264A56"
MUTED = "#5F6B70"
GRID = "#D6E0DE"
PAPER = "#FFFFFF"


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.0,
            "axes.labelsize": 7.2,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "axes.linewidth": 0.65,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "text.color": INK,
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )


def interval_band(ax, low: float, high: float, y: float, color: str, *, solid: bool) -> None:
    height = 0.32
    band = FancyBboxPatch(
        (low, y - height / 2),
        high - low,
        height,
        boxstyle="round,pad=0.01,rounding_size=0.16",
        facecolor=color if solid else PAPER,
        edgecolor=color,
        linewidth=0.85,
        alpha=0.24 if solid else 1.0,
        linestyle="solid" if solid else (0, (2.0, 1.6)),
        zorder=2,
    )
    ax.add_patch(band)


def draw_group(ax, rows: list[dict], ys: list[float], heading: str, count: str) -> None:
    ax.text(-41.5, ys[0] + 1.05, heading, ha="left", va="center", fontsize=7.0, weight="bold", color=MUTED)
    ax.text(-41.5, ys[0] + 0.63, count, ha="left", va="center", fontsize=7.0, weight="bold", color=MUTED)
    for row, y in zip(rows, ys, strict=True):
        name, color, marker = compact.MODEL_STYLE[row["model"]]
        value, low, high = float(row["value"]), float(row["low"]), float(row["high"])
        solid = low > 0 or high < 0

        ax.plot(
            -33.0,
            y,
            marker=marker,
            markersize=4.0,
            markerfacecolor=color if solid else PAPER,
            markeredgecolor=color,
            markeredgewidth=0.85,
            linestyle="none",
            clip_on=False,
            zorder=5,
        )
        ax.text(-29.8, y, name, ha="left", va="center", fontsize=7.0, color=INK)
        interval_band(ax, low, high, y, color, solid=solid)
        ax.plot(
            value,
            y,
            marker=marker,
            markersize=4.1,
            markerfacecolor=color if solid else PAPER,
            markeredgecolor=color,
            markeredgewidth=0.9,
            linestyle="none",
            zorder=5,
        )
        ax.text(
            value,
            y + 0.31,
            f"{value:+.1f}",
            ha="center",
            va="bottom",
            fontsize=7.0,
            weight="bold" if solid else "normal",
            color=INK,
            zorder=6,
        )


def draw(convention: list[dict], matched: list[dict]) -> plt.Figure:
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.55))

    convention_y = [8.0, 7.0, 6.0, 5.0]
    visible_y = [3.25, 2.25, 1.25, 0.25]
    draw_group(ax, convention, convention_y, "Convention told", "40 pairs")
    draw_group(ax, matched, visible_y, "Decision visible", "32 pairs")

    ax.axvline(0, color=INK, lw=0.9, zorder=1)
    ax.plot([-42, 88], [4.65, 4.65], color=GRID, lw=0.7, zorder=0)

    ax.set_xlim(-42, 90)
    ax.set_ylim(-0.35, 9.40)
    ax.set_xticks([-20, 0, 20, 40, 60, 80])
    ax.set_xlabel("Changed PairAcc effect (pp)")
    ax.set_yticks([])
    ax.grid(axis="x", color=GRID, lw=0.46, alpha=0.82, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="x", length=2.5, width=0.65, pad=2)

    fig.subplots_adjust(left=0.035, right=0.985, top=0.985, bottom=0.145)
    return fig


def save(fig: plt.Figure, output: Path, convention: list[dict], matched: list[dict]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"), metadata={"Creator": "TRI equal-call effect ladder"})
    fig.savefig(output.with_suffix(".svg"))
    png = output.with_suffix(".png")
    fig.savefig(png, dpi=400)
    plt.close(fig)

    with Image.open(png).convert("RGB") as image:
        image.convert("L").save(output.with_name(output.name + "-grayscale").with_suffix(".png"))
        rgb = np.asarray(image, dtype=np.float32) / 255.0
        deuteranopia = np.array(
            [
                [0.367322, 0.860646, -0.227968],
                [0.280085, 0.672501, 0.047413],
                [-0.011820, 0.042940, 0.968881],
            ],
            dtype=np.float32,
        )
        simulated = np.clip(rgb @ deuteranopia.T, 0.0, 1.0)
        Image.fromarray(np.uint8(np.round(simulated * 255))).save(
            output.with_name(output.name + "-deuteranopia").with_suffix(".png")
        )

    manifest = {
        "status": "Figure 6 shared-scale effect-ladder candidate",
        "size_inches": [3.35, 2.55],
        "minimum_text_pt": 7.0,
        "sources": {
            "convention": str(compact.source.DEFAULT_CONVENTION),
            "convention_sha256": hashlib.sha256(compact.source.DEFAULT_CONVENTION.read_bytes()).hexdigest(),
            "decision_visible": str(compact.source.DEFAULT_MATCHED),
            "decision_visible_sha256": hashlib.sha256(compact.source.DEFAULT_MATCHED.read_bytes()).hexdigest(),
        },
        "groups": {
            "convention_told_40_pairs": [
                {
                    "model": compact.MODEL_STYLE[row["model"]][0],
                    "effect_pp": round(float(row["value"]), 3),
                    "ci95_low_pp": round(float(row["low"]), 3),
                    "ci95_high_pp": round(float(row["high"]), 3),
                }
                for row in convention
            ],
            "decision_visible_32_pairs": [
                {
                    "model": compact.MODEL_STYLE[row["model"]][0],
                    "effect_pp": round(float(row["value"]), 3),
                    "ci95_low_pp": round(float(row["low"]), 3),
                    "ci95_high_pp": round(float(row["high"]), 3),
                }
                for row in matched
            ],
        },
        "encoding": {
            "horizontal_band": "cluster-bootstrap 95% CI",
            "marker_position": "changed-PairAcc effect",
            "marker_shape": "model identity",
            "filled_marker": "CI excludes zero",
            "open_marker": "CI includes zero",
        },
    }
    output.with_name(output.name + "-manifest").with_suffix(".json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    convention, matched = compact.load_rows()
    save(draw(convention, matched), args.output, convention, matched)
    print(args.output)


if __name__ == "__main__":
    main()
