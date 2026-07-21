from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#5B6570")
LINE = colors.HexColor("#CBD2D9")
GENERIC = colors.HexColor("#7A8793")
LIFECYCLE = colors.HexColor("#167D73")
GENERIC_FREE = colors.HexColor("#AAB2BA")
GENERIC_GATE = colors.HexColor("#65717C")
LIFECYCLE_FREE = colors.HexColor("#69B7AA")
LIFECYCLE_GATE = colors.HexColor("#167D73")
ACCENT = colors.HexColor("#C4572D")
PALE_GREEN = colors.HexColor("#E8F3F1")
PALE_ORANGE = colors.HexColor("#F8ECE7")
PALE_GRAY = colors.HexColor("#F1F3F5")


def text(c: canvas.Canvas, x: float, y: float, value: str, size: float = 7.0, bold: bool = False, color=INK) -> None:
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, value)


def centered(c: canvas.Canvas, x: float, y: float, value: str, size: float = 7.0, bold: bool = False, color=INK) -> None:
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
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


def fit_centered(c: canvas.Canvas, x: float, y: float, value: str, max_width: float, size: float = 7.0, bold: bool = False, color=INK) -> None:
    font = "Helvetica-Bold" if bold else "Helvetica"
    while size > 5.2 and stringWidth(value, font, size) > max_width:
        size -= 0.2
    centered(c, x, y, value, size, bold, color)


