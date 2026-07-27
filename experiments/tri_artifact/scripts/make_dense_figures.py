#!/usr/bin/env python3
"""Create dense, source-derived TRI result figures for the AAAI draft."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[0]
sys.path.insert(0, str(SCRIPT_DIR))

import make_results_dashboard_figure as dash  # noqa: E402


INK = dash.INK
MUTED = dash.MUTED
LINE = dash.LINE
QWEN = dash.QWEN
GLM = dash.GLM
DEEPSEEK = dash.DEEPSEEK
GREEN = dash.GREEN
RED = dash.RED
GRAY = dash.GRAY
PALE_GREEN = dash.PALE_GREEN
PALE_RED = dash.PALE_RED
PALE_BLUE = dash.PALE_BLUE
PALE_GRAY = dash.PALE_GRAY


def pct(num: float, den: float) -> float:
    return 100.0 * num / den if den else 0.0


def text(c: canvas.Canvas, x: float, y: float, s: str, size: float = 7.2, bold: bool = False, color=INK) -> None:
    dash.text(c, x, y, s, size, bold, color)


def centered(c: canvas.Canvas, x: float, y: float, s: str, size: float = 7.2, bold: bool = False, color=INK) -> None:
    dash.centered(c, x, y, s, size, bold, color)


def right(c: canvas.Canvas, x: float, y: float, s: str, size: float = 7.2, bold: bool = False, color=INK) -> None:
    dash.right(c, x, y, s, size, bold, color)


def box(c: canvas.Canvas, x: float, y: float, w: float, h: float, fill=colors.white, stroke=LINE, radius: float = 3) -> None:
    dash.box(c, x, y, w, h, fill, stroke, radius)


def load_json(name: str) -> dict:
    return dash.load_json(name)


def panel_label(c: canvas.Canvas, x: float, y: float, label: str) -> None:
    c.setFillColor(INK)
    c.setFont(dash.FONT_BOLD, 10.5)
    c.drawString(x, y, label)


def draw_axes(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    ticks: tuple[int, ...] = (0, 50, 100),
    xmax: float = 100.0,
    label: str | None = None,
) -> None:
    c.setStrokeColor(LINE)
    c.setLineWidth(0.55)
    for tick in ticks:
        xx = x + w * tick / xmax
        c.line(xx, y, xx, y + h)
        centered(c, xx, y - 10, str(tick), 6.7, False, MUTED)
    c.setStrokeColor(INK)
    c.setLineWidth(0.65)
    c.line(x, y, x + w, y)
    c.line(x, y, x, y + h)
    if label:
        centered(c, x + w / 2, y - 22, label, 7.4, True, INK)


def draw_hbar(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    value: float,
    color,
    xmax: float = 100.0,
    label: str | None = None,
) -> None:
    c.setFillColor(colors.HexColor("#F4F6F7"))
    c.setStrokeColor(colors.white)
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.setFillColor(color)
    c.rect(x, y, max(0.0, min(w, w * value / xmax)), h, fill=1, stroke=0)
    if label:
        text(c, x + w + 4, y + 1.5, label, 6.8, True, color)


def model_color(model: str):
    if model.startswith("Qwen"):
        return QWEN
    if model.startswith("GLM"):
        return GLM
    return DEEPSEEK


def v7_runs_by_controller() -> dict[tuple[str, str], dict]:
    data = load_json("v7_identifiability_regimes_v1.json")
    out: dict[tuple[str, str], dict] = {}
    for row in data["runs"]:
        if "-" not in row["controller"]:
            continue
        model, controller = row["controller"].split("-", 1)
        model = "Qwen3.5" if model == "Qwen" else model
        model = "GLM-5.1" if model == "GLM" else model
        out[(model, controller)] = row
    return out


def draw_pairacc_ci_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    panel_label(c, x, y + h - 11, "A")
    text(c, x + 16, y + h - 9, "Changed PairAcc with cluster CI", 8.6, True)
    rows = load_json("v7_shared_eligible_pairacc_v1.json")["models"]
    left, axis_w = x + 76, w - 103
    bottom, axis_h = y + 31, h - 59
    draw_axes(c, left, bottom, axis_w, axis_h, (0, 50, 100), 100, "PairAcc (%)")
    row_gap = axis_h / 3
    for idx, row in enumerate(rows):
        yy = bottom + axis_h - row_gap * (idx + 0.5)
        color = model_color(row["model"])
        text(c, x + 20, yy - 3, row["model"], 7.4, True, color)
        for key, series_color, dy, label in (
            ("generic_pairacc", RED, 4.5, "G"),
            ("cta_pairacc", GREEN, -4.5, "C"),
        ):
            metric = row[key]
            rate = metric["estimate"] * 100
            lo, hi = [v * 100 for v in metric["cluster_bootstrap_ci95"]]
            xlo = left + axis_w * lo / 100
            xhi = left + axis_w * hi / 100
            xp = left + axis_w * rate / 100
            c.setStrokeColor(series_color)
            c.setLineWidth(0.85)
            c.line(xlo, yy + dy, xhi, yy + dy)
            c.line(xlo, yy + dy - 2.2, xlo, yy + dy + 2.2)
            c.line(xhi, yy + dy - 2.2, xhi, yy + dy + 2.2)
            c.setFillColor(series_color)
            c.circle(xp, yy + dy, 2.6, fill=1, stroke=0)
            count_label = f"{label} {metric['both_correct']}/{metric['pairs']}"
            if rate > 70:
                right(c, xp - 5, yy + dy - 2.4, count_label, 6.4, True, series_color)
            else:
                text(c, xp + 5, yy + dy - 2.4, count_label, 6.4, True, series_color)
        delta = row["cta_minus_generic_pairacc"]
        lo, hi = [v * 100 for v in delta["cluster_bootstrap_ci95"]]
        right(c, x + w - 2, yy - 3, f"+{delta['estimate']*100:.1f} [{lo:.1f},{hi:.1f}]", 6.6, True, MUTED)


def draw_substitution_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    panel_label(c, x, y + h - 11, "B")
    text(c, x + 16, y + h - 9, "Shared-eligible substitution", 8.6, True)
    text(c, x + 18, y + h - 22, "gray tick=eligible denominator; CTA substitutions are 0 in all rows", 6.0, False, MUTED)
    rows = load_json("v7_shared_eligible_pairacc_v1.json")["models"]
    left, axis_w = x + 82, w - 117
    top = y + h - 33
    row_h = (h - 53) / 3
    draw_axes(c, left, y + 20, axis_w, h - 56, (0, 40, 80), 80, "count")
    for idx, row in enumerate(rows):
        yy = top - idx * row_h
        model = row["model"]
        elig = row["shared_eligible"]["eligible"]
        gsub = row["shared_eligible"]["generic_substitutions"]
        csub = row["shared_eligible"]["cta_substitutions"]
        text(c, x + 20, yy - 2, model, 7.4, True, model_color(model))
        c.setStrokeColor(GRAY)
        c.setLineWidth(0.8)
        c.line(left, yy + 7, left + axis_w * elig / 80, yy + 7)
        c.line(left + axis_w * elig / 80, yy + 2, left + axis_w * elig / 80, yy + 12)
        draw_hbar(c, left, yy - 4, axis_w, 8.0, gsub, RED, 80)
        c.setStrokeColor(GREEN)
        c.setLineWidth(1.1)
        c.line(left, yy - 15, left + axis_w * max(csub, 0.8) / 80, yy - 15)
        text(c, left + axis_w + 5, yy - 4, f"G {gsub}/{elig}", 6.4, True, RED)


def draw_e2e_write_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    panel_label(c, x, y + h - 11, "C")
    text(c, x + 16, y + h - 9, "E2E accuracy vs wrong writes", 8.6, True)
    runs = v7_runs_by_controller()
    diagnostic = {
        (row["model"], row["controller"]): row
        for row in load_json("main_paper_evidence_audit_v1.json")["v7_diagnostic_table"]
    }
    models = ("Qwen3.5", "GLM-5.1", "DeepSeek")
    left, axis_w = x + 58, w - 88
    top = y + h - 31
    row_h = (h - 55) / 3
    draw_axes(c, left, y + 20, axis_w, h - 55, (0, 50, 100), 100, "E2E (%)")
    for idx, model in enumerate(models):
        yy = top - idx * row_h
        text(c, x + 20, yy - 3, model, 7.4, True, model_color(model))
        for controller, color, dy in (("Generic", RED, 4), ("CTA", GREEN, -8)):
            r = runs[(model, controller)]
            acc = r["regimes"]["aggregate_e2e"]["accuracy"] * 100
            writes = diagnostic[(model, controller)]["all_wrong_writes"]
            draw_hbar(c, left, yy + dy, axis_w, 8, acc, color, 100)
            text(c, left + axis_w + 4, yy + dy + 1, f"{controller[0]} {acc:.1f}; W{writes}", 6.5, True, color)


def draw_call_matched_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    panel_label(c, x, y + h - 11, "D")
    text(c, x + 16, y + h - 9, "Information-matched ablation", 8.6, True)
    rows = load_json("call_matched_authorization_ablation_v2.json")["models"]
    modes = [("history_only", "History"), ("decision_visible", "Visible"), ("decision_enforced", "Enforced")]
    left, right_x = x + 68, x + w - 30
    bottom, top = y + 31, y + h - 36
    xs = [left + i * (right_x - left) / 2 for i in range(3)]
    for tick in (0, 50, 100):
        yy = bottom + (top - bottom) * tick / 100
        c.setStrokeColor(LINE)
        c.setLineWidth(0.55)
        c.line(left, yy, right_x, yy)
        right(c, left - 5, yy - 3, str(tick), 6.7, False, MUTED)
    for sx, (_, label) in zip(xs, modes):
        centered(c, sx, y + 18, label, 6.8, False, MUTED)
    for ridx, row in enumerate(rows):
        color = GLM if row["model"].startswith("Pro/") else QWEN
        label = "GLM" if row["model"].startswith("Pro/") else "Qwen"
        pair_values = [row["metrics"][mode]["changed_pairacc"]["rate"] * 100 for mode, _ in modes]
        sub_values = [row["metrics"][mode]["preserve_conditional_substitution"]["rate"] * 100 for mode, _ in modes]
        for values, width_line in ((pair_values, 1.3), (sub_values, 0.75)):
            c.setStrokeColor(color)
            c.setLineWidth(width_line)
            c.setDash(2, 2) if width_line < 1 else c.setDash()
            prev = None
            for sx, value in zip(xs, values):
                yy = bottom + (top - bottom) * value / 100
                if prev:
                    c.line(prev[0], prev[1], sx, yy)
                c.setFillColor(color)
                c.circle(sx, yy, 2.3 if width_line > 1 else 1.8, fill=1, stroke=0)
                prev = (sx, yy)
            c.setDash()
        text(c, right_x + 5, bottom + (top - bottom) * pair_values[-1] / 100 - 2, label, 6.8, True, color)
    text(c, x + 20, y + 6, "solid=PairAcc; dashed=substitution", 6.4, False, MUTED)


def draw_comprehensive_pairacc_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    panel_label(c, x, y + h - 11, "A")
    text(c, x + 16, y + h - 9, "Changed-winner PairAcc across frozen evidence", 8.6, True)
    v3 = load_json("matched_pair_consistency.json")["results"]
    v7 = load_json("v7_shared_eligible_pairacc_v1.json")["models"]
    rows = []
    for model in ("Qwen3.5", "GLM-5.1"):
        rec = {"label": f"v3 {model.replace('-5.1', '')}", "pairs": 32}
        for controller in ("Generic", "CTA"):
            item = next(r for r in v3 if r["dataset"] == "v3" and r["model"] == model and r["controller"] == controller)
            metric = item["slices"]["changed_winner_core"]
            rec[controller] = (metric["both_correct"], metric["pairs"], metric["pair_accuracy"] * 100)
        rows.append(rec)
    for item in v7:
        model = item["model"]
        rows.append(
            {
                "label": f"v7 {model.replace('-5.1', '')}",
                "pairs": 80,
                "Generic": (
                    item["generic_pairacc"]["both_correct"],
                    item["generic_pairacc"]["pairs"],
                    item["generic_pairacc"]["estimate"] * 100,
                ),
                "CTA": (
                    item["cta_pairacc"]["both_correct"],
                    item["cta_pairacc"]["pairs"],
                    item["cta_pairacc"]["estimate"] * 100,
                ),
            }
        )
    left, axis_w = x + 72, w - 104
    bottom, axis_h = y + 30, h - 60
    draw_axes(c, left, bottom, axis_w, axis_h, (0, 50, 100), 100, "PairAcc (%)")
    row_h = axis_h / len(rows)
    for idx, row in enumerate(rows):
        yy = bottom + axis_h - row_h * (idx + 0.5)
        text(c, x + 18, yy - 3, row["label"], 6.7, True, MUTED)
        for controller, color, dy in (("Generic", RED, 4.0), ("CTA", GREEN, -6.0)):
            count, den, rate = row[controller]
            draw_hbar(c, left, yy + dy, axis_w, 7.0, rate, color, 100)
            text(c, left + axis_w + 5, yy + dy + 1, f"{count}/{den}", 6.2, True, color)


def heat_color(value: float):
    if value >= 85:
        return PALE_GREEN
    if value >= 60:
        return PALE_BLUE
    return PALE_RED


def draw_balance_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    panel_label(c, x, y + h - 11, "B")
    text(c, x + 16, y + h - 9, "One-sided scores expose the failure mode", 8.6, True)
    runs = v7_runs_by_controller()
    models = ("Qwen3.5", "GLM-5.1", "DeepSeek")
    columns = (("G Preserve", "Generic", "preserve_only"), ("G Reeval", "Generic", "reevaluate_only"),
               ("C Preserve", "CTA", "preserve_only"), ("C Reeval", "CTA", "reevaluate_only"),
               ("PairAcc G/C", None, None))
    left = x + 58
    top = y + h - 34
    cell_w = (w - 70) / len(columns)
    cell_h = (h - 62) / 3
    for ci, (label, _, _) in enumerate(columns):
        centered(c, left + ci * cell_w + cell_w / 2, top + 12, label, 6.2, True, MUTED)
    for ri, model in enumerate(models):
        yy = top - (ri + 1) * cell_h
        text(c, x + 18, yy + cell_h / 2 - 3, model, 6.8, True, model_color(model))
        for ci, (_, controller, regime) in enumerate(columns):
            xx = left + ci * cell_w
            if controller:
                value = runs[(model, controller)]["regimes"][regime]["accuracy"] * 100
                label = f"{value:.0f}"
            else:
                g = runs[(model, "Generic")]["changed_pairacc"]
                cta = runs[(model, "CTA")]["changed_pairacc"]
                value = cta["pair_accuracy"] * 100
                label = f"{g['both_correct']}/{g['pairs']} -> {cta['both_correct']}/{cta['pairs']}"
            box(c, xx + 2, yy + 3, cell_w - 4, cell_h - 6, fill=heat_color(value), stroke=colors.white, radius=2)
            centered(c, xx + cell_w / 2, yy + cell_h / 2 - 2, label, 6.5, True, INK)


def draw_regret_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    panel_label(c, x, y + h - 11, "D")
    text(c, x + 16, y + h - 9, "Selection-regime identifiability", 8.6, True)
    text(c, x + 18, y + h - 22, "Five model-family candidate sets; zero means a proxy can select 0 PairAcc.", 6.0, False, MUTED)
    data = load_json("evaluation_selection_regret_v1.json")["rows"]
    regimes = [
        ("Aggregate", "aggregate_e2e"),
        ("Preserve-only", "preserve_only"),
        ("Reeval-only", "reevaluate_only"),
        ("Stable-only", "stable_only"),
    ]
    left, axis_w = x + 82, w - 114
    top = y + h - 43
    row_h = (h - 62) / len(regimes)
    draw_axes(c, left, y + 28, axis_w, h - 65, (0, 50, 100), 100, "worst regret (pp)")
    for idx, (label, key) in enumerate(regimes):
        rows = [r for r in data if r["proxy_regime"] == key]
        zero = sum(bool(r["zero_pairacc_maximizer_exists"]) for r in rows)
        regret = max(r["worst_case_selection_regret"] for r in rows) * 100
        yy = top - idx * row_h
        text(c, x + 18, yy - 3, label, 6.8, True, INK if key == "aggregate_e2e" else MUTED)
        draw_hbar(c, left, yy - 5, axis_w, 9.0, regret, GREEN if key == "aggregate_e2e" else RED, 100)
        text(c, left + axis_w + 5, yy - 3, f"zero {zero}/{len(rows)}", 6.4, True, RED if zero else GREEN)


def draw_policy_slice_panel(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    panel_label(c, x, y + h - 11, "C")
    text(c, x + 16, y + h - 9, "Actionable core vs Reject-policy slice", 8.6, True)
    text(c, x + 18, y + h - 22, "green=actionable (n=128); orange=author-specified Reject (n=32)", 5.8, False, MUTED)
    runs = load_json("v3_referential_policy_slices.json")["runs"]
    rows = (
        ("Qwen G", "Qwen Generic", QWEN),
        ("Qwen CTA", "Qwen Historical CTA", QWEN),
        ("GLM G", "GLM Generic", GLM),
        ("GLM CTA", "GLM Historical CTA", GLM),
    )
    left, axis_w = x + 69, w - 101
    bottom, axis_h = y + 31, h - 67
    draw_axes(c, left, bottom, axis_w, axis_h, (0, 50, 100), 100, "accuracy (%)")
    row_h = axis_h / len(rows)
    for index, (label, key, model_tint) in enumerate(rows):
        yy = bottom + axis_h - row_h * (index + 0.5)
        text(c, x + 18, yy - 3, label, 6.5, True, model_tint)
        actionable = runs[key]["actionable_referential_core"]
        reject = runs[key]["author_specified_reject_policy"]
        draw_hbar(c, left, yy + 3, axis_w, 6.5, actionable["accuracy"] * 100, GREEN, 100)
        draw_hbar(c, left, yy - 6, axis_w, 6.5, reject["accuracy"] * 100, RED, 100)
        text(c, left + axis_w + 4, yy + 1, f"{actionable['correct']}/{actionable['n']}", 5.8, True, GREEN)
        text(c, left + axis_w + 4, yy - 8, f"{reject['correct']}/{reject['n']}", 5.8, True, RED)


def draw_comprehensive_results(path: Path) -> None:
    width, height = 7.0 * inch, 4.75 * inch
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("TRI comprehensive dense result figure")
    c.setAuthor("anonymous")
    c.setCreator("anonymous")
    c.setSubject("Source-derived comprehensive TRI result dashboard")
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    margin, gap = 9, 13
    panel_w = (width - 2 * margin - gap) / 2
    panel_h = (height - 2 * margin - gap) / 2
    draw_comprehensive_pairacc_panel(c, margin, margin + panel_h + gap, panel_w, panel_h)
    draw_balance_panel(c, margin + panel_w + gap, margin + panel_h + gap, panel_w, panel_h)
    draw_policy_slice_panel(c, margin, margin, panel_w, panel_h)
    draw_regret_panel(c, margin + panel_w + gap, margin, panel_w, panel_h)
    c.showPage()
    c.save()


def draw_schema_transfer(path: Path) -> None:
    width, height = 7.0 * inch, 3.55 * inch
    c = canvas.Canvas(str(path), pagesize=(width, height), pageCompression=1)
    c.setTitle("TRI schema-transfer dense result figure")
    c.setAuthor("anonymous")
    c.setCreator("anonymous")
    c.setSubject("Source-derived v7 schema-transfer, write, and matched-ablation evidence")
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    margin, gap = 9, 12
    panel_w = (width - 2 * margin - gap) / 2
    panel_h = (height - 2 * margin - gap) / 2
    draw_pairacc_ci_panel(c, margin, margin + panel_h + gap, panel_w, panel_h)
    draw_substitution_panel(c, margin + panel_w + gap, margin + panel_h + gap, panel_w, panel_h)
    draw_e2e_write_panel(c, margin, margin, panel_w, panel_h)
    draw_call_matched_panel(c, margin + panel_w + gap, margin, panel_w, panel_h)
    c.showPage()
    c.save()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "reports/matched_pair_consistency.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/figures")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    comprehensive_path = args.output_dir / "tri_comprehensive_results.pdf"
    schema_path = args.output_dir / "tri_schema_transfer_dense.pdf"
    draw_comprehensive_results(comprehensive_path)
    draw_schema_transfer(schema_path)
    print(f"Created: {comprehensive_path}")
    print(f"Created: {schema_path}")


if __name__ == "__main__":
    main()
