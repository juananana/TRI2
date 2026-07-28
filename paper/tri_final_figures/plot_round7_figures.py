from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from plot_round4_figures import (
    CTA,
    E2E,
    FIXED,
    GENERIC,
    GRID,
    INK,
    MODEL_LABELS,
    MODEL_MARKERS,
    MODELS,
    OTHER,
    PAIR,
    PAPER,
    RULE,
    read_csv,
    row_where,
    save,
    wilson_interval,
)


def apply_compact_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 8.2,
            "axes.labelsize": 8.4,
            "axes.titlesize": 9.2,
            "xtick.labelsize": 8.2,
            "ytick.labelsize": 8.2,
            "legend.fontsize": 8.2,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
            "savefig.pad_inches": 0,
        }
    )


def build_policy_rulers(rows: list[dict[str, str]], stem: Path) -> None:
    apply_compact_style()
    fig, ax = plt.subplots(figsize=(3.31, 3.00))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9.5)

    def values_for(controller: str, model: str) -> tuple[list[float], list[str]]:
        all_row = row_where(rows, dataset="v3", model=model, controller=controller, slice="all")
        changed = row_where(
            rows,
            dataset="v3",
            model=model,
            controller=controller,
            slice="changed_winner_core",
        )
        values = [
            float(all_row["preserve_accuracy_pct"]),
            float(all_row["reevaluate_accuracy_pct"]),
            float(changed["pairacc_pct"]),
        ]
        counts = [
            f"{int(float(all_row['preserve_correct']))}/80",
            f"{int(float(all_row['reevaluate_correct']))}/80",
            f"{int(float(changed['both_correct']))}/32",
        ]
        return values, counts

    entries: list[tuple[str, list[float], list[str], str, str, bool]] = []
    for controller, color in [("CTA", CTA), ("Generic", GENERIC)]:
        for model in ("Qwen3.5", "GLM-5.1"):
            values, counts = values_for(controller, model)
            entries.append(
                (
                    f"{controller} · {MODEL_LABELS[model]}",
                    values,
                    counts,
                    color,
                    MODEL_MARKERS[model],
                    True,
                )
            )
    values, counts = values_for("Rule v2 (post-hoc)", "model-independent")
    entries.append(("Rule* · post-hoc", values, counts, RULE, "P", True))
    values, counts = values_for("Always-Lock+validity", "model-independent")
    entries.append(("Always Lock", values, counts, FIXED, "v", False))
    values, counts = values_for("Always-Reevaluate", "model-independent")
    entries.append(("Always Re-eval.", values, counts, FIXED, "^", False))

    order = [0, 1, 4, 2, 3, 5, 6]
    y_positions = [7.10, 6.25, 5.22, 4.15, 3.30, 2.18, 1.33]
    centers = [5.35, 7.85, 10.35]
    half_track = 0.86
    ax.text(
        6.0,
        9.03,
        "PairAcc exposes one-sided policies",
        ha="center",
        va="center",
        fontsize=9.2,
        color=INK,
        weight="bold",
    )
    ax.text(6.60, 8.35, "MARGINALS", ha="center", va="center", fontsize=8.2, color=FIXED, weight="bold")
    ax.text(10.35, 8.35, "JOINT", ha="center", va="center", fontsize=8.2, color=CTA, weight="bold")
    for x, label in zip(centers, ("Preserve", "Reevaluate", "PairAcc")):
        ax.text(x, 7.88, label, ha="center", va="center", fontsize=8.2, color=INK, weight="bold")

    for entry_index, y in zip(order, y_positions):
        label, values, counts, color, marker, filled = entries[entry_index]
        ax.scatter(
            0.45,
            y,
            s=28,
            marker=marker,
            facecolor=color if filled else PAPER,
            edgecolor=color,
            lw=0.85,
            zorder=4,
        )
        ax.text(0.82, y, label, ha="left", va="center", fontsize=8.2, color=color, weight="bold")
        for x, value, count in zip(centers, values, counts):
            left, right = x - half_track, x + half_track
            point_x = left + (right - left) * value / 100.0
            ax.plot([left, right], [y - 0.16, y - 0.16], color=OTHER, lw=2.45, solid_capstyle="round")
            ax.plot([left, point_x], [y - 0.16, y - 0.16], color=color, lw=2.35, solid_capstyle="round")
            ax.scatter(
                point_x,
                y - 0.16,
                s=17,
                marker=marker,
                facecolor=color if filled else PAPER,
                edgecolor=color,
                lw=0.75,
                zorder=5,
            )
            ax.text(x, y + 0.20, count, ha="center", va="center", fontsize=8.2, color=INK, weight="bold")
    for y in (5.72, 4.70, 2.72):
        ax.plot([0.25, 11.72], [y, y], color=GRID, lw=0.65, ls=(0, (3, 3)))
    ax.text(
        6.0,
        0.50,
        "Both requests must be correct",
        ha="center",
        va="center",
        fontsize=8.2,
        color=FIXED,
    )
    ax.set_axis_off()
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, stem)


