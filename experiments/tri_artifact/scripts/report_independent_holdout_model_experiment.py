#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tri.call_matched_authorization_ablation import load_jsonl, sha256_path
from tri.independent_holdout_model_experiment import (
    BOOTSTRAP_SAMPLES,
    BOOTSTRAP_SEED,
    MODEL_IDS,
    build_report,
    render_markdown,
    validate_run_row,
)
from tri.independent_language_holdout import validate_model_tasks


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "independent_language_holdout_v1.jsonl"
MANIFEST = ROOT / "reports" / "independent_language_holdout_model_freeze_v1.json"
DEFAULT_OUTPUT = ROOT / "reports" / "independent_language_holdout_model_report_v1.json"


def _validate_full_inputs(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not TASKS.exists() or not MANIFEST.exists():
        raise ValueError("the human-gated task inventory and model freeze manifest are absent")
    tasks = load_jsonl(TASKS)
    validate_model_tasks(tasks)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if sha256_path(TASKS) != manifest.get("task_sha256"):
        raise ValueError("task inventory differs from the frozen hash")
    expected_models = set(MODEL_IDS.values())
    by_model: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_model.setdefault(str(row.get("model", "")), []).append(row)
    if set(by_model) != expected_models:
        raise ValueError(
            f"full report requires exactly the three frozen models: {sorted(expected_models)}"
        )
    expected_ids = {task["id"] for task in tasks}
    expected_tasks = {task["id"]: task for task in tasks}
    for model, model_rows in by_model.items():
        if len(model_rows) != len(tasks):
            raise ValueError(f"{model} has {len(model_rows)} rows; expected {len(tasks)}")
        if {row["task"]["id"] for row in model_rows} != expected_ids:
            raise ValueError(f"{model} does not contain the exact frozen task inventory")
        if any(row["task"] != expected_tasks[row["task"]["id"]] for row in model_rows):
            raise ValueError(f"{model} embeds task content that differs from the frozen inventory")
        if any(row.get("run_scope") != "full" for row in model_rows):
            raise ValueError(f"{model} contains a non-full run row")
        for row in model_rows:
            validate_run_row(row)
            if row.get("task_file_sha256") != manifest.get("task_sha256"):
                raise ValueError(f"{model} task hash differs from the freeze manifest")
            if row.get("protocol_sha256") != manifest.get("protocol_sha256"):
                raise ValueError(f"{model} protocol hash differs from the freeze manifest")
            if row.get("prompt_sha256") != manifest.get("prompt_sha256"):
                raise ValueError(f"{model} prompt hash differs from the freeze manifest")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report the frozen independent-language holdout model experiment without API calls."
    )
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=BOOTSTRAP_SEED)
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Allow smoke or synthetic rows for debugging; never use as the evidence report.",
    )
    args = parser.parse_args()

    rows = [row for path in args.input for row in load_jsonl(path)]
    manifest = None if args.allow_partial else _validate_full_inputs(rows)
    report = build_report(rows, seed=args.seed, samples=args.bootstrap_samples)
    report["provenance"] = {
        "inputs": [
            {"path": str(path), "sha256": sha256_path(path), "rows": len(load_jsonl(path))}
            for path in args.input
        ],
        "freeze_manifest": manifest,
        "partial_debug_report": bool(args.allow_partial),
    }
    markdown = render_markdown(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    args.output.with_suffix(".md").write_text(markdown, encoding="utf-8")
    args.output.with_name(args.output.stem + "_claim_promotion.json").write_text(
        json.dumps(report["claim_promotion"], indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(markdown)


if __name__ == "__main__":
    main()
