from __future__ import annotations

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "outputs" / "fig1_shared_transition_symmetric_v1.pdf"

W = 6.9 * 72
H = 3.15 * 72
SX = W / 100
SY = H / 45

INK = HexColor("#28343A")
CHARCOAL = HexColor("#4A4D4F")
MUTED = HexColor("#69787E")
HAIRLINE = HexColor("#B9C3C5")
TEAL = HexColor("#2D7F7B")
TEAL_LIGHT = HexColor("#E5F1EF")
CORAL = HexColor("#B94D49")
CORAL_LIGHT = HexColor("#F7E7E3")
BLUE = HexColor("#66899D")
PAPER = HexColor("#FFFFFF")
PANEL = HexColor("#F7F9F9")


def x(value: float) -> float:
    return value * SX


def y(value: float) -> float:
    return value * SY


def register_fonts() -> None:
    root = Path("/System/Library/Fonts/Supplemental")
    pdfmetrics.registerFont(TTFont("FigureSans", root / "Arial.ttf"))
    pdfmetrics.registerFont(TTFont("FigureSans-Bold", root / "Arial Bold.ttf"))
    pdfmetrics.registerFont(TTFont("FigureSans-Italic", root / "Arial Italic.ttf"))


def text(
    c: canvas.Canvas,
    px: float,
    py: float,
    value: str,
    size: float,
    color=INK,
    font: str = "FigureSans",
    align: str = "left",
) -> None:
    c.setFillColor(color)
    c.setFont(font, size)
    if align == "center":
        c.drawCentredString(x(px), y(py) - size * 0.33, value)
    elif align == "right":
        c.drawRightString(x(px), y(py) - size * 0.33, value)
    else:
        c.drawString(x(px), y(py) - size * 0.33, value)


def multiline(
    c: canvas.Canvas,
    px: float,
    py: float,
    lines: list[str],
    size: float,
    leading: float,
    color=INK,
    font: str = "FigureSans",
    align: str = "left",
) -> None:
    for index, line in enumerate(lines):
        text(c, px, py - index * leading / SY, line, size, color, font, align)


def panel(c: canvas.Canvas, px: float, py: float, width: float, height: float, title: str) -> None:
    c.setFillColor(PANEL)
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.8)
    c.roundRect(x(px), y(py), x(width), y(height), 4.2, fill=1, stroke=1)
    c.setFillColor(CHARCOAL)
    c.rect(x(px), y(py + height - 3.7), x(width), y(3.7), fill=1, stroke=0)
    text(c, px + width / 2, py + height - 1.85, title, 8.5, PAPER, "FigureSans-Bold", "center")


def arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, color=CHARCOAL, width: float = 1.2) -> None:
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x(x1), y(y1), x(x2 - 1.2), y(y2))
    c.saveState()
    c.translate(x(x2), y(y2))
    c.rotate(0)
    path = c.beginPath()
    path.moveTo(0, 0)
    path.lineTo(-x(1.5), y(0.7))
    path.lineTo(-x(1.5), -y(0.7))
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    c.restoreState()


def envelope(c: canvas.Canvas, cx: float, cy: float, label: str, accent) -> None:
    width, height = 10.7, 7.1
    for dx, dy in ((2.0, 1.5), (1.0, 0.75)):
        c.setFillColor(PAPER)
        c.setStrokeColor(HAIRLINE)
        c.setLineWidth(0.55)
        c.roundRect(x(cx - width / 2 + dx), y(cy - height / 2 + dy), x(width), y(height), 2.8, fill=1, stroke=1)
    left, bottom = cx - width / 2, cy - height / 2
    c.setFillColor(PAPER)
    c.setStrokeColor(accent)
    c.setLineWidth(1.0)
    c.roundRect(x(left), y(bottom), x(width), y(height), 2.8, fill=1, stroke=1)
    c.setFillColor(accent)
    c.rect(x(left), y(bottom + height - 0.65), x(width), y(0.65), fill=1, stroke=0)
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.65)
    path = c.beginPath()
    path.moveTo(x(left + 0.35), y(bottom + height - 0.8))
    path.lineTo(x(cx), y(bottom + 2.25))
    path.lineTo(x(left + width - 0.35), y(bottom + height - 0.8))
    c.drawPath(path, fill=0, stroke=1)
    text(c, cx, cy - 0.1, label, 13.2, INK, "FigureSans-Bold", "center")


