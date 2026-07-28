#!/usr/bin/env python3
"""Generate the compact result figures that close the main-paper RQs (v3)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D


HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "figure_ready"
DEFAULT_OUTPUT = HERE.parent / "figure_outputs" / "result_closure_v3"

INK = "#30343F"
MUTED = "#69737A"
GRID = "#D9DEE2"
PAPER = "#FFFFFF"
QWEN = "#8F8DBB"
GLM = "#DA6B64"
DEEPSEEK = "#4F9EA0"
CONTROL = "#626C72"
RULE = "#52767B"

MODEL_STYLE = {
    "Qwen3.5": ("Qwen", "o", QWEN),
    "GLM-5.1": ("GLM", "s", GLM),
    "DeepSeek": ("DeepSeek", "D", DEEPSEEK),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(rows: list[dict[str, str]], **where: str) -> dict[str, str]:
    matches = [
        row for row in rows if all(row.get(field) == value for field, value in where.items())
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {where}, found {len(matches)}")
    return matches[0]


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.2,
            "axes.labelsize": 7.4,
            "axes.titlesize": 8.1,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.1,
            "legend.fontsize": 7.0,
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "text.color": INK,
            "axes.labelcolor": INK,
            "axes.edgecolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
        }
    )


def clean_axis(ax: plt.Axes, *, grid: bool = True) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    if grid:
        ax.grid(axis="x", color=GRID, lw=0.45, alpha=0.9, zorder=0)
        ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=2.6, width=0.65, pad=2)
    ax.tick_params(axis="y", length=0, pad=3)


def save_variants(fig: plt.Figure, stem: Path, creator: str) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"), metadata={"Creator": creator})
    fig.savefig(stem.with_suffix(".svg"))
    png = stem.with_suffix(".png")
    fig.savefig(png, dpi=400)
    plt.close(fig)

    with Image.open(png).convert("RGB") as image:
        image.convert("L").save(stem.with_name(stem.name + "_grayscale").with_suffix(".png"))
        rgb = np.asarray(image, dtype=np.float32) / 255.0
        # Machado et al.-style full deuteranopia approximation, used only for visual QA.
        matrix = np.array(
            [
                [0.367322, 0.860646, -0.227968],
                [0.280085, 0.672501, 0.047413],
                [-0.011820, 0.042940, 0.968881],
            ],
            dtype=np.float32,
        )
        simulated = np.clip(rgb @ matrix.T, 0.0, 1.0)
        Image.fromarray(np.uint8(np.round(simulated * 255))).save(
            stem.with_name(stem.name + "_deuteranopia").with_suffix(".png")
        )


def policy_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    definitions = {
        "Always Lock": [("model-independent", "Always-Lock+validity")],
        "Always Reeval.": [("model-independent", "Always-Reevaluate")],
        "Generic": [("Qwen3.5", "Generic"), ("GLM-5.1", "Generic")],
        "CTA": [("Qwen3.5", "CTA"), ("GLM-5.1", "CTA")],
        "Rule*": [("model-independent", "Rule v2 (post-hoc)")],
    }
    output: dict[str, dict[str, dict[str, str]]] = {}
    for label, cells in definitions.items():
        output[label] = {}
        for model, controller in cells:
            output[label][model] = {
                "marginal": one(
                    rows,
                    dataset="v3",
                    model=model,
                    controller=controller,
                    slice="all",
                ),
                "pair": one(
                    rows,
                    dataset="v3",
                    model=model,
                    controller=controller,
                    slice="changed_winner_core",
                ),
            }
    return output


def validate_policy(data: dict[str, dict[str, dict[str, str]]]) -> None:
    expected = {
        ("Always Lock", "model-independent"): (100.0, 20.0, 0),
        ("Always Reeval.", "model-independent"): (20.0, 100.0, 0),
        ("Generic", "Qwen3.5"): (33.75, 95.0, 3),
        ("Generic", "GLM-5.1"): (56.25, 87.5, 7),
        ("CTA", "Qwen3.5"): (91.25, 98.75, 30),
        ("CTA", "GLM-5.1"): (92.5, 100.0, 31),
        ("Rule*", "model-independent"): (92.5, 92.5, 28),
    }
    for (label, model), values in expected.items():
        marginal = data[label][model]["marginal"]
        pair = data[label][model]["pair"]
        observed = (
            float(marginal["preserve_accuracy_pct"]),
            float(marginal["reevaluate_accuracy_pct"]),
            int(pair["both_correct"]),
        )
        if observed != values or int(pair["pairs"]) != 32:
            raise ValueError(f"policy figure source mismatch for {label}/{model}: {observed}")


def draw_policy(rows: list[dict[str, str]], stem: Path) -> None:
    configure_style()
    data = policy_rows(rows)
    validate_policy(data)

    fig = plt.figure(figsize=(3.35, 1.92))
    outer = fig.add_gridspec(1, 2, width_ratios=[1.12, 1.12], wspace=0.18)
    marginal_ax = fig.add_subplot(outer[0])
    pair_grid = outer[1].subgridspec(1, 2, width_ratios=[0.84, 0.30], wspace=0.02)
    pair_ax = fig.add_subplot(pair_grid[0], sharey=marginal_ax)
    count_ax = fig.add_subplot(pair_grid[1], sharey=marginal_ax)
    labels = ["Always Lock", "Always Reeval.", "Generic", "CTA", "Rule*"]
    y_positions = dict(zip(labels, [4, 3, 2, 1, 0]))
    offsets = {"Qwen3.5": 0.17, "GLM-5.1": -0.17, "model-independent": 0.0}

    for label in labels:
        y = y_positions[label]
        for model, cell in data[label].items():
            marginal = cell["marginal"]
            preserve = float(marginal["preserve_accuracy_pct"])
            reevaluate = float(marginal["reevaluate_accuracy_pct"])
            yy = y + offsets[model]
            if model in MODEL_STYLE:
                _, marker, color = MODEL_STYLE[model]
            else:
                marker = "D"
                color = RULE if label == "Rule*" else CONTROL
            marginal_ax.plot(
                [preserve, reevaluate],
                [yy, yy],
                color=color,
                lw=1.15,
                alpha=0.9,
                zorder=2,
            )
            marginal_ax.scatter(
                preserve,
                yy,
                marker=marker,
                s=27,
                facecolor=color,
                edgecolor=color,
                linewidth=0.8,
                zorder=3,
            )
            marginal_ax.scatter(
                reevaluate,
                yy,
                marker=marker,
                s=27,
                facecolor=PAPER,
                edgecolor=color,
                linewidth=1.05,
                zorder=3,
            )

            pair = cell["pair"]
            score = float(pair["pairacc_pct"])
            count = int(pair["both_correct"])
            pair_ax.scatter(
                score,
                yy,
                marker=marker,
                s=28,
                facecolor=color if label not in {"Always Lock", "Always Reeval.", "Rule*"} else PAPER,
                edgecolor=color,
                linewidth=1.0,
                zorder=3,
            )
            count_ax.text(
                0.04,
                yy,
                f"{count}/32",
                va="center",
                ha="left",
                fontsize=6.9,
                color=color,
                clip_on=False,
            )

    marginal_ax.set_yticks([4, 3, 2, 1, 0], labels)
    marginal_ax.set_xlim(-3, 103)
    marginal_ax.set_xticks([0, 50, 100])
    marginal_ax.set_xlabel("Accuracy (%)", labelpad=2)
    marginal_ax.set_title("A  Marginals", loc="left", pad=2, weight="bold")
    clean_axis(marginal_ax)

    pair_ax.axvline(50, color=GRID, lw=0.75, ls=(0, (3, 2)), zorder=1)
    pair_ax.set_xlim(-3, 112)
    pair_ax.set_xticks([0, 50, 100])
    pair_ax.set_xlabel("PairAcc (%)", labelpad=2)
    pair_ax.set_title("B  PairAcc", loc="left", pad=2, weight="bold")
    clean_axis(pair_ax)
    pair_ax.spines["left"].set_visible(False)
    pair_ax.tick_params(axis="y", labelleft=False)
    count_ax.set_xlim(0, 1)
    count_ax.tick_params(axis="y", labelleft=False)
    count_ax.axis("off")
    count_ax.text(
        0.04,
        1.03,
        "n/32",
        transform=count_ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=6.9,
        color=MUTED,
    )

    fig.text(
        0.27,
        0.98,
        "filled = Preserve     open = Reevaluate",
        ha="left",
        va="top",
        fontsize=7.0,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.27, right=0.985, top=0.80, bottom=0.18)
    save_variants(fig, stem, "TRI compact policy-discrimination figure v2")


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    spread = (
        z
        * math.sqrt(proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total))
        / denominator
    )
    return 100.0 * (center - spread), 100.0 * (center + spread)


def validate_conditional(rows: list[dict[str, str]]) -> None:
    expected = {
        ("Qwen3.5", "Generic"): (66, 41, 7, 80, 8.75, 2.5, 16.25),
        ("Qwen3.5", "CTA"): (66, 0, 31, 80, 38.75, 26.25, 51.25),
        ("GLM-5.1", "Generic"): (70, 30, 15, 80, 18.75, 8.75, 30.0),
        ("GLM-5.1", "CTA"): (70, 0, 66, 80, 82.5, 73.75, 90.0),
        ("DeepSeek", "Generic"): (69, 50, 17, 80, 21.25, 11.25, 32.5),
        ("DeepSeek", "CTA"): (69, 0, 64, 80, 80.0, 70.0, 88.75),
    }
    for key, values in expected.items():
        row = one(rows, model=key[0], controller=key[1])
        observed = (
            int(row["shared_eligible"]),
            int(row["substitutions"]),
            int(row["pairacc_both_correct"]),
            int(row["pairacc_pairs"]),
            float(row["pairacc_pct"]),
            float(row["pairacc_ci95_low_pct"]),
            float(row["pairacc_ci95_high_pct"]),
        )
        if observed != values:
            raise ValueError(f"conditional figure source mismatch for {key}: {observed}")


def draw_conditional_pairing(rows: list[dict[str, str]], stem: Path) -> None:
    configure_style()
    validate_conditional(rows)
    models = [
        ("Qwen3.5", "Qwen", QWEN, 5.0, 4.15, 5.48),
        ("GLM-5.1", "GLM", GLM, 2.75, 1.90, 3.23),
        ("DeepSeek", "DeepSeek", DEEPSEEK, 0.50, -0.35, 0.98),
    ]

    fig = plt.figure(figsize=(3.35, 2.20))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.0, 0.49], wspace=0.04)
    ax = fig.add_subplot(grid[0])
    count_ax = fig.add_subplot(grid[1], sharey=ax)

    y_ticks: list[float] = []
    y_labels: list[str] = []
    for model, label, color, substitution_y, pair_y, heading_y in models:
        generic = one(rows, model=model, controller="Generic")
        cta = one(rows, model=model, controller="CTA")
        row_specs = [
            (
                substitution_y,
                float(generic["substitution_rate_pct"]),
                wilson_interval(int(generic["substitutions"]), int(generic["shared_eligible"])),
                float(cta["substitution_rate_pct"]),
                wilson_interval(int(cta["substitutions"]), int(cta["shared_eligible"])),
                (
                    rf'${generic["substitutions"]}/{generic["shared_eligible"]}'
                    rf'\rightarrow{cta["substitutions"]}/{cta["shared_eligible"]}$'
                ),
                "Substitution",
            ),
            (
                pair_y,
                float(generic["pairacc_pct"]),
                (
                    float(generic["pairacc_ci95_low_pct"]),
                    float(generic["pairacc_ci95_high_pct"]),
                ),
                float(cta["pairacc_pct"]),
                (float(cta["pairacc_ci95_low_pct"]), float(cta["pairacc_ci95_high_pct"])),
                (
                    rf'${generic["pairacc_both_correct"]}/{generic["pairacc_pairs"]}'
                    rf'\rightarrow{cta["pairacc_both_correct"]}/{cta["pairacc_pairs"]}$'
                ),
                "PairAcc",
            ),
        ]
        ax.text(
            -0.42,
            heading_y,
            label,
            transform=ax.get_yaxis_transform(),
            ha="left",
            va="center",
            fontsize=7.0,
            color=color,
            weight="bold",
            clip_on=False,
        )
        for y, generic_value, generic_ci, cta_value, cta_ci, count_text, row_label in row_specs:
            generic_y = y + 0.11
            cta_y = y - 0.11
            ax.plot(
                [generic_value, cta_value],
                [generic_y, cta_y],
                color=color,
                lw=1.0,
                alpha=0.8,
                zorder=2,
            )
            for value, interval, yy, marker, filled in (
                (generic_value, generic_ci, generic_y, "o", False),
                (cta_value, cta_ci, cta_y, "s", True),
            ):
                ax.errorbar(
                    value,
                    yy,
                    xerr=[[value - interval[0]], [interval[1] - value]],
                    fmt=marker,
                    ms=4.8,
                    mfc=color if filled else PAPER,
                    mec=color,
                    mew=1.0,
                    ecolor=color,
                    elinewidth=0.95,
                    capsize=1.9,
                    capthick=0.8,
                    zorder=3,
                )
            count_ax.text(
                0.03,
                y,
                count_text,
                ha="left",
                va="center",
                fontsize=7.0,
                color=color,
            )
            y_ticks.append(y)
            y_labels.append(row_label)

    for separator in (3.45, 1.20):
        ax.axhline(separator, color=GRID, lw=0.7, ls=(0, (2.5, 2.5)), zorder=0)
        count_ax.axhline(separator, color=GRID, lw=0.7, ls=(0, (2.5, 2.5)), zorder=0)

    ax.set_xlim(-7, 103)
    ax.set_ylim(-0.82, 5.70)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Percent (%)", labelpad=2)
    ax.set_yticks(y_ticks, y_labels)
    clean_axis(ax)
    count_ax.set_xlim(0, 1)
    count_ax.tick_params(axis="y", labelleft=False)
    count_ax.axis("off")
    count_ax.text(
        0.03,
        1.01,
        r"counts ($G\rightarrow C$)",
        transform=count_ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.0,
        color=MUTED,
    )
    legend_handles = [
        Line2D(
            [],
            [],
            marker="o",
            linestyle="none",
            markersize=4.8,
            markerfacecolor=PAPER,
            markeredgecolor=CONTROL,
            markeredgewidth=1.0,
            label="Generic",
        ),
        Line2D(
            [],
            [],
            marker="s",
            linestyle="none",
            markersize=4.8,
            markerfacecolor=CONTROL,
            markeredgecolor=CONTROL,
            markeredgewidth=1.0,
            label="CTA",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.61, 0.992),
        ncol=2,
        frameon=False,
        handletextpad=0.35,
        columnspacing=1.0,
        borderaxespad=0.0,
        labelcolor=MUTED,
    )
    fig.subplots_adjust(left=0.30, right=0.992, top=0.84, bottom=0.16)
    save_variants(fig, stem, "TRI integrated conditional-outcome figure v4")


def transfer_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = [
        row
        for row in rows
        if row["panel"] in {"pairacc", "e2e"}
        and row["dataset"] in {"Authored", "Source-derived"}
    ]
    expected = {
        ("pairacc", "Authored", "Qwen3.5"): (25.0, 6.25, 46.154),
        ("pairacc", "Authored", "GLM-5.1"): (53.125, 28.571, 77.778),
        ("pairacc", "Source-derived", "Qwen3.5"): (3.333, -11.111, 20.0),
        ("pairacc", "Source-derived", "GLM-5.1"): (30.0, 0.0, 55.556),
        ("pairacc", "Source-derived", "DeepSeek"): (10.0, -10.0, 30.0),
        ("e2e", "Authored", "Qwen3.5"): (4.688, 0.0, 9.375),
        ("e2e", "Authored", "GLM-5.1"): (14.062, 8.397, 20.0),
        ("e2e", "Source-derived", "Qwen3.5"): (0.0, -6.667, 6.667),
        ("e2e", "Source-derived", "GLM-5.1"): (18.333, 8.333, 30.0),
        ("e2e", "Source-derived", "DeepSeek"): (3.333, -5.0, 11.667),
    }
    if len(selected) != len(expected):
        raise ValueError(f"transfer figure requires {len(expected)} rows, found {len(selected)}")
    for key, values in expected.items():
        row = one(selected, panel=key[0], dataset=key[1], model=key[2])
        observed = tuple(float(row[field]) for field in ("difference_pp", "ci95_low_pp", "ci95_high_pp"))
        if observed != values:
            raise ValueError(f"transfer figure source mismatch for {key}: {observed}")
    return selected


def draw_transfer(rows: list[dict[str, str]], stem: Path) -> None:
    configure_style()
    data = transfer_rows(rows)
    specs = [
        ("Authored", "Qwen3.5", 4.05, True),
        ("Authored", "GLM-5.1", 3.15, True),
        ("Source-derived", "Qwen3.5", 1.65, False),
        ("Source-derived", "GLM-5.1", 0.75, False),
        ("Source-derived", "DeepSeek", -0.15, False),
    ]
    fig = plt.figure(figsize=(3.35, 2.03))
    grid = fig.add_gridspec(1, 3, width_ratios=[0.76, 1.0, 1.0], wspace=0.15)
    label_ax = fig.add_subplot(grid[0])
    pair_ax = fig.add_subplot(grid[1], sharey=label_ax)
    e2e_ax = fig.add_subplot(grid[2], sharey=label_ax)

    for ax, panel, title, limits, ticks in (
        (pair_ax, "pairacc", "A  PairAcc effect", (-14, 82), [0, 40, 80]),
        (e2e_ax, "e2e", "B  E2E effect", (-8, 31), [0, 10, 20, 30]),
    ):
        ax.axvline(0, color=CONTROL, lw=0.85, zorder=1)
        ax.axhline(2.42, color=GRID, lw=0.75, ls=(0, (2.5, 2.5)), zorder=1)
        for dataset, model, y, filled in specs:
            row = one(data, panel=panel, dataset=dataset, model=model)
            effect = float(row["difference_pp"])
            low = float(row["ci95_low_pp"])
            high = float(row["ci95_high_pp"])
            _, marker, color = MODEL_STYLE[model]
            ax.errorbar(
                effect,
                y,
                xerr=[[effect - low], [high - effect]],
                fmt=marker,
                ms=5.0,
                mfc=color if filled else PAPER,
                mec=color,
                mew=1.0,
                ecolor=color,
                elinewidth=1.0,
                capsize=2.1,
                capthick=0.85,
                zorder=3,
            )
        ax.set_xlim(*limits)
        ax.set_xticks(ticks)
        ax.set_ylim(-0.62, 4.55)
        ax.set_title(title, loc="left", pad=3, weight="bold")
        clean_axis(ax)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", labelleft=False)

    pair_ax.set_xlabel("Delta PairAcc (pp)", labelpad=3)
    e2e_ax.set_xlabel("Delta E2E (pp)", labelpad=3)

    label_ax.set_xlim(0, 1)
    label_ax.set_ylim(-0.62, 4.55)
    label_ax.axis("off")
    label_ax.text(
        0.02,
        4.49,
        "AUTHORED",
        ha="left",
        va="center",
        fontsize=7.0,
        color=INK,
        weight="bold",
    )
    label_ax.text(
        0.02,
        2.42,
        "SOURCE-DERIVED",
        ha="left",
        va="center",
        fontsize=7.0,
        color=RULE,
        weight="bold",
    )
    for y, model in ((4.05, "Qwen"), (3.15, "GLM"), (1.65, "Qwen"), (0.75, "GLM"), (-0.15, "DeepSeek")):
        label_ax.text(0.20, y, model, ha="left", va="center", fontsize=7.1, color=INK)

    fig.subplots_adjust(left=0.02, right=0.985, top=0.87, bottom=0.22)
    save_variants(fig, stem, "TRI equal-width decision-visibility and transfer figure v3")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy-data", type=Path, default=DATA / "matched_pairacc_and_marginals.csv")
    parser.add_argument(
        "--conditional-data",
        type=Path,
        default=DATA / "v7_shared_eligible_pairacc_and_substitution.csv",
    )
    parser.add_argument("--transfer-data", type=Path, default=DATA / "main_figure_paired_scores.csv")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    policy_stem = args.output_dir / "result_policy_discrimination"
    conditional_stem = args.output_dir / "result_conditional_pairing"
    transfer_stem = args.output_dir / "result_decision_transfer"
    draw_policy(read_csv(args.policy_data), policy_stem)
    draw_conditional_pairing(read_csv(args.conditional_data), conditional_stem)
    draw_transfer(read_csv(args.transfer_data), transfer_stem)
    manifest = {
        "status": "main-paper candidate v3; source-derived; no new experiment",
        "source_sha256": {
            args.policy_data.name: sha256(args.policy_data),
            args.conditional_data.name: sha256(args.conditional_data),
            args.transfer_data.name: sha256(args.transfer_data),
        },
        "outputs": {
            "policy": {
                "size_inches": [3.35, 1.92],
                "stem": str(policy_stem),
                "evidence": "v3 Qwen primary/frozen; GLM replication; Rule* post-hoc",
            },
            "conditional_pairing": {
                "size_inches": [3.35, 2.20],
                "stem": str(conditional_stem),
                "evidence": "post-primary ten-schema diagnostic; endpoint-specific denominators",
            },
            "decision_transfer": {
                "size_inches": [3.35, 2.03],
                "stem": str(transfer_stem),
                "evidence": "post-primary matched audits; no pooled effect",
            },
        },
        "minimum_text_pt": 7.0,
        "pdf_fonttype": 42,
        "png_dpi": 400,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
