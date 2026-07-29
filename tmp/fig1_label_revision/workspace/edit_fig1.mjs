import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const input = "/Users/chu/Documents/Codex/2026-07-15/k-y/TRI/paper/tri_final_figures/outputs/fig1_shared_transition_symmetric_v3_editable.pptx";
const output = "/Users/chu/Documents/Codex/2026-07-15/k-y/TRI/tmp/fig1_label_revision/fig1_shared_transition_symmetric_v3_editable_updated.pptx";
const qaDir = "/Users/chu/Documents/Codex/2026-07-15/k-y/TRI/tmp/fig1_label_revision/qa";

async function writeBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(qaDir, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(input));
const before = await presentation.inspect({
  kind: "slide,textbox,shape",
  search: "REFERENTIAL CONTROL STATE",
  maxChars: 12000,
});
await fs.writeFile(`${qaDir}/before.inspect.ndjson`, before.ndjson);
const record = before.ndjson
  .trim()
  .split("\n")
  .map((line) => JSON.parse(line))
  .find((item) => item.text === "REFERENTIAL CONTROL STATE");
if (!record) throw new Error("Figure 1 heading not found");

const slide = presentation.slides.items[0];
await writeBlob(
  `${qaDir}/before-slide.png`,
  await presentation.export({ slide, format: "png", scale: 1 }),
);
const target = presentation.resolve(record.id);
target.text.replace("REFERENTIAL CONTROL STATE", "REPRESENTED REFERENTIAL STATE");

const after = await presentation.inspect({
  target: { id: record.id, beforeLines: 1, afterLines: 1 },
  kind: "textbox,shape",
  maxChars: 4000,
});
await fs.writeFile(`${qaDir}/after.inspect.ndjson`, after.ndjson);
await writeBlob(
  `${qaDir}/after-slide.png`,
  await presentation.export({ slide, format: "png", scale: 1 }),
);
await fs.writeFile(
  `${qaDir}/after-slide.layout.json`,
  await (await slide.export({ format: "layout" })).text(),
);

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(output);
process.stdout.write(`${after.ndjson}\n${output}\n`);
