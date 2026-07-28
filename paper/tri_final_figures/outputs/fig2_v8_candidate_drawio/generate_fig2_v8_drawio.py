from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET


OUT = Path(__file__).with_name("fig2_tri_diagnostic_workflow_v8_candidate.drawio")

INK = "#264A56"
MUTED = "#66747A"
RULE = "#B8C7C9"
PANEL = "#FBFCFB"
WHITE = "#FFFFFF"
CORAL = "#E56D4E"
CORAL_LIGHT = "#FCEDE8"
TEAL = "#248D82"
TEAL_LIGHT = "#E8F5F2"
AMBER = "#EABC6B"
AMBER_LIGHT = "#FBF2DE"
GREEN = "#60AA84"
GREEN_LIGHT = "#EDF7F1"


def style(*parts: str) -> str:
    return ";".join(part.strip(";") for part in parts if part) + ";"


def text_style(size: int, *, color: str = INK, bold: bool = False,
               align: str = "left", valign: str = "middle", italic: bool = False) -> str:
    return style(
        "text", "html=1", "strokeColor=none", "fillColor=none", "whiteSpace=wrap",
        "overflow=hidden", f"fontFamily=Arial", f"fontSize={size}", f"fontColor={color}",
        f"align={align}", f"verticalAlign={valign}", f"fontStyle={(1 if bold else 0) + (2 if italic else 0)}",
        "spacing=0",
    )


def box_style(fill: str, stroke: str, *, width: int = 2, dashed: bool = False,
              arc: int = 14, align: str = "center", size: int = 24,
              color: str = INK, bold: bool = False) -> str:
    return style(
        "rounded=1", f"arcSize={arc}", "whiteSpace=wrap", "html=1", "overflow=hidden",
        f"fillColor={fill}", f"strokeColor={stroke}", f"strokeWidth={width}",
        "dashed=1" if dashed else "dashed=0", "dashPattern=10 8" if dashed else "",
        f"fontFamily=Arial", f"fontSize={size}", f"fontColor={color}",
        f"align={align}", "verticalAlign=middle", f"fontStyle={1 if bold else 0}",
        "spacing=8",
    )


def ellipse_style(fill: str, stroke: str, *, width: int = 3, size: int = 28,
                  color: str | None = None, bold: bool = True) -> str:
    return style(
        "ellipse", "whiteSpace=wrap", "html=1", "overflow=hidden", f"fillColor={fill}",
        f"strokeColor={stroke}", f"strokeWidth={width}", "fontFamily=Arial",
        f"fontSize={size}", f"fontColor={color or stroke}", f"fontStyle={1 if bold else 0}",
        "align=center", "verticalAlign=middle",
    )


def edge_style(color: str, *, width: int = 4, dashed: bool = False,
               orthogonal: bool = False, label_size: int = 22) -> str:
    return style(
        "edgeStyle=orthogonalEdgeStyle" if orthogonal else "edgeStyle=none",
        "rounded=0", "html=1", "endArrow=classic", "endFill=1", "endSize=12",
        f"strokeColor={color}", f"strokeWidth={width}",
        "dashed=1" if dashed else "dashed=0", "dashPattern=10 8" if dashed else "",
        "fontFamily=Arial", f"fontSize={label_size}", f"fontColor={color}",
        "labelBackgroundColor=#FFFFFF", "align=center", "verticalAlign=middle",
    )


mxfile = ET.Element("mxfile", {
    "host": "app.diagrams.net", "agent": "Codex", "version": "26.0.9", "pages": "1"
})
diagram = ET.SubElement(mxfile, "diagram", {"id": "tri-fig2-v8", "name": "Figure 2 candidate"})
model = ET.SubElement(diagram, "mxGraphModel", {
    "dx": "1800", "dy": "720", "grid": "1", "gridSize": "8", "guides": "1",
    "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
    "pageScale": "1", "pageWidth": "1800", "pageHeight": "720", "math": "0",
    "shadow": "0", "background": WHITE,
})
root = ET.SubElement(model, "root")
ET.SubElement(root, "mxCell", {"id": "0"})
ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})


