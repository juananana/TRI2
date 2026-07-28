from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle

from plot_round8_figures import (
    AMBER,
    BLUE,
    CORAL,
    GRAY_LIGHT,
    GRID,
    INK,
    MODEL_LABELS,
    MODEL_MARKERS,
    MODELS,
    MUTED,
    PAPER,
    TEAL,
    TEAL_LIGHT,
    apply_style,
    read_csv,
    row_where,
    save,
    validate_paired_scores,
)
from plot_round4_figures import wilson_interval


MODEL_COLORS = {"Qwen3.5": BLUE, "GLM-5.1": AMBER, "DeepSeek": TEAL}


def build_policy_phase_map(rows: list[dict[str, str]], stem: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.75))
    ax.add_patch(Rectangle((75, 75), 28, 28, facecolor=TEAL_LIGHT, edgecolor="none", alpha=0.55, zorder=0))

    def point(controller: str, model: str) -> tuple[float, float, int]:
        all_row = row_where(rows, dataset="v3", model=model, controller=controller, slice="all")
        changed = row_where(rows, dataset="v3", model=model, controller=controller, slice="changed_winner_core")
        return (
            float(all_row["preserve_accuracy_pct"]),
            float(all_row["reevaluate_accuracy_pct"]),
            int(float(changed["both_correct"])),
        )

    entries = [
        ("Always-Lock+validity", "model-independent", MUTED, "v", False),
        ("Always-Reevaluate", "model-independent", MUTED, "^", False),
        ("Generic", "Qwen3.5", CORAL, "o", True),
        ("Generic", "GLM-5.1", CORAL, "s", True),
        ("Rule v2 (post-hoc)", "model-independent", AMBER, "P", True),
        ("CTA", "Qwen3.5", TEAL, "o", True),
        ("CTA", "GLM-5.1", TEAL, "s", True),
    ]
    locations: dict[tuple[str, str], tuple[float, float, int]] = {}
    for controller, model, color, marker, filled in entries:
        x, y, pair = point(controller, model)
        locations[(controller, model)] = (x, y, pair)
        ax.scatter(
            x,
            y,
            s=42 if controller == "CTA" else 35,
            marker=marker,
            facecolor=color if filled else PAPER,
            edgecolor=color,
            linewidth=0.9,
            zorder=4,
        )

    annotations = [
        (("Always-Lock+validity", "model-independent"), "Lock\n0/32", (85, 26)),
        (("Always-Reevaluate", "model-independent"), "Re-eval\n0/32", (29, 87)),
        (("Generic", "Qwen3.5"), "Generic·Q\n3/32", (41, 97)),
        (("Generic", "GLM-5.1"), "Generic·G\n7/32", (58, 77)),
        (("Rule v2 (post-hoc)", "model-independent"), "Rule*\n28/32", (72, 86)),
    ]
    for key, label, text_position in annotations:
        x, y, _ = locations[key]
        ax.annotate(
            label,
            xy=(x, y),
            xytext=text_position,
            textcoords="data",
            ha="center",
            va="center",
            fontsize=6.9,
            color=INK if "Rule" not in label else AMBER,
            weight="bold",
            arrowprops={"arrowstyle": "-", "color": GRID, "lw": 0.7},
            zorder=5,
        )

    cta_q = locations[("CTA", "Qwen3.5")]
    cta_g = locations[("CTA", "GLM-5.1")]
    ax.annotate(
        "CTA·Q/G\n30/32 · 31/32",
        xy=((cta_q[0] + cta_g[0]) / 2, (cta_q[1] + cta_g[1]) / 2),
        xytext=(67, 99),
        ha="center",
        va="center",
        fontsize=6.9,
        color=TEAL,
        weight="bold",
        arrowprops={"arrowstyle": "-", "color": TEAL, "lw": 0.7},
        zorder=5,
    )

    ax.set_xlim(15, 103)
    ax.set_ylim(15, 103)
    ax.set_xticks([20, 40, 60, 80, 100])
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_xlabel("Preserve accuracy (%)")
    ax.set_ylabel("Reevaluate accuracy (%)")
    ax.grid(color=GRID, lw=0.45, alpha=0.75)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.subplots_adjust(left=0.18, right=0.985, top=0.98, bottom=0.18)
    save(fig, stem)


