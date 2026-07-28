#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tri.decision_block_stratification import (
    authored_stratification,
    interface_redundancy,
    load_jsonl,
    render_markdown,
    sha256_path,
    v7_boundary,
    validate_complete_matched_rows,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "decision_block_stratification_v1.json"

MATCHED_INPUTS = {
    "Authored / Qwen": ("runs/revision_full_diagnostic_qwen_full_v1.jsonl", 160),
    "Authored / GLM": ("runs/revision_full_diagnostic_glm_full_v1.jsonl", 160),
    "Rewrite / Qwen": ("runs/revision_human_rewrite_qwen_full_v1.jsonl", 50),
    "Rewrite / GLM": ("runs/revision_human_rewrite_glm_full_v1.jsonl", 50),
    "Source-derived / Qwen": ("runs/revision_source_grounded_qwen_full_v1.jsonl", 60),
    "Source-derived / GLM": ("runs/revision_source_grounded_glm_full_v1.jsonl", 60),
    "Source-derived / DeepSeek": ("runs/revision_source_grounded_deepseek_full_v1.jsonl", 60),
    "Cross-schema matched / Qwen": ("runs/call_matched_authorization_qwen_full_v2.jsonl", 80),
    "Cross-schema matched / GLM": ("runs/call_matched_authorization_glm_full_v2.jsonl", 80),
}

V7_INPUTS = {
    "Qwen": {
        "Generic": "runs/v7_qwen_generic_structured_ledger_then_act_full.jsonl",
        "Historical CTA": "runs/v7_qwen_compile_then_act_full.jsonl",
        "Lifecycle-Gated": "runs/v7_qwen_factorized_hybrid_compile_then_act_full.jsonl",
    },
    "GLM": {
        "Generic": "runs/v7_glm_generic_structured_ledger_then_act_full.jsonl",
        "Historical CTA": "runs/v7_glm_compile_then_act_full.jsonl",
        "Lifecycle-Gated": "runs/v7_glm_factorized_hybrid_compile_then_act_full.jsonl",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the zero-API decision-block stratification audit.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    matched: dict[str, list[dict[str, Any]]] = {}
    inputs: list[dict[str, Any]] = []
    for label, (relative, expected) in MATCHED_INPUTS.items():
        path = args.root / relative
        rows = load_jsonl(path)
        validate_complete_matched_rows(rows, expected)
        matched[label] = rows
        inputs.append({"path": relative, "rows": len(rows), "sha256": sha256_path(path)})

    authored = {
        "Qwen": authored_stratification(matched["Authored / Qwen"]),
        "GLM": authored_stratification(matched["Authored / GLM"]),
    }
    redundancy = {
        label: {"rows": len(rows), "checks": interface_redundancy(rows)}
        for label, rows in matched.items()
    }

    v7: dict[str, dict[str, Any]] = {}
    for model, controllers in V7_INPUTS.items():
        v7[model] = {}
        for controller, relative in controllers.items():
            path = args.root / relative
            rows = load_jsonl(path)
            if len(rows) != 240:
                raise ValueError(f"expected 240 v7 rows for {model}/{controller}, found {len(rows)}")
            v7[model][controller] = v7_boundary(rows, controller)
            inputs.append({"path": relative, "rows": len(rows), "sha256": sha256_path(path)})

    report = {
        "report_version": "TRI-decision-block-stratification-v1",
        "evidence_status": "post-primary zero-API descriptive audit",
        "interpretation_boundary": (
            "Compiler-quality strata are post-treatment and descriptive. They are not mediation "
            "estimates or causal effects of individual decision-block fields. The v7 table is an "
            "unmatched end-to-end boundary comparison."
        ),
        "authored_stratification": authored,
        "interface_redundancy": redundancy,
        "interface_redundancy_pooled": {
            "rows": sum(len(rows) for rows in matched.values()),
            "checks": interface_redundancy([row for rows in matched.values() for row in rows]),
        },
        "v7_end_to_end_boundary": v7,
        "inputs": inputs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown = render_markdown(report)
    args.output.with_suffix(".md").write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
