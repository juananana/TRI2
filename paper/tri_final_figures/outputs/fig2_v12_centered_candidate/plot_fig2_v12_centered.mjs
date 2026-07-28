import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT = process.argv[2] || path.resolve("output");
const W = 1600;
const H = 960;

const C = {
  ink: "#28343A",
  text: "#30343F",
  muted: "#69787E",
  rule: "#B9C3C5",
  soft: "#F7F9F9",
  coral: "#B94D49",
  coralLight: "#F7E7E3",
  teal: "#2D7F7B",
  tealLight: "#E5F1EF",
  blue: "#66899D",
  blueLight: "#EDF3F5",
  white: "#FFFFFF",
  grayNode: "#F1F3F3",
};

async function writeBlob(filename, blob) {
  await fs.writeFile(filename, new Uint8Array(await blob.arrayBuffer()));
}

function addText(slide, name, text, x, y, w, h, opts = {}) {
  const s = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: opts.fill ?? "none",
    line: { style: "solid", fill: opts.line ?? "none", width: opts.lineWidth ?? 0 },
  });
  s.text = text;
  s.text.style = {
    fontFamily: opts.font ?? "Arial",
    fontSize: opts.size ?? 18,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    color: opts.color ?? C.text,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
  };
  return s;
}

function addBox(slide, name, x, y, w, h, opts = {}) {
  const geometry = opts.geometry ?? "roundRect";
  const s = slide.shapes.add({
    geometry,
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: opts.fill ?? C.white,
    line: {
      style: opts.style ?? "solid",
      fill: opts.line ?? C.rule,
      width: opts.lineWidth ?? 1.2,
    },
  });
  if (geometry === "roundRect") s.borderRadius = opts.radius ?? "rounded-lg";
  return s;
}

function addCircle(slide, name, label, x, y, d, opts = {}) {
  const s = slide.shapes.add({
    geometry: "ellipse",
    name,
    position: { left: x, top: y, width: d, height: d },
    fill: opts.fill ?? C.white,
    line: {
      style: opts.style ?? "solid",
      fill: opts.line ?? C.ink,
      width: opts.lineWidth ?? 1.7,
    },
  });
  if (label) {
    s.text = label;
    s.text.style = {
      fontFamily: opts.font ?? "Arial",
      fontSize: opts.size ?? 18,
      bold: opts.bold ?? true,
      color: opts.color ?? opts.line ?? C.ink,
      alignment: "center",
      verticalAlignment: "middle",
    };
  }
  return s;
}

function connect(slide, from, to, opts = {}) {
  const connector = slide.shapes.connect(from, to, {
    kind: opts.kind ?? "straight",
    fromSide: opts.fromSide ?? "right",
    toSide: opts.toSide ?? "left",
    line: {
      style: opts.style ?? "solid",
      fill: opts.color ?? C.ink,
      width: opts.width ?? 2.5,
    },
    cap: "round",
    join: "round",
    head: { type: "none" },
    tail: opts.arrow === false
      ? { type: "none" }
      : { type: opts.arrowType ?? "stealth", width: opts.arrowWidth ?? "med", length: "med" },
  });
  connector.bringToFront();
  return connector;
}

function addPhaseTitle(slide, letter, title, x, y, w, color = C.ink) {
  addCircle(slide, `phase-${letter}`, letter, x, y, 34, {
    fill: color,
    line: color,
    color: C.white,
    size: 16,
  });
  addText(slide, `phase-${letter}-title`, title, x + 46, y - 2, w - 46, 38, {
    size: 24,
    bold: true,
    color: "#111719",
  });
}

function addClock(slide, name, x, y, d, color = C.ink, fill = C.white) {
  const face = addCircle(slide, `${name}-face`, "", x, y, d, {
    fill,
    line: color,
    lineWidth: 2,
  });
  addBox(slide, `${name}-hand-v`, x + d * 0.49, y + d * 0.18, 2, d * 0.32, {
    geometry: "rect", fill: color, line: color, lineWidth: 0,
  });
  addBox(slide, `${name}-hand-h`, x + d * 0.49, y + d * 0.49, d * 0.23, 2, {
    geometry: "rect", fill: color, line: color, lineWidth: 0,
  });
  addCircle(slide, `${name}-hub`, "", x + d * 0.44, y + d * 0.44, d * 0.12, {
    fill: color, line: color, lineWidth: 0,
  });
  return face;
}

