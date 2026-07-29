import fs from "node:fs/promises";
import path from "node:path";

const out = process.argv[2] || path.resolve("fig2_tri_diagnostic_workflow_v19_structured.drawio");

const C = {
  ink: "#264A56",
  black: "#0D0D0E",
  text: "#3E4A4E",
  muted: "#708084",
  rule: "#A9B6B8",
  shared: "#407A7F",
  soft: "#F7FAFA",
  wash: "#F1FAFA",
  coral: "#C12A36",
  coralLight: "#F8E8E9",
  teal: "#248D82",
  tealLight: "#DCEFF0",
  amber: "#EABC6B",
  amberLight: "#FFF5DE",
  white: "#FFFFFF",
};

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

const cells = [];

function vertex(id, value, style, x, y, width, height, parent = "1") {
  cells.push(`<mxCell id="${id}" value="${esc(value)}" style="${style}" vertex="1" parent="${parent}"><mxGeometry x="${x}" y="${y}" width="${width}" height="${height}" as="geometry"/></mxCell>`);
}

function edge(id, source, target, color, opts = {}) {
  const dashed = opts.dashed ? "dashed=1;dashPattern=8 6;" : "";
  cells.push(`<mxCell id="${id}" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;endSize=8;strokeColor=${color};strokeWidth=${opts.width ?? 2.8};${dashed}" edge="1" parent="1" source="${source}" target="${target}"><mxGeometry relative="1" as="geometry"/></mxCell>`);
}

const text = (size, color = C.text, bold = false, align = "left", italic = false) =>
  `text;html=1;strokeColor=none;fillColor=none;whiteSpace=wrap;overflow=hidden;fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=${(bold ? 1 : 0) + (italic ? 2 : 0)};align=${align};verticalAlign=middle;spacing=0;`;
const round = (fill, stroke, width = 1.5, dashed = false, size = 18, color = C.text) =>
  `rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=${fill};strokeColor=${stroke};strokeWidth=${width};${dashed ? "dashed=1;dashPattern=8 6;" : ""}fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=1;align=center;verticalAlign=middle;spacing=4;`;
const ellipse = (fill, stroke, width = 1.5, size = 18, color = C.text) =>
  `ellipse;whiteSpace=wrap;html=1;fillColor=${fill};strokeColor=${stroke};strokeWidth=${width};fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=1;align=center;verticalAlign=middle;`;
const port = `text;html=1;strokeColor=none;fillColor=none;fontFamily=Arial;fontSize=18;`;

function phase(letter, title, x, y, width, color) {
  vertex(`phase-${letter}`, letter, ellipse(color, color, 1, 20, C.white), x, y, 32, 32);
  vertex(`phase-${letter}-title`, title, text(28, C.black, true), x + 44, y - 1, width - 44, 44);
}

vertex("divider-ab", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 800, 20, 2, 460);
vertex("divider-bc", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 1075, 20, 2, 460);

phase("A", "Construct the matched pair", 20, 18, 770, C.ink);
phase("B", "Run the pair", 815, 18, 250, C.teal);
phase("C", "Readouts", 1090, 18, 290, C.ink);

vertex("contract", "", `rounded=1;arcSize=8;html=1;fillColor=${C.soft};strokeColor=none;`, 30, 68, 750, 50);
vertex("pair-icon", "⇄", text(18, C.shared, true, "center"), 44, 79, 24, 28);
vertex("fixed-label", "FIXED CONTRACT", text(16, C.shared, true), 75, 78, 142, 30);
vertex("fixed-items", "S0, S1, q, action, schema, I/O", text(16, C.ink, true), 225, 78, 292, 30);
vertex("change-label", "ONLY CHANGE", text(16, C.teal, true), 525, 78, 126, 30);
vertex("change-items", "commit point", text(15, C.teal, true, "center"), 655, 78, 108, 30);

