#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
REPORTS = ROOT / "reports"
REPORT_FIGURES = REPORTS / "figures"
PAPER_FIGURES = REPOSITORY / "paper" / "Figures"
COLORS = {"history_only": "#BE4D27", "decision_visible": "#17776B", "decision_enforced": "#5269A3"}
MODEL_LABELS = {
    "Qwen/Qwen3.5-122B-A10B": "Qwen3.5",
    "Pro/zai-org/GLM-5.1": "GLM-5.1",
    "deepseek-ai/DeepSeek-V4-Pro": "DeepSeek",
}


def load(name: str) -> dict:
    path = REPORTS / name
    if not path.exists():
        raise SystemExit(f"Missing completed report: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def point(metric: dict) -> tuple[float, float, float]:
    value = 100 * metric["rate"]
    lo, hi = metric["ci95_cluster"]
    return value, value - 100 * lo, 100 * hi - value


def clean_axis(ax, xlabel: str) -> None:
    ax.set_xlim(0, 100)
    ax.set_xlabel(xlabel, fontsize=8)
    ax.grid(axis="x", color="#D9DEE3", linewidth=0.6, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="both", labelsize=7, length=0)


def metric_panel(ax, report: dict, metric_name: str, title: str, denominator_note: str) -> None:
    models = report["models"]
    y = np.arange(len(models))
    offsets = {"history_only": -0.12, "decision_visible": 0.12}
    for index, model in enumerate(models):
        history = model["metrics"]["history_only"][metric_name]
        visible = model["metrics"]["decision_visible"][metric_name]
        if history["rate"] is not None and visible["rate"] is not None:
            ax.plot(
                [100 * history["rate"], 100 * visible["rate"]],
                [y[index] + offsets["history_only"], y[index] + offsets["decision_visible"]],
                color="#B7C0C8",
                linewidth=0.8,
                zorder=1,
            )
    for condition in ("history_only", "decision_visible"):
        for index, model in enumerate(models):
            metric = model["metrics"][condition][metric_name]
            if metric["rate"] is None:
                continue
            value, left, right = point(metric)
            ax.errorbar(
                value,
                y[index] + offsets[condition],
                xerr=[[left], [right]],
                fmt="o",
                color=COLORS[condition],
                ecolor=COLORS[condition],
                markersize=4.5,
                capsize=2,
                linewidth=1.1,
                zorder=3,
            )
            place_left = value >= 88
            ax.text(
                value - 2.2 if place_left else value + 2.2,
                y[index] + offsets[condition],
                f"{metric['numerator']}/{metric['denominator']}",
                ha="right" if place_left else "left",
                va="center",
                fontsize=6.5,
                color=COLORS[condition],
            )
    ax.set_yticks(y, [MODEL_LABELS[model["model"]] for model in models])
    ax.invert_yaxis()
    ax.set_title(title, loc="left", y=1.10, fontsize=9, fontweight="bold")
    ax.text(0, 1.015, denominator_note, transform=ax.transAxes, fontsize=6.5, color="#5D6875", va="bottom")
    clean_axis(ax, "accuracy (%)")


def make_full_human() -> plt.Figure:
    # V2 excludes the author-specified Reject slice from substitution denominators.
    full = load("revision_full_diagnostic_v2.json")
    fig, axes = plt.subplots(2, 1, figsize=(3.35, 4.0), constrained_layout=False)
    fig.subplots_adjust(left=0.25, right=0.97, bottom=0.10, top=0.86, hspace=0.55)
    metric_panel(axes[0], full, "changed_pairacc", "A  Changed PairAcc", "32 actionable changed pairs")
    metric_panel(axes[1], full, "actionable_e2e", "B  Actionable E2E", "128 actionable rows; Reject excluded")
    handles = [
        plt.Line2D([0], [0], marker="o", color=COLORS[condition], linestyle="", label=label)
        for condition, label in (("history_only", "History-only"), ("decision_visible", "Decision-visible"))
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.98),
        ncol=2,
        frameon=False,
        fontsize=7.5,
    )
    return fig


