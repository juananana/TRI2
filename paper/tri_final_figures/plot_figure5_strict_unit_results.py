#!/usr/bin/env python3
"""Figure 5: strict SQLite opportunities from refreshed ranking to issued write."""

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
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from PIL import Image

from forest_ember_palette import (
    EMBER,
    EMBER_LIGHT,
    GRID,
    INK,
    MUTED,
    NEUTRAL_EDGE,
    PAPER,
    PLUM,
    TEAL,
    TEAL_LIGHT,
)


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "summary_csv" / "sqlite_model_facing_outcomes.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "figure5_strict_unit_results_v1" / "figure5_strict_unit_results"


def read_frozen() -> dict[str, dict[str, int]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    keys = (
        "tasks",
        "correct_final_state",
        "core_tri_write",
        "fallback_wrong_write",
        "unneeded_reject",
        "strict_core_writes",
        "strict_core_opportunities",
        "stable_writes",
        "stable_opportunities",
    )
    result: dict[str, dict[str, int]] = {}
    for model in ("Qwen3.5", "GLM-5.1"):
        hit = [row for row in rows if row["model"] == model and row["controller"] == "Generic"]
        if len(hit) != 1:
            raise ValueError(f"Expected one Generic row for {model}, found {len(hit)}")
        result[model] = {key: int(hit[0][key]) for key in keys}

    expected = {
        "Qwen3.5": {
            "tasks": 40,
            "correct_final_state": 27,
            "core_tri_write": 8,
            "fallback_wrong_write": 5,
            "unneeded_reject": 0,
            "strict_core_writes": 8,
            "strict_core_opportunities": 8,
            "stable_writes": 0,
            "stable_opportunities": 4,
        },
        "GLM-5.1": {
            "tasks": 40,
            "correct_final_state": 26,
            "core_tri_write": 6,
            "fallback_wrong_write": 2,
            "unneeded_reject": 6,
            "strict_core_writes": 6,
            "strict_core_opportunities": 8,
            "stable_writes": 0,
            "stable_opportunities": 4,
        },
    }
    if result != expected:
        raise ValueError(f"Frozen Figure 5 data changed: {result}")
    return result


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "text.color": INK,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )


def arrow(ax, start: tuple[float, float], end: tuple[float, float], *, color: str = TEAL) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=5.5,
            linewidth=0.85,
            color=color,
            shrinkA=0,
            shrinkB=0,
            zorder=3,
        )
    )


def target(ax, x: float, y: float, label: str, *, active: bool, rank: str | None = None) -> None:
    face = TEAL_LIGHT if active else PAPER
    edge = TEAL if active else NEUTRAL_EDGE
    ax.add_patch(Circle((x, y), 0.027, facecolor=face, edgecolor=edge, linewidth=0.9, zorder=4))
    ax.text(x, y, label, ha="center", va="center", fontsize=7.0, weight="bold", color=INK, zorder=5)
    if rank:
        ax.text(x, y + 0.046, rank, ha="center", va="bottom", fontsize=7.0, weight="bold", color=MUTED)


def model_mark(ax, x: float, y: float, model: str) -> None:
    if model == "Qwen":
        ax.plot(x, y, marker="o", markersize=3.4, markerfacecolor=PLUM, markeredgecolor=PLUM, linestyle="none")
    else:
        ax.plot(x, y, marker="s", markersize=3.3, markerfacecolor=EMBER, markeredgecolor=EMBER, linestyle="none")
    ax.text(x + 0.018, y, model, ha="left", va="center", fontsize=7.0, color=INK)


def unit_row(
    ax,
    *,
    cx: float,
    y: float,
    errors: int,
    total: int,
) -> None:
    tile_w, tile_h, gap = 0.025, 0.055, 0.006
    row_w = total * tile_w + (total - 1) * gap
    start = cx - row_w / 2
    for index in range(total):
        is_error = index < errors
        x = start + index * (tile_w + gap)
        patch = FancyBboxPatch(
            (x - tile_w / 2, y - tile_h / 2),
            tile_w,
            tile_h,
            boxstyle="round,pad=0.001,rounding_size=0.006",
            facecolor=EMBER_LIGHT if is_error else PAPER,
            edgecolor=EMBER if is_error else NEUTRAL_EDGE,
            linewidth=0.9,
            zorder=3,
        )
        ax.add_patch(patch)
        ax.text(
            x,
            y,
            "B" if is_error else "·",
            ha="center",
            va="center",
            fontsize=7.0,
            weight="bold" if is_error else "normal",
            color=INK if is_error else MUTED,
            zorder=4,
        )
    ax.text(cx, y - 0.058, f"{errors}/{total}", ha="center", va="top", fontsize=7.2, weight="bold", color=INK)


def condition_cell(ax, y: float, *, changed: bool) -> None:
    color = EMBER if changed else TEAL
    title = "CHANGED" if changed else "STABLE"
    detail = "B #1; A valid" if changed else "A remains #1"
    ax.text(0.030, y + 0.055, title, ha="left", va="center", fontsize=7.2, weight="bold", color=INK)
    ax.text(0.030, y + 0.005, detail, ha="left", va="center", fontsize=7.0, color=MUTED)
    if changed:
        target(ax, 0.269, y + 0.025, "B", active=True)
        target(ax, 0.326, y + 0.025, "A", active=False)
    else:
        target(ax, 0.269, y + 0.025, "A", active=True)
        target(ax, 0.326, y + 0.025, "B", active=False)
    arrow(ax, (0.350, y + 0.025), (0.382, y + 0.025), color=color)