def vertex(cid: str, value: str, x: int, y: int, w: int, h: int, cell_style: str) -> ET.Element:
    cell = ET.SubElement(root, "mxCell", {
        "id": cid, "value": value, "style": cell_style, "vertex": "1", "parent": "1"
    })
    ET.SubElement(cell, "mxGeometry", {
        "x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"
    })
    return cell


def edge(cid: str, source: str, target: str, cell_style: str, value: str = "") -> ET.Element:
    cell = ET.SubElement(root, "mxCell", {
        "id": cid, "value": value, "style": cell_style, "edge": "1", "parent": "1",
        "source": source, "target": target,
    })
    ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    return cell


# Major panels.
panel_style = style(
    "rounded=1", "arcSize=12", "whiteSpace=wrap", "html=1", "container=1",
    "collapsible=0", "fillColor=none", f"strokeColor={RULE}", "strokeWidth=2", "dashed=0",
    "pointerEvents=0",
)
vertex("panel_a", "", 20, 16, 860, 688, panel_style)
vertex("panel_b", "", 896, 16, 384, 688, panel_style)
vertex("panel_c", "", 1296, 16, 484, 688, panel_style)

# Panel titles.
vertex("a_title", "<b>A. Construct the matched pair</b>", 44, 22, 560, 52,
       text_style(32, bold=True))
vertex("b_title", "<b>B. Run the pair</b>", 920, 22, 340, 52,
       text_style(32, bold=True))
vertex("c_title", "<b>C. Observable readouts</b>", 1320, 22, 446, 52,
       text_style(32, bold=True))

# A: compact specification strip.
spec_value = (
    f"<b><font color='{INK}'>Shared:</font></b> S<sub>0</sub>, S<sub>1</sub>, q, action, schema, interface"
    f"&nbsp;&nbsp; | &nbsp;&nbsp;<b><font color='{CORAL}'>Changed:</font></b> commitment timing"
)
vertex("spec_strip", spec_value, 44, 78, 812, 56,
       box_style(PANEL, RULE, width=2, size=20, color=INK, bold=False))

vertex("transition_label", "<b>SHARED<br>TRANSITION</b>", 48, 158, 146, 72,
       text_style(26, color=MUTED, bold=True))
vertex("state_s0", (
    f"<b>S<sub>0</sub></b><br><font color='{CORAL}'><b>q(S<sub>0</sub>) = A</b></font>"
    "<br><font color='#66747A'>A is initial winner</font>"
), 212, 150, 214, 112, box_style(CORAL_LIGHT, CORAL, width=3, size=25, bold=False))
vertex("refresh_clock", "<b>↻</b>", 458, 176, 58, 58,
       ellipse_style(AMBER_LIGHT, AMBER, width=3, size=32, color=INK))
vertex("state_s1", (
    f"<b>S<sub>1</sub></b><br><font color='{TEAL}'><b>q(S<sub>1</sub>) = B</b></font>"
    f"<br><font color='{GREEN}'><b>A remains present + action-valid</b></font>"
), 548, 150, 282, 112, box_style(TEAL_LIGHT, TEAL, width=3, size=24, bold=False))
edge("refresh_a", "state_s0", "refresh_clock", edge_style(AMBER, width=4), "refresh")
edge("refresh_b", "refresh_clock", "state_s1", edge_style(AMBER, width=4))

# A: Preserve lane.
lane_style_p = style("rounded=1", "arcSize=12", "container=1", "collapsible=0",
                     "fillColor=none", f"strokeColor={CORAL}", "strokeWidth=2", "dashed=0")
lane_style_r = style("rounded=1", "arcSize=12", "container=1", "collapsible=0",
                     "fillColor=none", f"strokeColor={TEAL}", "strokeWidth=2",
                     "dashed=1", "dashPattern=10 8")
vertex("preserve_lane", "", 44, 292, 812, 138, lane_style_p)
vertex("reevaluate_lane", "", 44, 446, 812, 138, lane_style_r)
vertex("preserve_badge", f"<b><font color='{CORAL}'>PRESERVE</font></b><br>bind at S<sub>0</sub>",
       62, 316, 176, 84, box_style(WHITE, CORAL, width=2, size=22, bold=False))
vertex("p_bound_a", "A", 278, 330, 62, 62,
       ellipse_style(CORAL_LIGHT, CORAL, width=3, size=30))
vertex("p_bound_label", "<b>bound(A)</b>",
       246, 394, 126, 28, text_style(18, color=CORAL, bold=True, align="center"))
