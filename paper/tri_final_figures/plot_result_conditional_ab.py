#!/usr/bin/env python3
"""Draw an isolated Figure 4 redesign candidate from the frozen TRI summary CSV."""

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
from matplotlib.patches import Patch, Rectangle
from PIL import Image


ROOT = Path(__file__).resolve().parent
REPO_DATA = ROOT / "data" / "summary_csv" / "v7_shared_eligible_pairacc_and_substitution.csv"
SNAPSHOT_DATA = ROOT.parent / "data" / "figure_ready" / "v7_shared_eligible_pairacc_and_substitution.csv"
FALLBACK_DATA = Path(
    "./paper/tri_final_figures/"
    "data/summary_csv/v7_shared_eligible_pairacc_and_substitution.csv"
)
DATA = next(path for path in (REPO_DATA, SNAPSHOT_DATA, FALLBACK_DATA) if path.exists())
if REPO_DATA.exists():
    STEM = ROOT / "outputs" / "result_closure_v6" / "result_conditional_pairing_ab"
elif SNAPSHOT_DATA.exists():
    STEM = ROOT.parent / "figure_outputs" / "result_closure_v5" / "result_conditional_pairing_ab"
else:
    STEM = ROOT / "figure4-redesign-final"

INK = "#264A56"
MUTED = "#5F6B70"
GRID = "#D6E0DE"
PAPER = "#FFFFFF"
QWEN = "#8B6F8E"
GLM = "#E56D4E"
DEEPSEEK = "#407A7F"

MODELS = [
    ("Qwen3.5", "Qwen", "o", QWEN),
    ("GLM-5.1", "GLM", "s", GLM),
    ("DeepSeek", "DeepSeek", "D", DEEPSEEK),
]
HATCHES = {"Qwen3.5": "", "GLM-5.1": "//", "DeepSeek": "xx"}

EXPECTED = {
    ("Qwen3.5", "Generic"): (66, 41, 7, 80, 8.75, 2.5, 16.25),
    ("Qwen3.5", "CTA"): (66, 0, 31, 80, 38.75, 26.25, 51.25),
    ("GLM-5.1", "Generic"): (70, 30, 15, 80, 18.75, 8.75, 30.0),
    ("GLM-5.1", "CTA"): (70, 0, 66, 80, 82.5, 73.75, 90.0),
    ("DeepSeek", "Generic"): (69, 50, 17, 80, 21.25, 11.25, 32.5),
    ("DeepSeek", "CTA"): (69, 0, 64, 80, 80.0, 70.0, 88.75),
}


