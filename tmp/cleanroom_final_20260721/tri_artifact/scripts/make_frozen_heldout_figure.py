from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas


MODE_ORDER = [
    "state_overwrite_once",
    "full_history_once",
    "generic_plan_then_act",
    "compile_then_act",
    "factorized_hybrid_compile_then_act",
]

MODE_LABELS = {
    "state_overwrite_once": "Overwrite",
    "full_history_once": "Full history",
    "generic_plan_then_act": "Generic plan",
    "compile_then_act": "Compile",
    "factorized_hybrid_compile_then_act": "Factorized hybrid",
}

ANCHOR = "#2F6B67"
DYNAMIC = "#C58A2B"
GRID = "#D5D5D5"
TEXT = "#202124"


def values(report: dict) -> tuple[list[str], dict[tuple[str, str, str], float]]:
    lookup = {
        (row["model"], row["mode"], row["binding"]): 100 * row["accuracy_all"]
        for row in report["by_binding"]
    }
    models = [model for model in ("GLM-5.1", "Qwen3.5") if any(key[0] == model for key in lookup)]
    return models, lookup


def draw_pdf(output: Path, models: list[str], lookup: dict[tuple[str, str, str], float]) -> None:
    width, height = 504, 205
    c = canvas.Canvas(str(output), pagesize=(width, height))
    panel_width = width / len(models)
    chart_top, chart_bottom = 168, 48
    for panel, model in enumerate(models):
        left = panel * panel_width + 38
        right = (panel + 1) * panel_width - 8
        plot_width = right - left
        c.setFillColor(HexColor(TEXT))
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString((left + right) / 2, 181, model)
        for tick in (0, 25, 50, 75, 100):
            y = chart_bottom + (chart_top - chart_bottom) * tick / 100
            c.setStrokeColor(HexColor(GRID))
            c.setLineWidth(0.5)
            c.line(left, y, right, y)
            if panel == 0:
                c.setFillColor(HexColor(TEXT))
                c.setFont("Helvetica", 6.5)
                c.drawRightString(left - 4, y - 2, str(tick))
        group_width = plot_width / len(MODE_ORDER)
        bar_width = group_width * 0.31
        for index, mode in enumerate(MODE_ORDER):
            center = left + group_width * (index + 0.5)
            for offset, binding, color in (
                (-bar_width, "anchored", ANCHOR),
                (0, "dynamic", DYNAMIC),
            ):
                value = lookup[(model, mode, binding)]
                bar_height = (chart_top - chart_bottom) * value / 100
                x = center + offset
                c.setFillColor(HexColor(color))
                c.rect(x, chart_bottom, bar_width, bar_height, stroke=0, fill=1)
                c.setFillColor(HexColor(TEXT))
                c.setFont("Helvetica", 5.5)
                c.drawCentredString(x + bar_width / 2, chart_bottom + bar_height + 2, f"{value:.0f}")
            label = MODE_LABELS[mode]
            c.saveState()
            c.translate(center, chart_bottom - 5)
            c.rotate(35)
            c.setFillColor(HexColor(TEXT))
            c.setFont("Helvetica", 5.8)
            c.drawRightString(0, 0, label)
            c.restoreState()
    legend_x = width / 2 - 57
    c.setFillColor(HexColor(ANCHOR))
    c.rect(legend_x, 195, 7, 7, stroke=0, fill=1)
    c.setFillColor(HexColor(TEXT))
    c.setFont("Helvetica", 6.5)
    c.drawString(legend_x + 10, 196, "Anchored")
    c.setFillColor(HexColor(DYNAMIC))
    c.rect(legend_x + 57, 195, 7, 7, stroke=0, fill=1)
    c.setFillColor(HexColor(TEXT))
    c.drawString(legend_x + 67, 196, "Dynamic")
    c.save()


def draw_png(output: Path, models: list[str], lookup: dict[tuple[str, str, str], float]) -> None:
    scale = 3
    width, height = 504 * scale, 205 * scale
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    font = ImageFont.truetype(font_path, 17)
    small = ImageFont.truetype(font_path, 15)
    title_font = ImageFont.truetype(font_path, 24)
    panel_width = width / len(models)
    plot_top, plot_bottom = 42 * scale, 158 * scale
    for panel, model in enumerate(models):
        left = panel * panel_width + 38 * scale
        right = (panel + 1) * panel_width - 8 * scale
        plot_width = right - left
        draw.text(((left + right) / 2, 18 * scale), model, fill=TEXT, font=title_font, anchor="mm")
        for tick in (0, 25, 50, 75, 100):
            y = plot_bottom - (plot_bottom - plot_top) * tick / 100
            draw.line((left, y, right, y), fill=GRID, width=2)
            if panel == 0:
                draw.text((left - 8, y), str(tick), fill=TEXT, font=small, anchor="rm")
        group_width = plot_width / len(MODE_ORDER)
        bar_width = group_width * 0.31
        for index, mode in enumerate(MODE_ORDER):
            center = left + group_width * (index + 0.5)
            for offset, binding, color in ((-bar_width, "anchored", ANCHOR), (0, "dynamic", DYNAMIC)):
                value = lookup[(model, mode, binding)]
                bar_height = (plot_bottom - plot_top) * value / 100
                x = center + offset
                y = plot_bottom - bar_height
                draw.rectangle((x, y, x + bar_width, plot_bottom), fill=color)
                draw.text((x + bar_width / 2, y - 4), f"{value:.0f}", fill=TEXT, font=small, anchor="mb")
            label = "Factorized\nhybrid" if mode == "factorized_hybrid_compile_then_act" else MODE_LABELS[mode]
            draw.multiline_text(
                (center, plot_bottom + 10), label, fill=TEXT, font=small,
                anchor="ma", align="center", spacing=0,
            )
    draw.rectangle((width - 300, 15, width - 280, 35), fill=ANCHOR)
    draw.text((width - 270, 25), "Anchored", fill=TEXT, font=font, anchor="lm")
    draw.rectangle((width - 160, 15, width - 140, 35), fill=DYNAMIC)
    draw.text((width - 130, 25), "Dynamic", fill=TEXT, font=font, anchor="lm")
    image.save(output)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    models, lookup = values(report)
    if not models:
        raise SystemExit("No supported model rows found")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    draw_pdf(output, models, lookup)
    draw_png(output.with_suffix(".png"), models, lookup)
    print(output)


if __name__ == "__main__":
    main()
