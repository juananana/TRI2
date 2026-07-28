from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


INK = "#29343A"
MUTED = "#68767B"
GRID = "#CDD4D6"
PAPER = "#FFFFFF"
CORAL = "#B6534F"
CORAL_LIGHT = "#F3DEDB"
TEAL = "#2D746F"
TEAL_LIGHT = "#DCEBE8"
AMBER = "#98691F"
AMBER_LIGHT = "#F3E8D2"
BLUE = "#50749A"
BLUE_LIGHT = "#DFE7EF"
GRAY_LIGHT = "#EDF0F1"

MODELS = ["Qwen3.5", "GLM-5.1", "DeepSeek"]
MODEL_LABELS = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM", "DeepSeek": "DeepSeek"}
MODEL_MARKERS = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}


def apply_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 7.7,
            "axes.labelsize": 7.7,
            "axes.titlesize": 8.8,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 7.2,
            "axes.linewidth": 0.7,
            "lines.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
            "savefig.pad_inches": 0,
        }
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def row_where(rows: list[dict[str, str]], **conditions: str) -> dict[str, str]:
    matches = [row for row in rows if all(row[key] == value for key, value in conditions.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {conditions}, found {len(matches)}")
    return matches[0]


def save(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"), metadata={"Creator": "TRI figure generator"})
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    plt.close(fig)


def validate_paired_scores(rows: list[dict[str, str]]) -> None:
    for row in rows:
        left = 100 * int(row["left_num"]) / int(row["left_den"])
        right = 100 * int(row["right_num"]) / int(row["right_den"])
        reported = float(row["difference_pp"])
        if abs((right - left) - reported) > 0.11:
            raise ValueError(f"Effect mismatch in {row}")


def build_policy_rulers(rows: list[dict[str, str]], stem: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.72))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    def values_for(controller: str, model: str) -> tuple[list[float], list[str]]:
        all_row = row_where(rows, dataset="v3", model=model, controller=controller, slice="all")
        changed = row_where(
            rows,
            dataset="v3",
            model=model,
            controller=controller,
            slice="changed_winner_core",
        )
        return (
            [
                float(all_row["preserve_accuracy_pct"]),
                float(all_row["reevaluate_accuracy_pct"]),
                float(changed["pairacc_pct"]),
            ],
            [
                f"{int(float(all_row['preserve_correct']))}/80",
                f"{int(float(all_row['reevaluate_correct']))}/80",
                f"{int(float(changed['both_correct']))}/32",
            ],
        )

    entries: list[tuple[str, list[float], list[str], str, str, bool]] = []
    for controller, color in (("CTA", TEAL), ("Generic", CORAL)):
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
    entries.append(("Rule* · post-hoc", values, counts, AMBER, "P", True))
    values, counts = values_for("Always-Lock+validity", "model-independent")
    entries.append(("Always Lock", values, counts, MUTED, "v", False))
    values, counts = values_for("Always-Reevaluate", "model-independent")
    entries.append(("Always Re-eval.", values, counts, MUTED, "^", False))

    ax.text(
        0.50,
        0.962,
        "PairAcc exposes one-sided policies",
        ha="center",
        va="center",
        fontsize=8.8,
        color=INK,
        weight="bold",
    )
    ax.text(0.58, 0.885, "MARGINALS", ha="center", color=MUTED, fontsize=7.4, weight="bold")
    ax.text(0.90, 0.885, "JOINT", ha="center", color=TEAL, fontsize=7.4, weight="bold")
    centers = [0.53, 0.72, 0.91]
    for x, label in zip(centers, ("Preserve", "Reevaluate", "PairAcc")):
        ax.text(x, 0.825, label, ha="center", color=INK, fontsize=7.5, weight="bold")

    order = [0, 1, 4, 2, 3, 5, 6]
    y_positions = [0.705, 0.622, 0.520, 0.414, 0.331, 0.220, 0.137]
    half_track = 0.066
    for entry_index, y in zip(order, y_positions):
        label, values, counts, color, marker, filled = entries[entry_index]
        ax.scatter(
            0.035,
            y,
            s=24,
            marker=marker,
            facecolor=color if filled else PAPER,
            edgecolor=color,
            lw=0.8,
            zorder=4,
        )
        ax.text(0.067, y, label, ha="left", va="center", fontsize=7.4, color=color, weight="bold")
        for x, value, count in zip(centers, values, counts):
            left, right = x - half_track, x + half_track
            point_x = left + (right - left) * value / 100.0
            ax.plot([left, right], [y - 0.019, y - 0.019], color=GRID, lw=2.2, solid_capstyle="round")
            ax.plot([left, point_x], [y - 0.019, y - 0.019], color=color, lw=2.05, solid_capstyle="round")
            ax.scatter(
                point_x,
                y - 0.019,
                s=15,
                marker=marker,
                facecolor=color if filled else PAPER,
                edgecolor=color,
                lw=0.7,
                zorder=5,
            )
            ax.text(x, y + 0.029, count, ha="center", va="center", fontsize=7.5, color=INK, weight="bold")

    for y in (0.571, 0.467, 0.276):
        ax.plot([0.018, 0.985], [y, y], color=GRID, lw=0.6, ls=(0, (3, 3)))
    ax.text(0.57, 0.042, "Both requests must be correct", ha="center", color=MUTED, fontsize=7.3)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.995, bottom=0.005)
    save(fig, stem)


def build_substitution_flow(rows: list[dict[str, str]], stem: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.05))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    ax.text(
        0.50,
        0.955,
        "Target use diverges after correct binding",
        ha="center",
        va="center",
        fontsize=8.7,
        color=INK,
        weight="bold",
    )
    ax.text(0.50, 0.902, "same eligible Preserve rows run through both probes", ha="center", fontsize=7.2, color=MUTED)
    ax.text(0.255, 0.833, "SHARED COHORT", ha="center", fontsize=6.8, color=MUTED, weight="bold")
    ax.plot([0.430, 0.470], [0.840, 0.840], color=TEAL, lw=5.0, solid_capstyle="butt")
    ax.text(0.480, 0.840, "kept target", ha="left", va="center", fontsize=7.0, color=INK)
    ax.plot([0.675, 0.715], [0.840, 0.840], color=CORAL, lw=5.0, solid_capstyle="butt")
    ax.text(0.725, 0.840, "refreshed winner", ha="left", va="center", fontsize=7.0, color=INK)

    group_centers = {"Qwen3.5": 0.69, "GLM-5.1": 0.43, "DeepSeek": 0.17}
    bar_left, bar_right, bar_h = 0.475, 0.965, 0.060
    for index, model in enumerate(MODELS):
        generic = row_where(rows, model=model, controller="Generic")
        cta = row_where(rows, model=model, controller="CTA")
        n = int(generic["shared_eligible"])
        replaced = int(generic["substitutions"])
        kept = n - replaced
        if int(cta["shared_eligible"]) != n or int(cta["substitutions"]) != 0:
            raise ValueError(f"Unexpected shared cohort in {model}")

        center = group_centers[model]
        generic_y = center + 0.045
        cta_y = center - 0.055
        model_fontsize = 7.0 if model == "DeepSeek" else 7.7
        ax.text(0.015, center + 0.005, MODEL_LABELS[model], ha="left", va="center", fontsize=model_fontsize, color=INK, weight="bold")
        badge = FancyBboxPatch(
            (0.210, center - 0.033),
            0.090,
            0.066,
            boxstyle="round,pad=0.005,rounding_size=0.012",
            facecolor=GRAY_LIGHT,
            edgecolor=MUTED,
            linewidth=0.65,
        )
        ax.add_patch(badge)
        ax.text(0.255, center, f"n={n}", ha="center", va="center", fontsize=7.2, color=INK, weight="bold")
        fork_x = 0.327
        ax.plot([0.300, fork_x], [center, center], color=GRID, lw=0.8)
        ax.plot([fork_x, fork_x], [cta_y, generic_y], color=GRID, lw=0.8)
        ax.plot([fork_x, 0.342], [generic_y, generic_y], color=GRID, lw=0.8)
        ax.plot([fork_x, 0.342], [cta_y, cta_y], color=GRID, lw=0.8)
        ax.text(0.350, generic_y, "Generic", ha="left", va="center", fontsize=7.2, color=CORAL, weight="bold")
        ax.text(0.350, cta_y, "CTA", ha="left", va="center", fontsize=7.2, color=TEAL, weight="bold")

        width = bar_right - bar_left
        kept_width = width * kept / n
        replaced_width = width - kept_width
        ax.add_patch(Rectangle((bar_left, generic_y - bar_h / 2), kept_width, bar_h, facecolor=TEAL_LIGHT, edgecolor=TEAL, linewidth=0.7))
        ax.add_patch(Rectangle((bar_left + kept_width, generic_y - bar_h / 2), replaced_width, bar_h, facecolor=CORAL_LIGHT, edgecolor=CORAL, linewidth=0.7))
        ax.text(bar_left + kept_width / 2, generic_y, f"{kept} kept", ha="center", va="center", fontsize=7.0, color=TEAL, weight="bold")
        ax.text(bar_left + kept_width + replaced_width / 2, generic_y, f"{replaced} replaced", ha="center", va="center", fontsize=7.0, color=CORAL, weight="bold")

        ax.add_patch(Rectangle((bar_left, cta_y - bar_h / 2), width, bar_h, facecolor=TEAL_LIGHT, edgecolor=TEAL, linewidth=0.7))
        ax.text((bar_left + bar_right) / 2, cta_y, f"{n} kept · 0 replaced", ha="center", va="center", fontsize=7.1, color=TEAL, weight="bold")

        if index < len(MODELS) - 1:
            ax.plot([0.015, 0.985], [center - 0.135, center - 0.135], color=GRID, lw=0.55, ls=(0, (3, 3)))

    fig.subplots_adjust(left=0.01, right=0.99, top=0.995, bottom=0.005)
    save(fig, stem)


