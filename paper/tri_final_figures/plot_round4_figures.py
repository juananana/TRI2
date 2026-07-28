from __future__ import annotations

import argparse
import csv
from math import sqrt
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch


INK = "#29343A"
MUTED = "#738086"
GRID = "#D1D6D7"
PAPER = "#FFFFFF"
GENERIC = "#E56D4E"
GENERIC_LIGHT = "#F8DDD5"
CTA = "#407A7F"
CTA_LIGHT = "#D9E7E7"
RULE = "#8B6F8E"
FIXED = "#70807D"
PAIR = "#407A7F"
E2E = "#E56D4E"
OTHER = "#D8D4CF"
WRONG = "#C85A46"

MODELS = ["Qwen3.5", "GLM-5.1", "DeepSeek"]
MODEL_LABELS = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM", "DeepSeek": "DeepSeek"}
MODEL_MARKERS = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}


def apply_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 7.2,
            "axes.labelsize": 7.6,
            "axes.titlesize": 7.2,
            "xtick.labelsize": 6.5,
            "ytick.labelsize": 6.5,
            "legend.fontsize": 6.2,
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
    fig.savefig(stem.with_suffix(".pdf"))
    fig.savefig(stem.with_suffix(".svg"))
    fig.savefig(stem.with_suffix(".png"), dpi=300)
    plt.close(fig)


def wilson_interval(successes: int, total: int, z: float = 1.959964) -> tuple[float, float, float]:
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return p * 100, max(0, center - half) * 100, min(1, center + half) * 100


