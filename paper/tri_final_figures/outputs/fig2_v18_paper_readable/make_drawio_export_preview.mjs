import fs from "node:fs/promises";
import path from "node:path";

const input = process.argv[2] || "fig2_tri_diagnostic_workflow_v18_paper_readable.drawio";
const output = process.argv[3] || "drawio-export-preview-v18.html";
const xml = await fs.readFile(input, "utf8");

const html = `<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>TRI Figure 2 v18 canvas</title>
<style>
  html, body { margin: 0; min-height: 100%; background: #ffffff; }
  body { display: grid; place-items: center; padding: 20px; box-sizing: border-box; }
  #render { display: block; width: min(96vw, 1600px); height: auto; }
  #drawio { position: fixed; left: -10000px; top: -10000px; width: 960px; height: 400px; border: 0; }
  #status { font: 16px Arial, sans-serif; color: #264a56; }
</style>
</head>
<body>
<div id="status">Rendering editable draw.io source...</div>
<img id="render" alt="TRI Figure 2 v18" hidden />
<iframe id="drawio" src="https://embed.diagrams.net/?embed=1&proto=json&spin=1&ui=min&libraries=0&grid=0&pv=0"></iframe>
<script>
const xml = ${JSON.stringify(xml)};
const origin = "https://embed.diagrams.net";
const frame = document.getElementById("drawio");
const image = document.getElementById("render");
const status = document.getElementById("status");
let requested = false;

function requestExport() {
  if (requested) return;
  requested = true;
  frame.contentWindow.postMessage(JSON.stringify({
    action: "export",
    format: "png",
    xml,
    scale: 2,
    border: 0,
    background: "#ffffff"
  }), origin);
}

window.addEventListener("message", (event) => {
  if (event.source !== frame.contentWindow || event.origin !== origin) return;
  let message = event.data;
  try { if (typeof message === "string") message = JSON.parse(message); } catch { return; }
  if (!message) return;
  if (message.event === "init" || message.event === "configure") {
    requestExport();
  } else if (message.event === "export" && message.data) {
    image.src = message.data;
    image.hidden = false;
    status.remove();
  }
});

setTimeout(requestExport, 2500);
</script>
</body>
</html>`;

await fs.writeFile(path.resolve(output), html, "utf8");
