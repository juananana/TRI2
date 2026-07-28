import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { icons as lucideIcons } from "lucide";

const OUT = process.argv[2] || path.resolve("output");
const W = 1280;
const H = 350;

const C = {
  ink: "#28343A",
  text: "#30343F",
  muted: "#69787E",
  rule: "#B9C3C5",
  soft: "#F8FAFA",
  coral: "#B94D49",
  coralLight: "#FAECE8",
  teal: "#2D7F7B",
  tealLight: "#EAF5F3",
  blue: "#66899D",
  blueLight: "#EFF5F7",
  white: "#FFFFFF",
  grayNode: "#F1F3F3",
};

async function writeBlob(filename, blob) {
  await fs.writeFile(filename, new Uint8Array(await blob.arrayBuffer()));
}

function escapeXml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function lucideSvg(iconName, color, strokeWidth = 2) {
  const nodes = lucideIcons[iconName];
  if (!nodes) throw new Error(`Unknown Lucide icon: ${iconName}`);
  const body = nodes.map(([tag, attrs]) => {
    const serialized = Object.entries(attrs)
      .map(([key, value]) => `${key}="${escapeXml(value)}"`)
      .join(" ");
    return `<${tag} ${serialized}/>`;
  }).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="${escapeXml(color)}" stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
}

function addIcon(slide, name, iconName, x, y, w, h, color, strokeWidth = 2) {
  const bytes = new TextEncoder().encode(lucideSvg(iconName, color, strokeWidth));
  return slide.images.add({
    blob: bytes,
    contentType: "image/svg+xml",
    alt: `${iconName} icon`,
    fit: "contain",
    position: { left: x, top: y, width: w, height: h },
  });
}

