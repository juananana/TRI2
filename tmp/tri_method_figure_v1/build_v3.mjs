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

function addShape(geometry, name, position, fill = "none", stroke = "none", width = 0, extra = {}) {
  return slide.shapes.add({
    geometry,
    name,
    position,
    fill,
    line: { style: extra.lineStyle ?? "solid", fill: stroke, width },
    ...extra,
  });
}

function rect(name, x, y, w, h, fill, stroke = "none", sw = 0) {
  return addShape("rect", name, { left: x, top: y, width: w, height: h }, fill, stroke, sw);
}

function round(name, x, y, w, h, fill, stroke, sw = 2, radius = 14, lineStyle = "solid") {
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

function circle(name, label, cx, cy, d, fill, stroke, labelColor = C.ink, size = 24) {
  const s = addShape("ellipse", name, { left: cx - d / 2, top: cy - d / 2, width: d, height: d }, fill, stroke, 2);
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

function stepTitle(n, label, x, y, width, color) {
  rect(`step-${n}-badge`, x, y, 32, 32, color, color, 0);
  text(`step-${n}-number`, String(n), x, y, 32, 32, { size: 22, bold: true, color: C.white, align: "center" });
  text(`step-${n}-label`, label, x + 42, y - 1, width - 42, 34, { size: 23, bold: true, italic: true, color });
}

function clipboard(name, x, y, color) {
  round(`${name}-paper`, x, y, 62, 76, C.white, color, 2, 8);
  round(`${name}-clip`, x + 18, y - 7, 26, 14, color, color, 0, 5);
  for (let i = 0; i < 3; i++) {
    circle(`${name}-dot-${i}`, "", x + 15, y + 21 + i * 17, 7, color, color, color, 1);
    line(`${name}-line-${i}`, x + 25, y + 21 + i * 17, 25, 0, color, 2);
  }
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
  line(`${name}-antenna`, x + 48, y - 12, 0, 14, color, 2);
  circle(`${name}-tip`, "", x + 48, y - 14, 7, color, color, color, 1);
  round(`${name}-head`, x, y, 96, 68, C.white, color, 2.6, 14);
  circle(`${name}-eye-1`, "", x + 30, y + 28, 10, color, color, color, 1);
  circle(`${name}-eye-2`, "", x + 66, y + 28, 10, color, color, color, 1);
  line(`${name}-mouth`, x + 31, y + 48, 34, 0, color, 2.4);
  for (let i = 0; i < 3; i++) {
    line(`${name}-pin-l-${i}`, x - 10, y + 16 + i * 18, 10, 0, color, 2);
    line(`${name}-pin-r-${i}`, x + 96, y + 16 + i * 18, 10, 0, color, 2);
  }
}

function database(name, x, y, color, label) {
  const s = addShape("can", name, { left: x, top: y, width: 66, height: 76 }, `${color}/10`, color, 2.2);
  text(`${name}-label`, label, x + 6, y + 20, 54, 36, { size: 23, bold: true, color, align: "center" });
  return s;
}

// Main panel frames and headers.
round("panel-a", 36, 28, 1012, 716, C.white, C.blue, 1.5, 2, "dashed");
round("panel-b", 1064, 28, 500, 716, C.white, C.blue, 1.5, 2, "dashed");
rect("panel-a-head", 36, 28, 1012, 48, C.ink, C.ink, 0);
rect("panel-b-head", 1064, 28, 500, 48, C.blue, C.blue, 0);
text("panel-a-title", "A.  MATCHED DIAGNOSTIC CONSTRUCTION", 56, 31, 972, 42, { size: 28, bold: true, color: C.white, align: "center" });
text("panel-b-title", "B.  EXECUTION AND SCORING", 1080, 31, 468, 42, { size: 28, bold: true, color: C.white, align: "center" });

// Nested step boundaries mirror top-conference framework figures without making every object a card.
round("step-1-frame", 54, 86, 238, 626, "transparent", `${C.olive}/70`, 1.2, 12, "dashed");
round("step-2-frame", 306, 86, 310, 626, "transparent", `${C.olive}/70`, 1.2, 12, "dashed");
round("step-4-frame", 1080, 86, 464, 456, "transparent", `${C.olive}/70`, 1.2, 12, "dashed");
round("step-5-frame", 1080, 552, 464, 184, "transparent", `${C.olive}/70`, 1.2, 12, "dashed");

// Connectors first so nodes remain legible.
arrow("a-flow-1", 271, 340, 42, 20, C.olive);
arrow("a-flow-2", 581, 340, 42, 20, C.olive);
arrow("state-refresh-arrow", 431, 262, 68, 24, C.amber);
arrow("preserve-timeline-1", 720, 406, 78, 18, C.coral);
arrow("preserve-timeline-2", 854, 406, 64, 18, C.coral);
arrow("reeval-timeline-1", 720, 566, 78, 18, C.teal);
arrow("reeval-timeline-2", 854, 566, 64, 18, C.teal);
arrow("pair-to-run-p", 1026, 296, 72, 18, C.coral);
arrow("pair-to-run-r", 1026, 384, 72, 18, C.teal);
arrow("b-input-p", 1106, 272, 74, 18, C.coral);
arrow("b-input-r", 1106, 360, 74, 18, C.teal);
arrow("b-output-p", 1376, 272, 68, 18, C.coral);
arrow("b-output-r", 1376, 360, 68, 18, C.teal);
arrow("tool-write-arrow", 1256, 464, 70, 20, C.olive);
arrow("state-diff-arrow", 1418, 464, 48, 20, C.green);

// Panel A / Step 1: task blueprint as a real artifact.
stepTitle(1, "TASK BLUEPRINT", 56, 94, 220, C.blue);
clipboard("blueprint-icon", 75, 145, C.blue);
text("blueprint-selector", "selector q", 151, 146, 120, 28, { size: 23, bold: true, color: C.blue });
text("blueprint-selector-v", "top-ranked\nunread", 151, 174, 124, 54, { size: 23, bold: true });
text("blueprint-action", "action a", 151, 234, 120, 28, { size: 23, bold: true, color: C.teal });
text("blueprint-action-v", "reply(id)", 151, 262, 120, 28, { size: 22, bold: true });
round("mini-table", 60, 326, 216, 154, `${C.blue}/4`, C.blue, 1.6, 10);
rect("mini-table-head", 60, 326, 216, 34, C.blue, C.blue, 0);
text("mini-h-1", "ID", 68, 329, 42, 28, { size: 22, bold: true, color: C.white, align: "center" });
text("mini-h-2", "S0", 112, 329, 44, 28, { size: 22, bold: true, color: C.white, align: "center" });
text("mini-h-3", "S1", 160, 329, 44, 28, { size: 22, bold: true, color: C.white, align: "center" });
text("mini-h-4", "valid", 205, 329, 62, 28, { size: 22, bold: true, color: C.white, align: "center" });
line("mini-v-1", 110, 326, 0, 154, C.olive, 1);
line("mini-v-2", 157, 326, 0, 154, C.olive, 1);
line("mini-v-3", 204, 326, 0, 154, C.olive, 1);
line("mini-h-row", 60, 411, 216, 0, C.olive, 1);
text("mini-a", "A", 72, 369, 30, 32, { size: 25, bold: true, color: C.coral, align: "center" });
text("mini-a0", "1", 118, 369, 30, 32, { size: 24, bold: true, align: "center" });
text("mini-a1", "2", 166, 369, 30, 32, { size: 24, align: "center" });
text("mini-av", "yes", 211, 369, 50, 32, { size: 22, bold: true, color: C.green, align: "center" });
text("mini-b", "B", 72, 426, 30, 32, { size: 25, bold: true, color: C.teal, align: "center" });
text("mini-b0", "2", 118, 426, 30, 32, { size: 24, align: "center" });
text("mini-b1", "1", 166, 426, 30, 32, { size: 24, bold: true, align: "center" });
text("mini-bv", "yes", 211, 426, 50, 32, { size: 22, bold: true, color: C.green, align: "center" });
round("generator-stack-back", 82, 520, 158, 72, `${C.olive}/10`, C.olive, 1.2, 8);
round("generator-stack-front", 70, 508, 158, 72, C.white, C.blue, 1.8, 8);
text("generator-label", "domain + schema", 84, 520, 130, 26, { size: 22, bold: true, color: C.blue, align: "center" });
text("generator-sub", "frozen task spec", 84, 548, 130, 24, { size: 22, italic: true, align: "center" });
text("blueprint-foot", "Defines the resolver, action, and validity slice", 62, 620, 210, 62, { size: 22, bold: true, color: C.ink, align: "center" });

// Panel A / Step 2: state-space transition rather than generic boxes.
stepTitle(2, "SHARED TRANSITION", 318, 94, 280, C.amber);
text("state-space-label", "selector score", 320, 145, 264, 28, { size: 22, italic: true, color: C.blue, align: "center" });
round("s0-space", 322, 180, 118, 210, C.white, C.coral, 1.8, 8);
round("s1-space", 500, 180, 118, 210, C.white, C.teal, 1.8, 8);
text("s0-space-title", "S0", 346, 187, 70, 28, { size: 24, bold: true, align: "center" });
text("s1-space-title", "S1", 524, 187, 70, 28, { size: 24, bold: true, align: "center" });
line("s0-axis", 343, 240, 0, 115, C.blue, 1.5);
line("s1-axis", 521, 240, 0, 115, C.blue, 1.5);
line("s0-high", 350, 248, 72, 0, C.olive, 1, "dashed");
line("s0-low", 350, 329, 72, 0, C.olive, 1, "dashed");
line("s1-high", 528, 248, 72, 0, C.olive, 1, "dashed");
line("s1-low", 528, 329, 72, 0, C.olive, 1, "dashed");
circle("s0-a", "A", 385, 247, 48, `${C.coral}/12`, C.coral, C.coral, 24);
circle("s0-b", "B", 385, 328, 42, `${C.teal}/8`, C.teal, C.teal, 22);
circle("s1-b", "B", 563, 247, 48, `${C.teal}/12`, C.teal, C.teal, 24);
circle("s1-a", "A", 563, 328, 42, `${C.coral}/8`, C.coral, C.coral, 22);
round("transition-facts", 324, 424, 292, 178, `${C.green}/6`, C.green, 1.8, 12);
text("facts-head", "CONTROLLED CONTRAST", 342, 434, 256, 30, { size: 23, bold: true, color: C.green, align: "center" });
circle("fact-check-1", "", 346, 486, 16, C.green, C.green, C.green, 1);
circle("fact-inner-1", "", 346, 486, 6, C.white, C.white, C.white, 1);
text("fact-1", "S0, S1, q, a fixed", 362, 470, 226, 32, { size: 22, bold: true });
circle("fact-check-2", "", 346, 530, 16, C.green, C.green, C.green, 1);
circle("fact-inner-2", "", 346, 530, 6, C.white, C.white, C.white, 1);
text("fact-2", "A remains actionable", 362, 514, 226, 32, { size: 22, bold: true });
circle("fact-check-3", "", 346, 574, 16, C.green, C.green, C.green, 1);
circle("fact-inner-3", "", 346, 574, 6, C.white, C.white, C.white, 1);
text("fact-3", "winner changes A -> B", 362, 558, 226, 32, { size: 22, bold: true, color: C.blue });
text("transition-foot", "World state changes;\nauthorization may not.", 334, 626, 270, 58, { size: 23, bold: true, italic: true, color: C.ink, align: "center" });

// Panel A / Step 3: the large, distinctive core.
round("core-panel", 628, 88, 402, 632, `${C.teal}/6`, C.teal, 2.6, 18);
rect("core-head", 628, 88, 402, 48, C.teal, C.teal, 0);
text("core-title", "3   MATCHED PAIR GENERATION", 646, 91, 366, 42, { size: 25, bold: true, color: C.white, align: "center" });
text("core-question", "WHEN DOES THE TARGET RESOLVE?", 652, 151, 354, 36, { size: 23, bold: true, color: C.ink, align: "center" });
circle("timing-switch", "BIND\nTIME", 829, 231, 100, C.white, C.ink, C.ink, 22);
line("timing-stem", 829, 279, 0, 35, C.ink, 2);
line("timing-branch", 726, 314, 206, 0, C.ink, 2);
line("timing-down-p", 726, 314, 0, 26, C.coral, 2.4);
line("timing-down-r", 932, 314, 0, 186, C.teal, 2.4);

round("preserve-track", 650, 334, 356, 128, `${C.coral}/8`, C.coral, 2.2, 14);
lockIcon("preserve-lock", 664, 360, C.coral);
text("preserve-mode", "PRESERVE", 728, 342, 138, 30, { size: 24, bold: true, color: C.coral });
text("preserve-event-1", "REFRESH", 738, 376, 78, 24, { size: 22, bold: true, color: C.coral, align: "center" });
text("preserve-event-2", "ACT", 872, 376, 60, 24, { size: 22, bold: true, color: C.coral, align: "center" });
circle("preserve-bound", "A", 828, 414, 50, C.white, C.coral, C.coral, 25);
circle("preserve-gold", "A", 950, 414, 56, C.white, C.coral, C.coral, 27);
text("preserve-bound-label", "bound S0", 782, 438, 92, 22, { size: 22, bold: true, color: C.coral, align: "center" });
text("preserve-gold-label", "gold", 920, 442, 60, 20, { size: 22, bold: true, color: C.coral, align: "center" });

round("reeval-track", 650, 494, 356, 128, `${C.teal}/8`, C.teal, 2.2, 14);
clockIcon("reeval-clock", 662, 526, C.teal);
text("reeval-mode", "REEVALUATE", 728, 502, 172, 30, { size: 24, bold: true, color: C.teal });
text("reeval-event-1", "DEFER", 738, 536, 78, 24, { size: 22, bold: true, color: C.teal, align: "center" });
text("reeval-event-2", "SELECT", 866, 536, 74, 24, { size: 22, bold: true, color: C.teal, align: "center" });
circle("reeval-deferred", "?", 828, 574, 50, C.white, C.teal, C.teal, 25);
circle("reeval-gold", "B", 950, 574, 56, C.white, C.teal, C.teal, 27);
text("reeval-deferred-label", "deferred", 782, 598, 92, 22, { size: 22, bold: true, color: C.teal, align: "center" });
text("reeval-gold-label", "gold", 920, 602, 60, 20, { size: 22, bold: true, color: C.teal, align: "center" });
round("core-conclusion", 664, 646, 328, 58, `${C.amber}/42`, C.amber, 1.8, 12);
text("core-conclusion-text", "Same transition + opposite golds\nmake selective re-resolution measurable", 676, 654, 304, 42, { size: 22, bold: true, italic: true, color: C.ink, align: "center" });

// Panel B / Step 4: controller execution and consequence chain.
stepTitle(4, "RUN BOTH MEMBERS", 1084, 94, 300, C.blue);
text("run-same-interface", "same states, tools, and controller interface", 1092, 137, 444, 30, { size: 22, italic: true, color: C.blue, align: "center" });
round("input-p", 1088, 240, 88, 52, `${C.coral}/8`, C.coral, 1.8, 10);
text("input-p-text", "P", 1088, 245, 88, 42, { size: 28, bold: true, color: C.coral, align: "center" });
round("input-r", 1088, 328, 88, 52, `${C.teal}/8`, C.teal, 1.8, 10);
text("input-r-text", "R", 1088, 333, 88, 42, { size: 28, bold: true, color: C.teal, align: "center" });
round("controller-chip", 1184, 190, 188, 254, `${C.blue}/6`, C.blue, 2.4, 18);
robot("controller-robot", 1230, 218, C.blue);
text("controller-label", "CONTROLLER\nPROBE", 1198, 302, 160, 60, { size: 22, bold: true, color: C.blue, align: "center" });
line("controller-rule", 1206, 372, 144, 0, C.olive, 1.4);
text("controller-io", "instruction + history", 1196, 378, 164, 24, { size: 22, bold: true, align: "center" });
text("controller-target", "selected ID", 1202, 405, 152, 24, { size: 22, bold: true, color: C.blue, align: "center" });
circle("output-p", "T_P", 1484, 280, 66, C.white, C.coral, C.coral, 24);
circle("output-r", "T_R", 1484, 368, 66, C.white, C.teal, C.teal, 24);
text("output-p-gold", "gold A", 1446, 313, 76, 22, { size: 22, bold: true, color: C.coral, align: "center" });
text("output-r-gold", "gold B", 1446, 401, 76, 22, { size: 22, bold: true, color: C.teal, align: "center" });

database("selected-id-db", 1182, 438, C.blue, "ID");
round("action-tool", 1326, 441, 92, 70, `${C.amber}/18`, C.amber, 2, 12);
text("action-tool-label", "WRITE", 1334, 452, 76, 46, { size: 22, bold: true, color: C.ink, align: "center" });
database("final-state-db", 1466, 438, C.green, "S1+");
text("consequence-label", "target-to-write consequence", 1150, 521, 386, 28, { size: 22, bold: true, italic: true, color: C.blue, align: "center" });

// Three endpoint rows use distinct pictograms instead of three repeated cards.
line("metric-divider", 1086, 558, 456, 0, C.olive, 1.3, "dashed");
rect("step-5-badge", 1372, 560, 32, 32, C.blue, C.blue, 0);
text("step-5-number", "5", 1372, 560, 32, 32, { size: 22, bold: true, color: C.white, align: "center" });
text("step-5-label", "READOUTS", 1412, 560, 116, 32, { size: 22, bold: true, italic: true, color: C.blue, align: "center" });
circle("metric-pair-a", "A", 1112, 586, 34, C.white, C.coral, C.coral, 18);
circle("metric-pair-b", "B", 1144, 586, 34, C.white, C.teal, C.teal, 18);
text("metric-pair", "PairAcc", 1172, 564, 124, 30, { size: 23, bold: true, color: C.ink });
text("metric-pair-desc", "both pair members correct", 1172, 592, 334, 28, { size: 22, bold: true, color: C.blue });

circle("metric-sub-a", "A", 1120, 642, 38, C.white, C.coral, C.coral, 19);
arrow("metric-sub-arrow", 1142, 634, 58, 16, C.coral);
circle("metric-sub-b", "B", 1224, 642, 38, C.white, C.coral, C.coral, 19);
text("metric-sub", "Conditional substitution", 1260, 619, 270, 30, { size: 23, bold: true, color: C.ink });
text("metric-sub-desc", "B replaces valid bound A", 1260, 647, 270, 28, { size: 22, bold: true, color: C.coral });

addShape("can", "metric-write-db", { left: 1100, top: 688, width: 54, height: 46 }, `${C.green}/10`, C.green, 2);
text("metric-write", "Executed state diff", 1172, 682, 210, 30, { size: 23, bold: true, color: C.ink });
text("metric-write-desc", "which entity received the action", 1172, 710, 354, 26, { size: 22, bold: true, color: C.green });

slide.speakerNotes.textFrame.setText(
  "[Sources]\n" +
  "- Internal manuscript: paper/AnonymousSubmission2027.tex (Diagnostic Construction; Measurements and Denominators; Controller Probes).\n" +
  "- User-supplied visual references: GSD problem/method overview; SymPareto comparative framework; MetaEval multi-step framework. Used for hierarchy and scientific-illustration grammar only; no artwork copied.\n" +
  "- Palette: #264a56, #407a7f, #248d82, #60aa84, #b4b87f, #eabc6b, #f1a464, #e56d4e."
);

await fs.mkdir(OUT, { recursive: true });
const stem = "fig2_tri_diagnostic_workflow_v6";
async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}
await writeBlob(path.join(OUT, `${stem}.png`), await deck.export({ slide, format: "png", scale: 2 }));
await fs.writeFile(path.join(OUT, `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
const inspection = await deck.inspect({ kind: "slide,textbox,shape,notes", maxChars: 40000 });
await fs.writeFile(path.join(OUT, `${stem}.inspect.ndjson`), inspection.ndjson);
const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(path.join(OUT, `${stem}.pptx`));