def lock_icon(c: canvas.Canvas, px: float, py: float, color) -> None:
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.rect(x(px - 0.85), y(py - 0.82), x(1.7), y(1.45), fill=1, stroke=0)
    c.setLineWidth(1.25)
    c.arc(x(px - 0.65), y(py + 0.2), x(px + 0.65), y(py + 1.55), 0, 180)
    c.setFillColor(PAPER)
    c.circle(x(px), y(py - 0.05), 1.1, fill=1, stroke=0)
    c.rect(x(px - 0.1), y(py - 0.55), x(0.2), y(0.5), fill=1, stroke=0)


def hourglass_icon(c: canvas.Canvas, px: float, py: float, color) -> None:
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.0)
    c.line(x(px - 0.9), y(py + 1.0), x(px + 0.9), y(py + 1.0))
    c.line(x(px - 0.9), y(py - 1.0), x(px + 0.9), y(py - 1.0))
    c.line(x(px - 0.68), y(py + 0.82), x(px + 0.68), y(py - 0.82))
    c.line(x(px + 0.68), y(py + 0.82), x(px - 0.68), y(py - 0.82))
    top = c.beginPath()
    top.moveTo(x(px - 0.5), y(py + 0.55))
    top.lineTo(x(px + 0.5), y(py + 0.55))
    top.lineTo(x(px), y(py + 0.05))
    top.close()
    c.drawPath(top, fill=1, stroke=0)
    bottom = c.beginPath()
    bottom.moveTo(x(px - 0.5), y(py - 0.62))
    bottom.lineTo(x(px + 0.5), y(py - 0.62))
    bottom.lineTo(x(px), y(py - 0.08))
    bottom.close()
    c.drawPath(bottom, fill=1, stroke=0)


def state_row(c: canvas.Canvas, py: float, mode: str, description: str, correct: str, color, icon: str) -> None:
    c.setFillColor(PAPER)
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.65)
    c.roundRect(x(54.3), y(py - 2.75), x(42.6), y(5.5), 3.2, fill=1, stroke=1)
    if icon == "lock":
        lock_icon(c, 57.5, py, color)
    else:
        hourglass_icon(c, 57.5, py, color)
    if mode == "DEFERRED UNTIL AFTER REFRESH":
        multiline(c, 60.1, py + 1.15, ["DEFERRED UNTIL", "AFTER REFRESH"], 7.7, 7.2, color, "FigureSans-Bold")
        text(c, 60.1, py - 1.42, description, 7.2, MUTED)
    else:
        text(c, 60.1, py + 0.82, mode, 8.2, color, "FigureSans-Bold")
        text(c, 60.1, py - 1.0, description, 7.2, MUTED)
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.55)
    c.line(x(86.0), y(py - 2.0), x(86.0), y(py + 2.0))
    text(c, 91.6, py + 0.65, "correct", 7.2, MUTED, "FigureSans-Bold", "center")
    text(c, 91.6, py - 0.72, correct, 10.4, color, "FigureSans-Bold", "center")


def matched_row(
    c: canvas.Canvas,
    py: float,
    mode: str,
    instruction: list[str],
    correct: str,
    failure: list[str],
    color,
    fill,
) -> None:
    c.setFillColor(fill)
    c.rect(x(2.0), y(py - 3.25), x(95.0), y(6.5), fill=1, stroke=0)
    text(c, 8.4, py, mode, 7.9, color, "FigureSans-Bold", "center")
    multiline(c, 17.0, py + 0.65, instruction, 7.55, 8.3, INK)
    text(c, 70.1, py, correct, 9.0, color, "FigureSans-Bold", "center")
    c.setFillColor(PAPER)
    c.setStrokeColor(CORAL)
    c.setLineWidth(0.85)
    c.roundRect(x(79.0), y(py - 2.15), x(15.2), y(4.3), 3.0, fill=1, stroke=1)
    multiline(c, 86.6, py + 0.65, failure, 7.4, 8.1, CORAL, "FigureSans-Bold", "center")


