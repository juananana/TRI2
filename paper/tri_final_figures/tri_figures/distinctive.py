from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, PathPatch, Rectangle
from matplotlib.path import Path as MplPath

from .style import COLORS, MODEL_LABELS, MODEL_MARKERS, apply_style, save_figure


MODELS = ["Qwen3.5", "GLM-5.1", "DeepSeek"]
CTRL_COLORS = {
    "Generic": COLORS["coral"],
    "CTA": COLORS["primary"],
    "Lifecycle-free": "#6D7894",
    "Lifecycle-gated": COLORS["positive"],
    "Always-Lock+validity": COLORS["muted_ink"],
    "Always-Reevaluate": COLORS["control"],
    "Rule v2 (post-hoc)": COLORS["amber"],
}
CTRL_MARKERS = {
    "Generic": "o",
    "CTA": "s",
    "Lifecycle-free": "^",
    "Lifecycle-gated": "D",
    "Always-Lock+validity": "<",
    "Always-Reevaluate": ">",
    "Rule v2 (post-hoc)": "P",
}
CTRL_LINESTYLES = {
    "Generic": "-",
    "CTA": "-",
    "Lifecycle-free": (0, (4, 2)),
    "Lifecycle-gated": (0, (1, 1)),
    "Always-Lock+validity": (0, (5, 2)),
    "Always-Reevaluate": (0, (1.5, 1.5)),
    "Rule v2 (post-hoc)": "-",
}


def _panel_label(ax, label: str) -> None:
    ax.text(-0.02, 1.02, label, transform=ax.transAxes, ha="left", va="bottom", fontsize=9.2, weight="bold")


def _rounded_box(ax, xy, width, height, text, edge, face="white", fontsize=6.6, weight="normal"):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        facecolor=face,
        edgecolor=edge,
        linewidth=0.75,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=fontsize, weight=weight)
    return patch


