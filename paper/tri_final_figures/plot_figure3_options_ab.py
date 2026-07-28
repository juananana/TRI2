#!/usr/bin/env python3
"""Generate two candidate representations for TRI Figure 3."""

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
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.patches import Rectangle
from PIL import Image


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "summary_csv" / "matched_pairacc_and_marginals.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "figure3_options_ab_v1"

INK = "#30343F"
MUTED = "#69737A"
GRID = "#D9DEE2"
PAPER = "#FFFFFF"
QWEN = "#8F8DBB"
GLM = "#DA6B64"
CONTROL = "#626C72"
RULE = "#52767B"
MARGINAL_DARK = "#52767B"
PAIR_DARK = "#C8615D"

ROWS = [
    ("Always Lock", "model-independent", "Always-Lock+validity", "D", CONTROL),
    ("Always Reeval.", "model-independent", "Always-Reevaluate", "D", CONTROL),
    ("Generic Qwen", "Qwen3.5", "Generic", "o", QWEN),
    ("Generic GLM", "GLM-5.1", "Generic", "s", GLM),
    ("CTA Qwen", "Qwen3.5", "CTA", "o", QWEN),
    ("CTA GLM", "GLM-5.1", "CTA", "s", GLM),
    ("Rule*", "model-independent", "Rule v2 (post-hoc)", "D", RULE),
]

EXPECTED = {
    ("Always Lock", "model-independent"): (100.0, 20.0, 0, 32),
    ("Always Reeval.", "model-independent"): (20.0, 100.0, 0, 32),
    ("Generic Qwen", "Qwen3.5"): (33.75, 95.0, 3, 32),
    ("Generic GLM", "GLM-5.1"): (56.25, 87.5, 7, 32),
    ("CTA Qwen", "Qwen3.5"): (91.25, 98.75, 30, 32),
    ("CTA GLM", "GLM-5.1"): (92.5, 100.0, 31, 32),
    ("Rule*", "model-independent"): (92.5, 92.5, 28, 32),
}


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.labelsize": 7.5,
            "axes.titlesize": 8.1,
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


def one(rows: list[dict[str, str]], **where: str) -> dict[str, str]:
    matches = [row for row in rows if all(row.get(key) == value for key, value in where.items())]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {where}, found {len(matches)}")
    return matches[0]


def read_data() -> list[dict[str, object]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    output: list[dict[str, object]] = []
    for label, model, controller, marker, color in ROWS:
        marginal = one(
            rows,
            dataset="v3",
            model=model,
            controller=controller,
            slice="all",
        )
        pair = one(
            rows,
            dataset="v3",
            model=model,
            controller=controller,
            slice="changed_winner_core",
        )
        observed = (
            float(marginal["preserve_accuracy_pct"]),
            float(marginal["reevaluate_accuracy_pct"]),
            int(pair["both_correct"]),
            int(pair["pairs"]),
        )
        if observed != EXPECTED[(label, model)]:
            raise ValueError(f"frozen source mismatch for {label}/{model}: {observed}")
        output.append(
            {
                "label": label,
                "model": model,
                "marker": marker,
                "color": color,
                "preserve": observed[0],
                "reevaluate": observed[1],
                "both": observed[2],
                "pairs": observed[3],
                "pairacc": 100.0 * observed[2] / observed[3],
            }
        )
    return output


def clean(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color=GRID, lw=0.42, alpha=0.78, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.5, width=0.65, pad=2)


def draw_phase_map(data: list[dict[str, object]]) -> plt.Figure:
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.52))
    ax.axvline(50, color=GRID, lw=0.65, ls=(0, (3, 2)), zorder=1)
    ax.axhline(50, color=GRID, lw=0.65, ls=(0, (3, 2)), zorder=1)

    labels = {
        "Always Lock": (96, 29, "Always lock\n0/32", "right", "bottom"),
        "Always Reeval.": (23, 108, "Always reeval.\n0/32", "left", "bottom"),
        "Generic Qwen": (34, 90, "Generic Q\n3/32", "left", "top"),
        "Generic GLM": (57, 81, "Generic G\n7/32", "left", "top"),
        "Rule*": (84, 89, "Rule*\n28/32", "right", "top"),
    }
    for row in data:
        x = float(row["preserve"])
        y = float(row["reevaluate"])
        label = str(row["label"])
        color = str(row["color"])
        ax.scatter(
            x,
            y,
            marker=str(row["marker"]),
            s=24,
            facecolor=color if "CTA" in label else PAPER,
            edgecolor=color,
            linewidth=0.9,
            zorder=3,
        )
        if label in labels:
            tx, ty, text, ha, va = labels[label]
            ax.annotate(
                text,
                xy=(x, y),
                xytext=(tx, ty),
                textcoords="data",
                ha=ha,
                va=va,
                fontsize=7.0,
                color=INK,
                linespacing=0.88,
                bbox={"boxstyle": "square,pad=0.08", "fc": PAPER, "ec": "none", "alpha": 0.94},
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.48},
                zorder=4,
            )

    cta_rows = [row for row in data if str(row["label"]).startswith("CTA")]
    cta_x = np.mean([float(row["preserve"]) for row in cta_rows])
    cta_y = np.mean([float(row["reevaluate"]) for row in cta_rows])
    ax.annotate(
        "CTA Q/G\n30/32 · 31/32",
        xy=(cta_x, cta_y),
        xytext=(74, 108),
        textcoords="data",
        ha="left",
        va="bottom",
        fontsize=7.0,
        color=INK,
        linespacing=0.88,
        bbox={"boxstyle": "square,pad=0.08", "fc": PAPER, "ec": "none", "alpha": 0.94},
        arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.48},
        zorder=4,
    )

    ax.text(
        0.02,
        0.02,
        "Q = Qwen · G = GLM · labels show PairAcc",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=6.5,
        color=MUTED,
    )
    ax.set_xlim(10, 108)
    ax.set_ylim(10, 114)
    ax.set_xticks([20, 40, 60, 80, 100])
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_xlabel("Preserve accuracy (%)")
    ax.set_ylabel("Reevaluate accuracy (%)")
    ax.set_title("", pad=0)
    clean(ax)
    fig.subplots_adjust(left=0.17, right=0.98, top=0.90, bottom=0.15)
    return fig


