from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


DATA = Path("./paper/tri_final_figures/data/summary_csv/main_figure_paired_scores.csv")
OUT = Path(__file__).resolve().parent / "tri-round14"

INK = "#263238"
MUTED = "#66747A"
GRID = "#D4DCDE"
PAPER = "#FFFFFF"
AUTH = "#264A56"
SOURCE = "#248D82"
POSITIVE = "#EAF5F2"

MODEL_MARKER = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}


def style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.4,
            "axes.labelsize": 7.6,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "axes.linewidth": 0.65,
            "lines.linewidth": 0.95,
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


def rows() -> list[dict[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find(items: list[dict[str, str]], panel: str, dataset: str, model: str) -> dict[str, str]:
    matches = [row for row in items if row["panel"] == panel and row["dataset"] == dataset and row["model"] == model]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {panel}/{dataset}/{model}, found {len(matches)}")
    return matches[0]


def save(fig: plt.Figure) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig5_joint_effect_map_round14"
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=360)
    plt.close(fig)


def main() -> None:
    style()
    data = rows()
    fig, ax = plt.subplots(figsize=(6.85, 2.62))

    ax.add_patch(Rectangle((0, 0), 84, 34, facecolor=POSITIVE, edgecolor="none", zorder=0))
    ax.axvline(0, color=MUTED, lw=0.8, zorder=1)
    ax.axhline(0, color=MUTED, lw=0.8, zorder=1)

    specs = [
        ("Authored", "Qwen3.5", "Auth/Qwen", AUTH, True, (7, -10)),
        ("Authored", "GLM-5.1", "Auth/GLM", AUTH, True, (7, 7)),
        ("Source-derived", "Qwen3.5", "Source/Qwen", SOURCE, False, (-7, -16)),
        ("Source-derived", "GLM-5.1", "Source/GLM", SOURCE, False, (-7, 8)),
        ("Source-derived", "DeepSeek", "Source/DeepSeek", SOURCE, False, (7, -15)),
    ]

    for dataset, model, label, color, filled, offset in specs:
        pair = find(data, "pairacc", dataset, model)
        e2e = find(data, "e2e", dataset, model)
        x = float(pair["difference_pp"])
        x_low, x_high = float(pair["ci95_low_pp"]), float(pair["ci95_high_pp"])
        y = float(e2e["difference_pp"])
        y_low, y_high = float(e2e["ci95_low_pp"]), float(e2e["ci95_high_pp"])
        marker = MODEL_MARKER[model]
        ax.errorbar(
            x,
            y,
            xerr=[[x - x_low], [x_high - x]],
            yerr=[[y - y_low], [y_high - y]],
            fmt=marker,
            ms=6.0,
            mfc=color if filled else PAPER,
            mec=color,
            mew=1.0,
            ecolor=color,
            elinewidth=0.85,
            capsize=2.0,
            zorder=3,
        )
        ax.annotate(
            label,
            xy=(x, y),
            xytext=offset,
            textcoords="offset points",
            ha="left" if offset[0] >= 0 else "right",
            va="bottom" if offset[1] >= 0 else "top",
            fontsize=7.0,
            color=color,
            weight="bold",
            arrowprops={"arrowstyle": "-", "color": color, "lw": 0.55, "shrinkA": 2, "shrinkB": 4},
            zorder=4,
        )

    ax.text(81, 31.5, "both endpoints improve", ha="right", va="top", fontsize=7.0, color=SOURCE, weight="bold")

    ax.set_xlim(-15, 84)
    ax.set_ylim(-9, 34)
    ax.set_xticks([-10, 0, 20, 40, 60, 80])
    ax.set_yticks([-5, 0, 10, 20, 30])
    ax.set_xlabel("Changed-winner PairAcc effect (pp)")
    ax.set_ylabel("Actionable E2E effect (pp)")
    ax.grid(color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.subplots_adjust(left=0.105, right=0.985, top=0.97, bottom=0.20)
    save(fig)


if __name__ == "__main__":
    main()