function addLock(slide, name, x, y, color, fill) {
  addCircle(slide, `${name}-shackle`, "", x + 6, y, 28, {
    fill: "none", line: color, lineWidth: 2.2,
  });
  addBox(slide, `${name}-body`, x, y + 13, 40, 31, {
    fill, line: color, lineWidth: 2, radius: "rounded-md",
  });
  addCircle(slide, `${name}-key`, "", x + 17, y + 22, 7, {
    fill: color, line: color, lineWidth: 0,
  });
}

function addState(slide, prefix, x, y, withB, accent) {
  const outer = addCircle(slide, `${prefix}-state`, "", x, y, 112, {
    fill: C.white,
    line: C.ink,
    lineWidth: 1.6,
  });
  const dots = [[22, 25], [50, 17], [18, 62], [50, 76]];
  for (const [i, [dx, dy]] of dots.entries()) {
    addCircle(slide, `${prefix}-other-${i}`, "", x + dx, y + dy, 16, {
      fill: C.grayNode, line: C.muted, lineWidth: 0.8,
    });
  }
  addCircle(slide, `${prefix}-a`, "A", x + 68, y + 52, 31, {
    fill: C.coral, line: C.coral, color: C.white, size: 16,
  });
  if (withB) {
    addCircle(slide, `${prefix}-b`, "B", x + 67, y + 17, 31, {
      fill: C.teal, line: C.teal, color: C.white, size: 16,
    });
  }
  addCircle(slide, `${prefix}-accent`, "", x + 101, y + 5, 7, {
    fill: accent, line: accent, lineWidth: 0,
  });
  return outer;
}

function addTarget(slide, name, label, x, y, color) {
  const target = addCircle(slide, `${name}-outer`, label, x, y, 58, {
    fill: C.white, line: color, lineWidth: 2.6, color, size: 22,
  });
  addBox(slide, `${name}-h`, x - 9, y + 28, 76, 2, {
    geometry: "rect", fill: color, line: color, lineWidth: 0,
  });
  addBox(slide, `${name}-v`, x + 28, y - 9, 2, 76, {
    geometry: "rect", fill: color, line: color, lineWidth: 0,
  });
  return target;
}

function addSpark(slide, name, x, y, color) {
  addBox(slide, `${name}-a`, x, y + 8, 15, 2, { geometry: "rect", fill: color, line: color, lineWidth: 0 });
  addBox(slide, `${name}-b`, x + 13, y, 2, 10, { geometry: "rect", fill: color, line: color, lineWidth: 0 });
  const dot = addCircle(slide, `${name}-c`, "", x + 19, y + 12, 5, { fill: color, line: color, lineWidth: 0 });
  return dot;
}

