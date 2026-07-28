import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT = process.argv[2] || path.resolve("output");

const W = 1280;
const H = 346;

const C = {
  ink: "#264A56",
  muted: "#407A7F",
  teal: "#248D82",
  tealLight: "#E8F5F2",
  coral: "#E56D4E",
  coralLight: "#FCEDE8",
  plum: "#8B6F8E",
  plumLight: "#E8DEE9",
  green: "#60AA84",
  greenLight: "#EDF7F1",
  neutral: "#AEBBB7",
  rule: "#B8C7C9",
  text: "#263238",
  gray: "#66747A",
  white: "#FFFFFF",
  panel: "#F4F7F5",
};

async function writeBlob(filename, blob) {
  await fs.writeFile(filename, new Uint8Array(await blob.arrayBuffer()));
}

function addText(slide, name, text, x, y, w, h, opts = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontFamily: "Arial",
    fontSize: opts.size ?? 17,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    color: opts.color ?? C.text,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
  };
  return shape;
}

function addBox(slide, name, x, y, w, h, opts = {}) {
  const geometry = opts.geometry ?? "roundRect";
  const config = {
    geometry,
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: opts.fill ?? C.white,
    line: {
      style: opts.lineStyle ?? "solid",
      fill: opts.line ?? C.rule,
      width: opts.lineWidth ?? 1.5,
    },
  };
  if (geometry === "roundRect") config.borderRadius = "rounded-md";
  return slide.shapes.add(config);
}

function addCircle(slide, name, label, x, y, diameter, opts = {}) {
  const shape = slide.shapes.add({
    geometry: "ellipse",
    name,
    position: { left: x, top: y, width: diameter, height: diameter },
    fill: opts.fill ?? C.white,
    line: {
      style: opts.lineStyle ?? "solid",
      fill: opts.line ?? C.ink,
      width: opts.lineWidth ?? 2,
    },
  });
  shape.text = label;
  shape.text.style = {
    fontFamily: "Arial",
    fontSize: opts.size ?? 20,
    bold: true,
    color: opts.color ?? opts.line ?? C.ink,
    alignment: "center",
    verticalAlignment: "middle",
  };
  return shape;
}

function connect(slide, from, to, opts = {}) {
  return slide.shapes.connect(from, to, {
    kind: opts.kind ?? "straight",
    fromSide: opts.fromSide ?? "right",
    toSide: opts.toSide ?? "left",
    line: {
      style: opts.style ?? "solid",
      fill: opts.color ?? C.ink,
      width: opts.width ?? 2.5,
    },
    head: { type: "none" },
    tail: opts.arrow === false
      ? { type: "none" }
      : { type: "triangle", width: "sm", length: "sm" },
  });
}

function addPanelHeading(slide, letter, title, x, width) {
  addText(slide, `${letter}-heading`, `${letter}. ${title}`, x, 10, width, 28, {
    size: 21,
    bold: true,
    color: C.ink,
  });
}