def build_substitution_dumbbell(rows: list[dict[str, str]], stem: Path) -> None:
    apply_compact_style()
    fig, ax = plt.subplots(figsize=(3.31, 2.35))
    y_positions = {"Qwen3.5": 2.5, "GLM-5.1": 1.5, "DeepSeek": 0.5}
    for model in MODELS:
        generic = row_where(rows, model=model, controller="Generic")
        cta = row_where(rows, model=model, controller="CTA")
        n = int(generic["shared_eligible"])
        generic_count = int(generic["substitutions"])
        cta_count = int(cta["substitutions"])
        generic_x, generic_low, generic_high = wilson_interval(generic_count, n)
        cta_x, cta_low, cta_high = wilson_interval(cta_count, n)
        y = y_positions[model]
        marker = MODEL_MARKERS[model]
        ax.plot([cta_x, generic_x], [y, y], color=GRID, lw=1.8, zorder=1)
        ax.errorbar(
            generic_x,
            y,
            xerr=[
                [max(0.0, generic_x - generic_low)],
                [max(0.0, generic_high - generic_x)],
            ],
            fmt=marker,
            ms=5.8,
            mfc=GENERIC,
            mec=INK,
            mew=0.7,
            ecolor=GENERIC,
            elinewidth=1.1,
            capsize=2.6,
            zorder=3,
        )
        ax.errorbar(
            cta_x,
            y,
            xerr=[
                [max(0.0, cta_x - cta_low)],
                [max(0.0, cta_high - cta_x)],
            ],
            fmt=marker,
            ms=5.8,
            mfc=PAPER,
            mec=CTA,
            mew=1.2,
            ecolor=CTA,
            elinewidth=1.1,
            capsize=2.6,
            zorder=4,
        )
        ax.text(
            generic_x,
            y + 0.26,
            f"{generic_count}/{n}",
            ha="center",
            va="bottom",
            fontsize=8.2,
            color=GENERIC,
            weight="bold",
        )
        ax.text(
            2.0,
            y + 0.20,
            f"{cta_count}/{n}",
            ha="left",
            va="bottom",
            fontsize=8.2,
            color=CTA,
            weight="bold",
        )

    ax.axvline(0, color=INK, lw=0.9)
    ax.set_xlim(-1, 85)
    ax.set_ylim(0.05, 3.12)
    ax.set_yticks([2.5, 1.5, 0.5])
    ax.set_yticklabels(["Qwen", "GLM", "DeepSeek"], weight="bold")
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_xlabel("Conditional substitution (%)\nshared-eligible Preserve rows", labelpad=3)
    ax.set_title("Post-binding target substitution", pad=13, weight="bold")
    ax.grid(axis="x", color=GRID, lw=0.55, alpha=0.75)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.subplots_adjust(left=0.24, right=0.98, top=0.78, bottom=0.27)
    save(fig, stem)