def build_policy_fingerprint(rows: list[dict[str, str]], stem: Path) -> None:
    """Three-axis policy profiles reveal failures hidden by marginal accuracy."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.82))
    axes_x = [0.0, 1.0, 2.0]

    profiles: list[tuple[str, list[float], str, str, str, float]] = []
    for model, linestyle in [("Qwen3.5", "-"), ("GLM-5.1", (0, (4, 2)) )]:
        for controller, color in [("Generic", GENERIC), ("CTA", CTA)]:
            all_row = row_where(rows, dataset="v3", model=model, controller=controller, slice="all")
            changed = row_where(rows, dataset="v3", model=model, controller=controller, slice="changed_winner_core")
            profiles.append(
                (
                    f"{controller} {MODEL_LABELS[model]}",
                    [
                        float(all_row["preserve_accuracy_pct"]),
                        float(all_row["reevaluate_accuracy_pct"]),
                        float(changed["pairacc_pct"]),
                    ],
                    color,
                    MODEL_MARKERS[model],
                    linestyle,
                    1.55,
                )
            )

    for controller, marker in [("Always-Lock+validity", "v"), ("Always-Reevaluate", "^")]:
        all_row = row_where(rows, dataset="v3", model="model-independent", controller=controller, slice="all")
        changed = row_where(rows, dataset="v3", model="model-independent", controller=controller, slice="changed_winner_core")
        profiles.append(
            (
                controller,
                [
                    float(all_row["preserve_accuracy_pct"]),
                    float(all_row["reevaluate_accuracy_pct"]),
                    float(changed["pairacc_pct"]),
                ],
                FIXED,
                marker,
                (0, (2, 2)),
                1.05,
            )
        )

    rule_all = row_where(rows, dataset="v3", model="model-independent", controller="Rule v2 (post-hoc)", slice="all")
    rule_changed = row_where(rows, dataset="v3", model="model-independent", controller="Rule v2 (post-hoc)", slice="changed_winner_core")
    profiles.append(
        (
            "Rule*",
            [
                float(rule_all["preserve_accuracy_pct"]),
                float(rule_all["reevaluate_accuracy_pct"]),
                float(rule_changed["pairacc_pct"]),
            ],
            RULE,
            "P",
            (0, (1, 1)),
            1.2,
        )
    )

    for x in axes_x:
        ax.axvline(x, color=INK if x == 2 else GRID, lw=0.75 if x == 2 else 0.55, zorder=0)
    for y in [0, 25, 50, 75, 100]:
        ax.axhline(y, color=GRID, lw=0.35, alpha=0.55, zorder=0)

    for _, values, color, marker, linestyle, linewidth in profiles:
        profile_x = axes_x.copy()
        if marker == "v":
            profile_x[-1] = 1.975
        elif marker == "^":
            profile_x[-1] = 2.025
        ax.plot(profile_x, values, color=color, lw=linewidth, ls=linestyle, alpha=0.92, zorder=2)
        ax.scatter(profile_x, values, s=27 if marker not in ("v", "^") else 24, marker=marker, facecolor=PAPER if color == FIXED else color, edgecolor=INK, lw=0.55, zorder=3)

    label_box = dict(facecolor=PAPER, edgecolor="none", alpha=0.90, pad=0.15)
    ax.text(2.07, 96.2, "CTA  30-31/32", ha="left", va="center", fontsize=5.45, color=CTA, weight="bold", bbox=label_box)
    ax.text(2.07, 87.2, "Rule*  28/32", ha="left", va="center", fontsize=5.35, color=RULE, weight="bold", bbox=label_box)
    ax.text(2.07, 16.2, "Generic  3-7/32", ha="left", va="center", fontsize=5.35, color=GENERIC, weight="bold", bbox=label_box)
    ax.text(2.07, 1.2, "fixed extremes  0/32", ha="left", va="bottom", fontsize=5.2, color=FIXED, weight="bold", bbox=label_box)

    ax.set_title("Marginals can hide zero PairAcc", color=INK, weight="bold", pad=25)
    ax.set_xlim(-0.14, 2.72)
    ax.set_ylim(-6, 104)
    ax.set_xticks(axes_x)
    ax.set_xticklabels(["Preserve\n(all 80)", "Reevaluate\n(all 80)", "Changed PairAcc\n(32 pairs)"])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("Accuracy (%)")
    ax.tick_params(axis="x", length=0, pad=4)
    ax.tick_params(axis="y", length=2.5)
    for spine in ("top", "right", "bottom"):
        ax.spines[spine].set_visible(False)
    legend = [
        Line2D([0], [0], marker="o", color=INK, lw=0, mfc=PAPER, mec=INK, markersize=4.3, label="Qwen"),
        Line2D([0], [0], marker="s", color=INK, lw=0, mfc=PAPER, mec=INK, markersize=4.1, label="GLM"),
    ]
    ax.legend(handles=legend, loc="lower left", bbox_to_anchor=(0.00, 1.015), ncol=2, frameon=False, handletextpad=0.3, columnspacing=0.8, borderaxespad=0)
    fig.subplots_adjust(left=0.17, right=0.98, top=0.75, bottom=0.20)
    save(fig, stem)


def build_policy_dot_matrix(rows: list[dict[str, str]], stem: Path) -> None:
    """Independent in-cell rulers expose complementary one-sided policies."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.72))

    records: list[dict[str, object]] = []
    for controller, color in [("CTA", CTA), ("Generic", GENERIC)]:
        for model in ["Qwen3.5", "GLM-5.1"]:
            all_row = row_where(rows, dataset="v3", model=model, controller=controller, slice="all")
            changed = row_where(rows, dataset="v3", model=model, controller=controller, slice="changed_winner_core")
            records.append(
                {
                    "key": f"{controller}-{MODEL_LABELS[model]}",
                    "label": f"{controller} · {MODEL_LABELS[model]}",
                    "values": [
                        float(all_row["preserve_accuracy_pct"]),
                        float(all_row["reevaluate_accuracy_pct"]),
                        float(changed["pairacc_pct"]),
                    ],
                    "counts": [
                        f"{int(float(all_row['preserve_correct']))}/80",
                        f"{int(float(all_row['reevaluate_correct']))}/80",
                        f"{int(float(changed['both_correct']))}/32",
                    ],
                    "color": color,
                    "marker": MODEL_MARKERS[model],
                    "filled": True,
                }
            )

    rule_all = row_where(rows, dataset="v3", model="model-independent", controller="Rule v2 (post-hoc)", slice="all")
    rule_changed = row_where(rows, dataset="v3", model="model-independent", controller="Rule v2 (post-hoc)", slice="changed_winner_core")
    records.append(
        {
            "key": "Rule*",
            "label": "Rule* · post-hoc",
            "values": [float(rule_all["preserve_accuracy_pct"]), float(rule_all["reevaluate_accuracy_pct"]), float(rule_changed["pairacc_pct"])],
            "counts": [f"{int(float(rule_all['preserve_correct']))}/80", f"{int(float(rule_all['reevaluate_correct']))}/80", f"{int(float(rule_changed['both_correct']))}/32"],
            "color": RULE,
            "marker": "P",
            "filled": True,
        }
    )
    for controller, key, label, marker in [
        ("Always-Lock+validity", "Always-Lock", "Always Lock", "v"),
        ("Always-Reevaluate", "Always-Reeval", "Always Reeval", "^"),
    ]:
        all_row = row_where(rows, dataset="v3", model="model-independent", controller=controller, slice="all")
        changed = row_where(rows, dataset="v3", model="model-independent", controller=controller, slice="changed_winner_core")
        records.append(
            {
                "key": key,
                "label": label,
                "values": [float(all_row["preserve_accuracy_pct"]), float(all_row["reevaluate_accuracy_pct"]), float(changed["pairacc_pct"])],
                "counts": [f"{int(float(all_row['preserve_correct']))}/80", f"{int(float(all_row['reevaluate_correct']))}/80", f"{int(float(changed['both_correct']))}/32"],
                "color": FIXED,
                "marker": marker,
                "filled": False,
            }
        )

    by_key = {str(record["key"]): record for record in records}
    row_order = ["CTA-Qwen", "CTA-GLM", "Rule*", "Generic-Qwen", "Generic-GLM", "Always-Lock", "Always-Reeval"]
    row_y = [6.05, 5.30, 4.38, 3.46, 2.71, 1.79, 1.04]
    cell_centers = [4.25, 6.45, 8.65]
    half_track = 0.72

    ax.text(5.35, 7.52, "MARGINAL ACCURACY", ha="center", va="center", fontsize=5.7, color=MUTED, weight="bold")
    ax.plot([3.53, 7.17], [7.30, 7.30], color=GRID, lw=0.55)
    ax.text(8.65, 7.52, "JOINT TEST", ha="center", va="center", fontsize=5.7, color=CTA, weight="bold")
    ax.plot([7.93, 9.37], [7.30, 7.30], color=CTA, lw=0.75)
    for x, label in zip(cell_centers, ["Preserve", "Reevaluate", "Changed PairAcc"]):
        ax.text(x, 6.91, label, ha="center", va="center", fontsize=6.0, color=INK, weight="bold")

    for key, y in zip(row_order, row_y):
        record = by_key[key]
        color = str(record["color"])
        marker = str(record["marker"])
        filled = bool(record["filled"])
        ax.scatter(0.48, y, s=25, marker=marker, facecolor=color if filled else PAPER, edgecolor=color, lw=0.7, zorder=4)
        ax.text(0.76, y, str(record["label"]), ha="left", va="center", fontsize=5.85, color=color, weight="bold")

        for x, value, count in zip(cell_centers, record["values"], record["counts"]):
            left = x - half_track
            point_x = left + 2 * half_track * float(value) / 100.0
            ax.plot([left, x + half_track], [y - 0.13, y - 0.13], color=GRID, lw=1.9, solid_capstyle="round", zorder=1)
            ax.plot([left, point_x], [y - 0.13, y - 0.13], color=color, lw=2.0, solid_capstyle="round", zorder=2)
            ax.scatter(point_x, y - 0.13, s=10, marker=marker, facecolor=color if filled else PAPER, edgecolor=color, lw=0.55, zorder=3)
            ax.text(x, y + 0.16, str(count), ha="center", va="center", fontsize=5.65, color=INK, weight="bold")

    for y in [4.84, 3.92, 2.25]:
        ax.plot([0.30, 9.52], [y, y], color=GRID, lw=0.5, ls=(0, (3, 3)))

    ax.text(5.0, 8.55, "PairAcc exposes one-sided policies", ha="center", va="center", fontsize=7.1, color=INK, weight="bold")
    ax.text(5.0, 8.06, "independent tracks show accuracy; labels show correct / denominator", ha="center", va="center", fontsize=5.75, color=MUTED)
    ax.text(5.0, 0.36, "Joint correctness requires both matched requests", ha="center", va="center", fontsize=5.65, color=MUTED)

    ax.set_xlim(0.0, 10.0)
    ax.set_ylim(0.05, 8.86)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.subplots_adjust(left=0.015, right=0.995, top=0.995, bottom=0.015)
    save(fig, stem)


