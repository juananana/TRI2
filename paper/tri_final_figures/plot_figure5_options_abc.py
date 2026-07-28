#!/usr/bin/env python3
"""Generate three candidate representations for TRI Figure 5."""

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
from matplotlib.lines import Line2D
from PIL import Image


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "summary_csv" / "main_figure_paired_scores.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "figure5_options_abc_v1"

INK = "#30343F"
MUTED = "#69737A"
GRID = "#D9DEE2"
PAPER = "#FFFFFF"
QWEN = "#8F7897"
GLM = "#D97863"
DEEPSEEK = "#4F9189"
PAIR = "#8F7897"
E2E = "#D97863"
POSITIVE = "#F7F8F7"

MODEL_STYLE = {
    "Qwen3.5": ("Qwen", "o", QWEN),
    "GLM-5.1": ("GLM", "s", GLM),
    "DeepSeek": ("DeepSeek", "D", DEEPSEEK),
}

SPECS = [
    ("Authored", "Qwen3.5"),
    ("Authored", "GLM-5.1"),
    ("Source-derived", "Qwen3.5"),
    ("Source-derived", "GLM-5.1"),
    ("Source-derived", "DeepSeek"),
]

EXPECTED = {
    ("pairacc", "Authored", "Qwen3.5"): (25.0, 6.25, 46.154),
    ("pairacc", "Authored", "GLM-5.1"): (53.125, 28.571, 77.778),
    ("pairacc", "Source-derived", "Qwen3.5"): (3.333, -11.111, 20.0),
    ("pairacc", "Source-derived", "GLM-5.1"): (30.0, 0.0, 55.556),
    ("pairacc", "Source-derived", "DeepSeek"): (10.0, -10.0, 30.0),
    ("e2e", "Authored", "Qwen3.5"): (4.688, 0.0, 9.375),
    ("e2e", "Authored", "GLM-5.1"): (14.062, 8.397, 20.0),
    ("e2e", "Source-derived", "Qwen3.5"): (0.0, -6.667, 6.667),
    ("e2e", "Source-derived", "GLM-5.1"): (18.333, 8.333, 30.0),
    ("e2e", "Source-derived", "DeepSeek"): (3.333, -5.0, 11.667),
}


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.labelsize": 7.5,
            "axes.titlesize": 8.0,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "axes.linewidth": 0.65,
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


