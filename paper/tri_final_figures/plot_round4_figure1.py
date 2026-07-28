from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path as MplPath


INK = "#29343A"
MUTED = "#758187"
HAIRLINE = "#BCC4C5"
PAPER = "#FFFFFF"
A_RED = "#B9534F"
A_LIGHT = "#F8E4DE"
B_GREEN = "#2D746F"
B_LIGHT = "#DDEDE8"
REFRESH_BLUE = "#6E91A6"
REFRESH_LIGHT = "#E6EEF1"
SELECT_GOLD = "#E5AD45"
WRONG = "#A83D4D"


def _apply_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 8.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
            "savefig.pad_inches": 0,
        }
    )


def _save(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    plt.close(fig)


def _envelope(
    ax: plt.Axes,
    x: float,
    y: float,
    label: str,
    edge: str,
    fill: str,
    marker: str,
    selected: bool = False,
    width: float = 0.72,
    height: float = 0.48,
    zorder: int = 5,
) -> None:
    left = x - width / 2
    bottom = y - height / 2
    ax.add_patch(
        FancyBboxPatch(
            (left, bottom),
            width,
            height,
            boxstyle="round,pad=0.015,rounding_size=0.055",
            facecolor=fill,
            edgecolor=edge,
            linewidth=0.9,
            zorder=zorder,
        )
    )
    ax.plot(
        [left + 0.04, x, left + width - 0.04],
        [bottom + height - 0.05, bottom + 0.18, bottom + height - 0.05],
        color=edge,
        lw=0.62,
        zorder=zorder + 1,
    )
    ax.scatter(x, y, s=25, marker=marker, facecolor=edge, edgecolor=PAPER, lw=0.45, zorder=zorder + 2)
    ax.text(x, y, label, ha="center", va="center", fontsize=8.0, color="white", weight="bold", zorder=zorder + 3)
    if selected:
        ax.scatter(x + width * 0.43, y + height * 0.49, s=28, marker="*", facecolor=SELECT_GOLD, edgecolor=INK, lw=0.4, zorder=zorder + 4)


def _seal(
    ax: plt.Axes,
    x: float,
    y: float,
    label: str,
    color: str,
    marker: str,
    filled: bool = True,
) -> None:
    ax.add_patch(Circle((x, y), 0.31, facecolor=PAPER, edgecolor=color, lw=1.0, zorder=5))
    ax.scatter(
        x,
        y,
        s=36,
        marker=marker,
        facecolor=color if filled else PAPER,
        edgecolor=color,
        lw=0.7,
        zorder=7,
    )
    ax.text(x, y, label, ha="center", va="center", fontsize=8.0, color="white" if filled else color, weight="bold", zorder=8)


def _arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str,
    width: float,
    style: str | tuple = "-",
    zorder: int = 3,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=7,
            linewidth=width,
            linestyle=style,
            color=color,
            shrinkA=0,
            shrinkB=0,
            zorder=zorder,
        )
    )