def draw_mechanism(path: Path) -> None:
    width, height = 7.0 * inch, 2.52 * inch
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Post-binding temporal authorization and TRI control")

    margin, gap = 8, 10
    left_w = 320
    right_x = margin + left_w + gap
    right_w = width - right_x - margin

    text(c, margin, height - 13, "A  Same world update, different authorization", 8.0, True)
    text(c, right_x, height - 13, "B  Lifecycle representation", 8.0, True)

    state_y = height - 40
    box(c, margin, state_y, left_w, 20, PALE_GRAY, radius=3)
    centered(c, margin + left_w / 2, state_y + 7, "S0: A wins selector q    |    refresh    |    S1: B wins q; A remains action-valid", 6.5, True)

    lane_x, instruction_w = margin, 126
    mid_x, mid_w = lane_x + instruction_w + 12, 70
    out_x, out_w = mid_x + mid_w + 38, 74
    lane_h = 44
    preserve_y = state_y - 52
    reevaluate_y = preserve_y - 52

    box(c, lane_x, preserve_y, instruction_w, lane_h, PALE_GREEN, radius=4)
    text(c, lane_x + 7, preserve_y + 29, "PRESERVE", 7.1, True, LIFECYCLE)
    text(c, lane_x + 7, preserve_y + 17, '"Choose q now; refresh;', 6.4)
    text(c, lane_x + 7, preserve_y + 7, 'then act on it."', 6.4)
    box(c, mid_x, preserve_y + 8, mid_w, 28, colors.white, stroke=LIFECYCLE, radius=3)
    centered(c, mid_x + mid_w / 2, preserve_y + 24, "bind at S0", 6.2, True, LIFECYCLE)
    centered(c, mid_x + mid_w / 2, preserve_y + 13, "d(r) = A", 7.0, True)
    arrow(c, lane_x + instruction_w, preserve_y + lane_h / 2, mid_x, preserve_y + lane_h / 2)
    arrow(c, mid_x + mid_w, preserve_y + lane_h / 2, out_x, preserve_y + lane_h / 2)
    box(c, out_x, preserve_y + 8, out_w, 28, PALE_GREEN, stroke=LIFECYCLE, radius=3)
    centered(c, out_x + out_w / 2, preserve_y + 24, "authorized target", 5.8, False, MUTED)
    centered(c, out_x + out_w / 2, preserve_y + 12, "A", 10.0, True, LIFECYCLE)

    box(c, lane_x, reevaluate_y, instruction_w, lane_h, PALE_ORANGE, radius=4)
    text(c, lane_x + 7, reevaluate_y + 29, "REEVALUATE", 7.1, True, ACCENT)
    text(c, lane_x + 7, reevaluate_y + 17, '"Refresh first; then choose q', 6.4)
    text(c, lane_x + 7, reevaluate_y + 7, 'and act."', 6.4)
    box(c, mid_x, reevaluate_y + 8, mid_w, 28, colors.white, stroke=ACCENT, radius=3)
    centered(c, mid_x + mid_w / 2, reevaluate_y + 24, "defer to S1", 6.2, True, ACCENT)
    centered(c, mid_x + mid_w / 2, reevaluate_y + 13, "d(r) unbound", 6.4, True)
    arrow(c, lane_x + instruction_w, reevaluate_y + lane_h / 2, mid_x, reevaluate_y + lane_h / 2)
    arrow(c, mid_x + mid_w, reevaluate_y + lane_h / 2, out_x, reevaluate_y + lane_h / 2)
    box(c, out_x, reevaluate_y + 8, out_w, 28, PALE_ORANGE, stroke=ACCENT, radius=3)
    centered(c, out_x + out_w / 2, reevaluate_y + 24, "authorized target", 5.8, False, MUTED)
    centered(c, out_x + out_w / 2, reevaluate_y + 12, "B = q(S1)", 8.0, True, ACCENT)

    # Right panel: compact implementation pipeline.
    initial_y, compiler_y, record_y, mutation_y = state_y - 5, 98, 54, 10
    box(c, right_x, initial_y, right_w, 25, PALE_GRAY, radius=3)
    centered(c, right_x + right_w / 2, initial_y + 10, "instruction + initial state S0", 6.7, True)
    arrow(c, right_x + right_w / 2, initial_y, right_x + right_w / 2, compiler_y + 30)
    box(c, right_x + 20, compiler_y, right_w - 40, 30, colors.white, stroke=LIFECYCLE, radius=4)
    centered(c, right_x + right_w / 2, compiler_y + 18, "Lifecycle compiler", 7.0, True, LIFECYCLE)
    centered(c, right_x + right_w / 2, compiler_y + 7, "learn mode + bound identity", 5.9, False, MUTED)
    arrow(c, right_x + right_w / 2, compiler_y, right_x + right_w / 2, record_y + 36)
    box(c, right_x + 5, record_y, right_w - 10, 36, PALE_GREEN, stroke=LIFECYCLE, radius=4)
    centered(c, right_x + right_w / 2, record_y + 21, "Reference contract L(r)", 7.0, True, LIFECYCLE)
    centered(c, right_x + right_w / 2, record_y + 8, "mode | ID | selector | validity | fallback", 5.8)
    arrow(c, right_x + right_w / 2, record_y, right_x + right_w / 2, mutation_y + 34)
    box(c, right_x + 5, mutation_y, right_w - 10, 34, colors.white, stroke=GENERIC_GATE, radius=4)
    centered(c, right_x + right_w / 2, mutation_y + 20, "Mutation boundary", 7.0, True)
    centered(c, right_x + right_w / 2, mutation_y + 8, "actor or gate; enforce action validity", 5.8, False, MUTED)

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
    width, height = 3.35 * inch, 2.55 * inch
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("TRI component audit on the frozen v3 inventory")
    c.setAuthor("anonymous")
    c.setCreator("anonymous")
    c.setSubject("Controller accuracy and transition-authorization component audit")
    text(c, 5, height - 12, "v3 component audit: exact target accuracy (%)", 7.2, True)

    labels = ["Generic", "+ mode", "+ validity gate", "Untyped plan", "Rule v2*", "Exact CTA", "Lifecycle free", "Lifecycle gate"]
    qwen = [64.4, 75.0, 65.0, 81.2, 92.5, 95.0, 96.9, 98.1]
    glm = [71.9, 75.0, 73.1, 70.6, 92.5, 96.2, 98.1, 100.0]
    chart_x, chart_w = 78, width - 86
    top_y, row_gap = height - 31, 16
    for value in (50, 75, 100):
        xx = chart_x + chart_w * (value - 50) / 50
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(xx, 30, xx, top_y + 4)
        centered(c, xx, 20, str(value), 5.3, False, MUTED)

    for index, label in enumerate(labels):
        yy = top_y - index * row_gap
        text(c, 5, yy - 2, label, 5.5, index >= 5, MUTED)
        qx = chart_x + chart_w * (qwen[index] - 50) / 50
        gx = chart_x + chart_w * (glm[index] - 50) / 50
        c.setStrokeColor(LINE)
        c.setLineWidth(1.0)
        c.line(qx, yy, gx, yy)
        c.setFillColor(ACCENT)
        c.circle(qx, yy, 2.5, fill=1, stroke=0)
        centered(c, qx, yy + 5, f"{qwen[index]:.1f}", 4.8, True, ACCENT)
        c.setFillColor(LIFECYCLE)
        c.circle(gx, yy, 2.5, fill=1, stroke=0)
        centered(c, gx, yy - 8, f"{glm[index]:.1f}", 4.8, True, LIFECYCLE)

    c.setFillColor(ACCENT)
    c.circle(8, 8, 2.5, fill=1, stroke=0)
    text(c, 14, 6, "Qwen3.5-122B", 5.2, False, MUTED)
    c.setFillColor(LIFECYCLE)
    c.circle(82, 8, 2.5, fill=1, stroke=0)
    text(c, 88, 6, "GLM-5.1", 5.2, False, MUTED)
    text(c, 145, 6, "* post-hoc rule", 5.2, True, ACCENT)
    c.showPage()
    c.save()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="reports/figures")
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    draw_mechanism(outdir / "tri_v3_mechanism.pdf")
    draw_results(outdir / "tri_v3_results.pdf")
    print(outdir / "tri_v3_mechanism.pdf")
    print(outdir / "tri_v3_results.pdf")


if __name__ == "__main__":
    main()
