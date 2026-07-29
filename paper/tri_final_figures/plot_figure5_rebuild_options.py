#!/usr/bin/env python3
"""Generate four structurally distinct Figure 5 previews from frozen data."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, PathPatch, Wedge
from matplotlib.path import Path as MplPath
from PIL import Image, ImageDraw, ImageFont, ImageOps
from matplotlib import font_manager

from forest_ember_palette import EMBER, EMBER_LIGHT, GRID, INK, MUTED, NEUTRAL_EDGE, PAPER, PLUM, TEAL, TEAL_LIGHT
from plot_figure5_strict_unit_results import read_frozen


ROOT = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / "outputs" / "figure5_rebuild_options_v2"


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


def clean_axes(figsize: tuple[float, float] = (3.35, 2.15)) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def target(ax: plt.Axes, x: float, y: float, letter: str, *, primary: bool) -> None:
    ax.add_patch(
        Circle(
            (x, y),
            0.026,
            facecolor=TEAL_LIGHT if primary else PAPER,
            edgecolor=TEAL if primary else NEUTRAL_EDGE,
            linewidth=0.9,
            zorder=5,
        )
    )
    ax.text(x, y, letter, ha="center", va="center", fontsize=7.0, weight="bold", color=INK, zorder=6)


def model_mark(ax: plt.Axes, x: float, y: float, model: str) -> None:
    if model == "Qwen":
        ax.plot(x, y, marker="o", markersize=3.5, color=PLUM, linestyle="none", zorder=6)
    else:
        ax.plot(x, y, marker="s", markersize=3.4, color=EMBER, linestyle="none", zorder=6)
    ax.text(x + 0.020, y, model, ha="left", va="center", fontsize=7.0, color=INK)


def condition_label(ax: plt.Axes, x: float, y: float, *, changed: bool, align: str = "left") -> None:
    title = "CHANGED" if changed else "STABLE"
    detail = "B #1; A valid" if changed else "A remains #1"
    ax.text(x, y + 0.025, title, ha=align, va="center", fontsize=7.1, weight="bold", color=INK)
    ax.text(x, y - 0.025, detail, ha=align, va="center", fontsize=7.0, color=MUTED)


def ribbon(ax: plt.Axes, x0: float, y0: float, x1: float, y1: float, height: float, color: str, alpha: float = 1.0) -> None:
    h = height / 2
    c1 = x0 + (x1 - x0) * 0.42
    c2 = x0 + (x1 - x0) * 0.58
    verts = [
        (x0, y0 + h),
        (c1, y0 + h),
        (c2, y1 + h),
        (x1, y1 + h),
        (x1, y1 - h),
        (c2, y1 - h),
        (c1, y0 - h),
        (x0, y0 - h),
        (x0, y0 + h),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color, edgecolor="none", alpha=alpha, zorder=2))


def option_a(data: dict[str, dict[str, int]]) -> plt.Figure:
    """Outcome river: flow width is the number of strict opportunities."""
    fig, ax = clean_axes()
    ax.text(0.035, 0.935, "CONDITION", ha="left", va="center", fontsize=7.0, weight="bold", color=MUTED)
    ax.text(0.425, 0.935, "MODEL", ha="center", va="center", fontsize=7.0, weight="bold", color=MUTED)
    ax.text(0.810, 0.935, "ISSUED OUTCOME", ha="center", va="center", fontsize=7.0, weight="bold", color=MUTED)
    ax.plot([0.025, 0.975], [0.890, 0.890], color=GRID, lw=0.7)

    condition_label(ax, 0.035, 0.685, changed=False)
    condition_label(ax, 0.035, 0.325, changed=True)

    rows = [
        ("Qwen", 0.735, 0, 4),
        ("GLM", 0.615, 0, 4),
        ("Qwen", 0.375, 8, 8),
        ("GLM", 0.255, 6, 8),
    ]
    for model, y, wrong, total in rows:
        model_mark(ax, 0.385, y, model)
        h_total = 0.065 * (total / 8)
        if wrong:
            h_wrong = h_total * (wrong / total)
            ribbon(ax, 0.515, y, 0.745, y + (h_total - h_wrong) / 2, h_wrong, EMBER_LIGHT)
            ax.plot([0.745, 0.745], [y - h_wrong / 2, y + h_wrong / 2], color=EMBER, lw=1.0, zorder=5)
        other = total - wrong
        if other:
            h_other = h_total * (other / total)
            offset = -h_total / 2 + h_other / 2
            ribbon(ax, 0.515, y + offset, 0.745, y + offset, h_other, TEAL_LIGHT if wrong == 0 else "#ECE9E5")
            ax.plot([0.745, 0.745], [y + offset - h_other / 2, y + offset + h_other / 2], color=TEAL if wrong == 0 else NEUTRAL_EDGE, lw=1.0, zorder=5)
        label = f"B write  {wrong}/{total}" if wrong else f"no B write  {wrong}/{total}"
        ax.text(0.775, y, label, ha="left", va="center", fontsize=7.0, weight="bold", color=INK)

    ax.text(0.035, 0.090, "Ribbon width = n", ha="left", va="center", fontsize=7.0, color=MUTED)
    ax.plot([0.430, 0.480], [0.090, 0.090], color=EMBER, lw=5.0, solid_capstyle="butt")
    ax.text(0.495, 0.090, "coral = wrong-target B", ha="left", va="center", fontsize=7.0, color=INK)
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.03, top=0.99)
    return fig


def ring(ax: plt.Axes, x: float, y: float, wrong: int, total: int) -> None:
    ring_ax = ax.inset_axes([x - 0.085, y - 0.085, 0.17, 0.17], transform=ax.transAxes)
    ring_ax.set_xlim(0, 1)
    ring_ax.set_ylim(0, 1)
    ring_ax.set_aspect("equal")
    ring_ax.axis("off")
    radius, width = 0.47, 0.15
    ring_ax.add_patch(Wedge((0.5, 0.5), radius, 0, 360, width=width, facecolor="#ECE9E5", edgecolor=NEUTRAL_EDGE, linewidth=0.65))
    if wrong:
        angle = 360 * wrong / total
        ring_ax.add_patch(Wedge((0.5, 0.5), radius, 90 - angle, 90, width=width, facecolor=EMBER, edgecolor=EMBER, linewidth=0.65))
    ring_ax.text(0.5, 0.56, f"{100 * wrong / total:.0f}%", ha="center", va="center", fontsize=7.4, weight="bold", color=INK)
    ring_ax.text(0.5, 0.33, f"{wrong}/{total}", ha="center", va="center", fontsize=7.0, color=MUTED)


def option_b(data: dict[str, dict[str, int]]) -> plt.Figure:
    """Ratio-ring matrix: condition by model."""
    fig, ax = clean_axes()
    ax.text(0.500, 0.950, "STRICT WRONG-TARGET WRITE RATE", ha="center", va="center", fontsize=7.0, weight="bold", color=MUTED)
    condition_label(ax, 0.515, 0.820, changed=False, align="center")
    target(ax, 0.515, 0.730, "A", primary=True)
    condition_label(ax, 0.800, 0.820, changed=True, align="center")
    target(ax, 0.770, 0.730, "B", primary=True)
    target(ax, 0.830, 0.730, "A", primary=False)

    model_mark(ax, 0.100, 0.590, "Qwen")
    model_mark(ax, 0.100, 0.300, "GLM")
    ax.plot([0.050, 0.955], [0.675, 0.675], color=GRID, lw=0.7)
    ax.plot([0.365, 0.365], [0.145, 0.675], color=GRID, lw=0.65)
    ax.plot([0.655, 0.655], [0.145, 0.675], color=GRID, lw=0.65)

    q, g = data["Qwen3.5"], data["GLM-5.1"]
    ring(ax, 0.515, 0.590, q["stable_writes"], q["stable_opportunities"])
    ring(ax, 0.800, 0.590, q["strict_core_writes"], q["strict_core_opportunities"])
    ring(ax, 0.515, 0.300, g["stable_writes"], g["stable_opportunities"])
    ring(ax, 0.800, 0.300, g["strict_core_writes"], g["strict_core_opportunities"])

    ax.add_patch(Circle((0.402, 0.085), 0.014, facecolor=EMBER, edgecolor=EMBER))
    ax.text(0.428, 0.085, "B write", ha="left", va="center", fontsize=7.0, color=INK)
    ax.add_patch(Circle((0.610, 0.085), 0.014, facecolor="#ECE9E5", edgecolor=NEUTRAL_EDGE, linewidth=0.65))
    ax.text(0.636, 0.085, "other", ha="left", va="center", fontsize=7.0, color=INK)
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.03, top=0.99)
    return fig


def option_c(data: dict[str, dict[str, int]]) -> plt.Figure:
    """Shared-axis bars: most conventional exact comparison."""
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.15))
    q, g = data["Qwen3.5"], data["GLM-5.1"]
    values = [
        100 * q["stable_writes"] / q["stable_opportunities"],
        100 * g["stable_writes"] / g["stable_opportunities"],
        100 * q["strict_core_writes"] / q["strict_core_opportunities"],
        100 * g["strict_core_writes"] / g["strict_core_opportunities"],
    ]
    counts = ["0/4", "0/4", "8/8", "6/8"]
    ys = [3.45, 2.65, 1.25, 0.45]
    models = ["Qwen", "GLM", "Qwen", "GLM"]

    ax.set_xlim(-40, 108)
    ax.set_ylim(-0.25, 4.30)
    ax.axvline(0, color=INK, lw=0.75, zorder=1)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    for y, value, count, model in zip(ys, values, counts, models, strict=True):
        ax.barh(y, 100, height=0.42, color="#ECE9E5", edgecolor=NEUTRAL_EDGE, linewidth=0.55, zorder=2)
        if value:
            ax.barh(y, value, height=0.42, color=EMBER_LIGHT, edgecolor=EMBER, linewidth=0.8, zorder=3)
        marker = "o" if model == "Qwen" else "s"
        color = PLUM if model == "Qwen" else EMBER
        ax.plot(-32, y, marker=marker, markersize=3.6, color=color, linestyle="none", clip_on=False)
        ax.text(-27, y, model, ha="left", va="center", fontsize=7.0, color=INK)
        ax.text(min(value + 3, 102) if value else 3, y, count, ha="left", va="center", fontsize=7.1, weight="bold", color=INK)

    ax.text(-38, 3.98, "STABLE · A remains #1", ha="left", va="center", fontsize=7.1, weight="bold", color=INK)
    ax.text(-38, 1.78, "CHANGED · B #1; A valid", ha="left", va="center", fontsize=7.1, weight="bold", color=INK)
    ax.plot([-38, 105], [2.05, 2.05], color=GRID, lw=0.7)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Strict wrong-target writes (%)")
    ax.set_yticks([])
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="x", length=2.5, width=0.65, pad=2)
    fig.subplots_adjust(left=0.04, right=0.98, top=0.98, bottom=0.19)
    return fig


def dot_cluster(ax: plt.Axes, cx: float, cy: float, wrong: int, total: int) -> None:
    cols = 4
    dx, dy = 0.048, 0.062
    rows = int(np.ceil(total / cols))
    for i in range(total):
        row, col = divmod(i, cols)
        x = cx + (col - (cols - 1) / 2) * dx
        y = cy + ((rows - 1) / 2 - row) * dy
        is_wrong = i < wrong
        ax.plot(
            x,
            y,
            marker="o" if is_wrong else "o",
            markersize=9.0,
            markerfacecolor=EMBER if is_wrong else PAPER,
            markeredgecolor=EMBER if is_wrong else NEUTRAL_EDGE,
            markeredgewidth=0.9,
            linestyle="none",
            zorder=4,
        )
        if is_wrong:
            ax.text(x, y, "B", ha="center", va="center", fontsize=7.0, weight="bold", color=PAPER, zorder=5)


def option_d(data: dict[str, dict[str, int]]) -> plt.Figure:
    """Opportunity constellations: every observed denominator remains visible."""
    fig, ax = clean_axes()
    q, g = data["Qwen3.5"], data["GLM-5.1"]
    condition_label(ax, 0.510, 0.850, changed=False, align="center")
    condition_label(ax, 0.810, 0.850, changed=True, align="center")
    ax.plot([0.050, 0.955], [0.745, 0.745], color=GRID, lw=0.7)
    ax.plot([0.355, 0.355], [0.150, 0.745], color=GRID, lw=0.65)
    ax.plot([0.660, 0.660], [0.150, 0.745], color=GRID, lw=0.65)

    model_mark(ax, 0.085, 0.570, "Qwen")
    model_mark(ax, 0.085, 0.285, "GLM")
    dot_cluster(ax, 0.510, 0.570, q["stable_writes"], q["stable_opportunities"])
    dot_cluster(ax, 0.810, 0.570, q["strict_core_writes"], q["strict_core_opportunities"])
    dot_cluster(ax, 0.510, 0.285, g["stable_writes"], g["stable_opportunities"])
    dot_cluster(ax, 0.810, 0.285, g["strict_core_writes"], g["strict_core_opportunities"])
    for x, y, label in ((0.510, 0.465, "0/4"), (0.810, 0.465, "8/8"), (0.510, 0.180, "0/4"), (0.810, 0.180, "6/8")):
        ax.text(x, y, label, ha="center", va="center", fontsize=7.2, weight="bold", color=INK)
    ax.plot(0.315, 0.075, marker="o", markersize=7.0, markerfacecolor=EMBER, markeredgecolor=EMBER, linestyle="none")
    ax.text(0.340, 0.075, "B write", ha="left", va="center", fontsize=7.0, color=INK)
    ax.plot(0.585, 0.075, marker="o", markersize=7.0, markerfacecolor=PAPER, markeredgecolor=NEUTRAL_EDGE, markeredgewidth=0.9, linestyle="none")
    ax.text(0.610, 0.075, "other", ha="left", va="center", fontsize=7.0, color=INK)
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.03, top=0.99)
    return fig


def save_figure(fig: plt.Figure, stem: Path) -> None:
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.012)
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.012)
    fig.savefig(stem.with_suffix(".png"), dpi=400, bbox_inches="tight", pad_inches=0.012)
    plt.close(fig)


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    props = font_manager.FontProperties(family="DejaVu Sans", weight="bold" if bold else "normal")
    return ImageFont.truetype(font_manager.findfont(props), size=size)


def contact_sheet(output_dir: Path, options: list[tuple[str, str, str]]) -> None:
    tile_w, tile_h = 1120, 820
    margin, gap, top = 42, 30, 80
    canvas = Image.new("RGB", (2 * tile_w + 2 * margin + gap, 2 * tile_h + 2 * margin + gap + top), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 28), "FIGURE 5 · FOUR STRUCTURAL DIRECTIONS", fill=INK, font=font(28, bold=True))
    for index, (code, name, description) in enumerate(options):
        row, col = divmod(index, 2)
        x = margin + col * (tile_w + gap)
        y = margin + top + row * (tile_h + gap)
        draw.text((x, y), f"{code}  {name}", fill=INK, font=font(23, bold=True))
        draw.text((x, y + 34), description, fill=MUTED, font=font(17))
        with Image.open(output_dir / f"option_{code.lower()}.png").convert("RGB") as image:
            fitted = ImageOps.contain(image, (tile_w - 12, tile_h - 82), method=Image.Resampling.LANCZOS)
            px = x + (tile_w - fitted.width) // 2
            py = y + 72 + (tile_h - 76 - fitted.height) // 2
            canvas.paste(fitted, (px, py))
        draw.line((x, y + tile_h - 2, x + tile_w, y + tile_h - 2), fill="#E4E0DC", width=2)
    canvas.save(output_dir / "figure5_rebuild_options_contact.png", dpi=(180, 180), optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    configure()
    data = read_frozen()
    options = [
        ("A", "Outcome river", "Flow width carries the strict denominator and outcome split"),
        ("B", "Ratio-ring matrix", "A compact condition × model view of wrong-write proportions"),
        ("C", "Shared-axis bars", "The most precise direct comparison on one 0–100% scale"),
        ("D", "Opportunity constellation", "Every observed opportunity remains individually visible"),
    ]
    figures = {"A": option_a(data), "B": option_b(data), "C": option_c(data), "D": option_d(data)}
    for code, figure in figures.items():
        save_figure(figure, args.output_dir / f"option_{code.lower()}")
    contact_sheet(args.output_dir, options)
    print(args.output_dir)


if __name__ == "__main__":
    main()
