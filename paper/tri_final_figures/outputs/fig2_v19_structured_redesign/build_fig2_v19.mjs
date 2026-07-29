import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT = process.argv[2] || path.resolve("output");
const W = 1400;
const H = 500;

const C = {
  ink: "#264A56",
  black: "#0D0D0E",
  text: "#3E4A4E",
  muted: "#708084",
  rule: "#A9B6B8",
  shared: "#407A7F",
  soft: "#F7FAFA",
  coral: "#C12A36",
  coralLight: "#F8E8E9",
  teal: "#248D82",
  tealLight: "#DCEFF0",
  amber: "#EABC6B",
  amberLight: "#FFF5DE",
  white: "#FFFFFF",
};

const TABLER_DIR = "/Users/chu/.codex/skills/drawio-diagram-builder/assets/icons/tabler/outline";

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
      width: opts.lineWidth ?? 1.4,
    },
  });
  if (geometry === "roundRect") item.borderRadius = opts.radius ?? "rounded-sm";
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
    fontSize: opts.size ?? 18,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    color: opts.color ?? C.text,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
  };
  return item;
}

async function addTablerIcon(slide, name, file, x, y, w, h, color) {
  const svg = (await fs.readFile(path.join(TABLER_DIR, file), "utf8")).replaceAll("currentColor", color);
  return slide.images.add({
    blob: new TextEncoder().encode(svg),
    contentType: "image/svg+xml",
    alt: `${file.replace(".svg", "")} icon`,
    fit: "contain",
    position: { left: x, top: y, width: w, height: h },
  });
}

function circle(slide, name, label, x, y, d, opts = {}) {
  const item = shape(slide, name, "ellipse", x, y, d, d, opts);
  if (label) {
    item.text = label;
    item.text.style = {
      fontFamily: opts.font ?? "Arial",
      fontSize: opts.size ?? 18,
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
      fill: opts.color ?? C.ink,
      width: opts.width ?? 2.6,
    },
    cap: "round",
    join: "round",
    head: { type: "none" },
    tail: { type: "stealth", width: "med", length: "med" },
  });
  if (typeof edge.bringToFront === "function") edge.bringToFront();
  return edge;
}

function phaseHeader(slide, letter, title, x, y, width, color) {
  circle(slide, `phase-${letter}`, letter, x, y, 32, {
    fill: color,
    line: color,
    color: C.white,
    size: 16,
  });
  textBox(slide, `phase-${letter}-title`, title, x + 44, y - 1, width - 44, 44, {
    size: 20,
    bold: true,
    color: C.black,
  });
}

function routePill(slide, name, label, x, y, w, h, color, fill, dashed = false, size = 20) {
  const box = shape(slide, `${name}-box`, "roundRect", x, y, w, h, {
    fill,
    line: color,
    lineWidth: 1.8,
    style: dashed ? "dashed" : "solid",
  });
  textBox(slide, `${name}-text`, label, x + 8, y + 5, w - 16, h - 10, {
    size,
    bold: true,
    color,
    align: "center",
  });
  return box;
}

function stateS0(slide, x, y) {
  const outer = shape(slide, "state-s0", "roundRect", x, y, 145, 78, {
    fill: C.white,
    line: C.ink,
    lineWidth: 1.8,
  });
  textBox(slide, "state-s0-label", "S0", x + 10, y + 7, 52, 24, {
    size: 13,
    bold: true,
    italic: true,
    font: "Times New Roman",
    color: C.ink,
  });
  textBox(slide, "state-s0-query", "q(S0)=A", x + 58, y + 7, 77, 24, {
    size: 11,
    italic: true,
    font: "Times New Roman",
    align: "right",
  });
  shape(slide, "state-s0-rule", "rect", x + 10, y + 36, 125, 1, {
    fill: C.rule,
    line: C.rule,
    lineWidth: 0,
  });
  routePill(slide, "state-s0-winner", "A wins", x + 25, y + 43, 95, 28, C.coral, C.coralLight, false, 11);
  return outer;
}

