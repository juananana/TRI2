#!/usr/bin/env python3
"""Generate an editable Figure 5 execution-storyboard candidate."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "summary_csv" / "sqlite_model_facing_outcomes.csv"
DEFAULT_OUT = ROOT / "outputs" / "figure5_execution_storyboard_v1"

INK = "#264A56"
TEAL = "#407A7F"
LEAF = "#60AA84"
CORAL = "#E56D4E"
AMBER = "#EABC6B"
PLUM = "#8B6F8E"
GRAY = "#D8D4CF"
MUTED = "#5F6B70"
PALE_TEAL = "#EAF2F0"
PALE_GREEN = "#EAF5EF"
PALE_CORAL = "#FBE6DF"
PALE_AMBER = "#FFF5DE"
PALE_PLUM = "#F0EBF1"
PAPER = "#FFFFFF"


def read_frozen() -> dict[str, dict[str, int]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    out: dict[str, dict[str, int]] = {}
    for model in ("Qwen3.5", "GLM-5.1"):
        match = [r for r in rows if r["model"] == model and r["controller"] == "Generic"]
        if len(match) != 1:
            raise ValueError(f"Expected one Generic row for {model}, found {len(match)}")
        r = match[0]
        values = {k: int(r[k]) for k in (
            "tasks", "correct_final_state", "core_tri_write", "fallback_wrong_write",
            "unneeded_reject", "strict_core_writes", "strict_core_opportunities",
            "stable_writes", "stable_opportunities",
        )}
        if values["tasks"] != 40:
            raise ValueError(f"Unexpected task count for {model}")
        if sum(values[k] for k in ("correct_final_state", "core_tri_write", "fallback_wrong_write", "unneeded_reject")) != 40:
            raise ValueError(f"Outcome partition does not sum to 40 for {model}")
        out[model] = values
    return out


def style(*parts: str) -> str:
    return ";".join(parts) + ";"


def build_xml(path: Path, data: dict[str, dict[str, int]]) -> None:
    mxfile = ET.Element("mxfile", {"host": "app.diagrams.net", "agent": "Codex", "version": "26.0.9", "pages": "1"})
    diagram = ET.SubElement(mxfile, "diagram", {"id": "tri-fig5-execution", "name": "Figure 5"})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "820", "dy": "760", "grid": "1", "gridSize": "10", "guides": "1", "tooltips": "1",
        "connect": "1", "arrows": "1", "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": "820", "pageHeight": "650", "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    def vertex(cid: str, value: str, x: int, y: int, w: int, h: int, st: str) -> None:
        cell = ET.SubElement(root, "mxCell", {"id": cid, "value": value, "style": st, "vertex": "1", "parent": "1"})
        ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})

    def edge(cid: str, source: str, target: str, color: str, *, dashed: bool = False, label: str = "", width: float = 2.2, points: list[tuple[int, int]] | None = None) -> None:
        st = style(
            "edgeStyle=orthogonalEdgeStyle", "rounded=1", "orthogonalLoop=1", "jettySize=auto", "html=1",
            "endArrow=classic", "endFill=1", f"strokeColor={color}", f"strokeWidth={width}",
            "fontFamily=Arial", "fontSize=10", f"fontColor={MUTED}", "labelBackgroundColor=#FFFFFF",
            "dashed=1" if dashed else "dashed=0", "dashPattern=6 4" if dashed else "",
        )
        cell = ET.SubElement(root, "mxCell", {"id": cid, "value": label, "style": st, "edge": "1", "parent": "1", "source": source, "target": target})
        geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        if points:
            array = ET.SubElement(geometry, "Array", {"as": "points"})
            for x, y in points:
                ET.SubElement(array, "mxPoint", {"x": str(x), "y": str(y)})

    text = lambda size=12, color=INK, bold=False, align="left": style(
        "text", "html=1", "strokeColor=none", "fillColor=none", "whiteSpace=wrap", "overflow=visible",
        "fontFamily=Arial", f"fontSize={size}", f"fontColor={color}", f"fontStyle={1 if bold else 0}", f"align={align}", "verticalAlign=middle",
    )
    rounded = lambda fill, stroke, size=12, bold=False: style(
        "rounded=1", "arcSize=10", "whiteSpace=wrap", "html=1", f"fillColor={fill}", f"strokeColor={stroke}",
        "strokeWidth=1.5", "fontFamily=Arial", f"fontSize={size}", f"fontColor={INK}", f"fontStyle={1 if bold else 0}", "align=center", "verticalAlign=middle",
    )
    circle = lambda fill, stroke, size=16, color=INK: style(
        "ellipse", "whiteSpace=wrap", "html=1", f"fillColor={fill}", f"strokeColor={stroke}", "strokeWidth=2",
        "fontFamily=Arial", f"fontSize={size}", f"fontColor={color}", "fontStyle=1", "align=center", "verticalAlign=middle",
    )

    # Title and experimental boundary.
    vertex("title", "Executed target consequence", 30, 18, 500, 30, text(18, INK, True))
    vertex("subtitle", "same Generic controller · correct initial ID · old target remains action-valid", 30, 46, 650, 22, text(11, MUTED))
    vertex("step_bind", "1  BIND", 32, 85, 120, 24, text(11, TEAL, True))
    vertex("step_refresh", "2  REFRESH", 218, 85, 120, 24, text(11, PLUM, True))
    vertex("step_issue", "3  MODEL WRITE", 420, 85, 145, 24, text(11, INK, True))
    vertex("step_diff", "4  SQLITE DIFF", 642, 85, 145, 24, text(11, LEAF, True))

    vertex("bind_a", "A", 70, 132, 62, 62, circle(PALE_TEAL, TEAL, 18))
    vertex("bind_label", "correct initial target", 30, 198, 145, 24, text(11, MUTED, False, "center"))
    vertex("refresh", "refresh", 238, 136, 86, 52, rounded(PALE_PLUM, PLUM, 12, True))
    edge("edge_bind_refresh", "bind_a", "refresh", MUTED, width=1.8)

    # Shared branch hub and direct lane labels.
    vertex("branch", "", 360, 152, 8, 8, style("ellipse", "fillColor=#FFFFFF", f"strokeColor={MUTED}", "strokeWidth=1.5"))
    edge("edge_refresh_branch", "refresh", "branch", MUTED, width=1.8)
    vertex("stable_label", "STABLE CONTROL", 520, 118, 150, 22, text(11, LEAF, True))
    vertex("changed_label", "CHANGED WINNER", 520, 230, 160, 22, text(11, CORAL, True))
    vertex("stable_state", "q(S1)=A", 380, 148, 105, 46, rounded(PALE_GREEN, LEAF, 12, True))
    vertex("changed_state", "q(S1)=B", 380, 260, 105, 46, rounded(PALE_CORAL, CORAL, 12, True))
    edge("edge_branch_stable", "branch", "stable_state", LEAF, width=2.6)
    edge("edge_branch_changed", "branch", "changed_state", CORAL, width=2.6, points=[(350, 283)])
    vertex("expected_a", "expected target remains A", 365, 310, 165, 22, text(10, MUTED, False, "center"))

    vertex("stable_write", "write(id=A)", 520, 148, 105, 46, rounded(PALE_GREEN, LEAF, 11, True))
    vertex("changed_write", "write(id=B)", 520, 260, 105, 46, rounded(PALE_CORAL, CORAL, 11, True))
    edge("edge_stable_write", "stable_state", "stable_write", LEAF, width=2.6)
    edge("edge_changed_write", "changed_state", "changed_write", CORAL, width=2.6)

    # Two row-level SQLite miniatures make the executed target observable.
    vertex("stable_db", "SQLITE", 682, 128, 90, 20, text(10, LEAF, True, "center"))
    vertex("stable_row_a", "row A   UPDATED", 658, 158, 128, 28, rounded(PALE_GREEN, LEAF, 10, True))
    vertex("stable_row_b", "row B   unchanged", 658, 194, 128, 26, rounded(PAPER, GRAY, 10, False))
    edge("edge_stable_db", "stable_write", "stable_row_a", LEAF, width=2.6)

    vertex("changed_db", "SQLITE", 682, 240, 90, 20, text(10, CORAL, True, "center"))
    vertex("changed_row_a", "row A   unchanged", 658, 270, 128, 26, rounded(PAPER, GRAY, 10, False))
    vertex("changed_row_b", "row B   UPDATED", 658, 306, 128, 28, rounded(PALE_CORAL, CORAL, 10, True))
    edge("edge_changed_db", "changed_write", "changed_row_b", CORAL, width=2.6)

    # Strict evidence is attached to the executed row, so the reader never leaves the path.
    strict_stable_text = '<b><font style="font-size:14px">0/4</font></b> wrong writes · <font style="font-size:10px">Qwen &amp; GLM · strict</font>'
    strict_changed_text = 'Qwen <b><font style="font-size:15px">8/8</font></b> · GLM <b><font style="font-size:15px">6/8</font></b><br><font style="font-size:10px">strict wrong-target writes</font>'
    vertex("strict_stable", strict_stable_text, 385, 202, 205, 28, rounded(PAPER, LEAF, 10, False) + "dashed=1;dashPattern=4 3;")
    vertex("strict_changed", strict_changed_text, 586, 340, 200, 44, rounded(PAPER, CORAL, 10, False) + "dashed=1;dashPattern=4 3;")

    # Frozen 40-task context is a compact exact-count table, not a second plot.
    vertex("ledger_rule", "", 30, 420, 760, 2, style("shape=line", f"strokeColor={GRAY}", "strokeWidth=1"))
    vertex("ledger_heading", "40-task outcome accounting", 30, 436, 300, 26, text(14, INK, True))
    vertex("ledger_n", "n = 40 per model", 282, 439, 140, 22, text(10, MUTED))
    vertex("header_model", "MODEL", 48, 478, 92, 22, text(10, MUTED, True))
    vertex("header_correct", "CORRECT FINAL", 190, 478, 130, 22, text(10, LEAF, True, "center"))
    vertex("header_tri", "TRI WRITE", 350, 478, 110, 22, text(10, CORAL, True, "center"))
    vertex("header_fallback", "FALLBACK", 490, 478, 110, 22, text(10, PLUM, True, "center"))
    vertex("header_reject", "REJECT", 630, 478, 110, 22, text(10, MUTED, True, "center"))
    vertex("table_rule_header", "", 48, 502, 692, 2, style("shape=line", f"strokeColor={GRAY}", "strokeWidth=1"))
    vertex("qwen_name", "Qwen", 48, 516, 92, 32, text(12, TEAL, True))
    vertex("qwen_correct", "27", 190, 512, 130, 38, text(16, INK, True, "center"))
    vertex("qwen_tri", "8", 350, 512, 110, 38, text(16, CORAL, True, "center"))
    vertex("qwen_fallback", "5", 490, 512, 110, 38, text(16, PLUM, True, "center"))
    vertex("qwen_reject", "0", 630, 512, 110, 38, text(16, MUTED, True, "center"))
    vertex("table_rule_rows", "", 48, 550, 692, 2, style("shape=line", f"strokeColor={GRAY}", "strokeWidth=1"))
    vertex("glm_name", "GLM", 48, 558, 92, 32, text(12, CORAL, True))
    vertex("glm_correct", "26", 190, 554, 130, 38, text(16, INK, True, "center"))
    vertex("glm_tri", "6", 350, 554, 110, 38, text(16, CORAL, True, "center"))
    vertex("glm_fallback", "2", 490, 554, 110, 38, text(16, PLUM, True, "center"))
    vertex("glm_reject", "6", 630, 554, 110, 38, text(16, MUTED, True, "center"))
    vertex("boundary", "Model-issued writes in a controlled SQLite test; not a prevalence estimate.", 30, 614, 760, 20, text(10, MUTED, False, "center"))

    path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    data = read_frozen()
    output = args.output_dir / "figure5_execution_storyboard.drawio"
    build_xml(output, data)
    print(output)


if __name__ == "__main__":
    main()
