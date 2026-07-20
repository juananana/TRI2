#!/usr/bin/env python3
"""Draw a unified three-color figure suite for the TRI paper."""

from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


# Three warm semantic colors. Light neutrals are layout-only.
INK = colors.HexColor("#4B5548")
TEAL = colors.HexColor("#6F9272")
CORAL = colors.HexColor("#C77A5C")
MUTED = colors.HexColor("#74786F")
LINE = colors.HexColor("#D8D1C8")
PALE_GRAY = colors.HexColor("#F5F2ED")
PALE_TEAL = colors.HexColor("#EDF3EB")
PALE_CORAL = colors.HexColor("#F8EEE8")

ANNOTATION_FONT = "Helvetica-Oblique"


def text(c, x, y, value, size=7.0, bold=False, color=INK):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, value)


def centered(c, x, y, value, size=7.0, bold=False, color=INK):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawCentredString(x, y, value)


def hand_text(c, x, y, value, size=7.0, color=INK):
    c.setFillColor(color)
    c.setFont(ANNOTATION_FONT, size)
    c.drawString(x, y, value)


def hand_centered(c, x, y, value, size=7.0, color=INK):
    c.setFillColor(color)
    c.setFont(ANNOTATION_FONT, size)
    c.drawCentredString(x, y, value)


def fit_centered(c, x, y, value, max_width, size=7.0, bold=False, color=INK):
    font = "Helvetica-Bold" if bold else "Helvetica"
    while size > 5.0 and stringWidth(value, font, size) > max_width:
        size -= 0.2
    centered(c, x, y, value, size, bold, color)


def box(c, x, y, w, h, fill=colors.white, stroke=LINE, radius=3, line_width=0.8):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(line_width)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def arrow(c, x1, y1, x2, y2, color=MUTED, line_width=0.9):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(line_width)
    c.line(x1, y1, x2, y2)
    if abs(x2 - x1) >= abs(y2 - y1):
        sign = 1 if x2 >= x1 else -1
        c.line(x2, y2, x2 - sign * 4, y2 + 2.4)
        c.line(x2, y2, x2 - sign * 4, y2 - 2.4)
    else:
        sign = 1 if y2 >= y1 else -1
        c.line(x2, y2, x2 + 2.4, y2 - sign * 4)
        c.line(x2, y2, x2 - 2.4, y2 - sign * 4)


def white_background(c, width, height):
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.white)
    c.rect(0, 0, width, height, fill=1, stroke=0)


def entity(c, x, y, label, color=INK, fill=colors.white, radius=10, line_width=1.2):
    c.setFillColor(fill)
    c.setStrokeColor(color)
    c.setLineWidth(line_width)
    c.circle(x, y, radius, fill=1, stroke=1)
    centered(c, x, y - 3, label, 7.2, True, color)


def email_token(c, x, y, label, color, fill=colors.white, scale=1.0):
    w, h = 29 * scale, 20 * scale
    left, bottom = x - w / 2, y - h / 2
    c.setFillColor(fill)
    c.setStrokeColor(color)
    c.setLineWidth(1.1)
    c.roundRect(left, bottom, w, h, 2.5 * scale, fill=1, stroke=1)
    c.setLineWidth(0.8)
    c.line(left + 3, bottom + h - 4, x, bottom + h / 2)
    c.line(left + w - 3, bottom + h - 4, x, bottom + h / 2)
    c.setFillColor(colors.white)
    c.setStrokeColor(color)
    c.circle(left + w - 2, bottom + 2, 6 * scale, fill=1, stroke=1)
    centered(c, left + w - 2, bottom - 0.5, label, 5.8 * scale, True, color)


def curved_arrow(c, points, color=INK, line_width=1.4, dashed=False):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(line_width)
    c.setDash(4, 3) if dashed else c.setDash()
    path = c.beginPath()
    path.moveTo(points[0][0], points[0][1])
    for index in range(1, len(points), 3):
        path.curveTo(
            points[index][0], points[index][1],
            points[index + 1][0], points[index + 1][1],
            points[index + 2][0], points[index + 2][1],
        )
    c.drawPath(path, fill=0, stroke=1)
    c.setDash()
    x, y = points[-1]
    c.line(x, y, x - 5, y + 3)
    c.line(x, y, x - 5, y - 3)