def add_node(
    ax: plt.Axes,
    center: tuple[float, float],
    size: tuple[float, float],
    text: str,
    facecolor: str,
    edgecolor: str,
    textcolor: str = INK,
    fontsize: float = 7.2,
) -> tuple[float, float, float, float]:
    x, y = center
    width, height = size
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.005,rounding_size=0.012",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=0.75,
        zorder=3,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color=textcolor, weight="bold", zorder=4)
    return (x - width / 2, y - height / 2, x + width / 2, y + height / 2)


def connect(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = GRID) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-",
            connectionstyle="arc3,rad=0.0",
            linewidth=0.9,
            color=color,
            zorder=1,
        )
    )


def build_sqlite_tree(rows: list[dict[str, str]], stem: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.55))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    ax.text(0.50, 0.965, "Target errors reach SQLite writes", ha="center", fontsize=8.7, color=INK, weight="bold")
    ax.text(0.50, 0.922, "all 40 model-facing trajectories are accounted for", ha="center", fontsize=7.2, color=MUTED)

    layouts = {
        "Qwen3.5": {"root_y": 0.700, "opp_y": 0.505},
        "GLM-5.1": {"root_y": 0.285, "opp_y": 0.055},
    }
    for model in ("Qwen3.5", "GLM-5.1"):
        row = row_where(rows, model=model, controller="Generic")
        total = int(row["tasks"])
        correct = int(row["correct_final_state"])
        strict = int(row["core_tri_write"])
        fallback = int(row["fallback_wrong_write"])
        reject = int(row["unneeded_reject"])
        wrong = strict + fallback
        if correct + wrong + reject != total:
            raise ValueError(f"SQLite outcomes do not sum to {total}: {row}")

        root_y = layouts[model]["root_y"]
        root_box = add_node(ax, (0.085, root_y), (0.145, 0.092), f"{MODEL_LABELS[model]}\nn={total}", BLUE_LIGHT, BLUE, fontsize=7.4)
        correct_y = root_y + 0.105
        wrong_y = root_y - 0.025
        reject_y = root_y - 0.145
        add_node(ax, (0.385, correct_y), (0.245, 0.078), f"{correct} correct states", TEAL_LIGHT, TEAL, TEAL)
        add_node(ax, (0.385, wrong_y), (0.245, 0.078), f"{wrong} wrong writes", CORAL_LIGHT, CORAL, CORAL)
        connect(ax, (root_box[2], root_y), (0.262, correct_y))
        connect(ax, (root_box[2], root_y), (0.262, wrong_y))

        if reject:
            add_node(ax, (0.385, reject_y), (0.245, 0.078), f"{reject} unneeded rejects", GRAY_LIGHT, MUTED, MUTED)
            connect(ax, (root_box[2], root_y), (0.262, reject_y))

        strict_y = wrong_y + 0.047
        fallback_y = wrong_y - 0.058
        add_node(ax, (0.755, strict_y), (0.275, 0.072), f"{strict} strict TRI", CORAL_LIGHT, CORAL, CORAL)
        add_node(ax, (0.755, fallback_y), (0.275, 0.072), f"{fallback} fallback-policy", AMBER_LIGHT, AMBER, AMBER)
        connect(ax, (0.508, wrong_y), (0.618, strict_y), CORAL)
        connect(ax, (0.508, wrong_y), (0.618, fallback_y), AMBER)

        strict_writes = int(row["strict_core_writes"])
        strict_opps = int(row["strict_core_opportunities"])
        stable_writes = int(row["stable_writes"])
        stable_opps = int(row["stable_opportunities"])
        opportunity_y = layouts[model]["opp_y"]
        ax.text(
            0.535,
            opportunity_y,
            f"strict:  changed {strict_writes}/{strict_opps}  ·  stable {stable_writes}/{stable_opps}",
            ha="center",
            va="center",
            fontsize=7.0,
            color=MUTED,
            weight="bold",
        )

    ax.plot([0.015, 0.985], [0.472, 0.472], color=GRID, lw=0.65, ls=(0, (3, 3)))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.995, bottom=0.005)
    save(fig, stem)


