import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT = process.argv[2] || path.resolve("output");
const W = 1600;
const H = 960;

const C = {
  ink: "#243F48",
  text: "#202A2E",
  muted: "#68767B",
  rule: "#AEBABD",
  soft: "#F7F9F8",
  coral: "#F05F45",
  coralLight: "#FFF0EC",
  teal: "#128B88",
  tealLight: "#E9F7F5",
  amber: "#E6A646",
  amberLight: "#FFF6E5",
  green: "#56A778",
  greenLight: "#EDF8F1",
  white: "#FFFFFF",
  grayNode: "#F0F2F2",
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
      width: opts.lineWidth ?? 1.4,
    },
  });
  if (geometry === "roundRect") s.borderRadius = "rounded-md";
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
      fontSize: opts.size ?? 20,
      bold: opts.bold ?? true,
      color: opts.color ?? opts.line ?? C.ink,
      alignment: "center",
      verticalAlignment: "middle",
    };
  }
  return s;
}

function connect(slide, from, to, opts = {}) {
  return slide.shapes.connect(from, to, {
    kind: opts.kind ?? "straight",
    fromSide: opts.fromSide ?? "right",
    toSide: opts.toSide ?? "left",
    line: {
      style: opts.style ?? "solid",
      fill: opts.color ?? C.ink,
      width: opts.width ?? 2.4,
    },
    head: { type: "none" },
    tail: opts.arrow === false
      ? { type: "none" }
      : { type: "triangle", width: "sm", length: "sm" },
  });
}

function addPanel(slide, letter, title, x, y, w, h) {
  addBox(slide, `panel-${letter}`, x, y, w, h, {
    fill: "none",
    line: "#303638",
    lineWidth: 1.5,
  });
  addText(slide, `panel-${letter}-title`, `${letter}. ${title}`, x + 18, y + 8, w - 36, 42, {
    size: 23,
    bold: true,
    color: "#111719",
    align: "center",
  });
}

function addEntityState(slide, prefix, x, y, withB = false) {
  const outer = addCircle(slide, `${prefix}-state`, "", x, y, 106, {
    fill: C.white,
    line: "#20282B",
    lineWidth: 1.3,
  });
  const dots = [
    [x + 22, y + 25],
    [x + 49, y + 17],
    [x + 18, y + 58],
    [x + 49, y + 72],
  ];
  for (const [i, [dx, dy]] of dots.entries()) {
    addCircle(slide, `${prefix}-other-${i}`, "", dx, dy, 15, {
      fill: C.grayNode,
      line: "#616A6D",
      lineWidth: 0.9,
    });
  }
  addCircle(slide, `${prefix}-a`, "A", x + 65, y + 46, 29, {
    fill: C.coral,
    line: C.coral,
    color: C.white,
    size: 16,
  });
  if (withB) {
    addCircle(slide, `${prefix}-b`, "B", x + 64, y + 14, 29, {
      fill: C.teal,
      line: C.teal,
      color: C.white,
      size: 16,
    });
  }
  return outer;
}

function addClock(slide, name, x, y, d, color = C.ink, fill = C.white) {
  const face = addCircle(slide, `${name}-face`, "", x, y, d, {
    fill,
    line: color,
    lineWidth: 2,
  });
  addBox(slide, `${name}-hand-v`, x + d * 0.48, y + d * 0.19, 2, d * 0.31, {
    geometry: "rect",
    fill: color,
    line: color,
    lineWidth: 0,
  });
  addBox(slide, `${name}-hand-h`, x + d * 0.48, y + d * 0.48, d * 0.22, 2, {
    geometry: "rect",
    fill: color,
    line: color,
    lineWidth: 0,
  });
  return face;
}

function addLock(slide, name, x, y, color, maskFill) {
  addCircle(slide, `${name}-shackle`, "", x + 5, y, 24, {
    fill: "none", line: color, lineWidth: 2,
  });
  addBox(slide, `${name}-body`, x, y + 11, 34, 27, {
    fill: maskFill, line: color, lineWidth: 2,
  });
  addCircle(slide, `${name}-key`, "", x + 14, y + 19, 6, {
    fill: color, line: color, lineWidth: 0,
  });
}

