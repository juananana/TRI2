#!/usr/bin/env python3
import json
from pathlib import Path

from tri.binding_drift_tri_report import build_report, markdown


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    report = build_report(
        ROOT / "data" / "binding_drift_tri_symmetric_smoke_v1.jsonl",
        ROOT / "runs" / "binding_drift_tri_qwen_self_reverify_smoke_v1.jsonl",
        ROOT / "runs" / "binding_drift_tri_glm_self_reverify_smoke_v1.jsonl",
        ROOT / "runs" / "v7_qwen_compile_then_act_full.jsonl",
        ROOT / "runs" / "v7_glm_compile_then_act_full.jsonl",
    )
    json_path = ROOT / "reports" / "binding_drift_tri_symmetric_smoke_v1.json"
    md_path = ROOT / "reports" / "binding_drift_tri_symmetric_smoke_v1.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