def read_data() -> dict[tuple[str, str, str], tuple[float, float, float]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    output: dict[tuple[str, str, str], tuple[float, float, float]] = {}
    for row in rows:
        key = (row["panel"], row["dataset"], row["model"])
        if key not in EXPECTED:
            continue
        observed = tuple(
            float(row[field])
            for field in ("difference_pp", "ci95_low_pp", "ci95_high_pp")
        )
        if observed != EXPECTED[key]:
            raise ValueError(f"frozen source mismatch for {key}: {observed}")
        output[key] = observed
    if set(output) != set(EXPECTED):
        raise ValueError(f"missing Figure 5 rows: {sorted(set(EXPECTED) - set(output))}")
    return output


def rounded(value: float) -> str:
    number = int(np.floor(value + 0.5)) if value >= 0 else int(np.ceil(value - 0.5))
    return f"{number:+d}" if number else "0"


def interval(
    ax: plt.Axes,
    values: tuple[float, float, float],
    x_or_y: float,
    *,
    horizontal: bool,
    color: str,
    marker: str,
    filled: bool,
    label_value: bool = True,
    line_style: str | tuple[int, tuple[float, ...]] = "solid",
) -> None:
    effect, low, high = values
    marker_face = color if filled else PAPER
    if horizontal:
        container = ax.errorbar(
            effect,
            x_or_y,
            xerr=[[effect - low], [high - effect]],
            fmt=marker,
            ms=4.2,
            mfc=marker_face,
            mec=color,
            mew=0.9,
            ecolor=color,
            elinewidth=0.95,
            capsize=2.0,
            capthick=0.8,
            zorder=3,
        )
        for collection in container[2]:
            collection.set_linestyle(line_style)
        if label_value:
            ax.annotate(
                rounded(effect),
                xy=(effect, x_or_y),
                xytext=(0, 5.0),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=7.0,
                color=INK,
                zorder=4,
            )
    else:
        container = ax.errorbar(
            x_or_y,
            effect,
            yerr=[[effect - low], [high - effect]],
            fmt=marker,
            ms=4.2,
            mfc=marker_face,
            mec=color,
            mew=0.9,
            ecolor=color,
            elinewidth=0.95,
            capsize=2.0,
            capthick=0.8,
            zorder=3,
        )
        for collection in container[2]:
            collection.set_linestyle(line_style)
        if label_value:
            ax.annotate(
                rounded(effect),
                xy=(x_or_y, effect),
                xytext=(4.0, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=7.0,
                color=INK,
                zorder=4,
            )


def clean_horizontal(ax: plt.Axes, limits: tuple[float, float], ticks: list[int]) -> None:
    ax.axvspan(0, limits[1], color=POSITIVE, zorder=0)
    ax.axvline(0, color=MUTED, lw=0.8, zorder=1)
    ax.set_xlim(*limits)
    ax.set_xticks(ticks)
    ax.grid(axis="x", color=GRID, lw=0.48, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.tick_params(axis="x", length=2.5, width=0.6, pad=2)
    ax.set_axisbelow(True)


def draw_twin_panels(
    data: dict[tuple[str, str, str], tuple[float, float, float]]
) -> plt.Figure:
    """Option A: equal-width endpoint panels."""
    configure()
    fig, (pair_ax, e2e_ax) = plt.subplots(
        1,
        2,
        figsize=(3.35, 2.35),
        sharey=True,
        gridspec_kw={"width_ratios": [1, 1], "wspace": 0.14},
    )
    y_positions = [4.15, 3.25, 1.65, 0.75, -0.15]
    for (dataset, model), y in zip(SPECS, y_positions, strict=True):
        label, marker, color = MODEL_STYLE[model]
        filled = dataset == "Authored"
        interval(
            pair_ax,
            data[("pairacc", dataset, model)],
            y,
            horizontal=True,
            color=color,
            marker=marker,
            filled=filled,
        )
        interval(
            e2e_ax,
            data[("e2e", dataset, model)],
            y,
            horizontal=True,
            color=color,
            marker=marker,
            filled=filled,
        )

    clean_horizontal(pair_ax, (-15, 82), [0, 40, 80])
    clean_horizontal(e2e_ax, (-10, 32), [0, 15, 30])
    pair_ax.set_title("A  PairAcc effect", loc="left", pad=3, weight="bold")
    e2e_ax.set_title("B  E2E effect", loc="left", pad=3, weight="bold")
    pair_ax.set_ylim(-0.65, 4.75)
    pair_ax.set_yticks(
        y_positions,
        [MODEL_STYLE[model][0] for _, model in SPECS],
    )
    pair_ax.axhline(2.45, color=GRID, lw=0.6, zorder=1)
    e2e_ax.axhline(2.45, color=GRID, lw=0.6, zorder=1)
    pair_ax.text(
        -0.47,
        4.65,
        "AUTHORED",
        transform=pair_ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=7.0,
        color=MUTED,
        weight="bold",
        clip_on=False,
    )
    pair_ax.text(
        -0.47,
        2.34,
        "SOURCE-DERIVED",
        transform=pair_ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=7.0,
        color=MUTED,
        weight="bold",
        clip_on=False,
    )
    fig.text(
        0.64,
        0.035,
        "Decision-visible − History-only (pp)",
        ha="center",
        va="bottom",
        fontsize=7.4,
        color=INK,
    )
    fig.subplots_adjust(left=0.31, right=0.985, top=0.88, bottom=0.21)
    return fig


def draw_shared_axis(
    data: dict[tuple[str, str, str], tuple[float, float, float]]
) -> plt.Figure:
    """Option B: both endpoints on one percentage-point scale."""
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.42))
    centers = [4.1, 3.2, 1.6, 0.7, -0.2]
    offsets = {"pairacc": 0.15, "e2e": -0.15}
    endpoint_style = {
        "pairacc": (PAIR, "PairAcc"),
        "e2e": (E2E, "E2E"),
    }
    for (dataset, model), center in zip(SPECS, centers, strict=True):
        _, marker, _ = MODEL_STYLE[model]
        filled = dataset == "Authored"
        for endpoint in ("pairacc", "e2e"):
            color, _ = endpoint_style[endpoint]
            interval(
                ax,
                data[(endpoint, dataset, model)],
                center + offsets[endpoint],
                horizontal=True,
                color=color,
                marker=marker,
                filled=filled,
                label_value=False,
                line_style="solid" if endpoint == "pairacc" else (0, (2.2, 1.5)),
            )

    clean_horizontal(ax, (-15, 82), [0, 20, 40, 60, 80])
    ax.set_ylim(-0.7, 4.7)
    ax.set_yticks(centers, [MODEL_STYLE[model][0] for _, model in SPECS])
    ax.axhline(2.4, color=GRID, lw=0.6, zorder=1)
    ax.text(
        -0.24,
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
        -0.24,
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
    ax.set_xlabel("Decision-visible − History-only (pp)")
    endpoint_handles = [
        Line2D([0], [0], color=PAIR, marker="o", lw=1.1, markersize=4, label="PairAcc"),
        Line2D([0], [0], color=E2E, marker="o", lw=1.1, ls=(0, (2.2, 1.5)), markersize=4, label="E2E"),
    ]
    ax.legend(
        handles=endpoint_handles,
        ncol=2,
        loc="lower left",
        bbox_to_anchor=(0.0, 1.005),
        frameon=False,
        handlelength=1.6,
        columnspacing=1.0,
        borderaxespad=0,
        fontsize=7.0,
    )
    fig.subplots_adjust(left=0.30, right=0.985, top=0.87, bottom=0.18)
    return fig


def draw_vertical_coefficients(
    data: dict[tuple[str, str, str], tuple[float, float, float]]
) -> plt.Figure:
    """Option C: vertical grouped coefficient plot."""
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.50))
    centers = [0.0, 1.0, 2.35, 3.35, 4.35]
    offsets = {"pairacc": -0.13, "e2e": 0.13}
    endpoint_style = {"pairacc": (PAIR, "PairAcc"), "e2e": (E2E, "E2E")}
    for (dataset, model), center in zip(SPECS, centers, strict=True):
        _, marker, _ = MODEL_STYLE[model]
        filled = dataset == "Authored"
        for endpoint in ("pairacc", "e2e"):
            color, _ = endpoint_style[endpoint]
            interval(
                ax,
                data[(endpoint, dataset, model)],
                center + offsets[endpoint],
                horizontal=False,
                color=color,
                marker=marker,
                filled=filled,
                label_value=False,
                line_style="solid" if endpoint == "pairacc" else (0, (2.2, 1.5)),
            )

    ax.axhspan(0, 82, color=POSITIVE, zorder=0)
    ax.axhline(0, color=MUTED, lw=0.8, zorder=1)
    ax.axvline(1.67, color=GRID, lw=0.65, zorder=1)
    ax.set_xlim(-0.55, 4.90)
    ax.set_ylim(-15, 82)
    ax.set_yticks([-10, 0, 20, 40, 60, 80])
    ax.set_ylabel("Effect of Decision-visible (pp)")
    ax.set_xticks(centers, [MODEL_STYLE[model][0] for _, model in SPECS])
    ax.grid(axis="y", color=GRID, lw=0.48, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=3)
    ax.tick_params(axis="y", length=2.5, width=0.6, pad=2)
    ax.text(
        0.5,
        -0.19,
        "AUTHORED",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=7.0,
        color=MUTED,
        weight="bold",
    )
    ax.text(
        3.35,
        -0.19,
        "SOURCE-DERIVED",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=7.0,
        color=MUTED,
        weight="bold",
    )
    endpoint_handles = [
        Line2D([0], [0], color=PAIR, marker="o", lw=1.1, markersize=4, label="PairAcc"),
        Line2D([0], [0], color=E2E, marker="o", lw=1.1, ls=(0, (2.2, 1.5)), markersize=4, label="E2E"),
    ]
    ax.legend(
        handles=endpoint_handles,
        ncol=2,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.005),
        frameon=False,
        handlelength=1.5,
        columnspacing=1.1,
        borderaxespad=0,
        fontsize=7.0,
    )
    fig.subplots_adjust(left=0.18, right=0.985, top=0.88, bottom=0.23)
    return fig


