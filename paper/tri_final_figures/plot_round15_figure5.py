from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "data" / "summary_csv" / "main_figure_paired_scores.csv"
DEFAULT_OUTPUT = HERE / "outputs" / "round15"

INK = "#263238"
MUTED = "#66747A"
GRID = "#D7DEE0"
PAPER = "#FFFFFF"
POSITIVE = "#F1F7F6"
AUTHORED = "#294F5A"
SOURCE = "#23877E"

MODEL_MARKER = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}
MODEL_LABEL = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM", "DeepSeek": "DeepSeek"}


def style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.6,
            "axes.labelsize": 7.6,
            "axes.titlesize": 8.2,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.4,
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.0,
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


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find(
    rows: list[dict[str, str]], panel: str, dataset: str, model: str
) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if row["panel"] == panel
        and row["dataset"] == dataset
        and row["model"] == model
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one row for {panel}/{dataset}/{model}, found {len(matches)}"
        )
    return matches[0]


def draw_interval(
    ax: plt.Axes,
    row: dict[str, str],
    y: float,
    color: str,
    marker: str,
    filled: bool,
) -> None:
    effect = float(row["difference_pp"])
    low = float(row["ci95_low_pp"])
    high = float(row["ci95_high_pp"])
    ax.errorbar(
        effect,
        y,
        xerr=[[effect - low], [high - effect]],
        fmt=marker,
        ms=5.2,
        mfc=color if filled else PAPER,
        mec=color,
        mew=1.0,
        ecolor=color,
        elinewidth=1.05,
        capsize=2.2,
        capthick=0.9,
        zorder=3,
    )


def configure_axis(
    ax: plt.Axes,
    title: str,
    limits: tuple[float, float],
    ticks: list[int],
) -> None:
    ax.axvspan(0, limits[1], color=POSITIVE, zorder=0)
    ax.axvline(0, color=MUTED, lw=0.9, zorder=1)
    ax.axhline(2.5, color=GRID, lw=0.7, ls=(0, (2.2, 2.2)), zorder=1)
    ax.set_xlim(*limits)
    ax.set_xticks(ticks)
    ax.set_ylim(-0.55, 5.45)
    ax.set_title(title, loc="left", pad=3.0, weight="bold")
    ax.grid(axis="x", color=GRID, lw=0.55, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.tick_params(axis="x", length=2.6, width=0.6, pad=2)


def save(fig: plt.Figure, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = output_dir / "fig5_transfer_effect_profiles_round15"
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=400)
    plt.close(fig)


def build(data_path: Path, output_dir: Path) -> None:
    style()
    rows = read_rows(data_path)
    specs = [
        ("Authored", "Qwen3.5", 4.15, AUTHORED, True),
        ("Authored", "GLM-5.1", 3.25, AUTHORED, True),
        ("Source-derived", "Qwen3.5", 1.75, SOURCE, False),
        ("Source-derived", "GLM-5.1", 0.85, SOURCE, False),
        ("Source-derived", "DeepSeek", -0.05, SOURCE, False),
    ]

    fig, (pair_ax, e2e_ax) = plt.subplots(
        1,
        2,
        figsize=(3.35, 2.16),
        sharey=True,
        gridspec_kw={"width_ratios": [1.25, 1.0], "wspace": 0.13},
    )
    configure_axis(
        pair_ax,
        "A  PairAcc",
        (-13, 81),
        [0, 40, 80],
    )
    configure_axis(
        e2e_ax,
        "B  E2E",
        (-8, 31),
        [0, 10, 20, 30],
    )

    for dataset, model, y, color, filled in specs:
        marker = MODEL_MARKER[model]
        draw_interval(pair_ax, find(rows, "pairacc", dataset, model), y, color, marker, filled)
        draw_interval(e2e_ax, find(rows, "e2e", dataset, model), y, color, marker, filled)

    pair_ax.set_yticks(
        [4.15, 3.25, 1.75, 0.85, -0.05],
        [MODEL_LABEL[model] for _, model, _, _, _ in specs],
    )
    pair_ax.text(
        -0.49,
        5.02,
        "AUTHORED",
        transform=pair_ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=7.0,
        color=AUTHORED,
        weight="bold",
        clip_on=False,
    )
    pair_ax.text(
        -0.49,
        2.50,
        "SOURCE",
        transform=pair_ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=7.0,
        color=SOURCE,
        weight="bold",
        clip_on=False,
    )

    fig.text(
        0.63,
        0.030,
        "Decision-visible − History-only (pp)",
        ha="center",
        va="bottom",
        fontsize=7.6,
        color=INK,
    )
    fig.subplots_adjust(left=0.285, right=0.985, top=0.89, bottom=0.22)
    save(fig, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    build(args.data, args.output_dir)
