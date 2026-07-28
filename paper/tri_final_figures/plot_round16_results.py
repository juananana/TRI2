from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "summary_csv"

# Round-16 coordinated result-figure contract.
INK = "#264A56"
MUTED = "#5F6B70"
OUTLINE = "#70807D"
GRID = "#D6E0DE"
PAPER = "#FFFFFF"

QWEN_LINE = "#407A7F"
QWEN_FILL = "#B8D0CD"
QWEN_TEXT = "#315F63"
GLM_LINE = "#E56D4E"
GLM_FILL = "#F2B09D"
GLM_TEXT = "#A94F39"
DEEPSEEK_LINE = "#60AA84"
DEEPSEEK_FILL = "#B8D8C6"
DEEPSEEK_TEXT = "#3F7B5C"

CORRECT = "#C8DAD9"
TRI_WRITE = "#E56D4E"
FALLBACK = "#F3C6B8"
REJECT = "#D8D4CF"
STABLE_BAND = "#E8F1ED"

TICK_SIZE = 7.2
AXIS_LABEL_SIZE = 7.6
PANEL_TITLE_SIZE = 8.2
ANNOTATION_SIZE = 7.2

MODEL_COLOR = {
    "Qwen3.5": QWEN_LINE,
    "GLM-5.1": GLM_LINE,
    "DeepSeek": DEEPSEEK_LINE,
}
MODEL_FILL = {
    "Qwen3.5": QWEN_FILL,
    "GLM-5.1": GLM_FILL,
    "DeepSeek": DEEPSEEK_FILL,
}
MODEL_TEXT = {
    "Qwen3.5": QWEN_TEXT,
    "GLM-5.1": GLM_TEXT,
    "DeepSeek": DEEPSEEK_TEXT,
}
MODEL_MARKER = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}
MODEL_SHORT = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM", "DeepSeek": "DeepSeek"}


def style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": AXIS_LABEL_SIZE,
            "axes.labelsize": AXIS_LABEL_SIZE,
            "axes.titlesize": PANEL_TITLE_SIZE,
            "xtick.labelsize": TICK_SIZE,
            "ytick.labelsize": TICK_SIZE,
            "legend.fontsize": TICK_SIZE,
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.0,
            "hatch.linewidth": 0.26,
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


