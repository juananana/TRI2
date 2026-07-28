from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt

from .style import COLORS, MODEL_LABELS, apply_style, save_figure


def build(df, output_stem: Path):
    apply_style()
    audit_order = [
        ("revision_full_diagnostic", "Authored full diagnostic"),
        ("revision_human_rewrite", "Human rewrite"),
        ("revision_source_grounded", "Source-grounded controlled contrast"),
    ]
    model_order = ["Qwen3.5", "GLM-5.1", "DeepSeek"]

    rows = []
    y = 0.0
    groups = []
    for aid, label in audit_order:
        start = y
        for model in model_order:
            match = df[(df["audit_id"] == aid) & (df["model"] == model)]
            if match.empty:
                continue
            r = match.iloc[0]
            rows.append((y, aid, label, model, int(r["repairs"]), int(r["harms"])))
            y += 1.0
        groups.append((start, y - 1.0, aid, label))
        y += 0.65

    fig, ax = plt.subplots(figsize=(7.05, 3.45))
    for yy, _, _, model, repairs, harms in rows:
        ax.barh(yy, -harms, height=0.58, color=COLORS["coral"], edgecolor="none")
        ax.barh(yy, repairs, height=0.58, color=COLORS["positive"], edgecolor="none")
        ax.text(-harms - 0.40 if harms else -0.30, yy, str(harms), ha="right", va="center", color=COLORS["coral"], weight="semibold")
        ax.text(repairs + 0.40, yy, str(repairs), ha="left", va="center", color=COLORS["positive"], weight="semibold")
        ax.text(-19.6, yy, MODEL_LABELS[model], ha="left", va="center", fontsize=7.8, color=COLORS["ink"])

    ax.axvline(0, color=COLORS["ink"], lw=0.9)
    ax.set_xlim(-20.5, 20.5)
    ax.set_ylim(-0.8, y - 0.45)
    ax.invert_yaxis()
    ax.set_xlabel("Event count")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_xticks([-20, -15, -10, -5, 0, 5, 10, 15, 20])
    ax.set_xticklabels(["20", "15", "10", "5", "0", "5", "10", "15", "20"])

    for start, end, aid, label in groups:
        ax.text(-20.2, start - 0.42, label, ha="left", va="bottom", color=COLORS["muted_ink"], style="italic", fontsize=7.1)
        if aid == "revision_source_grounded":
            ax.text(-8.8, start - 0.42, "(post-primary)", ha="left", va="bottom", color=COLORS["amber"], style="italic", fontsize=6.8)
        if end < rows[-1][0]:
            ax.axhline(end + 0.50, color=COLORS["grid"], ls=(0, (3, 3)), lw=0.65)

    ax.text(-7.5, -0.62, "Harms", color=COLORS["coral"], ha="center", va="bottom", fontsize=8.6, weight="semibold")
    ax.text(7.5, -0.62, "Repairs", color=COLORS["positive"], ha="center", va="bottom", fontsize=8.6, weight="semibold")
    fig.subplots_adjust(left=0.06, right=0.985, top=0.90, bottom=0.16)
    save_figure(fig, output_stem)
    plt.close(fig)
