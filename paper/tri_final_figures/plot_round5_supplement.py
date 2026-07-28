from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


INK = "#29343A"
MUTED = "#738086"
GRID = "#D1D6D7"
PAPER = "#FFFFFF"
QWEN = "#407A7F"
GLM = "#E56D4E"
RULE = "#B9822D"
FIXED = "#7C878B"
PALE = "#EEF3F2"


def apply_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "axes.titlesize": 10.0,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 8.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
            "savefig.pad_inches": 0,
        }
    )


def save(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def load_calibration(report_path: Path) -> list[dict[str, Any]]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    keep = {
        "Generic",
        "CTA",
        "Lifecycle-gated",
        "Always-Lock+validity",
        "Always-Reevaluate",
        "Rule v2 (post-hoc)",
    }
    points: list[dict[str, Any]] = []
    for row in report["results"]:
        if row["dataset"] != "v3" or row["controller"] not in keep:
            continue
        core = row["slices"]["changed_winner_core"]
        points.append(
            {
                "model": row["model"],
                "controller": row["controller"],
                "values": [
                    100 * core["preserve_accuracy"],
                    100 * core["reevaluate_accuracy"],
                    100 * core["pair_accuracy"],
                ],
            }
        )
    gated = [row for row in points if row["controller"] == "Lifecycle-gated"]
    if len(gated) == 2 and gated[0]["values"] == gated[1]["values"]:
        points = [row for row in points if row["controller"] != "Lifecycle-gated"]
        points.append({"model": "Qwen3.5/GLM-5.1", "controller": "Lifecycle-gated", "values": gated[0]["values"]})
    return points


def build_calibration_rulers(points: list[dict[str, Any]], stem: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(4.8, 4.05))
    key_order = [
        ("Qwen3.5", "CTA"),
        ("GLM-5.1", "CTA"),
        ("Qwen3.5/GLM-5.1", "Lifecycle-gated"),
        ("model-independent", "Rule v2 (post-hoc)"),
        ("Qwen3.5", "Generic"),
        ("GLM-5.1", "Generic"),
        ("model-independent", "Always-Lock+validity"),
        ("model-independent", "Always-Reevaluate"),
    ]
    by_key = {(row["model"], row["controller"]): row for row in points}
    y_positions = [7.65, 6.80, 5.95, 4.88, 3.82, 2.97, 1.90, 1.05]
    centers = [6.15, 9.15, 12.15]

    for x, label in zip(centers, ["Preserve", "Reevaluate", "PairAcc"]):
        ax.text(x, 8.62, label, ha="center", va="center", fontsize=8.5, color=INK, weight="bold")
        ax.text(x, 8.25, "0                         100", ha="center", va="center", fontsize=8.0, color=MUTED)

    for (model, controller), y in zip(key_order, y_positions):
        row = by_key[(model, controller)]
        if controller == "CTA":
            color = QWEN if model == "Qwen3.5" else GLM
            marker = "o" if model == "Qwen3.5" else "s"
            label = f"CTA - {'Qwen' if model == 'Qwen3.5' else 'GLM'}"
        elif controller == "Generic":
            color = QWEN if model == "Qwen3.5" else GLM
            marker = "o" if model == "Qwen3.5" else "s"
            label = f"Generic - {'Qwen' if model == 'Qwen3.5' else 'GLM'}"
        elif controller == "Lifecycle-gated":
            color, marker, label = GLM, "D", "Lifecycle-Gated - Q/G"
        elif controller == "Rule v2 (post-hoc)":
            color, marker, label = RULE, "P", "Rule* - post-hoc"
        elif controller == "Always-Lock+validity":
            color, marker, label = FIXED, "v", "Always Lock"
        else:
            color, marker, label = FIXED, "^", "Always Reevaluate"

        filled = controller not in {"Always-Lock+validity", "Always-Reevaluate"}
        ax.scatter(0.35, y, s=35, marker=marker, facecolor=color if filled else PAPER, edgecolor=color, lw=1.0, zorder=4)
        ax.text(0.72, y, label, ha="left", va="center", fontsize=8.5, color=color, weight="bold")
        for x, value in zip(centers, row["values"]):
            left, right = x - 1.13, x + 1.13
            point_x = left + (right - left) * value / 100.0
            ax.plot([left, right], [y - 0.13, y - 0.13], color=GRID, lw=3.1, solid_capstyle="round")
            ax.plot([left, point_x], [y - 0.13, y - 0.13], color=color, lw=2.8, solid_capstyle="round")
            ax.scatter(point_x, y - 0.13, s=23, marker=marker, facecolor=color if filled else PAPER, edgecolor=color, lw=0.9, zorder=5)
            correct = round(value * 32 / 100)
            ax.text(x, y + 0.19, f"{correct}/32", ha="center", va="center", fontsize=8.2, color=INK, weight="bold")

    for y in (6.36, 5.40, 4.35, 2.45):
        ax.plot([0.15, 13.47], [y, y], color=GRID, lw=0.7, ls=(0, (4, 3)))
    ax.text(6.8, 9.30, "Changed-winner calibration uses three independent rulers", ha="center", va="center", fontsize=10.0, color=INK, weight="bold")
    ax.text(6.8, 0.38, "All entries use the same 32 matched changed-winner pairs", ha="center", va="center", fontsize=8.2, color=MUTED)
    ax.set_xlim(0, 13.6)
    ax.set_ylim(0.0, 9.65)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, stem)


