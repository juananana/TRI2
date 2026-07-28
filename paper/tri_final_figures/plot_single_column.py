from __future__ import annotations

import argparse
import csv
from math import sqrt
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle


COLORS = {
    "ink": "#26343A",
    "muted": "#647278",
    "grid": "#B4BEC2",
    "teal": "#176D75",
    "teal_light": "#E0EFF0",
    "coral": "#C95851",
    "coral_light": "#F5E3E1",
    "amber": "#D58B24",
    "neutral": "#DDE2E4",
    "neutral_dark": "#879399",
    "white": "#FFFFFF",
}

MODELS = ["Qwen3.5", "GLM-5.1", "DeepSeek"]
MODEL_LABELS = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM", "DeepSeek": "DeepSeek"}
MODEL_MARKERS = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}


def apply_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 8.0,
            "axes.labelsize": 8.0,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 8.0,
            "axes.linewidth": 0.7,
            "lines.linewidth": 1.2,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.facecolor": COLORS["white"],
            "axes.facecolor": COLORS["white"],
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.025,
        }
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def row_where(rows: list[dict[str, str]], **conditions: str) -> dict[str, str]:
    matches = [row for row in rows if all(row[key] == value for key, value in conditions.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {conditions}, found {len(matches)}")
    return matches[0]


def save(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    plt.close(fig)


def build_main_trajectory(stem: Path) -> None:
    """Two concrete email requests sharing one refresh and requiring opposite targets."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)

    ax.text(0.1, 7.02, "Same mailbox refresh, opposite correct targets", ha="left", va="top",
            fontsize=8.0, color=COLORS["ink"], weight="bold")

    state_cards = [
        (0.1, 5.55, 3.0, "Before refresh\nA ranks first"),
        (3.8, 5.55, 2.2, "Mailbox\nrefresh"),
        (6.7, 5.55, 3.2, "After refresh\nB ranks first\nA remains valid"),
    ]
    for x, y, width, label in state_cards:
        ax.add_patch(Rectangle((x, y), width, 1.15, facecolor=COLORS["neutral"],
                               edgecolor=COLORS["neutral_dark"], lw=0.6))
        ax.text(x + width / 2, y + 0.58, label, ha="center", va="center", fontsize=8.0,
                color=COLORS["ink"], linespacing=1.15)
    for start, end in ((3.1, 3.8), (6.0, 6.7)):
        ax.add_patch(FancyArrowPatch((start, 6.13), (end, 6.13), arrowstyle="-|>",
                                     mutation_scale=8, lw=0.8, color=COLORS["neutral_dark"]))

    lanes = [
        (3.75, COLORS["coral"], COLORS["coral_light"], "PRESERVE",
         "Choose the highest-priority\nunread email now. Refresh,\nthen reply to it.",
         "bind A\npre-refresh", "Gold: A"),
        (0.85, COLORS["teal"], COLORS["teal_light"], "REEVALUATE",
         "Refresh first. Then choose the\nhighest-priority unread\nemail and reply.",
         "resolve after\nrefresh", "Gold: B"),
    ]
    for y, color, fill, mode, request, decision, gold in lanes:
        ax.text(0.1, y + 1.38, mode, ha="left", va="bottom", fontsize=8.0,
                color=color, weight="bold")
        ax.add_patch(Rectangle((0.1, y), 4.7, 1.25, facecolor=fill, edgecolor=color, lw=0.75))
        ax.text(0.3, y + 0.63, request, ha="left", va="center", fontsize=8.0,
                color=COLORS["ink"], linespacing=1.15)
        ax.add_patch(FancyArrowPatch((4.8, y + 0.63), (7.35, y + 0.63), arrowstyle="-|>",
                                     mutation_scale=8, lw=1.15, color=color))
        ax.text(6.05, y + 0.78, decision, ha="center", va="bottom", fontsize=8.0,
                color=color, linespacing=1.0)
        ax.add_patch(Rectangle((7.35, y), 2.55, 1.25, facecolor=COLORS["white"],
                               edgecolor=color, lw=1.0))
        ax.text(8.63, y + 0.63, gold, ha="center", va="center", fontsize=8.3,
                color=color, weight="bold")

    ax.text(6.05, 3.28, "Observed Generic write: B", ha="center", va="center",
            fontsize=8.0, color=COLORS["coral"], weight="bold")
    ax.add_patch(FancyArrowPatch((7.55, 3.73), (6.95, 3.34), arrowstyle="-|>",
                                 mutation_scale=8, lw=0.9, linestyle=(0, (3, 2)),
                                 color=COLORS["coral"]))

    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, stem)


def build_policy_phase_space(rows: list[dict[str, str]], stem: Path) -> None:
    """Single phase-space plot with controller transitions and changed PairAcc labels."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.20))
    ax.set_xlim(0, 106)
    ax.set_ylim(0, 106)

    ax.add_patch(Rectangle((0, 50), 50, 56, facecolor=COLORS["coral_light"], edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((50, 50), 56, 56, facecolor=COLORS["teal_light"], edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((50, 0), 56, 50, facecolor=COLORS["coral_light"], edgecolor="none", zorder=0))
    ax.axvline(50, color=COLORS["grid"], lw=0.6, ls=(0, (3, 3)))
    ax.axhline(50, color=COLORS["grid"], lw=0.6, ls=(0, (3, 3)))
    ax.text(72, 54, "selective", fontsize=8.0, color=COLORS["teal"], weight="bold")

    for model in ["Qwen3.5", "GLM-5.1"]:
        marker = MODEL_MARKERS[model]
        all_generic = row_where(rows, dataset="v3", model=model, controller="Generic", slice="all")
        all_cta = row_where(rows, dataset="v3", model=model, controller="CTA", slice="all")
        changed_generic = row_where(rows, dataset="v3", model=model, controller="Generic", slice="changed_winner_core")
        changed_cta = row_where(rows, dataset="v3", model=model, controller="CTA", slice="changed_winner_core")
        x0, y0 = float(all_generic["preserve_accuracy_pct"]), float(all_generic["reevaluate_accuracy_pct"])
        x1, y1 = float(all_cta["preserve_accuracy_pct"]), float(all_cta["reevaluate_accuracy_pct"])
        ax.plot([x0, x1], [y0, y1], color=COLORS["neutral_dark"], lw=0.9, zorder=2)
        marker_size = 46 if model == "Qwen3.5" else 34
        marker_zorder = 4 if model == "Qwen3.5" else 5
        ax.scatter(x0, y0, s=marker_size, marker=marker, facecolor=COLORS["coral"], edgecolor=COLORS["ink"], lw=0.65, zorder=marker_zorder)
        if model == "Qwen3.5":
            ax.scatter(x1, y1, s=13, marker=marker, facecolor=COLORS["teal"], edgecolor=COLORS["ink"], lw=0.75, zorder=5)
        else:
            ax.scatter(x1, y1, s=9, marker=marker, facecolor=COLORS["teal"], edgecolor=COLORS["ink"], lw=0.75, zorder=6)
        g_count = int(float(changed_generic["both_correct"]))
        c_count = int(float(changed_cta["both_correct"]))
        if model == "Qwen3.5":
            ax.text(42, 84.5, f"{g_count}$\\rightarrow${c_count}/32", ha="center", va="center", fontsize=8.0)
        else:
            ax.text(62, 73.5, f"{g_count}$\\rightarrow${c_count}/32", ha="center", va="center", fontsize=8.0)

    controls = [(20, 100), (100, 20)]
    for x, y in controls:
        ax.scatter(x, y, s=34, marker="X", facecolor=COLORS["neutral_dark"], edgecolor=COLORS["ink"], lw=0.5, zorder=4)
    ax.text(4, 93, "Always reevaluate\n0/32", ha="left", va="top", fontsize=8.0, color=COLORS["muted"])
    ax.text(62, 19, "Always lock\n0/32", ha="left", va="bottom", fontsize=8.0, color=COLORS["muted"])

    rule_all = row_where(rows, dataset="v3", model="model-independent", controller="Rule v2 (post-hoc)", slice="all")
    rule_changed = row_where(rows, dataset="v3", model="model-independent", controller="Rule v2 (post-hoc)", slice="changed_winner_core")
    rx, ry = float(rule_all["preserve_accuracy_pct"]), float(rule_all["reevaluate_accuracy_pct"])
    ax.scatter(rx, ry, s=24, marker="P", facecolor=COLORS["white"], edgecolor=COLORS["amber"], lw=0.9, zorder=5)
    ax.annotate(
        f"Rule* {int(float(rule_changed['both_correct']))}/32",
        (rx, ry),
        xytext=(94, 86),
        textcoords="data",
        fontsize=8.0,
        color=COLORS["amber"],
        ha="right",
        arrowprops=dict(arrowstyle="-", color=COLORS["amber"], lw=0.6),
    )

    ax.set_xlabel("Preserve accuracy (%)")
    ax.set_ylabel("Reevaluate accuracy (%)")
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.grid(color=COLORS["grid"], lw=0.35, alpha=0.35)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["white"], markeredgecolor=COLORS["ink"], markersize=4.5, label="Qwen"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["white"], markeredgecolor=COLORS["ink"], markersize=4.5, label="GLM"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["coral"], markeredgecolor=COLORS["ink"], markersize=4.5, label="Generic"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["teal"], markeredgecolor=COLORS["ink"], markersize=4.5, label="CTA"),
    ]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=4, frameon=False, columnspacing=0.75, handletextpad=0.25)
    fig.subplots_adjust(left=0.17, right=0.98, top=0.88, bottom=0.16)
    save(fig, stem)


def wilson_interval(successes: int, total: int, z: float = 1.959964) -> tuple[float, float, float]:
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return p * 100, max(0, center - half) * 100, min(1, center + half) * 100


def build_substitution_dumbbell(rows: list[dict[str, str]], stem: Path) -> None:
    """Shared-eligible Generic-to-CTA substitution transition with Wilson intervals."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.42))
    y_positions = [2, 1, 0]
    for y, model in zip(y_positions, MODELS):
        generic = row_where(rows, model=model, controller="Generic")
        cta = row_where(rows, model=model, controller="CTA")
        n = int(generic["shared_eligible"])
        g_count = int(generic["substitutions"])
        c_count = int(cta["substitutions"])
        g_rate, g_low, g_high = wilson_interval(g_count, n)
        c_rate, c_low, c_high = wilson_interval(c_count, n)
        ax.plot([c_rate, g_rate], [y, y], color=COLORS["neutral_dark"], lw=1.25, zorder=1)
        ax.errorbar(g_rate, y, xerr=[[max(0, g_rate - g_low)], [max(0, g_high - g_rate)]], fmt="o", ms=5.2,
                    mfc=COLORS["coral"], mec=COLORS["ink"], mew=0.55, ecolor=COLORS["coral"], elinewidth=1.0, capsize=2.2, zorder=3)
        ax.errorbar(c_rate, y, xerr=[[max(0, c_rate - c_low)], [max(0, c_high - c_rate)]], fmt="s", ms=4.8,
                    mfc=COLORS["teal"], mec=COLORS["ink"], mew=0.55, ecolor=COLORS["teal"], elinewidth=1.0, capsize=2.2, zorder=3)
        ax.text(g_rate + 3.0, y + 0.12, f"{g_count}/{n}", ha="left", va="bottom", fontsize=8.0, color=COLORS["coral"], weight="bold")
        ax.text(1.2, y - 0.16, f"0/{n}", ha="left", va="top", fontsize=8.0, color=COLORS["teal"], weight="bold")

    for y in (1.5, 0.5):
        ax.axhline(y, color=COLORS["grid"], lw=0.45, ls=(0, (3, 3)), alpha=0.7, zorder=0)
    ax.axvline(0, color=COLORS["ink"], lw=0.7)
    ax.set_xlim(-2, 91)
    ax.set_ylim(-0.55, 2.55)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([MODEL_LABELS[m] for m in MODELS])
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_xlabel("Refreshed-winner substitution (%)")
    ax.grid(axis="x", color=COLORS["grid"], lw=0.4, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=5)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["coral"], markeredgecolor=COLORS["ink"], markersize=4.8, label="Generic"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=COLORS["teal"], markeredgecolor=COLORS["ink"], markersize=4.6, label="CTA"),
    ]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2, frameon=False, columnspacing=1.1, handletextpad=0.35)
    fig.subplots_adjust(left=0.24, right=0.97, top=0.84, bottom=0.22)
    save(fig, stem)


def build_wrong_write_bars(rows: list[dict[str, str]], stem: Path) -> None:
    """Compact complete wrong-write attribution for Generic and CTA."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.72))
    positions = [5.15, 4.42, 3.10, 2.37, 1.05, 0.32]
    labels: list[str] = []
    idx = 0
    for model in MODELS:
        for controller, short in [("Generic", "G"), ("CTA", "CTA")]:
            row = row_where(rows, dataset="v7", model=model, controller=controller)
            core = int(row["core_substitution_writes"])
            other = int(row["non_core_wrong_writes"])
            total = int(row["all_wrong_writes"])
            y = positions[idx]
            ax.barh(y, core, height=0.43, color=COLORS["coral"], edgecolor="none")
            ax.barh(y, other, left=core, height=0.43, color=COLORS["neutral"], edgecolor=COLORS["neutral_dark"], lw=0.45)
            if core:
                ax.text(core / 2, y, str(core), ha="center", va="center", fontsize=8.0, color=COLORS["white"], weight="bold")
            else:
                ax.text(other / 2, y, "0 TRI", ha="center", va="center", fontsize=8.0, color=COLORS["coral"], weight="bold")
            ax.text(total + 1.5, y, str(total), ha="left", va="center", fontsize=8.0, color=COLORS["ink"])
            labels.append(f"{MODEL_LABELS[model]}  {short}")
            idx += 1

    for y in (3.76, 1.71):
        ax.axhline(y, color=COLORS["grid"], lw=0.55, ls=(0, (3, 3)))
    ax.set_xlim(0, 65)
    ax.set_ylim(-0.05, 5.58)
    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.set_xticks([0, 20, 40, 60])
    ax.set_xlabel("Wrong-target writes (count)")
    ax.grid(axis="x", color=COLORS["grid"], lw=0.4, alpha=0.45)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=4)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    legend = [
        Rectangle((0, 0), 1, 1, facecolor=COLORS["coral"], label="TRI substitution write"),
        Rectangle((0, 0), 1, 1, facecolor=COLORS["neutral"], edgecolor=COLORS["neutral_dark"], label="Other wrong write"),
    ]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2, frameon=False, columnspacing=0.8, handlelength=1.2, handletextpad=0.35)
    fig.subplots_adjust(left=0.27, right=0.97, top=0.85, bottom=0.19)
    save(fig, stem)


