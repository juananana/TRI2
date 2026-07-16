from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas


def load_rows(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    return [r for r in rows if r.get("status") == "ok"]


def short_model(name: str) -> str:
    if "GLM" in name:
        return "GLM-5.1"
    if "Qwen" in name:
        return "Qwen3.5"
    if "MiniMax" in name:
        return "MiniMax"
    return name.split("/")[-1]


def draw_text_box(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    lines: list[str],
    fill: colors.Color,
) -> None:
    c.setStrokeColor(colors.HexColor("#222222"))
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, 7, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#111111"))
    c.setFont("Helvetica", 9)
    total = 10 * len(lines)
    yy = y + h / 2 + total / 2 - 8
    for line in lines:
        c.drawCentredString(x + w / 2, yy, line)
        yy -= 10


def arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, color: str = "#333333") -> None:
    c.setStrokeColor(colors.HexColor(color))
    c.setFillColor(colors.HexColor(color))
    c.setLineWidth(1.1)
    c.line(x1, y1, x2, y2)
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 >= x1 else -1
        c.line(x2, y2, x2 - 5 * direction, y2 + 3)
        c.line(x2, y2, x2 - 5 * direction, y2 - 3)
    else:
        direction = 1 if y2 >= y1 else -1
        c.line(x2, y2, x2 - 3, y2 - 5 * direction)
        c.line(x2, y2, x2 + 3, y2 - 5 * direction)


def mechanism_flow(out: Path) -> None:
    width, height = 7.1 * inch, 2.6 * inch
    c = canvas.Canvas(str(out), pagesize=(width, height))
    c.setTitle("TRI mechanism flow")

    top_fill = colors.HexColor("#f7f7f2")
    bottom_fill = colors.HexColor("#edf4f7")
    box_w, box_h = 122, 52
    y_top, y_bottom = 116, 28
    xs = [22, 194, 372]

    draw_text_box(c, xs[0], y_top, box_w, box_h, ["Initial observation s0", "INC-104 severity 9"], top_fill)
    draw_text_box(c, xs[1], y_top, box_w, box_h, ["Refresh gives s1", "INC-205 severity 10"], top_fill)
    draw_text_box(c, xs[2], y_top, box_w, box_h, ["Latest-state controller", "acts on INC-205"], top_fill)
    draw_text_box(c, xs[0], y_bottom, box_w, box_h, ["Anchored instruction", '"that same incident"'], bottom_fill)
    draw_text_box(c, xs[1], y_bottom, box_w, box_h, ["Referent ledger", "time=pre, id=INC-104"], bottom_fill)
    draw_text_box(c, xs[2], y_bottom, box_w, box_h, ["Ledger controller", "acts on bound ID"], bottom_fill)

    arrow(c, xs[0] + box_w, y_top + box_h / 2, xs[1], y_top + box_h / 2)
    arrow(c, xs[1] + box_w, y_top + box_h / 2, xs[2], y_top + box_h / 2)
    arrow(c, xs[0] + box_w, y_bottom + box_h / 2, xs[1], y_bottom + box_h / 2)
    arrow(c, xs[1] + box_w, y_bottom + box_h / 2, xs[2], y_bottom + box_h / 2)

    c.setFillColor(colors.HexColor("#b84a62"))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(xs[2] + box_w / 2, 101, "referent drift")
    c.setFillColor(colors.HexColor("#333333"))
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, 96, "persist binding time and entity identity")
    c.showPage()
    c.save()