def build_external_boundary(stem: Path) -> None:
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(6.8, 6.15), gridspec_kw={"hspace": 0.48, "wspace": 0.48})
    ax_a, ax_b, ax_c, ax_d = axes.flat

    suites = ["ToolSandbox", "AppWorld", "tau3-bench", "API-Bank", "BFCL", "ToolTalk"]
    sizes = ["129 families", "244 families", "2,449 tasks", "528 units", "800 variants", "50 dialogues"]
    near = [1, 1, 0, 0, 0, 0]
    rows = list(range(5, -1, -1))
    ax_a.set_title("A  Public benchmark coverage", loc="left", weight="bold")
    ax_a.set_xlim(0, 10)
    ax_a.set_ylim(-0.7, 6.35)
    ax_a.text(7.2, 6.05, "STRICT", ha="center", va="center", fontsize=8.0, color=MUTED, weight="bold")
    ax_a.text(9.1, 6.05, "NEAR", ha="center", va="center", fontsize=8.0, color=MUTED, weight="bold")
    for suite, size, nm, y in zip(suites, sizes, near, rows):
        ax_a.text(0.0, y + 0.13, suite, ha="left", va="center", fontsize=8.2, color=INK, weight="bold")
        ax_a.text(0.0, y - 0.18, size, ha="left", va="center", fontsize=7.3, color=MUTED)
        ax_a.scatter(7.05, y, s=30, marker="o", facecolor=PAPER, edgecolor=FIXED, lw=1.1)
        ax_a.text(7.42, y, "0", ha="left", va="center", fontsize=8.0, color=FIXED, weight="bold")
        ax_a.scatter(8.95, y, s=30, marker="D", facecolor=QWEN if nm else PAPER, edgecolor=QWEN if nm else GRID, lw=1.0)
        ax_a.text(9.32, y, str(nm), ha="left", va="center", fontsize=8.0, color=QWEN if nm else MUTED, weight="bold")
        ax_a.plot([0, 9.85], [y - 0.48, y - 0.48], color=GRID, lw=0.5)
    ax_a.text(0, -0.55, "No strict native opportunity under the author checklist", ha="left", va="center", fontsize=8.0, color=MUTED, style="italic")
    ax_a.set_axis_off()

    labels = ["AgentDojo\nQwen", "AgentDojo\nGLM", "STATE-Bench\nQwen", "STATE-Bench\nGLM"]
    counts = [(2, 7), (0, 8), (0, 10), (0, 7)]
    rates = [100 * a / b for a, b in counts]
    rows = [2.55, 1.70, 0.85, 0.0]
    ax_b.set_title("B  Source-anchored ordinary history", loc="left", weight="bold")
    for label, rate, count, y in zip(labels, rates, counts, rows):
        color = QWEN if rate > 0 else FIXED
        ax_b.plot([0, rate], [y, y], color=GRID, lw=2.2, solid_capstyle="round")
        ax_b.scatter(rate, y, s=48, marker="D" if rate > 0 else "o", facecolor=color if rate > 0 else PAPER, edgecolor=color, lw=1.1, zorder=3)
        ax_b.text(rate + 1.4, y, f"{count[0]}/{count[1]}", ha="left", va="center", fontsize=8.2, color=color, weight="bold")
    ax_b.set_xlim(-1, 36)
    ax_b.set_ylim(-0.65, 3.65)
    ax_b.set_yticks(rows)
    ax_b.set_yticklabels(labels)
    ax_b.set_xticks([0, 10, 20, 30])
    ax_b.set_xlabel("Conditional substitution (%)")
    ax_b.grid(axis="x", color=GRID, lw=0.6)
    ax_b.text(35.5, 3.52, "positive in one slice", ha="right", va="center", fontsize=8.0, color=MUTED, style="italic")
    for spine in ("top", "right", "left"):
        ax_b.spines[spine].set_visible(False)
    ax_b.tick_params(axis="y", length=0, pad=2)

    slices = ["All\n(n=100)", "Actionable\n(n=30)", "Reject\n(n=20)", "Dynamic\n(n=50)"]
    majority = [86.0, 86.7, 55.0, 98.0]
    unanimous = [72.0, 63.3, 25.0, 96.0]
    rows = [2.40, 1.60, 0.80, 0.0]
    ax_c.set_title("C  Human agreement by construct slice", loc="left", weight="bold")
    for label, maj, uni, y in zip(slices, majority, unanimous, rows):
        ax_c.plot([uni, maj], [y, y], color=GRID, lw=2.4, solid_capstyle="round")
        ax_c.scatter(uni, y, s=43, marker="o", facecolor=PAPER, edgecolor=FIXED, lw=1.1, zorder=3)
        ax_c.scatter(maj, y, s=43, marker="s", facecolor=GLM, edgecolor=GLM, lw=1.0, zorder=3)
        ax_c.text(maj + 1.4, y + 0.13, f"{maj:.0f}", ha="left", va="center", fontsize=8.0, color=GLM, weight="bold")
        ax_c.text(uni - 1.4, y - 0.15, f"{uni:.0f}", ha="right", va="center", fontsize=8.0, color=FIXED)
    ax_c.set_xlim(15, 105)
    ax_c.set_ylim(-0.65, 3.35)
    ax_c.set_yticks(rows)
    ax_c.set_yticklabels(slices)
    ax_c.set_xticks([20, 40, 60, 80, 100])
    ax_c.set_xlabel("Agreement (%)")
    ax_c.grid(axis="x", color=GRID, lw=0.6)
    ax_c.legend(
        handles=[
            Line2D([0], [0], marker="s", color="none", markerfacecolor=GLM, markeredgecolor=GLM, label="Majority-gold"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=PAPER, markeredgecolor=FIXED, label="Unanimous"),
        ],
        loc="upper left",
        ncol=2,
        columnspacing=0.8,
        handletextpad=0.3,
        frameon=False,
    )
    for spine in ("top", "right", "left"):
        ax_c.spines[spine].set_visible(False)
    ax_c.tick_params(axis="y", length=0)

    measured = ["Controlled matched pairs", "Authored schema/state transfer", "Referent-core human validation"]
    unresolved = ["Open-language generalization", "Native coverage recall", "Deployment prevalence"]
    ax_d.set_title("D  Evidence boundary", loc="left", weight="bold")
    ax_d.set_xlim(0, 10)
    ax_d.set_ylim(0, 7)
    ax_d.text(0.4, 6.15, "MEASURED", fontsize=8.0, color=GLM, weight="bold")
    for i, label in enumerate(measured):
        y = 5.55 - i * 0.82
        ax_d.scatter(0.65, y, s=55, marker="s", facecolor=GLM, edgecolor=GLM)
        ax_d.text(1.08, y, label, ha="left", va="center", fontsize=8.1, color=INK)
    ax_d.text(0.4, 2.82, "UNRESOLVED", fontsize=8.0, color=QWEN, weight="bold")
    for i, label in enumerate(unresolved):
        y = 2.22 - i * 0.82
        ax_d.scatter(0.65, y, s=55, marker="s", facecolor=PAPER, edgecolor=QWEN, lw=1.2)
        ax_d.text(1.08, y, label, ha="left", va="center", fontsize=8.1, color=INK)
    ax_d.set_axis_off()

    fig.subplots_adjust(left=0.10, right=0.985, top=0.95, bottom=0.08)
    save(fig, stem)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Generate round-5 TRI supplement figures.")
    parser.add_argument(
        "--calibration-report",
        type=Path,
        default=root / "experiments" / "tri_artifact" / "reports" / "matched_pair_consistency.json",
    )
    parser.add_argument("--output-dir", type=Path, default=root / "paper" / "tri_final_figures" / "outputs" / "round5")
    args = parser.parse_args()
    build_calibration_rulers(load_calibration(args.calibration_report), args.output_dir / "fig_s2_changed_calibration_round5")
    build_external_boundary(args.output_dir / "fig_s8_external_boundary_round5")


if __name__ == "__main__":
    main()