function stateS1(slide, x, y) {
  const outer = shape(slide, "state-s1", "roundRect", x, y, 190, 78, {
    fill: C.white,
    line: C.ink,
    lineWidth: 1.8,
  });
  textBox(slide, "state-s1-label", "S1", x + 10, y + 7, 52, 24, {
    size: 13,
    bold: true,
    italic: true,
    font: "Times New Roman",
    color: C.ink,
  });
  textBox(slide, "state-s1-query", "q(S1)=B", x + 58, y + 7, 122, 24, {
    size: 11,
    italic: true,
    font: "Times New Roman",
    align: "right",
  });
  shape(slide, "state-s1-rule", "rect", x + 10, y + 36, 170, 1, {
    fill: C.rule,
    line: C.rule,
    lineWidth: 0,
  });
  routePill(slide, "state-s1-winner", "B wins", x + 8, y + 43, 82, 28, C.teal, C.tealLight, false, 11);
  routePill(slide, "state-s1-valid", "A valid", x + 100, y + 43, 82, 28, C.coral, C.coralLight, false, 11);
  return outer;
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  const slide = presentation.slides.add();
  slide.background.fill = C.white;

  shape(slide, "divider-ab", "rect", 800, 20, 2, 460, { fill: C.rule, line: C.rule, lineWidth: 0 });
  shape(slide, "divider-bc", "rect", 1075, 20, 2, 460, { fill: C.rule, line: C.rule, lineWidth: 0 });

  phaseHeader(slide, "A", "Construct the matched pair", 20, 18, 770, C.ink);
  phaseHeader(slide, "B", "Run the pair", 815, 18, 250, C.teal);
  phaseHeader(slide, "C", "Readouts", 1090, 18, 290, C.ink);

  shape(slide, "contract", "roundRect", 30, 68, 750, 50, { fill: C.soft, line: "none", lineWidth: 0 });
  await addTablerIcon(slide, "pair-icon", "arrows-right-left.svg", 44, 81, 24, 24, C.shared);
  textBox(slide, "fixed-label", "FIXED CONTRACT", 75, 78, 142, 30, { size: 10, bold: true, color: C.shared });
  textBox(slide, "fixed-items", "S0, S1, q, action, schema, I/O", 225, 78, 292, 30, { size: 12, bold: true, color: C.ink });
  textBox(slide, "change-label", "ONLY CHANGE", 525, 78, 126, 30, { size: 10, bold: true, color: C.teal });
  textBox(slide, "change-items", "commit point", 655, 78, 108, 30, { size: 11, bold: true, color: C.teal, align: "center" });

  shape(slide, "preserve-rule", "rect", 30, 135, 750, 2, { fill: C.coral, line: C.coral, lineWidth: 0 });
  const preserveAnchor = shape(slide, "preserve-anchor", "roundRect", 48, 150, 217, 66, { fill: "none", line: "none", lineWidth: 0 });
  circle(slide, "preserve-token", "P", 48, 160, 42, { fill: C.coral, line: C.coral, color: C.white, size: 18 });
  textBox(slide, "preserve-title", "PRESERVE", 105, 147, 160, 34, { size: 16, bold: true, color: C.coral });
  textBox(slide, "preserve-body", "commit at S0", 105, 182, 160, 30, { size: 13, bold: true, color: C.coral });
  const bind = routePill(slide, "bind", "bind q to A", 300, 151, 170, 58, C.coral, C.white, false, 14);
  const goldA = routePill(slide, "gold-a", "gold A", 680, 154, 82, 52, C.coral, C.white, false, 13);
  connect(slide, preserveAnchor, bind, { color: C.coral, width: 2.8 });
  connect(slide, bind, goldA, { color: C.coral, width: 2.8 });

  shape(slide, "state-rule-top", "rect", 30, 240, 750, 1, { fill: C.rule, line: C.rule, lineWidth: 0 });
  shape(slide, "state-rule-bottom", "rect", 30, 350, 750, 1, { fill: C.rule, line: C.rule, lineWidth: 0 });
  textBox(slide, "shared-state-title", "SHARED STATE", 48, 258, 160, 30, { size: 15, bold: true, color: C.shared });
  textBox(slide, "shared-state-note", "same transition", 48, 290, 160, 28, { size: 11, italic: true, color: C.muted });
  const s0 = stateS0(slide, 220, 255);
  const refresh = circle(slide, "refresh", "", 425, 257, 74, { fill: C.amberLight, line: C.amber, lineWidth: 2, color: C.ink, size: 12 });
  await addTablerIcon(slide, "refresh-icon", "refresh.svg", 446, 268, 32, 32, C.ink);
  textBox(slide, "refresh-label", "refresh", 408, 332, 108, 24, { size: 10, bold: true, color: C.ink, align: "center" });
  const s1 = stateS1(slide, 555, 255);
  connect(slide, s0, refresh, { color: C.ink, width: 2.6 });
  connect(slide, refresh, s1, { color: C.ink, width: 2.6 });

  shape(slide, "reevaluate-rule", "rect", 30, 365, 750, 2, { fill: C.teal, line: C.teal, lineWidth: 0, style: "dashed" });
  const reevaluateAnchor = shape(slide, "reevaluate-anchor", "roundRect", 48, 380, 217, 66, { fill: "none", line: "none", lineWidth: 0 });
  circle(slide, "reevaluate-token", "R", 48, 390, 42, { fill: C.teal, line: C.teal, color: C.white, size: 18 });
  textBox(slide, "reevaluate-title", "REEVALUATE", 105, 376, 175, 34, { size: 16, bold: true, color: C.teal });
  textBox(slide, "reevaluate-body", "commit at S1", 105, 411, 160, 28, { size: 13, bold: true, color: C.teal });
  const resolve = routePill(slide, "resolve", "resolve q to B", 480, 381, 170, 58, C.teal, C.white, true, 14);
  const goldB = routePill(slide, "gold-b", "gold B", 680, 384, 82, 52, C.teal, C.white, true, 13);
  connect(slide, reevaluateAnchor, resolve, { color: C.teal, width: 2.8, style: "dashed" });
  connect(slide, resolve, goldB, { color: C.teal, width: 2.8, style: "dashed" });

  textBox(slide, "withheld", "GOLD WITHHELD", 825, 78, 230, 30, { size: 14, bold: true, color: C.muted, align: "center" });
  shape(slide, "withheld-rule", "rect", 855, 112, 170, 2, { fill: C.rule, line: C.rule, lineWidth: 0 });
  const pRun = circle(slide, "p-run", "P", 828, 188, 44, { fill: C.coral, line: C.coral, color: C.white, size: 18 });
  const rRun = circle(slide, "r-run", "R", 828, 298, 44, { fill: C.teal, line: C.teal, color: C.white, size: 18 });
  const probe = shape(slide, "probe", "roundRect", 880, 155, 120, 220, { fill: C.soft, line: C.ink, lineWidth: 1.8 });
  await addTablerIcon(slide, "probe-icon", "robot.svg", 924, 174, 32, 32, C.ink);
  textBox(slide, "probe-title", "SAME PROBE", 890, 214, 100, 28, { size: 11, bold: true, color: C.ink, align: "center" });
  textBox(slide, "probe-kind", "opaque", 890, 250, 100, 24, { size: 10, italic: true, color: C.muted, align: "center" });
  const tp = routePill(slide, "tp", "T_P", 1014, 188, 55, 44, C.coral, C.coralLight, false, 11);
  const tr = routePill(slide, "tr", "T_R", 1014, 298, 55, 44, C.teal, C.tealLight, true, 11);
  const pIn = circle(slide, "probe-p-in", "", 868, 207, 6, { fill: C.coral, line: C.coral, lineWidth: 0 });
  const pOut = circle(slide, "probe-p-out", "", 1004, 207, 6, { fill: C.coral, line: C.coral, lineWidth: 0 });
  const rIn = circle(slide, "probe-r-in", "", 868, 317, 6, { fill: C.teal, line: C.teal, lineWidth: 0 });
  const rOut = circle(slide, "probe-r-out", "", 1004, 317, 6, { fill: C.teal, line: C.teal, lineWidth: 0 });
  connect(slide, pRun, pIn, { color: C.coral, width: 2.8 });
  connect(slide, rRun, rIn, { color: C.teal, width: 2.8, style: "dashed" });
  connect(slide, pOut, tp, { color: C.coral, width: 2.8 });
  connect(slide, rOut, tr, { color: C.teal, width: 2.8, style: "dashed" });
  textBox(slide, "probe-note", "same I/O; two independent runs", 825, 400, 230, 52, { size: 11, italic: true, color: C.muted, align: "center" });

  textBox(slide, "pairacc-title", "PairAcc", 1100, 75, 270, 32, { size: 16, bold: true, color: C.black });
  routePill(slide, "pairacc-formula", "T_P=A  AND  T_R=B", 1110, 115, 250, 52, C.shared, C.soft, false, 14);
  textBox(slide, "pairacc-slice", "complete pairs", 1110, 168, 250, 28, { size: 11, color: C.muted, align: "center" });
  shape(slide, "readout-sep-1", "rect", 1100, 205, 270, 1, { fill: C.rule, line: C.rule, lineWidth: 0 });

  textBox(slide, "sub-title", "Conditional substitution", 1090, 218, 290, 32, { size: 15, bold: true, color: C.black });
  const subA = circle(slide, "sub-a", "A", 1115, 273, 38, { fill: C.coral, line: C.coral, color: C.white, size: 15 });
  const subRefresh = routePill(slide, "sub-refresh", "refresh", 1178, 266, 100, 52, C.ink, C.amberLight, false, 10);
  const subB = circle(slide, "sub-b", "B", 1300, 273, 38, { fill: C.teal, line: C.teal, color: C.white, size: 15 });
  connect(slide, subA, subRefresh, { color: C.ink, width: 2.2 });
  connect(slide, subRefresh, subB, { color: C.ink, width: 2.2 });
  textBox(slide, "sub-slice", "eligible Preserve", 1110, 320, 250, 28, { size: 11, color: C.muted, align: "center" });
  shape(slide, "readout-sep-2", "rect", 1100, 350, 270, 1, { fill: C.rule, line: C.rule, lineWidth: 0 });

  textBox(slide, "exec-title", "Execution subset", 1100, 365, 220, 32, { size: 14, bold: true, color: C.black });
  await addTablerIcon(slide, "exec-icon", "database-cog.svg", 1330, 368, 24, 24, C.teal);
  const execId = routePill(slide, "exec-id", "ID", 1110, 414, 58, 44, C.ink, C.white, false, 11);
  const execWrite = routePill(slide, "exec-write", "write", 1185, 414, 78, 44, C.shared, C.soft, false, 11);
  const execDiff = routePill(slide, "exec-diff", "state diff", 1280, 414, 90, 44, C.teal, C.tealLight, false, 10);
  connect(slide, execId, execWrite, { color: C.shared, width: 2.2 });
  connect(slide, execWrite, execDiff, { color: C.shared, width: 2.2 });
  textBox(slide, "exec-slice", "executed writes", 1110, 460, 250, 28, { size: 11, color: C.muted, align: "center" });

  slide.speakerNotes.textFrame.setText(
    "[Sources]\n" +
    "- TRI Figure 1: palette and heading family.\n" +
    "- draw_learning/01407-AAAI24.ZhaoA.pdf: large aligned regions.\n" +
    "- draw_learning/accept_ACL_4820_Revealing_Procedural_Reas.pdf: single-baseline method flow.\n" +
    "- draw_learning/26253-AAAI26.GuoZ-NLP.pdf: horizontal semantic bands.\n" +
    "- draw_learning/16627-AAAI26.WangZ-NLP.pdf: compact outcome rows.\n" +
    "- Anonymous TRI manuscript: all scientific labels and boundaries."
  );
  slide.speakerNotes.setVisible(false);

  const stem = "fig2_tri_diagnostic_workflow_v19_structured";
  await writeBlob(path.join(OUT, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 2 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(OUT, `${stem}.layout.json`), await layout.text());
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,notes", maxChars: 50000 });
  await fs.writeFile(path.join(OUT, `${stem}.inspect.ndjson`), inspect.ndjson);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(OUT, `${stem}.pptx`));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
