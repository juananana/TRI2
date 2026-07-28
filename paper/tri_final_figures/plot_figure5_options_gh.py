#!/usr/bin/env python3
"""Generate line-light Figure 5 candidates using uncertainty bands."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

from plot_figure5_options_abc import (
    DATA,
    E2E,
    GRID,
    INK,
    MODEL_STYLE,
    MUTED,
    PAIR,
    PAPER,
    POSITIVE,
    ROOT,
    SPECS,
    configure,
    rounded,
    save_variants,
)
from plot_figure5_options_def import BASE, REMAINDER, read_full_data


DEFAULT_OUTPUT = ROOT / "outputs" / "figure5_options_gh_v1"


def group_rows(ax: plt.Axes, centers: list[float], *, show_headings: bool) -> None:
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


def configure_effect_axis(
    ax: plt.Axes,
    limits: tuple[float, float],
    ticks: list[int],
) -> None:
    ax.axvspan(0, limits[1], color=POSITIVE, zorder=0)
    ax.axvline(0, color=MUTED, lw=0.75, zorder=1)
    ax.set_xlim(*limits)
    ax.set_xticks(ticks)
    ax.set_ylim(-0.65, 4.70)
    ax.grid(axis="x", color=GRID, lw=0.48, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.tick_params(axis="x", length=2.5, width=0.6, pad=2)
    ax.set_axisbelow(True)


def draw_interval_ribbons(data: dict[tuple[str, str, str], dict[str, float]]) -> plt.Figure:
    """Option G: CI ribbons with a compact point-estimate stripe."""
    configure()
    fig, (pair_ax, e2e_ax) = plt.subplots(
        1,
        2,
        figsize=(3.35, 2.35),
        sharey=True,
        gridspec_kw={"width_ratios": [1, 1], "wspace": 0.14},
    )
    centers = [4.1, 3.2, 1.6, 0.7, -0.2]
    endpoint_specs = [
        (pair_ax, "pairacc", (-15, 82), [0, 40, 80], "A  PairAcc effect", 2.2),
        (e2e_ax, "e2e", (-10, 32), [0, 15, 30], "B  E2E effect", 1.0),
    ]
    for ax, endpoint, limits, ticks, title, stripe_width in endpoint_specs:
        for (dataset, model), y in zip(SPECS, centers, strict=True):
            row = data[(endpoint, dataset, model)]
            _, _, color = MODEL_STYLE[model]
            ax.add_patch(
                Rectangle(
                    (row["low"], y - 0.19),
                    row["high"] - row["low"],
                    0.38,
                    facecolor=color,
                    edgecolor="none",
                    alpha=0.23,
                    zorder=2,
                )
            )
            ax.add_patch(
                Rectangle(
                    (row["effect"] - stripe_width / 2, y - 0.23),
                    stripe_width,
                    0.46,
                    facecolor=color,
                    edgecolor=color,
                    linewidth=0.6,
                    zorder=3,
                )
            )
            ax.text(
                row["effect"],
                y + 0.29,
                rounded(row["effect"]),
                ha="center",
                va="bottom",
                fontsize=7.0,
                color=INK,
                weight="bold" if row["low"] > 0 else "normal",
                zorder=4,
            )
        configure_effect_axis(ax, limits, ticks)
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
    fig.legend(
        handles=[
            Patch(facecolor=MUTED, alpha=0.23, edgecolor="none", label="95% CI"),
            Patch(facecolor=MUTED, edgecolor=MUTED, label="estimate"),
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
    fig.subplots_adjust(left=0.31, right=0.985, top=0.84, bottom=0.20)
    return fig


def configure_rate_axis(ax: plt.Axes) -> None:
    ax.set_xlim(0, 105)
    ax.set_xticks([0, 50, 100])
    ax.set_ylim(-0.65, 4.70)
    ax.grid(axis="x", color=GRID, lw=0.48, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.tick_params(axis="x", length=2.5, width=0.6, pad=2)
    ax.set_axisbelow(True)


def draw_nested_rate_bands(data: dict[tuple[str, str, str], dict[str, float]]) -> plt.Figure:
    """Option H: actual-rate tracks with uncertainty halos instead of whiskers."""
    configure()
    fig, (pair_ax, e2e_ax) = plt.subplots(
        1,
        2,
        figsize=(3.35, 2.40),
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
            low_final = max(0.0, row["baseline"] + row["low"])
            high_final = min(105.0, row["baseline"] + row["high"])
            ax.add_patch(
                Rectangle(
                    (low_final, y - 0.30),
                    high_final - low_final,
                    0.60,
                    facecolor=color,
                    edgecolor="none",
                    alpha=0.14,
                    zorder=1,
                )
            )
            ax.barh(y, 100, height=0.38, color=REMAINDER, edgecolor="none", zorder=2)
            ax.barh(y, row["baseline"], height=0.38, color=BASE, edgecolor="none", zorder=3)
            ax.barh(
                y,
                row["visible"] - row["baseline"],
                left=row["baseline"],
                height=0.38,
                color=color if row["low"] > 0 else PAPER,
                edgecolor=color,
                linewidth=0.65,
                zorder=4,
            )
            ax.text(
                min(max(row["visible"], 5.0), 98.0),
                y + 0.28,
                f"Δ{rounded(row['effect'])}",
                ha="center",
                va="bottom",
                fontsize=7.0,
                color=INK,
                weight="bold" if row["low"] > 0 else "normal",
                zorder=5,
            )
        configure_rate_axis(ax)
        ax.set_title(title, loc="left", pad=3, weight="bold")
        group_rows(ax, centers, show_headings=ax is pair_ax)

    fig.legend(
        handles=[
            Patch(facecolor=BASE, edgecolor="none", label="History-only"),
            Patch(facecolor=MUTED, alpha=0.14, edgecolor="none", label="95% CI halo"),
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TRI Figure 5 options G and H.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = read_full_data()
    stems = {
        "g": args.output_dir / "figure5_option_g_interval_ribbons",
        "h": args.output_dir / "figure5_option_h_nested_rate_bands",
    }
    save_variants(draw_interval_ribbons(data), stems["g"], "TRI Figure 5 option G")
    save_variants(draw_nested_rate_bands(data), stems["h"], "TRI Figure 5 option H")
    manifest = {
        "status": "Figure 5 G/H line-light previews only; not integrated into the paper",
        "source": str(DATA),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "minimum_text_pt": 7.0,
        "png_dpi": 400,
        "pdf_fonttype": 42,
        "scope": "Authored and source-derived only; no pooled effect; human rewrite excluded",
        "outputs": {
            "option_g": {"stem": str(stems["g"]), "size_inches": [3.35, 2.35]},
            "option_h": {"stem": str(stems["h"]), "size_inches": [3.35, 2.40]},
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
