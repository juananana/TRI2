from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas


REP_LABELS = {
    "latest_state": "latest",
    "bound_name_only": "name",
    "bound_id_only": "ID",
    "binding_time_only": "time",
    "time_plus_id": "time+ID",
    "schema_lifecycle": "schema",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def blend(low: str, high: str, t: float) -> colors.Color:
    a = colors.HexColor(low)
    b = colors.HexColor(high)
    t = max(0.0, min(1.0, t))
    return colors.Color(
        a.red + (b.red - a.red) * t,
        a.green + (b.green - a.green) * t,
        a.blue + (b.blue - a.blue) * t,
    )


def draw_center(c: canvas.Canvas, text: str, x: float, y: float, size: float = 7, bold: bool = False) -> None:
    c.setFillColor(colors.HexColor("#111111"))
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawCentredString(x, y, text)


def representation_heatmap(report: dict, out: Path) -> None:
    reps = ["latest_state", "bound_name_only", "bound_id_only", "binding_time_only", "time_plus_id", "schema_lifecycle"]
    cols = [
        ("scalar", "anchored", "scalar A"),
        ("scalar", "dynamic", "scalar D"),
        ("conditional", "conditional", "cond."),
        ("collection", "anchored", "set A"),
        ("collection", "dynamic", "set D"),
        ("nested", "anchored", "nest A"),
        ("nested", "dynamic", "nest D"),
    ]
    lookup = {
        (row["representation"], row["task_type"], row["binding"]): row["accuracy"]
        for row in report["by_type"]
    }

    width, height = 7.1 * inch, 3.15 * inch
    c = canvas.Canvas(str(out), pagesize=(width, height))
    c.setTitle("TRI-v2 representation heatmap")
    left, top = 78, height - 78
    cell_w, cell_h = 52, 24

    c.setFillColor(colors.HexColor("#111111"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(24, height - 24, "TRI-v2 representation sufficiency")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#444444"))
    c.drawString(24, height - 38, "Accuracy by representation and referent lifecycle case")

    for j, (_, _, label) in enumerate(cols):
        draw_center(c, label, left + j * cell_w + cell_w / 2, top + 12, 7, True)
    for i, rep in enumerate(reps):
        y = top - (i + 1) * cell_h
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#111111"))
        c.drawRightString(left - 8, y + 8, REP_LABELS[rep])
        for j, (task_type, binding, _label) in enumerate(cols):
            acc = lookup.get((rep, task_type, binding))
            x = left + j * cell_w
            fill = colors.HexColor("#eeeeee") if acc is None else blend("#f1d1d1", "#4f9d69", acc)
            c.setFillColor(fill)
            c.rect(x, y, cell_w - 2, cell_h - 2, stroke=0, fill=1)
            label = "NA" if acc is None else f"{100 * acc:.0f}"
            draw_center(c, label, x + cell_w / 2 - 1, y + 7, 7, acc == 1.0 if acc is not None else False)

    c.setStrokeColor(colors.HexColor("#dddddd"))
    c.rect(left, top - len(reps) * cell_h, len(cols) * cell_w - 2, len(reps) * cell_h, stroke=1, fill=0)
    c.showPage()
    c.save()


def overall_bars(report: dict, out: Path) -> None:
    rows = sorted(report["overall"], key=lambda r: r["accuracy"])
    width, height = 3.35 * inch, 2.35 * inch
    c = canvas.Canvas(str(out), pagesize=(width, height))
    c.setTitle("TRI-v2 representation overall")
    left, bottom = 70, 28
    chart_w, chart_h = width - 90, height - 62

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#111111"))
    c.drawString(18, height - 18, "TRI-v2 overall accuracy")

    bar_h = chart_h / len(rows) - 4
    for i, row in enumerate(rows):
        y = bottom + i * (bar_h + 4)
        acc = row["accuracy"]
        c.setFillColor(colors.HexColor("#3e7cb1") if row["representation"] != "schema_lifecycle" else colors.HexColor("#4f9d69"))
        c.rect(left, y, chart_w * acc, bar_h, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#111111"))
        c.setFont("Helvetica", 7)
        c.drawRightString(left - 5, y + 4, REP_LABELS[row["representation"]])
        c.drawString(left + chart_w * acc + 3, y + 4, f"{100 * acc:.1f}")

    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.line(left, bottom - 3, left + chart_w, bottom - 3)
    c.showPage()
    c.save()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="reports/v2_ablation.json")
    ap.add_argument("--outdir", default="reports/figures")
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    report = load(Path(args.report))
    representation_heatmap(report, outdir / "v2_representation_heatmap.pdf")
    overall_bars(report, outdir / "v2_overall_bars.pdf")
    print(outdir / "v2_representation_heatmap.pdf")
    print(outdir / "v2_overall_bars.pdf")


if __name__ == "__main__":
    main()