def build_sqlite_outcomes(rows: list[dict[str, str]], stem: Path) -> None:
    apply_compact_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.70))
    categories = [
        ("correct_final_state", "Correct", CTA, "s"),
        ("core_tri_write", "TRI write", GENERIC, "o"),
        ("fallback_wrong_write", "Fallback write", RULE, "D"),
        ("unneeded_reject", "Reject", FIXED, "x"),
    ]
    panel_x = {"Qwen3.5": 0.8, "GLM-5.1": 10.8}
    for model in ("Qwen3.5", "GLM-5.1"):
        row = row_where(rows, model=model, controller="Generic")
        x0 = panel_x[model]
        ax.text(x0 + 3.6, 6.18, MODEL_LABELS[model], ha="center", va="center", fontsize=8.5, color=INK, weight="bold")
        task_index = 0
        for key, _, color, marker in categories:
            for _ in range(int(row[key])):
                column = task_index % 8
                grid_row = task_index // 8
                x = x0 + column * 0.91
                y = 5.48 - grid_row * 0.78
                if marker == "x":
                    ax.scatter(x + 0.35, y + 0.29, s=39, marker=marker, color=color, linewidth=1.2, zorder=3)
                else:
                    ax.scatter(
                        x + 0.35,
                        y + 0.29,
                        s=39,
                        marker=marker,
                        facecolor=color,
                        edgecolor=PAPER,
                        linewidth=0.7,
                        zorder=3,
                    )
                task_index += 1
        assert task_index == int(row["tasks"])
        ax.text(
            x0 + 3.6,
            1.16,
            f"correct {row['correct_final_state']} · TRI {row['core_tri_write']}\n"
            f"fallback {row['fallback_wrong_write']} · reject {row['unneeded_reject']}",
            ha="center",
            va="center",
            fontsize=7.8,
            color=INK,
            weight="bold",
        )
        ax.text(
            x0 + 3.6,
            0.44,
            f"strict {row['strict_core_writes']}/{row['strict_core_opportunities']} · stable {row['stable_writes']}/{row['stable_opportunities']}",
            ha="center",
            va="center",
            fontsize=7.8,
            color=FIXED,
        )

    ax.text(10.0, 7.72, "MODEL-FACING SQLITE OUTCOMES", ha="center", va="center", fontsize=8.8, color=INK, weight="bold")
    ax.text(10.0, 7.31, "each marker is one complete task trajectory", ha="center", va="center", fontsize=7.8, color=FIXED)
    handles = [
        Line2D(
            [0],
            [0],
            marker=marker,
            color="none",
            markerfacecolor=color if marker != "x" else "none",
            markeredgecolor=color,
            markeredgewidth=1.0,
            markersize=5.6,
            label=label,
        )
        for _, label, color, marker in categories
    ]
    ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.50, 0.87),
        frameon=False,
        ncol=4,
        columnspacing=0.50,
        handlelength=0.95,
        handletextpad=0.28,
    )
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 8.15)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, stem)