def build_visibility_forest(rows: list[dict[str, str]], stem: Path) -> None:
    """One claim-focused forest plot across authored and transfer evidence."""
    apply_style()
    selected = [
        ("revision_full_diagnostic", "changed_pairacc", "Qwen3.5", 7.0),
        ("revision_full_diagnostic", "changed_pairacc", "GLM-5.1", 6.1),
        ("revision_human_rewrite", "actionable_e2e", "Qwen3.5", 4.45),
        ("revision_human_rewrite", "actionable_e2e", "GLM-5.1", 3.55),
        ("revision_source_grounded", "actionable_e2e", "Qwen3.5", 1.9),
        ("revision_source_grounded", "actionable_e2e", "GLM-5.1", 1.0),
        ("revision_source_grounded", "actionable_e2e", "DeepSeek", 0.1),
    ]
    fig, ax = plt.subplots(figsize=(3.35, 3.50))
    y_ticks = []
    y_labels = []
    for audit_id, metric, model, y in selected:
        row = row_where(rows, audit_id=audit_id, metric=metric, model=model)
        value = float(row["difference_pp"])
        low = float(row["ci95_low_pp"])
        high = float(row["ci95_high_pp"])
        marker = MODEL_MARKERS[model]
        ax.errorbar(
            value,
            y,
            xerr=[[value - low], [high - value]],
            fmt=marker,
            ms=5.0,
            mfc=COLORS["teal"],
            mec=COLORS["ink"],
            mew=0.6,
            ecolor=COLORS["ink"],
            elinewidth=0.8,
            capsize=2.1,
            zorder=3,
        )
        ax.text(
            91,
            y,
            f"{value:+.1f}",
            ha="right",
            va="center",
            fontsize=8.0,
            color=COLORS["ink"],
            bbox=dict(facecolor=COLORS["white"], edgecolor="none", alpha=0.92, pad=0.15),
        )
        y_ticks.append(y)
        y_labels.append(MODEL_LABELS[model])

    ax.text(-18.5, 7.55, "Authored diagnostic / changed PairAcc", ha="left", va="bottom", fontsize=8.0, color=COLORS["muted"], weight="bold")
    ax.text(-18.5, 5.32, "Human rewrite / actionable E2E", ha="left", va="bottom", fontsize=8.0, color=COLORS["muted"], weight="bold")
    ax.text(-18.5, 2.70, "Source-derived / actionable E2E", ha="left", va="bottom", fontsize=8.0, color=COLORS["muted"], weight="bold")
    ax.axhline(5.78, color=COLORS["grid"], lw=0.55, ls=(0, (3, 3)))
    ax.axhline(3.15, color=COLORS["grid"], lw=0.55, ls=(0, (3, 3)))
    ax.axvline(0, color=COLORS["ink"], lw=0.8)
    ax.set_xlim(-20, 94)
    ax.set_ylim(-0.45, 8.0)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xticks([-20, 0, 20, 40, 60, 80])
    ax.set_xlabel("Decision-visible - History-only (percentage points)")
    ax.grid(axis="x", color=COLORS["grid"], lw=0.4, alpha=0.45)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=5)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.subplots_adjust(left=0.27, right=0.98, top=0.98, bottom=0.17)
    save(fig, stem)


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Generate compact single-column TRI figures.")
    parser.add_argument("--data-dir", type=Path, default=root / "data" / "summary_csv")
    parser.add_argument("--output-dir", type=Path, default=root / "outputs" / "single_column")
    parser.add_argument("--version-suffix", default="_v2")
    args = parser.parse_args()

    phase = read_csv(args.data_dir / "matched_pairacc_and_marginals.csv")
    flow = read_csv(args.data_dir / "v7_shared_eligible_pairacc_and_substitution.csv")
    writes = read_csv(args.data_dir / "v7_e2e_wrong_writes.csv")
    gains = read_csv(args.data_dir / "revision_decision_visible_gains.csv")

    suffix = args.version_suffix
    build_main_trajectory(args.output_dir / f"fig1_referent_trajectory{suffix}")
    build_policy_phase_space(phase, args.output_dir / f"fig2_policy_phase_space{suffix}")
    build_substitution_dumbbell(flow, args.output_dir / f"fig3_shared_eligible_substitution{suffix}")
    build_wrong_write_bars(writes, args.output_dir / f"fig4_wrong_write_attribution{suffix}")
    build_visibility_forest(gains, args.output_dir / f"fig5_decision_visibility_forest{suffix}")


if __name__ == "__main__":
    main()
