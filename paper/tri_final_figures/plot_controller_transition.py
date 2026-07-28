#!/usr/bin/env python3
"""Draw cross-schema controller transitions with paired slopes and confidence intervals."""

from __future__ import annotations

import argparse
import csv
from math import sqrt
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DATA = SCRIPT_DIR / "data" / "summary_csv" / "v7_shared_eligible_pairacc_and_substitution.csv"
FALLBACK_DATA = PROJECT_DATA
DATA = PROJECT_DATA if PROJECT_DATA.exists() else FALLBACK_DATA
DEFAULT_OUTPUT = SCRIPT_DIR / "outputs" / "fig_controller_transition" if PROJECT_DATA.exists() else SCRIPT_DIR / "tri_controller_transition_figure"
MODELS = ("Qwen3.5", "GLM-5.1", "DeepSeek")
LABELS = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM", "DeepSeek": "DeepSeek"}
MARKERS = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}
OFFSETS = {"Qwen3.5": -0.055, "GLM-5.1": 0.0, "DeepSeek": 0.055}
COLORS = {
    "ink": "#253238",
    "line": "#AAB4BA",
    "grid": "#D9E0E4",
    "generic": "#5E379D",
    "cta": "#2F74B8",
}


def load(path: Path) -> dict[tuple[str, str], dict[str, float]]:
    data: dict[tuple[str, str], dict[str, float]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["controller"] not in {"Generic", "CTA"}:
                continue
            data[(row["model"], row["controller"])] = {
                "eligible": float(row["shared_eligible"]),
                "sub": float(row["substitutions"]),
                "sub_rate": float(row["substitution_rate_pct"]),
                "pairacc": float(row["pairacc_pct"]),
                "pairacc_low": float(row["pairacc_ci95_low_pct"]),
                "pairacc_high": float(row["pairacc_ci95_high_pct"]),
            }
    return data


def wilson_interval(successes: float, total: float) -> tuple[float, float]:
    """Two-sided 95% Wilson interval in percentage points."""
    z = 1.959963984540054
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    radius = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return 100 * max(0.0, center - radius), 100 * min(1.0, center + radius)


def plot_panel(ax: plt.Axes, rows: dict[tuple[str, str], dict[str, float]], metric: str) -> None:
    for model in MODELS:
        generic = rows[(model, "Generic")]
        cta = rows[(model, "CTA")]
        offset = OFFSETS[model]
        if metric == "substitution":
            generic_value, cta_value = generic["sub_rate"], cta["sub_rate"]
            g_low, g_high = wilson_interval(generic["sub"], generic["eligible"])
            c_low, c_high = wilson_interval(cta["sub"], cta["eligible"])
            if model == "Qwen3.5":
                text = f"{int(generic['sub'])}/{int(generic['eligible'])}"
                ax.text(-0.10, generic_value, text, ha="right", va="center", fontsize=7.2, color=COLORS["ink"])
            elif model == "GLM-5.1":
                ax.text(-0.10, generic_value, f"{int(generic['sub'])}/{int(generic['eligible'])}", ha="right", va="center", fontsize=7.2, color=COLORS["ink"])
            else:
                ax.text(-0.10, generic_value, f"{int(generic['sub'])}/{int(generic['eligible'])}", ha="right", va="center", fontsize=7.2, color=COLORS["ink"])
        else:
            generic_value, cta_value = generic["pairacc"], cta["pairacc"]
            g_low, g_high = generic["pairacc_low"], generic["pairacc_high"]
            c_low, c_high = cta["pairacc_low"], cta["pairacc_high"]

        xs = (0 + offset, 1 + offset)
        ax.plot(xs, (generic_value, cta_value), color=COLORS["line"], linewidth=1.0, zorder=1)
        ax.errorbar(
            xs[0],
            generic_value,
            yerr=[[max(0.0, generic_value - g_low)], [max(0.0, g_high - generic_value)]],
            fmt=MARKERS[model],
            markersize=5.8,
            markerfacecolor=COLORS["generic"],
            markeredgecolor=COLORS["ink"],
            markeredgewidth=0.55,
            ecolor=COLORS["generic"],
            elinewidth=0.9,
            capsize=2.0,
            zorder=3,
        )
        ax.errorbar(
            xs[1],
            cta_value,
            yerr=[[max(0.0, cta_value - c_low)], [max(0.0, c_high - cta_value)]],
            fmt=MARKERS[model],
            markersize=5.8,
            markerfacecolor="white",
            markeredgecolor=COLORS["cta"],
            markeredgewidth=1.2,
            ecolor=COLORS["cta"],
            elinewidth=0.9,
            capsize=2.0,
            zorder=3,
        )

    ax.set_xlim(-0.22, 1.20)
    ax.set_xticks([0, 1], ["Generic", "CTA"])
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.55)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["bottom"].set_color(COLORS["ink"])
    ax.tick_params(axis="x", length=0, pad=4)


def draw(rows: dict[tuple[str, str], dict[str, float]], output: Path) -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 7.5,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
        }
    )
    fig, axes = plt.subplots(2, 1, figsize=(3.25, 3.05), sharex=True, gridspec_kw={"hspace": 0.42})
    top, bottom = axes
    plot_panel(top, rows, "substitution")
    plot_panel(bottom, rows, "pairacc")
    top.set_ylim(-5, 90)
    top.set_yticks([0, 25, 50, 75])
    top.set_ylabel("Conditional\nsubstitution (%)")
    top.set_title("A  Substitution after correct binding", loc="left", fontsize=8.7, weight="bold", pad=4)
    bottom.set_ylim(0, 100)
    bottom.set_yticks([0, 25, 50, 75, 100])
    bottom.set_ylabel("Cross-schema\nPairAcc (%)")
    bottom.set_title("B  Cross-schema PairAcc", loc="left", fontsize=8.7, weight="bold", pad=4)
    legend = [
        Line2D([0], [0], marker=MARKERS[model], color="none", markerfacecolor="white", markeredgecolor=COLORS["ink"], markersize=5.2, label=LABELS[model])
        for model in MODELS
    ]
    fig.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.52, -0.015), ncol=3, frameon=False, handletextpad=0.3, columnspacing=1.0, fontsize=7.2)
    fig.subplots_adjust(left=0.22, right=0.985, top=0.94, bottom=0.15)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".svg"))
    fig.savefig(output.with_suffix(".png"), dpi=400)
    plt.close(fig)
    with Image.open(output.with_suffix(".png")) as image:
        image.convert("RGB").save(output.with_suffix(".pdf"), resolution=400)
        image.convert("L").save(output.with_name(output.name + "_grayscale.png"), dpi=(400, 400))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    draw(load(args.data), args.output)


if __name__ == "__main__":
    main()
