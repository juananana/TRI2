#!/usr/bin/env python3
"""Generate three non-dumbbell candidate representations for TRI Figure 5."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Rectangle

from plot_figure5_options_abc import (
    DATA,
    DEEPSEEK,
    E2E,
    EXPECTED,
    GLM,
    GRID,
    INK,
    MODEL_STYLE,
    MUTED,
    PAIR,
    PAPER,
    POSITIVE,
    QWEN,
    ROOT,
    SPECS,
    configure,
    rounded,
    save_variants,
)


DEFAULT_OUTPUT = ROOT / "outputs" / "figure5_option_f_v3_refined"
BASE = "#D8D4CF"
REMAINDER = "#F2F1EF"
# Low-saturation teal/coral pair adapted from a popular scientific-figure
# "ocean breeze" palette; yellow members of the source palette are omitted.
PAIR_F = "#51999F"
PAIR_F_LIGHT = "#D9EBEC"
E2E_F = "#ED8D5A"
E2E_F_LIGHT = "#FAE1D4"
MODEL_PALE = {
    "Qwen3.5": "#D8CFDB",
    "GLM-5.1": "#F0CEC5",
    "DeepSeek": "#C9DEDA",
}


def read_full_data() -> dict[tuple[str, str, str], dict[str, float]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    output: dict[tuple[str, str, str], dict[str, float]] = {}
    for row in rows:
        key = (row["panel"], row["dataset"], row["model"])
        if key not in EXPECTED:
            continue
        effect = float(row["difference_pp"])
        low = float(row["ci95_low_pp"])
        high = float(row["ci95_high_pp"])
        if (effect, low, high) != EXPECTED[key]:
            raise ValueError(f"frozen source mismatch for {key}")
        left_num = float(row["left_num"])
        left_den = float(row["left_den"])
        right_num = float(row["right_num"])
        right_den = float(row["right_den"])
        baseline = 100.0 * left_num / left_den
        visible = 100.0 * right_num / right_den
        if not np.isclose(visible - baseline, effect, atol=0.001):
            raise ValueError(f"rate/effect mismatch for {key}: {visible - baseline} vs {effect}")
        output[key] = {
            "effect": effect,
            "low": low,
            "high": high,
            "baseline": baseline,
            "visible": visible,
        }
    if set(output) != set(EXPECTED):
        raise ValueError(f"missing Figure 5 rows: {sorted(set(EXPECTED) - set(output))}")
    return output


def group_rows(ax: plt.Axes, centers: list[float], *, show_headings: bool = True) -> None:
    ax.axhline(2.40, color=GRID, lw=0.6, zorder=1)
    ax.set_yticks(centers, [MODEL_STYLE[model][0] for _, model in SPECS])
    if not show_headings:
        return
    ax.text(
        -0.47,
        4.60,
        "AUTHORED",
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=7.0,
        color=MUTED,
        weight="bold",
        clip_on=False,
    )
    ax.text(
        -0.47,
        2.28,
        "SOURCE-DERIVED",
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=7.0,
        color=MUTED,
        weight="bold",
        clip_on=False,
    )


def clean_rate_axis(ax: plt.Axes) -> None:
    ax.set_xlim(0, 105)
    ax.set_xticks([0, 50, 100])
    ax.set_ylim(-0.65, 4.70)
    ax.grid(axis="x", color=GRID, lw=0.48, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.tick_params(axis="x", length=2.5, width=0.6, pad=2)
    ax.set_axisbelow(True)


def draw_baseline_gain(data: dict[tuple[str, str, str], dict[str, float]]) -> plt.Figure:
    """Option D: actual History-only rate plus the Decision-visible gain."""
    configure()
    fig, (pair_ax, e2e_ax) = plt.subplots(
        1,
        2,
        figsize=(3.35, 2.43),
        sharey=True,
        gridspec_kw={"width_ratios": [1, 1], "wspace": 0.14},
    )
    centers = [4.1, 3.2, 1.6, 0.7, -0.2]
    endpoint_specs = [
        (pair_ax, "pairacc", PAIR, "A  PairAcc rate"),
        (e2e_ax, "e2e", E2E, "B  E2E rate"),
    ]
    for ax, endpoint, color, title in endpoint_specs:
        for (dataset, model), y in zip(SPECS, centers, strict=True):
            row = data[(endpoint, dataset, model)]
            base = row["baseline"]
            visible = row["visible"]
            effect = row["effect"]
            excludes_zero = row["low"] > 0 or row["high"] < 0
            ax.barh(y, 100, height=0.46, color=REMAINDER, edgecolor="none", zorder=1)
            ax.barh(y, base, height=0.46, color=BASE, edgecolor=PAPER, linewidth=0.4, zorder=2)
            ax.barh(
                y,
                visible - base,
                left=base,
                height=0.46,
                color=color if excludes_zero else PAPER,
                edgecolor=color,
                linewidth=0.7,
                zorder=2,
            )
            low_final = base + row["low"]
            high_final = base + row["high"]
            ax.errorbar(
                visible,
                y,
                xerr=[[visible - low_final], [high_final - visible]],
                fmt="none",
                ecolor=INK,
                elinewidth=0.7,
                capsize=1.7,
                capthick=0.7,
                zorder=4,
            )
            ax.text(
                min(max(visible, 5.0), 98.0),
                y + 0.29,
                f"Δ{rounded(effect)}",
                ha="center",
                va="bottom",
                fontsize=7.0,
                color=INK,
                weight="bold" if excludes_zero else "normal",
                zorder=5,
            )
        clean_rate_axis(ax)
        ax.set_title(title, loc="left", pad=3, weight="bold")
        group_rows(ax, centers, show_headings=ax is pair_ax)

    fig.legend(
        handles=[
            Patch(facecolor=BASE, edgecolor="none", label="History-only"),
            Patch(facecolor=PAPER, edgecolor=INK, linewidth=0.7, label="visibility gain"),
        ],
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.64, 0.995),
        frameon=False,
        handlelength=1.0,
        columnspacing=0.8,
        handletextpad=0.35,
        fontsize=7.0,
    )
    fig.text(0.64, 0.03, "Observed rate (%)", ha="center", va="bottom", fontsize=7.5)
    fig.subplots_adjust(left=0.31, right=0.985, top=0.84, bottom=0.20)
    return fig


def clean_effect_axis(ax: plt.Axes, limits: tuple[float, float], ticks: list[int]) -> None:
    ax.axvspan(0, limits[1], color=POSITIVE, zorder=0)
    ax.axvline(0, color=MUTED, lw=0.8, zorder=1)
    ax.set_xlim(*limits)
    ax.set_xticks(ticks)
    ax.set_ylim(-0.65, 4.70)
    ax.grid(axis="x", color=GRID, lw=0.48, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.tick_params(axis="x", length=2.5, width=0.6, pad=2)
    ax.set_axisbelow(True)


def draw_horizontal_effect_bars(
    data: dict[tuple[str, str, str], dict[str, float]]
) -> plt.Figure:
    """Option E: effect bars with CI overlays."""
    configure()
    fig, (pair_ax, e2e_ax) = plt.subplots(
        1,
        2,
        figsize=(3.35, 2.38),
        sharey=True,
        gridspec_kw={"width_ratios": [1, 1], "wspace": 0.14},
    )
    centers = [4.1, 3.2, 1.6, 0.7, -0.2]
    endpoint_specs = [
        (pair_ax, "pairacc", (-15, 82), [0, 40, 80], "A  PairAcc gain"),
        (e2e_ax, "e2e", (-10, 32), [0, 15, 30], "B  E2E gain"),
    ]
    for ax, endpoint, limits, ticks, title in endpoint_specs:
        for (dataset, model), y in zip(SPECS, centers, strict=True):
            row = data[(endpoint, dataset, model)]
            _, _, color = MODEL_STYLE[model]
            excludes_zero = row["low"] > 0 or row["high"] < 0
            ax.barh(
                y,
                row["effect"],
                height=0.34,
                color=color if excludes_zero else MODEL_PALE[model],
                edgecolor=color,
                linewidth=0.65,
                zorder=2,
            )
            ax.errorbar(
                row["effect"],
                y,
                xerr=[[row["effect"] - row["low"]], [row["high"] - row["effect"]]],
                fmt="none",
                ecolor=INK,
                elinewidth=0.75,
                capsize=1.8,
                capthick=0.7,
                zorder=4,
            )
            ax.text(
                row["effect"],
                y + 0.25,
                rounded(row["effect"]),
                ha="center",
                va="bottom",
                fontsize=7.0,
                color=INK,
                weight="bold" if excludes_zero else "normal",
                zorder=5,
            )
        clean_effect_axis(ax, limits, ticks)
        ax.set_title(title, loc="left", pad=3, weight="bold")
        group_rows(ax, centers, show_headings=ax is pair_ax)

    fig.text(
        0.64,
        0.03,
        "Decision-visible − History-only (pp)",
        ha="center",
        va="bottom",
        fontsize=7.5,
    )
    fig.subplots_adjust(left=0.31, right=0.985, top=0.88, bottom=0.20)
    return fig


def draw_vertical_effect_bars(
    data: dict[tuple[str, str, str], dict[str, float]]
) -> plt.Figure:
    """Option F: compact grouped effects with quiet interval bands."""
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.35))
    centers = [0.0, 0.92, 2.18, 3.10, 4.02]
    width = 0.25
    endpoint_specs = [
        ("pairacc", -0.15, PAIR_F, PAIR_F_LIGHT, "PairAcc"),
        ("e2e", 0.15, E2E_F, E2E_F_LIGHT, "E2E"),
    ]
    for endpoint, offset, color, light, _label in endpoint_specs:
        for (dataset, model), x in zip(SPECS, centers, strict=True):
            row = data[(endpoint, dataset, model)]
            excludes_zero = row["low"] > 0 or row["high"] < 0
            ax.add_patch(
                Rectangle(
                    (x + offset - width * 0.23, row["low"]),
                    width * 0.46,
                    row["high"] - row["low"],
                    facecolor=color,
                    edgecolor="none",
                    alpha=0.13,
                    zorder=1,
                )
            )
            ax.bar(
                x + offset,
                row["effect"],
                width=width,
                color=color if excludes_zero else light,
                edgecolor=color,
                linewidth=0.70,
                zorder=2,
            )
            ax.text(
                x + offset,
                max(row["effect"] + 1.8, 1.8),
                rounded(row["effect"]),
                ha="center",
                va="bottom",
                fontsize=6.9,
                color=INK,
                zorder=5,
            )

    ax.axhspan(0, 82, color="#FAFAF9", zorder=0)
    ax.axhline(0, color=MUTED, lw=0.8, zorder=1)
    ax.axvline(1.55, color=GRID, lw=0.65, zorder=1)
    ax.set_xlim(-0.52, 4.52)
    ax.set_ylim(-15, 82.5)
    ax.set_yticks([-10, 0, 20, 40, 60, 80])
    ax.set_ylabel("Effect of Decision-visible (pp)")
    ax.set_xticks(centers, [MODEL_STYLE[model][0] for _, model in SPECS])
    ax.grid(axis="y", color=GRID, lw=0.48, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=3)
    ax.tick_params(axis="y", length=2.5, width=0.6, pad=2)
    ax.text(
        0.46,
        -0.18,
        "AUTHORED",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=7.0,
        color=MUTED,
        weight="bold",
    )
    ax.text(
        3.10,
        -0.18,
        "SOURCE-DERIVED",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=7.0,
        color=MUTED,
        weight="bold",
    )
    ax.legend(
        handles=[
            Patch(facecolor=PAIR_F, edgecolor=PAIR_F, label="PairAcc"),
            Patch(facecolor=E2E_F, edgecolor=E2E_F, label="E2E"),
        ],
        ncol=2,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        frameon=False,
        handlelength=1.0,
        columnspacing=1.0,
        handletextpad=0.35,
        borderaxespad=0,
        fontsize=7.0,
    )
    fig.subplots_adjust(left=0.18, right=0.985, top=0.875, bottom=0.235)
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TRI Figure 5 options D, E, and F.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = read_full_data()
    stems = {
        "d": args.output_dir / "figure5_option_d_baseline_gain",
        "e": args.output_dir / "figure5_option_e_horizontal_bars",
        "f": args.output_dir / "figure5_option_f_vertical_bars",
    }
    save_variants(draw_baseline_gain(data), stems["d"], "TRI Figure 5 option D")
    save_variants(draw_horizontal_effect_bars(data), stems["e"], "TRI Figure 5 option E")
    save_variants(draw_vertical_effect_bars(data), stems["f"], "TRI Figure 5 option F")
    manifest = {
        "status": "Option F selected and refined (v3); preview not integrated into the paper",
        "selected": "option_f",
        "source": str(DATA),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "minimum_text_pt": 7.0,
        "png_dpi": 400,
        "pdf_fonttype": 42,
        "palette": {
            "pairacc": PAIR_F,
            "pairacc_light": PAIR_F_LIGHT,
            "e2e": E2E_F,
            "e2e_light": E2E_F_LIGHT,
            "source_note": "adapted from a Xiaohongshu scientific-figure ocean-breeze palette",
        },
        "scope": "Authored and source-derived only; no pooled effect; human rewrite excluded",
        "outputs": {
            "option_d": {"stem": str(stems["d"]), "size_inches": [3.35, 2.43]},
            "option_e": {"stem": str(stems["e"]), "size_inches": [3.35, 2.38]},
            "option_f": {"stem": str(stems["f"]), "size_inches": [3.35, 2.35]},
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