function addReadoutNumber(slide, n, x, y, color) {
  return addCircle(slide, `readout-${n}-num`, String(n), x, y, 34, {
    fill: C.white, line: color, lineWidth: 2, color, size: 16,
  });
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const slide = presentation.slides.add();
  slide.background.fill = C.white;

  // Quiet stage boundaries retain the A/B/C reading order without dashboard panels.
  addBox(slide, "stage-divider-ab", 822, 28, 1, 900, { geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0 });
  addBox(slide, "stage-divider-bc", 1130, 28, 1, 900, { geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0 });
  addPhaseTitle(slide, "A", "Construct the matched pair", 28, 24, 760, C.ink);
  addPhaseTitle(slide, "B", "Run the pair", 846, 24, 260, C.blue);
  addPhaseTitle(slide, "C", "Read the evidence", 1154, 24, 412, C.ink);

  // A. Pair contract: concise, explicit, and visually subordinate to the pair itself.
  addBox(slide, "pair-contract", 28, 78, 766, 124, { fill: C.soft, line: C.rule, lineWidth: 1.1 });
  addText(slide, "fixed-label", "FIXED ACROSS BOTH ROWS", 48, 89, 276, 24, { size: 12, bold: true, color: C.blue });
  addText(slide, "fixed-items", "S0, S1, q, action, schema, controller interface", 48, 114, 716, 29, { size: 17, bold: true });
  addText(slide, "changed-label", "ONLY CHANGE", 48, 153, 126, 24, { size: 12, bold: true, color: C.teal });
  addText(slide, "changed-items", "instruction commitment timing", 170, 150, 280, 28, { size: 17, bold: true, color: C.teal });
  addText(slide, "transition", "q(S0)=A   ->   refresh   ->   q(S1)=B", 440, 148, 336, 30, {
    size: 16, bold: true, font: "Times New Roman", align: "center",
  });
  addBox(slide, "old-target-valid", 450, 180, 322, 30, { fill: C.blueLight, line: C.blue, lineWidth: 1.2 });
  addText(slide, "old-target-valid-text", "A still exists and remains action-valid in S1", 459, 181, 304, 26, {
    size: 12, italic: true, align: "center",
  });

  // A. The matched pair is the dominant visual thesis.
  addBox(slide, "pair-field", 28, 232, 766, 570, { fill: C.white, line: C.rule, lineWidth: 1.2 });
  addBox(slide, "pair-badge", 41, 426, 46, 176, { fill: C.ink, line: C.ink, lineWidth: 0, radius: "rounded-lg" });
  addText(slide, "pair-badge-text", "M\nA\nT\nC\nH\nE\nD", 49, 436, 30, 154, { size: 12, bold: true, color: C.white, align: "center" });
  addCircle(slide, "pair-link-top", "", 80, 348, 11, { fill: C.coral, line: C.white, lineWidth: 1 });
  addCircle(slide, "pair-link-bottom", "", 80, 634, 11, { fill: C.teal, line: C.white, lineWidth: 1 });
  addBox(slide, "pair-link-stem", 84, 358, 3, 276, { geometry: "rect", fill: C.ink, line: C.ink, lineWidth: 0 });

  // Preserve row.
  addBox(slide, "preserve-row-bg", 104, 258, 672, 246, { fill: C.coralLight, line: C.coral, lineWidth: 1.5 });
  addLock(slide, "preserve-lock", 121, 278, C.coral, C.white);
  addText(slide, "preserve-title", "Preserve", 171, 272, 122, 31, { size: 20, bold: true, color: C.coral });
  addText(slide, "preserve-rule", "bind A before refresh", 171, 303, 186, 28, { size: 14, bold: true, color: C.coral });
  const pS0 = addState(slide, "preserve-s0", 162, 347, false, C.coral);
  addText(slide, "preserve-s0-label", "S0   q(S0) = A", 152, 457, 132, 30, { size: 16, italic: true, font: "Times New Roman", align: "center" });
  addText(slide, "preserve-bound", "BOUND A", 300, 375, 82, 26, { size: 13, bold: true, color: C.coral, align: "center", line: C.coral, lineWidth: 1.2 });
  const pGate = addClock(slide, "preserve-gate-anchor", 416, 379, 44, C.blue, C.white);
  const pS1 = addState(slide, "preserve-s1", 514, 347, true, C.coral);
  addText(slide, "preserve-s1-label", "S1   q(S1) = B", 504, 457, 132, 30, { size: 16, italic: true, font: "Times New Roman", align: "center" });
  const pTarget = addTarget(slide, "preserve-target", "A", 692, 380, C.coral);
  addText(slide, "preserve-target-label", "execute on A", 667, 452, 110, 29, { size: 15, bold: true, color: C.coral, align: "center" });
  connect(slide, pS0, pGate, { color: C.coral, width: 3.3, kind: "curved" });
  connect(slide, pGate, pS1, { color: C.coral, width: 3.3, kind: "curved" });
  connect(slide, pS1, pTarget, { color: C.coral, width: 3.3, kind: "curved" });
  addSpark(slide, "preserve-spark", 753, 367, C.coral);

  // Reevaluate row.
  addBox(slide, "reevaluate-row-bg", 104, 520, 672, 246, { fill: C.tealLight, line: C.teal, lineWidth: 1.5, style: "dashed" });
  addClock(slide, "reevaluate-clock", 121, 542, 42, C.teal, C.white);
  addText(slide, "reevaluate-title", "Reevaluate", 171, 536, 145, 31, { size: 20, bold: true, color: C.teal });
  addText(slide, "reevaluate-rule", "defer q until after refresh", 171, 567, 205, 28, { size: 14, bold: true, color: C.teal });
  const rS0 = addState(slide, "reevaluate-s0", 162, 609, false, C.teal);
  addText(slide, "reevaluate-s0-label", "S0   q(S0) = A", 152, 719, 132, 30, { size: 16, italic: true, font: "Times New Roman", align: "center" });
  addText(slide, "reevaluate-deferred", "DEFER q", 300, 638, 82, 26, { size: 13, bold: true, color: C.teal, align: "center", line: C.teal, lineWidth: 1.2 });
  const rGate = addClock(slide, "reevaluate-gate-anchor", 416, 641, 44, C.blue, C.white);
  const rS1 = addState(slide, "reevaluate-s1", 514, 609, true, C.teal);
  addText(slide, "reevaluate-s1-label", "S1   q(S1) = B", 504, 719, 132, 30, { size: 16, italic: true, font: "Times New Roman", align: "center" });
  addText(slide, "reevaluate-resolve", "resolve q on S1", 595, 588, 102, 28, { size: 13, bold: true, color: C.teal, align: "center" });
  const rTarget = addTarget(slide, "reevaluate-target", "B", 692, 642, C.teal);
  addText(slide, "reevaluate-target-label", "execute on B", 667, 714, 110, 29, { size: 15, bold: true, color: C.teal, align: "center" });
  connect(slide, rS0, rGate, { color: C.teal, width: 3.3, kind: "curved", style: "dashed" });
  connect(slide, rGate, rS1, { color: C.teal, width: 3.3, kind: "curved", style: "dashed" });
  connect(slide, rS1, rTarget, { color: C.teal, width: 3.3, kind: "curved", style: "dashed" });
  addSpark(slide, "reevaluate-spark", 753, 629, C.teal);
  // Shared refresh tab sits above both lane fills and visually binds the two replayed gates.
  addBox(slide, "refresh-chip", 330, 240, 214, 34, { fill: C.blueLight, line: C.blue, lineWidth: 1.1 });
  addText(slide, "refresh-chip-text", "same refresh replayed in both rows", 340, 243, 194, 27, { size: 13, bold: true, color: C.blue, align: "center" });

  // Compact legend and one-sentence invariant, replacing the dashboard-like checklist.
  addCircle(slide, "legend-a", "A", 48, 835, 28, { fill: C.coral, line: C.coral, color: C.white, size: 14 });
  addText(slide, "legend-a-text", "initial winner", 82, 832, 104, 31, { size: 13 });
  addCircle(slide, "legend-b", "B", 194, 835, 28, { fill: C.teal, line: C.teal, color: C.white, size: 14 });
  addText(slide, "legend-b-text", "post-refresh winner", 228, 832, 145, 31, { size: 13 });
  addText(slide, "pair-invariant", "One matched pair = same world transition and interface; only commitment timing changes.", 388, 824, 394, 52, { size: 15, bold: true, color: C.ink, align: "center" });
  addText(slide, "line-semantics", "solid = Preserve     dashed = Reevaluate", 444, 876, 282, 26, { size: 13, color: C.muted, align: "center" });

  // B. A narrow bridge, not an architecture diagram.
  addBox(slide, "same-probe-chip", 846, 82, 260, 64, { fill: C.blueLight, line: C.blue, lineWidth: 1.2 });
  addText(slide, "same-probe-chip-text", "same controller + same interface", 860, 91, 232, 46, { size: 17, bold: true, align: "center" });
  addText(slide, "two-runs", "two independent runs", 865, 158, 222, 28, { size: 14, italic: true, color: C.muted, align: "center" });

  const pPacket = addBox(slide, "preserve-packet", 835, 258, 98, 82, { fill: C.coralLight, line: C.coral, lineWidth: 1.5 });
  addText(slide, "preserve-packet-text", "Preserve\nrow", 841, 266, 86, 64, { size: 13, bold: true, color: C.coral, align: "center" });
  const rPacket = addBox(slide, "reevaluate-packet", 835, 553, 98, 82, { fill: C.tealLight, line: C.teal, lineWidth: 1.5, style: "dashed" });
  addText(slide, "reevaluate-packet-text", "Reevaluate\nrow", 841, 561, 86, 64, { size: 10, bold: true, color: C.teal, align: "center" });

  const probe = addBox(slide, "controller-probe", 942, 228, 128, 442, { fill: C.soft, line: C.ink, lineWidth: 1.8 });
  addText(slide, "probe-title", "Controller\nprobe", 952, 258, 108, 68, { size: 17, bold: true, align: "center" });
  addCircle(slide, "probe-eye-p", "", 976, 351, 13, { fill: C.coral, line: C.white, lineWidth: 1 });
  addCircle(slide, "probe-eye-r", "", 1024, 351, 13, { fill: C.teal, line: C.white, lineWidth: 1 });
  addText(slide, "probe-blackbox", "BLACK BOX\ninternals unobserved", 952, 382, 108, 56, { size: 11, bold: true, color: C.muted, align: "center" });
  addText(slide, "probe-io", "instruction\n+ history\n+ observed state\n\n-> target ID", 951, 472, 110, 128, { size: 13, bold: true, align: "center" });

  const tp = addBox(slide, "tp", 1076, 270, 58, 58, { geometry: "ellipse", fill: C.white, line: C.coral, lineWidth: 2.1 });
  addText(slide, "tp-text", "T_P", 1082, 276, 46, 46, { size: 15, bold: true, italic: true, color: C.coral, font: "Times New Roman", align: "center" });
  const tr = addBox(slide, "tr", 1076, 568, 58, 58, { geometry: "ellipse", fill: C.white, line: C.teal, lineWidth: 2.1, style: "dashed" });
  addText(slide, "tr-text", "T_R", 1082, 574, 46, 46, { size: 15, bold: true, italic: true, color: C.teal, font: "Times New Roman", align: "center" });
  const pInAnchor = addCircle(slide, "probe-p-in-anchor", "", 940, 296, 4, { fill: "none", line: "none", lineWidth: 0 });
  const rInAnchor = addCircle(slide, "probe-r-in-anchor", "", 940, 590, 4, { fill: "none", line: "none", lineWidth: 0 });
  const pOutAnchor = addCircle(slide, "probe-p-out-anchor", "", 1068, 296, 4, { fill: "none", line: "none", lineWidth: 0 });
  const rOutAnchor = addCircle(slide, "probe-r-out-anchor", "", 1068, 590, 4, { fill: "none", line: "none", lineWidth: 0 });
  connect(slide, pPacket, pInAnchor, { color: C.coral, width: 3, kind: "curved" });
  connect(slide, pOutAnchor, tp, { color: C.coral, width: 3, kind: "curved" });
  connect(slide, rPacket, rInAnchor, { color: C.teal, width: 3, kind: "curved", style: "dashed" });
  connect(slide, rOutAnchor, tr, { color: C.teal, width: 3, kind: "curved", style: "dashed" });
  addCircle(slide, "probe-p-in-port", "", 937, 291, 12, { fill: C.coral, line: C.white, lineWidth: 1 });
  addCircle(slide, "probe-r-in-port", "", 937, 585, 12, { fill: C.teal, line: C.white, lineWidth: 1 });
  addCircle(slide, "probe-p-out-port", "", 1063, 291, 12, { fill: C.coral, line: C.white, lineWidth: 1 });
  addCircle(slide, "probe-r-out-port", "", 1063, 585, 12, { fill: C.teal, line: C.white, lineWidth: 1 });
  addText(slide, "tp-label", "final target", 1068, 332, 72, 24, { size: 12, align: "center" });
  addText(slide, "tr-label", "final target", 1068, 630, 72, 24, { size: 12, align: "center" });

  addBox(slide, "withheld-strip", 846, 706, 260, 194, { fill: C.white, line: C.rule, lineWidth: 1.1, style: "dashed" });
  addText(slide, "withheld-title", "Withheld from the probe", 860, 718, 232, 31, { size: 16, bold: true, align: "center" });
  addText(slide, "withheld-list", "NO gold mode      NO gold target\nNO normalized selector fields\nNO generator-computed winner IDs", 861, 756, 230, 82, { size: 13, bold: true, color: C.coral, align: "center" });
  addText(slide, "observed-note", "Observed instruction, history, and state follow the tested interface.", 862, 844, 228, 43, { size: 12, italic: true, color: C.muted, align: "center" });

  // C. Readouts fan from the two outputs along one evidence spine.
  addBox(slide, "evidence-spine", 1175, 110, 3, 770, { geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0 });
  connect(slide, tp, addCircle(slide, "spine-tp-anchor", "", 1169, 270, 14, { fill: C.coral, line: C.white, lineWidth: 1 }), { color: C.coral, width: 2.8, kind: "curved", arrow: false });
  connect(slide, tr, addCircle(slide, "spine-tr-anchor", "", 1169, 568, 14, { fill: C.teal, line: C.white, lineWidth: 1 }), { color: C.teal, width: 2.8, kind: "curved", style: "dashed", arrow: false });

  // C1 PairAcc, visually primary.
  addReadoutNumber(slide, 1, 1158, 112, C.blue);
  addText(slide, "pairacc-title", "Pair accuracy (PairAcc)", 1204, 105, 340, 40, { size: 22, bold: true });
  addText(slide, "pairacc-unit", "unit: one complete changed-winner pair", 1204, 144, 340, 27, { size: 14, color: C.muted });
  addBox(slide, "pairacc-formula", 1212, 190, 320, 78, { fill: C.blueLight, line: C.blue, lineWidth: 1.4 });
  addText(slide, "pairacc-formula-text", "T_P = A     AND     T_R = B", 1224, 199, 296, 58, { size: 19, bold: true, italic: true, font: "Times New Roman", align: "center" });
  addText(slide, "pairacc-denom", "Denominator: all complete changed-winner pairs", 1204, 279, 340, 45, { size: 14, align: "center" });

  addBox(slide, "separator-c12", 1204, 338, 340, 1, { geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0 });

  // C2 Conditional substitution.
  addReadoutNumber(slide, 2, 1158, 365, C.coral);
  addText(slide, "sub-title", "Conditional substitution", 1204, 358, 340, 40, { size: 21, bold: true });
  addText(slide, "sub-focus", "replacement after a correct observable binding", 1204, 397, 340, 27, { size: 14, color: C.muted });
  const subA = addCircle(slide, "sub-a", "A", 1220, 452, 42, { fill: C.coral, line: C.coral, color: C.white, size: 18 });
  const subClock = addClock(slide, "sub-clock", 1342, 452, 42, C.ink, C.white);
  const subB = addCircle(slide, "sub-b", "B", 1464, 452, 42, { fill: C.teal, line: C.teal, color: C.white, size: 18 });
  connect(slide, subA, subClock, { color: C.ink, width: 2.4 });
  connect(slide, subClock, subB, { color: C.ink, width: 2.4 });
  addText(slide, "sub-labels", "correct bind in S0                 refresh                 final target B", 1199, 500, 345, 33, { size: 12, align: "center" });
  addText(slide, "sub-denom", "Preserve denominator: correct binding + completed refresh + changed winner\n+ surviving, action-valid A", 1200, 539, 344, 58, { size: 13, align: "center" });

  addBox(slide, "separator-c23", 1204, 620, 340, 1, { geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0 });

  // C3 Execution subset.
  addReadoutNumber(slide, 3, 1158, 647, C.blue);
  addText(slide, "exec-title", "Execution subset", 1204, 640, 340, 40, { size: 21, bold: true });
  addText(slide, "exec-focus", "selected target ID -> tool write -> state diff", 1204, 679, 340, 27, { size: 14, color: C.muted });
  const execId = addTarget(slide, "exec-id", "ID", 1215, 735, C.ink);
  const write = addBox(slide, "exec-write", 1340, 740, 86, 50, { fill: C.blueLight, line: C.blue, lineWidth: 1.4 });
  addText(slide, "exec-write-text", "TOOL\nWRITE", 1347, 744, 72, 42, { size: 14, bold: true, align: "center" });
  const diff = addBox(slide, "exec-diff", 1464, 740, 86, 50, { fill: C.tealLight, line: C.teal, lineWidth: 1.4 });
  addText(slide, "exec-diff-text", "STATE\nDIFF", 1471, 744, 72, 42, { size: 14, bold: true, color: C.teal, align: "center" });
  connect(slide, execId, write, { color: C.blue, width: 2.7 });
  connect(slide, write, diff, { color: C.blue, width: 2.7 });
  addText(slide, "exec-labels", "selected ID                 model-issued                 executed change", 1200, 798, 348, 31, { size: 12, align: "center" });
  addText(slide, "exec-denom", "Denominator: executed model-issued writes\n(subset of all evaluation rows)", 1204, 842, 340, 54, { size: 13, align: "center" });

  slide.speakerNotes.textFrame.setText(
    "[Sources]\n" +
    "- User-provided TRI Figure 2 reference: information inventory and visual density.\n" +
    "- Anonymous TRI manuscript: matched-pair variables, strict substitution denominator, probe inputs, and execution readout.\n" +
    "- User-provided strong-paper examples: composition references only; no scientific content copied."
  );
  slide.speakerNotes.setVisible(false);

  const png = await presentation.export({ slide, format: "png", scale: 2 });
  await writeBlob(path.join(OUT, "fig2_tri_diagnostic_workflow_v12_centered.png"), png);
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(OUT, "fig2_tri_diagnostic_workflow_v12_centered.layout.json"), await layout.text());
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,notes", maxChars: 40000 });
  await fs.writeFile(path.join(OUT, "fig2_tri_diagnostic_workflow_v12_centered.inspect.ndjson"), inspect.ndjson);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(OUT, "fig2_tri_diagnostic_workflow_v12_centered.pptx"));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