def draw(data: dict[str, dict[str, int]]) -> plt.Figure:
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.05))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.430, 0.935, "CORRECT PRE-REFRESH BINDING", ha="center", va="center", fontsize=7.0, weight="bold", color=MUTED)
    target(ax, 0.770, 0.935, "A", active=True)

    ax.text(0.215, 0.825, "POST-REFRESH", ha="center", va="center", fontsize=7.0, weight="bold", color=INK)
    ax.text(0.215, 0.777, "condition", ha="center", va="center", fontsize=7.0, color=MUTED)
    model_mark(ax, 0.500, 0.825, "Qwen")
    ax.text(0.552, 0.777, "issued writes", ha="center", va="center", fontsize=7.0, color=MUTED)
    model_mark(ax, 0.802, 0.825, "GLM")
    ax.text(0.848, 0.777, "issued writes", ha="center", va="center", fontsize=7.0, color=MUTED)
    ax.plot([0.025, 0.975], [0.758, 0.758], color=GRID, linewidth=0.75)
    ax.plot([0.405, 0.405], [0.205, 0.842], color=GRID, linewidth=0.65)
    ax.plot([0.700, 0.700], [0.205, 0.842], color=GRID, linewidth=0.65)
    ax.plot([0.025, 0.975], [0.480, 0.480], color=GRID, linewidth=0.65)

    condition_cell(ax, 0.615, changed=False)
    condition_cell(ax, 0.335, changed=True)

    qwen = data["Qwen3.5"]
    glm = data["GLM-5.1"]
    unit_row(
        ax,
        cx=0.552,
        y=0.640,
        errors=qwen["stable_writes"],
        total=qwen["stable_opportunities"],
    )
    unit_row(
        ax,
        cx=0.848,
        y=0.640,
        errors=glm["stable_writes"],
        total=glm["stable_opportunities"],
    )
    unit_row(
        ax,
        cx=0.552,
        y=0.360,
        errors=qwen["strict_core_writes"],
        total=qwen["strict_core_opportunities"],
    )
    unit_row(
        ax,
        cx=0.848,
        y=0.360,
        errors=glm["strict_core_writes"],
        total=glm["strict_core_opportunities"],
    )

    # The legend names only the observed error; outlined units remain deliberately non-committal.
    legend_y = 0.105
    ax.add_patch(
        FancyBboxPatch(
            (0.030, legend_y - 0.024),
            0.030,
            0.048,
            boxstyle="round,pad=0.001,rounding_size=0.005",
            facecolor=EMBER_LIGHT,
            edgecolor=EMBER,
            linewidth=0.9,
        )
    )
    ax.text(0.045, legend_y, "B", ha="center", va="center", fontsize=7.0, weight="bold", color=INK)
    ax.text(0.073, legend_y, "wrong-target write to B", ha="left", va="center", fontsize=7.0, color=INK)
    ax.add_patch(
        FancyBboxPatch(
            (0.610, legend_y - 0.024),
            0.030,
            0.048,
            boxstyle="round,pad=0.001,rounding_size=0.005",
            facecolor=PAPER,
            edgecolor=NEUTRAL_EDGE,
            linewidth=0.9,
        )
    )
    ax.text(0.625, legend_y, "·", ha="center", va="center", fontsize=7.0, color=MUTED)
    ax.text(0.653, legend_y, "other outcome", ha="left", va="center", fontsize=7.0, color=INK)

    fig.subplots_adjust(left=0.008, right=0.992, bottom=0.025, top=0.995)
    return fig


def save(fig: plt.Figure, output: Path, data: dict[str, dict[str, int]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    metadata = {"Creator": "TRI strict SQLite opportunity chart"}
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.012, metadata=metadata)
    fig.savefig(output.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.012)
    png = output.with_suffix(".png")
    fig.savefig(png, dpi=400, bbox_inches="tight", pad_inches=0.012)
    plt.close(fig)

    with Image.open(png).convert("RGB") as image:
        image.convert("L").save(output.with_name(output.name + "-grayscale").with_suffix(".png"))
        rgb = np.asarray(image, dtype=np.float32) / 255.0
        transform = np.array(
            [
                [0.367322, 0.860646, -0.227968],
                [0.280085, 0.672501, 0.047413],
                [-0.011820, 0.042940, 0.968881],
            ],
            dtype=np.float32,
        )
        simulated = np.clip(rgb @ transform.T, 0.0, 1.0)
        Image.fromarray(np.uint8(np.round(simulated * 255))).save(
            output.with_name(output.name + "-deuteranopia").with_suffix(".png")
        )

    manifest = {
        "status": "Figure 5 strict-opportunity unit result chart",
        "source": str(DATA.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "size_inches": [3.35, 2.05],
        "minimum_text_pt": 7.0,
        "strict_counts": {
            "stable": {
                "Qwen": f'{data["Qwen3.5"]["stable_writes"]}/{data["Qwen3.5"]["stable_opportunities"]}',
                "GLM": f'{data["GLM-5.1"]["stable_writes"]}/{data["GLM-5.1"]["stable_opportunities"]}',
            },
            "changed": {
                "Qwen": f'{data["Qwen3.5"]["strict_core_writes"]}/{data["Qwen3.5"]["strict_core_opportunities"]}',
                "GLM": f'{data["GLM-5.1"]["strict_core_writes"]}/{data["GLM-5.1"]["strict_core_opportunities"]}',
            },
        },
        "encoding": {
            "unit": "one strict opportunity",
            "coral_B": "wrong-target write to refreshed winner B",
            "outlined_dot": "other outcome; not asserted to be correct or safe",
            "shape": "Qwen circle; GLM square",
            "top_glyphs": "post-refresh winner and continued validity manipulation",
        },
    }
    output.with_name(output.name + "-manifest").with_suffix(".json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = read_frozen()
    save(draw(data), args.output, data)
    print(args.output)


if __name__ == "__main__":
    main()
