from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch


DATA = Path("./paper/tri_final_figures/data/summary_csv/sqlite_model_facing_outcomes.csv")
OUT = Path(__file__).resolve().parent / "tri-round12"

INK = "#263238"
MUTED = "#66747A"
GRID = "#CBD4D6"
PAPER = "#FFFFFF"
SOURCE = "#476A7F"
TEAL = "#2D7A75"
CORAL = "#C45A52"
AMBER = "#9B6816"
SLATE = "#7B888D"


def style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.4,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "text.color": INK,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )


def rows() -> list[dict[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find(items: list[dict[str, str]], model: str) -> dict[str, str]:
    matches = [row for row in items if row["model"] == model and row["controller"] == "Generic"]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {model}")
    return matches[0]


def ribbon(
    ax: plt.Axes,
    x0: float,
    x1: float,
    y0_low: float,
    y0_high: float,
    y1_low: float,
    y1_high: float,
    color: str,
) -> None:
    control = (x1 - x0) * 0.45
    vertices = [
        (x0, y0_low),
        (x0 + control, y0_low),
        (x1 - control, y1_low),
        (x1, y1_low),
        (x1, y1_high),
        (x1 - control, y1_high),
        (x0 + control, y0_high),
        (x0, y0_high),
        (x0, y0_low),
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
    ax.add_patch(PathPatch(MplPath(vertices, codes), facecolor=color, edgecolor="none", alpha=0.88, zorder=1))


def save(fig: plt.Figure) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig4_sqlite_alluvial_recolored_round12"
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=360)
    plt.close(fig)


def main() -> None:
    style()
    data = rows()
    fig, ax = plt.subplots(figsize=(3.35, 2.90))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    categories = [
        ("correct_final_state", "Correct", TEAL),
        ("core_tri_write", "TRI", CORAL),
        ("fallback_wrong_write", "Fallback", AMBER),
        ("unneeded_reject", "Reject", SLATE),
    ]
    panel_centers = {"Qwen3.5": 0.72, "GLM-5.1": 0.28}
    labels = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM"}
    x0, x1 = 0.22, 0.72
    scale = 0.0060
    gap = 0.012

    for model in ("Qwen3.5", "GLM-5.1"):
        row = find(data, model)
        total = int(row["tasks"])
        values = [(key, label, color, int(row[key])) for key, label, color in categories if int(row[key]) > 0]
        if sum(value for _, _, _, value in values) != total:
            raise ValueError(f"Outcome counts do not sum to {total}: {row}")

        center = panel_centers[model]
        total_height = total * scale
        source_bottom = center - total_height / 2
        source_cursor = source_bottom
        target_total = total_height + gap * (len(values) - 1)
        target_cursor = center + target_total / 2

        ax.plot([x0, x0], [source_bottom, source_bottom + total_height], color=SOURCE, lw=3.4, solid_capstyle="butt", zorder=3)
        ax.text(0.025, center + 0.018, labels[model], ha="left", va="center", fontsize=8.0, weight="bold")
        ax.text(0.025, center - 0.040, f"n={total}", ha="left", va="center", fontsize=7.0, color=MUTED)

        for key, label, color, value in values:
            height = value * scale
            source_low, source_high = source_cursor, source_cursor + height
            target_high, target_low = target_cursor, target_cursor - height
            ribbon(ax, x0, x1, source_low, source_high, target_low, target_high, color)
            ax.plot([x1, x1], [target_low, target_high], color=color, lw=3.4, solid_capstyle="butt", zorder=3)
            if key == "core_tri_write":
                text = f"{label} {value} ({value}/{row['strict_core_opportunities']})"
            else:
                text = f"{label} {value}"
            ax.text(0.755, (target_low + target_high) / 2, text, ha="left", va="center", fontsize=7.0, color=color, weight="bold")
            source_cursor = source_high
            target_cursor = target_low - gap

        stable_y = target_cursor + gap - 0.045
        ax.scatter(0.755, stable_y, s=17, marker="o", facecolor=PAPER, edgecolor=MUTED, linewidth=0.8)
        ax.text(0.78, stable_y, "Stable 0/4", ha="left", va="center", fontsize=7.0, color=MUTED)

    ax.plot([0.02, 0.98], [0.50, 0.50], color=GRID, lw=0.6, ls=(0, (3, 3)))
    fig.subplots_adjust(left=0.02, right=0.99, top=0.98, bottom=0.02)
    save(fig)


if __name__ == "__main__":
    main()