function textBox(slide, name, text, x, y, w, h, opts = {}) {
  const s = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: opts.fill ?? "none",
    line: { style: opts.style ?? "solid", fill: opts.line ?? "none", width: opts.lineWidth ?? 0 },
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

function box(slide, name, x, y, w, h, opts = {}) {
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
  if (geometry === "roundRect") s.borderRadius = "rounded-lg";
  return s;
}

function circle(slide, name, label, x, y, d, opts = {}) {
  const s = slide.shapes.add({
    geometry: "ellipse",
    name,
    position: { left: x, top: y, width: d, height: d },
    fill: opts.fill ?? C.white,
    line: {
      style: opts.style ?? "solid",
      fill: opts.line ?? C.ink,
      width: opts.lineWidth ?? 1.6,
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
    line: { style: opts.style ?? "solid", fill: opts.color ?? C.ink, width: opts.width ?? 2.5 },
    cap: "round",
    join: "round",
    head: { type: "none" },
    tail: opts.arrow === false ? { type: "none" } : { type: "stealth", width: "med", length: "med" },
  });
  connector.bringToFront();
  return connector;
}

function phase(slide, letter, title, x, y, w, color) {
  circle(slide, `phase-${letter}`, letter, x, y, 26, { fill: color, line: color, color: C.white, size: 15 });
  textBox(slide, `phase-${letter}-title`, title, x + 35, y - 2, w - 35, 30, { size: 20, bold: true, color: "#111719" });
}

function clock(slide, name, x, y, d, color = C.ink) {
  const face = circle(slide, `${name}-face`, "", x, y, d, { fill: C.white, line: color, lineWidth: 1.8 });
  box(slide, `${name}-hand-v`, x + d * 0.49, y + d * 0.18, 2, d * 0.32, { geometry: "rect", fill: color, line: color, lineWidth: 0 });
  box(slide, `${name}-hand-h`, x + d * 0.49, y + d * 0.49, d * 0.22, 2, { geometry: "rect", fill: color, line: color, lineWidth: 0 });
  circle(slide, `${name}-hub`, "", x + d * 0.43, y + d * 0.43, d * 0.14, { fill: color, line: color, lineWidth: 0 });
  return face;
}

function lock(slide, name, x, y, color) {
  circle(slide, `${name}-shackle`, "", x + 4, y, 20, { fill: "none", line: color, lineWidth: 1.8 });
  box(slide, `${name}-body`, x, y + 9, 28, 23, { fill: C.white, line: color, lineWidth: 1.8 });
  circle(slide, `${name}-key`, "", x + 12, y + 16, 5, { fill: color, line: color, lineWidth: 0 });
}

function state(slide, name, x, y, withB) {
  const outer = circle(slide, `${name}-state`, "", x, y, 56, { fill: C.white, line: C.ink, lineWidth: 1.4 });
  const dots = [[12, 13], [27, 9], [10, 31], [28, 38]];
  for (const [i, [dx, dy]] of dots.entries()) {
    circle(slide, `${name}-other-${i}`, "", x + dx, y + dy, 8, { fill: C.grayNode, line: C.muted, lineWidth: 0.6 });
  }
  circle(slide, `${name}-a`, "A", x + 34, y + 26, 16, { fill: C.coral, line: C.coral, color: C.white, size: 10 });
  if (withB) circle(slide, `${name}-b`, "B", x + 34, y + 8, 16, { fill: C.teal, line: C.teal, color: C.white, size: 10 });
  return outer;
}

function target(slide, name, label, x, y, color) {
  const t = circle(slide, `${name}-circle`, label, x, y, 42, { fill: C.white, line: color, lineWidth: 2, color, size: 18 });
  box(slide, `${name}-h`, x - 5, y + 20, 52, 2, { geometry: "rect", fill: color, line: color, lineWidth: 0 });
  box(slide, `${name}-v`, x + 20, y - 5, 2, 52, { geometry: "rect", fill: color, line: color, lineWidth: 0 });
  return t;
}

function readoutNumber(slide, n, x, y, color) {
  return circle(slide, `readout-${n}`, String(n), x, y, 25, { fill: C.white, line: color, lineWidth: 1.8, color, size: 14 });
}

function spark(slide, name, x, y, color) {
  circle(slide, `${name}-dot-1`, "", x, y + 10, 3, { fill: color, line: color, lineWidth: 0 });
  circle(slide, `${name}-dot-2`, "", x + 7, y + 5, 4, { fill: color, line: color, lineWidth: 0 });
  circle(slide, `${name}-dot-3`, "", x + 16, y, 3, { fill: color, line: color, lineWidth: 0 });
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const slide = presentation.slides.add();
  slide.background.fill = C.white;

  phase(slide, "A", "Construct the matched pair", 16, 10, 640, C.ink);
  phase(slide, "B", "Run the pair", 696, 10, 210, C.blue);
  phase(slide, "C", "Observable readouts", 946, 10, 316, C.ink);

  // Pair contract: compact but complete.
  box(slide, "pair-contract", 16, 48, 640, 65, { fill: C.soft, line: "none", lineWidth: 0 });
  addIcon(slide, "fixed-icon", "Layers3", 31, 54, 15, 15, C.blue, 1.9);
  textBox(slide, "fixed-label", "FIXED", 49, 54, 50, 18, { size: 9, bold: true, color: C.blue });
  textBox(slide, "fixed-items", "S0, S1, q, action, schema, controller interface", 101, 53, 327, 20, { size: 12, bold: true });
  addIcon(slide, "change-icon", "TimerReset", 31, 81, 15, 15, C.teal, 1.9);
  textBox(slide, "change-label", "ONLY CHANGE", 49, 81, 73, 18, { size: 9, bold: true, color: C.teal });
  textBox(slide, "change-items", "commitment timing", 122, 80, 160, 20, { size: 15, bold: true, color: C.teal });
  textBox(slide, "transition", "q(S0)=A  ->  refresh  ->  q(S1)=B", 294, 76, 338, 22, { size: 15, bold: true, font: "Times New Roman", align: "center" });
  box(slide, "valid-pill", 405, 97, 228, 18, { fill: C.blueLight, line: C.blue, lineWidth: 1 });
  textBox(slide, "valid-text", "A remains present and action-valid in S1", 412, 98, 214, 15, { size: 10, italic: true, align: "center" });
  box(slide, "contract-rule", 28, 114, 606, 1, { geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0 });

  // Dominant matched pair: two compact lanes around the same refresh.
  box(slide, "pair-frame", 16, 128, 640, 205, { fill: C.white, line: "none", lineWidth: 0 });
  box(slide, "pair-stem", 42, 173, 2, 118, { geometry: "rect", fill: C.ink, line: C.ink, lineWidth: 0 });
  circle(slide, "pair-dot-p", "", 36, 167, 14, { fill: C.coral, line: C.white, lineWidth: 1 });
  circle(slide, "pair-dot-r", "", 36, 285, 14, { fill: C.teal, line: C.white, lineWidth: 1 });
  textBox(slide, "pair-badge-text", "PAIR", 20, 220, 46, 24, { size: 10, bold: true, color: C.ink, align: "center" });
  textBox(slide, "refresh-tab-text", "same refresh, replayed twice", 286, 121, 128, 18, { size: 10, bold: true, color: C.blue, align: "center" });
  circle(slide, "refresh-tab-left", "", 278, 127, 6, { fill: C.blue, line: C.blue, lineWidth: 0 });
  circle(slide, "refresh-tab-right", "", 416, 127, 6, { fill: C.blue, line: C.blue, lineWidth: 0 });

  box(slide, "preserve-lane", 64, 141, 578, 82, { fill: C.coralLight, line: "none", lineWidth: 0 });
  circle(slide, "preserve-icon-bg", "", 73, 146, 38, { fill: C.white, line: C.coral, lineWidth: 1.2 });
  addIcon(slide, "preserve-icon", "LockKeyhole", 81, 154, 22, 22, C.coral, 1.9);
  textBox(slide, "preserve-title", "Preserve", 114, 147, 112, 22, { size: 16, bold: true, color: C.coral });
  textBox(slide, "preserve-rule", "bind A before refresh", 114, 169, 150, 18, { size: 12, bold: true, color: C.coral });
  const pS0 = state(slide, "p-s0", 264, 155, false);
  const pClock = circle(slide, "p-refresh-node", "", 390, 166, 34, { fill: C.white, line: C.blue, lineWidth: 1.7 });
  addIcon(slide, "p-refresh-icon", "DatabaseBackup", 397, 173, 20, 20, C.blue, 1.8);
  const pS1 = state(slide, "p-s1", 468, 155, true);
  const pTarget = target(slide, "p-target", "A", 580, 162, C.coral);
  connect(slide, pS0, pClock, { color: C.coral, width: 2.8, kind: "curved" });
  connect(slide, pClock, pS1, { color: C.coral, width: 2.8, kind: "curved" });
  connect(slide, pS1, pTarget, { color: C.coral, width: 2.8, kind: "curved" });
  textBox(slide, "p-s0-label", "S0  q(S0)=A", 252, 208, 80, 16, { size: 10, italic: true, font: "Times New Roman", align: "center" });
  textBox(slide, "p-bound", "BOUND A", 334, 147, 64, 18, { size: 10, bold: true, color: C.coral, align: "center", line: C.coral, lineWidth: 1 });
  textBox(slide, "p-s1-label", "S1  q(S1)=B", 456, 208, 80, 16, { size: 10, italic: true, font: "Times New Roman", align: "center" });
  textBox(slide, "p-target-label", "target A", 571, 208, 60, 16, { size: 10, bold: true, color: C.coral, align: "center" });
  spark(slide, "p-spark", 625, 151, C.coral);

  box(slide, "reevaluate-lane", 76, 238, 560, 82, { fill: C.tealLight, line: "none", lineWidth: 0 });
  circle(slide, "reevaluate-icon-bg", "", 83, 243, 40, { fill: C.white, line: C.teal, lineWidth: 1.2 });
  addIcon(slide, "reevaluate-icon", "RefreshCcw", 92, 252, 22, 22, C.teal, 1.9);
  textBox(slide, "reevaluate-title", "Reevaluate", 124, 244, 122, 22, { size: 16, bold: true, color: C.teal });
  textBox(slide, "reevaluate-rule", "defer q until after refresh", 124, 266, 170, 18, { size: 12, bold: true, color: C.teal });
  const rS0 = state(slide, "r-s0", 276, 252, false);
  const rClock = circle(slide, "r-refresh-node", "", 402, 263, 34, { fill: C.white, line: C.blue, lineWidth: 1.7 });
  addIcon(slide, "r-refresh-icon", "DatabaseBackup", 409, 270, 20, 20, C.blue, 1.8);
  const rS1 = state(slide, "r-s1", 480, 252, true);
  const rTarget = target(slide, "r-target", "B", 590, 259, C.teal);
  connect(slide, rS0, rClock, { color: C.teal, width: 2.8, kind: "curved", style: "dashed" });
  connect(slide, rClock, rS1, { color: C.teal, width: 2.8, kind: "curved", style: "dashed" });
  connect(slide, rS1, rTarget, { color: C.teal, width: 2.8, kind: "curved", style: "dashed" });
  textBox(slide, "r-s0-label", "S0  q(S0)=A", 264, 305, 80, 16, { size: 10, italic: true, font: "Times New Roman", align: "center" });
  textBox(slide, "r-defer", "DEFER q", 346, 244, 64, 18, { size: 10, bold: true, color: C.teal, align: "center" });
  textBox(slide, "r-resolve", "resolve q on S1", 495, 235, 82, 17, { size: 9, bold: true, color: C.teal, align: "center" });
  textBox(slide, "r-s1-label", "S1  q(S1)=B", 468, 305, 80, 16, { size: 10, italic: true, font: "Times New Roman", align: "center" });
  textBox(slide, "r-target-label", "target B", 581, 305, 60, 16, { size: 10, bold: true, color: C.teal, align: "center" });
  spark(slide, "r-spark", 623, 246, C.teal);

  textBox(slide, "pair-invariant", "same world transition + same interface; only commitment timing changes", 70, 332, 470, 15, { size: 10, bold: true, color: C.ink, align: "center" });
  textBox(slide, "line-legend", "solid Preserve | dashed Reevaluate", 535, 332, 120, 15, { size: 8, color: C.muted, align: "center" });

  // B. Narrow probe bridge with separate ports for each independent run.
  box(slide, "same-chip", 696, 49, 210, 44, { fill: "none", line: "none", lineWidth: 0 });
  textBox(slide, "same-chip-text", "same controller + same interface", 708, 55, 186, 31, { size: 13, bold: true, align: "center" });
  box(slide, "same-chip-rule", 738, 87, 126, 2, { geometry: "rect", fill: C.blue, line: C.blue, lineWidth: 0 });
  textBox(slide, "independent", "two independent runs", 718, 95, 166, 20, { size: 11, italic: true, color: C.muted, align: "center" });
  const pPacket = circle(slide, "p-packet", "P", 704, 147, 44, { fill: C.coral, line: C.coral, color: C.white, size: 18 });
  const rPacket = circle(slide, "r-packet", "R", 704, 249, 44, { fill: C.teal, line: C.teal, color: C.white, size: 18 });
  const probe = box(slide, "probe", 768, 129, 96, 180, { geometry: "ellipse", fill: C.soft, line: C.ink, lineWidth: 1.7 });
  addIcon(slide, "probe-icon", "ScanSearch", 804, 141, 24, 24, C.ink, 1.8);
  textBox(slide, "probe-title", "Probe", 778, 164, 76, 20, { size: 11, bold: true, align: "center" });
  textBox(slide, "probe-kind", "controller black box", 778, 182, 76, 16, { size: 7, bold: true, color: C.muted, align: "center" });
  circle(slide, "probe-dot-p", "", 795, 202, 9, { fill: C.coral, line: C.white, lineWidth: 0.8 });
  circle(slide, "probe-dot-r", "", 830, 202, 9, { fill: C.teal, line: C.white, lineWidth: 0.8 });
  textBox(slide, "probe-blackbox", "internals unobserved", 780, 216, 72, 24, { size: 7, bold: true, color: C.muted, align: "center" });
  textBox(slide, "probe-io", "instruction + history\n+ observed state\n-> target ID", 778, 251, 76, 48, { size: 9, bold: true, align: "center" });
  const tp = box(slide, "tp", 870, 152, 50, 30, { fill: C.coralLight, line: C.coral, lineWidth: 1.5 });
  textBox(slide, "tp-text", "TP", 875, 155, 40, 24, { size: 8, bold: true, italic: true, color: C.coral, font: "Arial", align: "center" });
  const tr = box(slide, "tr", 870, 254, 50, 30, { fill: C.tealLight, line: C.teal, lineWidth: 1.5, style: "dashed" });
  textBox(slide, "tr-text", "TR", 875, 257, 40, 24, { size: 8, bold: true, italic: true, color: C.teal, font: "Arial", align: "center" });
  const pIn = circle(slide, "p-in", "", 772, 164, 4, { fill: "none", line: "none", lineWidth: 0 });
  const rIn = circle(slide, "r-in", "", 772, 266, 4, { fill: "none", line: "none", lineWidth: 0 });
  const pOut = circle(slide, "p-out", "", 858, 164, 4, { fill: "none", line: "none", lineWidth: 0 });
  const rOut = circle(slide, "r-out", "", 858, 266, 4, { fill: "none", line: "none", lineWidth: 0 });
  connect(slide, pPacket, pIn, { color: C.coral, width: 2.6, kind: "curved" });
  connect(slide, rPacket, rIn, { color: C.teal, width: 2.6, kind: "curved", style: "dashed" });
  connect(slide, pOut, tp, { color: C.coral, width: 2.6, kind: "curved" });
  connect(slide, rOut, tr, { color: C.teal, width: 2.6, kind: "curved", style: "dashed" });
  circle(slide, "p-in-port", "", 770, 161, 9, { fill: C.coral, line: C.white, lineWidth: 0.8 });
  circle(slide, "r-in-port", "", 770, 263, 9, { fill: C.teal, line: C.white, lineWidth: 0.8 });
  circle(slide, "p-out-port", "", 855, 161, 9, { fill: C.coral, line: C.white, lineWidth: 0.8 });
  circle(slide, "r-out-port", "", 855, 263, 9, { fill: C.teal, line: C.white, lineWidth: 0.8 });
  addIcon(slide, "withheld-icon", "EyeOff", 700, 320, 14, 14, C.muted, 1.8);
  textBox(slide, "withheld", "Withheld: gold mode/target; normalized selector fields; generator winner IDs", 718, 317, 192, 28, { size: 7, italic: true, color: C.muted, align: "center" });

  // C. One evidence spine, three distinct estimands.
  box(slide, "evidence-spine", 961, 58, 2, 278, { geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0 });
  readoutNumber(slide, 1, 950, 55, C.blue);
  addIcon(slide, "pairacc-icon", "BadgeCheck", 985, 55, 20, 20, C.blue, 1.8);
  textBox(slide, "pairacc-title", "PairAcc", 1010, 52, 82, 28, { size: 14, bold: true });
  box(slide, "pairacc-formula", 1092, 53, 167, 34, { fill: C.blueLight, line: "none", lineWidth: 0 });
  textBox(slide, "pairacc-formula-text", "T_P=A  AND  T_R=B", 1100, 57, 151, 25, { size: 13, bold: true, italic: true, font: "Times New Roman", align: "center" });
  textBox(slide, "pairacc-denom", "all complete changed-winner pairs", 985, 86, 274, 22, { size: 11, color: C.muted, align: "center" });
  box(slide, "c-sep-1", 985, 112, 274, 1, { geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0 });

  readoutNumber(slide, 2, 950, 126, C.coral);
  addIcon(slide, "sub-icon", "Route", 985, 126, 20, 20, C.coral, 1.8);
  textBox(slide, "sub-title", "Conditional substitution", 1010, 123, 249, 27, { size: 16, bold: true });
  const subA = circle(slide, "sub-a", "A", 998, 162, 30, { fill: C.coral, line: C.coral, color: C.white, size: 15 });
  const subClock = clock(slide, "sub-clock", 1104, 162, 30, C.ink);
  const subB = circle(slide, "sub-b", "B", 1220, 162, 30, { fill: C.teal, line: C.teal, color: C.white, size: 15 });
  connect(slide, subA, subClock, { color: C.ink, width: 2.2 });
  connect(slide, subClock, subB, { color: C.ink, width: 2.2 });
  textBox(slide, "sub-label", "correct bind       refresh       final B", 985, 193, 274, 18, { size: 9, align: "center" });
  textBox(slide, "sub-denom", "Preserve: correct binding + completed refresh + changed winner\n+ surviving, action-valid A", 985, 212, 274, 37, { size: 10, align: "center" });
  box(slide, "c-sep-2", 985, 254, 274, 1, { geometry: "rect", fill: C.rule, line: C.rule, lineWidth: 0 });

  readoutNumber(slide, 3, 950, 269, C.blue);
  addIcon(slide, "exec-icon", "DatabaseZap", 985, 269, 20, 20, C.blue, 1.8);
  textBox(slide, "exec-title", "Execution subset", 1010, 266, 249, 27, { size: 13, bold: true });
  const execId = box(slide, "exec-id", 998, 305, 42, 30, { fill: C.white, line: C.ink, lineWidth: 1.8 });
  textBox(slide, "exec-id-text", "ID", 1004, 308, 30, 24, { size: 10, bold: true, color: C.ink, align: "center" });
  const write = box(slide, "write", 1090, 305, 72, 30, { fill: C.blueLight, line: C.blue, lineWidth: 1 });
  addIcon(slide, "write-icon", "SquarePen", 1096, 312, 14, 14, C.ink, 1.8);
  textBox(slide, "write-text", "WRITE", 1112, 307, 44, 25, { size: 7, bold: true, align: "center" });
  const diff = box(slide, "diff", 1182, 305, 72, 30, { fill: C.tealLight, line: C.teal, lineWidth: 1 });
  addIcon(slide, "diff-icon", "Database", 1188, 312, 14, 14, C.teal, 1.8);
  textBox(slide, "diff-text", "DIFF", 1205, 307, 43, 25, { size: 9, bold: true, color: C.teal, align: "center" });
  connect(slide, execId, write, { color: C.blue, width: 2.2 });
  connect(slide, write, diff, { color: C.blue, width: 2.2 });
  textBox(slide, "exec-denom", "executed model-issued writes only", 985, 333, 274, 14, { size: 9, color: C.muted, align: "center" });

  slide.speakerNotes.textFrame.setText(
    "[Sources]\n" +
    "- Anonymous TRI manuscript: matched-pair construction, strict estimands, withheld fields, and execution trace.\n" +
    "- User-provided strong-paper examples: composition references only; no scientific content copied.\n" +
    "- Lucide Icons (ISC License): Layers3, TimerReset, LockKeyhole, RefreshCcw, DatabaseBackup, ScanSearch, EyeOff, BadgeCheck, Route, DatabaseZap, SquarePen, Database."
  );
  slide.speakerNotes.setVisible(false);

  const png = await presentation.export({ slide, format: "png", scale: 2 });
  await writeBlob(path.join(OUT, "fig2_tri_diagnostic_workflow_v15_icon_final.png"), png);
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(OUT, "fig2_tri_diagnostic_workflow_v15_icon_final.layout.json"), await layout.text());
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,notes", maxChars: 40000 });
  await fs.writeFile(path.join(OUT, "fig2_tri_diagnostic_workflow_v15_icon_final.inspect.ndjson"), inspect.ndjson);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(OUT, "fig2_tri_diagnostic_workflow_v15_icon_final.pptx"));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