def build_cross_schema_endpoints(rows: list[dict[str, str]], stem: Path) -> None:
    apply_style()
    fig, (ax, pair_ax) = plt.subplots(
        2,
        1,
        figsize=(3.35, 3.75),
        gridspec_kw={"height_ratios": [2.05, 1.15], "hspace": 0.42},
    )
    ax.axhspan(0, 6, color=TEAL_LIGHT, alpha=0.65, zorder=0)
    offsets = {"Qwen3.5": -0.045, "GLM-5.1": 0.0, "DeepSeek": 0.045}

    for model in MODELS:
        generic = row_where(rows, model=model, controller="Generic")
        cta = row_where(rows, model=model, controller="CTA")
        n = int(generic["shared_eligible"])
        generic_count = int(generic["substitutions"])
        cta_count = int(cta["substitutions"])
        if int(cta["shared_eligible"]) != n:
            raise ValueError(f"Mismatched shared denominator for {model}")
        generic_rate, generic_low, generic_high = wilson_interval(generic_count, n)
        cta_rate, cta_low, cta_high = wilson_interval(cta_count, n)
        x0, x1 = 0 + offsets[model], 1 + offsets[model]
        color = MODEL_COLORS[model]
        marker = MODEL_MARKERS[model]
        ax.plot([x0, x1], [generic_rate, cta_rate], color=color, lw=1.25, alpha=0.9, zorder=2)
        ax.errorbar(
            x0,
            generic_rate,
            yerr=[[max(0.0, generic_rate - generic_low)], [max(0.0, generic_high - generic_rate)]],
            fmt=marker,
            ms=5.7,
            mfc=color,
            mec=color,
            ecolor=color,
            elinewidth=0.9,
            capsize=2.2,
            zorder=4,
        )
        ax.errorbar(
            x1,
            cta_rate,
            yerr=[[max(0.0, cta_rate - cta_low)], [max(0.0, cta_high - cta_rate)]],
            fmt=marker,
            ms=5.7,
            mfc=PAPER,
            mec=color,
            mew=1.0,
            ecolor=color,
            elinewidth=0.9,
            capsize=2.2,
            zorder=4,
        )
        ax.text(
            x0 - 0.065,
            generic_rate,
            f"{MODEL_LABELS[model]}  {generic_count}/{n}",
            ha="right",
            va="center",
            fontsize=7.0,
            color=color,
            weight="bold",
        )

    ax.set_xlim(-0.52, 1.28)
    ax.set_ylim(-2, 86)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Generic", "CTA"], weight="bold")
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.set_ylabel("Conditional substitution (%)")
    ax.set_title("A  Post-binding substitution", loc="left", fontsize=8.2, weight="bold", pad=2)
    ax.grid(axis="y", color=GRID, lw=0.45, alpha=0.75)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "bottom"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=5)
    pair_y = {"Qwen3.5": 2, "GLM-5.1": 1, "DeepSeek": 0}
    for model in MODELS:
        generic = row_where(rows, model=model, controller="Generic")
        cta = row_where(rows, model=model, controller="CTA")
        generic_x = float(generic["pairacc_pct"])
        cta_x = float(cta["pairacc_pct"])
        generic_low = float(generic["pairacc_ci95_low_pct"])
        generic_high = float(generic["pairacc_ci95_high_pct"])
        cta_low = float(cta["pairacc_ci95_low_pct"])
        cta_high = float(cta["pairacc_ci95_high_pct"])
        y = pair_y[model]
        color = MODEL_COLORS[model]
        marker = MODEL_MARKERS[model]
        pair_ax.plot([generic_x, cta_x], [y, y], color=color, lw=1.15, zorder=1)
        pair_ax.errorbar(
            generic_x,
            y,
            xerr=[[generic_x - generic_low], [generic_high - generic_x]],
            fmt=marker,
            ms=5.0,
            mfc=PAPER,
            mec=color,
            mew=1.0,
            ecolor=color,
            elinewidth=0.8,
            capsize=2.0,
            zorder=3,
        )
        pair_ax.errorbar(
            cta_x,
            y,
            xerr=[[cta_x - cta_low], [cta_high - cta_x]],
            fmt=marker,
            ms=5.0,
            mfc=color,
            mec=color,
            ecolor=color,
            elinewidth=0.8,
            capsize=2.0,
            zorder=3,
        )
        pair_ax.text(
            104,
            y,
            f"{generic['pairacc_both_correct']}→{cta['pairacc_both_correct']}/80",
            ha="right",
            va="center",
            fontsize=6.8,
            color=color,
            weight="bold",
        )

    pair_ax.set_xlim(-4, 108)
    pair_ax.set_ylim(-0.55, 2.55)
    pair_ax.set_yticks([2, 1, 0])
    pair_ax.set_yticklabels(["Qwen", "GLM", "DeepSeek"], fontsize=7.0, weight="bold")
    pair_ax.set_xticks([0, 25, 50, 75, 100])
    pair_ax.set_xlabel("Changed-winner PairAcc (%)")
    pair_ax.set_title("B  Joint success", loc="left", fontsize=8.2, weight="bold", pad=2)
    pair_ax.grid(axis="x", color=GRID, lw=0.45, alpha=0.75)
    pair_ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        pair_ax.spines[spine].set_visible(False)
    pair_ax.tick_params(axis="y", length=0)
    generic_handle = Line2D([0], [0], marker="o", color=MUTED, markerfacecolor=PAPER, markeredgecolor=MUTED, markersize=4.5, label="Generic")
    cta_handle = Line2D([0], [0], marker="o", color=MUTED, markerfacecolor=MUTED, markeredgecolor=MUTED, markersize=4.5, label="CTA")
    pair_ax.legend(handles=[generic_handle, cta_handle], loc="lower center", bbox_to_anchor=(0.5, 1.00), frameon=False, ncol=2, handletextpad=0.3, columnspacing=0.8)

    fig.subplots_adjust(left=0.22, right=0.98, top=0.96, bottom=0.12)
    save(fig, stem)