vertex("p_target_a", "A", 748, 330, 62, 62,
       ellipse_style(WHITE, CORAL, width=3, size=30))
vertex("p_target_label", "<b>target A</b>", 710, 394, 136, 30,
       text_style(22, color=CORAL, bold=True, align="center"))
edge("preserve_path", "p_bound_a", "p_target_a", edge_style(CORAL, width=4),
     "commit before refresh")

# A: Reevaluate lane.
vertex("reevaluate_badge", f"<b><font color='{TEAL}'>REEVALUATE</font></b><br>defer q to S<sub>1</sub>",
       62, 470, 176, 84, box_style(WHITE, TEAL, width=2, dashed=True, size=22))
vertex("r_deferred_q", "q", 278, 484, 62, 62,
       ellipse_style(TEAL_LIGHT, TEAL, width=3, size=30))
vertex("r_deferred_label", "<b>deferred(q)</b>",
       246, 548, 126, 28, text_style(18, color=TEAL, bold=True, align="center"))
vertex("r_target_b", "B", 748, 484, 62, 62,
       ellipse_style(WHITE, TEAL, width=3, size=30))
vertex("r_target_label", "<b>target B</b>", 710, 548, 136, 30,
       text_style(22, color=TEAL, bold=True, align="center"))
edge("reevaluate_path", "r_deferred_q", "r_target_b",
     edge_style(TEAL, width=4, dashed=True), "resolve q on S1")

vertex("a_footer", (
    f"<font color='{CORAL}'><b>solid</b></font> = committed referent&nbsp;&nbsp;&nbsp;"
    f"<font color='{TEAL}'><b>dashed</b></font> = deferred selector&nbsp;&nbsp;&nbsp;"
    f"<font color='{GREEN}'><b>A remains valid in S<sub>1</sub></b></font>"
), 80, 608, 744, 50, box_style(PANEL, RULE, width=1, size=18))

# B: same probe, independent runs.
vertex("same_probe_note", "<b>same probe + interface</b><br>independent runs",
       922, 80, 332, 76, box_style(AMBER_LIGHT, AMBER, width=2, size=21))
vertex("p_instruction", f"<b><font color='{CORAL}'>P</font></b><br>Preserve",
       922, 210, 92, 74, box_style(CORAL_LIGHT, CORAL, width=2, size=21))
vertex("r_instruction", f"<b><font color='{TEAL}'>R</font></b><br>Reevaluate",
       922, 424, 92, 74, box_style(TEAL_LIGHT, TEAL, width=2, dashed=True, size=20))
vertex("controller_probe", "<b>CONTROLLER<br>PROBE</b><br><br><font color='#66747A'>black box</font><br>instruction + history<br>→ target ID",
       1038, 214, 132, 280, box_style(WHITE, INK, width=3, size=28))
vertex("tp_output", "<b>T<sub>P</sub></b><br><font color='#66747A'>output</font>",
       1188, 214, 68, 74, box_style(WHITE, CORAL, width=2, size=20, color=CORAL))
vertex("tr_output", "<b>T<sub>R</sub></b><br><font color='#66747A'>output</font>",
       1188, 424, 68, 74, box_style(WHITE, TEAL, width=2, dashed=True, size=20, color=TEAL))
edge("p_to_probe", "p_instruction", "controller_probe", edge_style(CORAL, width=4, orthogonal=True))
edge("probe_to_tp", "controller_probe", "tp_output", edge_style(CORAL, width=4, orthogonal=True))
edge("r_to_probe", "r_instruction", "controller_probe", edge_style(TEAL, width=4, dashed=True, orthogonal=True))
edge("probe_to_tr", "controller_probe", "tr_output", edge_style(TEAL, width=4, dashed=True, orthogonal=True))
vertex("withheld_note", "<b>Gold mode + targets withheld</b><br><font color='#66747A'>no gold answer enters the probe</font>",
       922, 594, 332, 64, box_style(PANEL, RULE, width=2, dashed=True, size=19))

# C: Readout 1.
readout_style = style("rounded=1", "arcSize=12", "container=1", "collapsible=0",
                      "fillColor=none", f"strokeColor={RULE}", "strokeWidth=2", "dashed=0")