def build_controller_outcome_plane(rows: list[dict[str, str]], stem: Path) -> None:
    """A two-dimensional controller contrast keeps both metric populations explicit."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.96))
    label_positions = {
        "Qwen3.5": (34, 26),
        "GLM-5.1": (18, 58),
        "DeepSeek": (49, 54),
    }
    cta_label_positions = {
        "Qwen3.5": (3.8, 34.0),
        "GLM-5.1": (4.0, 93.0),
        "DeepSeek": (4.0, 69.0),
    }
    cta_display_x = {"Qwen3.5": 0.0, "GLM-5.1": 0.7, "DeepSeek": 1.9}
    generic_label_offsets = {
        "Qwen3.5": (2.0, -7.0),
        "GLM-5.1": (2.0, -8.0),
        "DeepSeek": (-2.0, 7.0),
    }

    for model in MODELS:
        generic = row_where(rows, model=model, controller="Generic")
        cta = row_where(rows, model=model, controller="CTA")
        n = int(generic["shared_eligible"])
        g_sub = int(generic["substitutions"])
        c_sub = int(cta["substitutions"])
        gx, gx_low, gx_high = wilson_interval(g_sub, n)
        cx, cx_low, cx_high = wilson_interval(c_sub, n)
        gy = float(generic["pairacc_pct"])
        cy = float(cta["pairacc_pct"])
        gy_low, gy_high = float(generic["pairacc_ci95_low_pct"]), float(generic["pairacc_ci95_high_pct"])
        cy_low, cy_high = float(cta["pairacc_ci95_low_pct"]), float(cta["pairacc_ci95_high_pct"])
        marker = MODEL_MARKERS[model]

        cta_x = cta_display_x[model]
        ax.add_patch(
            FancyArrowPatch(
                (gx - 1.2, gy + 0.7),
                (cta_x + 1.2, cy - 0.7),
                arrowstyle="-|>",
                mutation_scale=8,
                color=FIXED,
                lw=1.05,
                alpha=0.78,
                zorder=1,
            )
        )
        ax.errorbar(
            gx,
            gy,
            xerr=[[max(0.0, gx - gx_low)], [max(0.0, gx_high - gx)]],
            yerr=[[gy - gy_low], [gy_high - gy]],
            fmt=marker,
            ms=4.8,
            mfc=GENERIC,
            mec=INK,
            mew=0.6,
            ecolor=GENERIC,
            elinewidth=0.85,
            capsize=2.0,
            zorder=4,
        )
        ax.errorbar(
            cta_x,
            cy,
            xerr=[[max(0.0, cta_x - cx_low)], [max(0.0, cx_high - cta_x)]],
            yerr=[[cy - cy_low], [cy_high - cy]],
            fmt=marker,
            ms=4.8,
            mfc=PAPER,
            mec=CTA,
            mew=1.15,
            ecolor=CTA,
            elinewidth=0.85,
            capsize=2.0,
            zorder=5,
        )
        if cta_x:
            ax.plot([0.0, cta_x], [cy, cy], color=CTA, lw=0.6, ls=(0, (1.2, 1.2)), zorder=6)
        lx, ly = label_positions[model]
        ax.text(lx, ly, MODEL_LABELS[model], ha="center", va="center", fontsize=6.2, color=INK, weight="bold", bbox=dict(facecolor=PAPER, edgecolor="none", alpha=0.88, pad=0.2))
        dx, dy = generic_label_offsets[model]
        ax.text(gx + dx, gy + dy, f"S {g_sub}/{n} · P {int(generic['pairacc_both_correct'])}/80", ha="right" if model == "DeepSeek" else "left", va="center", fontsize=5.55, color=GENERIC, weight="bold")
        tx, ty = cta_label_positions[model]
        cta_label = f"S 0/{n} · P {int(cta['pairacc_both_correct'])}/80"
        if model == "Qwen3.5":
            ax.text(tx, ty, cta_label, ha="left", va="center", fontsize=5.45, color=CTA, weight="bold")
        else:
            ax.annotate(
                cta_label,
                (cta_x, cy),
                xytext=(tx, ty),
                textcoords="data",
                ha="left",
                va="center",
                fontsize=5.45,
                color=CTA,
                weight="bold",
                arrowprops=dict(arrowstyle="-", color=CTA, lw=0.55, shrinkA=2.5, shrinkB=3.0),
            )

    ax.set_title("CTA shifts both cross-schema outcomes", color=INK, weight="bold", pad=30)
    ax.text(0.5, 1.065, "x: shared-eligible substitution n=66/70/69 (horizontal Wilson CI)", transform=ax.transAxes, ha="center", va="bottom", fontsize=5.45, color=MUTED)
    ax.text(0.5, 1.015, "y: all-80 PairAcc (vertical pair-cluster bootstrap CI) · labels: S/P counts", transform=ax.transAxes, ha="center", va="bottom", fontsize=5.4, color=MUTED)
    ax.set_xlim(-4, 88)
    ax.set_ylim(-3, 104)
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Conditional substitution (%) · lower is better")
    ax.set_ylabel("Changed PairAcc (%) · higher is better")
    ax.grid(color=GRID, lw=0.4, alpha=0.55)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    legend = [
        Line2D([0], [0], marker="o", color="none", mfc=GENERIC, mec=INK, markersize=4.6, label="Generic"),
        Line2D([0], [0], marker="o", color="none", mfc=PAPER, mec=CTA, mew=1.0, markersize=4.6, label="CTA"),
    ]
    ax.legend(handles=legend, loc="upper right", frameon=False, ncol=2, columnspacing=0.8, handletextpad=0.3)
    fig.subplots_adjust(left=0.18, right=0.98, top=0.72, bottom=0.18)
    save(fig, stem)


def build_wrong_write_mirror(rows: list[dict[str, str]], stem: Path) -> None:
    """Mirrored decomposition contrasts Generic and CTA error composition."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.30))
    y_positions = [2, 1, 0]

    for y, model in zip(y_positions, MODELS):
        generic = row_where(rows, dataset="v7", model=model, controller="Generic")
        cta = row_where(rows, dataset="v7", model=model, controller="CTA")
        g_core = int(generic["core_substitution_writes"])
        g_other = int(generic["non_core_wrong_writes"])
        c_core = int(cta["core_substitution_writes"])
        c_other = int(cta["non_core_wrong_writes"])

        ax.barh(y, -g_core, left=0, height=0.42, color=GENERIC, edgecolor="none", zorder=2)
        if g_other:
            ax.barh(y, -g_other, left=-g_core, height=0.42, color=OTHER, edgecolor=FIXED, lw=0.5, hatch="///", zorder=2)
        if c_other:
            ax.barh(y, c_other, left=0, height=0.42, color=OTHER, edgecolor=FIXED, lw=0.5, hatch="///", zorder=2)
        if c_core:
            ax.barh(y, c_core, left=c_other, height=0.42, color=GENERIC, edgecolor="none", zorder=2)

        ax.text(-g_core / 2, y, f"{g_core} TRI", ha="center", va="center", fontsize=6.2, color="white", weight="bold")
        if g_other:
            ax.text(-g_core - g_other + 0.5, y + 0.27, f"+{g_other} other", ha="left", va="bottom", fontsize=5.8, color=FIXED, weight="bold")
        ax.text(c_other / 2 if c_other else 3.0, y, f"{c_other} other", ha="center" if c_other else "left", va="center", fontsize=6.0, color=INK, weight="bold")
        ax.text(1.0, y + 0.29, "0 TRI", ha="left", va="bottom", fontsize=5.8, color=GENERIC, weight="bold")

    ax.axvline(0, color=INK, lw=0.8)
    for y in [0.5, 1.5]:
        ax.axhline(y, color=GRID, lw=0.5, ls=(0, (3, 3)))
    ax.text(-32, 2.48, "GENERIC", ha="center", va="bottom", fontsize=6.2, color=GENERIC, weight="bold")
    ax.text(32, 2.48, "CTA", ha="center", va="bottom", fontsize=6.2, color=CTA, weight="bold")
    ax.set_title("Wrong-write composition under fixed replay", color=INK, weight="bold", pad=20)
    ax.text(0.5, 1.015, "TRI / all wrong writes: Generic 140/142 · CTA 0/39 · 240 tasks/model", transform=ax.transAxes, ha="center", va="bottom", fontsize=5.7, color=MUTED)
    ax.set_xlim(-65, 65)
    ax.set_ylim(-0.48, 2.62)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([MODEL_LABELS[m] for m in MODELS])
    ax.set_xticks([-60, -40, -20, 0, 20, 40, 60])
    ax.set_xticklabels(["60", "40", "20", "0", "20", "40", "60"])
    ax.set_xlabel("Wrong-target writes (absolute count, mirrored)")
    ax.grid(axis="x", color=GRID, lw=0.4, alpha=0.55)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=5)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.subplots_adjust(left=0.20, right=0.98, top=0.76, bottom=0.20)
    save(fig, stem)


