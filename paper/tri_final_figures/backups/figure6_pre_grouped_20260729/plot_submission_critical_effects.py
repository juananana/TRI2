#!/usr/bin/env python3
"""Single-column, two-inventory PairAcc effect figure for the submission-critical audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_CONVENTION = (
    ROOT / "experiments/tri_artifact/reports/convention_told_natural_history_v1.json"
)
DEFAULT_MATCHED = (
    ROOT / "experiments/tri_artifact/reports/revision_full_diagnostic_four_model_v2.json"
)
DEFAULT_OUTPUT = HERE / "outputs" / "fig_submission_critical_pairacc_effects_v1"

INK = "#264A56"
MUTED = "#5F6B70"
GRID = "#D6E0DE"
PAPER = "#FFFFFF"
MODEL_STYLE = {
    "Qwen/Qwen3.5-122B-A10B": ("Qwen", "o", "#8B6F8E"),
    "Pro/zai-org/GLM-5.1": ("GLM", "s", "#E56D4E"),
    "deepseek-ai/DeepSeek-V4-Pro": ("DeepSeek", "D", "#407A7F"),
    "Pro/MiniMaxAI/MiniMax-M2.5": ("MiniMax", "^", "#60AA84"),
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _convention_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for model in report["models"]:
        contrast = next(
            item for item in model["paired_differences"] if item["metric"] == "changed_pairacc"
        )
        rows.append(
            {
                "model": model["model"],
                "value": 100 * contrast["difference_right_minus_left"],
                "low": 100 * contrast["ci95_state_cluster"][0],
                "high": 100 * contrast["ci95_state_cluster"][1],
            }
        )
    return rows


def _matched_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for model in report["models"]:
        contrast = model["decision_visible_minus_history"]["changed_pairacc"]
        rows.append(
            {
                "model": model["model"],
                "value": 100 * contrast["difference"],
                "low": 100 * contrast["ci95_cluster"][0],
                "high": 100 * contrast["ci95_cluster"][1],
            }
        )
    return rows


def _ordered(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model = {row["model"]: row for row in rows}
    if set(by_model) != set(MODEL_STYLE):
        raise ValueError(f"figure requires four complete model cells, found {sorted(by_model)}")
    return [by_model[model] for model in MODEL_STYLE]


def draw(convention: dict[str, Any], matched: dict[str, Any], output: Path) -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.labelsize": 7.4,
            "axes.titlesize": 8.0,
            "xtick.labelsize": 6.8,
            "ytick.labelsize": 7.0,
            "axes.linewidth": 0.65,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "text.color": INK,
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )
    panels = [
        ("A  Convention-told (40 pairs)", _ordered(_convention_rows(convention))),
        ("B  Decision-visible (32 pairs)", _ordered(_matched_rows(matched))),
    ]
    fig, axes = plt.subplots(2, 1, figsize=(3.35, 3.55), sharex=True)
    for ax, (title, rows) in zip(axes, panels):
        y_positions = list(reversed(range(len(rows))))
        ax.axvline(0, color=INK, lw=0.72, zorder=0)
        ax.grid(axis="x", color=GRID, lw=0.42, alpha=0.75, zorder=0)
        for y, row in zip(y_positions, rows):
            label, marker, color = MODEL_STYLE[row["model"]]
            ax.errorbar(
                row["value"],
                y,
                xerr=[[row["value"] - row["low"]], [row["high"] - row["value"]]],
                fmt=marker,
                ms=5.0,
                mfc=PAPER,
                mec=color,
                mew=1.0,
                ecolor=color,
                elinewidth=0.9,
                capsize=2.0,
                zorder=3,
            )
            label_on_left = row["high"] > 75
            label_x = row["low"] - 2.5 if label_on_left else row["high"] + 2.5
            ax.text(
                label_x,
                y,
                f"{row['value']:+.1f}",
                ha="right" if label_on_left else "left",
                va="center",
                fontsize=6.2,
                color=INK,
            )
        ax.set_yticks(y_positions, [MODEL_STYLE[row["model"]][0] for row in rows])
        ax.set_ylim(-0.65, len(rows) - 0.35)
        ax.set_title(title, loc="left", pad=3, weight="bold")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=4)
        ax.tick_params(axis="x", length=3, width=0.65)
    axes[-1].set_xlim(-20, 85)
    axes[-1].set_xticks([-20, 0, 20, 40, 60, 80])
    axes[-1].set_xlabel("Change in changed-pair accuracy (pp)")
    fig.text(
        0.99,
        0.012,
        "Separate audits; 95% pair-cluster intervals.",
        ha="right",
        va="bottom",
        fontsize=5.8,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.24, right=0.99, top=0.96, bottom=0.14, hspace=0.35)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"), metadata={"Creator": "TRI submission-critical plot"})
    svg_path = output.with_suffix(".svg")
    fig.savefig(svg_path)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    fig.savefig(output.with_suffix(".png"), dpi=400)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--convention", type=Path, default=DEFAULT_CONVENTION)
    parser.add_argument("--matched", type=Path, default=DEFAULT_MATCHED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    draw(_load(args.convention), _load(args.matched), args.output)


if __name__ == "__main__":
    main()
