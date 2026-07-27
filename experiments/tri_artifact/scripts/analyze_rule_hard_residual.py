#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from tri.rule_hard_residual import build_report, markdown


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


def main() -> None:
    report = build_report(
        RUNS / "deterministic_discourse_rule_v2_v7.jsonl",
        {
            "Qwen / History-only": RUNS / "v7_qwen_interactive_matched_full_v1.jsonl",
            "Qwen / Timing-reminder": RUNS / "v7_qwen_full_history_once_matched_full_v1.jsonl",
            "Qwen / CTA": RUNS / "v7_qwen_compile_then_act_full.jsonl",
            "GLM / History-only": RUNS / "v7_glm_interactive_matched_full_v1.jsonl",
            "GLM / Timing-reminder": RUNS / "v7_glm_full_history_once_matched_full_v1.jsonl",
            "GLM / CTA": RUNS / "v7_glm_compile_then_act_full.jsonl",
            "DeepSeek / History-only": RUNS / "v7_deepseek_interactive_matched_full_v1.jsonl",
            "DeepSeek / Timing-reminder": RUNS / "v7_deepseek_full_history_once_matched_full_v1.jsonl",
            "DeepSeek / CTA": RUNS / "v7_deepseek_compile_then_act_full_v1.jsonl",
        },
    )
    json_path = ROOT / "reports" / "rule_hard_residual_v1.json"
    md_path = ROOT / "reports" / "rule_hard_residual_v1.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