def build_authorization_trajectory(output_stem: Path) -> None:
    """Concept figure: world evidence and authorized referent as separate trajectories."""
    apply_style()
    fig = plt.figure(figsize=(3.35, 4.45))
    gs = GridSpec(3, 1, height_ratios=[1.05, 1.55, 1.35], hspace=0.42, figure=fig)

    # A. State evidence: the selector winner flips even though both entities persist.
    ax = fig.add_subplot(gs[0])
    _panel_label(ax, "A")
    x = np.array([0, 1])
    ax.plot(x, [0.82, 0.35], color=COLORS["coral"], marker="o", markersize=4.8, lw=1.7)
    ax.plot(x, [0.32, 0.86], color=COLORS["primary"], marker="s", markersize=4.6, lw=1.7)
    ax.axvline(0.5, color=COLORS["grid"], lw=0.7, ls=(0, (3, 3)))
    ax.text(0.5, 0.99, "refresh", ha="center", va="top", fontsize=6.6, color=COLORS["muted_ink"])
    ax.text(-0.035, 0.84, "A  highest", ha="right", va="center", fontsize=6.5, color=COLORS["coral"])
    ax.text(-0.035, 0.31, "B", ha="right", va="center", fontsize=6.5, color=COLORS["primary"])
    ax.text(1.035, 0.35, "A  valid", ha="left", va="center", fontsize=6.5, color=COLORS["coral"])
    ax.text(1.035, 0.86, "B  highest", ha="left", va="center", fontsize=6.5, color=COLORS["primary"])
    ax.text(0.0, 0.04, "$S_0$", ha="center", va="bottom", fontsize=7.2)
    ax.text(1.0, 0.04, "$S_1$", ha="center", va="bottom", fontsize=7.2)
    ax.set_xlim(-0.17, 1.18)
    ax.set_ylim(0, 1.02)
    ax.axis("off")

    # B. Referential trajectories: same evidence, opposite authorized target.
    ax = fig.add_subplot(gs[1])
    _panel_label(ax, "B")
    stages = np.arange(4)
    stage_labels = ["request", "bind slot", "refresh", "write"]
    ax.plot(stages, [1.0, 1.0, 0.0, 0.0], color=COLORS["grid"], lw=1.1, ls=(0, (3, 2)), zorder=1)
    ax.text(2.48, 0.16, "selector winner B", ha="center", va="bottom", fontsize=6.0, color=COLORS["muted_ink"])

    preserve = [1.0, 1.0, 1.0, 1.0]
    ax.plot(stages, preserve, color=COLORS["coral"], lw=2.2, marker="o", markersize=4.4, zorder=3)
    ax.text(3.03, 1.0, "Preserve: write A", ha="left", va="center", fontsize=6.5, color=COLORS["coral"], weight="semibold")
    ax.annotate("commit A", xy=(1, 1), xytext=(1, 1.32), ha="center", va="bottom", fontsize=6.2,
                arrowprops=dict(arrowstyle="-|>", color=COLORS["coral"], lw=0.65))

    ax.plot([0, 1.84], [-0.72, -0.72], color=COLORS["primary"], lw=1.4, ls=(0, (2, 2)))
    ax.plot([2, 3], [-0.72, 0.0], color=COLORS["primary"], lw=2.2, marker="s", markersize=4.2, zorder=3)
    ax.text(0.08, -0.58, "Reevaluate: selector remains deferred", ha="left", va="bottom", fontsize=6.3, color=COLORS["primary"])
    ax.text(3.03, -0.03, "write B", ha="left", va="top", fontsize=6.5, color=COLORS["primary"], weight="semibold")
    ax.annotate("resolve at $S_1$", xy=(2, -0.72), xytext=(2.18, -1.02), ha="left", va="top", fontsize=6.2,
                arrowprops=dict(arrowstyle="-|>", color=COLORS["primary"], lw=0.65))

    for i, label in enumerate(stage_labels):
        ax.axvline(i, color=COLORS["grid"], lw=0.45, alpha=0.55, zorder=0)
        ax.text(i, -1.22, label, ha="center", va="top", fontsize=6.2, color=COLORS["muted_ink"])
    ax.text(-0.13, 1.0, "A", ha="right", va="center", fontsize=7.0, weight="semibold")
    ax.text(-0.13, 0.0, "B", ha="right", va="center", fontsize=7.0, weight="semibold")
    ax.set_xlim(-0.35, 3.72)
    ax.set_ylim(-1.28, 1.5)
    ax.axis("off")

    # C. Compact decision tree plus the observed contradictory trace.
    ax = fig.add_subplot(gs[2])
    _panel_label(ax, "C")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _rounded_box(ax, (0.02, 0.64), 0.27, 0.20, "Referent bound\nbefore refresh?", COLORS["ink"], fontsize=5.9, weight="semibold")
    _rounded_box(ax, (0.41, 0.72), 0.22, 0.17, "yes: carry\nentity A", COLORS["coral"], face=COLORS["coral_light"], fontsize=6.2)
    _rounded_box(ax, (0.41, 0.43), 0.22, 0.17, "no: query\n$S_1$ -> B", COLORS["primary"], face=COLORS["primary_light"], fontsize=6.2)
    ax.add_patch(FancyArrowPatch((0.29, 0.76), (0.41, 0.805), arrowstyle="-|>", mutation_scale=7, lw=0.7, color=COLORS["ink"]))
    ax.add_patch(FancyArrowPatch((0.29, 0.70), (0.41, 0.515), arrowstyle="-|>", mutation_scale=7, lw=0.7, color=COLORS["ink"]))
    ax.text(0.70, 0.82, "validity may veto; it does not\nauthorize a replacement", ha="left", va="center", fontsize=5.8, color=COLORS["muted_ink"])

    ax.plot([0.06, 0.94], [0.24, 0.24], color=COLORS["grid"], lw=0.6)
    trace_x = [0.09, 0.39, 0.68, 0.92]
    trace_labels = ["stored A", "refresh", "selector->B", "wrote B"]
    for x0, label in zip(trace_x, trace_labels):
        ax.scatter(x0, 0.10, s=24, facecolor="white", edgecolor=COLORS["coral"], lw=0.9, zorder=3)
        ax.text(x0, 0.01, label, ha="center", va="bottom", fontsize=5.9)
    for left, right in zip(trace_x[:-1], trace_x[1:]):
        ax.add_patch(FancyArrowPatch((left + 0.02, 0.10), (right - 0.02, 0.10), arrowstyle="-|>", mutation_scale=6, lw=0.75, color=COLORS["coral"]))
    ax.text(0.50, 0.285, "observed Preserve trace: evidence overwrote commitment", ha="center", va="bottom", fontsize=6.2, color=COLORS["coral"], weight="semibold")

    fig.subplots_adjust(left=0.08, right=0.90, top=0.985, bottom=0.025)
    save_figure(fig, output_stem)
    plt.close(fig)


