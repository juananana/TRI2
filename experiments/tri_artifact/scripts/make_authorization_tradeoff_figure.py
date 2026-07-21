from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#5B6570")
LINE = colors.HexColor("#CBD2D9")
IDEAL = colors.HexColor("#E8F3F1")
QWEN = colors.HexColor("#C4572D")
GLM = colors.HexColor("#167D73")
INDEPENDENT = colors.HexColor("#65717C")


def load_points(report_path: Path) -> list[dict[str, Any]]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    keep = {
        "Generic",
        "CTA",
        "Lifecycle-gated",
        "Always-Lock+validity",
        "Always-Reevaluate",
        "Rule v2 (post-hoc)",
    }
    points = []
    for row in report["results"]:
        if row["dataset"] != "v3" or row["controller"] not in keep:
            continue
        core = row["slices"]["changed_winner_core"]
        points.append(
            {
                "model": row["model"],
                "controller": row["controller"],
                "preserve": 100 * core["preserve_accuracy"],
                "reevaluate": 100 * core["reevaluate_accuracy"],
                "pair": 100 * core["pair_accuracy"],
            }
        )
    gated = [point for point in points if point["controller"] == "Lifecycle-gated"]
    if len(gated) == 2 and all(
        gated[0][field] == gated[1][field] for field in ("preserve", "reevaluate", "pair")
    ):
        points = [point for point in points if point["controller"] != "Lifecycle-gated"]
        points.append({**gated[0], "model": "Qwen3.5/GLM-5.1"})
    return points