def read_rows(filename: str) -> list[dict[str, str]]:
    with (DATA / filename).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find(items: list[dict[str, str]], **where: str) -> dict[str, str]:
    matches = [row for row in items if all(row.get(key) == value for key, value in where.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {where}, found {len(matches)}")
    return matches[0]


def wilson(k: int, n: int) -> tuple[float, float, float]:
    if n <= 0:
        raise ValueError(f"Wilson interval requires positive n, got {n}")
    z = 1.959963984540054
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return 100 * p, 100 * max(0, center - half), 100 * min(1, center + half)


def save(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    metadata = {"Creator": "TRI round-16 result figure generator"}
    fig.savefig(stem.with_suffix(".pdf"), metadata=metadata)
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=360)
    plt.close(fig)


def clean_axis(ax: plt.Axes, *, grid_axis: str | None = None) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, lw=0.42, alpha=0.72, zorder=0)
        ax.set_axisbelow(True)
    ax.tick_params(axis="both", labelsize=TICK_SIZE)
    for label in (*ax.get_xticklabels(), *ax.get_yticklabels()):
        label.set_fontweight("normal")


def build_cross_schema(rows: list[dict[str, str]], stem: Path) -> None:
    style()
    fig = plt.figure(figsize=(3.35, 3.45))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.52, 1.0], hspace=0.42)
    top = fig.add_subplot(gs[0])
    bottom = fig.add_subplot(gs[1])

    models = ["Qwen3.5", "GLM-5.1", "DeepSeek"]
    offsets = [-0.070, 0.0, 0.070]
    label_y_offsets = {"Qwen3.5": -1.0, "GLM-5.1": 0.0, "DeepSeek": 1.0}
    for model, offset in zip(models, offsets):
        generic = find(rows, model=model, controller="Generic")
        cta = find(rows, model=model, controller="CTA")
        n = int(generic["shared_eligible"])
        if int(cta["shared_eligible"]) != n:
            raise ValueError(f"Shared-eligible denominator mismatch for {model}")
        gk, ck = int(generic["substitutions"]), int(cta["substitutions"])
        gr, gl, gh = wilson(gk, n)
        cr, cl, ch = wilson(ck, n)
        color, fill, marker = MODEL_COLOR[model], MODEL_FILL[model], MODEL_MARKER[model]
        x0, x1 = offset, 1 + offset
        top.plot([x0, x1], [gr, cr], color=color, lw=1.2, zorder=2)
        top.errorbar(
            x0,
            gr,
            yerr=[[max(0.0, gr - gl)], [max(0.0, gh - gr)]],
            fmt=marker,
            ms=5.0,
            mfc=PAPER,
            mec=color,
            mew=0.95,
            ecolor=color,
            capsize=2.0,
            elinewidth=0.76,
            zorder=3,
        )
        top.errorbar(
            x1,
            cr,
            yerr=[[max(0.0, cr - cl)], [max(0.0, ch - cr)]],
            fmt=marker,
            ms=5.0,
            mfc=fill,
            mec=color,
            mew=0.95,
            ecolor=color,
            capsize=2.0,
            elinewidth=0.76,
            zorder=3,
        )
        top.text(
            -0.48,
            gr + label_y_offsets[model],
            MODEL_SHORT[model],
            ha="left",
            va="center",
            fontsize=ANNOTATION_SIZE,
            color=MODEL_TEXT[model],
            weight="normal",
            bbox={"facecolor": PAPER, "edgecolor": "none", "alpha": 0.92, "pad": 0.15},
        )

    top.set(xlim=(-0.52, 1.25), ylim=(-2, 101), ylabel="Conditional substitution (%)")
    top.set_xticks([0, 1], ["Generic", "CTA"])
    top.set_yticks([0, 25, 50, 75, 100])
    top.set_title("A  Substitution after correct binding", loc="left", pad=2, weight="bold")
    top.tick_params(axis="x", length=0, pad=3)
    top.tick_params(axis="y", length=3, width=0.65)
    clean_axis(top, grid_axis="y")

    y_positions = [2, 1, 0]
    y_labels: list[str] = []
    for model, y in zip(models, y_positions):
        generic = find(rows, model=model, controller="Generic")
        cta = find(rows, model=model, controller="CTA")
        gx, cx = float(generic["pairacc_pct"]), float(cta["pairacc_pct"])
        gl, gh = float(generic["pairacc_ci95_low_pct"]), float(generic["pairacc_ci95_high_pct"])
        cl, ch = float(cta["pairacc_ci95_low_pct"]), float(cta["pairacc_ci95_high_pct"])
        color, fill, marker = MODEL_COLOR[model], MODEL_FILL[model], MODEL_MARKER[model]
        bottom.plot([gx, cx], [y, y], color=color, lw=1.2, zorder=1)
        bottom.errorbar(
            gx,
            y,
            xerr=[[gx - gl], [gh - gx]],
            fmt=marker,
            ms=4.8,
            mfc=PAPER,
            mec=color,
            mew=0.9,
            ecolor=color,
            capsize=1.8,
            elinewidth=0.78,
            zorder=3,
        )
        bottom.errorbar(
            cx,
            y,
            xerr=[[cx - cl], [ch - cx]],
            fmt=marker,
            ms=4.8,
            mfc=fill,
            mec=color,
            mew=0.9,
            ecolor=color,
            capsize=1.8,
            elinewidth=0.78,
            zorder=3,
        )
        y_labels.append(
            f"{MODEL_SHORT[model]}\n{generic['pairacc_both_correct']}→{cta['pairacc_both_correct']}/80"
        )

    bottom.set(xlim=(-2, 103), ylim=(-0.55, 2.55), xlabel="PairAcc (%)")
    bottom.set_yticks(y_positions, y_labels, fontsize=7.0)
    bottom.set_xticks([0, 25, 50, 75, 100])
    bottom.set_title("B  Pair accuracy", loc="left", pad=2, weight="bold")
    bottom.tick_params(axis="y", length=0, pad=4)
    bottom.tick_params(axis="x", length=3, width=0.65)
    clean_axis(bottom, grid_axis="x")
    for label, model in zip(bottom.get_yticklabels(), models):
        label.set_color(MODEL_TEXT[model])
        label.set_fontweight("normal")
        label.set_linespacing(0.88)
    legend = [
        Line2D([0], [0], marker="o", color=MUTED, mfc=PAPER, mec=MUTED, ms=4.2, label="Generic"),
        Line2D([0], [0], marker="o", color=MUTED, mfc="#C8C5CE", mec=MUTED, ms=4.2, label="CTA"),
    ]
    bottom.legend(
        handles=legend,
        frameon=False,
        ncol=2,
        loc="upper right",
        bbox_to_anchor=(1.01, 1.20),
        handletextpad=0.25,
        columnspacing=0.7,
        fontsize=7.0,
    )

    fig.subplots_adjust(left=0.25, right=0.985, top=0.94, bottom=0.11)
    save(fig, stem)


