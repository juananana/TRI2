from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#5B6570")
LINE = colors.HexColor("#CBD2D9")
GENERIC = colors.HexColor("#7A8793")
LIFECYCLE = colors.HexColor("#126F66")
GENERIC_FREE = colors.HexColor("#AAB2BA")
GENERIC_GATE = colors.HexColor("#65717C")
LIFECYCLE_FREE = colors.HexColor("#69B7AA")
LIFECYCLE_GATE = colors.HexColor("#126F66")
ACCENT = colors.HexColor("#B64926")
PALE_GREEN = colors.HexColor("#E8F3F1")
PALE_ORANGE = colors.HexColor("#F8ECE7")
PALE_GRAY = colors.HexColor("#F1F3F5")
FONT_REGULAR = "TRIHelvetica"
FONT_BOLD = "TRIHelvetica-Bold"

pdfmetrics.registerFont(
    TTFont(FONT_REGULAR, "/System/Library/Fonts/Helvetica.ttc", subfontIndex=0)
)
pdfmetrics.registerFont(
    TTFont(FONT_BOLD, "/System/Library/Fonts/Helvetica.ttc", subfontIndex=1)
)


def text(c: canvas.Canvas, x: float, y: float, value: str, size: float = 9.2, bold: bool = False, color=INK) -> None:
    c.setFillColor(color)
    c.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    c.drawString(x, y, value)


def centered(c: canvas.Canvas, x: float, y: float, value: str, size: float = 9.2, bold: bool = False, color=INK) -> None:
    c.setFillColor(color)
    c.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    c.drawCentredString(x, y, value)


def box(c: canvas.Canvas, x: float, y: float, w: float, h: float, fill, stroke=LINE, radius: float = 5) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, color=MUTED) -> None:
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(0.8)
    c.line(x1, y1, x2, y2)
    angle = 4
    if abs(x2 - x1) >= abs(y2 - y1):
        sign = 1 if x2 >= x1 else -1
        c.line(x2, y2, x2 - sign * angle, y2 + 2.5)
        c.line(x2, y2, x2 - sign * angle, y2 - 2.5)
    else:
        sign = 1 if y2 >= y1 else -1
        c.line(x2, y2, x2 + 2.5, y2 - sign * angle)
        c.line(x2, y2, x2 - 2.5, y2 - sign * angle)


def fit_centered(c: canvas.Canvas, x: float, y: float, value: str, max_width: float, size: float = 9.2, bold: bool = False, color=INK) -> None:
    font = FONT_BOLD if bold else FONT_REGULAR
    while size > 9.0 and stringWidth(value, font, size) > max_width:
        size -= 0.2
    centered(c, x, y, value, size, bold, color)


def draw_first_figure(path: Path) -> None:
    """Draw the matched TRI contrast at AAAI's final nine-point minimum."""
    width, height = 3.35 * inch, 2.05 * inch
    c = canvas.Canvas(
        str(path), pagesize=(width, height), pageCompression=1,
        initialFontName=FONT_REGULAR, initialFontSize=9.2,
    )
    c.setTitle("Formal state-transition view of a TRI minimal pair")
    c.setAuthor("anonymous")
    c.setCreator("anonymous")

    margin = 6
    content_w = width - 2 * margin
    text(c, margin, height - 13, "Same update, opposite authorized targets", 9.5, True)

    state_y = height - 49
    box(c, margin, state_y, content_w, 25, PALE_GRAY, radius=3)
    centered(
        c,
        margin + content_w / 2,
        state_y + 8,
        "S0: q -> A     refresh     S1: q -> B; A stays valid",
        9.2,
        True,
    )

    label_w = 72
    gap = 7
    action_x = margin + label_w + gap
    action_w = content_w - label_w - gap
    for y, mode, timing, action, color, fill in (
        (50, "PRESERVE", "bind now", "bind A  ->  refresh  ->  write A", LIFECYCLE, PALE_GREEN),
        (8, "REEVALUATE", "refresh first", "refresh  ->  resolve q  ->  write B", ACCENT, PALE_ORANGE),
    ):
        box(c, margin, y, label_w, 34, fill, stroke=color, radius=3)
        centered(c, margin + label_w / 2, y + 19, mode, 9.2, True, color)
        centered(c, margin + label_w / 2, y + 7, timing, 9.2, False, INK)
        box(c, action_x, y, action_w, 34, colors.white, stroke=color, radius=3)
        centered(c, action_x + action_w / 2, y + 12, action, 9.2, True, color)

    c.showPage()
    c.save()


