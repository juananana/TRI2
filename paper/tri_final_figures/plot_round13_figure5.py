from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt


DATA = Path("./paper/tri_final_figures/data/summary_csv/main_figure_paired_scores.csv")
OUT = Path(__file__).resolve().parent / "tri-round13"

INK = "#263238"
MUTED = "#66747A"
GRID = "#D4DCDE"
PAPER = "#FFFFFF"
BLUE = "#264A56"
TEAL = "#248D82"
AMBER = "#C98C2E"
GROUP_BG = {"Authored": "#EAF0F1", "Rewrite": "#FFF4E2", "Source-derived": "#EAF5F2"}

MODEL_MARKER = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}
DATASET_COLOR = {"Authored": BLUE, "Rewrite": AMBER, "Source-derived": TEAL}
DATASET_FILLED = {"Authored": True, "Rewrite": False, "Source-derived": False}


def style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.4,
            "axes.labelsize": 7.4,
            "axes.titlesize": 8.2,
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


def read_rows() -> list[dict[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find(rows: list[dict[str, str]], panel: str, dataset: str, model: str) -> dict[str, str]:
    matches = [row for row in rows if row["panel"] == panel and row["dataset"] == dataset and row["model"] == model]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {panel}/{dataset}/{model}, found {len(matches)}")
    return matches[0]


def row_label(dataset: str, model: str, row: dict[str, str]) -> str:
    dataset_short = {"Authored": "Auth", "Rewrite": "Rewrite", "Source-derived": "Source"}[dataset]
    model_short = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM", "DeepSeek": "DeepSeek"}[model]
    return f"{dataset_short}/{model_short}"


def draw_panel(
    ax: plt.Axes,
    rows: list[dict[str, str]],
    panel: str,
    specs: list[tuple[str, str]],
    y_positions: list[float],
    title: str,
    xlim: tuple[float, float],
    xticks: list[int],
) -> None:
    for dataset in dict.fromkeys(dataset for dataset, _ in specs):
        group_y = [y for (row_dataset, _), y in zip(specs, y_positions) if row_dataset == dataset]
        ax.axhspan(min(group_y) - 0.38, max(group_y) + 0.38, color=GROUP_BG[dataset], zorder=0)
    ax.axvline(0, color=MUTED, lw=0.8, zorder=1)

    previous_dataset = None
    for (dataset, model), y in zip(specs, y_positions):
        row = find(rows, panel, dataset, model)
        value = float(row["difference_pp"])
        low = float(row["ci95_low_pp"])
        high = float(row["ci95_high_pp"])
        color = DATASET_COLOR[dataset]
        marker = MODEL_MARKER[model]
        filled = DATASET_FILLED[dataset]
        ax.plot([0, value], [y, y], color=color, lw=1.35, solid_capstyle="round", zorder=2)
        ax.errorbar(
            value,
            y,
            xerr=[[value - low], [high - value]],
            fmt=marker,
            ms=5.0,
            mfc=color if filled else PAPER,
            mec=color,
            mew=0.9,
            ecolor=color,
            elinewidth=0.85,
            capsize=2.0,
            zorder=3,
        )
        if previous_dataset is not None and dataset != previous_dataset:
            ax.axhline(y + 0.5, color=GRID, lw=0.55, zorder=1)
        previous_dataset = dataset

    labels = [row_label(dataset, model, find(rows, panel, dataset, model)) for dataset, model in specs]
    ax.set_yticks(y_positions, labels, fontsize=7.0)
    ax.set_xlim(*xlim)
    ax.set_xticks(xticks)
    ax.set_xlabel("Decision-visible − History-only (pp)")
    ax.set_title(title, loc="left", pad=2, weight="bold")
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=4)


def save(fig: plt.Figure) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig5_grouped_lollipop_round13"
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=360)
    plt.close(fig)


def main() -> None:
    style()
    rows = read_rows()

    pair_specs = [
        ("Authored", "Qwen3.5"),
        ("Authored", "GLM-5.1"),
        ("Source-derived", "Qwen3.5"),
        ("Source-derived", "GLM-5.1"),
        ("Source-derived", "DeepSeek"),
    ]
    e2e_specs = [
        ("Authored", "Qwen3.5"),
        ("Authored", "GLM-5.1"),
        ("Rewrite", "Qwen3.5"),
        ("Rewrite", "GLM-5.1"),
        ("Source-derived", "Qwen3.5"),
        ("Source-derived", "GLM-5.1"),
        ("Source-derived", "DeepSeek"),
    ]

    fig, (pair_ax, e2e_ax) = plt.subplots(1, 2, figsize=(6.85, 2.25), gridspec_kw={"wspace": 0.52})
    draw_panel(
        pair_ax,
        rows,
        "pairacc",
        pair_specs,
        [6.0, 5.0, 3.5, 2.5, 1.5],
        "A  Changed-winner PairAcc",
        (-16, 82),
        [-10, 0, 20, 40, 60, 80],
    )
    pair_ax.set_ylim(0.35, 6.65)
    draw_panel(
        e2e_ax,
        rows,
        "e2e",
        e2e_specs,
        [6.0, 5.0, 3.8, 2.8, 1.6, 0.6, -0.4],
        "B  Actionable E2E",
        (-11, 34),
        [-10, 0, 10, 20, 30],
    )
    e2e_ax.set_ylim(-0.95, 6.65)

    fig.subplots_adjust(left=0.15, right=0.985, top=0.94, bottom=0.20)
    save(fig)


if __name__ == "__main__":
    main()