vertex("preserve-rule", "", `rect;html=1;fillColor=${C.coral};strokeColor=none;`, 30, 135, 750, 2);
vertex("preserve-token", "P", ellipse(C.coral, C.coral, 1, 22, C.white), 48, 160, 42, 42);
vertex("preserve-title", "PRESERVE", text(22, C.coral, true), 105, 147, 160, 34);
vertex("preserve-body", "commit at S0", text(20, C.coral, true), 105, 182, 160, 30);
vertex("preserve-port", "", port, 265, 178, 6, 6);
vertex("bind", "bind q to A", round(C.white, C.coral, 1.8, false, 21, C.coral), 300, 151, 170, 58);
vertex("gold-a", "gold: A", round(C.white, C.coral, 1.8, false, 20, C.coral), 680, 154, 82, 52);
edge("preserve-bind", "preserve-port", "bind", C.coral);
edge("bind-gold-a", "bind", "gold-a", C.coral);

vertex("state-rule-top", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 30, 240, 750, 1);
vertex("state-rule-bottom", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 30, 350, 750, 1);
vertex("shared-state-title", "SHARED STATE", text(22, C.shared, true), 48, 258, 160, 30);
vertex("shared-state-note", "same transition", text(18, C.muted, false, "left", true), 48, 290, 160, 28);
vertex("state-s0", "", round(C.white, C.ink, 1.8, false, 18, C.ink), 220, 255, 145, 78);
vertex("state-s0-head", "S0   q(S0)=A", text(15, C.ink, true, "center"), 230, 264, 125, 24);
vertex("state-s0-win", "A wins", text(16, C.coral, true, "center"), 230, 300, 125, 24);
vertex("refresh", "", ellipse(C.amberLight, C.amber, 2, 18, C.ink), 425, 257, 74, 74);
vertex("refresh-icon", "↻", text(20, C.ink, true, "center"), 446, 223, 32, 32);
vertex("refresh-label", "refresh", text(15, C.ink, true, "center"), 408, 332, 108, 24);
vertex("state-s1", "", round(C.white, C.ink, 1.8, false, 17, C.ink), 555, 255, 190, 78);
vertex("state-s1-head", "S1   q(S1)=B", text(15, C.ink, true, "center"), 565, 264, 170, 24);
vertex("state-s1-win", "B wins", text(15, C.teal, true, "center"), 565, 300, 78, 24);
vertex("state-s1-valid", "A valid", text(15, C.coral, true, "center"), 655, 300, 78, 24);
edge("state-s0-refresh", "state-s0", "refresh", C.ink, { width: 2.6 });
edge("refresh-state-s1", "refresh", "state-s1", C.ink, { width: 2.6 });

vertex("reevaluate-token", "R", ellipse(C.teal, C.teal, 1, 22, C.white), 48, 390, 42, 42);
vertex("reevaluate-title", "REEVALUATE", text(22, C.teal, true), 105, 376, 175, 34);
vertex("reevaluate-body", "commit at S1", text(20, C.teal, true), 105, 411, 160, 28);
vertex("reevaluate-port", "", port, 265, 408, 6, 6);
vertex("resolve", "resolve q to B", round(C.white, C.teal, 1.8, true, 21, C.teal), 480, 381, 170, 58);
vertex("gold-b", "gold: B", round(C.white, C.teal, 1.8, true, 20, C.teal), 680, 384, 82, 52);
edge("reevaluate-resolve", "reevaluate-port", "resolve", C.teal, { dashed: true });
edge("resolve-gold-b", "resolve", "gold-b", C.teal, { dashed: true });