def score_x(score: float) -> float:
    return 0.245 + 0.345 * score / 100.0


def draw_paired_panel(ax: plt.Axes, rows: list[dict[str, str]], panel: str, title: str) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    panel_rows = [row for row in rows if row["panel"] == panel]
    y_positions = (
        [0.70, 0.58, 0.39, 0.27, 0.15]
        if panel == "pairacc"
        else [0.72, 0.62, 0.47, 0.37, 0.22, 0.12, 0.02]
    )
    if len(panel_rows) != len(y_positions):
        raise ValueError(f"Unexpected row count for {panel}")

    ax.text(0.01, 0.965, title, ha="left", va="center", fontsize=8.5, color=INK, weight="bold")
    ax.text(0.245, 0.865, "0", ha="center", fontsize=6.8, color=MUTED)
    ax.text(score_x(50), 0.865, "score 50", ha="center", fontsize=6.8, color=MUTED)
    ax.text(0.590, 0.865, "100", ha="center", fontsize=6.8, color=MUTED)
    ax.text(0.700, 0.865, "exact counts", ha="center", fontsize=6.8, color=MUTED, weight="bold")
    ax.text(0.880, 0.865, "Δ pp [95% CI]", ha="center", fontsize=6.8, color=MUTED, weight="bold")
    for value in (0, 50, 100):
        x = score_x(value)
        ax.plot([x, x], [0.0, 0.83], color=GRID, lw=0.45, zorder=0)

    last_dataset = None
    for row, y in zip(panel_rows, y_positions):
        dataset = row["dataset"]
        if last_dataset is not None and dataset != last_dataset:
            ax.plot([0.01, 0.99], [y + 0.09, y + 0.09], color=GRID, lw=0.55, ls=(0, (3, 3)))
        last_dataset = dataset
        model = row["model"]
        left_num, left_den = int(row["left_num"]), int(row["left_den"])
        right_num, right_den = int(row["right_num"]), int(row["right_den"])
        left_score = 100 * left_num / left_den
        right_score = 100 * right_num / right_den
        x_left, x_right = score_x(left_score), score_x(right_score)
        marker = MODEL_MARKERS[model]
        label = f"{dataset} / {MODEL_LABELS[model]}"
        ax.text(0.01, y, label, ha="left", va="center", fontsize=7.2, color=INK, weight="bold")
        if abs(x_right - x_left) < 0.004:
            ax.plot([x_left, x_right], [y + 0.010, y - 0.010], color=MUTED, lw=0.9, zorder=1)
            left_y, right_y = y + 0.010, y - 0.010
        else:
            ax.add_patch(
                FancyArrowPatch(
                    (x_left, y),
                    (x_right, y),
                    arrowstyle="-|>",
                    mutation_scale=5.5,
                    linewidth=0.9,
                    color=MUTED,
                    shrinkA=3.5,
                    shrinkB=3.5,
                    zorder=1,
                )
            )
            left_y = right_y = y
        ax.scatter(x_left, left_y, s=24, marker=marker, facecolor=PAPER, edgecolor=MUTED, linewidth=0.9, zorder=3)
        ax.scatter(x_right, right_y, s=28, marker=marker, facecolor=BLUE, edgecolor=BLUE, linewidth=0.8, zorder=4)
        count_text = f"{left_num}→{right_num}/{right_den}" if left_den == right_den else f"{left_num}/{left_den}→{right_num}/{right_den}"
        ax.text(0.700, y, count_text, ha="center", va="center", fontsize=7.0, color=INK, weight="bold")
        diff = float(row["difference_pp"])
        low = float(row["ci95_low_pp"])
        high = float(row["ci95_high_pp"])
        interval_color = BLUE if low > 0 else MUTED
        ax.text(0.880, y, f"{diff:+.1f} [{low:.1f},{high:.1f}]", ha="center", va="center", fontsize=6.9, color=interval_color, weight="bold")


