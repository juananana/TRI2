#!/usr/bin/env python3
"""Compose the current Figure 3--6 candidates for visual-system QA."""

from __future__ import annotations

from pathlib import Path

from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "outputs" / "result_figure_system_v2" / "result_figure_contact_sheet.png"
FIGURES = [
    (
        "FIGURE 3 · POLICY DISCRIMINATION",
        ROOT / "outputs" / "figure3_palette_final_v3" / "figure3_palette_d_forest_ember.png",
    ),
    (
        "FIGURE 4 · CONDITIONAL SUBSTITUTION",
        ROOT / "outputs" / "result_closure_v6" / "result_conditional_pairing_ab.png",
    ),
    (
        "FIGURE 5 · STRICT SQLITE OPPORTUNITIES",
        ROOT / "outputs" / "figure5_strict_unit_results_v1" / "figure5_strict_unit_results.png",
    ),
    (
        "FIGURE 6 · EQUAL-CALL EFFECTS",
        ROOT / "outputs" / "figure6_effect_ladder_v1" / "figure6_effect_ladder.png",
    ),
]

INK = "#264A56"
MUTED = "#5F6B70"
PALETTE = ["#8B6F8E", "#E56D4E", "#407A7F", "#60AA84", "#D8D4CF"]


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    props = font_manager.FontProperties(family="DejaVu Sans", weight="bold" if bold else "normal")
    return ImageFont.truetype(font_manager.findfont(props), size=size)


def main() -> None:
    tile_w, tile_h = 1320, 900
    margin, gap, heading_h = 55, 38, 115
    canvas = Image.new(
        "RGB",
        (2 * tile_w + 2 * margin + gap, 2 * tile_h + 2 * margin + gap + heading_h),
        "white",
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 34), "TRI RESULT FIGURE SYSTEM", fill=INK, font=font(34, bold=True))
    draw.text((margin, 79), "single-column candidates · shared model and semantic palette", fill=MUTED, font=font(21))
    swatch_x = canvas.width - margin - len(PALETTE) * 72
    for color in PALETTE:
        draw.rounded_rectangle((swatch_x, 42, swatch_x + 54, 86), radius=5, fill=color)
        swatch_x += 72

    for index, (label, path) in enumerate(FIGURES):
        row, col = divmod(index, 2)
        x = margin + col * (tile_w + gap)
        y = margin + heading_h + row * (tile_h + gap)
        draw.text((x + 6, y + 4), label, fill=INK, font=font(24, bold=True))
        with Image.open(path).convert("RGB") as image:
            fitted = ImageOps.contain(image, (tile_w - 20, tile_h - 56), method=Image.Resampling.LANCZOS)
            paste_x = x + (tile_w - fitted.width) // 2
            paste_y = y + 48 + (tile_h - 52 - fitted.height) // 2
            canvas.paste(fitted, (paste_x, paste_y))
        draw.line((x, y + tile_h - 2, x + tile_w, y + tile_h - 2), fill="#E4E0DC", width=2)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, dpi=(180, 180), optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
