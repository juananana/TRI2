#!/usr/bin/env python3
"""Compact single-panel Figure 6 candidate for the two equal-call audits."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from PIL import Image

import plot_submission_critical_effects as source


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "outputs" / "fig_submission_critical_compact_v3" / "fig_submission_critical_pairacc_compact"

INK = "#264A56"
MUTED = "#5F6B70"
GRID = "#D6E0DE"
PAPER = "#FFFFFF"

MODEL_ORDER = [
    "Qwen/Qwen3.5-122B-A10B",
    "Pro/zai-org/GLM-5.1",
    "deepseek-ai/DeepSeek-V4-Pro",
    "Pro/MiniMaxAI/MiniMax-M2.5",
]
MODEL_STYLE = {
    MODEL_ORDER[0]: ("Qwen", "#8B6F8E", "o"),
    MODEL_ORDER[1]: ("GLM", "#E56D4E", "s"),
    MODEL_ORDER[2]: ("DeepSeek", "#407A7F", "D"),
    MODEL_ORDER[3]: ("MiniMax", "#60AA84", "^")
}


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.0,
            "axes.labelsize": 7.4,
            "axes.titlesize": 8.0,
            "xtick.labelsize": 6.8,
            "ytick.labelsize": 7.0,
            "legend.fontsize": 6.7,
            "axes.linewidth": 0.65,
            "hatch.linewidth": 0.28,
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


def ordered(rows: list[dict]) -> list[dict]:
    by_model = {row["model"]: row for row in rows}
    if set(by_model) != set(MODEL_ORDER):
        raise ValueError(f"Expected complete four-model audit, found {sorted(by_model)}")
    return [by_model[model] for model in MODEL_ORDER]


def load_rows() -> tuple[list[dict], list[dict]]:
    convention = source._load(source.DEFAULT_CONVENTION)
    matched = source._load(source.DEFAULT_MATCHED)
    return ordered(source._convention_rows(convention)), ordered(source._matched_rows(matched))


def draw(convention: list[dict], matched: list[dict]) -> plt.Figure:
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.42))
    group_x = [np.arange(4) * 0.72, 3.55 + np.arange(4) * 0.72]
    bar_width = 0.38
    halo_width = 0.15

    for group_index, (rows, xs) in enumerate(zip((convention, matched), group_x, strict=True)):
        for row, x in zip(rows, xs, strict=True):
            label, color, marker = MODEL_STYLE[row["model"]]
            value, low, high = float(row["value"]), float(row["low"]), float(row["high"])
            excludes_zero = low > 0 or high < 0
            ax.add_patch(
                Rectangle(
                    (x - halo_width / 2, low),
                    halo_width,
                    high - low,
                    facecolor=color,
                    edgecolor="none",
                    alpha=0.16,
                    zorder=1,
                )
            )
            ax.bar(
                x,
                value,
                width=bar_width,
                facecolor=color if excludes_zero else PAPER,
                edgecolor=color,
                linewidth=0.85,
                alpha=0.68 if excludes_zero else 1.0,
                zorder=2,
            )
            ax.plot(
                x,
                value,
                marker=marker,
                markersize=3.5,
                markerfacecolor=color if excludes_zero else PAPER,
                markeredgecolor=color,
                markeredgewidth=0.75,
                linestyle="none",
                zorder=3,
            )
            label_y = high + 2.8 if value >= 0 else low - 2.8
            if group_index == 0 and row["model"] == MODEL_ORDER[1]:
                label_y += 3.0
            if group_index == 0 and row["model"] == MODEL_ORDER[2]:
                label_y -= 2.0
            ax.text(
                x,
                label_y,
                f"{value:+.1f}",
                ha="center",
                va="bottom" if value >= 0 else "top",
                fontsize=6.7,
                color=INK,
                weight="bold" if excludes_zero else "normal",
                zorder=4,
            )

    all_x = np.concatenate(group_x)
    ax.axhline(0, color=INK, lw=0.72, zorder=1)
    ax.axvline(2.81, color=GRID, lw=0.75, zorder=0)
    ax.set_xlim(-0.45, 6.20)
    ax.set_ylim(-22, 88)
    ax.set_yticks([-20, 0, 20, 40, 60, 80])
    ax.set_ylabel("Changed PairAcc effect (pp)")
    ax.set_xticks(all_x, ["Q", "G", "D", "M"] * 2)
    ax.grid(axis="y", color=GRID, lw=0.46, alpha=0.82, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=2)
    ax.tick_params(axis="y", length=2.5, width=0.65, pad=2)

    ax.text(
        1.08,
        -0.16,
        "CONVENTION TOLD\n40 PAIRS",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=6.5,
        color=MUTED,
        weight="bold",
        linespacing=0.88,
    )
    ax.text(
        4.63,
        -0.16,
        "DECISION VISIBLE\n32 PAIRS",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=6.5,
        color=MUTED,
        weight="bold",
        linespacing=0.88,
    )

    handles = [
        Line2D(
            [0],
            [0],
            marker=marker,
            color="none",
            markerfacecolor=color,
            markeredgecolor=color,
            markeredgewidth=0.75,
            markersize=4.2,
            label=label,
        )
        for label, color, marker in MODEL_STYLE.values()
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.57, 0.995),
        ncol=4,
        frameon=False,
        handlelength=0.75,
        handletextpad=0.22,
        columnspacing=0.55,
    )
    fig.text(
        0.99,
        0.012,
        "Separate inventories; shaded bands = cluster-bootstrap 95% CIs.",
        ha="right",
        va="bottom",
        fontsize=5.9,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.18, right=0.985, top=0.87, bottom=0.275)
    return fig


def save(
    fig: plt.Figure,
    output: Path,
    convention: list[dict],
    matched: list[dict],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"), metadata={"Creator": "TRI compact equal-call effect plot"})
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
        "status": "Figure 6 v3 shape-coded equal-call effects; candidate not integrated",
        "size_inches": [3.35, 2.42],
        "minimum_text_pt": 5.9,
        "sources": {
            "convention": str(source.DEFAULT_CONVENTION),
            "convention_sha256": hashlib.sha256(source.DEFAULT_CONVENTION.read_bytes()).hexdigest(),
            "decision_visible": str(source.DEFAULT_MATCHED),
            "decision_visible_sha256": hashlib.sha256(source.DEFAULT_MATCHED.read_bytes()).hexdigest(),
        },
        "groups": {
            "convention_told_40_pairs": [
                {
                    "model": MODEL_STYLE[row["model"]][0],
                    "effect_pp": round(float(row["value"]), 3),
                    "ci95_low_pp": round(float(row["low"]), 3),
                    "ci95_high_pp": round(float(row["high"]), 3),
                }
                for row in convention
            ],
            "decision_visible_32_pairs": [
                {
                    "model": MODEL_STYLE[row["model"]][0],
                    "effect_pp": round(float(row["value"]), 3),
                    "ci95_low_pp": round(float(row["low"]), 3),
                    "ci95_high_pp": round(float(row["high"]), 3),
                }
                for row in matched
            ],
        },
        "encoding": {
            "bar": "effect estimate from zero",
            "translucent_band": "cluster-bootstrap 95% CI",
            "marker_shape": "model identity",
            "filled_marker_and_bar": "CI excludes zero",
            "open_marker_and_bar": "CI crosses zero",
        },
    }
    output.with_name(output.name + "-manifest").with_suffix(".json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    convention, matched = load_rows()
    save(draw(convention, matched), args.output, convention, matched)
    print(args.output)


if __name__ == "__main__":
    main()
