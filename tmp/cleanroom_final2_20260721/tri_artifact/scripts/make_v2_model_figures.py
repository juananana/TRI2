from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pct_label(x: float) -> str:
    return f"{100 * x:.1f}"


def draw_glm_binding(report: dict, out: Path) -> None:
    rows = [
        row for row in report["by_binding"]
        if row["model"] == "GLM-5.1" and row["mode"] in {"state_overwrite_once", "compile_then_act"}
    ]
    lookup = {(row["mode"], row["binding"]): row["accuracy_all"] for row in rows}
    width, height = 4.2 * inch, 2.65 * inch
    c = canvas.Canvas(str(out), pagesize=(width, height))
    c.setTitle("TRI-v2 GLM binding results")
    c.setFillColor(colors.HexColor("#111111"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(18, height - 20, "GLM-5.1 on TRI-v2 scalar tasks")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(18, height - 33, "Accuracy by controller state and referent binding")

    left, bottom = 50, 42
    chart_w, chart_h = width - 74, height - 86
    c.setStrokeColor(colors.HexColor("#cccccc"))
    for frac in [0.0, 0.5, 1.0]:
        y = bottom + chart_h * frac
        c.line(left, y, left + chart_w, y)
        c.setFillColor(colors.HexColor("#666666"))
        c.setFont("Helvetica", 6.5)
        c.drawRightString(left - 5, y - 2, f"{int(frac * 100)}")

    groups = ["anchored", "dynamic"]
    modes = [("state_overwrite_once", "state"), ("compile_then_act", "compile")]
    colors_by_mode = {
        "state_overwrite_once": colors.HexColor("#7b8da8"),
        "compile_then_act": colors.HexColor("#4f9d69"),
    }
    group_w = chart_w / len(groups)
    bar_w = 28
    for gi, binding in enumerate(groups):
        x0 = left + gi * group_w + group_w / 2
        for mi, (mode, label) in enumerate(modes):
            acc = lookup[(mode, binding)]
            x = x0 + (mi - 0.5) * (bar_w + 8)
            h = chart_h * acc
            c.setFillColor(colors_by_mode[mode])
            c.rect(x, bottom, bar_w, h, stroke=0, fill=1)
            c.setFillColor(colors.HexColor("#111111"))
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(x + bar_w / 2, bottom + h + 4, pct_label(acc))
            c.setFont("Helvetica", 6.5)
            c.drawCentredString(x + bar_w / 2, bottom - 10, label)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(x0, bottom - 23, binding)

    c.showPage()
    c.save()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-report", default="reports/v2_model_report_baseline.json")
    ap.add_argument("--outdir", default="reports/figures")
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    report = load(Path(args.model_report))
    out = outdir / "v2_glm_binding_bars.pdf"
    draw_glm_binding(report, out)
    print(out)


if __name__ == "__main__":
    main()