def build() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(
        str(OUTPUT),
        pagesize=(W, H),
        pageCompression=1,
        initialFontName="FigureSans",
        initialFontSize=9,
    )
    c.setTitle("TRI shared transition with symmetric failure modes")

    panel(c, 2.0, 24.0, 47.0, 19.0, "SHARED STATE TRANSITION")
    panel(c, 51.0, 24.0, 47.0, 19.0, "REFERENTIAL CONTROL STATE")

    envelope(c, 13.1, 34.0, "A", CORAL)
    envelope(c, 39.0, 34.0, "B", TEAL)
    arrow(c, 20.2, 34.0, 31.9, 34.0)
    text(c, 26.0, 35.75, "REFRESH", 7.4, BLUE, "FigureSans-Bold", "center")
    multiline(c, 13.1, 29.0, ["Before refresh", "A is highest priority"], 7.4, 7.8, INK, "FigureSans", "center")
    multiline(c, 39.0, 29.0, ["After refresh", "B is highest priority"], 7.4, 7.8, INK, "FigureSans", "center")
    c.setFillColor(TEAL_LIGHT)
    c.roundRect(x(5.0), y(24.55), x(40.9), y(2.15), y(1.0), fill=1, stroke=0)
    text(c, 25.45, 25.65, "Both snapshots and stable IDs remain available", 7.0, TEAL, "FigureSans-Bold", "center")

    state_row(c, 35.4, "BOUND BEFORE REFRESH", "reply to 'it' retains committed entity", "Email A", CORAL, "lock")
    state_row(c, 28.7, "DEFERRED UNTIL AFTER REFRESH", "resolve selector only after the update", "Email B", TEAL, "hourglass")

    text(
        c,
        50.0,
        22.55,
        "Same states, selector, transition, and action  |  wording encodes commitment timing",
        7.3,
        MUTED,
        "FigureSans-Italic",
        "center",
    )

    c.setFillColor(CHARCOAL)
    c.rect(x(2.0), y(18.5), x(95.0), y(2.7), fill=1, stroke=0)
    for px in (14.6, 63.2, 76.8):
        c.setStrokeColor(HAIRLINE)
        c.setLineWidth(0.6)
        c.line(x(px), y(4.55), x(px), y(21.2))
    text(c, 8.4, 19.85, "TIMING", 7.4, PAPER, "FigureSans-Bold", "center")
    text(c, 38.8, 19.85, "INSTRUCTION", 7.4, PAPER, "FigureSans-Bold", "center")
    text(c, 70.1, 19.85, "CORRECT TARGET", 7.4, PAPER, "FigureSans-Bold", "center")
    text(c, 86.6, 19.85, "FAILURE EXPOSED", 7.4, PAPER, "FigureSans-Bold", "center")

    matched_row(
        c,
        14.9,
        "PRESERVE",
        ["Choose the highest-priority unread email now.", "Refresh, then reply to it."],
        "Email A",
        ["A → B", "over-reevaluate"],
        CORAL,
        CORAL_LIGHT,
    )
    matched_row(
        c,
        7.8,
        "REEVALUATE",
        ["Refresh the mailbox first.", "Then choose the highest-priority unread email and reply."],
        "Email B",
        ["B → A", "over-lock"],
        TEAL,
        TEAL_LIGHT,
    )
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.65)
    c.line(x(2.0), y(4.55), x(97.0), y(4.55))
    c.line(x(2.0), y(11.65), x(97.0), y(11.65))
    c.setStrokeColor(CHARCOAL)
    c.line(x(2.0), y(18.5), x(97.0), y(18.5))

    c.showPage()
    c.save()


if __name__ == "__main__":
    build()
