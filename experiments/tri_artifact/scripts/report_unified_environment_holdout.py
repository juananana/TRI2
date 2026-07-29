#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tri.unified_environment_holdout import (
    read_jsonl,
    selection_maximizers,
    summarize_executed_results,
    summarize_rule_star,
)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_markdown(report: dict) -> str:
    lines = [
        "# Unified Environment Holdout",
        "",
        f"Evidence status: `{report['evidence_status']}`.",
        "",
        "| Environment | Model | E2E maximizers | PairAcc maximizers | Disjoint |",
        "|---|---|---|---|---|",
    ]
    for cell in report["selection"]["cells"]:
        lines.append(
            "| {environment} | {model} | {e2e} | {pairacc} | {strong} |".format(
                environment=cell["environment"],
                model=cell["model"],
                e2e=", ".join(cell["e2e_maximizers"]),
                pairacc=", ".join(cell["pairacc_maximizers"]),
                strong=cell["strong_selection_change"],
            )
        )
    lines.extend(
        [
            "",
            "Practical-selection promotion gate: "
            f"`{report['selection']['promote_practical_selection']}`.",
            "",
            "Rule* is a formal post-hoc baseline and is excluded from the six-controller "
            "maximizer sets.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report the frozen unified environment execution matrix."
    )
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--freeze-manifest", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--rule-star-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.freeze_manifest.read_text(encoding="utf-8"))
    if not (
        manifest.get("run_version") == "TRI-unified-environment-holdout-v1"
        and manifest.get("human_gate_passed") is True
        and manifest.get("model_calls_allowed") is True
        and manifest.get("execution_rows") == 120
        and manifest.get("locked_execution_sha256") == sha256_path(args.inventory)
    ):
        raise SystemExit("frozen inventory or independent-human gate validation failed")

    frozen = read_jsonl(args.inventory)
    summaries = summarize_executed_results(frozen, read_jsonl(args.results))
    selection = selection_maximizers(summaries)
    rule_star = summarize_rule_star(frozen, read_jsonl(args.rule_star_results))
    frozen_rule_hash = manifest.get("rule_star_source_sha256")
    if not frozen_rule_hash or rule_star["rule_source_sha256"] != frozen_rule_hash:
        raise SystemExit("Rule* source differs from the pre-model freeze manifest")

    report = {
        "run_version": "TRI-unified-environment-holdout-v1",
        "evidence_status": "post-primary independent-human executed holdout",
        "controller_cells": summaries,
        "selection": selection,
        "rule_star": rule_star,
        "provenance": {
            "inventory_sha256": sha256_path(args.inventory),
            "freeze_manifest_sha256": sha256_path(args.freeze_manifest),
            "results_sha256": sha256_path(args.results),
            "rule_star_results_sha256": sha256_path(args.rule_star_results),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    args.output.with_suffix(".md").write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report), end="")


if __name__ == "__main__":
    main()
