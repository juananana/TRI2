from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from .style import COLORS, MODEL_MARKERS, MODEL_LABELS, apply_style, save_figure


def build(df, output_stem: Path):
    apply_style()
    sources = ["AgentDojo", "STATE-Bench", "ToolSandbox"]
    models = ["Qwen3.5", "GLM-5.1", "DeepSeek"]

    fig, ax = plt.subplots(figsize=(7.05, 3.65))
    ax.set_xlim(-0.7, 3.0)
    ax.set_ylim(-0.65, 3.45)
    ax.axis("off")

    for j, source in enumerate(sources):
        ax.text(j+0.5, 3.00, source, ha="center", va="bottom", fontsize=8.7, color=COLORS["primary"], weight="semibold")
        if j > 0:
            ax.axvline(j, ymin=0.05, ymax=0.88, color=COLORS["grid"], ls=(0, (3, 3)), lw=0.65)
    for i in [1, 2]:
        ax.axhline(3-i-0.20, xmin=0.09, xmax=0.99, color=COLORS["grid"], ls=(0, (3, 3)), lw=0.65)

    for i, model in enumerate(models):
        yc = 2.30 - i*1.0
        ax.scatter(-0.55, yc, s=40, marker=MODEL_MARKERS[model], facecolor=COLORS["primary"], edgecolor=COLORS["ink"], lw=0.5)
        ax.text(-0.42, yc, MODEL_LABELS[model], ha="left", va="center", fontsize=8.3, weight="semibold")
        for j, source in enumerate(sources):
            cell = df[(df["source_slice"] == source) & (df["model"] == model)]
            pair_h = float(cell[(cell["condition"] == "history_only") & (cell["metric"] == "pairacc")]["rate_pct"].iloc[0])
            pair_d = float(cell[(cell["condition"] == "decision_visible") & (cell["metric"] == "pairacc")]["rate_pct"].iloc[0])
            e2e_h = float(cell[(cell["condition"] == "history_only") & (cell["metric"] == "e2e")]["rate_pct"].iloc[0])
            e2e_d = float(cell[(cell["condition"] == "decision_visible") & (cell["metric"] == "e2e")]["rate_pct"].iloc[0])

            xh, xd = j+0.22, j+0.78
            y_base = yc
            scale = 0.0038
            yh = y_base + (pair_h-50)*scale
            yd = y_base + (pair_d-50)*scale
            diff = pair_d - pair_h
            line_color = COLORS["positive"] if diff > 0 else COLORS["coral"] if diff < 0 else COLORS["muted_ink"]
            ax.plot([xh, xd], [yh, yd], color=line_color, lw=1.3)
            ax.scatter(xh, yh, s=38, facecolor="white", edgecolor=COLORS["ink"], lw=0.7, zorder=3)
            ax.scatter(xd, yd, s=38, facecolor=COLORS["primary"], edgecolor=COLORS["ink"], lw=0.7, zorder=3)
            ax.text(xh, yh+0.12, f"{pair_h:.0f}%", ha="center", va="bottom", fontsize=7)
            ax.text(xd, yd+0.12, f"{pair_d:.0f}%", ha="center", va="bottom", fontsize=7)
            ax.text(xh, yh-0.15, "H", ha="center", va="top", fontsize=6.8)
            ax.text(xd, yd-0.15, "D", ha="center", va="top", fontsize=6.8)
            ax.text((xh+xd)/2, y_base-0.39,
                    f"E2E: {e2e_h:.0f} $\\rightarrow$ {e2e_d:.0f}",
                    ha="center", va="center", fontsize=6.6,
                    color=COLORS["muted_ink"], style="italic")

    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=COLORS["ink"], markersize=5.5, label="H = History-only"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["primary"], markeredgecolor=COLORS["ink"], markersize=5.5, label="D = Decision-visible"),
    ]
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.50, 0.995), ncol=2, frameon=False)
    fig.text(0.985, 0.955, "Top: PairAcc (%)\nBottom: E2E rate (%)", ha="right", va="top", fontsize=6.7, color=COLORS["muted_ink"], style="italic")

    fig.subplots_adjust(left=0.03, right=0.995, top=0.88, bottom=0.04)
    save_figure(fig, output_stem)
    plt.close(fig)
