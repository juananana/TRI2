from __future__ import annotations

from pathlib import Path
import matplotlib as mpl

# Muted, color-blind-aware academic palette.
COLORS = {
    "ink": "#264A56",
    "muted_ink": "#5F6B70",
    "grid": "#D6E0DE",
    "primary": "#407A7F",       # teal: primary / decision-visible
    "primary_light": "#D9E7E7",
    "positive": "#60AA84",      # leaf: valid / repaired / third model
    "coral": "#E56D4E",          # ember: substitution / harm
    "coral_light": "#F8DDD5",
    "amber": "#8B6F8E",          # plum: post-hoc / fourth model
    "control": "#AEBBB7",
    "neutral": "#D8D4CF",
    "neutral_bg": "#F4F7F5",
    "white": "#FFFFFF",
}

MODEL_MARKERS = {
    "Qwen3.5": "o",
    "Qwen": "o",
    "GLM-5.1": "s",
    "GLM": "s",
    "DeepSeek": "D",
}

MODEL_LABELS = {
    "Qwen3.5": "Qwen",
    "GLM-5.1": "GLM",
    "DeepSeek": "DeepSeek",
}


def apply_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Liberation Sans", "DejaVu Sans"],
            "font.size": 8.0,
            "axes.labelsize": 8.5,
            "axes.titlesize": 9.0,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.2,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.1,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def save_figure(fig, output_stem: Path, png_dpi: int = 300) -> None:
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.03)
    fig.savefig(output_stem.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.03)
    fig.savefig(output_stem.with_suffix(".png"), dpi=png_dpi, bbox_inches="tight", pad_inches=0.03)
