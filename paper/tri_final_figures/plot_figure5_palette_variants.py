#!/usr/bin/env python3
"""Render palette-only variants of the selected TRI Figure 5 structure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager

import plot_figure5_options_def as base


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "outputs" / "figure5_palette_candidates_v1"

# Each candidate is a complete paper palette: primary and secondary drive
# Figure 5; tertiary is reserved for a third model/endpoint; support colors
# cover pale fills and neutral structure elsewhere in the manuscript.
PALETTES = {
    "a_ocean_breeze": {
        "label": "A  Ocean breeze",
        "primary": "#51999F",
        "secondary": "#ED8D5A",
        "tertiary": "#7BC0CD",
        "support": "#BFDFD2",
        "neutral": "#69737A",
        "primary_light": "#D9EBEC",
        "secondary_light": "#FAE1D4",
        "note": "Xiaohongshu scientific-figure palette; yellow members omitted",
    },
    "b_berry_coral": {
        "label": "B  Berry coral",
        "primary": "#8D718D",
        "secondary": "#D97B68",
        "tertiary": "#4F9189",
        "support": "#DCC9D4",
        "neutral": "#69737A",
        "primary_light": "#E7DDE4",
        "secondary_light": "#F5DDD7",
        "note": "soft editorial palette close to TRI's existing model colors",
    },
    "c_ink_blush": {
        "label": "C  Ink blue + blush",
        "primary": "#637A9F",
        "secondary": "#D88B96",
        "tertiary": "#6C9488",
        "support": "#BCC9DD",
        "neutral": "#66717C",
        "primary_light": "#DFE5EE",
        "secondary_light": "#F3E0E4",
        "note": "cooler conference-paper palette with restrained rose",
    },
    "d_forest_ember": {
        "label": "D  Forest ember",
        "primary": "#407A7F",
        "secondary": "#E56D4E",
        "tertiary": "#60AA84",
        "support": "#B8D0C7",
        "neutral": "#5F6B70",
        "primary_light": "#D9E7E7",
        "secondary_light": "#F8DDD5",
        "note": "higher-contrast version of the approved tropical-forest system",
    },
    "e_plum_seafoam": {
        "label": "E  Plum + seafoam",
        "primary": "#A0677D",
        "secondary": "#5C8F94",
        "tertiary": "#D38A6F",
        "support": "#D8BCC8",
        "neutral": "#6B7077",
        "primary_light": "#ECDDE3",
        "secondary_light": "#DDEBEC",
        "note": "warmer berry-led palette with quiet teal contrast",
    },
}


def render_candidate(data: dict, output_dir: Path, slug: str, palette: dict[str, str]) -> Path:
    base.PAIR_F = palette["primary"]
    base.PAIR_F_LIGHT = palette["primary_light"]
    base.E2E_F = palette["secondary"]
    base.E2E_F_LIGHT = palette["secondary_light"]
    stem = output_dir / f"figure5_palette_{slug}"
    base.save_variants(
        base.draw_vertical_effect_bars(data),
        stem,
        f"TRI Figure 5 palette {slug}",
    )
    return stem


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    properties = font_manager.FontProperties(family="DejaVu Sans", weight="bold" if bold else "normal")
    return ImageFont.truetype(font_manager.findfont(properties), size=size)


def make_contact_sheet(stems: dict[str, Path], output: Path) -> None:
    tile_w, tile_h = 1340, 1080
    margin, gap = 40, 28
    sheet = Image.new("RGB", (2 * tile_w + 2 * margin + gap, 3 * tile_h + 2 * margin + 2 * gap), "white")
    draw = ImageDraw.Draw(sheet)
    label_font = font(34, bold=True)
    hex_font = font(22)

    for index, (slug, palette) in enumerate(PALETTES.items()):
        row, col = divmod(index, 2)
        x = margin + col * (tile_w + gap)
        y = margin + row * (tile_h + gap)
        with Image.open(stems[slug].with_suffix(".png")).convert("RGB") as chart:
            chart.thumbnail((tile_w, 940), Image.Resampling.LANCZOS)
            sheet.paste(chart, (x, y + 72))
        draw.text((x + 8, y + 8), palette["label"], fill="#30343F", font=label_font)
        swatch_x = x + 500
        for key in ("primary", "secondary", "tertiary", "support", "neutral"):
            color = palette[key]
            draw.rounded_rectangle(
                (swatch_x, y + 10, swatch_x + 86, y + 54),
                radius=8,
                fill=color,
            )
            swatch_x += 98
        draw.text(
            (x + 8, y + tile_h - 35),
            f"{palette['primary']}  {palette['secondary']}  {palette['tertiary']}",
            fill="#69737A",
            font=hex_font,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, dpi=(200, 200), optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render palette candidates for TRI Figure 5.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = base.read_full_data()
    stems = {
        slug: render_candidate(data, args.output_dir, slug, palette)
        for slug, palette in PALETTES.items()
    }
    contact_sheet = args.output_dir / "figure5_palette_comparison.png"
    make_contact_sheet(stems, contact_sheet)
    manifest = {
        "status": "palette candidates only; not integrated into the paper",
        "structure": "selected Figure 5 option F v3",
        "source": str(base.DATA),
        "source_sha256": hashlib.sha256(base.DATA.read_bytes()).hexdigest(),
        "candidate_count": len(PALETTES),
        "palettes": PALETTES,
        "outputs": {slug: str(stem) for slug, stem in stems.items()},
        "contact_sheet": str(contact_sheet),
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
