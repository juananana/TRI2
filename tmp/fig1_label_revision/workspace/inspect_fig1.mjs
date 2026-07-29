import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const input = "/Users/chu/Documents/Codex/2026-07-15/k-y/TRI/paper/tri_final_figures/outputs/fig1_shared_transition_symmetric_v3_editable.pptx";
const presentation = await PresentationFile.importPptx(await FileBlob.load(input));
const snapshot = await presentation.inspect({
  kind: "slide,textbox,shape",
  search: "REFERENTIAL CONTROL STATE",
  maxChars: 12000,
});
process.stdout.write(snapshot.ndjson);