def refresh_symbol(c, x, y, radius=15):
    c.setStrokeColor(MUTED)
    c.setFillColor(MUTED)
    c.setLineWidth(1.2)
    c.arc(x - radius, y - radius, x + radius, y + radius, 35, 145)
    c.arc(x - radius, y - radius, x + radius, y + radius, 215, 145)
    c.line(x - radius + 1, y + 4, x - radius - 3, y + 8)
    c.line(x - radius + 1, y + 4, x - radius + 4, y + 9)
    c.line(x + radius - 1, y - 4, x + radius + 3, y - 8)
    c.line(x + radius - 1, y - 4, x + radius - 4, y - 9)


def draw_problem(path: Path) -> None:
    width, height = 7.0 * inch, 2.25 * inch
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("TRI problem: same refresh, different authorization")
    white_background(c, width, height)

    text(c, 8, height - 12, "One refresh, two authorized reference trajectories", 7.6, True)

    # Shared world snapshots: q changes winner from A to B while A remains valid.
    snapshot_y = height - 64
    text(c, 153, snapshot_y + 26, "S0", 6.3, True, MUTED)
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.line(91, snapshot_y - 2, 168, snapshot_y - 2)
    email_token(c, 112, snapshot_y + 9, "A", TEAL, PALE_TEAL, 1.15)
    email_token(c, 151, snapshot_y + 9, "B", INK, colors.white, 1.15)
    text(c, 96, snapshot_y - 20, "q winner", 5.4, True, TEAL)
    c.setFillColor(TEAL)
    p = c.beginPath()
    p.moveTo(112, snapshot_y + 25)
    p.lineTo(107, snapshot_y + 33)
    p.lineTo(117, snapshot_y + 33)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    refresh_symbol(c, width / 2, snapshot_y + 9, 17)
    centered(c, width / 2, snapshot_y - 20, "same REFRESH", 5.8, True, MUTED)
    arrow(c, 178, snapshot_y + 9, width / 2 - 20, snapshot_y + 9, LINE)
    arrow(c, width / 2 + 20, snapshot_y + 9, 324, snapshot_y + 9, LINE)

    text(c, 409, snapshot_y + 26, "S1", 6.3, True, MUTED)
    c.setStrokeColor(LINE)
    c.line(334, snapshot_y - 2, 414, snapshot_y - 2)
    email_token(c, 354, snapshot_y + 9, "A", TEAL, colors.white, 1.15)
    email_token(c, 394, snapshot_y + 9, "B", CORAL, PALE_CORAL, 1.15)
    text(c, 336, snapshot_y - 20, "still valid", 5.4, False, TEAL)
    text(c, 378, snapshot_y - 20, "q winner", 5.4, True, CORAL)
    c.setFillColor(CORAL)
    p = c.beginPath()
    p.moveTo(394, snapshot_y + 25)
    p.lineTo(389, snapshot_y + 33)
    p.lineTo(399, snapshot_y + 33)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    divider_x = width / 2
    c.setStrokeColor(LINE)
    c.setDash(2, 3)
    c.line(divider_x, 25, divider_x, snapshot_y - 26)
    c.setDash()

    # Preserve: an identity thread is anchored before refresh and remains attached to A.
    preserve_y = 50
    text(c, 14, preserve_y + 17, "PRESERVE", 7.0, True, TEAL)
    text(c, 14, preserve_y + 4, '"Choose q now ... act on it."', 5.9, False, MUTED)
    email_token(c, 164, preserve_y + 9, "A", TEAL, PALE_TEAL, 0.9)
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.3)
    c.circle(164, preserve_y + 9, 14, fill=0, stroke=1)
    curved_arrow(
        c,
        [(178, preserve_y + 9), (235, preserve_y + 24), (310, preserve_y - 5), (438, preserve_y + 9)],
        TEAL,
        1.5,
    )
    hand_text(c, 181, preserve_y + 22, "tie identity before refresh", 6.2, TEAL)
    email_token(c, 452, preserve_y + 9, "A", TEAL, PALE_TEAL, 1.0)
    hand_text(c, 470, preserve_y + 4, "act on A", 6.1, MUTED)

    # Reevaluate: no pre-refresh anchor; q runs only after the world update.
    reeval_y = 12
    text(c, 14, reeval_y + 17, "REEVALUATE", 7.0, True, CORAL)
    text(c, 14, reeval_y + 4, '"Refresh first ... then choose q."', 5.9, False, MUTED)
    c.setStrokeColor(CORAL)
    c.setLineWidth(1.2)
    c.setDash(4, 3)
    c.line(159, reeval_y + 9, divider_x - 8, reeval_y + 9)
    c.setDash()
    email_token(c, 344, reeval_y + 9, "B", CORAL, colors.white, 0.9)
    c.setStrokeColor(CORAL)
    c.setLineWidth(1.3)
    c.circle(344, reeval_y + 9, 14, fill=0, stroke=1)
    curved_arrow(
        c,
        [(358, reeval_y + 9), (386, reeval_y + 9), (414, reeval_y + 9), (438, reeval_y + 9)],
        CORAL,
        1.5,
    )
    hand_text(c, 303, reeval_y + 25, "run q after refresh", 6.2, CORAL)
    email_token(c, 452, reeval_y + 9, "B", CORAL, PALE_CORAL, 1.0)
    hand_text(c, 470, reeval_y + 4, "act on B", 6.1, MUTED)
    c.showPage()
    c.save()


