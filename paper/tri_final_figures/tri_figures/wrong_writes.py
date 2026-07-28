from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from .style import COLORS, MODEL_LABELS, apply_style, save_figure


def build(df, output_stem: Path):
    apply_style()
    models = ["Qwen3.5", "GLM-5.1", "DeepSeek"]
    controllers = ["Generic", "CTA"]

    fig, ax = plt.subplots(figsize=(7.05, 3.5))
    y_positions = []
    labels = []
    model_centers = []
    y = 0
    for model in models:
        model_rows = []
        for controller in controllers:
            row = df[(df["model"] == model) & (df["controller"] == controller)].iloc[0]
            y_positions.append(y)
            labels.append((controller, int(row["all_wrong_writes"])))
            model_rows.append(y)
            core = int(row["core_substitution_writes"])
            other = int(row["non_core_wrong_writes"])
            ax.barh(y, core, height=0.58, color=COLORS["coral"], edgecolor="none")
            ax.barh(y, other, left=core, height=0.58, color=COLORS["control"], edgecolor=COLORS["muted_ink"], lw=0.4)
            if core > 0:
                ax.text(core/2, y, f"{core}", ha="center", va="center", color="white", weight="semibold")
            if other > 0:
                ax.text(core+other+0.9, y, f"{other}", ha="left", va="center", color=COLORS["ink"])
            if core == 0:
                ax.text(0.8, y, "0 TRI", ha="left", va="center", color=COLORS["coral"], fontsize=7.2)
            y += 0.82
        model_centers.append((model, np.mean(model_rows)))
        y += 0.42

    ax.invert_yaxis()
    ax.set_xlim(0, 65)
    ax.set_xlabel("Wrong writes (count)")
    ax.set_yticks(y_positions)
    ax.set_yticklabels([f"{c} (total {t})" for c, t in labels])
    ax.tick_params(axis="y", length=0, pad=5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", color=COLORS["grid"], lw=0.45, alpha=0.45)
    ax.set_axisbelow(True)

    for i in range(2):
        sep = (model_centers[i][1] + model_centers[i+1][1]) / 2
        ax.axhline(sep, color=COLORS["grid"], ls=(0, (4, 3)), lw=0.7)
    for model, yc in model_centers:
        ax.text(-0.12, yc, MODEL_LABELS[model], transform=ax.get_yaxis_transform(), ha="right", va="center", color=COLORS["primary"], fontsize=8.7, weight="semibold", clip_on=False)

    legend = [
        Patch(facecolor=COLORS["coral"], label="TRI core substitution writes"),
        Patch(facecolor=COLORS["control"], edgecolor=COLORS["muted_ink"], label="Non-core wrong writes"),
    ]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False, columnspacing=2.0)
    fig.subplots_adjust(left=0.24, right=0.98, bottom=0.18, top=0.82)
    save_figure(fig, output_stem)
    plt.close(fig)
