#!/usr/bin/env python3
"""Generate two same-denominator candidates for TRI Figure 3."""

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
from matplotlib.patches import Patch
from PIL import Image


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "summary_csv" / "matched_pairacc_and_marginals.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "figure3_option_c_v5_compact_selected"

INK = "#30343F"
MUTED = "#69737A"
GRID = "#D9DEE2"
PAPER = "#FFFFFF"
PRESERVE = "#D97863"
PRESERVE_LIGHT = "#F2D6CE"
REEVALUATE = "#4F9189"
REEVALUATE_LIGHT = "#C8DED9"
PAIR = "#9B7088"
PAIR_EDGE = "#80576E"
NEITHER = "#D8D4CF"
NEITHER_EDGE = "#A7A099"

ROWS = [
    ("Always lock", "model-independent", "Always-Lock+validity"),
    ("Always reeval.", "model-independent", "Always-Reevaluate"),
    ("Generic Q", "Qwen3.5", "Generic"),
    ("Generic G", "GLM-5.1", "Generic"),
    ("CTA Q", "Qwen3.5", "CTA"),
    ("CTA G", "GLM-5.1", "CTA"),
    ("Rule*", "model-independent", "Rule v2 (post-hoc)"),
]

EXPECTED = {
    "Always lock": (32, 0, 0, 32),
    "Always reeval.": (0, 32, 0, 32),
    "Generic Q": (3, 32, 3, 32),
    "Generic G": (7, 29, 7, 32),
    "CTA Q": (31, 31, 30, 32),
    "CTA G": (31, 32, 31, 32),
    "Rule*": (30, 30, 28, 32),
}


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.labelsize": 7.5,
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


def read_data() -> list[dict[str, int | str | float]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))

    output: list[dict[str, int | str | float]] = []
    for label, model, controller in ROWS:
        matches = [
            row
            for row in source
            if row["dataset"] == "v3"
            and row["model"] == model
            and row["controller"] == controller
            and row["slice"] == "changed_winner_core"
        ]
        if len(matches) != 1:
            raise ValueError(f"expected one changed-winner row for {label}, found {len(matches)}")
        row = matches[0]
        observed = (
            int(row["preserve_correct"]),
            int(row["reevaluate_correct"]),
            int(row["both_correct"]),
            int(row["pairs"]),
        )
        if observed != EXPECTED[label]:
            raise ValueError(f"frozen source mismatch for {label}: {observed}")
        preserve, reevaluate, both, pairs = observed
        preserve_only = preserve - both
        reevaluate_only = reevaluate - both
        neither = pairs - both - preserve_only - reevaluate_only
        if min(both, preserve_only, reevaluate_only, neither) < 0:
            raise ValueError(f"invalid pair decomposition for {label}")
        if both + preserve_only + reevaluate_only + neither != pairs:
            raise ValueError(f"pair decomposition does not sum to {pairs} for {label}")
        output.append(
            {
                "label": label,
                "pairs": pairs,
                "preserve": preserve,
                "reevaluate": reevaluate,
                "both": both,
                "preserve_only": preserve_only,
                "reevaluate_only": reevaluate_only,
                "neither": neither,
                "preserve_pct": 100.0 * preserve / pairs,
                "reevaluate_pct": 100.0 * reevaluate / pairs,
                "pairacc_pct": 100.0 * both / pairs,
            }
        )
    return output


def add_group_separators(ax: plt.Axes) -> None:
    for y in [4.5, 2.5, 0.5]:
        ax.axhline(y, color=GRID, lw=0.55, zorder=0)