vertex("readout_1", "", 1320, 80, 436, 180, readout_style)
vertex("num_1", "1", 1338, 96, 44, 44, ellipse_style(WHITE, INK, width=2, size=24))
vertex("r1_title", "<b>Pair accuracy (PairAcc)</b>", 1394, 92, 340, 40,
       text_style(25, bold=True))
vertex("r1_unit", "unit: changed pair", 1394, 132, 340, 30,
       text_style(19, color=MUTED))
vertex("r1_formula_p", "<b>T<sub>P</sub> = A</b>", 1382, 174, 126, 48,
       box_style(WHITE, CORAL, width=2, dashed=True, size=24, color=CORAL))
vertex("r1_and", "<b>AND</b>", 1514, 180, 58, 36, text_style(22, bold=True, align="center"))
vertex("r1_formula_r", "<b>T<sub>R</sub> = B</b>", 1578, 174, 126, 48,
       box_style(WHITE, TEAL, width=2, dashed=True, size=24, color=TEAL))
vertex("r1_slice", "denom.: complete pairs", 1394, 224, 340, 30,
       text_style(18, color=MUTED, align="center"))

# C: Readout 2.
vertex("readout_2", "", 1320, 274, 436, 186,
       style(readout_style, f"strokeColor={CORAL}"))
vertex("num_2", "2", 1338, 290, 44, 44, ellipse_style(WHITE, INK, width=2, size=24))
vertex("r2_title", "<b>Conditional substitution</b>", 1394, 286, 340, 40,
       text_style(24, color=CORAL, bold=True))
vertex("r2_focus", "after a correct binding", 1394, 326, 340, 30,
       text_style(18, color=MUTED))
vertex("r2_a", "A", 1398, 364, 50, 50, ellipse_style(CORAL_LIGHT, CORAL, width=2, size=25))
vertex("r2_refresh", "refresh", 1500, 370, 90, 38,
       box_style(AMBER_LIGHT, AMBER, width=2, size=20))
vertex("r2_b", "B", 1642, 364, 50, 50, ellipse_style(TEAL_LIGHT, TEAL, width=2, size=25))
edge("r2_edge_a", "r2_a", "r2_refresh", edge_style(CORAL, width=3))
edge("r2_edge_b", "r2_refresh", "r2_b", edge_style(TEAL, width=3))
vertex("r2_slice", "denom.: strict eligible P rows", 1370, 418, 356, 30,
       text_style(18, color=MUTED, align="center"))

# C: Readout 3.
vertex("readout_3", "", 1320, 474, 436, 208,
       style(readout_style, f"strokeColor={GREEN}"))
vertex("num_3", "3", 1338, 490, 44, 44, ellipse_style(WHITE, INK, width=2, size=24))
vertex("r3_title", "<b>Execution subset</b>", 1394, 486, 334, 40,
       text_style(25, bold=True))
vertex("r3_focus", "ID → write → state diff", 1394, 526, 334, 30,
       text_style(19, color=MUTED))
vertex("r3_id", "<b>ID</b>", 1362, 568, 64, 58,
       style("shape=cylinder3", "boundedLbl=1", "backgroundOutline=1", "whiteSpace=wrap", "html=1",
             f"fillColor={WHITE}", f"strokeColor={GREEN}", "strokeWidth=2", "fontFamily=Arial",
             "fontSize=24", f"fontColor={GREEN}", "fontStyle=1"))
vertex("r3_write", "<b>TOOL<br>WRITE</b>", 1490, 570, 94, 54,
       box_style(WHITE, AMBER, width=2, size=20))
vertex("r3_diff", "<b>STATE<br>DIFF</b>", 1642, 570, 94, 54,
       box_style(WHITE, GREEN, width=2, size=20, color=GREEN))
edge("r3_edge_a", "r3_id", "r3_write", edge_style(AMBER, width=3))
edge("r3_edge_b", "r3_write", "r3_diff", edge_style(GREEN, width=3))
vertex("r3_slice", "denom.: executed writes", 1394, 636, 340, 30,
       text_style(18, color=MUTED, align="center"))


ET.indent(mxfile, space="  ")
OUT.write_text(ET.tostring(mxfile, encoding="unicode", xml_declaration=True), encoding="utf-8")
print(OUT)
