#!/usr/bin/env python3
"""
Demo redraw: ONE figure, two panels (not a four-panel composite).
Panel A: policy-identifiability truth table, redrawn as a filled matrix
         (no overlapping callout text; single arrow annotation instead).
Panel B: actionable-core accuracy, same numbers as the current paper figure,
         with model color decoupled from the pass/fail semantic color so
         teal is reserved for "supports construct / correct" everywhere.

Data is unchanged from the current tri_core_diagnostic.pdf panels A and C
(paper/AnonymousSubmission2027.tex lines ~416-420, ~445-449).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# ---- unified semantic palette --------------------------------------------
# Validated with the dataviz skill's validate_palette.js (OKLab CVD + contrast
# checks); see chat for the pass/fail report. Two roles, never mixed:
#   status pair  -> pass/fail, supports-construct/error (reused across figures)
#   categorical  -> model identity (Qwen/GLM), never reused for status
INK = "#17212B"
MUTED = "#5B6570"
LINE = "#CBD2D9"
PASS_TEAL = "#0B8A72"     # status: pass / supports construct / correct
FAIL_ORANGE = "#C1592E"   # status: fail / error / risk
QWEN_BLUE = "#2A78D6"     # categorical slot 1: model identity only
GLM_GOLD = "#EDA100"      # categorical slot 4: model identity only

plt.rcParams["font.family"] = "Helvetica"
plt.rcParams["font.size"] = 8
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42


def panel_a_identifiability(ax):
    ax.set_title("A  Policy identifiability", fontsize=10, weight="bold", loc="left")
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    rows = ["Stable only", "Preserve only", "Reevaluate only", "Changed-winner\nPairAcc"]
    lock = [True, True, False, False]
    reeval = [True, False, True, False]

    col_x = {"Lock": 5.4, "Reeval": 7.6}
    cell_w, cell_h = 1.7, 1.05
    row_label_x = 0.2
    top_y = 8.3
    row_gap = 1.85

    ax.text(col_x["Lock"], top_y + 0.95, "Lock", fontsize=8.5, weight="bold", ha="center")
    ax.text(col_x["Reeval"], top_y + 0.95, "Reeval", fontsize=8.5, weight="bold", ha="center")

    row_ys = [top_y - i * row_gap for i in range(4)]
    for i, (label, ys) in enumerate(zip(rows, row_ys)):
        ax.text(row_label_x, ys, label, fontsize=8, va="center", ha="left",
                weight="bold" if i == 3 else "normal", color=INK)
        for col, ok in (("Lock", lock[i]), ("Reeval", reeval[i])):
            cx = col_x[col]
            color = PASS_TEAL if ok else FAIL_ORANGE
            ax.add_patch(FancyBboxPatch(
                (cx - cell_w / 2, ys - cell_h / 2), cell_w, cell_h,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=color, edgecolor="none"))
            ax.text(cx, ys, "pass" if ok else "fail", fontsize=8, ha="center", va="center",
                     color="white", weight="bold")

    # single arrow annotation, offset below the table -- no overlap with row 4
    last_y = row_ys[-1]
    ax.annotate(
        "Only the changed-winner metric\nrejects both unconditional policies",
        xy=(col_x["Reeval"] + cell_w / 2, last_y), xytext=(9.7, last_y - 1.9),
        fontsize=7.3, color=FAIL_ORANGE, ha="right", va="top", style="italic",
        arrowprops=dict(arrowstyle="->", color=FAIL_ORANGE, lw=1.1,
                         connectionstyle="arc3,rad=-0.25"))


def panel_b_actionable_core(ax):
    ax.set_title("B  Actionable core (128 tasks)", fontsize=10, weight="bold", loc="left")
    conditions = ["Generic", "CTA", "Gated"]
    qwen = [(74.2, "95/128"), (98.4, "126/128"), (97.7, "125/128")]
    glm = [(72.7, "93/128"), (99.2, "127/128"), (100.0, "128/128")]

    x = np.arange(len(conditions))
    width = 0.34

    ax.bar(x - width / 2, [v for v, _ in qwen], width, label="Qwen",
           color=QWEN_BLUE, edgecolor=INK, linewidth=0.5)
    ax.bar(x + width / 2, [v for v, _ in glm], width, label="GLM",
           color=GLM_GOLD, edgecolor=INK, linewidth=0.5)

    # labels sit above the bars (never stamped inside the gold fill, which is
    # too light for reliable in-fill contrast) -- percentage bold, n/N muted.
    for i, ((qv, qn), (gv, gn)) in enumerate(zip(qwen, glm)):
        ax.text(i - width / 2, qv + 5.6, f"{qv:.1f}", ha="center", fontsize=7.5,
                 color=INK, weight="bold")
        ax.text(i - width / 2, qv + 1.8, qn, ha="center", fontsize=6, color=MUTED)
        ax.text(i + width / 2, gv + 5.6, f"{gv:.1f}", ha="center", fontsize=7.5,
                 color=INK, weight="bold")
        ax.text(i + width / 2, gv + 1.8, gn, ha="center", fontsize=6, color=MUTED)

    ax.set_xticks(x)
    ax.set_xticklabels(conditions, fontsize=8.5)
    ax.set_ylabel("Accuracy (%)", fontsize=8.5)
    ax.set_ylim(0, 116)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", color=LINE, linewidth=0.6, alpha=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False, fontsize=8,
              handlelength=1.2, columnspacing=1.2, borderaxespad=0.2)


def main() -> None:
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.2, 3.15))
    fig.subplots_adjust(left=0.045, right=0.98, top=0.86, bottom=0.14, wspace=0.28)

    panel_a_identifiability(ax_a)
    panel_b_actionable_core(ax_b)

    out_dirs = [
        Path("experiments/tri_artifact/reports/figures"),
        Path("paper/Figures"),
    ]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)
        fig.savefig(d / "tri_demo_identifiability_core.pdf", dpi=300)
    fig.savefig(out_dirs[0] / "tri_demo_identifiability_core.png", dpi=200)
    plt.close(fig)
    print("wrote tri_demo_identifiability_core.{pdf,png}")


if __name__ == "__main__":
    main()