def build_transfer_evidence_tree(rows: list[dict[str, str]], stem: Path) -> None:
    """A grouped evidence tree carries both PairAcc and E2E effect intervals."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.10))

    groups = [
        ("revision_full_diagnostic", "AUTHORED", [("Qwen3.5", 8.15), ("GLM-5.1", 7.25)]),
        ("revision_human_rewrite", "HUMAN REWRITE  [Pair n=3]", [("Qwen3.5", 5.55), ("GLM-5.1", 4.65)]),
        ("revision_source_grounded", "SOURCE-DERIVED", [("Qwen3.5", 2.95), ("GLM-5.1", 2.05), ("DeepSeek", 1.15)]),
    ]

    trunk_x = -38.2
    branch_x = -34.6
    ax.plot([trunk_x, trunk_x], [1.15, 8.15], color=GRID, lw=0.8, zorder=0)
    for audit_id, group_label, model_rows in groups:
        ys = [y for _, y in model_rows]
        center = sum(ys) / len(ys)
        ax.plot([trunk_x, branch_x], [center, center], color=GRID, lw=0.8, zorder=0)
        ax.plot([branch_x, branch_x], [min(ys), max(ys)], color=GRID, lw=0.8, zorder=0)
        ax.scatter(trunk_x, center, s=13, facecolor=PAPER, edgecolor=PAIR, lw=0.75, zorder=2)
        ax.text(-39.3, max(ys) + 0.48, group_label, ha="left", va="bottom", fontsize=5.0, color=INK, weight="bold")

        for model, y in model_rows:
            ax.plot([branch_x, -32.8], [y, y], color=GRID, lw=0.8, zorder=0)
            ax.text(-31.8, y, MODEL_LABELS[model], ha="left", va="center", fontsize=5.25, color=MUTED, weight="bold")
            for metric, offset, color, marker in [
                ("changed_pairacc", 0.14, PAIR, "D"),
                ("actionable_e2e", -0.14, E2E, "o"),
            ]:
                row = row_where(rows, audit_id=audit_id, model=model, metric=metric)
                value = float(row["difference_pp"])
                low = float(row["ci95_low_pp"])
                high = float(row["ci95_high_pp"])
                ax.errorbar(
                    value,
                    y + offset,
                    xerr=[[value - low], [high - value]],
                    fmt=marker,
                    ms=4.5,
                    mfc=PAPER if metric == "changed_pairacc" else color,
                    mec=color,
                    mew=0.9,
                    ecolor=color,
                    elinewidth=0.85,
                    capsize=1.8,
                    zorder=4,
                )
                ax.text(109.5, y + offset, f"{value:+.1f}", ha="right", va="center", fontsize=4.8, color=color, weight="bold")

    ax.axvline(0, color=INK, lw=0.85)
    for y in [6.45, 3.75]:
        ax.axhline(y, color=GRID, lw=0.5, ls=(0, (3, 3)))
    ax.text(42, 8.85, "favors Decision-visible", ha="center", va="center", fontsize=5.1, color=CTA, weight="bold")
    ax.set_title("Visibility gains weaken under transfer", color=INK, weight="bold", pad=25)
    ax.set_xlim(-40, 112)
    ax.set_ylim(0.62, 9.05)
    ax.set_xticks([-20, 0, 20, 40, 60, 80, 100])
    ax.set_yticks([])
    ax.set_xlabel("Decision-visible - History-only (percentage points)")
    ax.grid(axis="x", color=GRID, lw=0.4, alpha=0.55)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    legend = [
        Line2D([0], [0], marker="D", color=PAIR, lw=0.9, mfc=PAPER, mec=PAIR, markersize=4.2, label="Changed PairAcc"),
        Line2D([0], [0], marker="o", color=E2E, lw=0.9, mfc=E2E, mec=E2E, markersize=4.2, label="Actionable E2E"),
    ]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.57, 1.015), ncol=2, frameon=False, columnspacing=0.8, handletextpad=0.35)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.76, bottom=0.15)
    save(fig, stem)


def build_transfer_grouped_forest(rows: list[dict[str, str]], stem: Path) -> None:
    """Grouped dual-track forest plot without decorative branching."""
    apply_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.12))
    groups = [
        ("revision_full_diagnostic", "AUTHORED · primary P: 32 pairs · E: 128 rows", "changed_pairacc", [("Qwen3.5", 7.75), ("GLM-5.1", 6.80)]),
        ("revision_human_rewrite", "HUMAN REWRITE · primary E: 40 rows · P: 3 pairs", "actionable_e2e", [("Qwen3.5", 5.05), ("GLM-5.1", 4.10)]),
        ("revision_source_grounded", "SOURCE-DERIVED · primary E: 60 rows · P: 30 pairs", "actionable_e2e", [("Qwen3.5", 2.35), ("GLM-5.1", 1.40), ("DeepSeek", 0.45)]),
    ]

    for audit_id, group_label, primary_metric, model_rows in groups:
        ax.text(-31.1, max(y for _, y in model_rows) + 0.42, group_label, ha="left", va="bottom", fontsize=5.45, color=INK, weight="bold")
        for model, y in model_rows:
            ax.text(-18.5, y, MODEL_LABELS[model], ha="right", va="center", fontsize=6.0, color=MUTED, weight="bold")
            for metric, offset, color, marker, track_label in [
                ("changed_pairacc", 0.18, PAIR, "D", "P"),
                ("actionable_e2e", -0.18, E2E, "o", "E"),
            ]:
                row = row_where(rows, audit_id=audit_id, model=model, metric=metric)
                value = float(row["difference_pp"])
                low = float(row["ci95_low_pp"])
                high = float(row["ci95_high_pp"])
                alpha = 1.0 if metric == primary_metric else 0.52
                ax.text(-13.8, y + offset, track_label, ha="center", va="center", fontsize=5.8, color=color, weight="bold", alpha=alpha)
                ax.errorbar(
                    value,
                    y + offset,
                    xerr=[[value - low], [high - value]],
                    fmt=marker,
                    ms=4.7,
                    mfc=PAPER if metric == "changed_pairacc" else color,
                    mec=color,
                    mew=0.9,
                    ecolor=color,
                    elinewidth=1.0 if metric == primary_metric else 0.75,
                    capsize=1.9,
                    alpha=alpha,
                    zorder=4,
                )
                ax.text(110.5, y + offset, f"{value:+.1f}", ha="right", va="center", fontsize=5.85, color=color, weight="bold", alpha=alpha)

    ax.axvline(0, color=INK, lw=0.85)
    for y in [5.88, 3.18]:
        ax.axhline(y, color=GRID, lw=0.55, ls=(0, (3, 3)))
    ax.text(-18.0, 8.82, "favors History-only", ha="center", va="center", fontsize=5.35, color=MUTED, weight="bold")
    ax.text(45, 8.82, "favors Decision-visible", ha="center", va="center", fontsize=5.7, color=CTA, weight="bold")
    ax.set_title("Estimated visibility effects across audits", color=INK, weight="bold", pad=20)
    ax.text(0.5, 1.015, "P: changed PairAcc · E: actionable E2E · cluster-bootstrap 95% CI", transform=ax.transAxes, ha="center", va="bottom", fontsize=5.8, color=MUTED)
    ax.set_xlim(-32, 113)
    ax.set_ylim(-0.02, 9.02)
    ax.set_xticks([-20, 0, 20, 40, 60, 80, 100])
    ax.set_yticks([])
    ax.set_xlabel("Effect of Decision-visible (percentage points)")
    ax.grid(axis="x", color=GRID, lw=0.4, alpha=0.65)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.79, bottom=0.15)
    save(fig, stem)


def apply_round4_style() -> None:
    """Paper-scale style: every visible text element is at least 8 pt."""
    apply_style()
    mpl.rcParams.update(
        {
            "font.size": 8.0,
            "axes.labelsize": 8.5,
            "axes.titlesize": 9.5,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 8.0,
        }
    )


def build_policy_dot_matrix_round4(rows: list[dict[str, str]], stem: Path) -> None:
    """Three independent rulers preserve each metric's denominator."""
    apply_round4_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.55))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9.5)

    def get_values(controller: str, model: str) -> tuple[list[float], list[str]]:
        all_row = row_where(rows, dataset="v3", model=model, controller=controller, slice="all")
        changed = row_where(rows, dataset="v3", model=model, controller=controller, slice="changed_winner_core")
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
            values, counts = get_values(controller, model)
            entries.append((f"{controller} · {MODEL_LABELS[model]}", values, counts, color, MODEL_MARKERS[model], True))
    values, counts = get_values("Rule v2 (post-hoc)", "model-independent")
    entries.append(("Rule* · post-hoc", values, counts, RULE, "P", True))
    values, counts = get_values("Always-Lock+validity", "model-independent")
    entries.append(("Always Lock", values, counts, FIXED, "v", False))
    values, counts = get_values("Always-Reevaluate", "model-independent")
    entries.append(("Always Reeval.", values, counts, FIXED, "^", False))

    order = [0, 1, 4, 2, 3, 5, 6]
    y_positions = [7.10, 6.25, 5.22, 4.15, 3.30, 2.18, 1.33]
    centers = [5.35, 7.85, 10.35]
    half_track = 0.86
    ax.text(6.0, 9.13, "PairAcc exposes one-sided policies", ha="center", va="center", fontsize=9.5, color=INK, weight="bold")
    ax.text(6.60, 8.42, "MARGINALS", ha="center", va="center", fontsize=8.0, color=MUTED, weight="bold")
    ax.text(10.35, 8.42, "JOINT", ha="center", va="center", fontsize=8.0, color=CTA, weight="bold")
    for x, label in zip(centers, ("Preserve", "Reevaluate", "PairAcc")):
        ax.text(x, 7.94, label, ha="center", va="center", fontsize=8.0, color=INK, weight="bold")

    for entry_index, y in zip(order, y_positions):
        label, values, counts, color, marker, filled = entries[entry_index]
        ax.scatter(0.45, y, s=30, marker=marker, facecolor=color if filled else PAPER, edgecolor=color, lw=0.9, zorder=4)
        ax.text(0.82, y, label, ha="left", va="center", fontsize=8.0, color=color, weight="bold")
        for x, value, count in zip(centers, values, counts):
            left, right = x - half_track, x + half_track
            point_x = left + (right - left) * value / 100.0
            ax.plot([left, right], [y - 0.16, y - 0.16], color=OTHER, lw=2.6, solid_capstyle="round")
            ax.plot([left, point_x], [y - 0.16, y - 0.16], color=color, lw=2.5, solid_capstyle="round")
            ax.scatter(point_x, y - 0.16, s=18, marker=marker, facecolor=color if filled else PAPER, edgecolor=color, lw=0.8, zorder=5)
            ax.text(x, y + 0.20, count, ha="center", va="center", fontsize=8.0, color=INK, weight="bold")
    for y in (5.72, 4.70, 2.72):
        ax.plot([0.25, 11.72], [y, y], color=GRID, lw=0.7, ls=(0, (3, 3)))
    ax.text(6.0, 0.48, "Joint correctness requires both requests in a matched pair", ha="center", va="center", fontsize=8.0, color=MUTED)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, stem)