function addCrossTarget(slide, name, label, x, y, color) {
  const c = addCircle(slide, `${name}-circle`, label, x, y, 48, {
    fill: C.white,
    line: color,
    lineWidth: 2.2,
    color,
    size: 20,
  });
  addBox(slide, `${name}-h`, x - 8, y + 23, 64, 2, {
    geometry: "rect", fill: color, line: color, lineWidth: 0,
  });
  addBox(slide, `${name}-v`, x + 23, y - 8, 2, 64, {
    geometry: "rect", fill: color, line: color, lineWidth: 0,
  });
  return c;
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const slide = presentation.slides.add();
  slide.background.fill = C.white;

  addPanel(slide, "A", "Construct the matched pair", 14, 14, 650, 932);
  addPanel(slide, "B", "Run the pair", 678, 14, 404, 932);
  addPanel(slide, "C", "Observable readouts", 1096, 14, 490, 932);

  // A. Summary: retain the reference's explicit fixed/changed contract.
  addBox(slide, "a-summary", 30, 70, 618, 162, {
    fill: C.soft,
    line: C.rule,
    lineWidth: 1.2,
  });
  addText(slide, "a-fixed", "Fixed:  S0, S1, q, action, schema, controller interface", 48, 82, 582, 31, {
    size: 17,
    bold: true,
    align: "center",
  });
  addText(slide, "a-change", "Unique change: instruction commitment timing", 48, 113, 582, 31, {
    size: 17,
    bold: true,
    color: C.ink,
    align: "center",
  });
  addText(slide, "a-transition", "Shared transition:   q(S0) = A   ->   refresh   ->   q(S1) = B", 48, 145, 582, 34, {
    size: 19,
    bold: true,
    font: "Times New Roman",
    align: "center",
  });
  addBox(slide, "a-valid", 114, 184, 450, 35, {
    fill: C.amberLight,
    line: C.amber,
    lineWidth: 1.2,
  });
  addText(slide, "a-valid-text", "A remains present and action-valid in S1", 124, 187, 430, 29, {
    size: 18,
    italic: true,
    align: "center",
  });

  // A. Preserve lane: full S0/S1 snapshots and executable target trace.
  addBox(slide, "preserve-lane", 28, 247, 622, 211, {
    fill: "none",
    line: C.coral,
    lineWidth: 1.6,
  });
  addBox(slide, "preserve-band", 28, 247, 94, 211, {
    fill: C.coral,
    line: C.coral,
    lineWidth: 0,
  });
  addText(slide, "preserve-band-title", "Preserve", 36, 262, 78, 34, {
    size: 11,
    bold: true,
    color: C.white,
    align: "center",
  });
  addText(slide, "preserve-band-desc", "commit\nbefore\nrefresh", 36, 299, 78, 86, {
    size: 16,
    bold: true,
    color: C.white,
    align: "center",
  });
  addLock(slide, "preserve-lock", 58, 395, C.white, C.coral);

  addText(slide, "p-s0", "S0", 132, 257, 118, 28, {
    size: 19, bold: true, font: "Times New Roman", align: "center",
  });
  const pState0 = addEntityState(slide, "p-s0", 138, 287, false);
  addText(slide, "p-q0", "q(S0) = A", 128, 397, 128, 29, {
    size: 18, italic: true, font: "Times New Roman", align: "center",
  });

  addText(slide, "p-bind-label", "bound(A)\nbefore refresh", 249, 278, 103, 57, {
    size: 16, bold: true, color: C.coral, align: "center",
  });
  const pClock = addClock(slide, "p-clock", 298, 346, 42);
  addText(slide, "p-refresh", "refresh", 274, 390, 90, 25, {
    size: 15, align: "center",
  });
  connect(slide, pState0, pClock, { color: C.ink, width: 2.2 });

  addText(slide, "p-s1", "S1", 382, 257, 118, 28, {
    size: 19, bold: true, font: "Times New Roman", align: "center",
  });
  const pState1 = addEntityState(slide, "p-s1", 388, 287, true);
  addText(slide, "p-q1", "q(S1) = B", 378, 397, 128, 29, {
    size: 18, italic: true, font: "Times New Roman", align: "center",
  });
  connect(slide, pClock, pState1, { color: C.ink, width: 2.2 });

  const pTarget = addCrossTarget(slide, "p-target", "A", 573, 327, C.coral);
  connect(slide, pState1, pTarget, { color: C.coral, width: 2.4 });
  addText(slide, "p-action", "action executes", 505, 300, 136, 27, {
    size: 15, bold: true, align: "center",
  });
  addText(slide, "p-target-label", "target A", 558, 386, 80, 43, {
    size: 17, bold: true, color: C.coral, align: "center",
  });

  // A. Reevaluate lane: retain the same snapshots but change commitment timing only.
  addBox(slide, "reevaluate-lane", 28, 474, 622, 211, {
    fill: "none",
    line: C.teal,
    lineWidth: 1.6,
    style: "dashed",
  });
  addBox(slide, "reevaluate-band", 28, 474, 94, 211, {
    fill: C.teal,
    line: C.teal,
    lineWidth: 0,
  });
  addText(slide, "reevaluate-band-title", "Reevaluate", 33, 489, 84, 34, {
    size: 12,
    bold: true,
    color: C.white,
    align: "center",
  });
  addText(slide, "reevaluate-band-desc", "defer\nselection\nuntil after\nrefresh", 36, 524, 78, 102, {
    size: 13,
    bold: true,
    color: C.white,
    align: "center",
  });
  addClock(slide, "reevaluate-clock-icon", 60, 635, 30, C.white, "none");

  addText(slide, "r-s0", "S0", 132, 484, 118, 28, {
    size: 19, bold: true, font: "Times New Roman", align: "center",
  });
  const rState0 = addEntityState(slide, "r-s0", 138, 514, false);
  addText(slide, "r-q0", "q(S0) = A", 128, 624, 128, 29, {
    size: 18, italic: true, font: "Times New Roman", align: "center",
  });
  addText(slide, "r-defer-label", "deferred(q)\ndo not bind", 244, 505, 114, 57, {
    size: 16, bold: true, color: C.teal, align: "center",
  });
  const rClock = addClock(slide, "r-clock", 298, 573, 42);
  addText(slide, "r-refresh", "refresh", 274, 617, 90, 25, {
    size: 15, align: "center",
  });
  connect(slide, rState0, rClock, { color: C.teal, width: 2.2, style: "dashed" });

  addText(slide, "r-s1", "S1", 382, 484, 118, 28, {
    size: 19, bold: true, font: "Times New Roman", align: "center",
  });
  const rState1 = addEntityState(slide, "r-s1", 388, 514, true);
  addText(slide, "r-q1", "q(S1) = B", 378, 624, 128, 29, {
    size: 18, italic: true, font: "Times New Roman", align: "center",
  });
  connect(slide, rClock, rState1, { color: C.teal, width: 2.2, style: "dashed" });
  addText(slide, "r-resolve", "resolve(q) on S1", 471, 505, 110, 50, {
    size: 15, bold: true, color: C.teal, align: "center",
  });
  const rTarget = addCrossTarget(slide, "r-target", "B", 573, 554, C.teal);
  connect(slide, rState1, rTarget, { color: C.teal, width: 2.4, style: "dashed" });
  addText(slide, "r-target-label", "target B", 558, 613, 80, 43, {
    size: 17, bold: true, color: C.teal, align: "center",
  });

  // A. Preserve the reference legend and fixed-vs-changed checklist.
  addBox(slide, "a-legend", 28, 701, 622, 56, {
    fill: C.soft, line: C.rule, lineWidth: 1,
  });
  addCircle(slide, "legend-other", "", 43, 718, 16, {
    fill: C.grayNode, line: C.rule, lineWidth: 0.8,
  });
  addText(slide, "legend-other-text", "other entities", 63, 709, 88, 36, {
    size: 12, align: "center",
  });
  addCircle(slide, "legend-a", "A", 160, 714, 23, {
    fill: C.coral, line: C.coral, color: C.white, size: 12,
  });
  addText(slide, "legend-a-text", "entity A\ninitial winner", 186, 707, 92, 43, {
    size: 11, align: "center",
  });
  addCircle(slide, "legend-b", "B", 286, 714, 23, {
    fill: C.teal, line: C.teal, color: C.white, size: 12,
  });
  addText(slide, "legend-b-text", "entity B\npost-refresh winner", 312, 707, 105, 43, {
    size: 11, align: "center",
  });
  addText(slide, "legend-bound", "BOUND", 427, 714, 63, 24, {
    size: 9, bold: true, color: C.coral, align: "center", line: C.coral, lineWidth: 1,
  });
  addText(slide, "legend-deferred", "DEFERRED", 500, 714, 72, 24, {
    size: 8, bold: true, color: C.teal, align: "center", line: C.teal, lineWidth: 1,
  });
  addText(slide, "legend-action", "same action", 579, 707, 62, 42, {
    size: 11, bold: true, align: "center",
  });

  addBox(slide, "a-checklist", 28, 771, 622, 153, {
    fill: "none", line: C.rule, lineWidth: 1.1, style: "dashed",
  });
  addBox(slide, "a-check-divider", 340, 787, 1, 119, {
    geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0,
  });
  addText(slide, "a-fixed-head", "What is fixed across the pair", 48, 782, 272, 27, {
    size: 15, bold: true, align: "center",
  });
  addText(slide, "a-fixed-list", "✓  States: S0, S1, and all entities\n✓  Selector: q\n✓  Action and schema\n✓  Controller interface", 50, 811, 270, 97, {
    size: 14, color: C.text,
  });
  addText(slide, "a-changed-head", "What is uniquely changed", 359, 797, 270, 27, {
    size: 15, bold: true, color: C.teal, align: "center",
  });
  addText(slide, "a-changed-list", "Instruction commitment timing\n(bind before refresh vs. defer until after refresh)", 360, 836, 267, 60, {
    size: 14, color: C.teal, align: "center",
  });

  // B. Same black-box controller probe, two independent runs.
  addBox(slide, "b-same", 696, 70, 368, 45, {
    fill: C.amberLight, line: C.amber, lineWidth: 1.2,
  });
  addText(slide, "b-same-text", "same controller + same interface", 711, 76, 338, 31, {
    size: 18, bold: true, align: "center",
  });
  addText(slide, "b-independent", "two independent runs\nwithin the comparison", 740, 136, 280, 56, {
    size: 17, align: "center",
  });
  addBox(slide, "b-bracket-left", 724, 191, 1, 109, {
    geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0,
  });
  addBox(slide, "b-bracket-top-left", 724, 191, 50, 1, {
    geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0,
  });
  addBox(slide, "b-bracket-right", 1035, 191, 1, 112, {
    geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0,
  });
  addBox(slide, "b-bracket-top-right", 986, 191, 50, 1, {
    geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0,
  });

  const pInput = addBox(slide, "b-p-input", 690, 302, 108, 86, {
    fill: C.coralLight, line: C.coral, lineWidth: 1.5,
  });
  addText(slide, "b-p-input-text", "Preserve\ninstruction", 695, 311, 98, 68, {
    size: 13, bold: true, color: C.coral, align: "center",
  });
  const rInput = addBox(slide, "b-r-input", 690, 504, 108, 86, {
    fill: C.tealLight, line: C.teal, lineWidth: 1.5, style: "dashed",
  });
  addText(slide, "b-r-input-text", "Reevaluate\ninstruction", 695, 513, 98, 68, {
    size: 13, bold: true, color: C.teal, align: "center",
  });

  const probe = addBox(slide, "b-probe", 812, 250, 154, 406, {
    fill: C.soft, line: "#242C2F", lineWidth: 1.6,
  });
  addText(slide, "b-probe-title", "Controller\nprobe", 826, 290, 126, 62, {
    size: 19, bold: true, align: "center",
  });
  addText(slide, "b-probe-blackbox", "BLACK-BOX\ninternals unobserved", 829, 402, 120, 48, {
    size: 10, bold: true, color: C.muted, align: "center", line: C.rule, lineWidth: 1,
  });
  addText(slide, "b-probe-io", "instruction + history\n+ observed state\n-> final target ID", 827, 493, 124, 94, {
    size: 15, bold: true, color: C.ink, align: "center",
  });

  const tp = addBox(slide, "b-tp", 978, 309, 86, 70, {
    fill: C.white, line: C.coral, lineWidth: 1.5,
  });
  addText(slide, "b-tp-text", "T_P", 982, 314, 78, 58, {
    size: 23, italic: true, color: C.coral, font: "Times New Roman", align: "center",
  });
  addText(slide, "b-tp-label", "final target", 972, 382, 98, 28, {
    size: 13, align: "center",
  });
  const tr = addBox(slide, "b-tr", 978, 511, 86, 70, {
    fill: C.white, line: C.teal, lineWidth: 1.5, style: "dashed",
  });
  addText(slide, "b-tr-text", "T_R", 982, 516, 78, 58, {
    size: 23, italic: true, color: C.teal, font: "Times New Roman", align: "center",
  });
  addText(slide, "b-tr-label", "final target", 972, 584, 98, 28, {
    size: 13, align: "center",
  });
  const pInAnchor = addBox(slide, "b-p-in-anchor", 811, 344, 2, 2, {
    geometry: "ellipse", fill: "none", line: "none", lineWidth: 0,
  });
  const pOutAnchor = addBox(slide, "b-p-out-anchor", 965, 344, 2, 2, {
    geometry: "ellipse", fill: "none", line: "none", lineWidth: 0,
  });
  const rInAnchor = addBox(slide, "b-r-in-anchor", 811, 546, 2, 2, {
    geometry: "ellipse", fill: "none", line: "none", lineWidth: 0,
  });
  const rOutAnchor = addBox(slide, "b-r-out-anchor", 965, 546, 2, 2, {
    geometry: "ellipse", fill: "none", line: "none", lineWidth: 0,
  });
  connect(slide, pInput, pInAnchor, { color: C.coral, width: 2.5 });
  connect(slide, pOutAnchor, tp, { color: C.coral, width: 2.5 });
  connect(slide, rInput, rInAnchor, { color: C.teal, width: 2.5, style: "dashed" });
  connect(slide, rOutAnchor, tr, { color: C.teal, width: 2.5, style: "dashed" });

  addBox(slide, "b-withheld", 696, 678, 368, 240, {
    fill: "none", line: C.rule, lineWidth: 1.2, style: "dashed",
  });
  addText(slide, "b-withheld-title", "Withheld from the probe", 716, 690, 328, 34, {
    size: 18, bold: true, align: "center",
  });
  addText(slide, "b-withheld-items", "", 715, 730, 330, 20, {
    size: 14, color: C.muted, align: "center",
  });
  const withheldCards = [
    [706, 738, 78, "gold\nmode"],
    [792, 738, 78, "gold\ntarget"],
    [878, 738, 78, "norm.\nselector"],
    [964, 738, 90, "winner\nIDs"],
  ];
  for (const [i, [x, y, w, label]] of withheldCards.entries()) {
    addBox(slide, `b-withheld-card-${i}`, x, y, w, 78, {
      fill: C.soft, line: C.rule, lineWidth: 1,
    });
    addText(slide, `b-withheld-no-${i}`, "NO", x + 8, y + 6, w - 16, 22, {
      size: 11, bold: true, color: C.coral, align: "center",
    });
    addText(slide, `b-withheld-label-${i}`, label, x + 6, y + 27, w - 12, 43, {
      size: 11, bold: true, color: C.muted, align: "center",
    });
  }
  addText(slide, "b-withheld-note", "Observed instruction, history, and state follow\nthe tested controller interface.", 716, 837, 328, 58, {
    size: 14, italic: true, color: C.ink, align: "center",
  });

  // C1. PairAcc: pair-level co-correctness on complete changed-winner pairs.
  addBox(slide, "c-readout-1", 1113, 70, 456, 228, {
    fill: C.soft, line: C.rule, lineWidth: 1.2,
  });
  addCircle(slide, "c-num-1", "1", 1130, 88, 34, {
    fill: C.white, line: C.ink, color: C.ink, size: 17,
  });
  addText(slide, "c-r1-title", "Pair accuracy (PairAcc)", 1177, 82, 360, 38, {
    size: 20, bold: true,
  });
  addText(slide, "c-r1-unit", "Unit = one complete changed-winner pair", 1177, 119, 360, 29, {
    size: 15, color: C.ink,
  });
  addBox(slide, "c-r1-p", 1162, 163, 132, 55, {
    fill: C.white, line: C.coral, lineWidth: 1.5, style: "dashed",
  });
  addText(slide, "c-r1-p-text", "T_P = A", 1167, 168, 122, 45, {
    size: 20, italic: true, font: "Times New Roman", align: "center",
  });
  addText(slide, "c-r1-and", "AND", 1304, 170, 72, 42, {
    size: 18, bold: true, align: "center",
  });
  addBox(slide, "c-r1-r", 1388, 163, 132, 55, {
    fill: C.white, line: C.teal, lineWidth: 1.5, style: "dashed",
  });
  addText(slide, "c-r1-r-text", "T_R = B", 1393, 168, 122, 45, {
    size: 20, italic: true, font: "Times New Roman", align: "center",
  });
  addText(slide, "c-r1-denom", "Denominator: all complete changed-winner pairs", 1155, 235, 372, 43, {
    size: 16, align: "center",
  });

  // C2. Conditional substitution: preserve the full strict opportunity definition.
  addBox(slide, "c-readout-2", 1113, 315, 456, 275, {
    fill: "none", line: C.rule, lineWidth: 1.2,
  });
  addCircle(slide, "c-num-2", "2", 1130, 333, 34, {
    fill: C.white, line: C.ink, color: C.ink, size: 17,
  });
  addText(slide, "c-r2-title", "Conditional substitution", 1177, 327, 360, 38, {
    size: 20, bold: true,
  });
  addText(slide, "c-r2-focus", "Focus = replacement after a correct observable binding", 1177, 364, 360, 33, {
    size: 15,
  });
  const c2a = addCircle(slide, "c-r2-a", "A", 1174, 420, 42, {
    fill: C.coral, line: C.coral, color: C.white, size: 19,
  });
  addText(slide, "c-r2-a-label", "correct binding\nin S0", 1137, 464, 118, 50, {
    size: 14, align: "center",
  });
  const c2clock = addClock(slide, "c-r2-clock", 1310, 420, 42);
  addText(slide, "c-r2-clock-label", "refresh", 1286, 464, 90, 28, {
    size: 14, align: "center",
  });
  const c2b = addCircle(slide, "c-r2-b", "B", 1447, 420, 42, {
    fill: C.teal, line: C.teal, color: C.white, size: 19,
  });
  addText(slide, "c-r2-b-label", "final target\n(substitution)", 1409, 464, 118, 50, {
    size: 14, align: "center",
  });
  connect(slide, c2a, c2clock, { color: C.ink, width: 2.2 });
  connect(slide, c2clock, c2b, { color: C.ink, width: 2.2 });
  addText(slide, "c-r2-denom", "Denominator: Preserve rows with correct initial binding, completed refresh,\nchanged winner, and old A surviving + action-valid", 1140, 522, 400, 53, {
    size: 14, align: "center",
  });

  // C3. Executed consequence: selected target through tool write to state diff.
  addBox(slide, "c-readout-3", 1113, 607, 456, 311, {
    fill: "none", line: C.rule, lineWidth: 1.2,
  });
  addCircle(slide, "c-num-3", "3", 1130, 625, 34, {
    fill: C.white, line: C.ink, color: C.ink, size: 17,
  });
  addText(slide, "c-r3-title", "Execution subset (tool writes)", 1177, 619, 360, 38, {
    size: 20, bold: true,
  });
  addText(slide, "c-r3-focus", "Trace = selected target ID -> tool write -> state diff", 1177, 657, 360, 33, {
    size: 15,
  });
  const c3id = addCrossTarget(slide, "c-r3-id", "ID", 1162, 720, C.ink);
  addText(slide, "c-r3-id-label", "selected\ntarget ID", 1137, 780, 98, 52, {
    size: 14, align: "center",
  });
  const c3write = addBox(slide, "c-r3-write", 1300, 719, 92, 54, {
    fill: C.amberLight, line: C.amber, lineWidth: 1.4,
  });
  addText(slide, "c-r3-write-text", "TOOL\nWRITE", 1304, 722, 84, 48, {
    size: 16, bold: true, align: "center",
  });
  addText(slide, "c-r3-write-label", "model-issued", 1291, 780, 110, 28, {
    size: 14, align: "center",
  });
  const c3diff = addBox(slide, "c-r3-diff", 1451, 719, 90, 54, {
    fill: C.greenLight, line: C.green, lineWidth: 1.4,
  });
  addText(slide, "c-r3-diff-text", "STATE\nDIFF", 1455, 722, 82, 48, {
    size: 16, bold: true, color: C.green, align: "center",
  });
  addText(slide, "c-r3-diff-label", "executed change", 1438, 780, 116, 28, {
    size: 14, align: "center",
  });
  connect(slide, c3id, c3write, { color: C.ink, width: 2.2 });
  connect(slide, c3write, c3diff, { color: C.ink, width: 2.2 });
  addText(slide, "c-r3-denom", "Denominator: executed model-issued writes\n(subset of all evaluation rows)", 1160, 846, 360, 55, {
    size: 15, align: "center",
  });

  slide.speakerNotes.textFrame.setText(
    "[Sources]\n" +
    "- User-provided Figure 2 reference: structure, density, and visual grammar.\n" +
    "- Anonymous TRI manuscript: matched-pair variables, strict substitution denominator, probe inputs, and execution readout."
  );
  slide.speakerNotes.setVisible(false);

  const png = await presentation.export({ slide, format: "png", scale: 2 });
  await writeBlob(path.join(OUT, "fig2_tri_diagnostic_workflow_v10_space_optimized.png"), png);
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(OUT, "fig2_tri_diagnostic_workflow_v10_space_optimized.layout.json"), await layout.text());
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,notes", maxChars: 30000 });
  await fs.writeFile(path.join(OUT, "fig2_tri_diagnostic_workflow_v10_space_optimized.inspect.ndjson"), inspect.ndjson);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(OUT, "fig2_tri_diagnostic_workflow_v10_space_optimized.pptx"));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
