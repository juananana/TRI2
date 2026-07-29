import fs from "node:fs/promises";
import path from "node:path";
import { icons as lucideIcons } from "lucide";

const out = process.argv[2] || path.resolve("fig2_tri_diagnostic_workflow_v18_paper_readable.drawio");

const C = {
  ink: "#0D0D0E",
  charcoal: "#264A56",
  muted: "#708084",
  rule: "#A9B6B8",
  teal: "#248D82",
  tealMid: "#407A7F",
  tealLight: "#DCEFF0",
  tealWash: "#F1FAFA",
  coral: "#C12A36",
  coralLight: "#F8E8E9",
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

function iconUri(name, color) {
  const body = lucideIcons[name].map(([tag, attrs]) => {
    const serialized = Object.entries(attrs).map(([key, value]) => `${key}="${esc(value)}"`).join(" ");
    return `<${tag} ${serialized}/>`;
  }).join("");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
  return `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;
}

const cells = [];

function vertex(id, value, style, x, y, width, height) {
  cells.push(`<mxCell id="${id}" value="${esc(value)}" style="${style}" vertex="1" parent="content-group"><mxGeometry x="${x}" y="${y}" width="${width}" height="${height}" as="geometry"/></mxCell>`);
}

function edge(id, source, target, color, opts = {}) {
  const dashed = opts.dashed ? "dashed=1;dashPattern=8 6;" : "";
  const label = opts.label ? esc(opts.label) : "";
  const points = (opts.points || []).map(([x, y]) => `<mxPoint x="${x}" y="${y}"/>`).join("");
  const pointsXml = points ? `<Array as="points">${points}</Array>` : "";
  cells.push(`<mxCell id="${id}" value="${label}" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;endSize=8;strokeColor=${color};strokeWidth=${opts.width ?? 2.5};${dashed}fontFamily=Arial;fontSize=14;fontColor=${color};fontStyle=1;" edge="1" parent="content-group" source="${source}" target="${target}"><mxGeometry relative="1" as="geometry">${pointsXml}</mxGeometry></mxCell>`);
}

const text = (size, color = C.charcoal, bold = false, align = "left", italic = false) =>
  `text;html=1;strokeColor=none;fillColor=none;whiteSpace=wrap;overflow=hidden;fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=${(bold ? 1 : 0) + (italic ? 2 : 0)};align=${align};verticalAlign=middle;spacing=0;`;
const ellipse = (fill, stroke, width = 1.8, size = 15, color = C.charcoal) =>
  `ellipse;whiteSpace=wrap;html=1;fillColor=${fill};strokeColor=${stroke};strokeWidth=${width};fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=1;align=center;verticalAlign=middle;`;
const round = (fill, stroke, width = 1.5, dashed = false, size = 15, color = C.charcoal) =>
  `rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=${fill};strokeColor=${stroke};strokeWidth=${width};${dashed ? "dashed=1;dashPattern=8 6;" : ""}fontFamily=Arial;fontSize=${size};fontColor=${color};fontStyle=1;align=center;verticalAlign=middle;`;
const icon = (name, color) => `shape=image;html=1;imageAspect=1;image=${iconUri(name, color)};strokeColor=none;fillColor=none;`;

vertex("top-band", "", `rect;html=1;fillColor=${C.white};strokeColor=none;`, 0, 0, 960, 78);
vertex("bottom-band", "", `rect;html=1;fillColor=${C.white};strokeColor=none;`, 0, 300, 960, 100);
vertex("title", "One transition, two valid commitments", text(27, C.ink, true), 24, 8, 620, 45);
vertex("subtitle", "TRI turns resolution timing into a matched diagnostic.", text(16, C.tealMid, true, "left", true), 26, 45, 600, 28);

vertex("fixed", "FIXED: S0, S1, q, action, schema, I/O", text(15, C.charcoal, true), 30, 84, 350, 28);
vertex("timing", "ONLY COMMITMENT TIME CHANGES", text(15, C.teal, true), 400, 84, 315, 28);

vertex("preserve", "P  PRESERVE\nbind A pre-refresh", round(C.coralLight, C.coral, 1.5, false, 16, C.coral), 30, 132, 185, 58);
vertex("reevaluate", "R  REEVALUATE\nresolve q after refresh", round(C.tealLight, C.teal, 1.5, true, 16, C.teal), 30, 222, 185, 58);
vertex("pair", "MATCHED TASK PAIR", text(14, C.charcoal, true, "center"), 42, 195, 160, 24);

vertex("s0", "S0\nq(S0)=A", ellipse(C.white, C.charcoal, 2, 16, C.charcoal), 245, 145, 105, 105);
vertex("refresh", "", ellipse(C.amberLight, C.amber, 2.4, 15, C.charcoal), 400, 163, 70, 70);
vertex("refresh-label", "REFRESH", text(15, C.charcoal, true, "center"), 400, 135, 70, 24);
vertex("s1", "S1: q(S1)=B\nA remains valid", ellipse(C.white, C.charcoal, 2, 14, C.charcoal), 520, 145, 105, 105);
edge("shared-1", "s0", "refresh", C.charcoal, { width: 2.6 });
edge("shared-2", "refresh", "s1", C.charcoal, { width: 2.6 });

vertex("gold-a", "gold A", ellipse(C.white, C.coral, 2, 15, C.coral), 650, 105, 50, 50);
vertex("gold-b", "gold B", ellipse(C.white, C.teal, 2, 15, C.teal), 650, 230, 50, 50);
edge("preserve-path", "preserve", "gold-a", C.coral, {
  width: 3,
  label: "Preserve",
  points: [[230, 120], [625, 120]],
});
edge("reevaluate-path", "reevaluate", "gold-b", C.teal, {
  width: 3,
  dashed: true,
  label: "Reevaluate",
  points: [[230, 286], [625, 286]],
});

vertex("screen", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 708, 125, 2, 150);
vertex("withheld", "NO GOLD INPUT", text(14, C.muted, true, "center"), 716, 276, 136, 22);

vertex("probe-p", "P", ellipse(C.coral, C.coral, 1, 15, C.white), 728, 155, 28, 28);
vertex("probe-r", "R", ellipse(C.teal, C.teal, 1, 15, C.white), 728, 225, 28, 28);
vertex("probe", "SAME PROBE\nblack box", round(C.white, C.charcoal, 2.2, false, 16, C.ink), 760, 150, 100, 100);
vertex("probe-input", "same inputs", text(14, C.charcoal, true, "center"), 760, 254, 100, 22);
vertex("tp", "T_P", round(C.coralLight, C.coral, 1.5, false, 14, C.coral), 875, 155, 60, 35);
vertex("tr", "T_R", round(C.tealLight, C.teal, 1.5, true, 14, C.teal), 875, 225, 60, 35);
edge("probe-p-in", "probe-p", "probe", C.coral, { width: 2.5 });
edge("probe-r-in", "probe-r", "probe", C.teal, { width: 2.5, dashed: true });
edge("probe-p-out", "probe", "tp", C.coral, { width: 2.5 });
edge("probe-r-out", "probe", "tr", C.teal, { width: 2.5, dashed: true });

vertex("readout-rule", "", `shape=line;html=1;strokeColor=${C.charcoal};strokeWidth=2;`, 220, 316, 715, 2);
vertex("readout-title", "OBSERVABLE READOUTS", text(14, C.tealMid, true, "center"), 22, 304, 194, 25);
vertex("sep-1", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 320, 333, 1, 50);
vertex("sep-2", "", `rect;html=1;fillColor=${C.rule};strokeColor=none;`, 630, 333, 1, 50);
vertex("pairacc-title", "PairAcc", text(18, C.ink, true, "center"), 70, 330, 180, 27);
vertex("pairacc-flow", "P -&gt; A  AND  R -&gt; B", text(15, C.charcoal, true, "center"), 45, 358, 250, 27);
vertex("substitution-title", "Conditional substitution", text(17, C.ink, true, "center"), 345, 330, 260, 27);
vertex("substitution-flow", "A bound -&gt; refresh -&gt; B final", text(15, C.charcoal, true, "center"), 345, 358, 260, 27);
vertex("execution-title", "Execution subset", text(17, C.ink, true, "center"), 655, 330, 270, 27);
vertex("execution-flow", "ID -&gt; write -&gt; state diff", text(15, C.charcoal, true, "center"), 645, 358, 290, 27);

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="Codex" version="26.0.9" pages="1">
  <diagram id="tri-fig2-v18" name="TRI Figure 2 v18">
    <mxGraphModel dx="960" dy="400" grid="1" gridSize="4" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="960" pageHeight="400" background="${C.tealWash}" math="0" shadow="0">
      <root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="content-group" value="" style="group;dashed=1;fillColor=none;strokeColor=none;" vertex="1" parent="1"><mxGeometry x="0" y="0" width="960" height="400" as="geometry"/></mxCell>${cells.join("")}</root>
    </mxGraphModel>
  </diagram>
</mxfile>`;

await fs.writeFile(out, xml, "utf8");
