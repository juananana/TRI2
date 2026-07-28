from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from .style import COLORS, MODEL_MARKERS, MODEL_LABELS, apply_style, save_figure


def build(df, output_stem: Path):
    apply_style()
    audits = [
        ("revision_full_diagnostic", "Authored full diagnostic"),
        ("revision_human_rewrite", "Human rewrite"),
        ("revision_source_grounded", "Source-grounded contrast"),
    ]
    metrics = [("changed_pairacc", "Changed PairAcc gain (pp)", (-20, 120)), ("actionable_e2e", "Actionable E2E gain (pp)", (-20, 72))]
    model_order = ["Qwen3.5", "GLM-5.1", "DeepSeek"]

    rows = []
    y = 0
    group_bounds = []
    for audit_id, audit_label in audits:
        start = y
        available = [m for m in model_order if ((df["audit_id"] == audit_id) & (df["model"] == m)).any()]
        for m in available:
            rows.append((y, audit_id, audit_label, m))
            y += 1
        group_bounds.append((start, y-1, audit_label))
        y += 0.55

    fig = plt.figure(figsize=(7.05, 3.55))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.75, 2.35, 2.35], wspace=0.12)
    ax_labels = fig.add_subplot(gs[0])
    axes = [fig.add_subplot(gs[1]), fig.add_subplot(gs[2])]

    ax_labels.set_ylim(-0.6, y-0.4)
    ax_labels.invert_yaxis()
    ax_labels.axis("off")
    for start, end, label in group_bounds:
        ax_labels.text(0.0, start-0.25, label, ha="left", va="bottom", weight="semibold", color=COLORS["muted_ink"])
        if end < rows[-1][0]:
            ax_labels.axhline(end+0.45, color=COLORS["grid"], ls=(0, (3, 3)), lw=0.65)
    for yy, _, _, model in rows:
        ax_labels.scatter(0.08, yy, s=28, marker=MODEL_MARKERS[model], facecolor=COLORS["primary"], edgecolor=COLORS["ink"], lw=0.5)
        ax_labels.text(0.18, yy, MODEL_LABELS[model], va="center", ha="left")
    ax_labels.set_xlim(0, 1)

    for ax, (metric, title, xlim) in zip(axes, metrics):
        ax.set_ylim(-0.6, y-0.4)
        ax.invert_yaxis()
        ax.axvline(0, color=COLORS["ink"], lw=0.8)
        ax.set_xlim(*xlim)
        ax.set_title(title, pad=4, weight="semibold")
        ax.set_xlabel("Percentage points")
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", color=COLORS["grid"], lw=0.45, alpha=0.45)
        ax.set_axisbelow(True)
        for start, end, _ in group_bounds:
            if end < rows[-1][0]:
                ax.axhline(end+0.45, color=COLORS["grid"], ls=(0, (3, 3)), lw=0.65)

        for yy, audit_id, _, model in rows:
            row = df[(df["audit_id"] == audit_id) & (df["model"] == model) & (df["metric"] == metric)].iloc[0]
            val = float(row["difference_pp"])
            lo = float(row["ci95_low_pp"])
            hi = float(row["ci95_high_pp"])
            ax.errorbar(val, yy, xerr=[[val-lo], [hi-val]], fmt=MODEL_MARKERS[model], ms=5.2, mfc=COLORS["primary"], mec=COLORS["ink"], mew=0.5, ecolor=COLORS["ink"], elinewidth=0.75, capsize=2.3, zorder=3)
            text_x = xlim[1] - 2.0
            ax.text(
                text_x,
                yy,
                f"{val:+.1f} [{lo:.1f}, {hi:.1f}]",
                ha="right",
                va="center",
                fontsize=6.2,
                color=COLORS["ink"],
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.88, pad=0.15),
            )

    fig.subplots_adjust(left=0.03, right=0.995, bottom=0.16, top=0.91)
    save_figure(fig, output_stem)
    plt.close(fig)
