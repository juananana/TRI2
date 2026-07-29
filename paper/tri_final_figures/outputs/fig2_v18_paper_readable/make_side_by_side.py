#!/usr/bin/env python3
"""Build the Figure 1/Figure 2 visual-family comparison used for QA."""

from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: make_side_by_side.py FIG1.png FIG2.png OUT.png")

    fig1 = Image.open(sys.argv[1]).convert("RGB")
    fig2 = Image.open(sys.argv[2]).convert("RGB")
    label_height = 34
    gap = 28
    canvas = Image.new(
        "RGB",
        (fig1.width + gap + fig2.width, label_height + max(fig1.height, fig2.height)),
        "white",
    )
    canvas.paste(fig1, (0, label_height))
    canvas.paste(fig2, (fig1.width + gap, label_height))

    draw = ImageDraw.Draw(canvas)
    font = load_font(16)
    draw.text((8, 8), "Figure 1 reference", fill="#407A7F", font=font)
    draw.text((fig1.width + gap + 8, 8), "Figure 2 v18 final", fill="#407A7F", font=font)
    canvas.save(sys.argv[3], dpi=(180, 180))


if __name__ == "__main__":
    main()
