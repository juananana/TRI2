import fs from "node:fs/promises";
import path from "node:path";
import { icons as lucideIcons } from "lucide";

const out = process.argv[2] || path.resolve("fig2_tri_diagnostic_workflow_v16_centered.drawio");
const C = {
  ink: "#0D0D0E", charcoal: "#3C535C", text: "#58585A", muted: "#7D8D91",
  rule: "#AEBABD", teal: "#318383", tealMid: "#7FADB4", tealLight: "#D6EEF0",
  coral: "#B2242F", coralLight: "#F7E8E8", blue: "#6C9FA3", white: "#FFFFFF",
};

function esc(value) {
  return String(value).replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function iconUri(name, color) {
  const body = lucideIcons[name].map(([tag, attrs]) => {
    const serialized = Object.entries(attrs).map(([k, v]) => `${k}="${esc(v)}"`).join(" ");
    return `<${tag} ${serialized}/>`;
  }).join("");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
  return `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;
}

const cells = [];
function vertex(id, value, style, x, y, w, h) {
  cells.push(`<mxCell id="${id}" value="${esc(value)}" style="${style}" vertex="1" parent="1"><mxGeometry x="${x}" y="${y}" width="${w}" height="${h}" as="geometry"/></mxCell>`);
}
function edge(id, source, target, color, dashed = false, curved = false) {
  const style = `${curved ? "curved=1" : "edgeStyle=orthogonalEdgeStyle"};rounded=1;html=1;endArrow=block;endFill=1;endSize=8;strokeColor=${color};strokeWidth=2.6;${dashed ? "dashed=1;dashPattern=8 6;" : ""}`;
  cells.push(`<mxCell id="${id}" value="" style="${style}" edge="1" parent="1" source="${source}" target="${target}"><mxGeometry relative="1" as="geometry"/></mxCell>`);
}

const text = (size, color = C.text, bold = false, align = "left", italic = false) =>
  `text;html=1;strokeColor=none;fillColor=none;whiteSpace=wrap;overflow=hidden;fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=${(bold ? 1 : 0) + (italic ? 2 : 0)};align=${align};verticalAlign=middle;spacing=0;`;
const ellipse = (fill, stroke, sw = 1.5, size = 12, color = C.text) =>
  `ellipse;whiteSpace=wrap;html=1;fillColor=${fill};strokeColor=${stroke};strokeWidth=${sw};fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=1;align=center;verticalAlign=middle;`;
const round = (fill, stroke, sw = 1.3, dashed = false, size = 10, color = C.text) =>
  `rounded=1;arcSize=18;whiteSpace=wrap;html=1;fillColor=${fill};strokeColor=${stroke};strokeWidth=${sw};${dashed ? "dashed=1;dashPattern=7 5;" : ""}fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=1;align=center;verticalAlign=middle;`;
const icon = (name, color) => `shape=image;html=1;imageAspect=1;image=${iconUri(name, color)};strokeColor=none;fillColor=none;`;

vertex("title", "One transition, two valid commitments", text(22, C.ink, true), 24, 4, 550, 48);
vertex("kicker", "TRI matched diagnostic", text(13, C.teal, true, "left", true), 588, 15, 196, 24);

vertex("fixed_icon", "", icon("Layers3", C.blue), 54, 59, 16, 16);
vertex("fixed", "FIXED  S0, S1, q, action, schema, interface", text(10, C.charcoal, true), 78, 54, 315, 27);
vertex("timing_icon", "", icon("TimerReset", C.teal), 410, 59, 16, 16);
vertex("timing", "ONLY CHANGE  commitment timing", text(11, C.teal, true), 434, 54, 235, 27);
vertex("repeat", "same refresh, replayed twice", text(10, C.blue, false, "center", true), 712, 54, 210, 27);

vertex("p", "P", ellipse(C.coral, C.coral, 1.5, 16, C.white), 50, 98, 36, 36);
vertex("p_icon", "", icon("LockKeyhole", C.coral), 112, 101, 28, 28);
vertex("p_label", "Preserve", text(16, C.coral, true), 150, 91, 105, 25);
vertex("p_action", "bind A before refresh", text(10, C.coral, true), 150, 116, 150, 20);

vertex("r", "R", ellipse(C.teal, C.teal, 1.5, 16, C.white), 50, 246, 36, 36);
vertex("r_icon", "", icon("RefreshCcw", C.teal), 112, 249, 28, 28);
vertex("r_label", "Reevaluate", text(16, C.teal, true), 150, 239, 115, 25);
vertex("r_action", "defer q until after refresh", text(10, C.teal, true), 150, 264, 175, 20);
vertex("pair", "MATCHED PAIR", text(9, C.charcoal, true, "center"), 26, 174, 86, 22);

vertex("s0", "S0\nq(S0)=A\nA selected", ellipse(C.white, C.charcoal, 1.6, 11, C.charcoal), 292, 132, 88, 88);
vertex("refresh", "refresh", ellipse(C.white, C.blue, 1.8, 10, C.blue), 431, 151, 50, 50);
vertex("s1", "S1\nq(S1)=B\nA still valid", ellipse(C.white, C.charcoal, 1.6, 11, C.charcoal), 535, 132, 88, 88);
vertex("target_a", "gold\ntarget A", ellipse(C.white, C.coral, 2, 10, C.coral), 678, 91, 48, 48);
vertex("target_b", "gold\ntarget B", ellipse(C.white, C.teal, 2, 10, C.teal), 678, 247, 48, 48);
vertex("bound", "BOUND A", text(10, C.coral, true, "center"), 420, 91, 74, 20);
vertex("defer", "DEFER q", text(10, C.teal, true, "center"), 365, 255, 70, 20);
vertex("resolve", "resolve q on S1", text(9, C.teal, true, "center"), 540, 249, 112, 20);
vertex("a_valid", "A survives and remains action-valid in S1", text(9, C.coral, false, "center", true), 500, 286, 194, 24);

edge("shared_1", "s0", "refresh", C.charcoal, false, false);
edge("shared_2", "refresh", "s1", C.charcoal, false, false);
edge("p_1", "p_action", "s0", C.coral, false, true);
edge("p_2a", "s0", "bound", C.coral, false, true);
edge("p_2b", "bound", "s1", C.coral, false, true);
edge("p_3", "s1", "target_a", C.coral, false, true);
edge("r_1", "defer", "refresh", C.teal, true, true);
edge("r_2", "refresh", "s1", C.teal, true, true);
edge("r_3", "s1", "target_b", C.teal, true, true);

vertex("withheld_icon", "", icon("EyeOff", C.muted), 747, 164, 20, 20);
vertex("withheld", "gold mode/target and normalized generator fields withheld", text(8, C.muted, false, "center", true), 718, 188, 82, 55);

vertex("probe_heading", "same probe + interface", text(11, C.charcoal, true, "center"), 798, 75, 150, 22);
vertex("probe_p", "P", ellipse(C.coral, C.coral, 1, 13, C.white), 795, 120, 30, 30);
vertex("probe_r", "R", ellipse(C.teal, C.teal, 1, 13, C.white), 795, 219, 30, 30);
vertex("probe", "PROBE\nblack-box controller\ninstruction + history\n+ observed state\n-> target ID", ellipse(C.white, C.charcoal, 1.8, 12.5, C.charcoal), 842, 119, 96, 124);
vertex("tp", "T_P", round(C.coralLight, C.coral, 1.4, false, 9, C.coral), 946, 126, 42, 28);
vertex("tr", "T_R", round(C.tealLight, C.teal, 1.4, true, 9, C.teal), 946, 216, 42, 28);
vertex("independent", "two independent runs", text(9, C.muted, false, "center", true), 812, 291, 154, 20);
edge("probe_p_in", "probe_p", "probe", C.coral, false, true);
edge("probe_r_in", "probe_r", "probe", C.teal, true, true);
edge("probe_p_out", "probe", "tp", C.coral, false, true);
edge("probe_r_out", "probe", "tr", C.teal, true, true);
vertex("legend", "solid Preserve  |  dashed Reevaluate", text(8, C.muted, false, "center"), 74, 311, 260, 18);

vertex("m1", "1", ellipse(C.white, C.blue, 1.8, 13, C.blue), 1004, 63, 25, 25);
vertex("m1_icon", "", icon("BadgeCheck", C.blue), 1040, 64, 18, 18);
vertex("m1_title", "PairAcc", text(14, C.ink, true), 1066, 59, 84, 28);
vertex("m1_formula", "T_P=A  AND  T_R=B", text(12, C.charcoal, true, "center", true), 1040, 88, 214, 26);
vertex("m1_slice", "complete changed-winner pairs", text(9, C.muted, false, "center"), 1040, 114, 214, 18);

vertex("m2", "2", ellipse(C.white, C.coral, 1.8, 13, C.coral), 1004, 150, 25, 25);
vertex("m2_icon", "", icon("Route", C.coral), 1040, 151, 18, 18);
vertex("m2_title", "Conditional substitution", text(13, C.ink, true), 1066, 146, 188, 28);
vertex("m2_flow", "A (correct bind)  ->  refresh  ->  B (final)", text(10, C.charcoal, true, "center"), 1040, 181, 214, 28);
vertex("m2_slice", "eligible Preserve rows: correct bind + refresh + changed winner\nA survives and remains action-valid", text(8, C.muted, false, "center"), 1040, 217, 214, 42);

vertex("m3", "3", ellipse(C.white, C.blue, 1.8, 13, C.blue), 1004, 276, 25, 25);
vertex("m3_icon", "", icon("DatabaseZap", C.blue), 1040, 277, 18, 18);
vertex("m3_title", "Execution subset", text(13, C.ink, true), 1066, 272, 188, 28);
vertex("m3_flow", "target ID  ->  tool write  ->  state diff", text(10, C.charcoal, true, "center"), 1040, 306, 214, 28);
vertex("m3_slice", "executed model-issued writes only", text(8, C.muted, false, "center"), 1040, 333, 214, 15);

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="Codex" version="26.0.9" pages="1">
  <diagram id="tri-fig2-v16" name="TRI Figure 2 v16">
    <mxGraphModel dx="1280" dy="350" grid="1" gridSize="4" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1280" pageHeight="350" math="0" shadow="0">
      <root><mxCell id="0"/><mxCell id="1" parent="0"/>${cells.join("")}</root>
    </mxGraphModel>
  </diagram>
</mxfile>`;

await fs.writeFile(out, xml, "utf8");
