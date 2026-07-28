from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from plot_round4_figures import (
    CTA,
    GRID,
    INK,
    MODEL_LABELS,
    MODEL_MARKERS,
    PAIR,
    PAPER,
    RULE,
    apply_round4_style,
    read_csv,
    row_where,
    save,
)


def build_endpoint_panel_forest(rows: list[dict[str, str]], stem: Path) -> None:
    """Separate matched-pair and row-level effects into explicit panels."""
    apply_round4_style()
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(3.35, 5.10),
        sharex=True,
        gridspec_kw={"height_ratios": [5, 7], "hspace": 0.30},
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
                ms=5.6,
                mfc=PAPER if model != "Qwen3.5" else color,
                mec=color,
                mew=1.15,
                ecolor=color,
                elinewidth=1.15,
                capsize=2.7,
                zorder=3,
            )
            ax.text(105.0, y, f"{value:+.1f}", ha="right", va="center", fontsize=8.0, color=color, weight="bold")
        ax.axvline(0, color=INK, lw=1.0)
        ax.set_xlim(-30, 108)
        ax.set_ylim(-0.65, len(entries) - 0.35)
        ax.set_yticks(y_positions)
        ax.set_yticklabels([entry[0] for entry in entries], fontsize=8.0, weight="bold")
        ax.set_title(title, loc="left", pad=4, weight="bold")
        ax.grid(axis="x", color=GRID, lw=0.6, alpha=0.75)
        ax.set_axisbelow(True)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=4)

    axes[0].spines["bottom"].set_color(GRID)
    axes[0].tick_params(axis="x", bottom=False, labelbottom=False)
    axes[1].set_xticks([-20, 0, 20, 40, 60, 80, 100])
    axes[1].set_xlabel("Decision-visible - History-only (pp)")
    fig.subplots_adjust(left=0.41, right=0.985, top=0.94, bottom=0.10)
    save(fig, stem)


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Generate round-5 TRI main-paper figures.")
    parser.add_argument("--data-dir", type=Path, default=root / "data" / "summary_csv")
    parser.add_argument("--output-dir", type=Path, default=root / "outputs" / "round5")
    args = parser.parse_args()
    gains = read_csv(args.data_dir / "revision_decision_visible_gains.csv")
    build_endpoint_panel_forest(gains, args.output_dir / "fig5_visibility_endpoints_round5")


if __name__ == "__main__":
    main()
