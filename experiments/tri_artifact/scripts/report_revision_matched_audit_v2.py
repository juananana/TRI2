#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from tri.revision_matched_audit import (
    BOOTSTRAP_SAMPLES,
    BOOTSTRAP_SEED,
    CONDITIONS,
    build_report,
    exact_target,
    load_jsonl,
    render_markdown,
)


ROOT = Path(__file__).resolve().parents[1]


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return ordered[low]
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def corrected_substitution(
    rows: list[dict[str, Any]], seed: int = BOOTSTRAP_SEED, samples: int = BOOTSTRAP_SAMPLES
) -> dict[str, dict[str, Any]]:
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        clusters[row["task"]["pair_id"]].append(row)

    def eligible(row: dict[str, Any]) -> bool:
        task = row["task"]
        compiler = row.get("compiler", {}).get("parsed") or {}
        return (
            task["actionable_core"]
            and task["reference_mode_gold"] == "preserve"
            and task["pre_refresh_target"] != task["post_refresh_target"]
            and compiler.get("reference_mode") == "preserve"
            and exact_target(compiler.get("bound_target_id")) == task["pre_refresh_target"]
        )

    result = {}
    for condition in CONDITIONS:
        use = [row for row in rows if eligible(row)]

        def violation(row: dict[str, Any]) -> bool:
            return exact_target(row.get("outcomes", {}).get(condition)) == row["task"]["post_refresh_target"]

        numerator = sum(violation(row) for row in use)
        rng = random.Random(seed)
        names = sorted(clusters)
        draws = []
        for _ in range(samples):
            sample = [row for _ in names for row in clusters[rng.choice(names)]]
            selected = [row for row in sample if eligible(row)]
            if selected:
                draws.append(sum(violation(row) for row in selected) / len(selected))
        result[condition] = {
            "numerator": numerator,
            "denominator": len(use),
            "rate": numerator / len(use) if use else None,
            "ci95_cluster": [percentile(draws, 0.025), percentile(draws, 0.975)],
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the denominator-corrected revision report v2.")
    parser.add_argument("--audit", required=True, choices=("full_diagnostic", "human_rewrite", "source_grounded"))
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()
    rows = [row for path in args.inputs for row in load_jsonl(path)]
    report = build_report(rows)
    if report["audit_id"] != args.audit:
        raise SystemExit("Input rows do not match --audit")
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)
    for model in report["models"]:
        corrected = corrected_substitution(by_model[model["model"]])
        for condition in CONDITIONS:
            model["metrics"][condition]["preserve_substitution"] = corrected[condition]
    report["report_version"] = "TRI-revision-matched-audit-report-v2"
    report["report_amendment"] = {
        "status": "post-run zero-API denominator repair",
        "discovered": "during the temporary Qwen full-diagnostic summary",
        "change": "Preserve substitution now requires actionable_core before counting eligibility.",
        "unchanged": [
            "raw outputs",
            "tasks and gold",
            "all ITT accuracy and PairAcc metrics",
            "wrong-write metrics",
            "failure accounting",
        ],
        "superseded_report": f"reports/revision_{args.audit}_v1.json",
    }
    json_output = ROOT / "reports" / f"revision_{args.audit}_v2.json"
    md_output = ROOT / "reports" / f"revision_{args.audit}_v2.md"
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_markdown(report)
    markdown += (
        "\n## Report amendment\n\n"
        "The v1 report mixed author-specified Reject rows into the Preserve-substitution denominator. "
        "V2 requires `actionable_core`; all raw outputs, ITT accuracy, PairAcc, wrong-write, and "
        "failure metrics are unchanged. The v1 report remains in the artifact.\n"
    )
    md_output.write_text(markdown, encoding="utf-8")
    print(json.dumps({"audit": args.audit, "rows": len(rows), "json": str(json_output), "markdown": str(md_output)}, indent=2))


if __name__ == "__main__":
    main()