function addDatabase(slide, name, x, y, w, h, color) {
  const body = addBox(slide, `${name}-body`, x, y + 6, w, h - 12, {
    geometry: "rect",
    fill: C.white,
    line: color,
    lineWidth: 1.8,
  });
  const top = slide.shapes.add({
    geometry: "ellipse",
    name: `${name}-top`,
    position: { left: x, top: y, width: w, height: 14 },
    fill: C.white,
    line: { style: "solid", fill: color, width: 1.8 },
  });
  const bottom = slide.shapes.add({
    geometry: "arc",
    name: `${name}-bottom`,
    position: { left: x, top: y + h - 14, width: w, height: 14 },
    fill: "none",
    line: { style: "solid", fill: color, width: 1.8 },
  });
  return { body, top, bottom };
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });

  const presentation = Presentation.create({
    slideSize: { width: W, height: H },
  });
  const slide = presentation.slides.add();
  slide.background.fill = C.white;

  // One restrained composition: three stages separated by rules, not cards.
  const sep1 = addBox(slide, "separator-a-b", 716, 13, 2, 320, {
    geometry: "rect",
    fill: C.rule,
    line: C.rule,
    lineWidth: 0,
  });
  const sep2 = addBox(slide, "separator-b-c", 972, 13, 2, 320, {
    geometry: "rect",
    fill: C.rule,
    line: C.rule,
    lineWidth: 0,
  });
  sep1.sendToBack();
  sep2.sendToBack();

  addPanelHeading(slide, "A", "Construct the matched pair", 28, 660);
  addPanelHeading(slide, "B", "Run the pair", 738, 210);
  addPanelHeading(slide, "C", "Observable readouts", 994, 255);

  // A. Fixed world transition and the sole experimental contrast.
  addBox(slide, "fixed-strip", 29, 42, 660, 30, {
    geometry: "roundRect",
    fill: C.panel,
    line: C.rule,
    lineWidth: 1,
  });
  addText(slide, "fixed-text", "Shared across pair: S0, S1, q, action, schema", 45, 45, 390, 24, {
    size: 16,
    bold: true,
    color: C.muted,
  });
  addText(slide, "varied-text", "Varied: commitment timing", 435, 45, 240, 24, {
    size: 16,
    bold: true,
    color: C.coral,
    align: "right",
  });

  addText(slide, "world-label", "SHARED TRANSITION", 32, 81, 150, 20, {
    size: 16,
    bold: true,
    color: C.gray,
  });
  const s0 = addBox(slide, "state-s0", 180, 77, 150, 74, {
    fill: C.coralLight,
    line: C.coral,
    lineWidth: 1.8,
  });
  const s1 = addBox(slide, "state-s1", 455, 77, 206, 74, {
    fill: C.tealLight,
    line: C.teal,
    lineWidth: 1.8,
  });
  addText(slide, "s0-title", "S0", 194, 80, 122, 18, {
    size: 16,
    bold: true,
    color: C.ink,
    align: "center",
  });
  addText(slide, "s0-winner", "q(S0) = A", 194, 99, 122, 27, {
    size: 21,
    bold: true,
    color: C.coral,
    align: "center",
  });
  addText(slide, "s0-time", "winner at S0", 194, 127, 122, 18, {
    size: 16,
    bold: true,
    color: C.gray,
    align: "center",
  });
  addText(slide, "s1-title", "S1", 468, 80, 180, 18, {
    size: 16,
    bold: true,
    color: C.ink,
    align: "center",
  });
  addText(slide, "s1-winner", "q(S1) = B", 468, 99, 180, 25, {
    size: 21,
    bold: true,
    color: C.teal,
    align: "center",
  });
  addText(slide, "s1-valid", "A remains present\nand action-valid", 466, 117, 184, 31, {
    size: 16,
    bold: true,
    color: C.green,
    align: "center",
  });
  connect(slide, s0, s1, { color: C.plum, width: 4 });
  addText(slide, "refresh-label", "refresh", 330, 97, 105, 24, {
    size: 17,
    bold: true,
    color: C.ink,
    align: "center",
  });

  addText(slide, "preserve-label", "PRESERVE", 34, 173, 120, 22, {
    size: 18,
    bold: true,
    color: C.coral,
  });
  addText(slide, "preserve-desc", "bind at S0", 34, 196, 145, 20, {
    size: 16,
    color: C.ink,
  });
  const pStart = addCircle(slide, "preserve-bound-a", "A", 190, 169, 48, {
    fill: C.coralLight,
    line: C.coral,
    color: C.coral,
    size: 20,
  });
  addText(slide, "preserve-bound-text", "bound(A)", 169, 218, 90, 18, {
    size: 16,
    bold: true,
    color: C.coral,
    align: "center",
  });
  const pTarget = addCircle(slide, "preserve-target-a", "A", 620, 169, 48, {
    fill: C.white,
    line: C.coral,
    color: C.coral,
    size: 20,
  });
  connect(slide, pStart, pTarget, { color: C.coral, width: 3.2 });
  addText(slide, "preserve-target-text", "target A", 590, 218, 108, 18, {
    size: 16,
    bold: true,
    color: C.coral,
    align: "center",
  });

  addText(slide, "reevaluate-label", "REEVALUATE", 34, 251, 145, 22, {
    size: 18,
    bold: true,
    color: C.teal,
  });
  addText(slide, "reevaluate-desc", "defer q to S1", 34, 274, 145, 20, {
    size: 16,
    color: C.ink,
  });
  const rStart = addCircle(slide, "reevaluate-deferred-q", "q", 190, 247, 48, {
    fill: C.tealLight,
    line: C.teal,
    color: C.teal,
    size: 20,
  });
  addText(slide, "reevaluate-deferred-text", "deferred(q)", 150, 296, 130, 18, {
    size: 16,
    bold: true,
    color: C.teal,
    align: "center",
  });
  const rTarget = addCircle(slide, "reevaluate-target-b", "B", 620, 247, 48, {
    fill: C.white,
    line: C.teal,
    color: C.teal,
    size: 20,
  });
  connect(slide, rStart, rTarget, { color: C.teal, width: 3.2, style: "dashed" });
  addText(slide, "reevaluate-resolve", "resolve q on S1", 330, 253, 145, 20, {
    size: 16,
    bold: true,
    color: C.teal,
    align: "center",
  });
  addText(slide, "reevaluate-target-text", "target B", 590, 296, 108, 18, {
    size: 16,
    bold: true,
    color: C.teal,
    align: "center",
  });

  // B. Run both members under one probe; controller internals are deliberately unspecified.
  addText(slide, "controller-note", "same probe + interface", 740, 43, 218, 24, {
    size: 16,
    bold: true,
    italic: true,
    color: C.muted,
    align: "center",
  });
  const pInput = addBox(slide, "preserve-input", 744, 89, 46, 44, {
    fill: C.coralLight,
    line: C.coral,
    lineWidth: 1.8,
  });
  addText(slide, "preserve-input-text", "P", 744, 91, 46, 40, {
    size: 21,
    bold: true,
    color: C.coral,
    align: "center",
  });
  const rInput = addBox(slide, "reevaluate-input", 744, 209, 46, 44, {
    fill: C.tealLight,
    line: C.teal,
    lineWidth: 1.8,
  });
  addText(slide, "reevaluate-input-text", "R", 744, 211, 46, 40, {
    size: 21,
    bold: true,
    color: C.teal,
    align: "center",
  });
  const controller = addBox(slide, "controller-probe", 804, 108, 118, 124, {
    fill: C.panel,
    line: C.muted,
    lineWidth: 2,
  });
  addText(slide, "controller-title", "PROBE", 808, 124, 110, 24, {
    size: 16,
    bold: true,
    color: C.muted,
    align: "center",
  });
  addText(slide, "controller-io", "instruction + history\n-> target ID", 808, 155, 110, 52, {
    size: 16,
    bold: true,
    color: C.ink,
    align: "center",
  });
  const tp = addBox(slide, "preserve-output", 924, 96, 48, 36, {
    fill: C.white,
    line: C.coral,
    lineWidth: 1.8,
  });
  addText(slide, "preserve-output-text", "TP", 924, 97, 48, 34, {
    size: 16,
    bold: true,
    color: C.coral,
    align: "center",
  });
  const tr = addBox(slide, "reevaluate-output", 924, 216, 48, 36, {
    fill: C.white,
    line: C.teal,
    lineWidth: 1.8,
  });
  addText(slide, "reevaluate-output-text", "TR", 924, 217, 48, 34, {
    size: 16,
    bold: true,
    color: C.teal,
    align: "center",
  });
  const pInAnchor = addBox(slide, "p-input-anchor", 803, 110, 2, 2, {
    geometry: "ellipse",
    fill: "none",
    line: "none",
    lineWidth: 0,
  });
  const rInAnchor = addBox(slide, "r-input-anchor", 803, 230, 2, 2, {
    geometry: "ellipse",
    fill: "none",
    line: "none",
    lineWidth: 0,
  });
  const pOutAnchor = addBox(slide, "p-output-anchor", 921, 112, 2, 2, {
    geometry: "ellipse",
    fill: "none",
    line: "none",
    lineWidth: 0,
  });
  const rOutAnchor = addBox(slide, "r-output-anchor", 921, 232, 2, 2, {
    geometry: "ellipse",
    fill: "none",
    line: "none",
    lineWidth: 0,
  });
  connect(slide, pInput, pInAnchor, { color: C.coral, width: 2.6 });
  connect(slide, rInput, rInAnchor, { color: C.teal, width: 2.6, style: "dashed" });
  connect(slide, pOutAnchor, tp, { color: C.coral, width: 2.6 });
  connect(slide, rOutAnchor, tr, { color: C.teal, width: 2.6, style: "dashed" });
  addText(slide, "withheld-note", "Gold mode and targets withheld", 741, 276, 224, 36, {
    size: 16,
    bold: true,
    color: C.gray,
    align: "center",
  });

  // C. Three different endpoints, with their slice distinctions visible.
  addBox(slide, "pairacc-readout", 992, 48, 256, 78, {
    fill: C.panel,
    line: C.rule,
    lineWidth: 1.2,
  });
  addText(slide, "pairacc-title", "PairAcc", 1005, 54, 95, 23, {
    size: 18,
    bold: true,
    color: C.ink,
  });
  addText(slide, "pairacc-formula", "[TP = A] AND [TR = B]", 1005, 78, 230, 22, {
    size: 16,
    bold: true,
    color: C.muted,
  });
  addText(slide, "pairacc-slice", "complete changed pairs", 1005, 101, 230, 18, {
    size: 16,
    color: C.gray,
  });

  addBox(slide, "substitution-readout", 992, 135, 256, 86, {
    fill: C.coralLight,
    line: C.coral,
    lineWidth: 1.2,
  });
  addText(slide, "substitution-title", "Conditional substitution", 1005, 141, 230, 23, {
    size: 16,
    bold: true,
    color: C.coral,
  });
  addText(slide, "substitution-formula", "A -> refreshed winner B", 1005, 166, 230, 21, {
    size: 16,
    bold: true,
    color: C.coral,
  });
  addText(slide, "substitution-slice", "strict eligible Preserve rows", 1005, 190, 230, 18, {
    size: 16,
    color: C.gray,
  });

  addBox(slide, "execution-readout", 992, 230, 256, 91, {
    fill: C.greenLight,
    line: C.green,
    lineWidth: 1.2,
  });
  addText(slide, "execution-title", "Execution subset", 1005, 236, 230, 23, {
    size: 17,
    bold: true,
    color: C.ink,
  });
  const db = addBox(slide, "execution-database", 1008, 264, 40, 38, {
    geometry: "can",
    fill: C.white,
    line: C.green,
    lineWidth: 1.8,
  });
  addText(slide, "execution-database-text", "ID", 1008, 267, 40, 30, {
    size: 16,
    bold: true,
    color: C.green,
    align: "center",
  });
  const writeBox = addBox(slide, "write-box", 1058, 268, 82, 30, {
    fill: C.white,
    line: C.plum,
    lineWidth: 1.5,
  });
  addText(slide, "write-text", "WRITE", 1059, 269, 80, 28, {
    size: 16,
    bold: true,
    color: C.ink,
    align: "center",
  });
  const diffBox = addBox(slide, "state-diff-box", 1150, 268, 87, 30, {
    fill: C.white,
    line: C.green,
    lineWidth: 1.5,
  });
  addText(slide, "state-diff-text", "state diff", 1151, 269, 85, 28, {
    size: 16,
    bold: true,
    color: C.green,
    align: "center",
  });
  connect(slide, db, writeBox, { color: C.neutral, width: 2.5 });
  connect(slide, writeBox, diffBox, { color: C.green, width: 2.5 });
  addText(slide, "execution-slice", "executed writes only", 1050, 301, 185, 18, {
    size: 16,
    color: C.gray,
  });

  slide.speakerNotes.textFrame.setText(
    "[Sources]\n" +
    "- Anonymous TRI manuscript: diagnostic construction, controller-probe boundary, and endpoint definitions.\n" +
    "- User-provided Figure 1: palette and visual-language reference only; no external factual content."
  );
  slide.speakerNotes.setVisible(false);

  const png = await presentation.export({ slide, format: "png", scale: 2 });
  await writeBlob(path.join(OUT, "fig2_tri_diagnostic_workflow_v7.png"), png);
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(
    path.join(OUT, "fig2_tri_diagnostic_workflow_v7.layout.json"),
    await layout.text(),
  );
  const inspect = await presentation.inspect({
    kind: "slide,textbox,shape,notes",
    maxChars: 20000,
  });
  await fs.writeFile(
    path.join(OUT, "fig2_tri_diagnostic_workflow_v7.inspect.ndjson"),
    inspect.ndjson,
  );
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(OUT, "fig2_tri_diagnostic_workflow_v7.pptx"));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
