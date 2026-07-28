#!/usr/bin/env python3
"""Fresh structural candidates for Figure 5's execution-consequence panel.

The upper outcome accounting is preserved as-is.  These lower-panel options
encode the same frozen SQLite counts with distinct visual grammars:
capsule lanes, alluvial pathways, and compact proportion rings.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, FancyBboxPatch, Wedge

import plot_round16_results as fig5


ROOT = Path(__file__).resolve().parent
PAPER = "#FFFFFF"
INK = "#264A56"
MUTED = "#5F6B70"
GRID = "#D6E0DE"
TEAL = "#407A7F"
EMBER = "#E56D4E"
LEAF = "#60AA84"
NEUTRAL = "#D8D4CF"
PALE = "#F2F1EF"


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.labelsize": 7.5,
            "axes.titlesize": 8.2,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
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
    fig.savefig(stem.with_suffix(".pdf"), metadata={"Creator": "TRI Figure 5 structural candidates"})
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=400)
    plt.close(fig)


def load_data() -> list[dict[str, str]]:
    rows = fig5.read_rows("sqlite_model_facing_outcomes.csv")
    out = []
    for model in ("Qwen3.5", "GLM-5.1"):
        row = fig5.find(rows, model=model, controller="Generic")
        stable_n = int(row["stable_opportunities"])
        changed_n = int(row["strict_core_opportunities"])
        stable_k = int(row["stable_writes"])
        changed_k = int(row["strict_core_writes"])
        if (stable_n, changed_n) != (4, 8):
            raise ValueError(f"Unexpected frozen denominators for {model}: {stable_n}, {changed_n}")
        out.append(
            {
                "model": "Qwen" if model == "Qwen3.5" else "GLM",
                "color": TEAL if model == "Qwen3.5" else EMBER,
                "stable_k": stable_k,
                "stable_n": stable_n,
                "changed_k": changed_k,
                "changed_n": changed_n,
            }
        )
    return out


def panel_title(ax: plt.Axes, text: str) -> None:
    ax.set_title(text, loc="left", pad=3, weight="bold")
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.tick_params(length=0)


def draw_capsule_lanes(data: list[dict[str, str | int]]) -> plt.Figure:
    """Option A: each eligible opportunity is a rounded capsule."""
    configure()
    fig, ax = plt.subplots(figsize=(3.35, 1.62))
    ax.set_xlim(-0.90, 15.10)
    ax.set_ylim(-0.42, 2.05)
    group_x = {"Stable": np.arange(0, 4), "Changed": np.arange(5, 13)}
    for y, row in zip([1.35, 0.35], data, strict=True):
        for state, xs in group_x.items():
            n = len(xs)
            k = int(row[f"{state.lower()}_k"])
            for i, x in enumerate(xs):
                wrong = i < k
                patch = FancyBboxPatch(
                    (x - 0.19, y - 0.18), 0.38, 0.36,
                    boxstyle="round,pad=0.02,rounding_size=0.10",
                    facecolor=EMBER if wrong else (TEAL if state == "Changed" else PALE),
                    edgecolor=EMBER if wrong else (TEAL if state == "Changed" else MUTED),
                    linewidth=0.65,
                )
                ax.add_patch(patch)
            rate = 100 * k / n
            if state == "Changed":
                ax.text(14.05, y, f"{k}/{n}\n{rate:.0f}%", ha="center", va="center", color=INK, fontsize=6.7, linespacing=0.86, weight="bold" if k else "normal")
        ax.text(-0.46, y, str(row["model"]), ha="right", va="center", color=row["color"], fontsize=7.5, weight="bold")
    ax.text(1.5, 1.84, "Stable", ha="center", va="bottom", color=MUTED, fontsize=7.0, weight="bold")
    ax.text(8.5, 1.84, "Changed winner", ha="center", va="bottom", color=MUTED, fontsize=7.0, weight="bold")
    ax.plot([4.5, 4.5], [-0.22, 1.82], color=GRID, lw=0.8)
    ax.text(6.2, -0.27, "Each capsule = one eligible write opportunity", ha="center", va="top", color=MUTED, fontsize=6.6)
    fig.legend(
        handles=[
            FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02,rounding_size=0.1", facecolor=EMBER, edgecolor=EMBER, label="wrong target"),
            FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02,rounding_size=0.1", facecolor=PALE, edgecolor=MUTED, label="no wrong write"),
        ], loc="upper right", bbox_to_anchor=(0.985, 0.935), frameon=False, ncol=2, fontsize=6.4, handlelength=0.9, handleheight=0.65, columnspacing=0.6,
    )
    panel_title(ax, "")
    fig.text(0.02, 0.965, "B  Executed wrong-target writes", ha="left", va="top", fontsize=8.2, weight="bold", color=INK)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.subplots_adjust(left=0.16, right=0.985, top=0.69, bottom=0.15)
    return fig


def ribbon(ax: plt.Axes, x0: float, x1: float, y0: float, y1: float, width: float, color: str, alpha: float = 0.72) -> None:
    verts = [
        (x0, y0 + width / 2), (x0 + 0.30, y0 + width / 2), (x1 - 0.30, y1 + width / 2), (x1, y1 + width / 2),
        (x1, y1 - width / 2), (x1 - 0.30, y1 - width / 2), (x0 + 0.30, y0 - width / 2), (x0, y0 - width / 2), (x0, y0 + width / 2),
    ]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4, MplPath.LINETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4, MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color, edgecolor="none", alpha=alpha))


def draw_alluvial(data: list[dict[str, str | int]]) -> plt.Figure:
    """Option B: source-state to execution-outcome pathways."""
    configure()
    fig, axes = plt.subplots(2, 1, figsize=(3.35, 1.86), sharex=True)
    for ax, row in zip(axes, data, strict=True):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        stable_n, changed_n = int(row["stable_n"]), int(row["changed_n"])
        stable_k, changed_k = int(row["stable_k"]), int(row["changed_k"])
        # Left nodes: stable and changed. Right nodes: no wrong write / wrong target.
        ax.add_patch(FancyBboxPatch((0.15, 6.2), 1.25, 1.45, boxstyle="round,pad=0.04,rounding_size=0.15", facecolor=PALE, edgecolor=MUTED, lw=0.7))
        ax.add_patch(FancyBboxPatch((0.15, 2.25), 1.25, 2.85, boxstyle="round,pad=0.04,rounding_size=0.15", facecolor="#EAF2F0", edgecolor=TEAL, lw=0.7))
        ax.add_patch(FancyBboxPatch((8.35, 5.95), 1.35, 2.15, boxstyle="round,pad=0.04,rounding_size=0.15", facecolor="#EAF2F0", edgecolor=TEAL, lw=0.7))
        ax.add_patch(FancyBboxPatch((8.35, 2.25), 1.35, 2.85, boxstyle="round,pad=0.04,rounding_size=0.15", facecolor="#FBE6DF", edgecolor=EMBER, lw=0.7))
        # Flow widths are proportional to counts; stable always safe.
        ribbon(ax, 1.4, 8.35, 6.92, 7.02, 1.02, TEAL, 0.35)
        changed_safe = changed_n - changed_k
        if changed_safe:
            ribbon(ax, 1.4, 8.35, 4.18, 6.62, 1.72 * changed_safe / changed_n, TEAL, 0.42)
        if changed_k:
            ribbon(ax, 1.4, 8.35, 3.38, 3.68, 1.72 * changed_k / changed_n, EMBER, 0.82)
        ax.text(0.78, 6.92, f"Stable\n{stable_n}", ha="center", va="center", fontsize=6.8, color=INK, weight="bold")
        ax.text(0.78, 3.68, f"Changed\n{changed_n}", ha="center", va="center", fontsize=6.8, color=INK, weight="bold")
        safe = stable_n + changed_safe
        ax.text(9.02, 7.02, f"Safe\n{safe}", ha="center", va="center", fontsize=6.7, color=INK, weight="bold")
        ax.text(9.02, 3.68, f"Wrong\n{changed_k}", ha="center", va="center", fontsize=6.7, color=INK, weight="bold")
        ax.text(4.95, 8.55, f"{row['model']}  |  {changed_k}/{changed_n} changed writes", ha="center", va="bottom", fontsize=7.1, color=row["color"], weight="bold")
        ax.axis("off")
    fig.text(0.02, 0.975, "B  Winner state → executed consequence", ha="left", va="top", fontsize=8.2, color=INK, weight="bold")
    fig.text(0.04, 0.885, "winner state", ha="left", va="top", fontsize=6.5, color=MUTED)
    fig.text(0.82, 0.885, "execution", ha="left", va="top", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.82, bottom=0.02, hspace=0.15)
    return fig


def draw_rings(data: list[dict[str, str | int]]) -> plt.Figure:
    """Option C: four compact proportion rings, with count-first labels."""
    configure()
    fig, axes = plt.subplots(1, 4, figsize=(3.35, 1.52))
    specs = [(0, "Qwen", "Stable"), (1, "Qwen", "Changed"), (2, "GLM", "Stable"), (3, "GLM", "Changed")]
    row_by_model = {str(row["model"]): row for row in data}
    for ax, (_, model, state) in zip(axes, specs, strict=True):
        row = row_by_model[model]
        k, n = int(row[f"{state.lower()}_k"]), int(row[f"{state.lower()}_n"])
        frac = k / n
        ax.add_patch(Wedge((0, 0), 1.0, 0, 360, width=0.22, facecolor=PALE, edgecolor="none"))
        if frac:
            ax.add_patch(Wedge((0, 0), 1.0, 90, 90 - 360 * frac, width=0.22, facecolor=EMBER, edgecolor="none"))
        ax.text(0, 0.06, f"{k}/{n}", ha="center", va="center", fontsize=9.0, weight="bold", color=INK)
        ax.text(0, -0.23, f"{100 * frac:.0f}%", ha="center", va="top", fontsize=6.6, color=MUTED)
        ax.set_title(state, fontsize=6.8, pad=2, color=MUTED, weight="bold")
        ax.set_xlim(-1.18, 1.18); ax.set_ylim(-1.18, 1.18); ax.axis("off")
    fig.text(0.5, 0.025, "Filled arc = wrong-target share among eligible writes", ha="center", va="bottom", fontsize=6.6, color=MUTED)
    fig.text(0.02, 0.975, "B  Risk profile by winner state", ha="left", va="top", fontsize=8.2, color=INK, weight="bold")
    fig.text(0.26, 0.82, "Qwen", ha="center", va="center", fontsize=7.4, color=TEAL, weight="bold")
    fig.text(0.74, 0.82, "GLM", ha="center", va="center", fontsize=7.4, color=EMBER, weight="bold")
    fig.subplots_adjust(left=0.03, right=0.97, top=0.67, bottom=0.18, wspace=0.08)
    return fig


def compose(upper_path: Path, lower_fig_fn, stem: Path) -> None:
    # Keep the approved upper panel untouched and place a newly rendered lower panel beneath it.
    from PIL import Image
    with Image.open(upper_path).convert("RGB") as source:
        upper = source.crop((0, 0, source.width, 545))
    lower_fig = lower_fig_fn(load_data())
    tmp = Path("/private/tmp/tri-figure5-reconcept-lower.png")
    lower_fig.savefig(tmp, dpi=400, facecolor=PAPER)
    plt.close(lower_fig)
    with Image.open(tmp).convert("RGB") as lower:
        target_height = round(lower.height * upper.width / lower.width)
        lower = lower.resize((upper.width, target_height), Image.Resampling.LANCZOS)
        combined = Image.new("RGB", (upper.width, upper.height + lower.height), PAPER)
        combined.paste(upper, (0, 0)); combined.paste(lower, (0, upper.height))
        stem.parent.mkdir(parents=True, exist_ok=True)
        combined.save(stem.with_suffix(".png"), dpi=(220, 220), optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "figure5_reconceptualized_v1")
    parser.add_argument("--upper-figure5", type=Path, default=Path("/private/tmp/tri-round16-forest/fig4_sqlite_outcome_tree.png"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    compose(args.upper_figure5, draw_capsule_lanes, args.output_dir / "figure5_option_a_capsule_lanes")
    compose(args.upper_figure5, draw_alluvial, args.output_dir / "figure5_option_b_alluvial")
    compose(args.upper_figure5, draw_rings, args.output_dir / "figure5_option_c_proportion_rings")
    print(args.output_dir)


if __name__ == "__main__":
    main()
