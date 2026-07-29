import fs from "node:fs/promises";
import path from "node:path";
import { icons as lucideIcons } from "lucide";

const out = process.argv[2] || path.resolve("fig2_tri_diagnostic_workflow_v17_expressive.drawio");
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
  const style = `${curved ? "curved=1" : "edgeStyle=orthogonalEdgeStyle"};rounded=1;html=1;endArrow=block;endFill=1;endSize=8;strokeColor=${color};strokeWidth=2.5;${dashed ? "dashed=1;dashPattern=8 6;" : ""}`;
  cells.push(`<mxCell id="${id}" value="" style="${style}" edge="1" parent="1" source="${source}" target="${target}"><mxGeometry relative="1" as="geometry"/></mxCell>`);
}

const text = (size, color = C.text, bold = false, align = "left", italic = false) =>
  `text;html=1;strokeColor=none;fillColor=none;whiteSpace=wrap;overflow=hidden;fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=${(bold ? 1 : 0) + (italic ? 2 : 0)};align=${align};verticalAlign=middle;spacing=0;`;
const ellipse = (fill, stroke, sw = 1.5, size = 12, color = C.text) =>
  `ellipse;whiteSpace=wrap;html=1;fillColor=${fill};strokeColor=${stroke};strokeWidth=${sw};fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=1;align=center;verticalAlign=middle;`;
const round = (fill, stroke, sw = 1.3, dashed = false, size = 10, color = C.text) =>
  `rounded=1;arcSize=14;whiteSpace=wrap;html=1;fillColor=${fill};strokeColor=${stroke};strokeWidth=${sw};${dashed ? "dashed=1;dashPattern=7 5;" : ""}fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=1;align=center;verticalAlign=middle;`;
const icon = (name, color) => `shape=image;html=1;imageAspect=1;image=${iconUri(name, color)};strokeColor=none;fillColor=none;`;

vertex("title", "One transition, two valid commitments", text(26, C.ink, true), 24, 8, 560, 42);
vertex("subtitle", "TRI turns resolution timing into a matched diagnostic.", text(15, C.teal, true, "left", true), 26, 47, 560, 28);
vertex("fixed_icon", "", icon("Layers3", C.blue), 36, 91, 18, 18);
vertex("fixed", "FIXED  S0, S1, q, action, schema, interface", text(10, C.charcoal, true), 60, 87, 330, 26);
vertex("change_icon", "", icon("TimerReset", C.teal), 398, 91, 18, 18);
vertex("change", "ONLY COMMITMENT TIMING CHANGES", text(12, C.teal, true), 422, 87, 280, 26);

vertex("preserve", "P   Preserve\nbind A before refresh", round(C.coralLight, C.coral, 1.3, false, 14, C.coral), 42, 126, 245, 72);
vertex("reevaluate", "R   Reevaluate\nresolve q after refresh", round(C.tealLight, C.teal, 1.3, false, 14, C.teal), 42, 244, 245, 72);
vertex("pair", "MATCHED PAIR", text(10, C.charcoal, true, "center"), 91, 211, 145, 22);

vertex("bound", "BOUND A", text(11, C.coral, true, "center"), 339, 116, 80, 22);
vertex("s0", "S0\nq(S0)=A\nA selected", ellipse(C.white, C.charcoal, 1.8, 11, C.charcoal), 326, 148, 104, 104);
vertex("refresh", "refresh", ellipse(C.white, C.blue, 1.8, 11, C.blue), 489, 173, 58, 58);
vertex("s1", "S1\nq(S1)=B\nA survives + valid", ellipse(C.white, C.charcoal, 1.8, 11, C.charcoal), 605, 148, 104, 104);
vertex("p_path", "preserve A", text(9, C.coral, true, "center"), 497, 116, 92, 20);
vertex("defer", "DEFER q", text(11, C.teal, true, "center"), 448, 291, 80, 22);
vertex("target_a", "gold\ntarget A", ellipse(C.white, C.coral, 2, 10, C.coral), 759, 113, 48, 48);
vertex("target_b", "gold\ntarget B", ellipse(C.white, C.teal, 2, 10, C.teal), 759, 253, 48, 48);
vertex("valid", "A survives and remains action-valid", text(10, C.coral, true, "center", true), 606, 286, 190, 28);

