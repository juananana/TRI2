from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle


DATA = Path("./paper/tri_final_figures/data/summary_csv/sqlite_model_facing_outcomes.csv")
OUT = Path(__file__).resolve().parent / "tri-round11"

INK = "#263238"
MUTED = "#66747A"
GRID = "#D4DCDE"
PAPER = "#FFFFFF"
TEAL = "#2D7873"
CORAL = "#B9554F"
AMBER = "#996719"
BLUE = "#4E739D"
REJECT = "#C9D0D2"
MODEL_COLORS = {"Qwen3.5": BLUE, "GLM-5.1": AMBER}
MODEL_MARKERS = {"Qwen3.5": "o", "GLM-5.1": "s"}
MODEL_LABELS = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM"}


def style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.4,
            "axes.labelsize": 7.4,
            "axes.titlesize": 8.0,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.0,
            "hatch.linewidth": 0.35,
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
        rows = list(csv.DictReader(handle))
    for row in rows:
        total = sum(int(row[key]) for key in ("correct_final_state", "core_tri_write", "fallback_wrong_write", "unneeded_reject"))
        if total != int(row["tasks"]) or total != 40:
            raise ValueError(f"Outcome counts do not sum to 40: {row}")
    return rows


def find(rows: list[dict[str, str]], model: str) -> dict[str, str]:
    matches = [row for row in rows if row["model"] == model and row["controller"] == "Generic"]
    if len(matches) != 1:
        raise ValueError(f"Expected one Generic row for {model}")
    return matches[0]


def wilson(k: int, n: int) -> tuple[float, float, float]:
    z = 1.959963984540054
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return 100 * p, 100 * max(0, center - half), 100 * min(1, center + half)


def save(fig: plt.Figure) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig4_sqlite_outcome_ribbons_round11"
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=360)
    plt.close(fig)


def main() -> None:
    style()
    rows = read_rows()
    fig = plt.figure(figsize=(3.35, 2.95))
    grid = fig.add_gridspec(2, 1, height_ratios=[1.25, 1.0], hspace=0.46)
    outcome_ax = fig.add_subplot(grid[0])
    opportunity_ax = fig.add_subplot(grid[1])

    categories = [
        ("correct_final_state", "Correct", TEAL, None),
        ("core_tri_write", "TRI write", CORAL, "////"),
        ("fallback_wrong_write", "Fallback", AMBER, ".."),
        ("unneeded_reject", "Reject", REJECT, "\\\\"),
    ]
    y_positions = {"Qwen3.5": 1.0, "GLM-5.1": 0.0}
    bar_height = 0.42

    for model in ("Qwen3.5", "GLM-5.1"):
        row = find(rows, model)
        cursor = 0
        y = y_positions[model]
        for key, _, color, hatch in categories:
            value = int(row[key])
            if value == 0:
                continue
            patch = Rectangle(
                (cursor, y - bar_height / 2),
                value,
                bar_height,
                facecolor=color,
                edgecolor=INK,
                linewidth=0.5,
                hatch=hatch,
                zorder=2,
            )
            outcome_ax.add_patch(patch)
            text_color = INK if key == "unneeded_reject" else PAPER
            outcome_ax.text(cursor + value / 2, y, str(value), ha="center", va="center", color=text_color, fontsize=7.0, weight="bold", zorder=3)
            cursor += value

    outcome_ax.set_xlim(0, 40)
    outcome_ax.set_ylim(-0.55, 1.90)
    outcome_ax.set_yticks([1.0, 0.0], ["Qwen", "GLM"], weight="bold")
    outcome_ax.set_xticks([0, 10, 20, 30, 40])
    outcome_ax.set_title("A  Outcome composition (n=40/model)", loc="left", pad=2, weight="bold")
    outcome_ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    outcome_ax.set_axisbelow(True)
    outcome_ax.spines[["top", "right", "left"]].set_visible(False)
    outcome_ax.tick_params(axis="y", length=0, pad=5)
    legend = [Patch(facecolor=color, edgecolor=INK if hatch else color, hatch=hatch, label=label) for _, label, color, hatch in categories]
    outcome_ax.legend(
        handles=legend,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.96),
        ncol=4,
        frameon=False,
        fontsize=7.0,
        handlelength=1.0,
        handleheight=0.7,
        handletextpad=0.25,
        columnspacing=0.55,
    )

    opportunity_ax.axhspan(0, 6, color="#DDEBE9", zorder=0)
    offsets = {"Qwen3.5": -0.035, "GLM-5.1": 0.035}
    for model in ("Qwen3.5", "GLM-5.1"):
        row = find(rows, model)
        stable_k, stable_n = int(row["stable_writes"]), int(row["stable_opportunities"])
        changed_k, changed_n = int(row["strict_core_writes"]), int(row["strict_core_opportunities"])
        sr, sl, sh = wilson(stable_k, stable_n)
        cr, cl, ch = wilson(changed_k, changed_n)
        color, marker = MODEL_COLORS[model], MODEL_MARKERS[model]
        x0, x1 = offsets[model], 1 + offsets[model]
        opportunity_ax.plot([x0, x1], [sr, cr], color=color, lw=1.05, zorder=2)
        opportunity_ax.errorbar(
            x0,
            sr,
            yerr=[[max(0.0, sr - sl)], [max(0.0, sh - sr)]],
            fmt=marker,
            ms=4.6,
            mfc=PAPER,
            mec=color,
            mew=0.85,
            ecolor=color,
            elinewidth=0.8,
            capsize=2.0,
            zorder=3,
        )
        opportunity_ax.errorbar(
            x1,
            cr,
            yerr=[[max(0.0, cr - cl)], [max(0.0, ch - cr)]],
            fmt=marker,
            ms=4.6,
            mfc=color,
            mec=color,
            ecolor=color,
            elinewidth=0.8,
            capsize=2.0,
            zorder=3,
        )
        opportunity_ax.text(1.12, cr, f"{MODEL_LABELS[model]} {changed_k}/{changed_n}", ha="left", va="center", fontsize=7.0, color=color, weight="bold")

    opportunity_ax.text(-0.08, 8.5, "both 0/4", ha="right", va="bottom", fontsize=7.0, color=MUTED, weight="bold")
    opportunity_ax.set_xlim(-0.24, 1.48)
    opportunity_ax.set_ylim(-4, 112)
    opportunity_ax.set_xticks([0, 1], ["Stable", "Changed"], weight="bold")
    opportunity_ax.set_yticks([0, 50, 100])
    opportunity_ax.set_ylabel("Conditional write (%)")
    opportunity_ax.set_title("B  Strict-opportunity calibration", loc="left", pad=2, weight="bold")
    opportunity_ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    opportunity_ax.set_axisbelow(True)
    opportunity_ax.spines[["top", "right", "bottom"]].set_visible(False)
    opportunity_ax.tick_params(axis="x", length=0, pad=4)

    fig.subplots_adjust(left=0.17, right=0.955, top=0.96, bottom=0.13)
    save(fig)


if __name__ == "__main__":
    main()