def _refresh_lens(ax: plt.Axes) -> None:
    vertices = [
        (4.70, 6.60),
        (4.56, 5.80),
        (4.82, 5.00),
        (4.70, 4.20),
        (4.56, 3.40),
        (4.82, 2.20),
        (4.66, 1.15),
        (5.34, 1.15),
        (5.18, 2.20),
        (5.44, 3.40),
        (5.30, 4.20),
        (5.18, 5.00),
        (5.44, 5.80),
        (5.30, 6.60),
        (0.0, 0.0),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    ax.add_patch(
        PathPatch(
            MplPath(vertices, codes),
            facecolor=REFRESH_LIGHT,
            edgecolor=REFRESH_BLUE,
            linewidth=0.75,
            alpha=0.92,
            zorder=0,
        )
    )
    ax.add_patch(
        FancyBboxPatch(
            (4.22, 6.48),
            1.56,
            0.47,
            boxstyle="round,pad=0.01,rounding_size=0.22",
            facecolor=REFRESH_BLUE,
            edgecolor=REFRESH_BLUE,
            linewidth=0.6,
            zorder=10,
        )
    )
    ax.text(5.0, 6.715, "REFRESH", ha="center", va="center", fontsize=8.0, color="white", weight="bold", zorder=11)


def build_refresh_lens(stem: Path) -> None:
    """Draw TRI as a ranking swap crossed by persistent and deferred identity threads."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.68))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.8)
    _refresh_lens(ax)

    ax.text(5.0, 7.57, "BINDING TIME CHANGES THE CORRECT TARGET", ha="center", va="top", fontsize=7.0, color=INK, weight="bold")
    ax.text(2.18, 6.88, "$S_0$  BEFORE", ha="center", va="center", fontsize=6.0, color=INK, weight="bold")
    ax.text(7.82, 6.88, "$S_1$  AFTER", ha="center", va="center", fontsize=6.0, color=INK, weight="bold")

    # Ranking swap: the two envelopes cross inside the refresh lens.
    ax.add_patch(
        FancyArrowPatch(
            (2.25, 6.00),
            (7.60, 5.40),
            arrowstyle="-|>",
            mutation_scale=6,
            connectionstyle="arc3,rad=-0.07",
            color=A_RED,
            lw=1.0,
            alpha=0.75,
            zorder=1,
        )
    )
    ax.add_patch(
        FancyArrowPatch(
            (2.90, 5.40),
            (6.95, 6.00),
            arrowstyle="-|>",
            mutation_scale=6,
            connectionstyle="arc3,rad=-0.08",
            color=B_GREEN,
            lw=1.0,
            alpha=0.75,
            zorder=1,
        )
    )
    _envelope(ax, 1.88, 6.00, "A", A_RED, A_LIGHT, "o", selected=True)
    _envelope(ax, 2.58, 5.40, "B", B_GREEN, PAPER, "s")
    _envelope(ax, 7.42, 6.00, "B", B_GREEN, B_LIGHT, "s", selected=True)
    _envelope(ax, 8.00, 5.40, "A", A_RED, PAPER, "o")
    ax.text(1.88, 6.38, "selector winner: A", ha="center", va="bottom", fontsize=5.9, color=A_RED, weight="bold")
    ax.text(7.42, 6.38, "selector winner: B", ha="center", va="bottom", fontsize=5.9, color=B_GREEN, weight="bold")
    ax.text(8.00, 5.03, "A stays action-valid", ha="center", va="top", fontsize=5.8, color=MUTED)

    ax.plot([0.46, 9.54], [4.72, 4.72], color=HAIRLINE, lw=0.55, zorder=0)
    ax.text(0.48, 4.92, "IDENTITY THREAD", ha="left", va="bottom", fontsize=5.8, color=MUTED, weight="bold")

    # Preserve: a wax-seal-like binding carries A through the refresh.
    ax.text(0.48, 3.83, "PRESERVE", ha="left", va="center", fontsize=6.4, color=A_RED, weight="bold")
    ax.text(0.48, 3.48, "bind before", ha="left", va="center", fontsize=5.7, color=MUTED)
    _seal(ax, 2.72, 3.67, "A", A_RED, "o")
    ax.text(2.72, 3.18, "bound A", ha="center", va="top", fontsize=5.7, color=A_RED, weight="bold")
    ax.plot([3.03, 6.18], [3.67, 3.67], color=A_RED, lw=2.0, solid_capstyle="round", zorder=3)

    # The schematic error branch splices the refreshed winner into the preserved thread.
    ax.add_patch(
        FancyArrowPatch(
            (7.35, 5.73),
            (6.20, 3.72),
            arrowstyle="-|>",
            mutation_scale=6,
            connectionstyle="arc3,rad=0.13",
            color=WRONG,
            linewidth=0.9,
            linestyle=(0, (2.4, 2.0)),
            zorder=4,
        )
    )
    ax.scatter(6.22, 3.67, s=35, marker="X", facecolor=SELECT_GOLD, edgecolor=WRONG, lw=0.7, zorder=7)
    ax.text(6.25, 4.15, "selector re-run", ha="center", va="center", fontsize=5.9, color=WRONG, weight="bold")

    ax.plot([6.30, 7.88], [3.67, 3.88], color=A_RED, lw=0.9, alpha=0.45, zorder=2)
    _arrow(ax, (7.88, 3.88), (8.15, 3.88), A_RED, 0.9, zorder=3)
    _envelope(ax, 8.22, 3.88, "A", A_RED, PAPER, "o", width=0.67, height=0.45)
    ax.text(8.22, 4.22, "correct: A", ha="center", va="bottom", fontsize=5.75, color=A_RED, weight="bold")

    ax.add_patch(
        FancyArrowPatch(
            (6.30, 3.61),
            (7.78, 3.18),
            arrowstyle="-|>",
            mutation_scale=7,
            connectionstyle="arc3,rad=0.10",
            color=WRONG,
            linewidth=1.25,
            linestyle=(0, (3.0, 1.8)),
            zorder=4,
        )
    )
    _envelope(ax, 8.22, 3.18, "B", WRONG, "#F4E3E6", "s", width=0.67, height=0.45)
    ax.scatter(8.66, 3.18, s=30, marker="X", facecolor=WRONG, edgecolor=PAPER, lw=0.55, zorder=8)
    ax.text(8.22, 2.84, "example error: B", ha="center", va="top", fontsize=5.55, color=WRONG, weight="bold")

    # Reevaluate: the open query becomes a B binding only after the lens.
    ax.text(0.48, 2.18, "REEVALUATE", ha="left", va="center", fontsize=6.4, color=B_GREEN, weight="bold")
    ax.text(0.48, 1.83, "bind after", ha="left", va="center", fontsize=5.7, color=MUTED)
    _seal(ax, 2.72, 2.02, "?", B_GREEN, "D", filled=False)
    ax.text(2.72, 1.53, "deferred", ha="center", va="top", fontsize=5.7, color=B_GREEN, weight="bold")
    ax.plot([3.03, 5.33], [2.02, 2.02], color=B_GREEN, lw=1.45, ls=(0, (2.8, 2.0)), solid_capstyle="round", zorder=3)
    _seal(ax, 6.18, 2.02, "B", B_GREEN, "s")
    ax.text(6.18, 1.53, "bound B", ha="center", va="top", fontsize=5.7, color=B_GREEN, weight="bold")
    _arrow(ax, (6.49, 2.02), (7.98, 2.02), B_GREEN, 1.55, zorder=3)
    _envelope(ax, 8.22, 2.02, "B", B_GREEN, B_LIGHT, "s", width=0.67, height=0.45)
    ax.text(8.22, 1.68, "correct: B", ha="center", va="top", fontsize=5.75, color=B_GREEN, weight="bold")

    ax.plot([0.48, 9.52], [0.91, 0.91], color=HAIRLINE, lw=0.55)
    ax.text(0.48, 0.56, "MATCHED PAIR", ha="left", va="center", fontsize=5.9, color=INK, weight="bold")
    ax.text(6.20, 0.56, "same transition · only binding time differs · correct A vs B", ha="center", va="center", fontsize=5.7, color=MUTED)

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.subplots_adjust(left=0.015, right=0.992, top=0.99, bottom=0.02)
    _save(fig, stem)


def build_round4(stem: Path) -> None:
    """Simplified single-column schematic with no text below 8 pt."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.05))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.15)
    _refresh_lens(ax)

    ax.text(5.0, 7.86, "RESOLUTION TIMING CHANGES", ha="center", va="center", fontsize=9.0, color=INK, weight="bold")
    ax.text(5.0, 7.50, "THE CORRECT TARGET", ha="center", va="center", fontsize=9.0, color=INK, weight="bold")
    ax.text(2.18, 6.14, "$S_0$  BEFORE", ha="center", va="center", fontsize=8.2, color=INK, weight="bold")
    ax.text(7.82, 6.14, "$S_1$  AFTER", ha="center", va="center", fontsize=8.2, color=INK, weight="bold")

    _envelope(ax, 2.15, 5.45, "A", A_RED, A_LIGHT, "o", selected=True, width=0.82, height=0.52)
    _envelope(ax, 7.85, 5.45, "B", B_GREEN, B_LIGHT, "s", selected=True, width=0.82, height=0.52)
    ax.text(2.15, 5.84, "selector winner: A", ha="center", va="bottom", fontsize=8.0, color=A_RED, weight="bold")
    ax.text(7.85, 5.84, "selector winner: B", ha="center", va="bottom", fontsize=8.0, color=B_GREEN, weight="bold")
    ax.add_patch(FancyArrowPatch((2.60, 5.45), (7.40, 5.45), arrowstyle="-|>", mutation_scale=8, color=HAIRLINE, linewidth=1.0))
    ax.text(7.85, 4.93, "A remains action-valid", ha="center", va="center", fontsize=8.0, color=MUTED)

    ax.plot([0.45, 9.55], [4.55, 4.55], color=HAIRLINE, lw=0.7)
    ax.text(0.48, 3.88, "PRESERVE", ha="left", va="center", fontsize=8.5, color=A_RED, weight="bold")
    ax.text(0.48, 3.48, "bind before", ha="left", va="center", fontsize=8.0, color=MUTED)
    _seal(ax, 2.72, 3.68, "A", A_RED, "o")
    ax.plot([3.03, 7.50], [3.68, 3.68], color=A_RED, lw=2.0, solid_capstyle="round")
    _envelope(ax, 8.10, 3.68, "A", A_RED, PAPER, "o", width=0.75, height=0.48)
    ax.text(8.52, 3.68, "correct", ha="left", va="center", fontsize=8.0, color=A_RED, weight="bold")

    ax.add_patch(FancyArrowPatch((7.55, 5.25), (6.25, 3.72), arrowstyle="-|>", mutation_scale=8, connectionstyle="arc3,rad=0.12", color=WRONG, linewidth=1.0, linestyle=(0, (3, 2))))
    ax.add_patch(FancyArrowPatch((6.32, 3.58), (7.60, 3.05), arrowstyle="-|>", mutation_scale=8, connectionstyle="arc3,rad=0.08", color=WRONG, linewidth=1.3, linestyle=(0, (3, 2))))
    _envelope(ax, 8.10, 2.97, "B", WRONG, "#F4E3E6", "s", width=0.75, height=0.48)
    ax.text(8.52, 2.97, "error", ha="left", va="center", fontsize=8.0, color=WRONG, weight="bold")

    ax.text(0.48, 2.08, "REEVALUATE", ha="left", va="center", fontsize=8.5, color=B_GREEN, weight="bold")
    ax.text(0.48, 1.68, "bind after", ha="left", va="center", fontsize=8.0, color=MUTED)
    _seal(ax, 2.72, 1.88, "?", B_GREEN, "D", filled=False)
    ax.plot([3.03, 5.38], [1.88, 1.88], color=B_GREEN, lw=1.5, ls=(0, (3, 2)))
    _seal(ax, 6.18, 1.88, "B", B_GREEN, "s")
    _arrow(ax, (6.49, 1.88), (7.70, 1.88), B_GREEN, 1.7)
    _envelope(ax, 8.10, 1.88, "B", B_GREEN, B_LIGHT, "s", width=0.75, height=0.48)
    ax.text(8.52, 1.88, "correct", ha="left", va="center", fontsize=8.0, color=B_GREEN, weight="bold")

    ax.plot([0.48, 9.52], [0.84, 0.84], color=HAIRLINE, lw=0.7)
    ax.text(5.0, 0.43, "MATCHED PAIR: same transition, opposite targets", ha="center", va="center", fontsize=8.0, color=INK, weight="bold")
    ax.set_axis_off()
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    _save(fig, stem)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=root / "outputs" / "round4")
    args = parser.parse_args()
    build_round4(args.output_dir / "fig1_referent_trajectory_round4")
