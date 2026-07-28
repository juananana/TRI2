#!/usr/bin/env python3
"""Build a minimal localhost page that exports a draw.io file as PNG or SVG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


TEMPLATE = """<!doctype html>
<html><head><meta charset=\"utf-8\"><title>{title}</title>
<style>html,body{{margin:0;background:#fff}}iframe{{position:absolute;width:1px;height:1px;opacity:0}}#exported{{display:block;max-width:100%;height:auto;margin:0 auto}}</style>
</head><body><iframe id=\"drawio\" src=\"https://embed.diagrams.net/?embed=1&proto=json&spin=1&ui=min&libraries=0&grid=0&pv=0\"></iframe><img id=\"exported\" alt=\"draw.io export\"><script>
const xml={xml}; const format={fmt}; const scale={scale}; const frame=document.getElementById('drawio'); let sent=false;
function sendExport(){{frame.contentWindow.postMessage(JSON.stringify({{action:'export',format,xml,scale,border:0}}),'https://embed.diagrams.net')}}
window.addEventListener('message',e=>{{if(e.source!==frame.contentWindow||e.origin!=='https://embed.diagrams.net')return;let m=e.data;try{{if(typeof m==='string')m=JSON.parse(m)}}catch(_){{return}}if(!m)return;if(m.event==='export'&&m.data){{document.getElementById('exported').src=m.data;document.title='{title} - exported';return}}if(!sent&&(m.event==='init'||m.event==='configure')){{sent=true;sendExport()}}}});
setTimeout(()=>{{if(!sent){{sent=true;sendExport()}}}},2500);
</script></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("drawio", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--format", choices=("png", "svg"), default="png")
    parser.add_argument("--scale", type=float, default=1.0)
    args = parser.parse_args()
    xml = args.drawio.read_text(encoding="utf-8")
    html = TEMPLATE.format(
        title=args.drawio.name,
        xml=json.dumps(xml),
        fmt=json.dumps(args.format),
        scale=json.dumps(args.scale),
    )
    args.out.write_text(html, encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
