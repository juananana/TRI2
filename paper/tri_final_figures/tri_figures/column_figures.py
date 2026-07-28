from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

from .style import COLORS, MODEL_LABELS, MODEL_MARKERS, apply_style, save_figure
from .target_flow import _ribbon


MODELS = ["Qwen3.5", "GLM-5.1", "DeepSeek"]


def build_target_flow(df, output_stem: Path) -> None:
    """Single-column flow view of shared-eligible substitutions."""
    apply_style()
    rows = df[df["controller"].isin(["Generic", "CTA"])].copy()
    fig, ax = plt.subplots(figsize=(3.35, 3.65))
    ax.set_xlim(0, 1)
    ax.set_ylim(0.02, 3.35)
    ax.axis("off")

    x_source0, x_source1 = 0.02, 0.18
    x_method = 0.30
    x_flow0, x_out0, x_out1 = 0.40, 0.70, 0.985
    group_centers = [2.75, 1.65, 0.55]
    for model, center in zip(MODELS, group_centers):
        model_rows = rows[rows["model"] == model]
        generic = model_rows[model_rows["controller"] == "Generic"].iloc[0]
        cta = model_rows[model_rows["controller"] == "CTA"].iloc[0]
        n = int(generic["shared_eligible"])
        substitutions = int(generic["substitutions"])
        retained = n - substitutions

        ax.text(0.02, center + 0.43, MODEL_LABELS[model], ha="left", va="bottom", fontsize=8.2, color=COLORS["primary"], weight="semibold")
        ax.add_patch(Rectangle((x_source0, center - 0.24), x_source1 - x_source0, 0.48, facecolor="white", edgecolor=COLORS["primary"], linewidth=0.8))
        ax.text((x_source0 + x_source1) / 2, center, f"shared\neligible\n$n={n}$", ha="center", va="center", fontsize=6.2, linespacing=1.0)

        y_sub = center + 0.17
        y_retained = center - 0.02
        y_cta = center - 0.27
        label_box = dict(facecolor="white", edgecolor="none", pad=0.3)
        ax.text(x_method, center + 0.08, "Generic", ha="center", va="center", fontsize=6.7, weight="semibold", bbox=label_box, zorder=5)
        ax.text(x_method, y_cta, "CTA", ha="center", va="center", fontsize=6.7, weight="semibold", bbox=label_box, zorder=5)
        ax.plot([x_source1, x_flow0], [center + 0.08, center + 0.08], color=COLORS["ink"], linewidth=0.6, zorder=1)
        ax.plot([x_source1, x_flow0], [y_cta, y_cta], color=COLORS["ink"], linewidth=0.6, zorder=1)

        sub_height = 0.07 + 0.08 * substitutions / n
        retained_height = 0.07 + 0.08 * retained / n
        _ribbon(ax, x_flow0, x_out0, center + 0.08, y_sub, 0.045, sub_height, COLORS["coral"], alpha=0.96, lw=0.3)
        _ribbon(ax, x_flow0, x_out0, center + 0.08, y_retained, 0.045, retained_height, COLORS["neutral"], alpha=1.0, edge=COLORS["grid"], lw=0.4)
        _ribbon(ax, x_flow0, x_out0, y_cta, y_cta, 0.05, 0.12, COLORS["primary"], alpha=0.98, lw=0.3)

        ax.add_patch(Rectangle((x_out0, y_sub - 0.085), x_out1 - x_out0, 0.17, facecolor=COLORS["coral"], edgecolor="none"))
        ax.add_patch(Rectangle((x_out0, y_retained - 0.085), x_out1 - x_out0, 0.17, facecolor=COLORS["neutral"], edgecolor=COLORS["grid"], linewidth=0.45))
        ax.add_patch(Rectangle((x_out0, y_cta - 0.085), x_out1 - x_out0, 0.17, facecolor=COLORS["primary"], edgecolor="none"))
        ax.text((x_out0 + x_out1) / 2, y_sub, f"substitute {substitutions}/{n}", ha="center", va="center", color="white", fontsize=6.3, weight="semibold")
        ax.text((x_out0 + x_out1) / 2, y_retained, f"retain/other {retained}/{n}", ha="center", va="center", color=COLORS["ink"], fontsize=6.1)
        ax.text((x_out0 + x_out1) / 2, y_cta, f"substitute 0/{int(cta['shared_eligible'])}", ha="center", va="center", color="white", fontsize=6.3, weight="semibold")

        if center > group_centers[-1]:
            ax.axhline(center - 0.55, color=COLORS["grid"], linestyle=(0, (3, 3)), linewidth=0.55)

    ax.text((x_source0 + x_source1) / 2, 3.28, "Input", ha="center", va="bottom", fontsize=7.0, color=COLORS["muted_ink"], weight="semibold")
    ax.text(x_method, 3.28, "Method", ha="center", va="bottom", fontsize=7.0, color=COLORS["muted_ink"], weight="semibold")
    ax.text((x_out0 + x_out1) / 2, 3.28, "Observed target", ha="center", va="bottom", fontsize=7.0, color=COLORS["muted_ink"], weight="semibold")
    ax.legend(
        handles=[
            Patch(facecolor=COLORS["coral"], label="Refreshed-winner substitution"),
            Patch(facecolor=COLORS["neutral"], edgecolor=COLORS["grid"], label="Retained / other"),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 1.07),
        ncol=2,
        frameon=False,
        handlelength=1.2,
        columnspacing=0.8,
        handletextpad=0.35,
        fontsize=6.4,
        borderaxespad=0,
    )
    fig.subplots_adjust(left=0.02, right=0.99, top=0.86, bottom=0.02)
    save_figure(fig, output_stem)
    plt.close(fig)