def build_visibility_forest(rows: list[dict[str, str]], stem: Path) -> None:
    apply_compact_style()
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(3.31, 4.05),
        sharex=True,
        gridspec_kw={"height_ratios": [5, 7], "hspace": 0.16},
    )
    panels = [
        (
            axes[0],
            "A  Changed PairAcc",
            "changed_pairacc",
            [
                ("Authored / Qwen", "revision_full_diagnostic", "Qwen3.5", PAIR),
                ("Authored / GLM", "revision_full_diagnostic", "GLM-5.1", PAIR),
                ("Source / Qwen", "revision_source_grounded", "Qwen3.5", CTA),
                ("Source / GLM", "revision_source_grounded", "GLM-5.1", CTA),
                ("Source / DeepSeek", "revision_source_grounded", "DeepSeek", CTA),
            ],
        ),
        (
            axes[1],
            "B  Actionable E2E",
            "actionable_e2e",
            [
                ("Authored / Qwen", "revision_full_diagnostic", "Qwen3.5", PAIR),
                ("Authored / GLM", "revision_full_diagnostic", "GLM-5.1", PAIR),
                ("Rewrite / Qwen", "revision_human_rewrite", "Qwen3.5", RULE),
                ("Rewrite / GLM", "revision_human_rewrite", "GLM-5.1", RULE),
                ("Source / Qwen", "revision_source_grounded", "Qwen3.5", CTA),
                ("Source / GLM", "revision_source_grounded", "GLM-5.1", CTA),
                ("Source / DeepSeek", "revision_source_grounded", "DeepSeek", CTA),
            ],
        ),
    ]
    for ax, title, metric, entries in panels:
        y_positions = list(range(len(entries) - 1, -1, -1))
        for (label, audit_id, model, color), y in zip(entries, y_positions):
            row = row_where(rows, audit_id=audit_id, model=model, metric=metric)
            value = float(row["difference_pp"])
            low = float(row["ci95_low_pp"])
            high = float(row["ci95_high_pp"])
            marker = MODEL_MARKERS[model]
            ax.errorbar(
                value,
                y,
                xerr=[[value - low], [high - value]],
                fmt=marker,
                ms=5.2,
                mfc=PAPER if model != "Qwen3.5" else color,
                mec=color,
                mew=1.05,
                ecolor=color,
                elinewidth=1.05,
                capsize=2.4,
                zorder=3,
            )
            ax.text(105.0, y, f"{value:+.1f}", ha="right", va="center", fontsize=8.2, color=color, weight="bold")
        ax.axvline(0, color=INK, lw=0.95)
        ax.set_xlim(-30, 108)
        ax.set_ylim(-0.65, len(entries) - 0.10)
        ax.set_yticks(y_positions)
        ax.set_yticklabels([entry[0] for entry in entries], fontsize=8.2, weight="bold")
        ax.set_title(title, loc="left", pad=3, fontsize=9.2, weight="bold")
        ax.grid(axis="x", color=GRID, lw=0.55, alpha=0.75)
        ax.set_axisbelow(True)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=3)
    axes[0].spines["bottom"].set_color(GRID)
    axes[0].text(-28.0, 4.47, "n=32 / 30 pairs (authored / source)",
                 ha="left", va="center", fontsize=7.0, color=FIXED)
    axes[0].tick_params(axis="x", bottom=False, labelbottom=False)
    axes[1].set_xticks([-20, 0, 20, 40, 60, 80, 100])
    axes[1].text(-28.0, 6.47, "n=128 / 40 / 60 rows (authored / rewrite / source)",
                 ha="left", va="center", fontsize=7.0, color=FIXED)
    axes[1].set_xlabel("Decision-visible - History-only (pp)")
    fig.subplots_adjust(left=0.40, right=0.985, top=0.94, bottom=0.12)
    save(fig, stem)


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Generate compact round-7 TRI main-paper figures.")
    parser.add_argument("--data-dir", type=Path, default=root / "data" / "summary_csv")
    parser.add_argument("--output-dir", type=Path, default=root / "outputs" / "round7")
    args = parser.parse_args()
    phase = read_csv(args.data_dir / "matched_pairacc_and_marginals.csv")
    flow = read_csv(args.data_dir / "v7_shared_eligible_pairacc_and_substitution.csv")
    sqlite = read_csv(args.data_dir / "sqlite_model_facing_outcomes.csv")
    gains = read_csv(args.data_dir / "revision_decision_visible_gains.csv")
    build_policy_rulers(phase, args.output_dir / "fig2_policy_rulers_round7")
    build_substitution_dumbbell(flow, args.output_dir / "fig3_shared_eligible_dumbbell_round7")
    build_visibility_forest(gains, args.output_dir / "fig5_visibility_endpoints_round7")


if __name__ == "__main__":
    main()