def read_rows() -> dict[tuple[str, str], dict[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    selected = {
        (row["model"], row["controller"]): row
        for row in rows
        if row["controller"] in {"Generic", "CTA"}
    }
    if set(selected) != set(EXPECTED):
        raise ValueError(f"unexpected data cells: {sorted(selected)}")
    for key, expected in EXPECTED.items():
        row = selected[key]
        observed = (
            int(row["shared_eligible"]),
            int(row["substitutions"]),
            int(row["pairacc_both_correct"]),
            int(row["pairacc_pairs"]),
            float(row["pairacc_pct"]),
            float(row["pairacc_ci95_low_pct"]),
            float(row["pairacc_ci95_high_pct"]),
        )
        if observed != expected:
            raise ValueError(f"frozen source mismatch for {key}: {observed}")
    return selected


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return 100 * (center - half), 100 * (center + half)


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


def clean(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.45, alpha=0.9, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.4, width=0.65, pad=2)


def add_group_cue(
    ax: plt.Axes,
    bounds: tuple[float, float, float, float],
    *,
    style: str,
) -> None:
    """Group endpoints without capsule- or ellipse-like containers."""
    x, y, width, height = bounds
    if style == "none":
        return
    if style == "band":
        ax.add_patch(
            Rectangle(
                (x, y),
                width,
                height,
                transform=ax.transAxes,
                facecolor="#F1F4F4",
                edgecolor="none",
                zorder=0.5,
                clip_on=False,
            )
        )
        return
    if style == "brackets":
        cap = min(0.035, width * 0.16)
        line_style = {
            "transform": ax.transAxes,
            "color": MUTED,
            "linewidth": 0.70,
            "linestyle": (0, (2.4, 2.0)),
            "zorder": 0.5,
            "clip_on": False,
        }
        ax.plot([x, x], [y, y + height], **line_style)
        ax.plot([x, x + cap], [y, y], **line_style)
        ax.plot([x, x + cap], [y + height, y + height], **line_style)
        right = x + width
        ax.plot([right, right], [y, y + height], **line_style)
        ax.plot([right - cap, right], [y, y], **line_style)
        ax.plot([right - cap, right], [y + height, y + height], **line_style)
        return
    raise ValueError(f"unknown grouping style: {style}")


def draw(
    rows: dict[tuple[str, str], dict[str, str]],
    *,
    grouping_style: str = "none",
) -> plt.Figure:
    configure()
    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(3.35, 2.16),
        gridspec_kw={"width_ratios": [1.0, 1.0], "wspace": 0.30},
    )

    # Panel A: the markers are controller conditions, not world states.
    add_group_cue(ax_a, (0.04, 0.315, 0.30, 0.57), style=grouping_style)
    add_group_cue(ax_a, (0.66, 0.065, 0.31, 0.22), style=grouping_style)

    endpoint_offsets = [-0.11, 0.0, 0.11]
    for endpoint_offset, (model, _short, marker, color) in zip(
        endpoint_offsets, MODELS, strict=True
    ):
        generic = rows[(model, "Generic")]
        cta = rows[(model, "CTA")]
        values = []
        intervals = []
        for row in (generic, cta):
            n = int(row["shared_eligible"])
            k = int(row["substitutions"])
            values.append(100 * k / n)
            intervals.append(wilson(k, n))
        endpoint_xs = [endpoint_offset, 1 + endpoint_offset]
        ax_a.plot(endpoint_xs, values, color=color, lw=0.95, zorder=2)
        for x, value, interval, filled in zip(
            endpoint_xs, values, intervals, [False, True], strict=True
        ):
            ax_a.errorbar(
                x,
                value,
                yerr=[[value - interval[0]], [interval[1] - value]],
                fmt="none",
                ecolor=color,
                elinewidth=0.75,
                capsize=3.0,
                capthick=0.7,
                zorder=3,
            )
            ax_a.plot(
                x,
                value,
                marker=marker,
                ms=3.0,
                mfc=color if filled else PAPER,
                mec=color,
                mew=0.75,
                linestyle="none",
                zorder=4,
            )
    ax_a.set_xlim(-0.30, 1.30)
    ax_a.set_ylim(-20, 105)
    ax_a.set_xticks([0, 1], ["Generic", "CTA"])
    ax_a.set_yticks([-20, 0, 25, 50, 75, 100])
    ax_a.set_ylabel("Conditional substitution (%)")
    ax_a.set_title("A  Substitution", loc="left", pad=3, weight="bold")
    clean(ax_a)

    # Panel B: two compact controller groups. Exact counts remain in the paper text.
    centers = np.array([0.0, 1.0])
    offsets = [-0.22, 0.0, 0.22]
    width = 0.18
    for offset, (model, _short, _marker, color) in zip(offsets, MODELS, strict=True):
        values = []
        lows = []
        highs = []
        for controller in ("Generic", "CTA"):
            row = rows[(model, controller)]
            value = float(row["pairacc_pct"])
            values.append(value)
            lows.append(float(row["pairacc_ci95_low_pct"]))
            highs.append(float(row["pairacc_ci95_high_pct"]))
        xs = centers + offset
        ax_b.bar(
            xs,
            values,
            width=width,
            color=color,
            alpha=0.78,
            edgecolor=color,
            linewidth=0.7,
            hatch=HATCHES[model],
            zorder=2,
        )
        ax_b.errorbar(
            xs,
            values,
            yerr=[np.array(values) - np.array(lows), np.array(highs) - np.array(values)],
            fmt="none",
            ecolor=INK,
            elinewidth=0.75,
            capsize=2.0,
            capthick=0.7,
            zorder=3,
        )
        for x, value, high in zip(xs, values, highs, strict=True):
            ax_b.text(
                x,
                high + 2.2,
                f"{int(value + 0.5)}",
                ha="center",
                va="bottom",
                fontsize=7.0,
                color=INK,
            )
    ax_b.set_xlim(-0.48, 1.48)
    ax_b.set_ylim(0, 110)
    ax_b.set_xticks(centers, ["Generic", "CTA"])
    ax_b.set_yticks([0, 25, 50, 75, 100])
    ax_b.set_ylabel("PairAcc (%)")
    ax_b.set_title("B  PairAcc", loc="left", pad=3, weight="bold")
    clean(ax_b)

    handles = [
        Patch(
            facecolor=color,
            edgecolor=color,
            hatch=HATCHES[model],
            label=short,
        )
        for model, short, _marker, color in MODELS
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.75, 0.985),
        ncol=3,
        frameon=False,
        handlelength=0.7,
        handletextpad=0.25,
        columnspacing=0.55,
    )

    fig.subplots_adjust(left=0.15, right=0.985, top=0.84, bottom=0.20)
    return fig


def save(fig: plt.Figure, *, stem: Path, grouping_style: str) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"), metadata={"Creator": "TRI Figure 4 grouping refinement"})
    fig.savefig(stem.with_suffix(".svg"))
    png = stem.with_suffix(".png")
    fig.savefig(png, dpi=400)
    plt.close(fig)
    with Image.open(png).convert("RGB") as image:
        image.convert("L").save(stem.with_name(stem.name + "-grayscale").with_suffix(".png"))
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
            stem.with_name(stem.name + "-deuteranopia").with_suffix(".png")
        )
    manifest = {
        "status": "unified Figure 4 A/B result with direct endpoints and no decorative enclosure",
        "grouping_style": grouping_style,
        "source": str(DATA),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "size_inches": [3.35, 2.16],
        "minimum_text_pt": 7.0,
        "png_dpi": 400,
        "pdf_fonttype": 42,
        "panel_a": f"Generic open to CTA filled; grouping={grouping_style}; visible lower caps at the zero boundary; Wilson 95% CI; y-axis -20 to 105",
        "panel_b": "controller-grouped bars with direct integer percentages; cluster-bootstrap 95% CI; exact counts retained outside the plot",
    }
    manifest_path = stem.with_name(stem.name + "-manifest").with_suffix(".json")
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grouping", choices=("none", "band", "brackets"), default="none")
    parser.add_argument("--stem", type=Path, default=STEM)
    args = parser.parse_args()
    save(
        draw(read_rows(), grouping_style=args.grouping),
        stem=args.stem,
        grouping_style=args.grouping,
    )


if __name__ == "__main__":
    main()
