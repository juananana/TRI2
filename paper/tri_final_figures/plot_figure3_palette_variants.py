#!/usr/bin/env python3
"""Compare shortlisted paper palettes on TRI Figure 3."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from matplotlib import font_manager
from PIL import Image, ImageColor, ImageDraw, ImageFont

import plot_figure3_options_cd as base
from plot_figure5_palette_variants import PALETTES


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "outputs" / "figure3_palette_candidates_acd_v1"
SHORTLIST = ("a_ocean_breeze", "c_ink_blush", "d_forest_ember")


def mix_with_white(color: str, white_weight: float = 0.67) -> str:
    rgb = ImageColor.getrgb(color)
    mixed = tuple(round(channel * (1.0 - white_weight) + 255 * white_weight) for channel in rgb)
    return "#" + "".join(f"{channel:02X}" for channel in mixed)


def darken(color: str, factor: float = 0.78) -> str:
    rgb = ImageColor.getrgb(color)
    dark = tuple(round(channel * factor) for channel in rgb)
    return "#" + "".join(f"{channel:02X}" for channel in dark)


def render_candidate(data: list[dict], output_dir: Path, slug: str) -> Path:
    palette = PALETTES[slug]
    base.INK = "#264A56"
    base.MUTED = "#5F6B70"
    base.GRID = "#D6E0DE"
    base.PAIR = palette["primary"]
    base.PAIR_EDGE = darken(palette["primary"])
    base.PRESERVE = palette["secondary"]
    base.PRESERVE_LIGHT = mix_with_white(palette["secondary"])
    base.REEVALUATE = palette["tertiary"]
    base.REEVALUATE_LIGHT = mix_with_white(palette["tertiary"])
    base.NEITHER = "#D8D4CF"
    base.NEITHER_EDGE = "#A7A099"
    stem = output_dir / f"figure3_palette_{slug}"
    base.save_variants(
        base.draw_outcome_composition(data),
        stem,
        f"TRI Figure 3 palette {slug}",
    )
    return stem


def get_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    properties = font_manager.FontProperties(
        family="DejaVu Sans", weight="bold" if bold else "normal"
    )
    return ImageFont.truetype(font_manager.findfont(properties), size=size)


def make_contact_sheet(stems: dict[str, Path], output: Path) -> None:
    tile_w, tile_h = 1340, 1060
    margin, gap = 44, 26
    sheet = Image.new(
        "RGB",
        (tile_w + 2 * margin, len(SHORTLIST) * tile_h + 2 * margin + (len(SHORTLIST) - 1) * gap),
        "white",
    )
    draw = ImageDraw.Draw(sheet)
    label_font = get_font(36, bold=True)
    hex_font = get_font(22)

    for index, slug in enumerate(SHORTLIST):
        palette = PALETTES[slug]
        x = margin
        y = margin + index * (tile_h + gap)
        draw.text((x + 8, y + 8), palette["label"], fill="#30343F", font=label_font)
        swatch_x = x + 510
        for key in ("primary", "secondary", "tertiary", "support", "neutral"):
            draw.rounded_rectangle(
                (swatch_x, y + 10, swatch_x + 110, y + 58),
                radius=8,
                fill=palette[key],
            )
            swatch_x += 124
        with Image.open(stems[slug].with_suffix(".png")).convert("RGB") as chart:
            chart.thumbnail((tile_w, 930), Image.Resampling.LANCZOS)
            sheet.paste(chart, (x, y + 74))
        draw.text(
            (x + 8, y + tile_h - 32),
            f"{palette['primary']}  {palette['secondary']}  {palette['tertiary']}",
            fill="#69737A",
            font=hex_font,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, dpi=(200, 200), optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render A/C/D palettes on TRI Figure 3.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = base.read_data()
    stems = {slug: render_candidate(data, args.output_dir, slug) for slug in SHORTLIST}
    contact_sheet = args.output_dir / "figure3_palette_acd_comparison.png"
    make_contact_sheet(stems, contact_sheet)
    manifest = {
        "status": "Figure 3 v3 palette/accessibility comparison; Forest Ember selected",
        "figure": "selected Figure 3 pair-outcome composition",
        "selected": "d_forest_ember",
        "minimum_text_pt": 7.0,
        "accessibility_encoding": {
            "both_correct": "solid dark fill",
            "preserve_only": "sparse forward diagonal",
            "reevaluate_only": "sparse backward diagonal",
            "neither": "plain neutral fill",
        },
        "shared_neutrals": {
            "ink": "#264A56",
            "muted": "#5F6B70",
            "grid": "#D6E0DE",
        },
        "source": str(base.DATA),
        "source_sha256": hashlib.sha256(base.DATA.read_bytes()).hexdigest(),
        "shortlist": list(SHORTLIST),
        "palettes": {slug: PALETTES[slug] for slug in SHORTLIST},
        "outputs": {slug: str(stem) for slug, stem in stems.items()},
        "contact_sheet": str(contact_sheet),
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