edge("shared_1", "s0", "refresh", C.charcoal, false, false);
edge("shared_2", "refresh", "s1", C.charcoal, false, false);
edge("p_1", "bound", "s0", C.coral, false, true);
edge("p_2", "s0", "p_path", C.coral, false, true);
edge("p_3", "p_path", "s1", C.coral, false, true);
edge("p_4", "s1", "target_a", C.coral, false, true);
edge("r_1", "defer", "refresh", C.teal, true, true);
edge("r_2", "refresh", "s1", C.teal, true, true);
edge("r_3", "s1", "target_b", C.teal, true, true);

vertex("eye", "", icon("EyeOff", C.muted), 835, 181, 18, 18);
vertex("withheld", "Withheld: gold mode/target, normalized selector fields, generator winner IDs", text(8, C.muted, false, "center", true), 735, 319, 390, 18);
vertex("probe_heading", "same controller + interface", text(11, C.charcoal, true, "center"), 899, 109, 178, 23);
vertex("probe_p", "P", ellipse(C.coral, C.coral, 1, 14, C.white), 892, 146, 32, 32);
vertex("probe_r", "R", ellipse(C.teal, C.teal, 1, 14, C.white), 892, 236, 32, 32);
vertex("probe", "PROBE\ncontroller black box\n\ninstruction + history\n+ observed state\n-&gt; target ID", ellipse(C.white, C.charcoal, 2, 12, C.charcoal), 932, 138, 118, 118);
vertex("tp", "T_P", round(C.coralLight, C.coral, 1.5, false, 10, C.coral), 1063, 149, 58, 32);
vertex("tr", "T_R", round(C.tealLight, C.teal, 1.5, true, 10, C.teal), 1063, 237, 58, 32);
vertex("runs", "two independent runs", text(9, C.muted, false, "center", true), 1070, 300, 170, 18);
edge("probe_p_in", "probe_p", "probe", C.coral, false, true);
edge("probe_r_in", "probe_r", "probe", C.teal, true, true);
edge("probe_p_out", "probe", "tp", C.coral, false, true);
edge("probe_r_out", "probe", "tr", C.teal, true, true);

vertex("band_title", "OBSERVABLE READOUTS", text(10, C.blue, true), 43, 356, 180, 24);
vertex("pairacc_icon", "", icon("BadgeCheck", C.blue), 44, 393, 22, 22);
vertex("pairacc_title", "PairAcc", text(18, C.ink, true), 77, 387, 140, 32);
vertex("pairacc_formula", "T_P=A  AND  T_R=B", text(15, C.charcoal, true, "left", true), 77, 421, 260, 28);
vertex("pairacc_denom", "complete changed-winner pairs", text(10, C.muted), 77, 452, 270, 20);

vertex("sub_icon", "", icon("Route", C.coral), 449, 393, 22, 22);
vertex("sub_title", "Conditional substitution", text(17, C.ink, true), 482, 387, 300, 32);
vertex("sub_flow", "A (correct bind)  -&gt;  refresh  -&gt;  B (final)", text(11, C.charcoal, true, "center"), 470, 422, 330, 28);
vertex("sub_denom", "eligible Preserve: correct bind + completed refresh + changed winner + surviving, action-valid A", text(9, C.muted, false, "center"), 452, 450, 370, 25);

vertex("exec_icon", "", icon("DatabaseZap", C.blue), 879, 393, 22, 22);
vertex("exec_title", "Execution subset", text(17, C.ink, true), 912, 387, 280, 32);
vertex("exec_flow", "target ID  -&gt;  tool write  -&gt;  state diff", text(11, C.charcoal, true, "center"), 886, 422, 340, 28);
vertex("exec_denom", "executed model-issued writes only", text(10, C.muted, false, "center"), 903, 452, 290, 20);

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="Codex" version="26.0.9" pages="1">
  <diagram id="tri-fig2-v17" name="TRI Figure 2 v17">
    <mxGraphModel dx="1280" dy="480" grid="1" gridSize="4" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1280" pageHeight="480" math="0" shadow="0">
      <root><mxCell id="0"/><mxCell id="1" parent="0"/>${cells.join("")}</root>
    </mxGraphModel>
  </diagram>
</mxfile>`;

await fs.writeFile(out, xml, "utf8");