def draw_outcome_composition(data: list[dict[str, int | str | float]]) -> plt.Figure:
    """Show the mutually exclusive outcome of each matched pair."""
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.25))
    y = np.arange(len(data))[::-1]
    categories = [
        ("both", "Both correct", PAIR, PAIR_EDGE),
        ("preserve_only", "Preserve only", PRESERVE_LIGHT, PRESERVE),
        ("reevaluate_only", "Reeval. only", REEVALUATE_LIGHT, REEVALUATE),
        ("neither", "Neither", NEITHER, NEITHER_EDGE),
    ]
    left = np.zeros(len(data))
    for key, _, color, edge in categories:
        values = np.asarray([int(row[key]) for row in data])
        ax.barh(
            y,
            values,
            left=left,
            height=0.56,
            color=color,
            edgecolor=edge,
            linewidth=0.50,
            zorder=2,
        )
        left += values

    for yi, row in zip(y, data, strict=True):
        both = int(row["both"])
        if both >= 3:
            ax.text(
                both / 2,
                yi,
                str(both),
                ha="center",
                va="center",
                fontsize=7.0,
                color=PAPER,
                weight="bold",
                zorder=3,
            )
    add_group_separators(ax)
    ax.set_xlim(0, 32.6)
    ax.set_ylim(-0.65, 6.65)
    ax.set_yticks(y, [str(row["label"]) for row in data])
    ax.set_xticks([0, 8, 16, 24, 32])
    ax.set_xlabel("Changed-winner pairs (n = 32)")
    ax.tick_params(axis="y", length=0, pad=4)
    ax.tick_params(axis="x", length=2.5, width=0.65, pad=2)
    ax.grid(axis="x", color=GRID, lw=0.45, alpha=0.82, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    handles = [
        Patch(facecolor=color, edgecolor=edge, linewidth=0.65, label=label)
        for _, label, color, edge in categories
    ]
    ax.legend(
        handles=handles,
        ncol=2,
        loc="lower left",
        bbox_to_anchor=(-0.01, 1.01),
        frameon=False,
        handlelength=1.15,
        handleheight=0.75,
        columnspacing=0.9,
        handletextpad=0.35,
        borderaxespad=0,
        fontsize=7.0,
    )
    fig.subplots_adjust(left=0.31, right=0.98, top=0.81, bottom=0.19)
    return fig


def draw_grouped_endpoints(data: list[dict[str, int | str | float]]) -> plt.Figure:
    """Compare all three changed-winner endpoints on the same denominator."""
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.62))
    centers = np.arange(len(data))[::-1]
    bar_height = 0.15
    offsets = [0.19, 0.0, -0.19]
    series = [
        ("preserve_pct", "Preserve", PRESERVE_LIGHT, PRESERVE),
        ("reevaluate_pct", "Reevaluate", REEVALUATE_LIGHT, REEVALUATE),
        ("pairacc_pct", "PairAcc", PAIR, PAIR_EDGE),
    ]
    for (key, _, fill, edge), offset in zip(series, offsets, strict=True):
        values = [float(row[key]) for row in data]
        ax.barh(
            centers + offset,
            values,
            height=bar_height,
            color=fill,
            edgecolor=edge,
            linewidth=0.52,
            zorder=2,
        )

    for center, row in zip(centers, data, strict=True):
        pairacc = float(row["pairacc_pct"])
        ax.text(
            max(pairacc + 1.5, 3.0),
            center - 0.19,
            f"{int(row['both'])}/32",
            ha="left",
            va="center",
            fontsize=7.0,
            color=PAIR_EDGE if pairacc else MUTED,
            weight="bold" if pairacc >= 87.5 else "normal",
            zorder=3,
        )

    add_group_separators(ax)
    ax.axvline(100, color=GRID, lw=0.55, zorder=0)
    ax.set_xlim(0, 112)
    ax.set_ylim(-0.62, 6.62)
    ax.set_yticks(centers, [str(row["label"]) for row in data])
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Accuracy on changed-winner pairs (%)")
    ax.tick_params(axis="y", length=0, pad=4)
    ax.tick_params(axis="x", length=2.5, width=0.65, pad=2)
    ax.grid(axis="x", color=GRID, lw=0.45, alpha=0.82, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    handles = [
        Patch(facecolor=fill, edgecolor=edge, linewidth=0.65, label=label)
        for _, label, fill, edge in series
    ]
    ax.legend(
        handles=handles,
        ncol=3,
        loc="lower left",
        bbox_to_anchor=(-0.01, 1.015),
        frameon=False,
        handlelength=1.1,
        handleheight=0.75,
        columnspacing=0.75,
        handletextpad=0.3,
        borderaxespad=0,
        fontsize=7.0,
    )
    fig.subplots_adjust(left=0.31, right=0.985, top=0.88, bottom=0.17)
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
    parser = argparse.ArgumentParser(description="Generate TRI Figure 3 options C and D.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = read_data()
    option_c = args.output_dir / "figure3_option_c_pair_outcomes"
    option_d = args.output_dir / "figure3_option_d_grouped_endpoints"
    save_variants(draw_outcome_composition(data), option_c, "TRI Figure 3 option C pair outcomes")
    save_variants(draw_grouped_endpoints(data), option_d, "TRI Figure 3 option D grouped endpoints")
    manifest = {
        "status": "Option C selected for Figure 3; preview not integrated into the paper",
        "selected": "option_c",
        "source": str(DATA),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "slice": "v3 changed_winner_core",
        "common_denominator": 32,
        "minimum_text_pt": 7.0,
        "png_dpi": 400,
        "pdf_fonttype": 42,
        "palette": {
            "preserve": PRESERVE,
            "reevaluate": REEVALUATE,
            "pairacc": PAIR,
            "neither": NEITHER,
        },
        "outputs": {
            "option_c": {"stem": str(option_c), "size_inches": [3.35, 2.25]},
            "option_d": {"stem": str(option_d), "size_inches": [3.35, 2.62]},
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