def blend(color: str, value: float, floor: float = 0.06, ceiling: float = 0.78) -> tuple[float, ...]:
    amount = floor + (ceiling - floor) * np.clip(value / 100.0, 0.0, 1.0)
    rgb = np.asarray(to_rgb(color))
    return tuple((1.0 - amount) + amount * rgb)


def draw_metric_matrix(data: list[dict[str, object]]) -> plt.Figure:
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.34))
    y_positions = np.arange(len(data))[::-1]
    for y, row in zip(y_positions, data, strict=True):
        values = [float(row["preserve"]), float(row["reevaluate"]), float(row["pairacc"])]
        for x, value in enumerate(values):
            dark = MARGINAL_DARK if x < 2 else PAIR_DARK
            ax.add_patch(
                Rectangle(
                    (x - 0.44, y - 0.36),
                    0.88,
                    0.72,
                    facecolor=blend(dark, value),
                    edgecolor=PAPER,
                    linewidth=1.0,
                    zorder=2,
                )
            )
            text = f"{value:.0f}%" if x < 2 else f"{int(row['both'])}/{int(row['pairs'])}"
            ax.text(
                x,
                y,
                text,
                ha="center",
                va="center",
                fontsize=7.2,
                color=PAPER if value >= 68 else INK,
                weight="bold" if x == 2 else "normal",
                zorder=3,
            )
        ax.scatter(
            -0.65,
            y,
            marker=str(row["marker"]),
            s=17,
            facecolor=str(row["color"]) if "CTA" in str(row["label"]) else PAPER,
            edgecolor=str(row["color"]),
            linewidth=0.8,
            clip_on=False,
            zorder=4,
        )

    ax.axvline(1.50, color=INK, lw=0.8, zorder=4)
    ax.axhline(4.50, color=GRID, lw=0.55, zorder=1)
    ax.axhline(2.50, color=GRID, lw=0.55, zorder=1)
    ax.axhline(0.50, color=GRID, lw=0.55, zorder=1)
    ax.set_xlim(-0.78, 2.48)
    ax.set_ylim(-0.55, 7.08)
    ax.set_xticks([])
    ax.set_yticks(y_positions, [str(row["label"]) for row in data])
    ax.tick_params(axis="y", length=0, pad=4)
    ax.text(0.5, 7.00, "MARGINAL ACCURACY", ha="center", va="bottom", fontsize=6.8, color=MUTED, weight="bold")
    ax.text(2.0, 7.00, "JOINT SCORE", ha="center", va="bottom", fontsize=6.8, color=PAIR_DARK, weight="bold")
    ax.text(0.0, 6.66, "Preserve", ha="center", va="bottom", fontsize=7.2, color=INK)
    ax.text(1.0, 6.66, "Reevaluate", ha="center", va="bottom", fontsize=7.2, color=INK)
    ax.text(2.0, 6.66, "PairAcc (n/32)", ha="center", va="bottom", fontsize=7.2, color=INK)
    ax.plot([-0.43, 1.43], [6.60, 6.60], color=GRID, lw=0.55, clip_on=False)
    ax.plot([1.57, 2.43], [6.60, 6.60], color=GRID, lw=0.55, clip_on=False)
    ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
    fig.subplots_adjust(left=0.34, right=0.98, top=0.96, bottom=0.05)
    return fig


def save_variants(fig: plt.Figure, stem: Path, creator: str) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"), metadata={"Creator": creator})
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
    parser = argparse.ArgumentParser(description="Generate TRI Figure 3 options A and B.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = read_data()
    option_a = args.output_dir / "figure3_option_a_phase_map"
    option_b = args.output_dir / "figure3_option_b_metric_matrix"
    save_variants(draw_phase_map(data), option_a, "TRI Figure 3 option A phase map")
    save_variants(draw_metric_matrix(data), option_b, "TRI Figure 3 option B metric matrix")
    manifest = {
        "status": "Figure 3 A/B candidates only; not integrated into the paper",
        "source": str(DATA),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "minimum_text_pt": 7.0,
        "png_dpi": 400,
        "pdf_fonttype": 42,
        "outputs": {
            "option_a": {"stem": str(option_a), "size_inches": [3.35, 2.52]},
            "option_b": {"stem": str(option_b), "size_inches": [3.35, 2.34]},
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