def _parallel_panel(ax, df, model: str, title: str) -> None:
    dims = [
        ("changed_winner_core", "preserve_accuracy_pct", "Changed\nPreserve"),
        ("changed_winner_core", "reevaluate_accuracy_pct", "Changed\nReevaluate"),
        ("stable_control", "pairacc_pct", "Stable\nPairAcc"),
        ("invalidity_policy", "pairacc_pct", "Reject slice\nPairAcc"),
    ]
    controllers = ["Generic", "CTA", "Lifecycle-free", "Lifecycle-gated"]
    x = np.arange(len(dims))
    for controller in controllers:
        values = []
        for slice_name, metric, _ in dims:
            row = df[(df["dataset"] == "v3") & (df["model"] == model) & (df["controller"] == controller) & (df["slice"] == slice_name)]
            values.append(float(row.iloc[0][metric]))
        ax.plot(
            x,
            values,
            color=CTRL_COLORS[controller],
            marker=CTRL_MARKERS[controller],
            ls=CTRL_LINESTYLES[controller],
            markersize=4.2,
            lw=1.5,
            alpha=0.95,
            label=controller,
        )
    for xi in x:
        ax.axvline(xi, color=COLORS["grid"], lw=0.65, zorder=0)
    ax.set_xlim(-0.08, len(dims) - 0.92)
    ax.set_ylim(-3, 103)
    ax.set_xticks(x)
    ax.set_xticklabels([label for _, _, label in dims], fontsize=6.2)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_title(title, fontsize=8.0, weight="semibold", pad=5)
    ax.grid(axis="y", color=COLORS["grid"], lw=0.45, alpha=0.45)
    for spine in ("top", "right", "left", "bottom"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=3)
    ax.tick_params(axis="y", length=0, pad=2)


def build_policy_fingerprints(df, output_stem: Path) -> None:
    """Parallel-coordinate policy signatures across task slices."""
    apply_style()
    fig = plt.figure(figsize=(7.05, 3.55))
    gs = GridSpec(2, 3, height_ratios=[3.25, 1.05], hspace=0.42, wspace=0.28, figure=fig)
    ax_q = fig.add_subplot(gs[0, 0])
    ax_g = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    _parallel_panel(ax_q, df, "Qwen3.5", "Qwen")
    _parallel_panel(ax_g, df, "GLM-5.1", "GLM")

    dims = [
        ("changed_winner_core", "preserve_accuracy_pct", "Changed\nPreserve"),
        ("changed_winner_core", "reevaluate_accuracy_pct", "Changed\nReevaluate"),
        ("stable_control", "pairacc_pct", "Stable\nPairAcc"),
        ("invalidity_policy", "pairacc_pct", "Reject slice\nPairAcc"),
    ]
    controls = ["Always-Lock+validity", "Always-Reevaluate", "Rule v2 (post-hoc)"]
    x = np.arange(4)
    for ctrl in controls:
        vals = []
        for slice_name, metric, _ in dims:
            row = df[(df["dataset"] == "v3") & (df["controller"] == ctrl) & (df["slice"] == slice_name)]
            vals.append(float(row.iloc[0][metric]))
        ax_c.plot(
            x,
            vals,
            color=CTRL_COLORS[ctrl],
            marker=CTRL_MARKERS[ctrl],
            markersize=4.0,
            lw=1.45,
            ls=CTRL_LINESTYLES[ctrl],
            label=ctrl,
        )
    for xi in x:
        ax_c.axvline(xi, color=COLORS["grid"], lw=0.65, zorder=0)
    ax_c.set_xlim(-0.08, 3.08)
    ax_c.set_ylim(-3, 103)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels([label for _, _, label in dims], fontsize=6.2)
    ax_c.set_yticks([0, 25, 50, 75, 100])
    ax_c.set_title("Policy controls", fontsize=8.0, weight="semibold", pad=5)
    ax_c.grid(axis="y", color=COLORS["grid"], lw=0.45, alpha=0.45)
    for spine in ("top", "right", "left", "bottom"):
        ax_c.spines[spine].set_visible(False)
    ax_c.tick_params(axis="both", length=0, pad=2)

    ax_note = fig.add_subplot(gs[1, :])
    ax_note.set_xlim(0, 100)
    ax_note.set_ylim(0, 1)
    ax_note.axis("off")
    ax_note.axhline(0.55, xmin=0.02, xmax=0.98, color=COLORS["grid"], lw=0.7)
    ax_note.text(2, 0.76, "diagnostic signature", fontsize=6.7, color=COLORS["muted_ink"], weight="semibold")
    ax_note.text(2, 0.27, "unconditional policies trace opposite diagonals; selective controllers stay high on both changed members", fontsize=7.1)
    legend_controllers = [
        ("Generic", "Generic"),
        ("CTA", "CTA"),
        ("Lifecycle-free", "Lifecycle actor"),
        ("Lifecycle-gated", "Lifecycle gated"),
        ("Always-Lock+validity", "Always-Lock"),
        ("Always-Reevaluate", "Always-Reevaluate"),
        ("Rule v2 (post-hoc)", "Rule*"),
    ]
    handles = [
        Line2D(
            [0],
            [0],
            color=CTRL_COLORS[key],
            marker=CTRL_MARKERS[key],
            ls=CTRL_LINESTYLES[key],
            lw=1.4,
            markersize=3.8,
            label=label,
        )
        for key, label in legend_controllers
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.005), ncol=7, frameon=False, columnspacing=0.72, handletextpad=0.35, fontsize=6.3)
    fig.text(0.012, 0.60, "Accuracy (%)", rotation=90, va="center", ha="center", fontsize=8.2)
    fig.subplots_adjust(left=0.055, right=0.99, top=0.94, bottom=0.13)
    save_figure(fig, output_stem)
    plt.close(fig)


