import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/chu/Documents/Codex/2026-07-15/k-y/TRI";
const TMP = path.join(ROOT, "tmp", "tri_method_figure_v1");
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

const presentation = Presentation.create({ slideSize: { width: 1600, height: 780 } });
const slide = presentation.slides.add();
slide.background.fill = C.white;

function shape(geometry, name, left, top, width, height, fill = "none", lineFill = "none", lineWidth = 0) {
  return slide.shapes.add({
    geometry,
    name,
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
  });
}

function textBox(name, text, left, top, width, height, opts = {}) {
  const s = shape("textbox", name, left, top, width, height, "none", "none", 0);
  s.text = text;
  s.text.style = {
    typeface: "Arial",
    fontSize: opts.size ?? 26,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    color: opts.color ?? C.ink,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
    autoFit: "shrinkText",
    wrap: "square",
    lineSpacing: opts.lineSpacing ?? 0.95,
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return s;
}

function line(name, left, top, width, height, color = C.blue, lineWidth = 2, style = "solid") {
  return slide.shapes.add({
    geometry: "line",
    name,
    position: { left, top, width, height },
    fill: "none",
    line: { style, fill: color, width: lineWidth },
  });
}

function roundRect(name, left, top, width, height, fill, stroke, strokeWidth = 2, radius = 16) {
  const s = shape("roundRect", name, left, top, width, height, fill, stroke, strokeWidth);
  s.borderRadius = radius;
  return s;
}

function circle(name, label, cx, cy, diameter, fill, stroke, textColor = C.ink, fontSize = 28) {
  const s = shape("ellipse", name, cx - diameter / 2, cy - diameter / 2, diameter, diameter, fill, stroke, 2.4);
  s.text = label;
  s.text.style = {
    typeface: "Arial",
    fontSize,
    bold: true,
    color: textColor,
    alignment: "center",
    verticalAlignment: "middle",
    autoFit: "shrinkText",
    insets: { top: 0, right: 0, bottom: 0, left: 0 },
  };
  return s;
}

function rightArrow(name, left, top, width, height, fill) {
  return shape("rightArrow", name, left, top, width, height, fill, fill, 0.5);
}

function stageHeader(number, label, x, width, color) {
  circle(`stage-${number}`, String(number), x + 18, 140, 36, color, color, C.white, 23);
  textBox(`stage-label-${number}`, label, x + 48, 120, width - 48, 40, {
    size: 24,
    bold: true,
    color: C.ink,
    valign: "middle",
  });
}

function clipboardIcon(name, x, y, color) {
  roundRect(`${name}-paper`, x, y, 30, 36, C.white, color, 1.8, 5);
  roundRect(`${name}-clip`, x + 8, y - 4, 14, 8, color, color, 0, 3);
  circle(`${name}-dot-1`, "", x + 8, y + 13, 5, color, color, color, 1);
  circle(`${name}-dot-2`, "", x + 8, y + 25, 5, color, color, color, 1);
  line(`${name}-line-1`, x + 14, y + 13, 10, 0, color, 1.6);
  line(`${name}-line-2`, x + 14, y + 25, 10, 0, color, 1.6);
}

function robotIcon(name, x, y, color) {
  line(`${name}-antenna`, x + 28, y - 10, 0, 11, color, 1.8);
  circle(`${name}-antenna-tip`, "", x + 28, y - 12, 6, color, color, color, 1);
  roundRect(`${name}-head`, x, y, 56, 42, C.white, color, 2, 10);
  circle(`${name}-eye-1`, "", x + 18, y + 18, 7, color, color, color, 1);
  circle(`${name}-eye-2`, "", x + 38, y + 18, 7, color, color, color, 1);
  line(`${name}-mouth`, x + 19, y + 31, 18, 0, color, 1.8);
}

function pairIcon(name, x, y) {
  circle(`${name}-q`, "q", x, y, 28, C.white, C.white, C.teal, 16);
  line(`${name}-trunk`, x + 14, y, 18, 0, C.white, 1.8);
  line(`${name}-split`, x + 32, y - 18, 0, 36, C.white, 1.8);
  line(`${name}-branch-a`, x + 32, y - 18, 4, 0, C.white, 1.8);
  line(`${name}-branch-b`, x + 32, y + 18, 4, 0, C.white, 1.8);
  circle(`${name}-a`, "A", x + 48, y - 18, 24, C.white, C.white, C.coral, 14);
  circle(`${name}-b`, "B", x + 48, y + 18, 24, C.white, C.white, C.teal, 14);
}

// Connectors are created first so all semantic nodes sit above them.
rightArrow("flow-1", 325, 322, 58, 22, C.olive);
rightArrow("flow-2", 695, 322, 58, 22, C.olive);
rightArrow("flow-3", 1192, 322, 50, 22, C.olive);
rightArrow("state-refresh", 500, 266, 78, 24, C.amber);
rightArrow("preserve-flow-1", 938, 251, 42, 18, C.coral);
rightArrow("preserve-flow-2", 1026, 251, 61, 18, C.coral);
rightArrow("reeval-flow-1", 938, 390, 42, 18, C.teal);
rightArrow("reeval-flow-2", 1026, 390, 61, 18, C.teal);
rightArrow("controller-output-p", 1390, 412, 45, 15, C.coral);
rightArrow("controller-output-r", 1390, 462, 45, 15, C.teal);

// Global title and rule.
textBox("title", "TRI converts one controlled transition into a matched diagnostic", 44, 22, 1512, 48, {
  size: 37,
  bold: true,
  color: C.ink,
});
textBox("subtitle", "Hold the world fixed; vary only when the action target becomes committed.", 46, 69, 1470, 30, {
  size: 24,
  bold: true,
  color: C.teal,
});
line("title-rule", 44, 108, 1512, 0, C.ink, 2.5);

// Flat stage zones, with a soft spotlight around the diagnostic core.
roundRect("core-spotlight", 734, 116, 476, 418, `${C.teal}/7`, `${C.teal}/55`, 2.2, 22);
line("sep-1", 354, 124, 0, 402, C.olive, 1.4, "dashed");
line("sep-2", 724, 124, 0, 402, C.olive, 1.4, "dashed");
line("sep-3", 1214, 124, 0, 402, C.olive, 1.4, "dashed");
stageHeader(1, "TASK SPECIFICATION", 44, 294, C.ink);
stageHeader(2, "CONTROLLED TRANSITION", 378, 326, C.amber);
roundRect("stage-3-core-header", 750, 120, 438, 44, C.teal, C.teal, 0, 14);
textBox("stage-3-core-label", "CORE 3   MATCHED PAIR", 770, 124, 300, 36, {
  size: 24,
  bold: true,
  color: C.white,
});
pairIcon("stage-3-pair-icon", 1110, 142);
stageHeader(4, "SAME CONTROLLER", 1236, 316, C.blue);

// Stage 1: compact, source-like task specification.
textBox("entity-table-label", "Entities + resolver", 58, 174, 220, 30, { size: 24, bold: true });
clipboardIcon("task-spec-icon", 292, 170, C.blue);
roundRect("entity-table-frame", 58, 210, 264, 124, `${C.blue}/4`, C.blue, 1.8, 10);
shape("rect", "entity-table-header", 58, 210, 264, 34, C.blue, C.blue, 0);
textBox("entity-head-id", "ID", 70, 211, 44, 31, { size: 21, bold: true, color: C.white, align: "center" });
textBox("entity-head-s0", "rank S0", 112, 211, 72, 31, { size: 21, bold: true, color: C.white, align: "center" });
textBox("entity-head-s1", "rank S1", 184, 211, 72, 31, { size: 21, bold: true, color: C.white, align: "center" });
textBox("entity-head-valid", "valid", 256, 211, 54, 31, { size: 21, bold: true, color: C.white, align: "center" });
line("entity-mid-1", 58, 273, 264, 0, C.olive, 1.1);
line("entity-v-1", 110, 210, 0, 124, C.olive, 1.1);
line("entity-v-2", 184, 210, 0, 124, C.olive, 1.1);
line("entity-v-3", 256, 210, 0, 124, C.olive, 1.1);
textBox("entity-a", "A", 70, 242, 28, 30, { size: 25, bold: true, color: C.coral, align: "center" });
textBox("entity-a-s0", "1", 126, 242, 44, 30, { size: 24, bold: true, align: "center" });
textBox("entity-a-s1", "2", 198, 242, 44, 30, { size: 24, align: "center" });
textBox("entity-a-valid", "yes", 264, 242, 40, 30, { size: 22, bold: true, color: C.green, align: "center" });
textBox("entity-b", "B", 70, 278, 28, 30, { size: 25, bold: true, color: C.teal, align: "center" });
textBox("entity-b-s0", "2", 126, 278, 44, 30, { size: 24, align: "center" });
textBox("entity-b-s1", "1", 198, 278, 44, 30, { size: 24, bold: true, align: "center" });
textBox("entity-b-valid", "yes", 264, 278, 40, 30, { size: 22, bold: true, color: C.green, align: "center" });
textBox("selector", "selector q: highest-priority unread", 58, 354, 278, 54, { size: 23, bold: true, color: C.ink });
textBox("action", "action a: reply(entity)", 58, 412, 278, 34, { size: 23, bold: true, color: C.blue });
textBox("precondition", "precondition: old target remains actionable", 58, 454, 278, 53, { size: 22, color: C.ink });

// Stage 2: identical states shared across both members.
textBox("transition-note", "Same S0, S1, q, and action", 394, 174, 294, 32, { size: 24, bold: true, align: "center" });
roundRect("s0-frame", 392, 222, 122, 142, C.white, C.coral, 2.2, 14);
roundRect("s1-frame", 574, 222, 122, 142, C.white, C.teal, 2.2, 14);
textBox("s0-title", "S0  BEFORE", 401, 232, 104, 28, { size: 22, bold: true, align: "center" });
textBox("s1-title", "S1  AFTER", 583, 232, 104, 28, { size: 22, bold: true, align: "center" });
circle("s0-a", "A", 453, 301, 62, C.white, C.coral, C.coral, 30);
circle("s1-b", "B", 635, 301, 62, C.white, C.teal, C.teal, 30);
textBox("s0-winner", "winner", 407, 337, 92, 24, { size: 20, bold: true, color: C.coral, align: "center" });
textBox("s1-winner", "winner", 589, 337, 92, 24, { size: 20, bold: true, color: C.teal, align: "center" });
textBox("refresh-label", "REFRESH", 506, 235, 68, 28, { size: 19, bold: true, color: C.ink, align: "center" });
roundRect("validity-band", 402, 390, 284, 72, `${C.green}/6`, C.green, 2, 12);
textBox("validity-main", "A stays present and action-valid", 416, 397, 256, 28, { size: 22, bold: true, color: C.ink, align: "center" });
textBox("validity-sub", "Only the selector winner changes: A -> B", 416, 429, 256, 27, { size: 20, bold: true, color: C.green, align: "center" });
textBox("controlled-tag", "controlled contrast", 439, 476, 208, 30, { size: 21, italic: true, color: C.blue, align: "center" });

// Stage 3: paired instruction timing with redundant solid/dashed identity threads.
textBox("pair-note", "Instruction timing chooses the gold target", 768, 174, 398, 32, { size: 24, bold: true, align: "center" });
roundRect("preserve-lane", 768, 214, 398, 112, `${C.coral}/5`, C.coral, 2.2, 14);
shape("rect", "preserve-stripe", 768, 214, 9, 112, C.coral, C.coral, 0);
textBox("preserve-title", "PRESERVE", 788, 220, 154, 28, { size: 23, bold: true, color: C.coral });
textBox("preserve-sub", "bind before refresh", 788, 249, 150, 42, { size: 20, bold: true, color: C.ink });
circle("preserve-q", "q", 1000, 260, 52, C.white, C.coral, C.coral, 25);
circle("preserve-a", "A", 1116, 260, 58, C.white, C.coral, C.coral, 28);
textBox("preserve-eq", "q(S0)=A", 958, 292, 84, 24, { size: 20, bold: true, color: C.coral, align: "center" });
textBox("preserve-gold", "gold A", 1079, 292, 74, 24, { size: 20, bold: true, color: C.coral, align: "center" });
roundRect("reevaluate-lane", 768, 350, 398, 112, `${C.teal}/5`, C.teal, 2.2, 14);
shape("rect", "reevaluate-stripe", 768, 350, 9, 112, C.teal, C.teal, 0);
textBox("reevaluate-title", "REEVALUATE", 788, 356, 164, 28, { size: 22, bold: true, color: C.teal });
textBox("reevaluate-sub", "defer until after refresh", 788, 385, 150, 48, { size: 20, bold: true, color: C.ink });
circle("reevaluate-q", "q", 1000, 399, 52, C.white, C.teal, C.teal, 25);
circle("reevaluate-b", "B", 1116, 399, 58, C.white, C.teal, C.teal, 28);
textBox("reevaluate-eq", "q(S1)=B", 958, 431, 84, 24, { size: 20, bold: true, color: C.teal, align: "center" });
textBox("reevaluate-gold", "gold B", 1079, 431, 74, 24, { size: 20, bold: true, color: C.teal, align: "center" });
textBox("matched-foot", "Opposite golds; all task content is shared", 792, 480, 350, 30, { size: 21, bold: true, color: C.blue, align: "center" });

// Stage 4: controller is a probe, not claimed as the method.
textBox("controller-note", "Run both members under one interface", 1250, 174, 288, 54, { size: 23, bold: true, align: "center" });
roundRect("controller-box", 1270, 238, 248, 146, `${C.blue}/6`, C.blue, 2.4, 18);
robotIcon("controller-robot", 1366, 250, C.blue);
textBox("controller-title", "CONTROLLER PROBE", 1290, 294, 208, 30, { size: 23, bold: true, color: C.blue, align: "center" });
line("controller-divider", 1290, 328, 208, 0, C.olive, 1.4);
textBox("controller-input", "instruction + state history  ->  selected target ID", 1292, 337, 204, 40, { size: 20, bold: true, color: C.ink, align: "center" });
textBox("tp-label", "Preserve output", 1248, 398, 136, 34, { size: 20, bold: true, color: C.coral });
circle("tp-node", "T_P", 1472, 421, 58, C.white, C.coral, C.coral, 22);
textBox("tr-label", "Reevaluate output", 1248, 448, 142, 34, { size: 20, bold: true, color: C.teal });
circle("tr-node", "T_R", 1472, 471, 58, C.white, C.teal, C.teal, 22);
textBox("controller-boundary", "Probe the decision; do not assume an internal mechanism", 1252, 500, 292, 30, { size: 19, italic: true, color: C.blue, align: "center" });

// Bottom scoring band.
shape("rect", "score-band-bg", 44, 548, 1512, 188, C.white, C.ink, 2.2);
shape("rect", "score-band-head", 44, 548, 1512, 42, C.ink, C.ink, 0);
textBox("score-band-title", "SCORING: separate joint correctness, post-binding substitution, and executed consequence", 62, 552, 1474, 34, {
  size: 24,
  bold: true,
  color: C.white,
  align: "center",
});
line("score-sep-1", 552, 590, 0, 146, C.olive, 1.4);
line("score-sep-2", 1058, 590, 0, 146, C.olive, 1.4);

// PairAcc block.
circle("metric-one", "1", 82, 624, 34, C.blue, C.blue, C.white, 21);
textBox("metric-one-title", "CHANGED-WINNER PairAcc", 108, 602, 410, 38, { size: 24, bold: true, color: C.blue });
textBox("metric-one-formula", "1 only if  T_P = A  AND  T_R = B", 72, 648, 444, 34, { size: 24, bold: true, color: C.ink, align: "center" });
textBox("metric-one-note", "Rejects Always-Lock and Always-Reevaluate jointly", 72, 688, 444, 30, { size: 21, color: C.ink, align: "center" });

// Conditional substitution block.
circle("metric-two", "2", 590, 624, 34, C.orange, C.orange, C.white, 21);
textBox("metric-two-title", "CONDITIONAL SUBSTITUTION", 616, 602, 410, 38, { size: 24, bold: true, color: C.ink });
textBox("metric-two-formula", "Preserve: correct bind A  ->  final target B", 580, 648, 448, 34, { size: 23, bold: true, color: C.coral, align: "center" });
textBox("metric-two-note", "Counts replacement only when A remains valid", 580, 688, 448, 30, { size: 21, color: C.ink, align: "center" });

// Executed consequence block.
circle("metric-three", "3", 1096, 624, 34, C.green, C.green, C.white, 21);
textBox("metric-three-title", "EXECUTED STATE DIFF", 1122, 602, 402, 38, { size: 24, bold: true, color: C.ink });
textBox("metric-three-formula", "selected ID  ->  model-issued write  ->  final state", 1086, 648, 444, 34, { size: 23, bold: true, color: C.green, align: "center" });
textBox("metric-three-note", "Localizes which entity actually received the action", 1086, 688, 444, 30, { size: 21, color: C.ink, align: "center" });

slide.speakerNotes.textFrame.setText(
  "[Sources]\n" +
  "- Internal manuscript: paper/AnonymousSubmission2027.tex, especially Diagnostic Construction, Measurements and Denominators, and Controller Probes.\n" +
  "- Internal visual references: draw_learning/*.pdf. Layout adapted at the level of hierarchy and reading order; no external artwork reused.\n" +
  "- User-supplied palette: #264a56, #407a7f, #248d82, #60aa84, #b4b87f, #eabc6b, #f1a464, #e56d4e."
);

await fs.mkdir(TMP, { recursive: true });
await fs.mkdir(OUT, { recursive: true });

async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

const stem = "fig2_tri_diagnostic_workflow_v2";
const png = await presentation.export({ slide, format: "png", scale: 2 });
await writeBlob(path.join(OUT, `${stem}.png`), png);
const layout = await slide.export({ format: "layout" });
await fs.writeFile(path.join(OUT, `${stem}.layout.json`), await layout.text());
const inspect = await presentation.inspect({ kind: "slide,textbox,shape,notes", maxChars: 30000 });
await fs.writeFile(path.join(OUT, `${stem}.inspect.ndjson`), inspect.ndjson);
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(path.join(OUT, `${stem}.pptx`));
