from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


DATA = Path(__file__).resolve().parent / "data" / "summary_csv"
OUT = Path(__file__).resolve().parent / "tri-round10"

INK = "#263238"
MUTED = "#66747A"
GRID = "#D4DCDE"
PAPER = "#FFFFFF"
TEAL = "#2D7873"
TEAL_SOFT = "#DDEBE9"
CORAL = "#B9554F"
AMBER = "#996719"
BLUE = "#4E739D"
LIGHT = "#EEF2F2"

MODEL_COLOR = {"Qwen3.5": BLUE, "GLM-5.1": AMBER, "DeepSeek": TEAL}
MODEL_MARKER = {"Qwen3.5": "o", "GLM-5.1": "s", "DeepSeek": "D"}
MODEL_SHORT = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM", "DeepSeek": "DeepSeek"}


def style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 7.4,
            "axes.labelsize": 7.6,
            "axes.titlesize": 8.0,
            "xtick.labelsize": 7.0,
            "ytick.labelsize": 7.0,
            "axes.linewidth": 0.65,
            "lines.linewidth": 0.9,
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


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find(items: list[dict[str, str]], **where: str) -> dict[str, str]:
    matches = [row for row in items if all(row.get(key) == value for key, value in where.items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {where}, found {len(matches)}")
    return matches[0]


def save(fig: plt.Figure, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix in ("pdf", "svg", "png"):
        kwargs = {}
        if suffix == "png":
            kwargs["dpi"] = 360
        fig.savefig(OUT / f"{name}.{suffix}", **kwargs)
    plt.close(fig)


def wilson(k: int, n: int) -> tuple[float, float, float]:
    if n == 0:
        return 0.0, 0.0, 0.0
    z = 1.959963984540054
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return 100 * p, 100 * max(0, center - half), 100 * min(1, center + half)


def clean_axis(ax: plt.Axes, *, grid: str | None = None) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.5, zorder=0)
        ax.set_axisbelow(True)


def figure2() -> None:
    data = rows("matched_pairacc_and_marginals.csv")
    fig, ax = plt.subplots(figsize=(3.35, 2.62))
    ax.add_patch(Rectangle((75, 75), 30, 30, facecolor=TEAL_SOFT, edgecolor="none", zorder=0))

    specs = [
        ("Always-Reevaluate", "model-independent", "Re-eval", MUTED, "^", False, (2.5, -8.0), "left"),
        ("Always-Lock+validity", "model-independent", "Lock", MUTED, "v", False, (-2.0, 3.5), "right"),
        ("Generic", "Qwen3.5", "Generic-Q", CORAL, "o", True, (2.5, 1.5), "left"),
        ("Generic", "GLM-5.1", "Generic-G", CORAL, "s", True, (2.0, -2.0), "left"),
        ("Rule v2 (post-hoc)", "model-independent", "Rule*", AMBER, "P", True, (-3.0, -5.0), "right"),
        ("CTA", "Qwen3.5", "CTA-Q", TEAL, "o", True, (-3.5, -1.0), "right"),
        ("CTA", "GLM-5.1", "CTA-G", TEAL, "s", True, (-3.0, 2.0), "right"),
    ]
    for controller, model, label, color, marker, filled, offset, align in specs:
        all_row = find(data, dataset="v3", model=model, controller=controller, slice="all")
        changed = find(data, dataset="v3", model=model, controller=controller, slice="changed_winner_core")
        x = float(all_row["preserve_accuracy_pct"])
        y = float(all_row["reevaluate_accuracy_pct"])
        count = int(changed["both_correct"])
        ax.scatter(
            x,
            y,
            s=36 if controller == "CTA" else 31,
            marker=marker,
            facecolor=color if filled else PAPER,
            edgecolor=color,
            linewidth=0.9,
            zorder=3,
        )
        ax.annotate(
            f"{label}  {count}/32",
            (x, y),
            xytext=offset,
            textcoords="offset points",
            ha=align,
            va="bottom" if offset[1] >= 0 else "top",
            fontsize=7.0,
            color=color,
            weight="bold",
            zorder=4,
        )

    ax.set(xlim=(15, 104), ylim=(15, 104), xlabel="Preserve accuracy (%)", ylabel="Reevaluate accuracy (%)")
    ax.set_xticks([20, 40, 60, 80, 100])
    ax.set_yticks([20, 40, 60, 80, 100])
    clean_axis(ax, grid="both")
    fig.subplots_adjust(left=0.18, right=0.985, bottom=0.17, top=0.975)
    save(fig, "fig2_policy_phase_map_round10")


def figure3() -> None:
    data = rows("v7_shared_eligible_pairacc_and_substitution.csv")
    fig = plt.figure(figsize=(3.35, 3.50))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.55, 1.0], hspace=0.42)
    top = fig.add_subplot(gs[0])
    bottom = fig.add_subplot(gs[1])

    models = ["Qwen3.5", "GLM-5.1", "DeepSeek"]
    offsets = [-0.055, 0.0, 0.055]
    for model, offset in zip(models, offsets):
        generic = find(data, model=model, controller="Generic")
        cta = find(data, model=model, controller="CTA")
        n = int(generic["shared_eligible"])
        gk, ck = int(generic["substitutions"]), int(cta["substitutions"])
        gr, gl, gh = wilson(gk, n)
        cr, cl, ch = wilson(ck, n)
        color, marker = MODEL_COLOR[model], MODEL_MARKER[model]
        x0, x1 = offset, 1 + offset
        top.plot([x0, x1], [gr, cr], color=color, lw=1.1, zorder=2)
        top.errorbar(x0, gr, yerr=[[max(0.0, gr - gl)], [max(0.0, gh - gr)]], fmt=marker, ms=5.0,
                     mfc=PAPER, mec=color, mew=0.9, ecolor=color, capsize=2.0,
                     elinewidth=0.8, zorder=3)
        top.errorbar(x1, cr, yerr=[[max(0.0, cr - cl)], [max(0.0, ch - cr)]], fmt=marker, ms=5.0,
                     mfc=color, mec=color, ecolor=color, capsize=2.0, elinewidth=0.8, zorder=3)
        top.text(-0.48, gr, f"{MODEL_SHORT[model]}\n{gk}/{n}", ha="left", va="center",
                 fontsize=7.0, color=color, weight="bold", linespacing=0.88)

    top.set(xlim=(-0.52, 1.25), ylim=(-2, 101), ylabel="Conditional substitution (%)")
    top.set_xticks([0, 1], ["Generic", "CTA"], weight="bold")
    top.set_yticks([0, 25, 50, 75, 100])
    top.set_title("A  Substitution after correct binding", loc="left", pad=2, weight="bold")
    top.tick_params(axis="x", length=0, pad=3)
    top.tick_params(axis="y", length=3, width=0.65)
    clean_axis(top)

    y_positions = [2, 1, 0]
    y_labels = []
    for model, y in zip(models, y_positions):
        generic = find(data, model=model, controller="Generic")
        cta = find(data, model=model, controller="CTA")
        gx, cx = float(generic["pairacc_pct"]), float(cta["pairacc_pct"])
        gl, gh = float(generic["pairacc_ci95_low_pct"]), float(generic["pairacc_ci95_high_pct"])
        cl, ch = float(cta["pairacc_ci95_low_pct"]), float(cta["pairacc_ci95_high_pct"])
        color, marker = MODEL_COLOR[model], MODEL_MARKER[model]
        bottom.plot([gx, cx], [y, y], color=color, lw=1.15, zorder=1)
        bottom.errorbar(gx, y, xerr=[[gx - gl], [gh - gx]], fmt=marker, ms=4.8,
                        mfc=PAPER, mec=color, mew=0.9, ecolor=color, capsize=1.8, elinewidth=0.75, zorder=3)
        bottom.errorbar(cx, y, xerr=[[cx - cl], [ch - cx]], fmt=marker, ms=4.8,
                        mfc=color, mec=color, ecolor=color, capsize=1.8, elinewidth=0.75, zorder=3)
        y_labels.append(f"{MODEL_SHORT[model]}\n{generic['pairacc_both_correct']}→{cta['pairacc_both_correct']}/80")

    bottom.set(xlim=(-2, 101), ylim=(-0.55, 2.55), xlabel="Changed-winner PairAcc (%)")
    bottom.set_yticks(y_positions, y_labels, fontsize=7.0, weight="bold")
    bottom.set_xticks([0, 25, 50, 75, 100])
    bottom.set_title("B  Joint success", loc="left", pad=2, weight="bold")
    bottom.tick_params(axis="y", length=0, pad=4)
    bottom.tick_params(axis="x", length=3, width=0.65)
    clean_axis(bottom)
    legend = [
        Line2D([0], [0], marker="o", color=MUTED, mfc=PAPER, mec=MUTED, ms=4.2, label="Generic"),
        Line2D([0], [0], marker="o", color=MUTED, mfc=MUTED, mec=MUTED, ms=4.2, label="CTA"),
    ]
    bottom.legend(handles=legend, frameon=False, ncol=2, loc="upper right", bbox_to_anchor=(1, 1.22),
                  handletextpad=0.25, columnspacing=0.7, fontsize=7.0)
    # Leave enough internal canvas above the panel-A title after PDF embedding.
    fig.subplots_adjust(left=0.25, right=0.985, top=0.94, bottom=0.11)
    save(fig, "fig3_cross_schema_endpoints_round10")