def _tapered_band(ax, x0, x1, y0, y1, h0, h1, color, alpha=1.0):
    verts = [
        (x0, y0 - h0 / 2),
        (x0 + 0.38 * (x1 - x0), y0 - h0 / 2),
        (x0 + 0.62 * (x1 - x0), y1 - h1 / 2),
        (x1, y1 - h1 / 2),
        (x1, y1 + h1 / 2),
        (x0 + 0.62 * (x1 - x0), y1 + h1 / 2),
        (x0 + 0.38 * (x1 - x0), y0 + h0 / 2),
        (x0, y0 + h0 / 2),
        (x0, y0 - h0 / 2),
    ]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4, MplPath.LINETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4, MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color, edgecolor="none", alpha=alpha))


def build_evidence_tree(flow_df, writes_df, output_stem: Path) -> None:
    """Evidence-chain tree from eligible Preserve rows to executed consequences."""
    apply_style()
    fig, axes = plt.subplots(3, 1, figsize=(7.05, 4.75), sharex=True)
    for ax, model in zip(axes, MODELS):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        display = MODEL_LABELS[model]
        generic_flow = flow_df[(flow_df["model"] == model) & (flow_df["controller"] == "Generic")].iloc[0]
        cta_flow = flow_df[(flow_df["model"] == model) & (flow_df["controller"] == "CTA")].iloc[0]
        generic_write = writes_df[(writes_df["model"] == model) & (writes_df["controller"] == "Generic")].iloc[0]
        cta_write = writes_df[(writes_df["model"] == model) & (writes_df["controller"] == "CTA")].iloc[0]
        n = int(generic_flow["shared_eligible"])
        sub = int(generic_flow["substitutions"])
        retained = n - sub
        cta_n = int(cta_flow["shared_eligible"])
        other_generic = int(generic_write["non_core_wrong_writes"])
        other_cta = int(cta_write["non_core_wrong_writes"])

        ax.text(0.008, 0.78, display, ha="left", va="center", fontsize=8.4, color=COLORS["primary"], weight="semibold")
        ax.text(0.008, 0.48, f"shared eligible\n$n={n}$", ha="left", va="center", fontsize=6.4, color=COLORS["muted_ink"])
        ax.add_patch(Rectangle((0.12, 0.38), 0.105, 0.26, facecolor="white", edgecolor=COLORS["ink"], lw=0.75))
        ax.text(0.1725, 0.51, "correct bind\nchanged winner\nold target valid", ha="center", va="center", fontsize=6.0)

        _tapered_band(ax, 0.225, 0.43, 0.57, 0.70, 0.095, 0.08, COLORS["coral"], 0.95)
        _tapered_band(ax, 0.225, 0.43, 0.45, 0.30, 0.095, 0.08, COLORS["primary"], 0.95)
        ax.text(0.33, 0.78, "Generic", ha="center", va="bottom", fontsize=6.4, weight="semibold")
        ax.text(0.33, 0.18, "CTA", ha="center", va="top", fontsize=6.4, weight="semibold")

        sub_h = 0.055 + 0.09 * (sub / n)
        retained_h = 0.04 + 0.07 * (retained / n)
        _tapered_band(ax, 0.43, 0.66, 0.70, 0.80, 0.07, sub_h, COLORS["coral"], 0.95)
        _tapered_band(ax, 0.43, 0.66, 0.70, 0.58, 0.07, retained_h, COLORS["neutral"], 1.0)
        _tapered_band(ax, 0.43, 0.66, 0.30, 0.30, 0.075, 0.09, COLORS["primary"], 0.95)
        ax.text(0.665, 0.80, f"substituted {sub}/{n}", ha="left", va="center", fontsize=6.6, color=COLORS["coral"], weight="semibold")
        ax.text(0.665, 0.58, f"retained / other {retained}/{n}", ha="left", va="center", fontsize=6.3)
        ax.text(0.665, 0.30, f"substituted 0/{cta_n}", ha="left", va="center", fontsize=6.6, color=COLORS["primary"], weight="semibold")

        ax.add_patch(FancyArrowPatch((0.80, 0.80), (0.90, 0.80), arrowstyle="-|>", mutation_scale=7, lw=0.8, color=COLORS["coral"]))
        ax.add_patch(FancyArrowPatch((0.80, 0.30), (0.90, 0.30), arrowstyle="-|>", mutation_scale=7, lw=0.8, color=COLORS["primary"]))
        ax.text(0.85, 0.86, "fixed executor", ha="center", va="bottom", fontsize=5.8, color=COLORS["muted_ink"])
        ax.text(0.91, 0.80, f"{sub} TRI writes\n+ {other_generic} other", ha="left", va="center", fontsize=6.5, color=COLORS["coral"], weight="semibold")
        ax.text(0.91, 0.30, f"0 TRI writes\n+ {other_cta} other", ha="left", va="center", fontsize=6.5, color=COLORS["primary"], weight="semibold")
        ax.axhline(0.03, color=COLORS["grid"], lw=0.55, ls=(0, (3, 3)))

    fig.text(0.172, 0.985, "conditioning", ha="center", va="top", fontsize=7.0, color=COLORS["muted_ink"], weight="semibold")
    fig.text(0.54, 0.985, "observed target after refresh", ha="center", va="top", fontsize=7.0, color=COLORS["muted_ink"], weight="semibold")
    fig.text(0.93, 0.985, "executed consequence", ha="center", va="top", fontsize=7.0, color=COLORS["muted_ink"], weight="semibold")
    fig.subplots_adjust(left=0.02, right=0.985, top=0.94, bottom=0.025, hspace=0.02)
    save_figure(fig, output_stem)
    plt.close(fig)