def draw_controller(path: Path) -> None:
    width, height = 7.0 * inch, 2.40 * inch
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Lifecycle-Compiled Controller")
    white_background(c, width, height)

    text(c, 8, height - 12, "Lifecycle contract carries authorization across refresh", 7.6, True)

    # Instruction document and the pre-refresh state are compressed into a typed contract.
    doc_x, doc_y = 28, 72
    c.setStrokeColor(INK)
    c.setFillColor(colors.white)
    c.setLineWidth(1.1)
    c.rect(doc_x, doc_y, 36, 47, fill=1, stroke=1)
    c.line(doc_x + 8, doc_y + 34, doc_x + 28, doc_y + 34)
    c.line(doc_x + 8, doc_y + 25, doc_x + 28, doc_y + 25)
    c.line(doc_x + 8, doc_y + 16, doc_x + 23, doc_y + 16)
    centered(c, doc_x + 18, doc_y - 13, "instruction u", 5.7, True)

    email_token(c, 87, doc_y + 32, "A", TEAL, PALE_TEAL, 0.9)
    email_token(c, 87, doc_y + 8, "B", INK, colors.white, 0.78)
    text(c, 103, doc_y + 28, "q winner", 5.3, True, TEAL)
    text(c, 103, doc_y + 8, "mailbox S0", 5.5, True, MUTED)
    text(c, 86, doc_y - 31, "action schema", 5.5, True, MUTED)

    # Funnel/compiler: visual compression rather than a process box.
    c.setStrokeColor(TEAL)
    c.setFillColor(PALE_TEAL)
    c.setLineWidth(1.2)
    funnel = c.beginPath()
    funnel.moveTo(135, doc_y + 46)
    funnel.lineTo(174, doc_y + 46)
    funnel.lineTo(160, doc_y + 27)
    funnel.lineTo(160, doc_y + 13)
    funnel.lineTo(149, doc_y + 13)
    funnel.lineTo(149, doc_y + 27)
    funnel.close()
    c.drawPath(funnel, fill=1, stroke=1)
    centered(c, 154, doc_y - 13, "lifecycle compiler", 5.9, True, TEAL)
    arrow(c, 119, doc_y + 27, 135, doc_y + 27, TEAL)
    arrow(c, 136, doc_y - 27, 149, doc_y + 13, MUTED)

    # The contract is a continuous ribbon that survives the refresh.
    ribbon_y, ribbon_h = 79, 28
    c.setFillColor(PALE_TEAL)
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.2)
    c.rect(174, ribbon_y, 171, ribbon_h, fill=1, stroke=1)
    for x in (215, 254, 302):
        c.line(x, ribbon_y, x, ribbon_y + ribbon_h)
    centered(c, 194.5, ribbon_y + 11, "mode", 5.4, True, TEAL)
    centered(c, 234.5, ribbon_y + 11, "bound ID", 5.4, True, TEAL)
    centered(c, 278, ribbon_y + 11, "selector q", 5.4, True, TEAL)
    centered(c, 323.5, ribbon_y + 11, "invalidity policy", 4.8, True, TEAL)
    centered(c, 259.5, ribbon_y + 36, "reference contract L(r)", 6.1, True, TEAL)

    # Above the ribbon, the world changes from S0 to S1; the contract does not.
    refresh_symbol(c, 258, 132, 16)
    email_token(c, 222, 132, "A", TEAL, colors.white, 0.68)
    email_token(c, 292, 132, "B", CORAL, PALE_CORAL, 0.68)
    curved_arrow(c, [(232, 132), (244, 144), (274, 144), (282, 132)], MUTED, 1.0)
    centered(c, 258, 153, "world refresh: q(S0)=A  ->  q(S1)=B", 5.8, True, MUTED)

    # Mutation gate reads the ribbon and authorizes one of three semantic outcomes.
    gate_x = 355
    c.setStrokeColor(INK)
    c.setLineWidth(2.2)
    c.line(gate_x, 37, gate_x, 132)
    c.line(gate_x + 13, 37, gate_x + 13, 132)
    c.setFillColor(TEAL)
    c.circle(gate_x + 6.5, ribbon_y + ribbon_h / 2, 4, fill=1, stroke=0)
    c.saveState()
    c.translate(gate_x - 7, 45)
    c.rotate(90)
    text(c, 0, 0, "TRI mutation gate", 5.8, True, TEAL)
    c.restoreState()

    outcomes = [
        (121, "A", TEAL, PALE_TEAL, "preserve bound ID"),
        (85, "x", INK, colors.white, "reject invalid target"),
        (49, "B", CORAL, PALE_CORAL, "reevaluate q(S1)"),
    ]
    for oy, label, accent, fill, caption in outcomes:
        arrow(c, gate_x + 13, oy, 406, oy, accent)
        if label == "x":
            entity(c, 418, oy, label, accent, fill, 10)
        else:
            email_token(c, 418, oy, label, accent, fill, 0.9)
        text(c, 433, oy - 2, caption, 5.5, label != "x", accent if label != "x" else MUTED)

    c.showPage()
    c.save()