def unit_grid(ax: plt.Axes, x0: float, y0: float, values: list[tuple[str, int]], *, cols: int = 10) -> None:
    appearance = {
        "Correct": (TEAL, "o", TEAL),
        "TRI write": (CORAL, "X", CORAL),
        "Fallback": (AMBER, "^", AMBER),
        "Reject": (PAPER, "s", MUTED),
    }
    expanded: list[str] = []
    for label, count in values:
        expanded.extend([label] * count)
    for index, label in enumerate(expanded):
        row, col = divmod(index, cols)
        face, marker, edge = appearance[label]
        ax.scatter(x0 + col, y0 - row, s=19, marker=marker, facecolor=face, edgecolor=edge,
                   linewidth=0.65, zorder=2)


def opportunity_row(ax: plt.Axes, x0: float, y: float, writes: int, total: int, color: str, marker: str) -> None:
    for index in range(total):
        filled = index < writes
        ax.scatter(x0 + index * 0.28, y, s=19, marker=marker,
                   facecolor=color if filled else PAPER, edgecolor=color, linewidth=0.75, zorder=3)


def figure4() -> None:
    data = rows("sqlite_model_facing_outcomes.csv")
    fig = plt.figure(figsize=(3.35, 3.35))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.70, 1.0], hspace=0.28)
    top = fig.add_subplot(gs[0])
    bottom = fig.add_subplot(gs[1])
    top.set_xlim(-2.0, 11.2)
    top.set_ylim(-9.25, 1.0)
    top.axis("off")
    top.set_title("A  SQLite tool-loop outcomes (n=40/model)", loc="left", pad=2, weight="bold")

    for model, y0 in (("Qwen3.5", -1.0), ("GLM-5.1", -5.1)):
        row = find(data, model=model, controller="Generic")
        values = [
            ("Correct", int(row["correct_final_state"])),
            ("TRI write", int(row["core_tri_write"])),
            ("Fallback", int(row["fallback_wrong_write"])),
            ("Reject", int(row["unneeded_reject"])),
        ]
        values = [(label, count) for label, count in values if count]
        unit_grid(top, 0.0, y0, values)
        top.text(-0.35, y0 - 1.50, MODEL_SHORT[model], ha="right", va="center", fontsize=7.3, weight="bold")

    handles = [
        Line2D([0], [0], marker="o", color="none", mfc=TEAL, mec=TEAL, ms=4.2, label="Correct"),
        Line2D([0], [0], marker="X", color="none", mfc=CORAL, mec=CORAL, ms=4.2, label="TRI write"),
        Line2D([0], [0], marker="^", color="none", mfc=AMBER, mec=AMBER, ms=4.2, label="Fallback"),
        Line2D([0], [0], marker="s", color="none", mfc=PAPER, mec=MUTED, ms=4.2, label="Reject"),
    ]
    top.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.52, -0.005), ncol=4, frameon=False,
               handletextpad=0.2, columnspacing=0.45, fontsize=7.0)

    bottom.set_xlim(-1.65, 4.45)
    bottom.set_ylim(-0.65, 1.55)
    bottom.axis("off")
    bottom.set_title("B  Strict opportunities", loc="left", pad=2, weight="bold")
    bottom.text(0.42, 1.27, "Stable · 0/4", ha="center", va="center", fontsize=7.0, weight="bold")
    bottom.text(2.38, 1.27, "Changed", ha="center", va="center", fontsize=7.0, weight="bold")
    for model, y in (("Qwen3.5", 0.68), ("GLM-5.1", -0.05)):
        row = find(data, model=model, controller="Generic")
        color, marker = MODEL_COLOR[model], MODEL_MARKER[model]
        bottom.text(-0.12, y, MODEL_SHORT[model], ha="right", va="center", fontsize=7.0, weight="bold")
        opportunity_row(bottom, 0.0, y, int(row["stable_writes"]), int(row["stable_opportunities"]), color, marker)
        opportunity_row(bottom, 1.4, y, int(row["strict_core_writes"]), int(row["strict_core_opportunities"]), color, marker)
        bottom.text(4.32, y, f"{row['strict_core_writes']}/{row['strict_core_opportunities']}",
                    ha="right", va="center", fontsize=7.0, color=color, weight="bold")
    bottom.plot([-1.55, 4.36], [1.02, 1.02], color=GRID, lw=0.55)
    fig.subplots_adjust(left=0.06, right=0.985, top=0.975, bottom=0.05)
    save(fig, "fig4_sqlite_unit_outcomes_round10")