def build_sqlite_outcomes(rows: list[dict[str, str]], stem: Path) -> None:
    style()
    for row in rows:
        total = sum(
            int(row[key])
            for key in (
                "correct_final_state",
                "core_tri_write",
                "fallback_wrong_write",
                "unneeded_reject",
            )
        )
        if total != int(row["tasks"]) or total != 40:
            raise ValueError(f"Outcome counts do not sum to 40: {row}")

    fig = plt.figure(figsize=(3.35, 2.95))
    grid = fig.add_gridspec(2, 1, height_ratios=[1.25, 1.0], hspace=0.46)
    outcome_ax = fig.add_subplot(grid[0])
    opportunity_ax = fig.add_subplot(grid[1])

    categories = [
        ("correct_final_state", "Correct", CORRECT, None, INK),
        ("core_tri_write", "TRI write", TRI_WRITE, "///", PAPER),
        ("fallback_wrong_write", "Fallback", FALLBACK, "--", INK),
        ("unneeded_reject", "Reject", REJECT, "\\\\", INK),
    ]
    y_positions = {"Qwen3.5": 1.0, "GLM-5.1": 0.0}
    bar_height = 0.42

    for model in ("Qwen3.5", "GLM-5.1"):
        row = find(rows, model=model, controller="Generic")
        cursor = 0
        y = y_positions[model]
        for key, _, color, hatch, label_color in categories:
            value = int(row[key])
            if value == 0:
                continue
            outcome_ax.add_patch(
                Rectangle(
                    (cursor, y - bar_height / 2),
                    value,
                    bar_height,
                    facecolor=color,
                    edgecolor=OUTLINE,
                    linewidth=0.38,
                    hatch=hatch,
                    zorder=2,
                )
            )
            outcome_ax.text(
                cursor + value / 2,
                y,
                str(value),
                ha="center",
                va="center",
                color=label_color,
                fontsize=ANNOTATION_SIZE,
                weight="bold",
                zorder=3,
            )
            cursor += value

    outcome_ax.set_xlim(0, 40)
    outcome_ax.set_ylim(-0.55, 1.90)
    outcome_ax.set_yticks([1.0, 0.0], ["Qwen", "GLM"])
    outcome_ax.set_xticks([0, 10, 20, 30, 40])
    outcome_ax.set_title("A  Outcomes (40 tasks per model)", loc="left", pad=2, weight="bold")
    outcome_ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    outcome_ax.set_axisbelow(True)
    outcome_ax.spines[["top", "right", "left"]].set_visible(False)
    outcome_ax.tick_params(axis="y", length=0, pad=5)
    outcome_ax.legend(
        handles=[
            Patch(facecolor=color, edgecolor=OUTLINE, linewidth=0.45, hatch=hatch, label=label)
            for _, label, color, hatch, _ in categories
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.955),
        ncol=4,
        frameon=False,
        fontsize=TICK_SIZE,
        handlelength=1.0,
        handleheight=0.65,
        handletextpad=0.25,
        columnspacing=0.55,
    )

    opportunity_ax.axhspan(0, 6, color=STABLE_BAND, alpha=0.70, zorder=0)
    offsets = {"Qwen3.5": -0.045, "GLM-5.1": 0.045}
    for model in ("Qwen3.5", "GLM-5.1"):
        row = find(rows, model=model, controller="Generic")
        stable_k, stable_n = int(row["stable_writes"]), int(row["stable_opportunities"])
        changed_k, changed_n = int(row["strict_core_writes"]), int(row["strict_core_opportunities"])
        sr, sl, sh = wilson(stable_k, stable_n)
        cr, cl, ch = wilson(changed_k, changed_n)
        color, fill, marker = MODEL_COLOR[model], MODEL_FILL[model], MODEL_MARKER[model]
        x0, x1 = offsets[model], 1 + offsets[model]
        opportunity_ax.plot([x0, x1], [sr, cr], color=color, lw=1.2, zorder=2)
        opportunity_ax.errorbar(
            x0,
            sr,
            yerr=[[max(0.0, sr - sl)], [max(0.0, sh - sr)]],
            fmt=marker,
            ms=4.8,
            mfc=PAPER,
            mec=color,
            mew=0.95,
            ecolor=color,
            elinewidth=0.85,
            capsize=2.0,
            zorder=3,
        )
        opportunity_ax.errorbar(
            x1,
            cr,
            yerr=[[max(0.0, cr - cl)], [max(0.0, ch - cr)]],
            fmt=marker,
            ms=4.8,
            mfc=fill,
            mec=color,
            mew=0.90,
            ecolor=color,
            elinewidth=0.85,
            capsize=2.0,
            zorder=3,
        )
        opportunity_ax.text(
            1.08,
            cr,
            f"{MODEL_SHORT[model]} {changed_k}/{changed_n}",
            ha="left",
            va="center",
            fontsize=ANNOTATION_SIZE,
            color=MODEL_TEXT[model],
            weight="bold",
        )

    opportunity_ax.text(
        -0.10,
        10.0,
        "both 0/4",
        ha="right",
        va="bottom",
        fontsize=ANNOTATION_SIZE,
        color=MUTED,
        weight="normal",
    )
    opportunity_ax.set_xlim(-0.24, 1.48)
    opportunity_ax.set_ylim(-4, 112)
    opportunity_ax.set_xticks([0, 1], ["Stable", "Changed"])
    opportunity_ax.set_yticks([0, 50, 100])
    opportunity_ax.set_ylabel("Rate (%)")
    opportunity_ax.set_title("B  Writes to the wrong target", loc="left", pad=2, weight="bold")
    opportunity_ax.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    opportunity_ax.set_axisbelow(True)
    opportunity_ax.spines[["top", "right", "bottom"]].set_visible(False)
    opportunity_ax.tick_params(axis="x", length=0, pad=4)

    for ax in (outcome_ax, opportunity_ax):
        ax.tick_params(axis="both", labelsize=TICK_SIZE)
        for label in (*ax.get_xticklabels(), *ax.get_yticklabels()):
            label.set_fontweight("normal")
    for label, model in zip(outcome_ax.get_yticklabels(), ("Qwen3.5", "GLM-5.1")):
        label.set_color(MODEL_TEXT[model])
        label.set_fontweight("normal")
        label.set_fontsize(7.0)

    fig.subplots_adjust(left=0.17, right=0.955, top=0.96, bottom=0.13)
    save(fig, stem)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate coordinated round-16 TRI result figures.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "round16_result_polish" / "cycle1",
    )
    args = parser.parse_args()

    cross_schema = read_rows("v7_shared_eligible_pairacc_and_substitution.csv")
    sqlite = read_rows("sqlite_model_facing_outcomes.csv")
    build_cross_schema(cross_schema, args.output_dir / "fig3_substitution_flow")
    build_sqlite_outcomes(sqlite, args.output_dir / "fig4_sqlite_outcome_tree")


if __name__ == "__main__":
    main()