def _source_gain_matrix(source_df, model: str) -> tuple[list[str], np.ndarray]:
    labels = ["Agent\nPair", "Agent\nE2E", "STATE\nPair", "STATE\nE2E", "Tool\nPair", "Tool\nE2E"]
    values = []
    for source in ["AgentDojo", "STATE-Bench", "ToolSandbox"]:
        for metric in ["pairacc", "e2e"]:
            rows = source_df[(source_df["source_slice"] == source) & (source_df["model"] == model) & (source_df["metric"] == metric)]
            h = float(rows[rows["condition"] == "history_only"]["rate_pct"].iloc[0])
            d = float(rows[rows["condition"] == "decision_visible"]["rate_pct"].iloc[0])
            values.append(d - h)
    return labels, np.array(values)


def build_transfer_radar(source_df, gains_df, output_stem: Path) -> None:
    """Source-specific radar fingerprints paired with exact overall confidence intervals."""
    apply_style()
    fig = plt.figure(figsize=(7.05, 4.75))
    gs = GridSpec(2, 3, height_ratios=[2.1, 1.55], hspace=0.42, wspace=0.36, figure=fig)
    min_gain, max_gain = -10.0, 50.0
    theta = np.linspace(0, 2 * np.pi, 6, endpoint=False)
    closed_theta = np.r_[theta, theta[0]]

    for idx, model in enumerate(MODELS):
        ax = fig.add_subplot(gs[0, idx], projection="polar")
        labels, values = _source_gain_matrix(source_df, model)
        radial = (values - min_gain) / (max_gain - min_gain)
        closed = np.r_[radial, radial[0]]
        ax.plot(closed_theta, closed, color=COLORS["primary"], lw=1.55, marker=MODEL_MARKERS[model], markersize=3.8)
        ax.fill(closed_theta, closed, color=COLORS["primary"], alpha=0.12)
        zero_r = (0 - min_gain) / (max_gain - min_gain)
        ax.plot(closed_theta, np.repeat(zero_r, 7), color=COLORS["coral"], lw=0.8, ls=(0, (3, 2)))
        ax.set_xticks(theta)
        ax.set_xticklabels(labels, fontsize=5.8)
        ax.set_ylim(0, 1)
        ticks = [-10, 0, 20, 40]
        ax.set_yticks([(v - min_gain) / (max_gain - min_gain) for v in ticks])
        ax.set_yticklabels([str(v) for v in ticks], fontsize=5.4, color=COLORS["muted_ink"])
        ax.set_rlabel_position(90)
        ax.grid(color=COLORS["grid"], lw=0.45, alpha=0.65)
        ax.spines["polar"].set_color(COLORS["grid"])
        ax.spines["polar"].set_linewidth(0.6)
        ax.set_title(MODEL_LABELS[model], fontsize=8.0, weight="semibold", pad=8)
        for angle, r, val in zip(theta, radial, values):
            ax.text(angle, min(1.03, max(0.06, r + 0.08)), f"{val:+.0f}", ha="center", va="center", fontsize=5.4, color=COLORS["ink"])

    source_gains = gains_df[gains_df["audit_id"] == "revision_source_grounded"].copy()
    metrics = [("changed_pairacc", "Changed PairAcc"), ("actionable_e2e", "Actionable E2E")]
    for col, (metric, title) in enumerate(metrics):
        ax = fig.add_subplot(gs[1, col:col + 2] if col == 0 else gs[1, 2])
        rows = source_gains[source_gains["metric"] == metric]
        y = np.arange(3)[::-1]
        for yi, model in zip(y, MODELS):
            row = rows[rows["model"] == model].iloc[0]
            value = float(row["difference_pp"])
            low = float(row["ci95_low_pp"])
            high = float(row["ci95_high_pp"])
            ax.errorbar(value, yi, xerr=[[value - low], [high - value]], fmt=MODEL_MARKERS[model], markersize=5.0,
                        markerfacecolor=COLORS["primary"], markeredgecolor=COLORS["ink"], markeredgewidth=0.55,
                        ecolor=COLORS["ink"], elinewidth=0.8, capsize=2.2, zorder=3)
            label_x = 61.0 if metric == "changed_pairacc" else 37.0
            ax.text(label_x, yi + 0.18, f"{value:+.1f} [{low:.1f}, {high:.1f}]", ha="right", va="bottom", fontsize=5.8,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.88, pad=0.15))
        ax.axvline(0, color=COLORS["ink"], lw=0.8)
        ax.set_xlim(-15, 62 if metric == "changed_pairacc" else 38)
        ax.set_ylim(-0.65, 2.65)
        ax.set_yticks(y)
        ax.set_yticklabels([MODEL_LABELS[m] for m in MODELS], fontsize=6.8)
        ax.set_title(title, fontsize=7.6, weight="semibold", pad=4)
        ax.set_xlabel("Decision-visible - History-only (pp)", fontsize=6.8)
        ax.grid(axis="x", color=COLORS["grid"], lw=0.45, alpha=0.5)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.tick_params(axis="y", length=0)

    fig.text(0.012, 0.985, "A  source-specific response fingerprint", ha="left", va="top", fontsize=8.0, weight="bold")
    fig.text(0.012, 0.405, "B", ha="left", va="top", fontsize=8.0, weight="bold")
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.10)
    save_figure(fig, output_stem)
    plt.close(fig)


def build_all_distinctive(tables: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    build_authorization_trajectory(output_dir / "fig_authorization_trajectory_tree")
    build_policy_fingerprints(tables["phase"], output_dir / "fig_policy_parallel_fingerprints")
    build_evidence_tree(tables["flow"], tables["writes"], output_dir / "fig_conditional_evidence_tree")
    build_transfer_radar(tables["transfer"], tables["gains"], output_dir / "fig_transfer_radar_forest")