vertex("withheld", "GOLD WITHHELD", text(18, C.muted, true, "center"), 825, 78, 230, 30);
vertex("withheld-rule", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 855, 112, 170, 2);
vertex("p-run", "P", ellipse(C.coral, C.coral, 1, 22, C.white), 828, 188, 44, 44);
vertex("r-run", "R", ellipse(C.teal, C.teal, 1, 22, C.white), 828, 298, 44, 44);
vertex("probe", "", round(C.soft, C.ink, 1.8, false, 18, C.ink), 880, 155, 120, 220);
vertex("probe-icon", "AI", ellipse(C.soft, C.ink, 1.5, 13, C.ink), 924, 122, 32, 32);
vertex("probe-title", "SAME PROBE", text(16, C.ink, true, "center"), 890, 214, 100, 28);
vertex("probe-kind", "opaque", text(14, C.muted, false, "center", true), 890, 250, 100, 24);
vertex("probe-p-in", "", port, 868, 207, 6, 6);
vertex("probe-p-out", "", port, 1004, 207, 6, 6);
vertex("probe-r-in", "", port, 868, 317, 6, 6);
vertex("probe-r-out", "", port, 1004, 317, 6, 6);
vertex("tp", "T_P", round(C.coralLight, C.coral, 1.8, false, 17, C.coral), 1014, 188, 55, 44);
vertex("tr", "T_R", round(C.tealLight, C.teal, 1.8, true, 17, C.teal), 1014, 298, 55, 44);
edge("p-run-in", "p-run", "probe-p-in", C.coral);
edge("r-run-in", "r-run", "probe-r-in", C.teal, { dashed: true });
edge("p-run-out", "probe-p-out", "tp", C.coral);
edge("r-run-out", "probe-r-out", "tr", C.teal, { dashed: true });
vertex("probe-note", "same I/O; two independent runs", text(20, C.muted, false, "center", true), 825, 400, 230, 52);

vertex("pairacc-title", "PairAcc", text(24, C.black, true), 1100, 75, 270, 32);
vertex("pairacc-formula", "T_P=A  AND  T_R=B", round(C.soft, C.shared, 1.2, false, 21, C.ink), 1110, 115, 250, 52);
vertex("pairacc-slice", "complete pairs", text(20, C.muted, false, "center"), 1110, 168, 250, 28);
vertex("readout-sep-1", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 1100, 205, 270, 1);

vertex("sub-title", "Conditional substitution", text(20, C.black, true), 1090, 218, 290, 32);
vertex("sub-a", "A", ellipse(C.coral, C.coral, 1, 20, C.white), 1115, 273, 38, 38);
vertex("sub-refresh", "refresh", round(C.amberLight, C.ink, 1.6, false, 15, C.ink), 1178, 266, 100, 52);
vertex("sub-b", "B", ellipse(C.teal, C.teal, 1, 20, C.white), 1300, 273, 38, 38);
edge("sub-a-refresh", "sub-a", "sub-refresh", C.ink, { width: 2.2 });
edge("sub-refresh-b", "sub-refresh", "sub-b", C.ink, { width: 2.2 });
vertex("sub-slice", "eligible Preserve", text(20, C.muted, false, "center"), 1110, 320, 250, 28);
vertex("readout-sep-2", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 1100, 350, 270, 1);

vertex("exec-title", "Execution subset", text(21, C.black, true), 1100, 365, 220, 32);
vertex("exec-icon", "DB", `shape=cylinder3;boundedLbl=1;backgroundOutline=1;whiteSpace=wrap;html=1;fillColor=${C.tealLight};strokeColor=${C.teal};strokeWidth=1.4;fontFamily=Arial;fontSize=9;fontColor=${C.teal};fontStyle=1;align=center;verticalAlign=middle;`, 1330, 368, 24, 24);
vertex("exec-id", "ID", round(C.white, C.ink, 1.6, false, 17, C.ink), 1110, 414, 58, 44);
vertex("exec-write", "write", round(C.soft, C.shared, 1.6, false, 16, C.shared), 1185, 414, 78, 44);
vertex("exec-diff", "state diff", round(C.tealLight, C.teal, 1.6, false, 15, C.teal), 1280, 414, 90, 44);
edge("exec-id-write", "exec-id", "exec-write", C.shared, { width: 2.2 });
edge("exec-write-diff", "exec-write", "exec-diff", C.shared, { width: 2.2 });
vertex("exec-slice", "executed writes", text(20, C.muted, false, "center"), 1110, 460, 250, 28);

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="Codex" version="26.0.9" pages="1">
  <diagram id="tri-fig2-v19" name="TRI Figure 2 v19 structured">
    <mxGraphModel dx="1400" dy="500" grid="1" gridSize="5" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="500" background="#FFFFFF" math="0" shadow="0">
      <root><mxCell id="0"/><mxCell id="1" parent="0"/>${cells.join("")}</root>
    </mxGraphModel>
  </diagram>
</mxfile>`;

await fs.writeFile(out, xml, "utf8");