def build_shared_eligible_dumbbell(rows: list[dict[str, str]], stem: Path) -> None:
    """Single-endpoint Generic/CTA comparison on shared-eligible rows."""
    apply_round4_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.72))
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
        ax.plot([cta_x, generic_x], [y, y], color=GRID, lw=2.0, zorder=1)
        ax.errorbar(
            generic_x,
            y,
            xerr=[[max(0.0, generic_x - generic_low)], [max(0.0, generic_high - generic_x)]],
            fmt=marker,
            ms=6.2,
            mfc=GENERIC,
            mec=INK,
            mew=0.7,
            ecolor=GENERIC,
            elinewidth=1.2,
            capsize=3,
            zorder=3,
        )
        ax.errorbar(
            cta_x,
            y,
            xerr=[[max(0.0, cta_x - cta_low)], [max(0.0, cta_high - cta_x)]],
            fmt=marker,
            ms=6.2,
            mfc=PAPER,
            mec=CTA,
            mew=1.3,
            ecolor=CTA,
            elinewidth=1.2,
            capsize=3,
            zorder=4,
        )
        ax.text(generic_x, y + 0.28, f"{generic_count}/{n}", ha="center", va="bottom", fontsize=8.0, color=GENERIC, weight="bold")
        ax.text(max(cta_x + 1.0, 2.0), y - 0.28, f"{cta_count}/{n}", ha="left", va="top", fontsize=8.0, color=CTA, weight="bold")

    ax.axvline(0, color=INK, lw=0.9)
    ax.set_xlim(-2, 88)
    ax.set_ylim(0.05, 3.20)
    ax.set_yticks([2.5, 1.5, 0.5])
    ax.set_yticklabels(["Qwen", "GLM", "DeepSeek"], weight="bold")
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_xlabel("Conditional substitution on shared-eligible rows (%)")
    ax.set_title("Substitution after correct binding", pad=34, weight="bold")
    ax.grid(axis="x", color=GRID, lw=0.6, alpha=0.75)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    handles = [
        Line2D([0], [0], marker="o", color="none", mfc=GENERIC, mec=INK, markersize=6, label="Generic"),
        Line2D([0], [0], marker="o", color="none", mfc=PAPER, mec=CTA, mew=1.2, markersize=6, label="CTA"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.52, 1.12), frameon=False, ncol=2, handletextpad=0.3, columnspacing=0.9)
    fig.subplots_adjust(left=0.24, right=0.98, top=0.70, bottom=0.21)
    save(fig, stem)


