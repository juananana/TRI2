import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/chu/Documents/Codex/2026-07-15/k-y/TRI";
const OUT = path.join(ROOT, "paper", "tri_final_figures", "outputs");
const C = {
  ink: "#264a56",
  blue: "#407a7f",
  teal: "#248d82",
  green: "#60aa84",
  olive: "#b4b87f",
  amber: "#eabc6b",
  orange: "#f1a464",
  coral: "#e56d4e",
  white: "#ffffff",
};

const deck = Presentation.create({ slideSize: { width: 1600, height: 780 } });
const slide = deck.slides.add();
slide.background.fill = C.white;

function addShape(geometry, name, position, fill = "none", stroke = "none", sw = 0, extra = {}) {
  return slide.shapes.add({
    geometry,
    name,
    position,
    fill,
    line: { style: extra.lineStyle ?? "solid", fill: stroke, width: sw },
    ...extra,
  });
}
function rect(name, x, y, w, h, fill, stroke = "none", sw = 0) {
  return addShape("rect", name, { left: x, top: y, width: w, height: h }, fill, stroke, sw);
}
function round(name, x, y, w, h, fill, stroke, sw = 2, radius = 16, lineStyle = "solid") {
  const s = addShape("roundRect", name, { left: x, top: y, width: w, height: h }, fill, stroke, sw, { lineStyle });
  s.borderRadius = radius;
  return s;
}
function line(name, x, y, w, h, color, sw = 2, style = "solid") {
  return addShape("line", name, { left: x, top: y, width: w, height: h }, "none", color, sw, { lineStyle: style });
}
function arrow(name, x, y, w, h, color) {
  return addShape("rightArrow", name, { left: x, top: y, width: w, height: h }, color, color, 0.4);
}
function text(name, value, x, y, w, h, opts = {}) {
  const s = addShape("textbox", name, { left: x, top: y, width: w, height: h }, "none", "none", 0);
  s.text = value;
  s.text.style = {
    typeface: "Arial",
    fontSize: opts.size ?? 24,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    color: opts.color ?? C.ink,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
    autoFit: "shrinkText",
    wrap: "square",
    lineSpacing: opts.lineSpacing ?? 0.94,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return s;
}
function circle(name, label, cx, cy, d, fill, stroke, labelColor = C.ink, size = 24, sw = 2) {
  const s = addShape("ellipse", name, { left: cx - d / 2, top: cy - d / 2, width: d, height: d }, fill, stroke, sw);
  s.text = label;
  s.text.style = {
    typeface: "Arial",
    fontSize: size,
    bold: true,
    color: labelColor,
    alignment: "center",
    verticalAlignment: "middle",
    autoFit: "shrinkText",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return s;
}
function lockIcon(name, x, y, color) {
  round(`${name}-shackle`, x + 8, y, 38, 36, "none", color, 4, 18);
  rect(`${name}-mask`, x + 3, y + 23, 48, 16, C.white, C.white, 0);
  round(`${name}-body`, x, y + 24, 54, 44, color, color, 0, 8);
  circle(`${name}-key`, "", x + 27, y + 43, 9, C.white, C.white, C.white, 1);
  rect(`${name}-key-stem`, x + 24, y + 44, 6, 13, C.white, C.white, 0);
}
function clockIcon(name, x, y, color) {
  circle(`${name}-face`, "", x + 29, y + 32, 58, C.white, color, color, 1);
  line(`${name}-hand-1`, x + 29, y + 17, 0, 15, color, 3);
  line(`${name}-hand-2`, x + 29, y + 32, 14, 7, color, 3);
  circle(`${name}-hub`, "", x + 29, y + 32, 7, color, color, color, 1);
}
function robot(name, x, y, color) {
  line(`${name}-antenna`, x + 38, y - 10, 0, 12, color, 2);
  circle(`${name}-tip`, "", x + 38, y - 12, 7, color, color, color, 1);
  round(`${name}-head`, x, y, 76, 56, C.white, color, 2.3, 13);
  circle(`${name}-eye-1`, "", x + 24, y + 23, 8, color, color, color, 1);
  circle(`${name}-eye-2`, "", x + 52, y + 23, 8, color, color, color, 1);
  line(`${name}-mouth`, x + 24, y + 40, 28, 0, color, 2.2);
}

// Title and compact direct legend.
text("title", "TRI evaluates two referent threads over one controlled transition", 48, 20, 1120, 48, { size: 36, bold: true });
text("subtitle", "World evidence changes once; commitment timing determines which identity may reach the action.", 50, 67, 1100, 30, { size: 23, bold: true, color: C.teal });
line("title-rule", 48, 108, 1504, 0, C.ink, 2.2);
line("legend-p-line", 1210, 38, 72, 0, C.coral, 5);
text("legend-p", "Preserve: bound identity", 1292, 24, 250, 28, { size: 21, bold: true, color: C.coral });
line("legend-r-line", 1210, 78, 72, 0, C.teal, 4, "dashed");
text("legend-r", "Reevaluate: deferred selector", 1292, 64, 250, 28, { size: 21, bold: true, color: C.teal });

// Continuous layered canvas and refresh lens.
round("world-band", 48, 126, 1504, 232, `${C.blue}/4`, `${C.blue}/35`, 1.4, 22);
round("referent-band", 48, 378, 1504, 252, C.white, `${C.ink}/28`, 1.5, 22);
round("refresh-lens", 704, 140, 190, 474, `${C.amber}/12`, C.amber, 2.2, 50);
rect("world-tag", 68, 141, 214, 34, C.blue, C.blue, 0);
text("world-tag-text", "WORLD / SELECTOR LAYER", 78, 144, 194, 28, { size: 21, bold: true, color: C.white, align: "center" });
rect("ref-tag", 68, 393, 244, 34, C.ink, C.ink, 0);
text("ref-tag-text", "REFERENT / AUTHORIZATION LAYER", 78, 396, 224, 28, { size: 21, bold: true, color: C.white, align: "center" });
text("refresh-label", "CONTROLLED\nREFRESH", 726, 170, 146, 64, { size: 24, bold: true, color: C.ink, align: "center" });

// Frozen task substrate floats at the left; it is not a separate pipeline box.
round("task-token", 78, 198, 218, 126, C.white, C.blue, 1.8, 14);
text("task-token-head", "FROZEN TASK SUBSTRATE", 94, 210, 186, 28, { size: 22, bold: true, color: C.blue, align: "center" });
line("task-token-rule", 96, 246, 182, 0, C.olive, 1.3);
text("task-token-body", "selector q: top-ranked valid entity\naction a: mutate selected ID", 98, 256, 178, 56, { size: 21, bold: true, align: "center" });
arrow("substrate-to-state", 292, 245, 58, 20, C.olive);

// State nodes exist before connectors; connectors are routed behind them below.
circle("a0-halo", "", 418, 210, 88, `${C.coral}/10`, `${C.coral}/20`, C.coral, 1, 1);
const a0 = circle("a0", "A", 418, 210, 56, C.white, C.coral, C.coral, 28, 2.4);
const b0 = circle("b0", "B", 418, 300, 48, C.white, C.teal, C.teal, 24, 2);
circle("b1-halo", "", 1074, 210, 88, `${C.teal}/10`, `${C.teal}/20`, C.teal, 1, 1);
const b1 = circle("b1", "B", 1074, 210, 56, C.white, C.teal, C.teal, 28, 2.4);
const a1 = circle("a1", "A", 1074, 300, 48, C.white, C.coral, C.coral, 24, 2);
text("s0-label", "S0  BEFORE", 354, 150, 128, 30, { size: 23, bold: true, align: "center" });
text("s1-label", "S1  AFTER", 1010, 150, 128, 30, { size: 23, bold: true, align: "center" });
text("a0-winner", "q(S0) winner", 356, 244, 124, 24, { size: 20, bold: true, color: C.coral, align: "center" });
text("b1-winner", "q(S1) winner", 1012, 244, 124, 24, { size: 20, bold: true, color: C.teal, align: "center" });
text("a1-valid", "A remains action-valid", 970, 312, 208, 24, { size: 20, bold: true, color: C.green, align: "center" });
line("time-axis", 342, 342, 846, 0, C.olive, 1.5);
text("time-axis-before", "pre-refresh", 350, 346, 120, 20, { size: 18, italic: true, color: C.blue, align: "center" });
text("time-axis-after", "post-refresh", 1018, 346, 120, 20, { size: 18, italic: true, color: C.blue, align: "center" });

// Two referent threads, bound/deferred on the same world-state transition.
lockIcon("preserve-lock", 96, 447, C.coral);
text("preserve-label", "PRESERVE", 168, 438, 158, 30, { size: 25, bold: true, color: C.coral });
text("preserve-sub", "bind before refresh", 168, 471, 176, 28, { size: 22, bold: true });
clockIcon("reeval-clock", 95, 536, C.teal);
text("reeval-label", "REEVALUATE", 168, 528, 176, 30, { size: 25, bold: true, color: C.teal });
text("reeval-sub", "resolve after refresh", 168, 561, 178, 28, { size: 22, bold: true });

const pBound = circle("p-bound", "A", 418, 470, 60, `${C.coral}/9`, C.coral, C.coral, 29, 2.4);
text("p-bound-note", "bound at S0", 362, 506, 112, 24, { size: 20, bold: true, color: C.coral, align: "center" });
const rOpen = circle("r-open", "q?", 418, 570, 60, C.white, C.teal, C.teal, 23, 2.4);
text("r-open-note", "deferred", 370, 606, 96, 22, { size: 20, bold: true, color: C.teal, align: "center" });
const rBind = circle("r-bind", "B", 1074, 570, 60, `${C.teal}/9`, C.teal, C.teal, 29, 2.4);
text("r-bind-note", "bind at S1", 1020, 606, 108, 22, { size: 20, bold: true, color: C.teal, align: "center" });

// Controller is a lens on the two threads, not a separate module.
round("controller-lens", 1158, 416, 158, 190, `${C.blue}/7`, C.blue, 2.4, 58);
robot("controller-robot", 1199, 438, C.blue);
text("controller-text", "SAME\nCONTROLLER", 1174, 505, 126, 58, { size: 20, bold: true, color: C.blue, align: "center" });
text("controller-target", "target ID", 1192, 566, 90, 24, { size: 20, bold: true, color: C.ink, align: "center" });

const pOut = circle("p-output", "A", 1388, 470, 62, C.white, C.coral, C.coral, 30, 2.4);
const rOut = circle("r-output", "B", 1388, 570, 62, C.white, C.teal, C.teal, 30, 2.4);
text("p-output-label", "T_P  gold A", 1336, 505, 104, 24, { size: 20, bold: true, color: C.coral, align: "center" });
text("r-output-label", "T_R  gold B", 1336, 605, 104, 24, { size: 20, bold: true, color: C.teal, align: "center" });

// Joint target bracket and PairAcc seal.
line("joint-bracket-v", 1450, 470, 0, 100, C.ink, 2.2);
line("joint-bracket-top", 1438, 470, 12, 0, C.ink, 2.2);
line("joint-bracket-bottom", 1438, 570, 12, 0, C.ink, 2.2);
arrow("joint-to-pairacc", 1452, 510, 34, 18, C.ink);
circle("pairacc-seal", "2/2", 1514, 520, 64, C.ink, C.ink, C.white, 22, 2);
text("pairacc-label", "PairAcc", 1476, 555, 76, 24, { size: 20, bold: true, color: C.ink, align: "center" });

// Connectors and identity links.
const aTrajectory = slide.shapes.connect(a0, a1, {
  kind: "straight",
  fromSide: "right",
  toSide: "left",
  line: { style: "solid", fill: C.coral, width: 4 },
  tail: { type: "arrow", width: "sm", length: "sm" },
});
const bTrajectory = slide.shapes.connect(b0, b1, {
  kind: "straight",
  fromSide: "right",
  toSide: "left",
  line: { style: "solid", fill: C.teal, width: 4 },
  tail: { type: "arrow", width: "sm", length: "sm" },
});
const aIdentity = slide.shapes.connect(a0, pBound, {
  kind: "straight",
  fromSide: "bottom",
  toSide: "top",
  line: { style: "dashed", fill: C.coral, width: 2.2 },
});
const bIdentity = slide.shapes.connect(b1, rBind, {
  kind: "straight",
  fromSide: "bottom",
  toSide: "top",
  line: { style: "dashed", fill: C.teal, width: 2.2 },
});
const preserveThread = slide.shapes.connect(pBound, pOut, {
  kind: "straight",
  fromSide: "right",
  toSide: "left",
  line: { style: "solid", fill: C.coral, width: 5 },
  tail: { type: "arrow", width: "med", length: "med" },
});
const deferredThread = slide.shapes.connect(rOpen, rBind, {
  kind: "straight",
  fromSide: "right",
  toSide: "left",
  line: { style: "dashed", fill: C.teal, width: 4 },
});
const resolvedThread = slide.shapes.connect(rBind, rOut, {
  kind: "straight",
  fromSide: "right",
  toSide: "left",
  line: { style: "solid", fill: C.teal, width: 5 },
  tail: { type: "arrow", width: "med", length: "med" },
});

for (const connector of [aTrajectory, bTrajectory, aIdentity, bIdentity, preserveThread, deferredThread, resolvedThread]) {
  connector.bringToFront();
}

// Observable error is a branch on the Preserve thread, not another module.
const errorNode = circle("substitution-node", "B", 960, 522, 48, C.white, C.coral, C.coral, 24, 2);
const errorBranch = slide.shapes.connect(pBound, errorNode, {
  kind: "curved",
  fromSide: "right",
  toSide: "left",
  line: { style: "dashed", fill: C.coral, width: 2.8 },
  tail: { type: "arrow", width: "sm", length: "sm" },
});
errorBranch.bringToFront();
text("error-label", "re-run q: A -> B\nconditional substitution", 800, 483, 172, 56, { size: 20, bold: true, color: C.coral, align: "center" });
circle("error-x", "x", 992, 522, 24, C.coral, C.coral, C.white, 17, 1.5);

// Overlay the semantic nodes and controller lens so foreground lines terminate cleanly.
circle("a0-overlay", "A", 418, 210, 56, C.white, C.coral, C.coral, 28, 2.4);
circle("b0-overlay", "B", 418, 300, 48, C.white, C.teal, C.teal, 24, 2);
circle("b1-overlay", "B", 1074, 210, 56, C.white, C.teal, C.teal, 28, 2.4);
circle("a1-overlay", "A", 1074, 300, 48, C.white, C.coral, C.coral, 24, 2);
circle("p-bound-overlay", "A", 418, 470, 60, `${C.coral}/9`, C.coral, C.coral, 29, 2.4);
circle("r-open-overlay", "q?", 418, 570, 60, C.white, C.teal, C.teal, 23, 2.4);
circle("r-bind-overlay", "B", 1074, 570, 60, `${C.teal}/9`, C.teal, C.teal, 29, 2.4);
round("controller-lens-overlay", 1158, 416, 158, 190, `${C.blue}/7`, C.blue, 2.4, 58);
robot("controller-robot-overlay", 1199, 438, C.blue);
text("controller-text-overlay", "SAME\nCONTROLLER", 1174, 505, 126, 58, { size: 20, bold: true, color: C.blue, align: "center" });
text("controller-target-overlay", "target ID", 1192, 566, 90, 24, { size: 20, bold: true, color: C.ink, align: "center" });
circle("p-output-overlay", "A", 1388, 470, 62, C.white, C.coral, C.coral, 30, 2.4);
circle("r-output-overlay", "B", 1388, 570, 62, C.white, C.teal, C.teal, 30, 2.4);
circle("substitution-node-overlay", "B", 960, 522, 48, C.white, C.coral, C.coral, 24, 2);
circle("error-x-overlay", "x", 992, 522, 24, C.coral, C.coral, C.white, 17, 1.5);

// Metric legend is a reading key for the integrated graph.
line("footer-rule", 48, 654, 1504, 0, C.ink, 1.8);
circle("footer-p-a", "A", 88, 704, 36, C.white, C.coral, C.coral, 18);
circle("footer-p-b", "B", 118, 704, 36, C.white, C.teal, C.teal, 18);
text("footer-pair", "PairAcc", 146, 674, 116, 28, { size: 23, bold: true });
text("footer-pair-desc", "both tracks correct", 146, 704, 210, 28, { size: 21, bold: true, color: C.blue });

circle("footer-s-a", "A", 492, 704, 40, C.white, C.coral, C.coral, 20);
arrow("footer-s-arrow", 516, 696, 58, 16, C.coral);
circle("footer-s-b", "B", 598, 704, 40, C.white, C.coral, C.coral, 20);
text("footer-sub", "Conditional substitution", 634, 674, 286, 28, { size: 23, bold: true });
text("footer-sub-desc", "Preserve ends at B", 634, 704, 326, 28, { size: 21, bold: true, color: C.coral });

addShape("can", "footer-db", { left: 1100, top: 678, width: 54, height: 54 }, `${C.green}/10`, C.green, 2);
arrow("footer-write-arrow", 1164, 696, 58, 16, C.green);
text("footer-write", "Executed state diff", 1234, 674, 222, 28, { size: 23, bold: true });
text("footer-write-desc", "selected ID receives the write", 1234, 704, 292, 28, { size: 21, bold: true, color: C.green });

slide.speakerNotes.textFrame.setText(
  "[Sources]\n" +
  "- Internal manuscript: paper/AnonymousSubmission2027.tex (TRI definition, Diagnostic Construction, Measurements and Denominators, Controller Probes).\n" +
  "- User-supplied references: GSD problem/method overview, SymPareto scientific comparison, MetaEval framework. The integrated layered visual grammar is adapted; no artwork is copied.\n" +
  "- Palette: #264a56, #407a7f, #248d82, #60aa84, #b4b87f, #eabc6b, #f1a464, #e56d4e."
);

await fs.mkdir(OUT, { recursive: true });
const stem = "fig2_tri_crossed_referent_graph_v4";
async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}
await writeBlob(path.join(OUT, `${stem}.png`), await deck.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(path.join(OUT, `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
const inspection = await deck.inspect({ kind: "slide,textbox,shape,notes", maxChars: 40000 });
await fs.writeFile(path.join(OUT, `${stem}.inspect.ndjson`), inspection.ndjson);
const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(path.join(OUT, `${stem}.pptx`));