def lifecycle_accuracy(rows: list[dict], out: Path) -> None:
    groups = defaultdict(lambda: {"n": 0, "correct": 0})
    for row in rows:
        task = row["task"]
        result = row["result"]
        key = (short_model(row["model"]), result["mode"], task["binding"])
        groups[key]["n"] += 1
        groups[key]["correct"] += int(bool(result.get("success")))

    models = ["GLM-5.1", "Qwen3.5", "MiniMax"]
    series = [
        ("state_overwrite_once", "anchored", "overwrite anchored", "#b84a62"),
        ("state_overwrite_once", "dynamic", "overwrite dynamic", "#d68f45"),
        ("compile_then_act", "anchored", "compile anchored", "#3e7cb1"),
        ("compile_then_act", "dynamic", "compile dynamic", "#4f9d69"),
    ]

    width, height = 7.1 * inch, 3.65 * inch
    c = canvas.Canvas(str(out), pagesize=(width, height))
    c.setTitle("Lifecycle accuracy")
    left, bottom = 52, 42
    chart_w, chart_h = width - 84, height - 142

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#111111"))
    c.drawString(left, height - 24, "Lifecycle stress test: latest-state drift and ledger repair")

    c.setStrokeColor(colors.HexColor("#dddddd"))
    c.setLineWidth(0.5)
    c.setFont("Helvetica", 9)
    for tick in range(0, 101, 25):
        y = bottom + chart_h * tick / 100
        c.line(left, y, left + chart_w, y)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawRightString(left - 6, y - 2, str(tick))
    c.setFillColor(colors.HexColor("#111111"))
    c.setFont("Helvetica", 8)
    c.setFont("Helvetica", 9)
    c.drawString(left - 28, bottom + chart_h + 9, "Accuracy (%)")

    group_w = chart_w / len(models)
    bar_w = 17
    offsets = [-31, -10, 11, 32]
    for i, model in enumerate(models):
        cx = left + group_w * i + group_w / 2
        c.setFillColor(colors.HexColor("#111111"))
        c.setFont("Helvetica", 9)
        c.drawCentredString(cx, bottom - 16, model)
        for offset, (mode, binding, _label, color) in zip(offsets, series):
            stats = groups[(model, mode, binding)]
            pct = 100 * stats["correct"] / stats["n"] if stats["n"] else 0
            h = chart_h * pct / 100
            x = cx + offset - bar_w / 2
            c.setFillColor(colors.HexColor(color))
            c.rect(x, bottom, bar_w, h, stroke=0, fill=1)
            c.setFont("Helvetica", 9)
            if pct > 0:
                c.setFillColor(colors.white)
                c.drawCentredString(x + bar_w / 2, bottom + h - 11, f"{pct:.0f}")
            else:
                c.setFillColor(colors.HexColor("#111111"))
                c.drawCentredString(x + bar_w / 2, bottom + 7, "0")

    legend_x = left + 56
    legend_y = height - 48
    c.setFont("Helvetica", 9)
    for j, (_mode, _binding, label, color) in enumerate(series):
        x = legend_x + (j % 2) * 150
        y = legend_y - (j // 2) * 12
        c.setFillColor(colors.HexColor(color))
        c.rect(x, y - 6, 8, 8, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#111111"))
        c.drawString(x + 12, y - 5, label)

    c.showPage()
    c.save()


def lifecycle_accuracy_column(rows: list[dict], out: Path) -> None:
    groups = defaultdict(lambda: {"n": 0, "correct": 0})
    for row in rows:
        task = row["task"]
        result = row["result"]
        key = (short_model(row["model"]), result["mode"], task["binding"])
        groups[key]["n"] += 1
        groups[key]["correct"] += int(bool(result.get("success")))

    models = ["GLM-5.1", "Qwen3.5", "MiniMax"]
    series = [
        ("state_overwrite_once", "anchored", "overwrite A", "#b84a62"),
        ("state_overwrite_once", "dynamic", "overwrite D", "#d68f45"),
        ("compile_then_act", "anchored", "compile A", "#3e7cb1"),
        ("compile_then_act", "dynamic", "compile D", "#4f9d69"),
    ]

    width, height = 3.35 * inch, 2.35 * inch
    c = canvas.Canvas(str(out), pagesize=(width, height))
    c.setTitle("Lifecycle accuracy column")
    left, bottom = 30, 30
    chart_w, chart_h = width - 44, height - 86

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#111111"))
    c.drawString(left, height - 16, "Lifecycle stress accuracy")

    c.setStrokeColor(colors.HexColor("#dddddd"))
    c.setLineWidth(0.45)
    c.setFont("Helvetica", 7)
    for tick in range(0, 101, 25):
        y = bottom + chart_h * tick / 100
        c.line(left, y, left + chart_w, y)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawRightString(left - 4, y - 2, str(tick))
    c.setFillColor(colors.HexColor("#111111"))
    c.drawString(left - 8, bottom + chart_h + 5, "Acc. (%)")

    group_w = chart_w / len(models)
    bar_w = 7.5
    offsets = [-12, -4, 4, 12]
    for i, model in enumerate(models):
        cx = left + group_w * i + group_w / 2
        c.setFillColor(colors.HexColor("#111111"))
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx, bottom - 12, model)
        for offset, (mode, binding, _label, color) in zip(offsets, series):
            stats = groups[(model, mode, binding)]
            pct = 100 * stats["correct"] / stats["n"] if stats["n"] else 0
            h = chart_h * pct / 100
            x = cx + offset - bar_w / 2
            c.setFillColor(colors.HexColor(color))
            c.rect(x, bottom, bar_w, h, stroke=0, fill=1)
            c.setFillColor(colors.HexColor("#111111"))
            c.setFont("Helvetica-Bold", 6.2)
            label_y = bottom + h + 2 if pct > 0 else bottom + 4
            label_y = min(label_y, bottom + chart_h - 7)
            c.drawCentredString(x + bar_w / 2, label_y, f"{pct:.0f}")

    legend_x = left
    legend_y = height - 32
    c.setFont("Helvetica", 6.8)
    for j, (_mode, _binding, label, color) in enumerate(series):
        x = legend_x + (j % 2) * 76
        y = legend_y - (j // 2) * 9
        c.setFillColor(colors.HexColor(color))
        c.rect(x, y - 5, 5, 5, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#111111"))
        c.drawString(x + 7, y - 5, label)

    c.showPage()
    c.save()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rows = load_rows([Path(p) for p in args.runs])
    lifecycle_accuracy(rows, outdir / "lifecycle_accuracy.pdf")
    lifecycle_accuracy_column(rows, outdir / "lifecycle_accuracy_column.pdf")
    mechanism_flow(outdir / "tri_mechanism_flow.pdf")
    print(outdir / "lifecycle_accuracy.pdf")
    print(outdir / "lifecycle_accuracy_column.pdf")
    print(outdir / "tri_mechanism_flow.pdf")


if __name__ == "__main__":
    main()
