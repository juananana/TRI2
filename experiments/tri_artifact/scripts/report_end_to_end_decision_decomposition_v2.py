#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.end_to_end_decision_decomposition import load_jsonl, sha256_path
from tri.end_to_end_decision_decomposition_v2 import (
    BOOTSTRAP_SAMPLES,
    BOOTSTRAP_SEED,
    MODEL_IDS,
    build_report,
    load_frozen_tasks,
    render_markdown,
    validate_run_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"
DEFAULT_OUTPUT = ROOT / "reports" / "end_to_end_decision_decomposition_v2.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Report Decision Decomposition v2.")
    parser.add_argument("--input", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    parser.add_argument("--seed", type=int, default=BOOTSTRAP_SEED)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()

    rows = [row for path in args.input for row in load_jsonl(path)]
    tasks = load_frozen_tasks(TASKS)
    by_model: dict[str, list[dict]] = {}
    for row in rows:
        by_model.setdefault(row.get("model", ""), []).append(row)
    if not args.allow_partial and set(by_model) != set(MODEL_IDS.values()):
        raise SystemExit("full report requires exactly the three frozen models")
    if not args.allow_partial:
        for model, model_rows in by_model.items():
            validate_run_inventory(model_rows, model, tasks)

    report = build_report(rows, seed=args.seed, samples=args.bootstrap_samples)
    report["provenance"] = {
        "inputs": [
            {"path": str(path), "sha256": sha256_path(path), "rows": len(load_jsonl(path))}
            for path in args.input
        ],
        "task_sha256": sha256_path(TASKS),
        "reporter_sha256": sha256_path(Path(__file__)),
        "core_sha256": sha256_path(ROOT / "tri" / "end_to_end_decision_decomposition_v2.py"),
    }
    markdown = render_markdown(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output.with_suffix(".md").write_text(markdown, encoding="utf-8")
    args.output.with_name(args.output.stem + "_claim_promotion.json").write_text(
        json.dumps(report["claim_promotion"], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(markdown)


if __name__ == "__main__":
    main()
