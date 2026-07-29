#!/usr/bin/env python3
"""Two-color, model-grouped Figure 6 for the submission-critical audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = next(
    parent
    for parent in HERE.parents
    if (parent / "experiments/tri_artifact").is_dir() and (parent / "paper").is_dir()
)
DEFAULT_CONVENTION = (
    ROOT / "experiments/tri_artifact/reports/convention_told_natural_history_v1.json"
)
DEFAULT_MATCHED = (
    ROOT / "experiments/tri_artifact/reports/revision_full_diagnostic_four_model_v2.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "paper/tri_final_figures/outputs/fig_submission_critical_pairacc_effects_v1"
)

INK = "#264A56"
MUTED = "#5F6B70"
GRID = "#D6E0DE"
PAPER = "#FFFFFF"
PLUM = "#8B6F8E"
PLUM_FILL = "#D8CAD9"
TEAL = "#407A7F"
MODEL_LABEL = {
    "Qwen/Qwen3.5-122B-A10B": "Qwen",
    "Pro/zai-org/GLM-5.1": "GLM",
    "deepseek-ai/DeepSeek-V4-Pro": "DeepSeek",
    "Pro/MiniMaxAI/MiniMax-M2.5": "MiniMax",
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
    if set(by_model) != set(MODEL_LABEL):
        raise ValueError(f"figure requires four complete model cells, found {sorted(by_model)}")
    return [by_model[model] for model in MODEL_LABEL]


def _configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 6.5,
            "axes.labelsize": 6.8,
            "xtick.labelsize": 6.1,
            "ytick.labelsize": 6.4,
            "legend.fontsize": 6.1,
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


def _draw_bar(
    ax: plt.Axes,
    x: float,
    row: dict[str, Any],
    edge: str,
    face: str,
    right_series: bool,
) -> None:
    value, low, high = row["value"], row["low"], row["high"]
    width = 0.26
    ax.bar(
        x,
        value,
        width=width,
        color=face,
        edgecolor=edge,
        linewidth=0.8,
        alpha=0.88 if right_series else 1.0,
        zorder=2,
    )
    ax.errorbar(
        x,
        value,
        yerr=[[value - low], [high - value]],
        fmt="none",
        ecolor=edge,
        elinewidth=0.85,
        capsize=2.2,
        capthick=0.8,
        zorder=3,
    )
    ax.text(
        x + (width / 2 + 0.035 if right_series else -(width / 2 + 0.035)),
        value,
        f"{value:+.1f}",
        ha="left" if right_series else "right",
        va="center",
        fontsize=6.1,
        weight="bold" if low > 0 or high < 0 else "normal",
        color=INK,
        zorder=4,
    )


def draw(convention: dict[str, Any], matched: dict[str, Any], output: Path) -> None:
    _configure()
    convention_rows = _ordered(_convention_rows(convention))
    matched_rows = _ordered(_matched_rows(matched))
    fig, ax = plt.subplots(figsize=(2.80, 2.48))
    width = 0.26
    for center, (convention_row, matched_row) in enumerate(
        zip(convention_rows, matched_rows, strict=True)
    ):
        if convention_row["model"] != matched_row["model"]:
            raise ValueError("Figure 6 model ordering differs between reports")
        _draw_bar(ax, center - width / 2, convention_row, PLUM, PLUM_FILL, False)
        _draw_bar(ax, center + width / 2, matched_row, TEAL, TEAL, True)

    ax.axhline(0, color=INK, lw=0.75, zorder=1)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.grid(axis="y", which="major", color=GRID, lw=0.42, alpha=0.80, zorder=0)
    ax.grid(axis="y", which="minor", color=GRID, lw=0.25, alpha=0.32, zorder=0)
    ax.set_xlim(-0.60, 3.75)
    ax.set_ylim(-15, 75)
    ax.set_xticks(range(4), [MODEL_LABEL[row["model"]] for row in convention_rows])
    ax.set_ylabel("Changed PairAcc effect (pp)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=3)
    ax.tick_params(axis="y", length=2.4, width=0.65, pad=2)

    fig.legend(
        handles=[
            Patch(facecolor=PLUM_FILL, edgecolor=PLUM, label="Convention told"),
            Patch(facecolor=TEAL, edgecolor=TEAL, alpha=0.88, label="Decision visible"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.60, 0.985),
        ncol=2,
        frameon=False,
        handlelength=0.9,
        handletextpad=0.35,
        columnspacing=0.9,
    )
    fig.text(
        0.58,
        0.018,
        "Bar = effect; whisker = cluster-bootstrap 95% CI",
        ha="center",
        va="bottom",
        fontsize=6.1,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.18, right=0.98, top=0.84, bottom=0.18)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"), metadata={"Creator": "TRI Figure 6 grouped bars"})
    svg_path = output.with_suffix(".svg")
    fig.savefig(svg_path)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    png_path = output.with_suffix(".png")
    fig.savefig(png_path, dpi=400)
    plt.close(fig)

    with Image.open(png_path).convert("RGB") as image:
        image.convert("L").save(output.with_name(f"{output.name}-grayscale.png"))
        deuteranopia = image.convert(
            "RGB",
            (
                0.367322,
                0.860646,
                -0.227968,
                0.0,
                0.280085,
                0.672501,
                0.047413,
                0.0,
                -0.011820,
                0.042940,
                0.968881,
                0.0,
            ),
        )
        deuteranopia.save(output.with_name(f"{output.name}-deuteranopia.png"))

    manifest = {
        "status": "Figure 6 integrated two-color grouped effect bars",
        "source_size_in": [2.80, 2.48],
        "source_minimum_text_pt": 6.1,
        "insertion": "0.97 columnwidth",
        "minimum_text_pt": 7.0,
        "inputs": {
            "convention": str(DEFAULT_CONVENTION.relative_to(ROOT)),
            "decision_visible": str(DEFAULT_MATCHED.relative_to(ROOT)),
        },
        "encoding": {
            "left_lavender_bar": "Convention told minus Plain history",
            "right_teal_bar": "Decision visible minus History only",
            "bar_height": "changed PairAcc effect in percentage points",
            "whisker": "cluster-bootstrap 95% CI",
            "model": "x-axis label",
        },
        "effects_pp": {
            MODEL_LABEL[convention_row["model"]]: {
                "convention_told": convention_row["value"],
                "decision_visible": matched_row["value"],
            }
            for convention_row, matched_row in zip(convention_rows, matched_rows, strict=True)
        },
    }
    output.with_name(f"{output.name}-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--convention", type=Path, default=DEFAULT_CONVENTION)
    parser.add_argument("--matched", type=Path, default=DEFAULT_MATCHED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    draw(_load(args.convention), _load(args.matched), args.output)


if __name__ == "__main__":
    main()
