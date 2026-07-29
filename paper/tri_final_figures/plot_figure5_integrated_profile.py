#!/usr/bin/env python3
"""Render the optimized single-structure Figure 5 candidate C."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from PIL import Image

from plot_figure5_figure4_aligned import INK, PAPER, configure, read_frozen, wilson


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "figure5_integrated_profile_v1"
STEM = OUT / "figure5_integrated_profile"
DATA = ROOT / "data" / "summary_csv" / "sqlite_model_facing_outcomes.csv"

GRID = "#D6E0DE"
MUTED = "#5F6B70"

# Keep Figure 4's cool-purple versus warm-coral model identities, but move both
# families toward the cleaner pastel anchors in the supplied reference image.
MODEL_STYLES = {
    "Qwen3.5": {
        "short": "Qwen",
        "base": "#D8CBE4",
        "edge": "#9C83B9",
        "ci": "#73558F",
        "track": "#F7F4F9",
        "track_edge": "#DCCFE7",
        "outline": "#8D72AD",
        "shades": ("#D4C6E0", "#DFD4E8", "#E9E1EF", "#F3EFF6"),
        "shade_edges": ("#9A82BA", "#B29BC8", "#C9B8D8", "#DED4E7"),
    },
    "GLM-5.1": {
        "short": "GLM",
        "base": "#F8C7C7",
        "edge": "#E87378",
        "ci": "#C74D59",
        "track": "#FFF7F6",
        "track_edge": "#F8D5D4",
        "outline": "#DF666C",
        "shades": ("#F7BCBD", "#F9CECD", "#FBE0DF", "#FDF0EF"),
        "shade_edges": ("#E96F75", "#F59694", "#F8B4B1", "#FBD8D6"),
    },
}
OUTCOME_FIELDS = (
    "correct_final_state",
    "core_tri_write",
    "fallback_wrong_write",
    "unneeded_reject",
)


def relative_luminance(hex_color: str) -> float:
    rgb = np.array([int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)])
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2])


def count_color(fill: str) -> str:
    white_contrast = 1.05 / (relative_luminance(fill) + 0.05)
    return PAPER if white_contrast >= 4.5 else INK


def draw_outcomes(
    ax: plt.Axes,
    row: dict[str, int],
    *,
    y: float,
    shades: tuple[str, str, str, str],
    edges: tuple[str, str, str, str],
    outline: str,
) -> None:
    cursor = 0.0
    height = 0.43
    for field, color, edge in zip(OUTCOME_FIELDS, shades, edges, strict=True):
        count = row[field]
        width = 100.0 * count / row["tasks"]
        if count == 0:
            continue
        ax.add_patch(
            Rectangle(
                (cursor, y - height / 2),
                width,
                height,
                facecolor=color,
                edgecolor=edge,
                linewidth=0.72,
                zorder=2,
            )
        )
        ax.text(
            cursor + width / 2,
            y,
            str(count),
            ha="center",
            va="center",
            fontsize=7.0,
            weight="bold",
            color=count_color(color),
            zorder=3,
        )
        cursor += width

    ax.add_patch(
        Rectangle(
            (0, y - height / 2),
            100,
            height,
            facecolor="none",
            edgecolor=outline,
            linewidth=0.78,
            zorder=4,
        )
    )


def draw_strict_rate(
    ax: plt.Axes,
    *,
    y: float,
    k: int,
    n: int,
    color: str,
    edge: str,
    ci: str,
    track: str,
    track_edge: str,
) -> None:
    rate, low, high = wilson(k, n)
    height = 0.27
    ax.barh(
        y,
        100,
        height=height,
        color=track,
        edgecolor=track_edge,
        linewidth=0.55,
        zorder=1,
    )
    if rate > 0:
        ax.barh(
            y,
            rate,
            height=height,
            color=color,
            edgecolor=edge,
            linewidth=0.75,
            zorder=2,
        )
    else:
        ax.plot([0, 2.4], [y, y], color=edge, lw=1.5, zorder=3)

    ax.plot([low, high], [y, y], color=ci, lw=0.82, zorder=4)
    ax.plot([low, low], [y - 0.095, y + 0.095], color=ci, lw=0.72, zorder=4)
    ax.plot([high, high], [y - 0.095, y + 0.095], color=ci, lw=0.72, zorder=4)

    if rate == 100:
        label_x, align = 99.4, "right"
    elif rate == 0:
        label_x, align = 3.2, "left"
    else:
        label_x, align = rate, "center"
    ax.text(
        label_x,
        y + 0.215,
        f"{k}/{n}",
        ha=align,
        va="bottom",
        fontsize=7.0,
        color=INK,
        zorder=5,
    )


def draw(data: dict[str, dict[str, int]]) -> plt.Figure:
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.16))
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.20, 6.15)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=GRID, lw=0.48, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=5)
    ax.tick_params(axis="x", length=2.4, width=0.65, pad=2)

    positions = {
        "Qwen3.5": (4.92, 4.12, 3.32),
        "GLM-5.1": (1.87, 1.07, 0.27),
    }
    ticks: list[float] = []
    labels: list[str] = []

    for model in ("Qwen3.5", "GLM-5.1"):
        row = data[model]
        style = MODEL_STYLES[model]
        outcome_y, stable_y, changed_y = positions[model]

        ax.text(
            -13.4,
            outcome_y + 0.57,
            style["short"],
            ha="left",
            va="center",
            fontsize=7.5,
            weight="bold",
            color=INK,
            clip_on=False,
        )
        draw_outcomes(
            ax,
            row,
            y=outcome_y,
            shades=style["shades"],
            edges=style["shade_edges"],
            outline=style["outline"],
        )
        draw_strict_rate(
            ax,
            y=stable_y,
            k=row["stable_writes"],
            n=row["stable_opportunities"],
            color=style["base"],
            edge=style["edge"],
            ci=style["ci"],
            track=style["track"],
            track_edge=style["track_edge"],
        )
        draw_strict_rate(
            ax,
            y=changed_y,
            k=row["strict_core_writes"],
            n=row["strict_core_opportunities"],
            color=style["base"],
            edge=style["edge"],
            ci=style["ci"],
            track=style["track"],
            track_edge=style["track_edge"],
        )

        ticks.extend([outcome_y, stable_y, changed_y])
        labels.extend(["Outcomes, n=40", "Stable", "Changed"])

    ax.set_yticks(ticks, labels)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Outcome share / B-write rate (%)", labelpad=4)

    fig.text(
        0.500,
        0.958,
        "Correct | Strict B | Fallback B | Reject",
        ha="center",
        va="center",
        fontsize=7.0,
        color=INK,
    )
    fig.subplots_adjust(left=0.275, right=0.975, top=0.89, bottom=0.17)
    return fig


def save(fig: plt.Figure) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(STEM.with_suffix(".pdf"), metadata={"Creator": "TRI Figure 5 candidate C using Figure 4's concise result grammar"})
    fig.savefig(STEM.with_suffix(".svg"))
    png = STEM.with_suffix(".png")
    fig.savefig(png, dpi=400)
    plt.close(fig)

    with Image.open(png).convert("RGB") as image:
        image.convert("L").save(STEM.with_name(STEM.name + "-grayscale").with_suffix(".png"))
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
            STEM.with_name(STEM.name + "-deuteranopia").with_suffix(".png")
        )

    manifest = {
        "status": "Provisional integrated Figure 5 profile; further visual optimization planned",
        "source": str(DATA),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "size_inches": [3.35, 2.16],
        "minimum_text_pt": 7.0,
        "png_dpi": 400,
        "pdf_fonttype": 42,
        "encoding": (
            "Qwen uses a clean lavender family and GLM a rose-coral family derived from "
            "the supplied reference image. Every filled mark uses a slightly darker "
            "same-hue outline rather than a universal ink border, and Wilson intervals use "
            "a darker tone from that same model family; shade order is "
            "Correct, Strict B, Fallback B, Reject. Strict rows use model-color fill, "
            "direct fractions, explicit denominators, and Wilson 95% intervals."
        ),
    }
    STEM.with_name(STEM.name + "-manifest").with_suffix(".json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    save(draw(read_frozen()))


if __name__ == "__main__":
    main()