def build_sqlite_outcomes(rows: list[dict[str, str]], stem: Path) -> None:
    """Exact 40-task outcome maps for the Generic model-facing tool loop."""
    apply_round4_style()
    fig, ax = plt.subplots(figsize=(3.35, 2.90))
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
        ax.text(x0 + 3.6, 6.24, MODEL_LABELS[model], ha="center", va="center", fontsize=9.0, color=INK, weight="bold")
        task_index = 0
        for key, _, color, marker in categories:
            for _ in range(int(row[key])):
                column = task_index % 8
                grid_row = task_index // 8
                x = x0 + column * 0.91
                y = 5.48 - grid_row * 0.78
                if marker == "x":
                    ax.scatter(x + 0.35, y + 0.29, s=43, marker=marker, color=color, linewidth=1.3, zorder=3)
                else:
                    ax.scatter(x + 0.35, y + 0.29, s=43, marker=marker, facecolor=color, edgecolor=PAPER, linewidth=0.7, zorder=3)
                task_index += 1
        assert task_index == int(row["tasks"])
        ax.text(
            x0 + 3.6,
            1.18,
            f"correct {row['correct_final_state']} · TRI {row['core_tri_write']}\n"
            f"fallback {row['fallback_wrong_write']} · reject {row['unneeded_reject']}",
            ha="center",
            va="center",
            fontsize=8.0,
            color=INK,
            weight="bold",
        )
        ax.text(
            x0 + 3.6,
            0.43,
            f"strict writes {row['strict_core_writes']}/{row['strict_core_opportunities']} · stable {row['stable_writes']}/{row['stable_opportunities']}",
            ha="center",
            va="center",
            fontsize=8.0,
            color=MUTED,
        )

    ax.text(10.0, 7.78, "MODEL-FACING SQLITE OUTCOMES", ha="center", va="center", fontsize=9.5, color=INK, weight="bold")
    ax.text(10.0, 7.35, "each marker is one complete task trajectory", ha="center", va="center", fontsize=8.0, color=MUTED)
    handles = [
        Line2D([0], [0], marker=marker, color="none", markerfacecolor=color if marker != "x" else "none", markeredgecolor=color, markeredgewidth=1.0, markersize=6, label=label)
        for _, label, color, marker in categories
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.50, 0.86), frameon=False, ncol=4, columnspacing=0.55, handlelength=1.0, handletextpad=0.30)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 8.15)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, stem)