def build_paired_transfer_matrix(rows: list[dict[str, str]], stem: Path) -> None:
    apply_style()
    validate_paired_scores(rows)
    fig = plt.figure(figsize=(6.85, 5.15))
    fig.text(0.50, 0.982, "Decision visibility: authored PairAcc gains, mixed transfer", ha="center", va="center", fontsize=9.0, color=INK, weight="bold")
    legend = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PAPER, markeredgecolor=MUTED, markersize=5.0, label="History-only"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=BLUE, markeredgecolor=BLUE, markersize=5.0, label="Decision-visible"),
    ]
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.50, 0.956), frameon=False, ncol=2, handletextpad=0.35, columnspacing=1.2)
    ax_pair = fig.add_axes([0.035, 0.575, 0.93, 0.315])
    ax_e2e = fig.add_axes([0.035, 0.205, 0.93, 0.325])
    draw_paired_panel(ax_pair, rows, "pairacc", "A  Changed-winner PairAcc")
    draw_paired_panel(ax_e2e, rows, "e2e", "B  Actionable E2E")

    boundary = row_where(rows, panel="rule_boundary")
    ax_rule = fig.add_axes([0.04, 0.035, 0.92, 0.105])
    ax_rule.set_xlim(0, 1)
    ax_rule.set_ylim(0, 1)
    ax_rule.set_axis_off()
    box = FancyBboxPatch(
        (0.0, 0.02),
        1.0,
        0.94,
        boxstyle="round,pad=0.005,rounding_size=0.012",
        facecolor=AMBER_LIGHT,
        edgecolor=AMBER,
        linewidth=0.7,
    )
    ax_rule.add_patch(box)
    left_num, left_den = int(boundary["left_num"]), int(boundary["left_den"])
    right_num, right_den = int(boundary["right_num"]), int(boundary["right_den"])
    ax_rule.text(0.025, 0.50, "POST-HOC RULE* BOUNDARY", ha="left", va="center", fontsize=7.2, color=AMBER, weight="bold")
    ax_rule.scatter(0.43, 0.50, s=27, marker="P", facecolor=AMBER, edgecolor=AMBER)
    ax_rule.text(0.45, 0.50, f"Authored {left_num}/{left_den}", ha="left", va="center", fontsize=7.4, color=INK, weight="bold")
    ax_rule.add_patch(FancyArrowPatch((0.61, 0.50), (0.72, 0.50), arrowstyle="-|>", mutation_scale=6.0, linewidth=0.9, color=AMBER))
    ax_rule.scatter(0.75, 0.50, s=27, marker="P", facecolor=PAPER, edgecolor=AMBER, linewidth=0.9)
    ax_rule.text(0.77, 0.50, f"Source-derived {right_num}/{right_den}", ha="left", va="center", fontsize=7.4, color=INK, weight="bold")
    save(fig, stem)


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Generate round-8 TRI main-paper figures.")
    parser.add_argument("--data-dir", type=Path, default=root / "data" / "summary_csv")
    parser.add_argument("--output-dir", type=Path, default=root.parent / "figure-backup" / "candidates-round8")
    args = parser.parse_args()

    policy_rows = read_csv(args.data_dir / "matched_pairacc_and_marginals.csv")
    substitution_rows = read_csv(args.data_dir / "v7_shared_eligible_pairacc_and_substitution.csv")
    sqlite_rows = read_csv(args.data_dir / "sqlite_model_facing_outcomes.csv")
    paired_rows = read_csv(args.data_dir / "main_figure_paired_scores.csv")

    build_policy_rulers(policy_rows, args.output_dir / "fig2_policy_rulers")
    build_substitution_flow(substitution_rows, args.output_dir / "fig3_substitution_flow")
    build_sqlite_tree(sqlite_rows, args.output_dir / "fig4_sqlite_outcome_tree")
    build_paired_transfer_matrix(paired_rows, args.output_dir / "fig5_paired_transfer_matrix")


if __name__ == "__main__":
    main()
