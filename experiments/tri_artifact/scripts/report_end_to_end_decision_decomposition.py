#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.end_to_end_decision_decomposition import (
    BOOTSTRAP_SAMPLES,
    BOOTSTRAP_SEED,
    MODEL_IDS,
    TASK_FILE_SHA256,
    build_report,
    load_jsonl,
    load_frozen_tasks,
    render_markdown,
    report_implementation_provenance,
    run_implementation_provenance,
    sha256_path,
    validate_run_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "end_to_end_decision_decomposition_v1.json"
TASKS = ROOT / "data" / "call_matched_authorization_ablation_v1.jsonl"
PROTOCOL = ROOT / "reports" / "TRI_end_to_end_decision_decomposition_protocol.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Report the frozen decision-decomposition run.")
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=BOOTSTRAP_SEED)
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Allow smoke or synthetic inputs for debugging; never use as the full evidence report.",
    )
    args = parser.parse_args()

    rows = [row for path in args.input for row in load_jsonl(path)]
    tasks = load_frozen_tasks(TASKS)
    if sha256_path(TASKS) != TASK_FILE_SHA256:
        raise SystemExit("The reporting inventory differs from the frozen task hash.")
    protocol_sha256 = sha256_path(PROTOCOL)
    run_implementation = run_implementation_provenance(ROOT)
    if not args.allow_partial:
        by_model: dict[str, list[dict]] = {}
        for row in rows:
            by_model.setdefault(row.get("model", ""), []).append(row)
        expected_models = set(MODEL_IDS.values())
        if set(by_model) != expected_models:
            raise SystemExit(
                "Full reporting requires exactly Qwen and GLM inputs; observed "
                f"{sorted(by_model)}."
            )
        invalid = {
            model: {
                "rows": len(group),
                "scopes": sorted({str(row.get('run_scope')) for row in group}),
            }
            for model, group in by_model.items()
            if len(group) != 80 or any(row.get("run_scope") != "full" for row in group)
        }
        if invalid:
            raise SystemExit(
                "Full reporting requires 80 full-scope rows per model; "
                f"invalid inputs: {invalid}."
            )
        for model, group in by_model.items():
            validate_run_inventory(
                group,
                model,
                tasks,
                "full",
                protocol_sha256,
                run_implementation,
                require_exact=True,
            )

    report = build_report(rows, seed=args.seed, samples=args.bootstrap_samples)
    report["provenance"]["input_run_files"] = [
        {"path": str(path), "sha256": sha256_path(path), "rows": len(load_jsonl(path))}
        for path in args.input
    ]
    report["provenance"]["report_implementation"] = report_implementation_provenance(ROOT)
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