def build_primary_endpoint_forest(rows: list[dict[str, str]], stem: Path) -> None:
    """One display endpoint per dataset/model row."""
    apply_round4_style()
    fig, ax = plt.subplots(figsize=(3.35, 3.85))
    groups = [
        ("AUTHORED · PairAcc (32 pairs)", "revision_full_diagnostic", "changed_pairacc", ["Qwen3.5", "GLM-5.1"], PAIR, "D"),
        ("HUMAN REWRITE · E2E (40 rows)", "revision_human_rewrite", "actionable_e2e", ["Qwen3.5", "GLM-5.1"], E2E, "o"),
        ("SOURCE-DERIVED · E2E (60 rows)", "revision_source_grounded", "actionable_e2e", ["Qwen3.5", "GLM-5.1", "DeepSeek"], CTA, "s"),
    ]
    y = 7.4
    y_ticks: list[float] = []
    y_labels: list[str] = []
    for heading, audit_id, metric, models, color, marker in groups:
        ax.text(-29, y + 0.34, heading, ha="left", va="center", fontsize=8.0, color=INK, weight="bold")
        for model in models:
            row = row_where(rows, audit_id=audit_id, model=model, metric=metric)
            value = float(row["difference_pp"])
            low = float(row["ci95_low_pp"])
            high = float(row["ci95_high_pp"])
            ax.errorbar(
                value,
                y,
                xerr=[[value - low], [high - value]],
                fmt=marker,
                ms=6.0,
                mfc=PAPER if marker != "o" else color,
                mec=color,
                mew=1.2,
                ecolor=color,
                elinewidth=1.2,
                capsize=3,
                zorder=3,
            )
            ax.text(98.0, y, f"{value:+.1f}", ha="right", va="center", fontsize=8.0, color=color, weight="bold")
            y_ticks.append(y)
            y_labels.append(MODEL_LABELS[model])
            y -= 0.72
        y -= 0.63

    ax.axvline(0, color=INK, lw=1.0)
    ax.set_xlim(-30, 100)
    ax.set_ylim(0.0, 8.15)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, weight="bold")
    ax.set_xticks([-20, 0, 20, 40, 60, 80])
    ax.set_xlabel("Decision-visible - History-only (pp)")
    ax.set_title("Decision visibility across sources", pad=10, weight="bold")
    ax.grid(axis="x", color=GRID, lw=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.subplots_adjust(left=0.22, right=0.98, top=0.86, bottom=0.15)
    save(fig, stem)


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Generate round-4 single-column TRI result figures.")
    parser.add_argument("--data-dir", type=Path, default=root / "data" / "summary_csv")
    parser.add_argument("--output-dir", type=Path, default=root / "outputs" / "round4")
    args = parser.parse_args()

    phase = read_csv(args.data_dir / "matched_pairacc_and_marginals.csv")
    flow = read_csv(args.data_dir / "v7_shared_eligible_pairacc_and_substitution.csv")
    sqlite = read_csv(args.data_dir / "sqlite_model_facing_outcomes.csv")
    gains = read_csv(args.data_dir / "revision_decision_visible_gains.csv")

    build_policy_dot_matrix_round4(phase, args.output_dir / "fig2_policy_rulers_round4")
    build_shared_eligible_dumbbell(flow, args.output_dir / "fig3_shared_eligible_dumbbell_round4")
    build_sqlite_outcomes(sqlite, args.output_dir / "fig4_sqlite_outcomes_round4")
    build_primary_endpoint_forest(gains, args.output_dir / "fig5_visibility_forest_round4")


if __name__ == "__main__":
    main()
