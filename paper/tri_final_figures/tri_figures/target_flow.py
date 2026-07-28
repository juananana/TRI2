from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle

from .style import COLORS, MODEL_LABELS, apply_style, save_figure


def _ribbon(ax, x0, x1, y0, y1, h0, h1, color, alpha=1.0, edge=None, lw=0.4):
    c = (x1 - x0) * 0.36
    verts = [
        (x0, y0 - h0 / 2),
        (x0 + c, y0 - h0 / 2),
        (x1 - c, y1 - h1 / 2),
        (x1, y1 - h1 / 2),
        (x1, y1 + h1 / 2),
        (x1 - c, y1 + h1 / 2),
        (x0 + c, y0 + h0 / 2),
        (x0, y0 + h0 / 2),
        (x0, y0 - h0 / 2),
    ]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
             MplPath.LINETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4, MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color, edgecolor=edge or color, lw=lw, alpha=alpha))


def build(df, output_stem: Path):
    apply_style()
    d = df[df["controller"].isin(["Generic", "CTA"])].copy()
    models = ["Qwen3.5", "GLM-5.1", "DeepSeek"]

    fig, ax = plt.subplots(figsize=(7.05, 3.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 3.15)
    ax.axis("off")

    x_box0, x_box1 = 0.02, 0.19
    x_method = 0.235
    x_flow0, x_flow1 = 0.285, 0.79
    x_out0, x_out1 = 0.80, 0.985

    ax.text(x_method, 3.02, "Method", ha="center", va="bottom", weight="semibold")
    ax.text((x_flow0 + x_flow1) / 2, 3.02, "Refreshed-winner substitution (core TRI)", ha="center", va="bottom", color=COLORS["coral"], weight="semibold")
    ax.text((x_out0 + x_out1) / 2, 3.02, "Retained / other", ha="center", va="bottom", color=COLORS["muted_ink"], weight="semibold")

    row_centers = [2.48, 1.53, 0.58]
    max_n = 70
    for model, yc in zip(models, row_centers):
        rows = d[d["model"] == model]
        gen = rows[rows["controller"] == "Generic"].iloc[0]
        cta = rows[rows["controller"] == "CTA"].iloc[0]
        n = int(gen["shared_eligible"])
        sub = int(gen["substitutions"])
        retained = n - sub

        box_h = 0.56
        ax.add_patch(Rectangle((x_box0, yc - box_h / 2), x_box1 - x_box0, box_h, facecolor="white", edgecolor=COLORS["primary"], lw=0.9))
        ax.text((x_box0+x_box1)/2, yc, f"Shared-eligible\ncorrect initial binding\nn={n}", ha="center", va="center", fontsize=7.3, linespacing=1.15)
        ax.text(0.005, yc, MODEL_LABELS[model], rotation=90, ha="center", va="center", color=COLORS["primary"], fontsize=9.2, weight="semibold")

        yg, yc2 = yc + 0.14, yc - 0.16
        method_box = dict(facecolor="white", edgecolor="none", pad=0.6)
        ax.text(x_method, yg, "Generic", ha="center", va="center", weight="semibold",
                zorder=5, bbox=method_box)
        ax.text(x_method, yc2, "CTA", ha="center", va="center", weight="semibold",
                zorder=5, bbox=method_box)
        ax.plot([x_box1, x_flow0], [yg, yg], color=COLORS["ink"], lw=0.7)
        ax.plot([x_box1, x_flow0], [yc2, yc2], color=COLORS["ink"], lw=0.7)

        base_h = 0.23
        sub_h = base_h * (sub / max_n) * 2.0 + 0.04
        ret_h = base_h * (retained / max_n) * 2.0 + 0.04
        cta_h = base_h * (n / max_n) * 1.7 + 0.04

        _ribbon(ax, x_flow0, x_flow1, yg, yg, 0.06, sub_h, COLORS["coral"], alpha=0.94)
        ax.add_patch(Rectangle((x_flow1, yg - sub_h/2), x_out0-x_flow1, sub_h, facecolor=COLORS["coral"], edgecolor=COLORS["coral"], lw=0.4))
        ax.add_patch(Rectangle((x_out0, yg - ret_h/2), x_out1-x_out0, ret_h, facecolor=COLORS["neutral"], edgecolor=COLORS["grid"], lw=0.6))
        ax.text((x_flow0+x_out0)/2+0.06, yg, f"{sub}/{n}\n({100*sub/n:.1f}%)", ha="center", va="center", fontsize=7.5, weight="semibold")
        ax.text((x_out0+x_out1)/2, yg, f"{retained}/{n}\n({100*retained/n:.1f}%)", ha="center", va="center", fontsize=7.5, weight="semibold")

        _ribbon(ax, x_flow0, x_flow1, yc2, yc2, 0.06, cta_h, COLORS["primary"], alpha=0.98)
        ax.add_patch(Rectangle((x_flow1, yc2-cta_h/2), x_out1-x_flow1, cta_h, facecolor=COLORS["primary"], edgecolor=COLORS["primary"], lw=0.4))
        ax.text((x_flow1+x_out1)/2, yc2, f"No core substitution\n0/{n} (0%)", ha="center", va="center", color="white", fontsize=7.4, weight="semibold")

    fig.subplots_adjust(left=0.04, right=0.995, top=0.94, bottom=0.04)
    save_figure(fig, output_stem)
    plt.close(fig)