def ribbon(
    ax: plt.Axes,
    x0: float,
    x1: float,
    y0_low: float,
    y0_high: float,
    y1_low: float,
    y1_high: float,
    color: str,
) -> None:
    control = (x1 - x0) * 0.45
    vertices = [
        (x0, y0_low),
        (x0 + control, y0_low),
        (x1 - control, y1_low),
        (x1, y1_low),
        (x1, y1_high),
        (x1 - control, y1_high),
        (x0 + control, y0_high),
        (x0, y0_high),
        (x0, y0_low),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    ax.add_patch(PathPatch(MplPath(vertices, codes), facecolor=color, edgecolor="none", alpha=0.78, zorder=1))


def build_sqlite_alluvial(rows: list[dict[str, str]], stem: Path) -> None:
    apply_style()
    fig = plt.figure(figsize=(3.35, 3.68))
    ax = fig.add_axes([0.01, 0.27, 0.98, 0.72])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    category_defs = [
        ("correct_final_state", "Correct", TEAL),
        ("core_tri_write", "TRI", CORAL),
        ("fallback_wrong_write", "Fallback", AMBER),
        ("unneeded_reject", "Reject", MUTED),
    ]
    panel_centers = {"Qwen3.5": 0.70, "GLM-5.1": 0.27}
    x0, x1 = 0.22, 0.72
    scale = 0.0060
    gap = 0.012

    for model in ("Qwen3.5", "GLM-5.1"):
        row = row_where(rows, model=model, controller="Generic")
        total = int(row["tasks"])
        values = [(key, label, color, int(row[key])) for key, label, color in category_defs if int(row[key]) > 0]
        if sum(value for _, _, _, value in values) != total:
            raise ValueError(f"SQLite outcomes do not sum to {total}: {row}")
        center = panel_centers[model]
        total_height = total * scale
        source_bottom = center - total_height / 2
        source_cursor = source_bottom
        target_total = total_height + gap * (len(values) - 1)
        target_cursor = center + target_total / 2

        ax.plot([x0, x0], [source_bottom, source_bottom + total_height], color=BLUE, lw=3.4, solid_capstyle="butt", zorder=3)
        ax.text(0.025, center + 0.02, MODEL_LABELS[model], ha="left", va="center", fontsize=8.2, color=INK, weight="bold")
        ax.text(0.025, center - 0.035, f"n={total}", ha="left", va="center", fontsize=7.1, color=MUTED)

        for key, label, color, value in values:
            height = value * scale
            source_low, source_high = source_cursor, source_cursor + height
            target_high, target_low = target_cursor, target_cursor - height
            ribbon(ax, x0, x1, source_low, source_high, target_low, target_high, color)
            ax.plot([x1, x1], [target_low, target_high], color=color, lw=3.4, solid_capstyle="butt", zorder=3)
            if key == "core_tri_write":
                strict_opportunities = int(row["strict_core_opportunities"])
                text = f"{label} {value} ({value}/{strict_opportunities})"
            else:
                text = f"{label} {value}"
            ax.text(0.755, (target_low + target_high) / 2, text, ha="left", va="center", fontsize=7.0, color=color, weight="bold")
            source_cursor = source_high
            target_cursor = target_low - gap

    ax.plot([0.02, 0.98], [0.485, 0.485], color=GRID, lw=0.55, ls=(0, (3, 3)))

    calibration_ax = fig.add_axes([0.20, 0.07, 0.75, 0.16])
    calibration_ax.set_title("B  Strict opportunity check", loc="left", fontsize=8.0, weight="bold", pad=1)
    for model, offset in (("Qwen3.5", -0.035), ("GLM-5.1", 0.035)):
        row = row_where(rows, model=model, controller="Generic")
        stable_count = int(row["stable_writes"])
        stable_n = int(row["stable_opportunities"])
        changed_count = int(row["strict_core_writes"])
        changed_n = int(row["strict_core_opportunities"])
        stable_rate, stable_low, stable_high = wilson_interval(stable_count, stable_n)
        changed_rate, changed_low, changed_high = wilson_interval(changed_count, changed_n)
        color = MODEL_COLORS[model]
        marker = MODEL_MARKERS[model]
        x0, x1 = 0 + offset, 1 + offset
        calibration_ax.plot([x0, x1], [stable_rate, changed_rate], color=color, lw=1.0, zorder=1)
        calibration_ax.errorbar(
            x0,
            stable_rate,
            yerr=[[max(0.0, stable_rate - stable_low)], [max(0.0, stable_high - stable_rate)]],
            fmt=marker,
            ms=4.4,
            mfc=PAPER,
            mec=color,
            ecolor=color,
            elinewidth=0.7,
            capsize=1.8,
            zorder=3,
        )
        calibration_ax.errorbar(
            x1,
            changed_rate,
            yerr=[[max(0.0, changed_rate - changed_low)], [max(0.0, changed_high - changed_rate)]],
            fmt=marker,
            ms=4.4,
            mfc=color,
            mec=color,
            ecolor=color,
            elinewidth=0.7,
            capsize=1.8,
            zorder=3,
        )
        calibration_ax.text(x1 + 0.08, changed_rate, f"{MODEL_LABELS[model]} {changed_count}/{changed_n}", ha="left", va="center", fontsize=6.6, color=color, weight="bold")
    calibration_ax.text(-0.10, 4, "0/4", ha="right", va="center", fontsize=6.6, color=MUTED, weight="bold")
    calibration_ax.set_xlim(-0.25, 1.45)
    calibration_ax.set_ylim(-5, 112)
    calibration_ax.set_xticks([0, 1])
    calibration_ax.set_xticklabels(["Stable", "Changed"], fontsize=7.0, weight="bold")
    calibration_ax.set_yticks([0, 50, 100])
    calibration_ax.set_ylabel("Write (%)", fontsize=7.0)
    calibration_ax.grid(axis="y", color=GRID, lw=0.4, alpha=0.7)
    calibration_ax.set_axisbelow(True)
    for spine in ("top", "right", "bottom"):
        calibration_ax.spines[spine].set_visible(False)
    calibration_ax.tick_params(axis="x", length=0)
    save(fig, stem)


def build_effect_phase_map(rows: list[dict[str, str]], stem: Path) -> None:
    apply_style()
    validate_paired_scores(rows)
    fig, ax = plt.subplots(figsize=(3.35, 2.85))
    ax.add_patch(Rectangle((0, 0), 82, 35, facecolor=TEAL_LIGHT, edgecolor="none", alpha=0.50, zorder=0))
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.axhline(0, color=MUTED, lw=0.8)

    entries = [
        ("Authored", "Qwen3.5", "Auth·Q", BLUE, True, (3, -12)),
        ("Authored", "GLM-5.1", "Auth·G", BLUE, True, (3, 3)),
        ("Source-derived", "Qwen3.5", "Source·Q", TEAL, False, (3, -10)),
        ("Source-derived", "GLM-5.1", "Source·G", TEAL, False, (-37, 3)),
        ("Source-derived", "DeepSeek", "Source·D", TEAL, False, (-5, 8)),
    ]
    for dataset, model, label, color, filled, offset in entries:
        pair = row_where(rows, panel="pairacc", dataset=dataset, model=model)
        e2e = row_where(rows, panel="e2e", dataset=dataset, model=model)
        x = float(pair["difference_pp"])
        x_low, x_high = float(pair["ci95_low_pp"]), float(pair["ci95_high_pp"])
        y = float(e2e["difference_pp"])
        y_low, y_high = float(e2e["ci95_low_pp"]), float(e2e["ci95_high_pp"])
        marker = MODEL_MARKERS[model]
        ax.errorbar(
            x,
            y,
            xerr=[[x - x_low], [x_high - x]],
            yerr=[[y - y_low], [y_high - y]],
            fmt=marker,
            ms=6.0,
            mfc=color if filled else PAPER,
            mec=color,
            mew=1.0,
            ecolor=color,
            elinewidth=0.85,
            capsize=2.0,
            alpha=0.95,
            zorder=4,
        )
        ax.annotate(
            label,
            xy=(x, y),
            xytext=offset,
            textcoords="offset points",
            fontsize=6.8,
            color=color,
            weight="bold",
            ha="left" if offset[0] >= 0 else "right",
            va="bottom" if offset[1] >= 0 else "top",
        )

    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=BLUE, markeredgecolor=BLUE, markersize=5.2, label="Authored"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PAPER, markeredgecolor=TEAL, markersize=5.2, label="Source-derived"),
    ]
    ax.legend(handles=handles, loc="upper left", frameon=False, ncol=2, handletextpad=0.35, columnspacing=0.9)
    ax.set_xlim(-15, 82)
    ax.set_ylim(-10, 36)
    ax.set_xticks([-10, 0, 20, 40, 60, 80])
    ax.set_yticks([-10, 0, 10, 20, 30])
    ax.set_xlabel("PairAcc effect (pp)")
    ax.set_ylabel("Actionable E2E effect (pp)")
    ax.grid(color=GRID, lw=0.45, alpha=0.75)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.subplots_adjust(left=0.20, right=0.985, top=0.98, bottom=0.18)
    save(fig, stem)


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Generate accepted-paper-inspired round-9 TRI figures.")
    parser.add_argument("--data-dir", type=Path, default=root / "data" / "summary_csv")
    parser.add_argument("--output-dir", type=Path, default=root.parent / "figure-backup" / "candidates-round9-v1")
    args = parser.parse_args()

    policy_rows = read_csv(args.data_dir / "matched_pairacc_and_marginals.csv")
    substitution_rows = read_csv(args.data_dir / "v7_shared_eligible_pairacc_and_substitution.csv")
    sqlite_rows = read_csv(args.data_dir / "sqlite_model_facing_outcomes.csv")
    paired_rows = read_csv(args.data_dir / "main_figure_paired_scores.csv")

    build_policy_phase_map(policy_rows, args.output_dir / "fig2_policy_phase_map")
    build_cross_schema_endpoints(substitution_rows, args.output_dir / "fig3_cross_schema_endpoints")
    build_sqlite_alluvial(sqlite_rows, args.output_dir / "fig4_sqlite_outcomes")
    build_effect_phase_map(paired_rows, args.output_dir / "fig5_effect_phase_map")


if __name__ == "__main__":
    main()