def figure5() -> None:
    data = rows("main_figure_paired_scores.csv")
    row_specs = [
        ("Authored", "Qwen3.5", "Authored · Qwen", BLUE, "o", True),
        ("Authored", "GLM-5.1", "Authored · GLM", BLUE, "s", True),
        ("Source-derived", "Qwen3.5", "Source · Qwen", TEAL, "o", False),
        ("Source-derived", "GLM-5.1", "Source · GLM", TEAL, "s", False),
        ("Source-derived", "DeepSeek", "Source · DeepSeek", TEAL, "D", False),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(3.35, 2.48), sharey=True, gridspec_kw={"wspace": 0.12})
    y = [4, 3, 1.75, 0.75, -0.25]
    panels = [
        (axes[0], "pairacc", "PairAcc effect (pp)", (-16, 82), [-10, 0, 20, 40, 60, 80]),
        (axes[1], "e2e", "E2E effect (pp)", (-11, 34), [-10, 0, 10, 20, 30]),
    ]
    for ax, panel, xlabel, limits, ticks in panels:
        ax.axvline(0, color=MUTED, lw=0.8, zorder=1)
        ax.axhspan(2.45, 4.45, color=LIGHT, zorder=0)
        for (dataset, model, label, color, marker, filled), yy in zip(row_specs, y):
            row = find(data, panel=panel, dataset=dataset, model=model)
            effect = float(row["difference_pp"])
            low, high = float(row["ci95_low_pp"]), float(row["ci95_high_pp"])
            ax.errorbar(effect, yy, xerr=[[effect - low], [high - effect]], fmt=marker, ms=4.8,
                        mfc=color if filled else PAPER, mec=color, mew=0.9, ecolor=color,
                        elinewidth=0.85, capsize=2.0, zorder=3)
        ax.set_xlim(*limits)
        ax.set_xticks(ticks)
        ax.set_xlabel(xlabel, fontsize=7.0)
        ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    axes[0].set_yticks(y, [spec[2] for spec in row_specs], fontsize=7.0)
    axes[0].set_xticks([0, 20, 40, 60, 80])
    axes[0].set_title("A  Joint success", loc="left", pad=2, weight="bold")
    axes[1].set_title("B  End-to-end", loc="left", pad=2, weight="bold")
    axes[0].set_ylim(-0.75, 4.55)
    axes[0].plot([-16, 82], [2.42, 2.42], color=GRID, lw=0.6, clip_on=False)
    axes[1].plot([-11, 34], [2.42, 2.42], color=GRID, lw=0.6, clip_on=False)
    handles = [
        Line2D([0], [0], marker="o", color="none", mfc=BLUE, mec=BLUE, ms=4.3, label="Authored"),
        Line2D([0], [0], marker="o", color="none", mfc=PAPER, mec=TEAL, ms=4.3, label="Source-derived"),
    ]
    fig.legend(handles=handles, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.62, 1.0),
               handletextpad=0.3, columnspacing=0.8, fontsize=7.0)
    fig.subplots_adjust(left=0.34, right=0.985, top=0.84, bottom=0.20)
    save(fig, "fig5_transfer_forest_matrix_round10")


def main() -> None:
    style()
    figure2()
    figure3()
    figure4()
    figure5()


if __name__ == "__main__":
    main()