def draw_mechanism(path: Path) -> None:
    # This panel is printed at a single-column width. Keep only the diagnostic
    # contrast here; implementation details belong in the text and supplement.
    width, height = 3.35 * inch, 2.55 * inch
    c = canvas.Canvas(
        str(path), pagesize=(width, height), pageCompression=1,
        initialFontName=FONT_REGULAR, initialFontSize=9.2,
    )
    c.setTitle("Authorization contrast in temporal referent integrity")

    margin = 7
    content_w = width - 2 * margin
    text(c, margin, height - 13, "Same refresh, opposite authorized targets", 8.2, True)

    state_y = height - 37
    box(c, margin, state_y, content_w, 18, PALE_GRAY, radius=3)
    centered(c, margin + content_w / 2, state_y + 6.5,
             "S0: A wins q  ->  refresh  ->  S1: B wins q; A remains valid", 6.2, True)

    label_w, decision_w, output_w = 57, 94, 58
    gap = (content_w - label_w - decision_w - output_w) / 2
    label_x = margin
    decision_x = label_x + label_w + gap
    output_x = decision_x + decision_w + gap
    lane_h = 40
    preserve_y = state_y - 49
    reevaluate_y = preserve_y - 49

    box(c, label_x, preserve_y, label_w, lane_h, PALE_GREEN, radius=4)
    centered(c, label_x + label_w / 2, preserve_y + 25, "PRESERVE", 6.7, True, LIFECYCLE)
    centered(c, label_x + label_w / 2, preserve_y + 13, "choose q now", 5.8, False)
    centered(c, label_x + label_w / 2, preserve_y + 5, "then refresh", 5.8, False)
    box(c, decision_x, preserve_y + 5, decision_w, 30, colors.white, stroke=LIFECYCLE, radius=3)
    centered(c, decision_x + decision_w / 2, preserve_y + 23, "bind A before refresh", 6.2, True, LIFECYCLE)
    centered(c, decision_x + decision_w / 2, preserve_y + 12, "keep the resolved ID", 5.5, False, MUTED)
    box(c, output_x, preserve_y + 5, output_w, 30, PALE_GREEN, stroke=LIFECYCLE, radius=3)
    centered(c, output_x + output_w / 2, preserve_y + 22, "write A", 8.8, True, LIFECYCLE)
    centered(c, output_x + output_w / 2, preserve_y + 11, "old target", 5.4, False, MUTED)
    arrow(c, label_x + label_w, preserve_y + lane_h / 2, decision_x, preserve_y + lane_h / 2)
    arrow(c, decision_x + decision_w, preserve_y + lane_h / 2, output_x, preserve_y + lane_h / 2)

    box(c, label_x, reevaluate_y, label_w, lane_h, PALE_ORANGE, radius=4)
    centered(c, label_x + label_w / 2, reevaluate_y + 25, "REEVALUATE", 6.7, True, ACCENT)
    centered(c, label_x + label_w / 2, reevaluate_y + 13, "refresh first", 5.8, False)
    centered(c, label_x + label_w / 2, reevaluate_y + 5, "then choose q", 5.8, False)
    box(c, decision_x, reevaluate_y + 5, decision_w, 30, colors.white, stroke=ACCENT, radius=3)
    centered(c, decision_x + decision_w / 2, reevaluate_y + 23, "evaluate q after refresh", 6.0, True, ACCENT)
    centered(c, decision_x + decision_w / 2, reevaluate_y + 12, "no prior target commitment", 5.4, False, MUTED)
    box(c, output_x, reevaluate_y + 5, output_w, 30, PALE_ORANGE, stroke=ACCENT, radius=3)
    centered(c, output_x + output_w / 2, reevaluate_y + 22, "write B", 8.8, True, ACCENT)
    centered(c, output_x + output_w / 2, reevaluate_y + 11, "new winner", 5.4, False, MUTED)
    arrow(c, label_x + label_w, reevaluate_y + lane_h / 2, decision_x, reevaluate_y + lane_h / 2)
    arrow(c, decision_x + decision_w, reevaluate_y + lane_h / 2, output_x, reevaluate_y + lane_h / 2)

    centered(c, margin + content_w / 2, 7,
             "Stable controls mask this difference; changed-winner pairs expose it.", 5.9, False, MUTED)

    c.showPage()
    c.save()


