from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
REPORT = ROOT / "reports" / "call_matched_authorization_ablation_v2.json"
OUTPUTS = (
    ROOT / "reports" / "figures" / "tri_call_matched_ablation.pdf",
    REPOSITORY / "paper" / "Figures" / "tri_call_matched_ablation.pdf",
)

INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#5B6570")
GRID = colors.HexColor("#D3D9DF")
QWEN = colors.HexColor("#407A7F")
GLM = colors.HexColor("#E56D4E")
HARM = colors.HexColor("#C85A46")
REPAIR = colors.HexColor("#60AA84")
FONT = "TRIHelvetica"
BOLD = "TRIHelvetica-Bold"

pdfmetrics.registerFont(TTFont(FONT, "/System/Library/Fonts/Helvetica.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont(BOLD, "/System/Library/Fonts/Helvetica.ttc", subfontIndex=1))


def label(c: canvas.Canvas, x: float, y: float, value: str, size: float = 9, bold: bool = False, color=INK) -> None:
    c.setFillColor(color)
    c.setFont(BOLD if bold else FONT, size)
    c.drawString(x, y, value)


def centered(c: canvas.Canvas, x: float, y: float, value: str, size: float = 9, bold: bool = False, color=INK) -> None:
    c.setFillColor(color)
    c.setFont(BOLD if bold else FONT, size)
    c.drawCentredString(x, y, value)


def model_rows(report: dict) -> list[tuple[str, colors.Color, str, dict]]:
    rows = {row["model"]: row for row in report["models"]}
    return [
        ("Qwen", QWEN, "circle", rows["Qwen/Qwen3.5-122B-A10B"]),
        ("GLM", GLM, "square", rows["Pro/zai-org/GLM-5.1"]),
    ]


def draw_marker(c: canvas.Canvas, x: float, y: float, shape: str, color) -> None:
    c.setFillColor(color)
    c.setStrokeColor(colors.white)
    c.setLineWidth(0.7)
    if shape == "circle":
        c.circle(x, y, 3.6, fill=1, stroke=1)
    else:
        c.rect(x - 3.4, y - 3.4, 6.8, 6.8, fill=1, stroke=1)


def draw_metric_panel(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    panel: str,
    title: str,
    metric: str,
    ymax: float,
    rows: list[tuple[str, colors.Color, str, dict]],
) -> None:
    label(c, x, y + h - 10, panel, 9.5, True)
    label(c, x + 18, y + h - 10, title, 9.5, True)
    left, right = x + 30, x + w - 7
    bottom, top = y + 40, y + h - 32
    conditions = ("history_only", "decision_visible", "decision_enforced")
    names = ("History", "Decision", "Enforced")

    def sx(index: int, offset: float) -> float:
        return left + index * (right - left) / 2 + offset

    def sy(value: float) -> float:
        return bottom + value / ymax * (top - bottom)

    for tick in range(0, int(ymax) + 1, 20):
        yy = sy(tick)
        c.setStrokeColor(GRID)
        c.setLineWidth(0.45)
        c.line(left, yy, right, yy)
        c.setFillColor(MUTED)
        c.setFont(FONT, 8.5)
        c.drawRightString(left - 5, yy - 3, str(tick))

    for index, name in enumerate(names):
        centered(c, sx(index, 0), bottom - 18, name, 8.5, color=MUTED)

    for model_index, (model, color, shape, model_row) in enumerate(rows):
        offset = -3.5 if model_index == 0 else 3.5
        points: list[tuple[float, float]] = []
        for index, condition in enumerate(conditions):
            cell = model_row["metrics"][condition][metric]
            value = 100 * cell["rate"]
            low, high = [100 * item for item in cell["ci95_state_cluster"]]
            xx, yy = sx(index, offset), sy(value)
            points.append((xx, yy))
            c.setStrokeColor(color)
            c.setLineWidth(1.0)
            c.line(xx, sy(low), xx, sy(high))
            c.line(xx - 2.6, sy(low), xx + 2.6, sy(low))
            c.line(xx - 2.6, sy(high), xx + 2.6, sy(high))
            draw_marker(c, xx, yy, shape, color)
        c.setStrokeColor(color)
        c.setLineWidth(1.35)
        c.setLineJoin(1)
        path = c.beginPath()
        path.moveTo(*points[0])
        for point in points[1:]:
            path.lineTo(*point)
        c.drawPath(path, stroke=1, fill=0)

    centered(c, (left + right) / 2, y + 5, "Outcome condition", 8.5, color=MUTED)
    c.saveState()
    c.translate(x + 5, (bottom + top) / 2)
    c.rotate(90)
    centered(c, 0, 0, "Percent", 8.5, color=MUTED)
    c.restoreState()


def draw_enforcement_panel(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    rows: list[tuple[str, colors.Color, str, dict]],
) -> None:
    label(c, x, y + h - 10, "C", 9.5, True)
    label(c, x + 18, y + h - 10, "Enforcement changes", 9.5, True)
    left, right = x + 24, x + w - 8
    center_x = left + (right - left) * 8 / 14
    top = y + h - 63
    scale = (right - left) / 14
    c.setStrokeColor(GRID)
    c.setLineWidth(0.7)
    c.line(center_x, y + 42, center_x, top + 20)
    centered(c, center_x, y + 25, "0", 8.5, color=MUTED)
    centered(c, left + 2 * scale, y + 25, "harms", 8.5, color=HARM)
    centered(c, right - 2 * scale, y + 25, "repairs", 8.5, color=REPAIR)

    for index, (model, _color, _shape, model_row) in enumerate(rows):
        yy = top - index * 54
        harms = model_row["enforcement"]["harms"]
        repairs = model_row["enforcement"]["repairs"]
        label(c, left, yy + 15, model, 9, True)
        c.setFillColor(HARM)
        c.rect(center_x - harms * scale, yy - 5, harms * scale, 10, fill=1, stroke=0)
        c.setFillColor(REPAIR)
        c.rect(center_x, yy - 5, repairs * scale, 10, fill=1, stroke=0)
        label(c, center_x - harms * scale - 10, yy - 3, str(harms), 8.5, True, HARM)
        label(c, center_x + repairs * scale + 3, yy - 3, str(repairs), 8.5, True, REPAIR)


def make_figure(output: Path, report: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height = 7.1 * inch, 3.15 * inch
    c = canvas.Canvas(str(output), pagesize=(width, height), initialFontName=FONT)
    c.setTitle("Equal-call decision visibility")
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    label(c, 16, height - 18, "Equal-call decision visibility", 10.5, True)
    rows = model_rows(report)

    draw_metric_panel(c, 12, 10, 184, height - 35, "A", "Changed PairAcc", "changed_pairacc", 80, rows)
    draw_metric_panel(
        c,
        200,
        10,
        184,
        height - 35,
        "B",
        "Preserve substitution",
        "preserve_conditional_substitution",
        80,
        rows,
    )
    draw_enforcement_panel(c, 390, 10, width - 402, height - 35, rows)

    label(c, width - 106, height - 18, "Qwen", 8.8, color=QWEN)
    draw_marker(c, width - 116, height - 15, "circle", QWEN)
    label(c, width - 42, height - 18, "GLM", 8.8, color=GLM)
    draw_marker(c, width - 52, height - 15, "square", GLM)
    c.showPage()
    c.save()


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    for output in OUTPUTS:
        make_figure(output, report)
        print(output)


if __name__ == "__main__":
    main()