def draw_bar(c, x, y, w, h, color, solid):
    c.setStrokeColor(color)
    c.setLineWidth(1.0)
    c.setFillColor(color if solid else colors.white)
    c.rect(x, y, w, h, fill=1, stroke=1)


def draw_results_panel(c, x, y, w, h, title, groups, values, panel):
    text(c, x, y + h - 9, f"{panel}  {title}", 7.2, True)
    chart_x, chart_y = x + 22, y + 27
    chart_w, chart_h = w - 29, h - 49
    for value in (0, 50, 100):
        yy = chart_y + chart_h * value / 100
        c.setStrokeColor(LINE)
        c.setLineWidth(0.5)
        c.line(chart_x, yy, chart_x + chart_w, yy)
        text(c, x, yy - 2, str(value), 5.5, False, MUTED)

    group_w = chart_w / len(groups)
    bar_w = min(14, group_w * 0.18)
    styles = [(INK, False), (INK, True), (TEAL, False), (TEAL, True)]
    for gi, group in enumerate(groups):
        center_x = chart_x + group_w * (gi + 0.5)
        for si, (color, solid) in enumerate(styles):
            value = values[gi][si]
            bx = center_x + (si - 1.5) * bar_w * 1.08 - bar_w / 2
            bh = chart_h * value / 100
            draw_bar(c, bx, chart_y, bar_w, bh, color, solid)
            label_y = chart_y + bh + 3 + (6 if si % 2 == 0 else 0)
            fit_centered(c, bx + bar_w / 2, label_y, f"{value:.1f}", bar_w + 8, 5.2, True)
        fit_centered(c, center_x, y + 14, group, group_w - 2, 5.9, False, MUTED)


def draw_results(path: Path) -> None:
    width, height = 7.0 * inch, 2.42 * inch
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("TRI factorial results")
    white_background(c, width, height)
    margin, gap = 7, 8
    panel_w = (width - 2 * margin - 2 * gap) / 3
    draw_results_panel(c, margin, 20, panel_w, height - 22, "Qwen primary", ["160 tasks"], [[64.4, 65.0, 96.9, 98.1]], "A")
    draw_results_panel(c, margin + panel_w + gap, 20, panel_w, height - 22, "GLM primary", ["160 tasks"], [[71.9, 73.1, 98.1, 100.0]], "B")
    draw_results_panel(c, margin + 2 * (panel_w + gap), 20, panel_w, height - 22, "Qwen transfer / write", ["Unseen", "SQLite"], [[46.2, 46.2, 87.5, 82.5], [67.5, 67.5, 100.0, 100.0]], "C")

    legend = [
        (INK, False, "Generic + actor"),
        (INK, True, "Generic + gate"),
        (TEAL, False, "Lifecycle + actor"),
        (TEAL, True, "Lifecycle + gate"),
    ]
    legend_x = 24
    for color, solid, label in legend:
        draw_bar(c, legend_x, 5, 8, 8, color, solid)
        text(c, legend_x + 11, 6, label, 5.7, False, MUTED)
        legend_x += 118
    c.showPage()
    c.save()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("outputs/aaai_submission/figures/unified_style"),
    )
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    draw_problem(args.outdir / "tri_fig1_problem_unified.pdf")
    draw_controller(args.outdir / "tri_fig2_controller_unified.pdf")
    draw_results(args.outdir / "tri_fig3_results_unified.pdf")
    for path in sorted(args.outdir.glob("*.pdf")):
        print(path)


if __name__ == "__main__":
    main()