def make_source() -> plt.Figure:
    report = load("revision_source_grounded_v2.json")
    rule = load("revision_source_grounded_rule_star_frozen_v1.json")
    sources = ("STATE-Bench", "AgentDojo", "ToolSandbox")
    by_model = {row["model"]: row for row in report["models"]}
    models = [by_model[model] for model in MODEL_LABELS if model in by_model]
    fig, (ax_pair, ax_write) = plt.subplots(
        1,
        2,
        figsize=(7.0, 3.35),
        gridspec_kw={"width_ratios": [1.55, 1]},
        constrained_layout=False,
    )
    fig.subplots_adjust(left=0.20, right=0.985, bottom=0.18, top=0.72, wspace=0.32)

    rows = [(source, model) for source in sources for model in models]
    y = np.arange(len(rows))
    offsets = {"history_only": -0.12, "decision_visible": 0.12}
    labels = []
    for index, (source, model) in enumerate(rows):
        labels.append(f"{source} / {MODEL_LABELS[model['model']]}")
        for condition in ("history_only", "decision_visible"):
            metric = model["source_slices"][source][condition]["pairacc"]
            value, left, right = point(metric)
            ax_pair.errorbar(value, y[index] + offsets[condition], xerr=[[left], [right]], fmt="o", color=COLORS[condition], markersize=4, capsize=2, linewidth=1, zorder=3)
            place_left = value >= 88
            ax_pair.text(
                value - 1.8 if place_left else value + 1.8,
                y[index] + offsets[condition],
                f"{metric['numerator']}/10",
                ha="right" if place_left else "left",
                va="center",
                fontsize=6,
                color=COLORS[condition],
            )
    ax_pair.set_yticks(y, labels)
    ax_pair.invert_yaxis()
    ax_pair.set_title("A  PairAcc by source and model", loc="left", y=1.10, fontsize=9, fontweight="bold")
    ax_pair.text(0, 1.015, "30 source-grounded changed pairs; post-primary", transform=ax_pair.transAxes, fontsize=6.5, color="#5D6875", va="bottom")
    clean_axis(ax_pair, "PairAcc (%)")

    x = np.arange(len(models))
    width = 0.28
    for offset, condition in ((-width / 2, "history_only"), (width / 2, "decision_visible")):
        values = [model["metrics"][condition]["fixed_executor_wrong_writes"]["numerator"] for model in models]
        bars = ax_write.bar(x + offset, values, width, color=COLORS[condition], label=condition.replace("_", " "))
        for bar, value in zip(bars, values):
            ax_write.text(bar.get_x() + bar.get_width() / 2, value + 0.5, str(value), ha="center", va="bottom", fontsize=6.5)
    ax_write.set_xticks(x, [MODEL_LABELS[model["model"]] for model in models], rotation=15, ha="right")
    ax_write.set_ylabel("wrong-entity writes (count)", fontsize=8)
    ax_write.set_title("B  Fixed-executor wrong writes", loc="left", y=1.10, fontsize=9, fontweight="bold")
    ax_write.text(0, 1.015, f"Frozen Rule*: {rule['row_accuracy'][0]}/60 rows, {rule['pairacc'][0]}/30 pairs", transform=ax_write.transAxes, fontsize=6.5, color="#5D6875", va="bottom")
    ax_write.spines[["top", "right"]].set_visible(False)
    ax_write.grid(axis="y", color="#D9DEE3", linewidth=0.6, zorder=0)
    ax_write.tick_params(axis="both", labelsize=7)
    handles = [
        plt.Line2D([0], [0], marker="o", color=COLORS[condition], linestyle="", label=label)
        for condition, label in (("history_only", "History-only"), ("decision_visible", "Decision-visible"))
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.60, 0.89), ncol=2, frameon=False, fontsize=7)
    fig.suptitle("Source-grounded matched-call transfer", y=0.985, fontsize=10.5, fontweight="bold")
    return fig


def save(fig: plt.Figure, name: str) -> None:
    REPORT_FIGURES.mkdir(parents=True, exist_ok=True)
    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)
    for directory in (REPORT_FIGURES, PAPER_FIGURES):
        fig.savefig(directory / name, format="pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.unicode_minus": False, "pdf.fonttype": 42})
    save(make_full_human(), "tri_revision_matched_confirmation.pdf")
    save(make_source(), "tri_source_grounded_confirmation.pdf")
    print(REPORT_FIGURES / "tri_revision_matched_confirmation.pdf")
    print(REPORT_FIGURES / "tri_source_grounded_confirmation.pdf")


if __name__ == "__main__":
    main()
