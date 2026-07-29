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
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
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


def _draw_effect(
    ax: plt.Axes,
    x: float,
    row: dict[str, Any],
    marker: str,
    color: str,
    decision_visible: bool,
) -> None:
    value, low, high = row["value"], row["low"], row["high"]
    width = 0.10
    ax.add_patch(
        FancyBboxPatch(
            (x - width / 2, low),
            width,
            high - low,
            boxstyle="round,pad=0.004,rounding_size=0.07",
            facecolor=color,
            edgecolor=color,
            linewidth=0.75,
            alpha=0.18 if decision_visible else 0.09,
            linestyle="solid" if decision_visible else (0, (2.0, 1.6)),
            zorder=2,
        )
    )
    ax.errorbar(
        x,
        value,
        yerr=[[value - low], [high - value]],
        fmt="none",
        ecolor=color,
        elinewidth=0.8,
        capsize=2.2,
        capthick=0.75,
        zorder=3,
    )
    ax.plot(
        x,
        value,
        marker=marker,
        markersize=3.8,
        markerfacecolor=color if decision_visible else PAPER,
        markeredgecolor=color,
        markeredgewidth=0.85,
        linestyle="none",
        zorder=4,
    )
    ax.text(
        x + (0.10 if decision_visible else -0.10),
        value,
        f"{value:+.1f}",
        ha="left" if decision_visible else "right",
        va="center",
        fontsize=6.1,
        weight="bold" if low > 0 or high < 0 else "normal",
        color=INK,
        zorder=5,
    )


def draw(convention: dict[str, Any], matched: dict[str, Any], output: Path) -> None:
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
    convention_rows = _ordered(_convention_rows(convention))
    matched_rows = _ordered(_matched_rows(matched))
    fig, ax = plt.subplots(figsize=(2.80, 2.65))
    ax.axhline(0, color=INK, lw=0.75, zorder=1)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.grid(axis="y", which="major", color=GRID, lw=0.42, alpha=0.80, zorder=0)
    ax.grid(axis="y", which="minor", color=GRID, lw=0.25, alpha=0.32, zorder=0)
    for center, (convention_row, matched_row) in enumerate(
        zip(convention_rows, matched_rows, strict=True)
    ):
        if convention_row["model"] != matched_row["model"]:
            raise ValueError("Figure 6 model ordering differs between reports")
        _, marker, color = MODEL_STYLE[convention_row["model"]]
        _draw_effect(ax, center - 0.07, convention_row, marker, color, False)
        _draw_effect(ax, center + 0.07, matched_row, marker, color, True)

    ax.set_xlim(-0.48, 3.65)
    ax.set_ylim(-15, 75)
    ax.set_xticks(range(4), [MODEL_STYLE[row["model"]][0] for row in convention_rows])
    ax.set_ylabel("Changed PairAcc effect (pp)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=3)
    ax.tick_params(axis="y", length=2.4, width=0.65, pad=2)

    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color=MUTED,
            markerfacecolor=PAPER,
            markeredgecolor=MUTED,
            linestyle=(0, (2.0, 1.6)),
            linewidth=0.8,
            markersize=3.6,
            label="Convention told",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color=MUTED,
            markerfacecolor=MUTED,
            markeredgecolor=MUTED,
            linestyle="solid",
            linewidth=0.8,
            markersize=3.6,
            label="Decision visible",
        ),
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.60, 0.985),
        ncol=2,
        frameon=False,
        handlelength=1.25,
        handletextpad=0.35,
        columnspacing=0.9,
    )
    fig.text(
        0.58,
        0.018,
        "95% cluster-bootstrap CI",
        ha="center",
        va="bottom",
        fontsize=6.1,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.18, right=0.98, top=0.84, bottom=0.18)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"), metadata={"Creator": "TRI submission-critical plot"})
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
        "status": "Figure 6 integrated model-grouped equal-call effects",
        "source_size_in": [2.80, 2.65],
        "source_minimum_text_pt": 6.1,
        "insertion": "0.97 columnwidth",
        "minimum_text_pt": 7.0,
        "inputs": {
            "convention": str(DEFAULT_CONVENTION.relative_to(ROOT)),
            "decision_visible": str(DEFAULT_MATCHED.relative_to(ROOT)),
        },
        "encoding": {
            "open_dashed": "Convention told minus Plain history",
            "filled_solid": "Decision visible minus History only",
            "band": "cluster-bootstrap 95% CI",
            "model": "color and shape",
        },
        "effects_pp": {
            MODEL_STYLE[convention_row["model"]][0]: {
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