def draw_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, labels: list[str], values: list[list[float]], panel: str) -> None:
    text(c, x, y + h - 9, f"{panel}  {title}", 7.2, True)
    chart_y = y + 26
    chart_h = h - 47
    chart_x = x + 22
    chart_w = w - 29
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    for value in (0, 50, 100):
        yy = chart_y + chart_h * value / 100
        c.line(chart_x, yy, chart_x + chart_w, yy)
        text(c, x, yy - 2, str(value), 5.5, False, MUTED)

    group_w = chart_w / len(labels)
    fills = [GENERIC_FREE, GENERIC_GATE, LIFECYCLE_FREE, LIFECYCLE_GATE]
    bar_w = min(13, group_w * 0.17)
    for index, label in enumerate(labels):
        center_x = chart_x + group_w * (index + 0.5)
        for method, fill in enumerate(fills):
            value = values[index][method]
            offset = (method - 1.5) * bar_w * 1.08
            bx = center_x + offset - bar_w / 2
            bh = chart_h * value / 100
            c.setFillColor(fill)
            c.rect(bx, chart_y, bar_w, bh, fill=1, stroke=0)
            label_y = chart_y + bh + 3 + (6 if method % 2 else 0)
            fit_centered(c, bx + bar_w / 2, label_y, f"{value:.1f}", bar_w + 7, 5.3, True)
        fit_centered(c, center_x, y + 13, label, group_w - 2, 5.9, False, MUTED)


def draw_results(path: Path) -> None:
    width, height = 3.35 * inch, 2.65 * inch
    c = canvas.Canvas(
        str(path), pagesize=(width, height), pageCompression=1,
        initialFontName=FONT_REGULAR, initialFontSize=9.2,
    )
    c.setTitle("TRI component audit on the frozen v3 inventory")
    c.setAuthor("anonymous")
    c.setCreator("anonymous")
    c.setSubject("Controller accuracy and transition-authorization component audit")
    text(c, 5, height - 13, "v3 component audit: exact target accuracy (%)", 9.4, True)

    labels = ["Generic", "+ mode", "+ validity gate", "Untyped plan", "Rule v2*", "Exact CTA", "Lifecycle free", "Lifecycle gate"]
    qwen = [64.4, 75.0, 65.0, 81.2, 92.5, 95.0, 96.9, 98.1]
    glm = [71.9, 75.0, 73.1, 70.6, 92.5, 96.2, 98.1, 100.0]
    chart_x, chart_w = 91, width - 99
    top_y, row_gap = height - 32, 17
    for value in (50, 75, 100):
        xx = chart_x + chart_w * (value - 50) / 50
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(xx, 30, xx, top_y + 4)
        centered(c, xx, 24, str(value), 9.2, False, MUTED)

    for index, label in enumerate(labels):
        yy = top_y - index * row_gap
        text(c, 5, yy - 3, label, 9.2, index >= 5, MUTED)
        qx = chart_x + chart_w * (qwen[index] - 50) / 50
        gx = chart_x + chart_w * (glm[index] - 50) / 50
        c.setStrokeColor(LINE)
        c.setLineWidth(1.0)
        c.line(qx, yy, gx, yy)
        c.setFillColor(ACCENT)
        c.circle(qx, yy, 3.0, fill=1, stroke=0)
        c.setFillColor(LIFECYCLE)
        c.rect(gx - 3, yy - 3, 6, 6, fill=1, stroke=0)

    c.setFillColor(ACCENT)
    c.circle(8, 10, 3.0, fill=1, stroke=0)
    text(c, 14, 7, "Qwen3.5-122B", 9.2, False, MUTED)
    c.setFillColor(LIFECYCLE)
    c.rect(100, 7, 6, 6, fill=1, stroke=0)
    text(c, 111, 7, "GLM-5.1", 9.2, False, MUTED)
    text(c, 166, 7, "* post-hoc", 9.2, True, ACCENT)
    c.showPage()
    c.save()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="reports/figures")
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    draw_first_figure(outdir / "tri_first_figure.pdf")
    draw_mechanism(outdir / "tri_v3_mechanism.pdf")
    draw_results(outdir / "tri_v3_results.pdf")
    print(outdir / "tri_first_figure.pdf")
    print(outdir / "tri_v3_mechanism.pdf")
    print(outdir / "tri_v3_results.pdf")


if __name__ == "__main__":
    main()