def save_variants(fig: plt.Figure, stem: Path, creator: str) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"), metadata={"Creator": creator})
    fig.savefig(stem.with_suffix(".svg"))
    png = stem.with_suffix(".png")
    fig.savefig(png, dpi=400)
    plt.close(fig)
    with Image.open(png).convert("RGB") as source:
        source.convert("L").save(stem.with_name(stem.name + "_grayscale").with_suffix(".png"))
        rgb = np.asarray(source, dtype=np.float32) / 255.0
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
            stem.with_name(stem.name + "_deuteranopia").with_suffix(".png")
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TRI Figure 5 options A, B, and C.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = read_data()
    stems = {
        "a": args.output_dir / "figure5_option_a_equal_panels",
        "b": args.output_dir / "figure5_option_b_shared_axis",
        "c": args.output_dir / "figure5_option_c_vertical_coefficients",
    }
    save_variants(draw_twin_panels(data), stems["a"], "TRI Figure 5 option A")
    save_variants(draw_shared_axis(data), stems["b"], "TRI Figure 5 option B")
    save_variants(draw_vertical_coefficients(data), stems["c"], "TRI Figure 5 option C")
    manifest = {
        "status": "Figure 5 A/B/C previews only; not integrated into the paper",
        "source": str(DATA),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "minimum_text_pt": 7.0,
        "png_dpi": 400,
        "pdf_fonttype": 42,
        "scope": "Authored and source-derived only; no pooled effect; human rewrite excluded",
        "outputs": {
            "option_a": {"stem": str(stems["a"]), "size_inches": [3.35, 2.35]},
            "option_b": {"stem": str(stems["b"]), "size_inches": [3.35, 2.42]},
            "option_c": {"stem": str(stems["c"]), "size_inches": [3.35, 2.50]},
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