def draw(path: Path, points: list[dict[str, Any]]) -> None:
    width, height = 4.8 * inch, 3.45 * inch
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Preserve-Reevaluate calibration on matched changed-winner pairs")
    c.setAuthor("anonymous")
    c.setCreator("anonymous")

    left, bottom, right, top = 42, 31, width - 12, height - 27
    chart_w, chart_h = right - left, top - bottom
    axis_min, axis_max = -3, 103

    def sx(value: float) -> float:
        return left + chart_w * (value - axis_min) / (axis_max - axis_min)

    def sy(value: float) -> float:
        return bottom + chart_h * (value - axis_min) / (axis_max - axis_min)

    c.setFillColor(IDEAL)
    c.rect(sx(80), sy(80), sx(103) - sx(80), sy(103) - sy(80), fill=1, stroke=0)
    for tick in range(0, 101, 20):
        x = sx(tick)
        y = sy(tick)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.45)
        c.line(x, bottom, x, top)
        c.line(left, y, right, y)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 6)
        c.drawCentredString(x, bottom - 10, str(tick))
        c.drawRightString(left - 5, y - 2, str(tick))

    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.rect(left, bottom, chart_w, chart_h, fill=0, stroke=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(left + chart_w / 2, 8, "Preserve accuracy (%)")
    c.saveState()
    c.translate(10, bottom + chart_h / 2)
    c.rotate(90)
    c.drawCentredString(0, 0, "Reevaluate accuracy (%)")
    c.restoreState()
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(left, height - 11, "Matched changed-winner calibration (v3)")

    offsets = {
        ("Qwen3.5", "Generic"): (5, -20),
        ("GLM-5.1", "Generic"): (5, 5),
        ("Qwen3.5", "CTA"): (-125, -26),
        ("GLM-5.1", "CTA"): (-125, -6),
        ("Qwen3.5/GLM-5.1", "Lifecycle-gated"): (-80, -43),
        ("model-independent", "Always-Lock+validity"): (-73, 6),
        ("model-independent", "Always-Reevaluate"): (5, -5),
        ("model-independent", "Rule v2 (post-hoc)"): (-18, -62),
    }
    short = {
        "Lifecycle-gated": "Gated",
        "Always-Lock+validity": "Always-Lock",
        "Always-Reevaluate": "Always-Reeval",
        "Rule v2 (post-hoc)": "Rule v2*",
    }
    for point in points:
        x = sx(point["preserve"])
        y = sy(point["reevaluate"])
        color = QWEN if point["model"] == "Qwen3.5" else GLM if point["model"] in {"GLM-5.1", "Qwen3.5/GLM-5.1"} else INDEPENDENT
        c.setFillColor(color)
        if point["model"] == "model-independent":
            c.rect(x - 2.6, y - 2.6, 5.2, 5.2, fill=1, stroke=0)
        else:
            c.circle(x, y, 3, fill=1, stroke=0)
        dx, dy = offsets[(point["model"], point["controller"])]
        model_tag = "Q" if point["model"] == "Qwen3.5" else "G" if point["model"] == "GLM-5.1" else "Q/G " if point["model"] == "Qwen3.5/GLM-5.1" else ""
        label = f"{model_tag}{short.get(point['controller'], point['controller'])} P={point['pair']:.0f}"
        c.setFont("Helvetica", 6.0)
        c.drawString(x + dx, y + dy, label)

    c.setFont("Helvetica", 5.8)
    c.setFillColor(MUTED)
    c.drawRightString(right, height - 11, "P = PairAcc; * post-hoc")
    c.showPage()
    c.save()


def draw_compact(path: Path, points: list[dict[str, Any]]) -> None:
    width, height = 3.35 * inch, 2.62 * inch
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("Compact Preserve-Reevaluate calibration on matched changed-winner pairs")
    c.setAuthor("anonymous")
    c.setCreator("anonymous")

    left, bottom, right, top = 29, 25, width - 7, height - 18
    chart_w, chart_h = right - left, top - bottom
    axis_min, axis_max = -4, 104

    def sx(value: float) -> float:
        return left + chart_w * (value - axis_min) / (axis_max - axis_min)

    def sy(value: float) -> float:
        return bottom + chart_h * (value - axis_min) / (axis_max - axis_min)

    c.setFillColor(IDEAL)
    c.rect(sx(80), sy(80), sx(104) - sx(80), sy(104) - sy(80), fill=1, stroke=0)
    for tick in (0, 50, 100):
        x, y = sx(tick), sy(tick)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.45)
        c.line(x, bottom, x, top)
        c.line(left, y, right, y)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 5.2)
        c.drawCentredString(x, bottom - 9, str(tick))
        c.drawRightString(left - 4, y - 2, str(tick))

    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.rect(left, bottom, chart_w, chart_h, fill=0, stroke=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 6.2)
    c.drawString(left, height - 10, "Changed-winner calibration (v3)")
    c.setFont("Helvetica", 5.0)
    c.setFillColor(MUTED)
    c.drawRightString(right, height - 10, "label number = PairAcc; * post-hoc")
    c.setFont("Helvetica-Bold", 5.6)
    c.setFillColor(INK)
    c.drawCentredString(left + chart_w / 2, 7, "Preserve accuracy (%)")
    c.saveState()
    c.translate(8, bottom + chart_h / 2)
    c.rotate(90)
    c.drawCentredString(0, 0, "Reevaluate accuracy (%)")
    c.restoreState()

    labels = {
        ("Qwen3.5", "Generic"): ("Q-Gen", 4, -15),
        ("GLM-5.1", "Generic"): ("G-Gen", 4, 4),
        ("Qwen3.5", "CTA"): ("Q-CTA", -52, -9),
        ("GLM-5.1", "CTA"): ("G-CTA", -81, -7),
        ("Qwen3.5/GLM-5.1", "Lifecycle-gated"): ("Q/G-Gate", -59, -21),
        ("model-independent", "Always-Lock+validity"): ("Lock", -43, 4),
        ("model-independent", "Always-Reevaluate"): ("Reeval", 4, -4),
        ("model-independent", "Rule v2 (post-hoc)"): ("Rule*", -34, -34),
    }
    for point in points:
        x, y = sx(point["preserve"]), sy(point["reevaluate"])
        color = QWEN if point["model"] == "Qwen3.5" else GLM if point["model"] in {"GLM-5.1", "Qwen3.5/GLM-5.1"} else INDEPENDENT
        c.setFillColor(color)
        if point["model"] == "model-independent":
            c.rect(x - 2.3, y - 2.3, 4.6, 4.6, fill=1, stroke=0)
        else:
            c.circle(x, y, 2.6, fill=1, stroke=0)
        name, dx, dy = labels[(point["model"], point["controller"])]
        c.setFont("Helvetica", 5.2)
        c.drawString(x + dx, y + dy, f"{name} {point['pair']:.0f}")

    c.showPage()
    c.save()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=ROOT / "reports/matched_pair_consistency.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/figures/tri_authorization_tradeoff.pdf")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    points = load_points(args.report)
    if args.compact:
        draw_compact(args.output, points)
    else:
        draw(args.output, points)
    print(args.output)


if __name__ == "__main__":
    main()
