#!/usr/bin/env python3
"""Preview structural alternatives for the two latest result figures.

The previews keep frozen data and the Forest Ember palette. Figure 5 reuses
the approved upper outcome accounting and varies only the lower execution panel.
Figure 6 varies the representation of the two separate matched audits.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from PIL import Image, ImageDraw, ImageFont

import plot_round16_results as fig5
import plot_submission_critical_effects as fig6


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "outputs" / "figure5_6_structure_candidates_v1"
PAPER = "#FFFFFF"
INK = "#264A56"
MUTED = "#5F6B70"
GRID = "#D6E0DE"
TEAL = "#407A7F"
EMBER = "#E56D4E"
LEAF = "#60AA84"
PLUM = "#8B6F8E"


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.labelsize": 7.6,
            "axes.titlesize": 8.2,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "legend.fontsize": 6.8,
            "axes.linewidth": 0.65,
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


def save_figure(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"), metadata={"Creator": "TRI structure candidate preview"})
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=400)
    plt.close(fig)


def load_sqlite() -> list[dict[str, str]]:
    return fig5.read_rows("sqlite_model_facing_outcomes.csv")


def sqlite_rates(rows: list[dict[str, str]]) -> list[dict[str, float | str]]:
    output = []
    for model in ("Qwen3.5", "GLM-5.1"):
        row = fig5.find(rows, model=model, controller="Generic")
        stable_k, stable_n = int(row["stable_writes"]), int(row["stable_opportunities"])
        changed_k, changed_n = int(row["strict_core_writes"]), int(row["strict_core_opportunities"])
        sr, sl, sh = fig5.wilson(stable_k, stable_n)
        cr, cl, ch = fig5.wilson(changed_k, changed_n)
        output.append(
            {
                "model": "Qwen" if model == "Qwen3.5" else "GLM",
                "color": TEAL if model == "Qwen3.5" else EMBER,
                "stable": sr,
                "stable_low": sl,
                "stable_high": sh,
                "changed": cr,
                "changed_low": cl,
                "changed_high": ch,
                "changed_count": f"{changed_k}/{changed_n}",
            }
        )
    return output


def lower_endpoint_strips(ax: plt.Axes, data: list[dict[str, float | str]]) -> None:
    """Option 5A: two model rows, open/filled endpoint markers, no slope lines."""
    for y, row in zip([1.0, 0.0], data, strict=True):
        color = str(row["color"])
        ax.errorbar(
            float(row["stable"]), y,
            xerr=[[float(row["stable"]) - float(row["stable_low"])], [float(row["stable_high"]) - float(row["stable"])]],
            fmt="o", ms=4.8, mfc=PAPER, mec=color, ecolor=color, mew=0.9, capsize=2.0, elinewidth=0.8,
        )
        ax.errorbar(
            float(row["changed"]), y,
            xerr=[[float(row["changed"]) - float(row["changed_low"])], [float(row["changed_high"]) - float(row["changed"])]],
            fmt="s", ms=4.8, mfc=color, mec=color, ecolor=color, mew=0.9, capsize=2.0, elinewidth=0.8,
        )
        ax.text(103, y, str(row["changed_count"]), ha="left", va="center", fontsize=6.8, color=color, weight="bold")
    ax.set_title("B  Writes to the wrong target  |  A: endpoint strips", loc="left", pad=2, weight="bold")
    ax.set_yticks([1.0, 0.0], ["Qwen", "GLM"])
    ax.set_xlim(-8, 118)
    ax.set_ylim(-0.55, 1.55)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Rate (%)")
    ax.axvspan(0, 5, color="#E8F1ED", zorder=0)
    ax.grid(axis="x", color=GRID, lw=0.48)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=4)
    ax.legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", mfc=PAPER, mec=INK, ms=4.4, label="Stable"),
            Line2D([0], [0], marker="s", color="none", mfc=INK, mec=INK, ms=4.4, label="Changed"),
        ], loc="upper left", bbox_to_anchor=(0, 1.16), frameon=False, ncol=2, handletextpad=0.25, columnspacing=0.8,
    )


def lower_grouped_bars(ax: plt.Axes, data: list[dict[str, float | str]]) -> None:
    """Option 5B: direct grouped bars with one uncertainty cap per estimate."""
    x = np.arange(2)
    width = 0.28
    for offset, row in zip([-width / 2, width / 2], data, strict=True):
        color = str(row["color"])
        values = [float(row["stable"]), float(row["changed"])]
        lows = [float(row["stable_low"]), float(row["changed_low"])]
        highs = [float(row["stable_high"]), float(row["changed_high"])]
        ax.bar(x + offset, values, width=width, color=color, alpha=0.86, edgecolor=color, linewidth=0.7,
               label=str(row["model"]), zorder=2)
        ax.errorbar(x + offset, values, yerr=[np.array(values) - np.array(lows), np.array(highs) - np.array(values)],
                    fmt="none", ecolor=INK, elinewidth=0.7, capsize=1.8, capthick=0.7, zorder=3)
        for xx, value in zip(x + offset, values, strict=True):
            ax.text(xx, value + 4, f"{value:.0f}", ha="center", va="bottom", fontsize=6.8, color=INK)
    ax.set_title("B  Writes to the wrong target  |  B: grouped rates", loc="left", pad=2, weight="bold")
    ax.set_xticks(x, ["Stable", "Changed"])
    ax.set_ylim(-5, 112)
    ax.set_yticks([0, 50, 100])
    ax.set_ylabel("Rate (%)")
    ax.grid(axis="y", color=GRID, lw=0.48)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(0, 1.16), handlelength=0.9, columnspacing=0.7)


def lower_endpoint_tracks(ax: plt.Axes, data: list[dict[str, float | str]]) -> None:
    """Option 5C: compact tracks with stable/changed positions and CI ranges."""
    for y, row in zip([1.0, 0.0], data, strict=True):
        color = str(row["color"])
        ax.plot([0, 100], [y, y], color=GRID, lw=3.0, solid_capstyle="round", zorder=1)
        for key, marker, filled in (("stable", "o", False), ("changed", "s", True)):
            value = float(row[key])
            low = float(row[f"{key}_low"])
            high = float(row[f"{key}_high"])
            ax.plot([low, high], [y, y], color=color, lw=1.3, zorder=2)
            ax.scatter(value, y, marker=marker, s=25, facecolor=color if filled else PAPER, edgecolor=color, linewidth=0.9, zorder=3)
        ax.text(103, y, str(row["changed_count"]), ha="left", va="center", fontsize=6.8, color=color, weight="bold")
    ax.set_title("B  Writes to the wrong target  |  C: endpoint tracks", loc="left", pad=2, weight="bold")
    ax.set_yticks([1.0, 0.0], ["Qwen", "GLM"])
    ax.set_xlim(-8, 118)
    ax.set_ylim(-0.55, 1.55)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Rate (%)")
    ax.grid(axis="x", color=GRID, lw=0.48)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=4)
    ax.legend(handles=[Line2D([0], [0], marker="o", color="none", mfc=PAPER, mec=INK, ms=4.4, label="Stable"),
                       Line2D([0], [0], marker="s", color="none", mfc=INK, mec=INK, ms=4.4, label="Changed")],
              frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(0, 1.16), handletextpad=0.25, columnspacing=0.8)


def compose_figure5(upper_path: Path, lower_fn, lower_name: str, output: Path) -> None:
    with Image.open(upper_path).convert("RGB") as source:
        upper = source.crop((0, 0, source.width, 545))
    configure()
    lower_fig, lower_ax = plt.subplots(figsize=(3.35, 1.48))
    lower_fn(lower_ax, sqlite_rates(load_sqlite()))
    lower_fig.subplots_adjust(left=0.17, right=0.96, top=0.78, bottom=0.24)
    lower_fig.savefig("/private/tmp/tri-figure5-lower.png", dpi=360, facecolor=PAPER)
    plt.close(lower_fig)
    with Image.open("/private/tmp/tri-figure5-lower.png").convert("RGB") as lower:
        lower = lower.resize((upper.width, 530), Image.Resampling.LANCZOS)
        combined = Image.new("RGB", (upper.width, upper.height + lower.height), PAPER)
        combined.paste(upper, (0, 0))
        combined.paste(lower, (0, upper.height))
        output.parent.mkdir(parents=True, exist_ok=True)
        combined.save(output, dpi=(220, 220), optimize=True)


def figure6_data() -> tuple[list[dict], list[dict]]:
    convention = fig6._load(fig6.DEFAULT_CONVENTION)
    matched = fig6._load(fig6.DEFAULT_MATCHED)
    return fig6._ordered(fig6._convention_rows(convention)), fig6._ordered(fig6._matched_rows(matched))


MODEL_COLORS = [TEAL, EMBER, LEAF, PLUM]
MODEL_LABELS = ["Qwen", "GLM", "DeepSeek", "MiniMax"]
MODEL_MARKERS = ["o", "s", "D", "^"]


def figure6_grouped_bars(convention: list[dict], matched: list[dict], output: Path) -> None:
    """Option 6A: two side-by-side grouped bar panels."""
    configure()
    fig, axes = plt.subplots(1, 2, figsize=(6.7, 2.65), sharey=True, gridspec_kw={"wspace": 0.10})
    for ax, title, rows in zip(axes, ["A  Convention told", "B  Decision visible"], [convention, matched], strict=True):
        values = [row["value"] for row in rows]
        lows = [row["low"] for row in rows]
        highs = [row["high"] for row in rows]
        x = np.arange(4)
        ax.bar(x, values, width=0.58, color=MODEL_COLORS, alpha=0.86, edgecolor=MODEL_COLORS, linewidth=0.7, zorder=2)
        ax.errorbar(x, values, yerr=[np.array(values) - np.array(lows), np.array(highs) - np.array(values)],
                    fmt="none", ecolor=INK, elinewidth=0.75, capsize=2.0, capthick=0.7, zorder=3)
        for xx, value in zip(x, values, strict=True):
            ax.text(xx, value + 4, f"{value:+.1f}", ha="center", va="bottom", fontsize=6.6, color=INK)
        ax.axhline(0, color=INK, lw=0.7)
        ax.set_title(title, loc="left", pad=3, weight="bold")
        ax.set_xticks(x, MODEL_LABELS)
        ax.set_ylim(-25, 90)
        ax.set_yticks([-20, 0, 20, 40, 60, 80])
        ax.grid(axis="y", color=GRID, lw=0.45)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Change in changed-pair accuracy (pp)")
    fig.text(0.5, 0.02, "Separate matched audits; cluster-bootstrap 95% CIs", ha="center", fontsize=6.7, color=MUTED)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.22)
    save_figure(fig, output)


def figure6_banded_bars(convention: list[dict], matched: list[dict], output: Path) -> None:
    """Option 6B: horizontal effect bands with direct labels."""
    configure()
    fig, axes = plt.subplots(1, 2, figsize=(6.7, 2.55), sharey=True, gridspec_kw={"wspace": 0.08})
    for ax, title, rows in zip(axes, ["A  Convention told", "B  Decision visible"], [convention, matched], strict=True):
        y = np.arange(4)[::-1]
        values = np.array([row["value"] for row in rows])
        lows = np.array([row["low"] for row in rows])
        highs = np.array([row["high"] for row in rows])
        for yy, value, low, high, color, label in zip(y, values, lows, highs, MODEL_COLORS, MODEL_LABELS, strict=True):
            ax.barh(yy, value, height=0.42, color=color, alpha=0.86, edgecolor=color, linewidth=0.7, zorder=2)
            ax.errorbar(value, yy, xerr=[[value - low], [high - value]], fmt="none", ecolor=INK, elinewidth=0.75, capsize=2.0, zorder=3)
            ax.text(max(value + 3, 3), yy, f"{value:+.1f}", va="center", ha="left", fontsize=6.7, color=INK)
        ax.axvline(0, color=INK, lw=0.7)
        ax.set_title(title, loc="left", pad=3, weight="bold")
        ax.set_yticks(y, MODEL_LABELS)
        ax.set_xlim(-25, 90)
        ax.set_xticks([-20, 0, 20, 40, 60, 80])
        ax.grid(axis="x", color=GRID, lw=0.45)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=3)
    axes[0].set_xlabel("Effect (pp)")
    axes[1].set_xlabel("Effect (pp)")
    fig.text(0.5, 0.02, "Separate inventories; bars show point estimates and CI caps", ha="center", fontsize=6.7, color=MUTED)
    fig.subplots_adjust(left=0.13, right=0.99, top=0.86, bottom=0.22)
    save_figure(fig, output)


def figure6_matrix(convention: list[dict], matched: list[dict], output: Path) -> None:
    """Option 6C: compact two-column estimate matrix with CI whiskers."""
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 2.85))
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.65, 3.65)
    ax.axvline(0.5, color=GRID, lw=0.75)
    ax.axhline(-0.5, color=GRID, lw=0.6)
    for col, rows, heading in [(0, convention, "Convention"), (1, matched, "Decision-visible")]:
        ax.text(col, 3.45, heading, ha="center", va="bottom", fontsize=7.3, weight="bold", color=INK)
        for row_index, (row, color, marker) in enumerate(zip(rows, MODEL_COLORS, MODEL_MARKERS, strict=True)):
            value, low, high = row["value"], row["low"], row["high"]
            yy = 2.8 - row_index * 0.85
            ax.errorbar(col, yy, yerr=[[value - low], [high - value]], fmt=marker, ms=4.7, mfc=color, mec=color,
                        ecolor=color, elinewidth=1.0, capsize=2.0, capthick=0.7, zorder=3)
            ax.text(col + 0.14, yy, f"{value:+.1f}", ha="left", va="center", fontsize=6.5, color=INK)
    ax.set_xticks([0, 1], ["Convention told", "Decision visible"])
    ax.set_yticks([2.8, 1.95, 1.10, 0.25], MODEL_LABELS)
    ax.set_ylabel("Change in changed-pair accuracy (pp)")
    ax.grid(axis="y", color=GRID, lw=0.45)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=3)
    ax.legend(handles=[Line2D([0], [0], marker=m, color="none", mfc=c, mec=c, ms=4.2, label=l) for m, c, l in zip(MODEL_MARKERS, MODEL_COLORS, MODEL_LABELS, strict=True)],
              frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.17), handletextpad=0.2, columnspacing=0.65)
    fig.subplots_adjust(left=0.25, right=0.99, top=0.79, bottom=0.19)
    save_figure(fig, output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--upper-figure5", type=Path, default=Path("/private/tmp/tri-round16-forest/fig4_sqlite_outcome_tree.png"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fig5_dir = args.output_dir / "figure5"
    compose_figure5(args.upper_figure5, lower_endpoint_strips, "A", fig5_dir / "figure5_lower_option_a_endpoint_strips.png")
    compose_figure5(args.upper_figure5, lower_grouped_bars, "B", fig5_dir / "figure5_lower_option_b_grouped_bars.png")
    compose_figure5(args.upper_figure5, lower_endpoint_tracks, "C", fig5_dir / "figure5_lower_option_c_endpoint_tracks.png")
    convention, matched = figure6_data()
    fig6_dir = args.output_dir / "figure6"
    figure6_grouped_bars(convention, matched, fig6_dir / "figure6_option_a_grouped_bars")
    figure6_banded_bars(convention, matched, fig6_dir / "figure6_option_b_horizontal_bands")
    figure6_matrix(convention, matched, fig6_dir / "figure6_option_c_matrix")
    print(f"Figure 5 previews: {fig5_dir}")
    print(f"Figure 6 previews: {fig6_dir}")


if __name__ == "__main__":
    main()
