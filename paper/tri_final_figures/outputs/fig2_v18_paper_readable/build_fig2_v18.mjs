import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { icons as lucideIcons } from "lucide";

const OUT = process.argv[2] || path.resolve("output");
const W = 960;
const H = 400;

const C = {
  ink: "#0D0D0E",
  charcoal: "#264A56",
  text: "#3E4A4E",
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
  green: "#60AA84",
  white: "#FFFFFF",
  node: "#EFF4F4",
};

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

async function writeBlob(filename, blob) {
  await fs.writeFile(filename, new Uint8Array(await blob.arrayBuffer()));
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
  if (geometry === "roundRect") item.borderRadius = opts.radius ?? "rounded-md";
  return item;
}

function textBox(slide, name, text, x, y, w, h, opts = {}) {
  const item = shape(slide, name, "textbox", x, y, w, h, {
    fill: opts.fill ?? "none",
    line: opts.line ?? "none",
    lineWidth: opts.lineWidth ?? 0,
  });
  item.text = text;
  item.text.style = {
    fontFamily: opts.font ?? "Arial",
    fontSize: opts.size ?? 14,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    color: opts.color ?? C.text,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
  };
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

function connect(slide, from, to, opts = {}) {
  const edge = slide.shapes.connect(from, to, {
    kind: opts.kind ?? "straight",
    fromSide: opts.fromSide ?? "right",
    toSide: opts.toSide ?? "left",
    line: {
      style: opts.style ?? "solid",
      fill: opts.color ?? C.charcoal,
      width: opts.width ?? 2.2,
    },
    cap: "round",
    join: "round",
    head: { type: "none" },
    tail: opts.arrow === false ? { type: "none" } : { type: "stealth", width: "med", length: "med" },
  });
  if (typeof edge.bringToFront === "function") edge.bringToFront();
  return edge;
}

function stateSnapshot(slide, name, x, y, postRefresh = false) {
  const outer = circle(slide, `${name}-outer`, "", x, y, 108, {
    fill: C.white,
    line: C.charcoal,
    lineWidth: 2,
  });
  const candidates = postRefresh
    ? [[18, 21], [25, 72], [55, 16]]
    : [[18, 21], [24, 72], [57, 17], [54, 70]];
  candidates.forEach(([dx, dy], index) => {
    circle(slide, `${name}-candidate-${index}`, "", x + dx, y + dy, 13, {
      fill: C.node,
      line: C.muted,
      lineWidth: 0.8,
    });
  });
  const a = circle(slide, `${name}-A`, "A", x + 69, y + 67, 30, {
    fill: C.coral,
    line: C.coral,
    color: C.white,
    size: 16,
  });
  let b = null;
  if (postRefresh) {
    b = circle(slide, `${name}-B`, "B", x + 69, y + 27, 30, {
      fill: C.teal,
      line: C.teal,
      color: C.white,
      size: 16,
    });
  }
  return { outer, a, b };
}

function modeRow(slide, name, mode, title, body, x, y, color, fill, iconName) {
  const row = shape(slide, `${name}-row`, "roundRect", x, y, 202, 61, {
    fill,
    line: "none",
    lineWidth: 0,
    radius: "rounded-md",
  });
  shape(slide, `${name}-accent`, "rect", x, y + 8, 4, 45, {
    fill: color,
    line: color,
    lineWidth: 0,
  });
  const token = circle(slide, `${name}-token`, mode, x - 14, y + 15, 32, {
    fill: color,
    line: color,
    color: C.white,
    size: 16,
  });
  circle(slide, `${name}-icon-ring`, "", x + 23, y + 11, 39, {
    fill: C.white,
    line: color,
    lineWidth: 1.5,
  });
  addIcon(slide, `${name}-icon`, iconName, x + 32, y + 20, 21, 21, color, 2);
  textBox(slide, `${name}-title`, title, x + 72, y + 4, 124, 25, {
    size: 17,
    bold: true,
    color,
  });
  textBox(slide, `${name}-body`, body, x + 72, y + 29, 124, 25, {
    size: 15,
    bold: true,
    color,
  });
  return { row, token };
}

function targetMarker(slide, name, label, x, y, color) {
  const outer = circle(slide, `${name}-outer`, label, x, y, 38, {
    fill: C.white,
    line: color,
    lineWidth: 2,
    color,
    size: 17,
  });
  shape(slide, `${name}-h`, "rect", x - 4, y + 18, 46, 2, { fill: color, line: color, lineWidth: 0 });
  shape(slide, `${name}-v`, "rect", x + 18, y - 4, 2, 46, { fill: color, line: color, lineWidth: 0 });
  return outer;
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const slide = presentation.slides.add();
  slide.background.fill = C.white;

  textBox(slide, "title", "One transition, two valid commitments", 24, 8, 560, 39, {
    size: 27,
    bold: true,
    color: C.ink,
  });
  textBox(slide, "subtitle", "TRI turns resolution timing into a matched diagnostic.", 26, 45, 560, 25, {
    size: 16,
    bold: true,
    italic: true,
    color: C.tealMid,
  });

  shape(slide, "scene-wash", "ellipse", 15, 79, 930, 220, {
    fill: C.tealWash,
    line: "none",
    lineWidth: 0,
  });
  addIcon(slide, "fixed-icon", "Layers3", 29, 87, 20, 20, C.tealMid, 1.9);
  textBox(slide, "fixed", "FIXED: S0, S1, q, action, schema, I/O", 54, 84, 340, 27, {
    size: 15,
    bold: true,
    color: C.charcoal,
  });
  addIcon(slide, "timing-icon", "TimerReset", 394, 87, 20, 20, C.teal, 1.9);
  textBox(slide, "timing", "ONLY COMMITMENT TIME CHANGES", 419, 84, 296, 27, {
    size: 15,
    bold: true,
    color: C.teal,
  });

  const preserve = modeRow(slide, "preserve", "P", "Preserve", "bind A pre-refresh", 27, 128, C.coral, C.coralLight, "LockKeyhole");
  const reevaluate = modeRow(slide, "reevaluate", "R", "Reevaluate", "resolve q post-refresh", 27, 221, C.teal, C.tealLight, "Hourglass");
  textBox(slide, "pair-label", "MATCHED TASK PAIR", 47, 194, 160, 24, {
    size: 15,
    bold: true,
    color: C.charcoal,
    align: "center",
  });

  const s0 = stateSnapshot(slide, "s0", 240, 139, false);
  const refresh = circle(slide, "refresh", "", 390, 164, 60, {
    fill: C.amberLight,
    line: C.amber,
    lineWidth: 2.4,
  });
  addIcon(slide, "refresh-icon", "RefreshCcw", 405, 179, 30, 30, C.charcoal, 2);
  const s1 = stateSnapshot(slide, "s1", 494, 139, true);

  connect(slide, s0.outer, refresh, { color: C.charcoal, width: 2.6 });
  connect(slide, refresh, s1.outer, { color: C.charcoal, width: 2.6 });
  textBox(slide, "s0-label", "S0", 272, 241, 44, 22, {
    size: 16,
    bold: true,
    italic: true,
    font: "Times New Roman",
    align: "center",
  });
  textBox(slide, "s0-winner", "q(S0)=A", 252, 261, 84, 22, {
    size: 15,
    italic: true,
    font: "Times New Roman",
    align: "center",
  });
  textBox(slide, "refresh-label", "refresh", 375, 225, 90, 22, {
    size: 15,
    bold: true,
    color: C.charcoal,
    align: "center",
  });
  textBox(slide, "s1-label", "S1", 526, 241, 44, 22, {
    size: 16,
    bold: true,
    italic: true,
    font: "Times New Roman",
    align: "center",
  });
  textBox(slide, "s1-winner", "q(S1)=B", 506, 261, 84, 22, {
    size: 15,
    italic: true,
    font: "Times New Roman",
    align: "center",
  });

  const bound = textBox(slide, "bound", "BIND A", 261, 112, 74, 24, {
    size: 15,
    bold: true,
    color: C.coral,
    align: "center",
  });
  const defer = textBox(slide, "defer", "DEFER q", 368, 266, 84, 24, {
    size: 15,
    bold: true,
    color: C.teal,
    align: "center",
  });
  const targetA = targetMarker(slide, "target-a", "A", 640, 121, C.coral);
  const targetB = targetMarker(slide, "target-b", "B", 640, 231, C.teal);
  connect(slide, bound, s0.a, { color: C.coral, width: 3, kind: "curved", fromSide: "bottom", toSide: "top" });
  const preserveTrack = circle(slide, "preserve-track", "", 428, 131, 3, {
    fill: C.coral,
    line: C.coral,
    lineWidth: 0,
  });
  connect(slide, s0.a, preserveTrack, { color: C.coral, width: 3, kind: "straight", fromSide: "top", toSide: "left", arrow: false });
  connect(slide, preserveTrack, s1.a, { color: C.coral, width: 3, kind: "straight", fromSide: "right", toSide: "top" });
  const preserveExit = circle(slide, "preserve-exit", "", 615, 206, 3, {
    fill: C.coral,
    line: C.coral,
    lineWidth: 0,
  });
  connect(slide, s1.a, preserveExit, { color: C.coral, width: 3, kind: "straight", arrow: false });
  connect(slide, preserveExit, targetA, { color: C.coral, width: 3, kind: "straight", fromSide: "right", toSide: "left" });
  connect(slide, defer, refresh, { color: C.teal, width: 3, kind: "curved", style: "dashed", fromSide: "top", toSide: "bottom" });
  connect(slide, refresh, s1.b, { color: C.teal, width: 3, kind: "curved", style: "dashed", fromSide: "bottom", toSide: "bottom" });
  const reevaluateExit = circle(slide, "reevaluate-exit", "", 615, 166, 3, {
    fill: C.teal,
    line: C.teal,
    lineWidth: 0,
  });
  connect(slide, s1.b, reevaluateExit, { color: C.teal, width: 3, kind: "straight", style: "dashed", arrow: false });
  connect(slide, reevaluateExit, targetB, { color: C.teal, width: 3, kind: "straight", style: "dashed", fromSide: "right", toSide: "left" });
  textBox(slide, "target-a-label", "gold A", 623, 101, 72, 20, {
    size: 15,
    bold: true,
    color: C.coral,
    align: "center",
  });
  textBox(slide, "target-b-label", "gold B", 623, 272, 72, 20, {
    size: 15,
    bold: true,
    color: C.teal,
    align: "center",
  });
  addIcon(slide, "valid-icon", "CircleCheck", 495, 282, 18, 18, C.green, 1.9);
  textBox(slide, "valid", "A still valid", 515, 279, 105, 23, {
    size: 15,
    bold: true,
    italic: true,
    color: C.coral,
    align: "center",
  });

  shape(slide, "gold-screen", "rect", 704, 117, 2, 166, {
    fill: C.rule,
    line: C.rule,
    lineWidth: 0,
    style: "dashed",
  });
  circle(slide, "eye-bg", "", 691, 184, 28, {
    fill: C.white,
    line: C.rule,
    lineWidth: 1.2,
  });
  addIcon(slide, "eye", "EyeOff", 697, 190, 16, 16, C.muted, 1.8);
  textBox(slide, "withheld", "NO GOLD INPUT", 648, 285, 116, 22, {
    size: 15,
    bold: true,
    color: C.muted,
    align: "center",
  });

  textBox(slide, "probe-heading", "SAME PROBE", 753, 108, 126, 24, {
    size: 15,
    bold: true,
    color: C.charcoal,
    align: "center",
  });
  const probeP = circle(slide, "probe-p", "P", 724, 148, 30, {
    fill: C.coral,
    line: C.coral,
    color: C.white,
    size: 15,
  });
  const probeR = circle(slide, "probe-r", "R", 724, 226, 30, {
    fill: C.teal,
    line: C.teal,
    color: C.white,
    size: 15,
  });
  const probe = circle(slide, "probe", "", 758, 137, 108, {
    fill: C.white,
    line: C.charcoal,
    lineWidth: 2.2,
  });
  circle(slide, "probe-inner", "", 770, 149, 84, {
    fill: "none",
    line: C.tealMid,
    lineWidth: 1.1,
  });
  addIcon(slide, "probe-icon", "ScanSearch", 795, 161, 34, 34, C.charcoal, 1.9);
  textBox(slide, "probe-title", "Probe", 776, 192, 72, 27, {
    size: 17,
    bold: true,
    color: C.ink,
    align: "center",
  });
  textBox(slide, "probe-kind", "opaque", 767, 216, 90, 22, {
    size: 15,
    bold: true,
    color: C.muted,
    align: "center",
  });
  const tp = shape(slide, "tp", "roundRect", 873, 149, 64, 34, {
    fill: C.coralLight,
    line: C.coral,
    lineWidth: 1.5,
  });
  textBox(slide, "tp-text", "T_P", 880, 153, 50, 26, {
    size: 15,
    bold: true,
    italic: true,
    color: C.coral,
    align: "center",
  });
  const tr = shape(slide, "tr", "roundRect", 873, 224, 64, 34, {
    fill: C.tealLight,
    line: C.teal,
    lineWidth: 1.5,
    style: "dashed",
  });
  textBox(slide, "tr-text", "T_R", 880, 228, 50, 26, {
    size: 15,
    bold: true,
    italic: true,
    color: C.teal,
    align: "center",
  });
  connect(slide, probeP, probe, { color: C.coral, width: 2.5, kind: "curved" });
  connect(slide, probeR, probe, { color: C.teal, width: 2.5, kind: "curved", style: "dashed" });
  connect(slide, probe, tp, { color: C.coral, width: 2.5, kind: "curved" });
  connect(slide, probe, tr, { color: C.teal, width: 2.5, kind: "curved", style: "dashed" });
  textBox(slide, "probe-input", "same inputs", 766, 266, 136, 22, {
    size: 15,
    bold: true,
    color: C.charcoal,
    align: "center",
  });

  shape(slide, "readout-rule", "rect", 218, 315, 718, 2, {
    fill: C.charcoal,
    line: C.charcoal,
    lineWidth: 0,
  });
  textBox(slide, "readout-band-title", "OBSERVABLE READOUTS", 22, 303, 194, 25, {
    size: 15,
    bold: true,
    color: C.tealMid,
    fill: C.white,
    align: "center",
  });
  shape(slide, "readout-sep-1", "rect", 320, 331, 1, 52, { fill: C.rule, line: C.rule, lineWidth: 0 });
  shape(slide, "readout-sep-2", "rect", 630, 331, 1, 52, { fill: C.rule, line: C.rule, lineWidth: 0 });

  addIcon(slide, "pairacc-icon", "BadgeCheck", 34, 338, 25, 25, C.tealMid, 1.9);
  textBox(slide, "pairacc-title", "PairAcc", 68, 331, 112, 30, {
    size: 19,
    bold: true,
    color: C.ink,
  });
  textBox(slide, "pairacc-formula", "P -> A  AND  R -> B", 68, 360, 224, 28, {
    size: 16,
    bold: true,
    italic: true,
    font: "Times New Roman",
    color: C.charcoal,
  });

  addIcon(slide, "sub-icon", "Route", 342, 338, 25, 25, C.coral, 1.9);
  textBox(slide, "sub-title", "Conditional substitution", 376, 331, 238, 30, {
    size: 18,
    bold: true,
    color: C.ink,
  });
  textBox(slide, "sub-flow", "A bound  ->  refresh  ->  B final", 376, 360, 238, 28, {
    size: 15,
    bold: true,
    color: C.charcoal,
    align: "center",
  });

  addIcon(slide, "exec-icon", "DatabaseZap", 650, 338, 25, 25, C.tealMid, 1.9);
  textBox(slide, "exec-title", "Execution subset", 684, 331, 224, 30, {
    size: 18,
    bold: true,
    color: C.ink,
  });
  textBox(slide, "exec-flow", "ID -> write -> state diff", 672, 360, 266, 28, {
    size: 15,
    bold: true,
    color: C.charcoal,
    align: "center",
  });

  slide.speakerNotes.textFrame.setText(
    "[Sources]\n" +
    "- TRI Figure 1: title/subtitle hierarchy, tropical-forest palette, central refresh lens, and bottom explanatory band.\n" +
    "- Anonymous TRI manuscript and AGENTS.md: matched-pair semantics, fixed variables, information boundary, and readout definitions.\n" +
    "- Lucide Icons (ISC): Layers3, TimerReset, LockKeyhole, Hourglass, RefreshCcw, CircleCheck, EyeOff, ScanSearch, BadgeCheck, Route, DatabaseZap."
  );
  slide.speakerNotes.setVisible(false);

  const stem = "fig2_tri_diagnostic_workflow_v18_paper_readable";
  await writeBlob(path.join(OUT, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 2 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(OUT, `${stem}.layout.json`), await layout.text());
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,image,notes", maxChars: 60000 });
  await fs.writeFile(path.join(OUT, `${stem}.inspect.ndjson`), inspect.ndjson);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(OUT, `${stem}.pptx`));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
