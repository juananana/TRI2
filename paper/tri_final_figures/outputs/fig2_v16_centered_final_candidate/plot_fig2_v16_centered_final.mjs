import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { icons as lucideIcons } from "lucide";

const OUT = process.argv[2] || path.resolve("output");
const W = 1280;
const H = 350;

const C = {
  ink: "#0D0D0E",
  charcoal: "#3C535C",
  text: "#58585A",
  muted: "#7D8D91",
  rule: "#AEBABD",
  teal: "#318383",
  tealMid: "#7FADB4",
  tealLight: "#D6EEF0",
  tealWash: "#F1FAFA",
  coral: "#B2242F",
  coralMid: "#E77576",
  coralLight: "#F7E8E8",
  blue: "#6C9FA3",
  white: "#FFFFFF",
  node: "#EEF2F2",
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
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: opts.fill ?? "none",
    line: { style: opts.style ?? "solid", fill: opts.line ?? "none", width: opts.lineWidth ?? 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontFamily: opts.font ?? "Arial",
    fontSize: opts.size ?? 12,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    color: opts.color ?? C.text,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
  };
  return shape;
}

function shape(slide, name, geometry, x, y, w, h, opts = {}) {
  const item = slide.shapes.add({
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
  if (geometry === "roundRect") item.borderRadius = opts.radius ?? "rounded-lg";
  return item;
}

function circle(slide, name, label, x, y, d, opts = {}) {
  const item = shape(slide, name, "ellipse", x, y, d, d, opts);
  if (label) {
    item.text = label;
    item.text.style = {
      fontFamily: opts.font ?? "Arial",
      fontSize: opts.size ?? 14,
      bold: opts.bold ?? true,
      italic: opts.italic ?? false,
      color: opts.color ?? opts.line ?? C.ink,
      alignment: "center",
      verticalAlignment: "middle",
    };
  }
  return item;
}

function connect(slide, from, to, opts = {}) {
  const edge = slide.shapes.connect(from, to, {
    kind: opts.kind ?? "straight",
    fromSide: opts.fromSide ?? "right",
    toSide: opts.toSide ?? "left",
    line: {
      style: opts.style ?? "solid",
      fill: opts.color ?? C.charcoal,
      width: opts.width ?? 2.4,
    },
    cap: "round",
    join: "round",
    head: { type: "none" },
    tail: opts.arrow === false ? { type: "none" } : { type: "stealth", width: "med", length: "med" },
  });
  if (opts.back === true && typeof edge.sendToBack === "function") edge.sendToBack();
  else if (typeof edge.bringToFront === "function") edge.bringToFront();
  return edge;
}

function stateSnapshot(slide, name, x, y, postRefresh = false) {
  const outer = circle(slide, `${name}-outer`, "", x, y, 84, {
    fill: C.white,
    line: C.charcoal,
    lineWidth: 1.6,
  });
  const faint = postRefresh
    ? [[15, 18], [25, 49], [48, 14]]
    : [[16, 17], [22, 50], [50, 14], [51, 48]];
  faint.forEach(([dx, dy], index) => {
    circle(slide, `${name}-candidate-${index}`, "", x + dx, y + dy, 11, {
      fill: C.node,
      line: C.muted,
      lineWidth: 0.8,
    });
  });
  const a = circle(slide, `${name}-A`, "A", x + 50, y + 47, 24, {
    fill: C.coral,
    line: C.coral,
    color: C.white,
    size: 12,
  });
  let b = null;
  if (postRefresh) {
    b = circle(slide, `${name}-B`, "B", x + 50, y + 17, 24, {
      fill: C.teal,
      line: C.teal,
      color: C.white,
      size: 12,
    });
  }
  return { outer, a, b };
}

function targetMarker(slide, name, label, x, y, color) {
  const outer = circle(slide, `${name}-outer`, label, x, y, 38, {
    fill: C.white,
    line: color,
    lineWidth: 2,
    color,
    size: 16,
  });
  shape(slide, `${name}-h`, "rect", x - 4, y + 18, 46, 2, { fill: color, line: color, lineWidth: 0 });
  shape(slide, `${name}-v`, "rect", x + 18, y - 4, 2, 46, { fill: color, line: color, lineWidth: 0 });
  return outer;
}

function metricNode(slide, number, y, color) {
  circle(slide, `metric-${number}-node`, String(number), 990, y, 25, {
    fill: C.white,
    line: color,
    lineWidth: 1.8,
    color,
    size: 13,
  });
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const slide = presentation.slides.add();
  slide.background.fill = C.white;

  textBox(slide, "main-title", "One transition, two valid commitments", 24, 8, 470, 31, {
    size: 22,
    bold: true,
    color: C.ink,
  });
  textBox(slide, "main-kicker", "TRI matched diagnostic", 502, 12, 196, 24, {
    size: 13,
    bold: true,
    italic: true,
    color: C.teal,
  });

  // One dominant scene, visually continuous from pair construction to the shared probe.
  shape(slide, "diagnostic-field", "ellipse", 18, 42, 954, 294, {
    fill: C.tealWash,
    line: "none",
    lineWidth: 0,
  });

  addIcon(slide, "fixed-icon", "Layers3", 65, 58, 16, 16, C.blue, 1.9);
  textBox(slide, "fixed-label", "FIXED", 85, 56, 48, 20, { size: 9, bold: true, color: C.blue });
  textBox(slide, "fixed-items", "S0, S1, q, action, schema, interface", 136, 55, 260, 22, {
    size: 11,
    bold: true,
    color: C.charcoal,
  });
  addIcon(slide, "timing-icon", "TimerReset", 421, 58, 16, 16, C.teal, 1.9);
  textBox(slide, "timing-label", "ONLY CHANGE", 441, 56, 82, 20, { size: 9, bold: true, color: C.teal });
  textBox(slide, "timing-value", "commitment timing", 523, 54, 150, 24, {
    size: 14,
    bold: true,
    color: C.teal,
  });
  textBox(slide, "same-refresh", "same refresh, replayed twice", 696, 55, 215, 22, {
    size: 11,
    italic: true,
    color: C.blue,
    align: "center",
  });

  // Matched pair bracket and commitment labels.
  shape(slide, "pair-stem", "rect", 67, 107, 2, 155, { fill: C.charcoal, line: C.charcoal, lineWidth: 0 });
  const pToken = circle(slide, "preserve-token", "P", 50, 91, 36, {
    fill: C.coral,
    line: C.coral,
    color: C.white,
    size: 16,
  });
  const rToken = circle(slide, "reevaluate-token", "R", 50, 246, 36, {
    fill: C.teal,
    line: C.teal,
    color: C.white,
    size: 16,
  });
  textBox(slide, "pair-label", "MATCHED\nPAIR", 30, 157, 76, 46, {
    size: 9,
    bold: true,
    color: C.charcoal,
    align: "center",
  });

  circle(slide, "preserve-icon-ring", "", 110, 87, 44, {
    fill: C.white,
    line: C.coral,
    lineWidth: 1.4,
  });
  addIcon(slide, "preserve-icon", "LockKeyhole", 120, 97, 24, 24, C.coral, 2);
  textBox(slide, "preserve-name", "Preserve", 160, 85, 100, 23, {
    size: 16,
    bold: true,
    color: C.coral,
  });
  textBox(slide, "preserve-action", "bind A before refresh", 160, 107, 155, 20, {
    size: 11,
    bold: true,
    color: C.coral,
  });

  circle(slide, "reevaluate-icon-ring", "", 110, 242, 44, {
    fill: C.white,
    line: C.teal,
    lineWidth: 1.4,
  });
  addIcon(slide, "reevaluate-icon", "RefreshCcw", 120, 252, 24, 24, C.teal, 2);
  textBox(slide, "reevaluate-name", "Reevaluate", 160, 240, 110, 23, {
    size: 16,
    bold: true,
    color: C.teal,
  });
  textBox(slide, "reevaluate-action", "defer q until after refresh", 160, 262, 175, 20, {
    size: 11,
    bold: true,
    color: C.teal,
  });

  // The state spine is shared, not duplicated across two template lanes.
  const s0 = stateSnapshot(slide, "state-s0", 325, 133, false);
  const refresh = circle(slide, "shared-refresh", "", 455, 150, 50, {
    fill: C.white,
    line: C.blue,
    lineWidth: 1.8,
  });
  addIcon(slide, "shared-refresh-icon", "DatabaseBackup", 467, 162, 26, 26, C.blue, 1.8);
  const s1 = stateSnapshot(slide, "state-s1", 565, 133, true);
  connect(slide, s0.outer, refresh, { color: C.charcoal, width: 2.6, kind: "straight" });
  connect(slide, refresh, s1.outer, { color: C.charcoal, width: 2.6, kind: "straight" });
  textBox(slide, "s0-label", "S0", 345, 205, 42, 18, {
    size: 12,
    bold: true,
    italic: true,
    font: "Times New Roman",
    align: "center",
  });
  textBox(slide, "s0-winner", "q(S0)=A", 323, 220, 88, 18, {
    size: 11,
    italic: true,
    font: "Times New Roman",
    align: "center",
  });
  textBox(slide, "refresh-label", "refresh", 450, 205, 60, 18, {
    size: 10,
    bold: true,
    color: C.blue,
    align: "center",
  });
  textBox(slide, "s1-label", "S1", 585, 205, 42, 18, {
    size: 12,
    bold: true,
    italic: true,
    font: "Times New Roman",
    align: "center",
  });
  textBox(slide, "s1-winner", "q(S1)=B", 563, 220, 88, 18, {
    size: 11,
    italic: true,
    font: "Times New Roman",
    align: "center",
  });

  // Gold commitment paths use redundant color, line style, labels, and icons.
  const targetA = targetMarker(slide, "gold-target-a", "A", 700, 91, C.coral);
  const targetB = targetMarker(slide, "gold-target-b", "B", 700, 247, C.teal);
  const pBoundRoute = textBox(slide, "bound-a", "BOUND A", 374, 89, 78, 20, {
    size: 10,
    bold: true,
    color: C.coral,
    align: "center",
  });
  const rDeferRoute = textBox(slide, "r-defer", "DEFER q", 405, 255, 76, 20, {
    size: 10,
    bold: true,
    color: C.teal,
    align: "center",
  });
  connect(slide, pBoundRoute, s0.a, { color: C.coral, width: 3, kind: "curved", fromSide: "bottom", toSide: "top" });
  connect(slide, s0.a, s1.a, { color: C.coral, width: 3, kind: "curved", fromSide: "top", toSide: "top" });
  connect(slide, s1.a, targetA, { color: C.coral, width: 3, kind: "curved", fromSide: "top", toSide: "left" });
  connect(slide, rDeferRoute, refresh, { color: C.teal, width: 3, kind: "curved", style: "dashed", fromSide: "top", toSide: "bottom" });
  connect(slide, refresh, s1.b, { color: C.teal, width: 3, kind: "curved", style: "dashed", fromSide: "bottom", toSide: "bottom" });
  connect(slide, s1.b, targetB, { color: C.teal, width: 3, kind: "curved", style: "dashed", fromSide: "bottom", toSide: "left" });
  textBox(slide, "resolve-s1", "resolve q on S1", 588, 248, 104, 19, {
    size: 9,
    bold: true,
    color: C.teal,
    align: "center",
  });
  textBox(slide, "gold-a-label", "gold target A", 675, 76, 88, 18, {
    size: 10,
    bold: true,
    color: C.coral,
    align: "center",
  });
  textBox(slide, "gold-b-label", "gold target B", 675, 287, 88, 18, {
    size: 10,
    bold: true,
    color: C.teal,
    align: "center",
  });
  textBox(slide, "a-valid", "A survives and remains action-valid in S1", 495, 306, 220, 18, {
    size: 9.5,
    italic: true,
    color: C.coral,
    align: "center",
  });

  // A visible information boundary prevents the gold path from reading as probe input.
  shape(slide, "withheld-divider", "rect", 752, 89, 1.6, 207, {
    fill: C.rule,
    line: C.rule,
    lineWidth: 0,
    style: "dashed",
  });
  circle(slide, "withheld-icon-bg", "", 738, 160, 30, {
    fill: C.white,
    line: C.rule,
    lineWidth: 1.1,
  });
  addIcon(slide, "withheld-icon", "EyeOff", 745, 167, 16, 16, C.muted, 1.8);
  textBox(slide, "withheld-label", "Withheld from probe:\ngold mode/target;\nnormalized selector fields;\ngenerator winner IDs", 692, 187, 115, 46, {
    size: 8,
    italic: true,
    color: C.muted,
    align: "center",
  });

  textBox(slide, "probe-shared", "same probe + interface", 790, 73, 150, 22, {
    size: 11,
    bold: true,
    color: C.charcoal,
    align: "center",
  });
  const probeP = circle(slide, "probe-packet-p", "P", 785, 112, 30, {
    fill: C.coral,
    line: C.coral,
    color: C.white,
    size: 13,
  });
  const probeR = circle(slide, "probe-packet-r", "R", 785, 236, 30, {
    fill: C.teal,
    line: C.teal,
    color: C.white,
    size: 13,
  });
  const probe = shape(slide, "controller-probe", "ellipse", 826, 99, 102, 178, {
    fill: C.white,
    line: C.charcoal,
    lineWidth: 1.8,
  });
  addIcon(slide, "probe-icon", "ScanSearch", 863, 111, 28, 28, C.charcoal, 1.9);
  textBox(slide, "probe-title", "Probe", 842, 140, 70, 22, {
    size: 13,
    bold: true,
    color: C.ink,
    align: "center",
  });
  textBox(slide, "probe-type", "controller black box", 838, 160, 78, 20, {
    size: 8,
    bold: true,
    color: C.muted,
    align: "center",
  });
  textBox(slide, "probe-io", "instruction + history\n+ observed state\n-> target ID", 840, 188, 74, 57, {
    size: 9,
    bold: true,
    color: C.charcoal,
    align: "center",
  });
  const tp = shape(slide, "tp-output", "roundRect", 930, 119, 50, 28, {
    fill: C.coralLight,
    line: C.coral,
    lineWidth: 1.4,
  });
  textBox(slide, "tp-label", "T_P", 934, 121, 42, 24, {
    size: 9,
    bold: true,
    italic: true,
    color: C.coral,
    align: "center",
  });
  const tr = shape(slide, "tr-output", "roundRect", 930, 239, 50, 28, {
    fill: C.tealLight,
    line: C.teal,
    lineWidth: 1.4,
    style: "dashed",
  });
  textBox(slide, "tr-label", "T_R", 934, 241, 42, 24, {
    size: 9,
    bold: true,
    italic: true,
    color: C.teal,
    align: "center",
  });
  connect(slide, probeP, probe, { color: C.coral, width: 2.6, kind: "curved" });
  connect(slide, probeR, probe, { color: C.teal, width: 2.6, kind: "curved", style: "dashed" });
  connect(slide, probe, tp, { color: C.coral, width: 2.6, kind: "curved", fromSide: "right", toSide: "left" });
  connect(slide, probe, tr, { color: C.teal, width: 2.6, kind: "curved", style: "dashed", fromSide: "right", toSide: "left" });
  textBox(slide, "probe-repeat", "two independent runs", 804, 290, 154, 20, {
    size: 9,
    italic: true,
    color: C.muted,
    align: "center",
  });
  textBox(slide, "line-legend", "solid Preserve  |  dashed Reevaluate", 72, 309, 270, 18, {
    size: 9,
    color: C.muted,
    align: "center",
  });

  // The readouts form a narrow evidence trail rather than a third equal panel.
  shape(slide, "evidence-spine", "rect", 1002, 53, 2, 278, {
    fill: C.rule,
    line: C.rule,
    lineWidth: 0,
  });

  metricNode(slide, 1, 63, C.blue);
  addIcon(slide, "pairacc-icon", "BadgeCheck", 1030, 62, 20, 20, C.blue, 1.8);
  textBox(slide, "pairacc-title", "PairAcc", 1055, 58, 84, 28, {
    size: 14,
    bold: true,
    color: C.ink,
  });
  textBox(slide, "pairacc-formula", "T_P=A  AND  T_R=B", 1030, 88, 222, 26, {
    size: 12,
    bold: true,
    italic: true,
    font: "Times New Roman",
    color: C.charcoal,
    align: "center",
  });
  textBox(slide, "pairacc-slice", "complete changed-winner pairs", 1030, 112, 222, 18, {
    size: 9,
    color: C.muted,
    align: "center",
  });
  shape(slide, "metric-separator-1", "rect", 1030, 137, 222, 1, { fill: C.rule, line: C.rule, lineWidth: 0 });

  metricNode(slide, 2, 149, C.coral);
  addIcon(slide, "substitution-icon", "Route", 1030, 148, 20, 20, C.coral, 1.8);
  textBox(slide, "substitution-title", "Conditional substitution", 1055, 144, 197, 28, {
    size: 13,
    bold: true,
    color: C.ink,
  });
  const subA = circle(slide, "sub-a", "A", 1034, 181, 27, {
    fill: C.coral,
    line: C.coral,
    color: C.white,
    size: 12,
  });
  const subRefresh = circle(slide, "sub-refresh", "", 1128, 181, 27, {
    fill: C.white,
    line: C.charcoal,
    lineWidth: 1.4,
  });
  addIcon(slide, "sub-refresh-icon", "Clock3", 1134, 187, 15, 15, C.charcoal, 1.8);
  const subB = circle(slide, "sub-b", "B", 1220, 181, 27, {
    fill: C.teal,
    line: C.teal,
    color: C.white,
    size: 12,
  });
  connect(slide, subA, subRefresh, { color: C.charcoal, width: 1.9 });
  connect(slide, subRefresh, subB, { color: C.charcoal, width: 1.9 });
  textBox(slide, "substitution-flow-label", "correct bind        refresh        final B", 1025, 209, 230, 17, {
    size: 9,
    color: C.text,
    align: "center",
  });
  textBox(slide, "substitution-slice", "eligible Preserve: correct bind + completed refresh + changed winner\n+ surviving, action-valid A", 1025, 226, 230, 34, {
    size: 8.5,
    color: C.muted,
    align: "center",
  });
  shape(slide, "metric-separator-2", "rect", 1030, 267, 222, 1, { fill: C.rule, line: C.rule, lineWidth: 0 });

  metricNode(slide, 3, 278, C.blue);
  addIcon(slide, "execution-icon", "DatabaseZap", 1030, 277, 20, 20, C.blue, 1.8);
  textBox(slide, "execution-title", "Execution subset", 1055, 273, 197, 28, {
    size: 13,
    bold: true,
    color: C.ink,
  });
  const execId = shape(slide, "exec-id", "roundRect", 1032, 307, 48, 28, {
    fill: C.white,
    line: C.charcoal,
    lineWidth: 1.4,
  });
  textBox(slide, "exec-id-label", "ID", 1038, 309, 36, 24, { size: 9, bold: true, align: "center" });
  const execWrite = shape(slide, "exec-write", "roundRect", 1100, 307, 66, 28, {
    fill: C.white,
    line: C.blue,
    lineWidth: 1.2,
  });
  addIcon(slide, "exec-write-icon", "SquarePen", 1107, 314, 14, 14, C.charcoal, 1.8);
  textBox(slide, "exec-write-label", "tool", 1123, 309, 38, 24, { size: 8, bold: true, align: "center" });
  const execDiff = shape(slide, "exec-diff", "roundRect", 1186, 307, 66, 28, {
    fill: C.tealLight,
    line: C.teal,
    lineWidth: 1.2,
  });
  addIcon(slide, "exec-diff-icon", "Database", 1193, 314, 14, 14, C.teal, 1.8);
  textBox(slide, "exec-diff-label", "DIFF", 1209, 309, 38, 24, {
    size: 8,
    bold: true,
    color: C.teal,
    align: "center",
  });
  connect(slide, execId, execWrite, { color: C.blue, width: 1.9 });
  connect(slide, execWrite, execDiff, { color: C.blue, width: 1.9 });
  textBox(slide, "execution-slice", "executed model-issued writes only", 1032, 334, 220, 14, {
    size: 9,
    color: C.muted,
    align: "center",
  });

  slide.speakerNotes.textFrame.setText(
    "[Sources]\n" +
    "- Anonymous TRI manuscript and project AGENTS.md: matched-pair semantics, readout definitions, denominator boundaries, and withheld fields.\n" +
    "- TRI Figure 1: palette, asymmetric composition, and semantic icon language.\n" +
    "- Lucide Icons (ISC License): Layers3, TimerReset, LockKeyhole, RefreshCcw, DatabaseBackup, EyeOff, ScanSearch, BadgeCheck, Route, Clock3, DatabaseZap, SquarePen, Database."
  );
  slide.speakerNotes.setVisible(false);

  const stem = "fig2_tri_diagnostic_workflow_v16_centered";
  const png = await presentation.export({ slide, format: "png", scale: 2 });
  await writeBlob(path.join(OUT, `${stem}.png`), png);
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(OUT, `${stem}.layout.json`), await layout.text());
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,image,notes", maxChars: 50000 });
  await fs.writeFile(path.join(OUT, `${stem}.inspect.ndjson`), inspect.ndjson);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(OUT, `${stem}.pptx`));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
