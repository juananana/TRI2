from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from .style import COLORS, MODEL_MARKERS, MODEL_LABELS, apply_style, save_figure


def _label(ax, x, y, text, dx, dy, color=None, ha="left", va="center"):
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(dx, dy),
        textcoords="offset points",
        fontsize=6.9,
        color=color or COLORS["ink"],
        ha=ha,
        va=va,
        annotation_clip=False,
    )


def build(df, output_stem: Path):
    apply_style()
    d = df[(df["dataset"] == "v3") & (df["slice"] == "all")].copy()

    fig = plt.figure(figsize=(7.05, 4.45))
    gs = GridSpec(2, 1, height_ratios=[3.45, 1.15], hspace=0.04, figure=fig)
    ax_top = fig.add_subplot(gs[0])
    ax_bot = fig.add_subplot(gs[1], sharex=ax_top)

    for ax in (ax_top, ax_bot):
        ax.set_xlim(0, 112)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.tick_params(direction="out", length=3, width=0.7, colors=COLORS["ink"])

    ax_top.set_ylim(50, 102)
    ax_bot.set_ylim(0, 22)
    ax_top.spines["bottom"].set_visible(False)
    ax_bot.spines["top"].set_visible(False)
    ax_top.tick_params(labelbottom=False, bottom=False)

    # Region backgrounds.
    ax_top.add_patch(Rectangle((0, 50), 50, 52, color=COLORS["coral_light"], zorder=0))
    ax_top.add_patch(Rectangle((50, 50), 50, 52, color=COLORS["primary_light"], zorder=0))
    ax_bot.add_patch(Rectangle((0, 0), 50, 22, color=COLORS["neutral_bg"], zorder=0))
    ax_bot.add_patch(Rectangle((50, 0), 50, 22, color=COLORS["coral_light"], zorder=0))
    for ax in (ax_top, ax_bot):
        ax.axvline(50, color=COLORS["grid"], ls=(0, (4, 4)), lw=0.8, zorder=1)
    ax_top.axhline(50, color=COLORS["grid"], ls=(0, (4, 4)), lw=0.8, zorder=1)

    # Region labels.
    ax_top.text(19, 67, "Always-Reevaluate", color=COLORS["coral"], fontsize=9.2, weight="semibold")
    ax_top.text(67, 58.5, "Selective region", color=COLORS["primary"], fontsize=9.2, weight="semibold")
    ax_bot.text(18, 11.0, "Fails both", color=COLORS["muted_ink"], fontsize=8.8, weight="semibold")
    ax_bot.text(68, 11.0, "Always-Lock", color=COLORS["coral"], fontsize=8.8, weight="semibold")

    marker_size = 46
    edge = COLORS["ink"]

    # Deterministic anchors.
    anchors = d[d["controller"].isin(["Always-Lock+validity", "Always-Reevaluate"])]
    for _, row in anchors.iterrows():
        x = row["preserve_accuracy_pct"]
        y = row["reevaluate_accuracy_pct"]
        ax = ax_top if y >= 50 else ax_bot
        ax.scatter(x, y, s=marker_size, marker="o", facecolor=COLORS["control"], edgecolor=edge, lw=0.7, zorder=5)
        changed_note = "0/32 changed"
        if row["controller"] == "Always-Reevaluate":
            _label(ax, x, y, f"Always-Reevaluate\nPairAcc {int(row['both_correct'])}/80; {changed_note}", 7, -2)
        else:
            _label(ax, x, y, f"Always-Lock + validity\nPairAcc {int(row['both_correct'])}/80; {changed_note}", 10, -1)

    # Controller points.
    controllers = ["Generic", "CTA", "Lifecycle-free", "Lifecycle-gated"]
    label_offsets = {
        ("Qwen3.5", "Generic"): (-6, -17),
        ("GLM-5.1", "Generic"): (-10, -17),
        ("Qwen3.5", "CTA"): (-38, -8),
        ("GLM-5.1", "CTA"): (-38, -24),
    }
    lifecycle_label_y = {
        ("GLM-5.1", "Lifecycle-gated"): 101.0,
        ("Qwen3.5", "Lifecycle-gated"): 96.5,
        ("GLM-5.1", "Lifecycle-free"): 91.8,
        ("Qwen3.5", "Lifecycle-free"): 87.0,
    }
    for _, row in d[d["controller"].isin(controllers)].iterrows():
        model = row["model"]
        ctrl = row["controller"]
        x = row["preserve_accuracy_pct"]
        y = row["reevaluate_accuracy_pct"]
        marker = MODEL_MARKERS[model]
        ax_top.scatter(x, y, s=marker_size, marker=marker, facecolor=COLORS["primary"], edgecolor=edge, lw=0.7, zorder=6)
        if ctrl in {"Lifecycle-free", "Lifecycle-gated"}:
            ly = lifecycle_label_y[(model, ctrl)]
            display_ctrl = {
                "Lifecycle-free": "Lifecycle-Actor",
                "Lifecycle-gated": "Lifecycle-Gated",
            }[ctrl]
            ax_top.annotate(
                f"{MODEL_LABELS[model]} {display_ctrl}\nPairAcc {int(row['both_correct'])}/80",
                xy=(x, y), xytext=(102.2, ly), textcoords="data",
                ha="left", va="center", fontsize=6.7, color=COLORS["ink"],
                arrowprops=dict(arrowstyle="-", color=COLORS["grid"], lw=0.6),
                annotation_clip=False,
            )
        else:
            if ctrl == "CTA":
                tx, ty = ((86.5, 97.0) if model == "Qwen3.5" else (86.5, 92.0))
                ax_top.annotate(
                    f"{MODEL_LABELS[model]} {ctrl}\nPairAcc {int(row['both_correct'])}/80",
                    xy=(x, y), xytext=(tx, ty), textcoords="data",
                    ha="right", va="center", fontsize=6.7, color=COLORS["ink"],
                    arrowprops=dict(arrowstyle="-", color=COLORS["grid"], lw=0.55),
                    annotation_clip=False,
                )
            else:
                dx, dy = label_offsets[(model, ctrl)]
                _label(
                    ax_top, x, y,
                    f"{MODEL_LABELS[model]} {ctrl}\nPairAcc {int(row['both_correct'])}/80",
                    dx, dy, ha="right" if dx < -20 else "left",
                )

    # Post-hoc rule.
    rule = d[d["controller"] == "Rule v2 (post-hoc)"].iloc[0]
    ax_top.scatter(
        rule["preserve_accuracy_pct"],
        rule["reevaluate_accuracy_pct"],
        s=54,
        marker="s",
        facecolor="white",
        edgecolor=COLORS["amber"],
        lw=1.2,
        zorder=7,
    )
    _label(
        ax_top,
        rule["preserve_accuracy_pct"],
        rule["reevaluate_accuracy_pct"],
        f"Rule* (post-hoc)\nPairAcc {int(rule['both_correct'])}/80",
        -5,
        -23,
        color=COLORS["amber"],
        ha="center",
    )

    # Axes and break marks.
    ax_bot.set_xlabel("Preserve accuracy (%)", labelpad=4)
    fig.text(0.015, 0.48, "Reevaluate accuracy (%)", rotation=90, va="center", ha="center", fontsize=8.5)
    ax_bot.set_xticks([0, 20, 40, 60, 80, 100])
    ax_bot.set_yticks([0, 20])
    ax_top.set_yticks([60, 80, 100])
    dmark = 0.009
    kwargs = dict(transform=ax_top.transAxes, color=COLORS["ink"], clip_on=False, lw=0.9)
    ax_top.plot((-dmark, +dmark), (-dmark, +dmark), **kwargs)
    kwargs.update(transform=ax_bot.transAxes)
    ax_bot.plot((-dmark, +dmark), (1 - dmark, 1 + dmark), **kwargs)

    # Compact, centered legend above plot.
    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=edge, markersize=5.5, label="Qwen"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="white", markeredgecolor=edge, markersize=5.5, label="GLM"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["primary"], markeredgecolor=edge, markersize=5.5, label="Controller probes"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["control"], markeredgecolor=edge, markersize=5.5, label="Deterministic controls"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="white", markeredgecolor=COLORS["amber"], markersize=5.5, label="Rule* (post-hoc)"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.995),
        ncol=5,
        frameon=True,
        fancybox=False,
        edgecolor=COLORS["grid"],
        framealpha=1,
        columnspacing=1.1,
        handletextpad=0.4,
        borderpad=0.5,
    )

    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.12, top=0.88)
    save_figure(fig, output_stem)
    plt.close(fig)
