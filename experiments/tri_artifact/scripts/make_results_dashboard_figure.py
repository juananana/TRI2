from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
INK = colors.HexColor("#17212B")
MUTED = colors.HexColor("#5B6570")
LINE = colors.HexColor("#CBD2D9")
PALE_GREEN = colors.HexColor("#E8F3F1")
PALE_RED = colors.HexColor("#F8ECE7")
PALE_BLUE = colors.HexColor("#EAF0F7")
PALE_GRAY = colors.HexColor("#F1F3F5")
QWEN = colors.HexColor("#407A7F")
GLM = colors.HexColor("#E56D4E")
DEEPSEEK = colors.HexColor("#60AA84")
GRAY = colors.HexColor("#5F6B70")
GREEN = colors.HexColor("#60AA84")
RED = colors.HexColor("#E56D4E")
FONT_REGULAR = "TRIHelvetica"
FONT_BOLD = "TRIHelvetica-Bold"

pdfmetrics.registerFont(TTFont(FONT_REGULAR, "/System/Library/Fonts/Helvetica.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont(FONT_BOLD, "/System/Library/Fonts/Helvetica.ttc", subfontIndex=1))


def load_json(name: str) -> dict:
    return json.loads((ROOT / "reports" / name).read_text(encoding="utf-8"))


def text(c: canvas.Canvas, x: float, y: float, s: str, size: float = 7.2, bold: bool = False, color=INK) -> None:
    c.setFillColor(color)
    c.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    c.drawString(x, y, s)


def centered(c: canvas.Canvas, x: float, y: float, s: str, size: float = 7.2, bold: bool = False, color=INK) -> None:
    c.setFillColor(color)
    c.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    c.drawCentredString(x, y, s)


def right(c: canvas.Canvas, x: float, y: float, s: str, size: float = 7.2, bold: bool = False, color=INK) -> None:
    c.setFillColor(color)
    c.setFont(FONT_BOLD if bold else FONT_REGULAR, size)
    c.drawRightString(x, y, s)


def box(c: canvas.Canvas, x: float, y: float, w: float, h: float, fill=colors.white, stroke=LINE, radius: float = 3) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.55)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def pct(num: int, den: int) -> float:
    return 100.0 * num / den if den else 0.0


def component_values() -> list[tuple[str, float, float]]:
    q_factor = load_json("v3_factorial_qwen_primary_cluster.json")["runs"]
    g_factor = load_json("v3_factorial_glm_primary_cluster.json")["runs"]
    q_modes = {r["mode"]: 100 * r["task_accuracy"] for r in q_factor}
    g_modes = {r["mode"]: 100 * r["task_accuracy"] for r in g_factor}
    q_ref = 100 * load_json("reference_mode_ablation_qwen.json")["reference_mode"]["accuracy"]
    g_ref = 100 * load_json("reference_mode_ablation_glm.json")["reference_mode"]["accuracy"]
    q_untyped = next(
        100 * r["task_accuracy"]
        for r in load_json("v3_prefrefresh_untyped_primary_report.json")["runs"]
        if r["model"] == "Qwen3.5" and r["mode"] == "pre_refresh_untyped_compile_then_act"
    )
    g_untyped = next(
        100 * r["task_accuracy"]
        for r in load_json("v3_prefrefresh_untyped_primary_report.json")["runs"]
        if r["model"] == "GLM-5.1" and r["mode"] == "pre_refresh_untyped_compile_then_act"
    )
    exact = load_json("v3_exact_predecessor_two_model.json")["runs"]
    q_cta = next(100 * r["itt_accuracy"] for r in exact if r["model"] == "Qwen3.5")
    g_cta = next(100 * r["itt_accuracy"] for r in exact if r["model"] == "GLM-5.1")
    rule = 100 * load_json("deterministic_discourse_rule_v2.json")["datasets"][0]["overall"]["correct"] / 160
    return [
        ("Generic", q_modes["generic_structured_ledger_then_act"], g_modes["generic_structured_ledger_then_act"]),
        ("+ mode field", q_ref, g_ref),
        ("+ validity gate", q_modes["generic_validity_gated_ledger_then_act"], g_modes["generic_validity_gated_ledger_then_act"]),
        ("Untyped plan", q_untyped, g_untyped),
        ("Rule*", rule, rule),
        ("Historical CTA", q_cta, g_cta),
        ("Lifecycle free", q_modes["factorized_schema_compile_then_act"], g_modes["factorized_schema_compile_then_act"]),
        ("Lifecycle gate", q_modes["factorized_hybrid_compile_then_act"], g_modes["factorized_hybrid_compile_then_act"]),
    ]


def draw_calibration(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    points = []
    for row in load_json("matched_pair_consistency.json")["results"]:
        if row["dataset"] != "v3":
            continue
        if row["controller"] not in {"Generic", "CTA", "Lifecycle-gated", "Always-Lock+validity", "Always-Reevaluate", "Rule v2 (post-hoc)"}:
            continue
        core = row["slices"]["changed_winner_core"]
        points.append((row["model"], row["controller"], 100 * core["preserve_accuracy"], 100 * core["reevaluate_accuracy"], 100 * core["pair_accuracy"]))
    # merge identical gated points
    seen = []
    for p in points:
        if p[1] == "Lifecycle-gated" and any(q[1] == "Lifecycle-gated" for q in seen):
            continue
        seen.append(("Q/G" if p[1] == "Lifecycle-gated" else p[0], p[1], p[2], p[3], p[4]))

    text(c, x, y + h - 11, "Changed-winner policy space", 9.4, True)
    left, bottom, right_x, top = x + 33, y + 28, x + w - 7, y + h - 29
    chart_w, chart_h = right_x - left, top - bottom

    axis_min, axis_max = -5.0, 110.0

    def sx(v: float) -> float:
        return left + chart_w * (v - axis_min) / (axis_max - axis_min)

    def sy(v: float) -> float:
        return bottom + chart_h * (v - axis_min) / (axis_max - axis_min)

    for tick in (0, 50, 100):
        c.setStrokeColor(LINE)
        c.setLineWidth(0.55)
        c.line(sx(tick), bottom, sx(tick), top)
        c.line(left, sy(tick), right_x, sy(tick))
        centered(c, sx(tick), bottom - 12, str(tick), 9.0, False, MUTED)
        right(c, left - 5, sy(tick) - 3, str(tick), 9.0, False, MUTED)
    c.setStrokeColor(INK)
    c.setLineWidth(0.65)
    c.rect(left, bottom, chart_w, chart_h, fill=0, stroke=1)
    centered(c, left + chart_w / 2, y + 5, "Preserve accuracy", 9.0, True)
    c.saveState()
    c.translate(x + 9, bottom + chart_h / 2)
    c.rotate(90)
    centered(c, 0, 0, "Reevaluate accuracy", 9.0, True)
    c.restoreState()
    labels = {
        ("Qwen3.5", "Generic"): ("Q-Gen", 4, -31, False),
        ("GLM-5.1", "Generic"): ("G-Gen", 6, -28, False),
        ("Qwen3.5", "CTA"): ("Q-CTA", -55, -18, True),
        ("GLM-5.1", "CTA"): ("G-CTA", -55, -1, True),
        ("Q/G", "Lifecycle-gated"): ("Gated", -25, -38, True),
        ("model-independent", "Always-Lock+validity"): ("Lock", -34, 8, False),
        ("model-independent", "Always-Reevaluate"): ("Reeval", 7, -11, False),
        ("model-independent", "Rule v2 (post-hoc)"): ("Rule*", -45, -30, True),
    }
    for model, controller, preserve, reevaluate, pair in seen:
        color = QWEN if model == "Qwen3.5" else GLM if model in {"GLM-5.1", "Q/G"} else GRAY
        px, py = sx(preserve), sy(reevaluate)
        c.setFillColor(color)
        if model == "model-independent":
            c.setStrokeColor(color)
            c.setLineWidth(0.8)
            c.rect(px - 3, py - 3, 6, 6, fill=0, stroke=1)
        elif model == "Qwen3.5":
            c.circle(px, py, 3.0, fill=1, stroke=0)
        else:
            c.rect(px - 3, py - 3, 6, 6, fill=1, stroke=0)
        label, dx, dy, leader = labels[(model, controller)]
        if leader:
            c.setStrokeColor(color)
            c.setLineWidth(0.55)
            c.line(px, py, px + dx + 4, py + dy + 5)
        text(c, px + dx, py + dy, label, 9.0, False, color)


def draw_components(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    text(c, x, y + h - 9, "Primary component audit", 7.4, True)
    rows = component_values()
    left, right_x = x + 70, x + w - 8
    top = y + h - 25
    row_h = (h - 43) / len(rows)

    def sx(v: float) -> float:
        return left + (right_x - left) * (v - 50) / 50

    for tick in (50, 75, 100):
        c.setStrokeColor(LINE)
        c.setLineWidth(0.45)
        c.line(sx(tick), y + 15, sx(tick), top + 5)
        centered(c, sx(tick), y + 6, str(tick), 6.1, False, MUTED)
    for i, (label, q, g) in enumerate(rows):
        yy = top - i * row_h
        text(c, x + 3, yy - 2, label, 6.2, i >= 5, MUTED if i < 5 else INK)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.65)
        c.line(sx(q), yy, sx(g), yy)
        c.setFillColor(QWEN)
        c.circle(sx(q), yy, 2.3, fill=1, stroke=0)
        c.setFillColor(GLM)
        c.rect(sx(g) - 2.3, yy - 2.3, 4.6, 4.6, fill=1, stroke=0)
    c.setFillColor(QWEN)
    c.circle(x + 4, y + 8, 2.2, fill=1, stroke=0)
    text(c, x + 9, y + 5, "Qwen", 5.8, False, MUTED)
    c.setFillColor(GLM)
    c.rect(x + 40, y + 6, 4.5, 4.5, fill=1, stroke=0)
    text(c, x + 49, y + 5, "GLM", 5.8, False, MUTED)


def draw_replication(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    text(c, x, y + h - 11, "Conditional substitution and all-write audit", 9.4, True)
    shared_rows = load_json("v7_shared_eligible_pairacc_v1.json")["models"]
    diagnostic_rows = load_json("main_paper_evidence_audit_v1.json")["v7_diagnostic_table"]
    core_runs = load_json("v7_core_replication.json")["runs"]
    deepseek_runs = load_json("v7_deepseek_full_v1.json")["runs"]
    diagnostic = {
        (row["model"], row["controller"]): row
        for row in diagnostic_rows
    }
    controller_name = {
        "generic_structured_ledger_then_act": "Generic",
        "compile_then_act": "CTA",
    }
    e2e = {
        (row["model"], controller_name[row["controller"]]): 100 * row["correct"] / row["n"]
        for row in core_runs + deepseek_runs
        if row["controller"] in controller_name
    }
    models = [("Qwen3.5", QWEN), ("GLM-5.1", GLM), ("DeepSeek", DEEPSEEK)]
    shared = {row["model"]: row["shared_eligible"] for row in shared_rows}
    gap = 12
    panel_w = (w - 2 * gap) / 3
    chart_bottom = y + 48
    chart_top = y + h - 39
    stage_labels = (("Both", "bind"), ("Substitute", ""), ("Wrong", "write"))

    def sy(value: float) -> float:
        return chart_bottom + (chart_top - chart_bottom) * value / 80.0

    for index, (model, model_color) in enumerate(models):
        px = x + index * (panel_w + gap)
        left = px + 31
        right_x = px + panel_w - 31
        stage_x = [left + i * (right_x - left) / 2 for i in range(3)]
        centered(c, px + panel_w / 2, y + h - 27, model, 9.2, True, model_color)
        for tick in (0, 40, 80):
            c.setStrokeColor(LINE)
            c.setLineWidth(0.55)
            c.line(left, sy(tick), right_x, sy(tick))
            if index == 0:
                right(c, left - 5, sy(tick) - 3, str(tick), 9.0, False, MUTED)
        for sx, (line_one, line_two) in zip(stage_x, stage_labels):
            centered(c, sx, y + 34, line_one, 9.0, False, MUTED)
            if line_two:
                centered(c, sx, y + 24, line_two, 9.0, False, MUTED)

        item = shared[model]
        eligible = item["eligible"]
        generic_sub = item["generic_substitutions"]
        cta_sub = item["cta_substitutions"]
        series = [
            ("Generic", RED, [eligible, generic_sub, generic_sub], 2.0),
            ("CTA", GREEN, [eligible, cta_sub, cta_sub], 1.4),
        ]
        for label, color, values, line_width in series:
            c.setStrokeColor(color)
            c.setLineWidth(line_width)
            c.setLineCap(1)
            c.line(stage_x[0], sy(values[0]), stage_x[1], sy(values[1]))
            c.line(stage_x[1], sy(values[1]), stage_x[2], sy(values[2]))
            for sx, value in zip(stage_x, values):
                c.setFillColor(color)
                c.circle(sx, sy(value), 3.2 if label == "Generic" else 2.8, fill=1, stroke=0)
            offset = 6 if label == "Generic" else -13
            text(c, stage_x[0] + 4, sy(values[0]) + offset, f"{label} {values[0]}", 9.0, True, color)
            if values[1]:
                centered(c, stage_x[1], sy(values[1]) + 7, str(values[1]), 9.0, True, color)
                centered(c, stage_x[2], sy(values[2]) + 7, str(values[2]), 9.0, True, color)
            else:
                centered(c, stage_x[1], sy(0) + 6, "0", 9.0, True, color)
                centered(c, stage_x[2], sy(0) + 6, "0", 9.0, True, color)

        gen = diagnostic[(model, "Generic")]
        cta = diagnostic[(model, "CTA")]
        generic_other = gen["all_wrong_writes"] - gen["core_substitution_writes"]
        cta_other = cta["all_wrong_writes"] - cta["core_substitution_writes"]
        centered(
            c,
            px + panel_w / 2,
            y + 11,
            f"All 240: E2E G/C {e2e[(model, 'Generic')]:.1f}/{e2e[(model, 'CTA')]:.1f}",
            8.3,
            True,
            MUTED,
        )
        centered(
            c,
            px + panel_w / 2,
            y + 1,
            f"Wrong G/C {gen['all_wrong_writes']}/{cta['all_wrong_writes']} | outside core {generic_other}/{cta_other}",
            7.8,
            False,
            MUTED,
        )


def draw_boundary(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    text(c, x, y + h - 9, "Evidence that narrows the claim", 7.4, True)
    rows = [
        ("Full history", "post-primary", "mixed: reminder helps, still lower than CTA"),
        ("Rule*", "post-hoc", "92.5/96.0/91.7%; novelty limited"),
        ("Human core", "audit", "86% majority-gold; reject weak"),
        ("Public native", "audit", "0 strict opportunities in six suites"),
        ("Source transfer", "frozen", "positive only in one AgentDojo Qwen slice"),
        ("Composition", "stress", "mixed; scalar result does not compose"),
    ]
    top = y + h - 25
    row_h = 16
    for i, (name, status, outcome) in enumerate(rows):
        yy = top - i * row_h
        fill = PALE_RED if status in {"post-hoc", "stress"} else PALE_BLUE if status in {"audit", "frozen"} else PALE_GRAY
        box(c, x + 3, yy - 4, 47, 13, fill=colors.white, stroke=LINE, radius=2)
        text(c, x + 7, yy - 1, name, 5.9, True if name in {"Rule*", "Composition"} else False, INK)
        box(c, x + 54, yy - 4, 43, 13, fill=fill, stroke=LINE, radius=2)
        centered(c, x + 75.5, yy - 1, status, 5.8, False, MUTED)
        text(c, x + 103, yy - 1, outcome, 5.55, False, MUTED)


def draw(path: Path) -> None:
    width, height = 6.85 * inch, 3.18 * inch
    c = canvas.Canvas(
        str(path), pagesize=(width, height), pageCompression=1, initialFontName=FONT_REGULAR
    )
    c.setTitle("TRI diagnostic evidence dashboard")
    c.setAuthor("anonymous")
    c.setCreator("anonymous")
    c.setSubject("Source-derived diagnostic, component, replication, and boundary evidence")
    margin, gap = 8, 10
    half_w = (width - 2 * margin - gap) / 2
    half_h = (height - 2 * margin - gap) / 2
    draw_calibration(c, margin, margin + half_h + gap, half_w, half_h)
    draw_components(c, margin + half_w + gap, margin + half_h + gap, half_w, half_h)
    draw_replication(c, margin, margin, half_w, half_h)
    draw_boundary(c, margin + half_w + gap, margin, half_w, half_h)
    c.showPage()
    c.save()


def draw_split(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        ("tri_changed_winner_calibration.pdf", 3.35 * inch, 2.65 * inch, draw_calibration),
        ("tri_component_audit_dotline.pdf", 3.35 * inch, 2.22 * inch, draw_components),
        ("tri_new_schema_consequence_matrix.pdf", 6.85 * inch, 2.08 * inch, draw_replication),
        ("tri_claim_boundary_matrix.pdf", 3.35 * inch, 2.22 * inch, draw_boundary),
    ]
    for filename, width, height, drawer in specs:
        path = output_dir / filename
        c = canvas.Canvas(
            str(path), pagesize=(width, height), pageCompression=1, initialFontName=FONT_REGULAR
        )
        c.setTitle(filename.replace("_", " ").replace(".pdf", ""))
        c.setAuthor("anonymous")
        c.setCreator("anonymous")
        drawer(c, 7, 5, width - 14, height - 10)
        c.showPage()
        c.save()
        print(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports/figures/tri_results_dashboard.pdf")
    parser.add_argument("--split-dir", type=Path)
    args = parser.parse_args()
    if args.split_dir:
        draw_split(args.split_dir)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        draw(args.output)
        print(args.output)


if __name__ == "__main__":
    main()
