from __future__ import annotations

import argparse
import json
from pathlib import Path

from .v2_model_report import is_api_failure
from .v3_cluster_report import load_jsonl, success, summarize_pair


def summarize_run(rows: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(str(row["task"]["binding"]), []).append(row)
    return {
        "n": len(rows),
        "correct": sum(success(row) for row in rows),
        "accuracy": sum(success(row) for row in rows) / len(rows),
        "api_errors": sum(is_api_failure(row) for row in rows),
        "statuses": sorted({str(row.get("status", "missing")) for row in rows}),
        "binding_slices": {
            name: {
                "n": len(group),
                "correct": sum(success(row) for row in group),
                "accuracy": sum(success(row) for row in group) / len(group),
            }
            for name, group in sorted(groups.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generic", required=True)
    parser.add_argument("--reference-mode", required=True)
    parser.add_argument("--output", default="reports/reference_mode_ablation.json")
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260719)
    args = parser.parse_args()

    generic = load_jsonl(Path(args.generic))
    reference_mode = load_jsonl(Path(args.reference_mode))
    ids_a = {row["task"]["id"] for row in generic}
    ids_b = {row["task"]["id"] for row in reference_mode}
    if len(generic) != 160 or len(reference_mode) != 160 or len(ids_a) != 160 or ids_a != ids_b:
        raise ValueError("Both runs must contain the same 160 unique frozen task IDs")

    pair = summarize_pair(
        Path(args.generic),
        Path(args.reference_mode),
        args.bootstrap_samples,
        args.seed,
    )
    result = {
        "protocol": "post_refresh_generic_representation_ablation",
        "generic_run": str(Path(args.generic)),
        "reference_mode_run": str(Path(args.reference_mode)),
        "n_tasks": 160,
        "generic": summarize_run(generic),
        "reference_mode": summarize_run(reference_mode),
        "comparison": pair,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    markdown = "\n".join([
        "# Generic + reference_mode ablation",
        "",
        "This is a frozen 160-task paired comparison. The treatment adds only an explicit",
        "`reference_mode` field to the Generic Structured Ledger; it adds no guard, fallback,",
        "invalidity policy, or deterministic gate.",
        "",
        "| Generic | Generic + mode | Tasks | Clusters | Delta | Cluster 95% CI |",
        "|---:|---:|---:|---:|---:|---:|",
        f"| {result['generic']['accuracy']:.1%} | {result['reference_mode']['accuracy']:.1%} | "
        f"{pair['n_tasks']} | {pair['n_clusters']} | "
        f"{pair['delta_b_minus_a']:.1%} | "
        f"[{pair['cluster_bootstrap_ci95_low']:.1%}, {pair['cluster_bootstrap_ci95_high']:.1%}] |",
        "",
        "| Binding | Generic | Generic + mode |",
        "|---|---:|---:|",
        *[
            f"| {binding} | {result['generic']['binding_slices'][binding]['accuracy']:.1%} | "
            f"{result['reference_mode']['binding_slices'][binding]['accuracy']:.1%} |"
            for binding in sorted(result["generic"]["binding_slices"])
        ],
        "",
        f"API errors: Generic={result['generic']['api_errors']}; "
        f"Generic+mode={result['reference_mode']['api_errors']}.",
        "",
        "Interpretation is conditional: this comparison identifies the contribution of explicit",
        "mode classification, not the superiority of Lifecycle-Gated or the validity policy.",
        "",
    ])
    output.with_suffix(".md").write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
