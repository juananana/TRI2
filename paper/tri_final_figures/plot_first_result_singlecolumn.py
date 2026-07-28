#!/usr/bin/env python3
"""Draw TRI's first quantitative result figure from source-derived CSV data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DATA = SCRIPT_DIR / "data" / "summary_csv" / "matched_pairacc_and_marginals.csv"
FALLBACK_DATA = PROJECT_DATA
DEFAULT_DATA = PROJECT_DATA if PROJECT_DATA.exists() else FALLBACK_DATA
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "outputs" if PROJECT_DATA.exists() else SCRIPT_DIR
DEFAULT_STEM = "fig_resolution_policy_phase_space_singlecolumn" if PROJECT_DATA.exists() else "tri_first_result_figure"

COLORS = {
    "ink": "#253238",
    "muted": "#66747A",
    "grid": "#C1CBD0",
    "generic": "#5E379D",
    "generic_text": "#5E379D",
    "cta": "#2F74B8",
    "lifecycle": "#9A4C00",
    "posthoc": "#59636B",
    "control": "#9AA5AA",
    "selective_bg": "#E0EDF8",
    "reevaluate_bg": "#EEE8F6",
    "lock_bg": "#F8EEE4",
    "neutral_bg": "#F2F4F5",
}

CONTROLLER_LABELS = {
    "Generic": "Generic",
    "CTA": "CTA",
    "Lifecycle-free": "Lifecycle-Actor",
    "Lifecycle-gated": "Lifecycle-Gated",
    "Always-Lock+validity": "Unconditional policies",
    "Always-Reevaluate": "Unconditional policies",
    "Rule v2 (post-hoc)": "Rule* (post-hoc)",
}

CONTROLLER_COLORS = {
    "Generic": COLORS["generic"],
    "CTA": COLORS["cta"],
    "Lifecycle-free": COLORS["lifecycle"],
    "Lifecycle-gated": COLORS["lifecycle"],
    "Always-Lock+validity": COLORS["control"],
    "Always-Reevaluate": COLORS["control"],
    "Rule v2 (post-hoc)": COLORS["posthoc"],
}

MODEL_MARKERS = {"Qwen3.5": "o", "GLM-5.1": "s", "model-independent": "D"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--stem", default=DEFAULT_STEM)
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["dataset"] != "v3" or row["slice"] not in {"all", "changed_winner_core"}:
                continue
            parsed: dict[str, object] = dict(row)
            for field in (
                "pairs",
                "preserve_correct",
                "reevaluate_correct",
                "both_correct",
            ):
                parsed[field] = int(row[field])
            for field in (
                "preserve_accuracy_pct",
                "reevaluate_accuracy_pct",
                "pairacc_pct",
            ):
                parsed[field] = float(row[field])
            rows.append(parsed)
    return rows


def style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8.2,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.2,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
        }
    )


def by_key(rows: list[dict[str, object]], slice_name: str) -> dict[tuple[str, str], dict[str, object]]:
    return {
        (str(row["model"]), str(row["controller"])): row
        for row in rows
        if row["slice"] == slice_name
    }


def panel_phase_space(ax: plt.Axes, rows: list[dict[str, object]]) -> None:
    """Marginal policy space; the matched score is shown in the aligned strip below."""
    data = by_key(rows, "all")
    ax.axvspan(50, 100, ymin=0.5, ymax=1.0, color=COLORS["selective_bg"], zorder=0)
    ax.axvspan(0, 50, ymin=0.5, ymax=1.0, color=COLORS["reevaluate_bg"], zorder=0)
    ax.axvspan(50, 100, ymin=0.0, ymax=0.5, color=COLORS["lock_bg"], zorder=0)
    ax.axvspan(0, 50, ymin=0.0, ymax=0.5, color=COLORS["neutral_bg"], zorder=0)
    ax.axvline(50, color=COLORS["grid"], linestyle=(0, (4, 3)), linewidth=0.8)
    ax.axhline(50, color=COLORS["grid"], linestyle=(0, (4, 3)), linewidth=0.8)

    # Generic points are the only individual model points that are separated at this scale.
    for model in ("Qwen3.5", "GLM-5.1"):
        row = data[(model, "Generic")]
        ax.scatter(row["preserve_accuracy_pct"], row["reevaluate_accuracy_pct"], s=42,
                   marker=MODEL_MARKERS[model], facecolor=COLORS["generic"],
                   edgecolor=COLORS["ink"], linewidth=0.8, zorder=5)

    # CTA and lifecycle probes occupy a narrow, high-performing envelope; show its exact range.
    ax.add_patch(Rectangle((91.25, 96.25), 8.75, 3.75, facecolor="#E8F1FA",
                           edgecolor=COLORS["cta"], linewidth=1.2, zorder=4))
    ax.plot([91.25, 100.0], [96.25, 96.25], color=COLORS["lifecycle"], linewidth=1.2, zorder=5)
    ax.text(96.0, 98.0, "CTA/Life.\n29--32/32", fontsize=5.6,
            ha="center", va="center", color=COLORS["ink"])

    for controller, label, xytext in (("Always-Reevaluate", "Always-Reeval.", (-5, -18)),
                                       ("Always-Lock+validity", "Always-Lock", (-5, 13))):
        row = data[("model-independent", controller)]
        ax.scatter(row["preserve_accuracy_pct"], row["reevaluate_accuracy_pct"], s=52,
                   marker="D", facecolor="white", edgecolor=COLORS["ink"], linewidth=1.0, zorder=6)
        ax.annotate(label, (row["preserve_accuracy_pct"], row["reevaluate_accuracy_pct"]),
                    xytext=xytext, textcoords="offset points", fontsize=6.8,
                    ha="left" if xytext[0] > 0 else "right", va="center", color=COLORS["ink"])

    rule = data[("model-independent", "Rule v2 (post-hoc)")]
    ax.scatter(rule["preserve_accuracy_pct"], rule["reevaluate_accuracy_pct"], s=55,
                marker="D", facecolor="white", edgecolor=COLORS["posthoc"], linewidth=1.4, zorder=6)
    ax.annotate("Rule*", (rule["preserve_accuracy_pct"], rule["reevaluate_accuracy_pct"]),
                xytext=(-5, -16), textcoords="offset points", fontsize=7.0,
                ha="right", va="center", color=COLORS["posthoc"])

    ax.text(24, 57, "Reevaluate-dominant", ha="center", va="center", fontsize=7.2, color=COLORS["muted"])
    ax.text(76, 57, "Both marginals high", ha="center", va="center", fontsize=7.2, color=COLORS["muted"])
    ax.text(76, 38, "Preserve-dominant", ha="center", va="center", fontsize=7.2, color=COLORS["muted"])
    ax.set_xlim(0, 106)
    ax.set_ylim(0, 106)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Reevaluate accuracy (%)")
    ax.set_title("A  Policy marginals", loc="left", weight="bold", pad=5)
    ax.spines[["top", "right"]].set_visible(False)


def panel_pairacc(ax: plt.Axes, rows: list[dict[str, object]]) -> None:
    """Ranked matched-pair scores, aligned with the phase-space panel."""
    data = by_key(rows, "changed_winner_core")
    row_defs = [
        ("Always-Lock", ("Always-Lock+validity",)),
        ("Reeval. extreme", ("Always-Reevaluate",)),
        ("Generic", ("Generic",)),
        ("CTA", ("CTA",)),
        ("Lifecycle", ("Lifecycle-free", "Lifecycle-gated")),
        ("Rule*", ("Rule v2 (post-hoc)",)),
    ]
    y_positions = list(range(len(row_defs)))[::-1]
    for y, (label, controllers) in zip(y_positions, row_defs):
        if label in {"Always-Lock", "Reeval. extreme", "Rule*"}:
            controller = controllers[0]
            row = data[("model-independent", controller)]
            value, count = float(row["pairacc_pct"]), int(row["both_correct"])
            edge = COLORS["posthoc"] if label == "Rule*" else COLORS["ink"]
            ax.scatter(value, y, s=44, marker="D", facecolor="white", edgecolor=edge, linewidth=1.1, zorder=4)
            ax.text(109, y, f"{count}/32", va="center", ha="center", fontsize=6.7, color=edge)
        else:
            controller = controllers[0]
            offsets = {"Qwen3.5": 0.10, "GLM-5.1": -0.10}
            counts = {}
            for model in ("Qwen3.5", "GLM-5.1"):
                row = data[(model, controller)]
                value, count = float(row["pairacc_pct"]), int(row["both_correct"])
                counts[model] = count
                yy = y + offsets[model]
                ax.scatter(value, yy, s=38, marker=MODEL_MARKERS[model],
                           facecolor=CONTROLLER_COLORS.get(controller, COLORS["lifecycle"]),
                           edgecolor=COLORS["ink"], linewidth=0.7, zorder=4)
            ax.text(108, y, f"{counts['Qwen3.5']} / {counts['GLM-5.1']}",
                    va="center", ha="center", fontsize=6.7, color=COLORS["ink"])
    ax.axvspan(0, 50, color=COLORS["reevaluate_bg"], zorder=0)
    ax.axvspan(50, 100, color=COLORS["selective_bg"], zorder=0)
    ax.axvline(50, color=COLORS["grid"], linestyle=(0, (4, 3)), linewidth=0.8, zorder=1)
    ax.set_xlim(0, 116)
    ax.set_ylim(-0.55, len(row_defs) - 0.45)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks(y_positions, [label for label, _ in row_defs])
    ax.set_xlabel("Changed-winner PairAcc (%)")
    ax.set_title("B  Matched PairAcc", loc="left", weight="bold", pad=5)
    ax.grid(axis="x", color="white", linewidth=0.8, zorder=1)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.text(108, 5.28, "Qwen / GLM", fontsize=6.2, color=COLORS["muted"], va="bottom", ha="center")


def contrast_ratio(hex_color: str) -> float:
    rgb = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in rgb]
    luminance = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    return 1.05 / (luminance + 0.05)


def save_outputs(fig: plt.Figure, output_dir: Path, data_path: Path, stem_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = output_dir / stem_name
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=400)
    plt.close(fig)

    with Image.open(stem.with_suffix(".png")) as color:
        color.convert("L").save(output_dir / f"{stem_name}_grayscale.png", dpi=(400, 400))
        color.convert("RGB").save(stem.with_suffix(".pdf"), resolution=400)

    digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
    manifest = {
        "source_csv": str(data_path.resolve()),
        "source_sha256": digest,
        "evidence": "v3 Qwen primary/frozen; GLM post-primary; Rule* post-hoc",
        "figure_size_inches": [3.25, 4.25],
        "minimum_text_pt": 5.6,
        "raster_dpi": 400,
        "text_contrast_on_white": {
            color: round(contrast_ratio(COLORS[color]), 2)
            for color in ("ink", "generic_text", "cta", "lifecycle", "posthoc")
        },
        "note": "All colored text exceeds 4.5:1 contrast on white; quadrant labels use dark neutral text.",
    }
    (output_dir / f"{stem_name}_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    os.environ.setdefault("MPLCONFIGDIR", str(args.output_dir / ".mplconfig"))
    style()
    rows = load_rows(args.data)
    fig = plt.figure(figsize=(3.25, 4.25))
    grid = fig.add_gridspec(2, 1, height_ratios=[2.25, 1.5], hspace=0.40)
    panel_phase_space(fig.add_subplot(grid[0]), rows)
    panel_pairacc(fig.add_subplot(grid[1]), rows)
    fig.subplots_adjust(left=0.28, right=0.985, bottom=0.11, top=0.97)
    save_outputs(fig, args.output_dir, args.data, args.stem)


if __name__ == "__main__":
    main()
