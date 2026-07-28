#!/usr/bin/env python3
"""Draw the compact TRI decision-visibility effect matrix (v6)."""

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
from matplotlib.colors import to_rgb
from matplotlib.patches import Rectangle
from PIL import Image


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "summary_csv" / "main_figure_paired_scores.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "result_closure_v6"

INK = "#30343F"
MUTED = "#69737A"
GRID = "#D9DEE2"
PAPER = "#FFFFFF"
QWEN = "#8F8DBB"
GLM = "#DA6B64"
DEEPSEEK = "#4F9EA0"

MODEL_STYLE = {
    "Qwen3.5": ("Qwen", QWEN),
    "GLM-5.1": ("GLM", GLM),
    "DeepSeek": ("DeepSeek", DEEPSEEK),
}

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
            "axes.titlesize": 8.1,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 6.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "text.color": INK,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )


def read_rows() -> dict[tuple[str, str, str], dict[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    selected = {
        (row["panel"], row["dataset"], row["model"]): row
        for row in rows
        if (row["panel"], row["dataset"], row["model"]) in EXPECTED
    }
    if set(selected) != set(EXPECTED):
        raise ValueError(f"unexpected transfer cells: {sorted(selected)}")
    for key, expected in EXPECTED.items():
        row = selected[key]
        observed = tuple(
            float(row[field])
            for field in ("difference_pp", "ci95_low_pp", "ci95_high_pp")
        )
        if observed != expected:
            raise ValueError(f"frozen source mismatch for {key}: {observed}")
    return selected


def blend(color: str, amount: float = 0.22) -> tuple[float, float, float]:
    rgb = np.asarray(to_rgb(color))
    return tuple((1.0 - amount) + amount * rgb)


def rounded(value: float) -> str:
    rounded_value = int(np.floor(value + 0.5)) if value >= 0 else int(np.ceil(value - 0.5))
    return f"{rounded_value:+d}" if rounded_value != 0 else "0"


def draw(rows: dict[tuple[str, str, str], dict[str, str]]) -> plt.Figure:
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.15))

    specs = [
        ("Authored", "Qwen3.5", 3.70),
        ("Authored", "GLM-5.1", 2.82),
        ("Source-derived", "Qwen3.5", 1.35),
        ("Source-derived", "GLM-5.1", 0.47),
        ("Source-derived", "DeepSeek", -0.41),
    ]
    panels = [("pairacc", 0.0, "PairAcc (pp)"), ("e2e", 1.0, "E2E (pp)")]

    for dataset, model, y in specs:
        short, color = MODEL_STYLE[model]
        ax.text(-0.54, y, short, ha="right", va="center", fontsize=7.2, color=INK)
        for panel, x, _title in panels:
            row = rows[(panel, dataset, model)]
            effect = float(row["difference_pp"])
            low = float(row["ci95_low_pp"])
            high = float(row["ci95_high_pp"])
            excludes_zero = low > 0 or high < 0
            ax.add_patch(
                Rectangle(
                    (x - 0.39, y - 0.31),
                    0.78,
                    0.62,
                    facecolor=blend(color) if excludes_zero else PAPER,
                    edgecolor=color,
                    linewidth=0.85,
                    linestyle="solid" if excludes_zero else (0, (2.4, 1.7)),
                    zorder=2,
                )
            )
            ax.text(
                x,
                y + 0.075,
                rounded(effect),
                ha="center",
                va="center",
                fontsize=7.6,
                color=INK,
                weight="bold" if excludes_zero else "normal",
                zorder=3,
            )
            ax.text(
                x,
                y - 0.14,
                f"[{rounded(low)}, {rounded(high)}]",
                ha="center",
                va="center",
                fontsize=7.0,
                color=MUTED,
                zorder=3,
            )

    ax.axhline(2.12, color=GRID, lw=0.65, zorder=1)
    ax.text(-0.54, 4.25, "AUTHORED", ha="right", va="center", fontsize=7.0, weight="bold")
    ax.text(
        -0.54,
        1.92,
        "SOURCE-DERIVED",
        ha="right",
        va="center",
        fontsize=7.0,
        color="#52767B",
        weight="bold",
    )
    for _panel, x, title in panels:
        ax.text(x, 4.25, title, ha="center", va="center", fontsize=7.6, weight="bold")

    ax.text(
        0.50,
        -1.00,
        "filled: CI excludes 0     dashed: CI includes 0",
        ha="center",
        va="center",
        fontsize=6.8,
        color=MUTED,
    )

    ax.set_xlim(-1.35, 1.50)
    ax.set_ylim(-1.20, 4.48)
    ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.985, top=0.97, bottom=0.04)
    return fig


def save(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"), metadata={"Creator": "TRI transfer effect matrix v6"})
    fig.savefig(stem.with_suffix(".svg"))
    png = stem.with_suffix(".png")
    fig.savefig(png, dpi=400)
    plt.close(fig)
    with Image.open(png).convert("RGB") as image:
        image.convert("L").save(stem.with_name(stem.name + "_grayscale").with_suffix(".png"))
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
            stem.with_name(stem.name + "_deuteranopia").with_suffix(".png")
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the TRI transfer effect matrix v6.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    stem = args.output_dir / "result_decision_transfer_matrix"
    save(draw(read_rows()), stem)
    manifest = {
        "status": "main-paper transfer matrix v6; no new experiment",
        "source": str(DATA),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "output_stem": str(stem),
        "size_inches": [3.35, 2.15],
        "minimum_text_pt": 7.0,
        "png_dpi": 400,
        "pdf_fonttype": 42,
        "encoding": "cell text gives rounded effect and CI; solid fill means CI excludes zero",
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