def build_wrong_writes(df, output_stem: Path) -> None:
    """Single-column decomposition of fixed-executor wrong writes."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.05))
    y_positions = [5.25, 4.58, 3.28, 2.61, 1.31, 0.64]
    labels: list[str] = []

    index = 0
    for model in MODELS:
        for controller in ("Generic", "CTA"):
            row = df[(df["model"] == model) & (df["controller"] == controller)].iloc[0]
            y = y_positions[index]
            core = int(row["core_substitution_writes"])
            other = int(row["non_core_wrong_writes"])
            total = int(row["all_wrong_writes"])
            labels.append(f"{MODEL_LABELS[model]} / {controller} ({total})")
            ax.barh(y, core, height=0.46, color=COLORS["coral"], edgecolor="none")
            ax.barh(y, other, left=core, height=0.46, color=COLORS["control"], edgecolor=COLORS["muted_ink"], linewidth=0.4)
            if core:
                ax.text(core / 2, y, str(core), ha="center", va="center", color="white", fontsize=7.0, weight="semibold")
            else:
                ax.text(other + 1.0, y, "0 TRI", ha="left", va="center", color=COLORS["coral"], fontsize=6.9, weight="semibold")
            if other and core:
                ax.text(core + other + 0.9, y, str(other), ha="left", va="center", color=COLORS["ink"], fontsize=7.0)
            index += 1

    for y in (3.94, 1.97):
        ax.axhline(y, color=COLORS["grid"], linestyle=(0, (3, 3)), linewidth=0.65)
    ax.set_xlim(0, 65)
    ax.set_ylim(0.15, 5.72)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=6.8)
    ax.set_xlabel("Wrong-target writes (count)")
    ax.tick_params(axis="y", length=0, pad=4)
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.45, alpha=0.45)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.legend(
        handles=[
            Patch(facecolor=COLORS["coral"], label="TRI substitution"),
            Patch(facecolor=COLORS["control"], edgecolor=COLORS["muted_ink"], label="Other error"),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=2,
        frameon=False,
        columnspacing=1.1,
        handlelength=1.5,
        borderaxespad=0,
    )
    fig.subplots_adjust(left=0.36, right=0.98, top=0.87, bottom=0.17)
    save_figure(fig, output_stem)
    plt.close(fig)


def build_transfer_fingerprints(df, output_stem: Path) -> None:
    """Single-column source/model fingerprint with a compact metric table."""
    apply_style()
    sources = ["STATE-Bench", "AgentDojo", "ToolSandbox"]
    fig, ax = plt.subplots(figsize=(3.35, 4.3))
    group_rows = {
        "STATE-Bench": [8.15, 7.35, 6.55],
        "AgentDojo": [5.15, 4.35, 3.55],
        "ToolSandbox": [2.15, 1.35, 0.55],
    }
    y_ticks: list[float] = []
    y_labels: list[str] = []
    for source in sources:
        ax.text(
            -0.42,
            group_rows[source][0] + 0.52,
            source,
            transform=ax.get_yaxis_transform(),
            ha="left",
            va="bottom",
            fontsize=7.5,
            color=COLORS["primary"],
            weight="semibold",
            clip_on=False,
        )
        for model, y in zip(MODELS, group_rows[source]):
            pair = df[(df["source_slice"] == source) & (df["model"] == model) & (df["metric"] == "pairacc")]
            e2e = df[(df["source_slice"] == source) & (df["model"] == model) & (df["metric"] == "e2e")]
            pair_h = float(pair[pair["condition"] == "history_only"]["rate_pct"].iloc[0])
            pair_d = float(pair[pair["condition"] == "decision_visible"]["rate_pct"].iloc[0])
            e2e_h = float(e2e[e2e["condition"] == "history_only"]["rate_pct"].iloc[0])
            e2e_d = float(e2e[e2e["condition"] == "decision_visible"]["rate_pct"].iloc[0])
            delta = pair_d - pair_h
            color = COLORS["positive"] if delta > 0 else COLORS["coral"] if delta < 0 else COLORS["muted_ink"]
            ax.plot([pair_h, pair_d], [y, y], color=color, linewidth=1.35, zorder=2)
            ax.scatter(pair_h, y, s=30, facecolor="white", edgecolor=COLORS["ink"], linewidth=0.65, zorder=3)
            ax.scatter(pair_d, y, s=30, facecolor=COLORS["primary"], edgecolor=COLORS["ink"], linewidth=0.65, zorder=3)
            ax.text(1.06, y, f"{pair_h:.0f}$\\rightarrow${pair_d:.0f}", transform=ax.get_yaxis_transform(), ha="center", va="center", fontsize=6.3, color=color, weight="semibold" if delta else "normal", clip_on=False)
            ax.text(1.43, y, f"{e2e_h:.0f}$\\rightarrow${e2e_d:.0f}", transform=ax.get_yaxis_transform(), ha="center", va="center", fontsize=6.3, color=COLORS["muted_ink"], clip_on=False)
            y_ticks.append(y)
            y_labels.append(MODEL_LABELS[model])

    ax.set_xlim(-5, 105)
    ax.set_ylim(0.05, 9.05)
    ax.set_xticks([0, 50, 100])
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=6.8)
    ax.set_xlabel("Changed PairAcc (%)", labelpad=2)
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.45, alpha=0.45)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=4)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    for separator in (5.95, 2.95):
        ax.axhline(separator, color=COLORS["grid"], linestyle=(0, (3, 3)), linewidth=0.65)

    fig.text(0.69, 0.88, "PairAcc\nH$\\rightarrow$D", ha="center", va="bottom", fontsize=6.7, weight="semibold")
    fig.text(0.89, 0.88, "E2E\nH$\\rightarrow$D", ha="center", va="bottom", fontsize=6.7, weight="semibold")

    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=COLORS["ink"], markersize=4.8, label="History-only"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["primary"], markeredgecolor=COLORS["ink"], markersize=4.8, label="Decision-visible"),
    ]
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.56, 0.995), ncol=2, frameon=False, columnspacing=0.9, handletextpad=0.3)
    fig.subplots_adjust(left=0.28, right=0.64, top=0.85, bottom=0.11)
    save_figure(fig, output_stem)
    plt.close(fig)


def build_effect_sizes(df, output_stem: Path) -> None:
    """Single-column stacked forest plots for equal-call effects."""
    apply_style()
    audits = [
        ("revision_full_diagnostic", "Authored"),
        ("revision_human_rewrite", "Rewrite"),
        ("revision_source_grounded", "Source"),
    ]
    metrics = [
        ("changed_pairacc", "Changed PairAcc gain", (-20, 112)),
        ("actionable_e2e", "Actionable E2E gain", (-20, 72)),
    ]
    rows: list[tuple[str, str, str]] = []
    for audit_id, short_label in audits:
        for model in MODELS:
            if ((df["audit_id"] == audit_id) & (df["model"] == model)).any():
                rows.append((audit_id, short_label, model))

    fig, axes = plt.subplots(2, 1, figsize=(3.35, 4.8), sharey=True, gridspec_kw={"hspace": 0.48})
    y_positions = np.arange(len(rows))[::-1]
    labels = [f"{audit} / {MODEL_LABELS[model]}" for _, audit, model in rows]

    for ax, (metric, title, xlim) in zip(axes, metrics):
        for y, (audit_id, _, model) in zip(y_positions, rows):
            row = df[(df["audit_id"] == audit_id) & (df["model"] == model) & (df["metric"] == metric)].iloc[0]
            value = float(row["difference_pp"])
            low = float(row["ci95_low_pp"])
            high = float(row["ci95_high_pp"])
            ax.errorbar(
                value,
                y,
                xerr=[[value - low], [high - value]],
                fmt=MODEL_MARKERS[model],
                markersize=5.0,
                markerfacecolor=COLORS["primary"],
                markeredgecolor=COLORS["ink"],
                markeredgewidth=0.5,
                ecolor=COLORS["ink"],
                elinewidth=0.75,
                capsize=2.2,
                zorder=3,
            )
            ax.text(
                xlim[1] - 1.5,
                y,
                f"{value:+.1f} [{low:.1f}, {high:.1f}]",
                ha="right",
                va="center",
                fontsize=6.0,
                color=COLORS["ink"],
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=0.12),
            )
        ax.axvline(0, color=COLORS["ink"], linewidth=0.8)
        ax.set_xlim(*xlim)
        ax.set_ylim(-0.65, len(rows) - 0.35)
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels, fontsize=6.7)
        ax.set_xlabel("Decision-visible minus History-only (pp)", labelpad=2)
        ax.set_title(title, fontsize=8.2, weight="semibold", pad=4)
        ax.grid(axis="x", color=COLORS["grid"], linewidth=0.45, alpha=0.45)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0, pad=4)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        for separator in (4.5, 2.5):
            ax.axhline(separator, color=COLORS["grid"], linestyle=(0, (3, 3)), linewidth=0.65)

    fig.subplots_adjust(left=0.31, right=0.99, top=0.96, bottom=0.09)
    save_figure(fig, output_stem)
    plt.close(fig)
