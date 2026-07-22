from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
DEFAULT_RUNS = {
    "Qwen Generic": "20260717T025047Z_Qwen_Qwen3.5-122B-A10B_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl",
    "Qwen Generic + validity gate": "v3_factorial_qwen_primary_generic_validity_gate.jsonl",
    "Qwen Untyped plan": "v3_prefrefresh_untyped_qwen_full.jsonl",
    "Qwen Historical CTA": "v3_exact_predecessor_qwen_full.jsonl",
    "Qwen Lifecycle-free": "v3_factorial_qwen_primary_lifecycle_free.jsonl",
    "Qwen Lifecycle-Gated": "20260717T030034Z_Qwen_Qwen3.5-122B-A10B_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl",
    "GLM Generic": "20260717T032824Z_Pro_zai-org_GLM-5.1_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl",
    "GLM Generic + validity gate": "v3_factorial_glm_primary_generic_validity_gate.jsonl",
    "GLM Untyped plan": "v3_prefrefresh_untyped_glm_full.jsonl",
    "GLM Historical CTA": "v3_exact_predecessor_glm_full.jsonl",
    "GLM Lifecycle-free": "v3_factorial_glm_primary_lifecycle_free.jsonl",
    "GLM Lifecycle-Gated": "20260717T034201Z_Pro_zai-org_GLM-5.1_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl",
}


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def summarize(rows: list[dict]) -> dict[str, dict[str, float | int]]:
    slices = {
        "actionable_referential_core": lambda row: row["task"]["correct_target"]
        != "INVALID_BOUND_ENTITY",
        "author_specified_reject_policy": lambda row: row["task"]["correct_target"]
        == "INVALID_BOUND_ENTITY",
    }
    result = {}
    for label, predicate in slices.items():
        selected = [row for row in rows if predicate(row)]
        correct = sum(bool(row.get("result", {}).get("success")) for row in selected)
        result[label] = {
            "n": len(selected),
            "correct": correct,
            "accuracy": correct / len(selected),
        }
    return result


def paired_cluster_difference(
    baseline: list[dict],
    treatment: list[dict],
    reject_policy: bool,
    samples: int = 10_000,
    seed: int = 20260718,
) -> dict[str, float | int | list[float]]:
    baseline_by_id = {row["task"]["id"]: row for row in baseline}
    treatment_by_id = {row["task"]["id"]: row for row in treatment}
    ids = sorted(
        task_id
        for task_id, row in baseline_by_id.items()
        if (row["task"]["correct_target"] == "INVALID_BOUND_ENTITY") == reject_policy
    )
    if set(ids) - set(treatment_by_id):
        raise ValueError("Treatment run is missing paired tasks")
    effects = {
        task_id: float(treatment_by_id[task_id]["result"]["success"])
        - float(baseline_by_id[task_id]["result"]["success"])
        for task_id in ids
    }
    clusters: dict[str, list[str]] = {}
    for task_id in ids:
        cluster = baseline_by_id[task_id]["task"]["template_id"]
        clusters.setdefault(cluster, []).append(task_id)
    cluster_ids = sorted(clusters)
    rng = random.Random(seed)
    draws = []
    for _ in range(samples):
        selected = [rng.choice(cluster_ids) for _ in cluster_ids]
        sampled_ids = [task_id for cluster in selected for task_id in clusters[cluster]]
        draws.append(sum(effects[task_id] for task_id in sampled_ids) / len(sampled_ids))
    draws.sort()
    return {
        "difference": sum(effects.values()) / len(effects),
        "cluster_95_interval": [draws[int(0.025 * samples)], draws[int(0.975 * samples)]],
        "n": len(ids),
        "n_clusters": len(cluster_ids),
        "samples": samples,
        "seed": seed,
    }


def markdown(results: dict[str, dict], comparisons: dict[str, dict]) -> str:
    lines = [
        "# Referential-Core and Reject-Policy Sensitivity",
        "",
        "This post-primary sensitivity uses unchanged frozen TRI-v3 runs. The actionable",
        "referential core excludes the 32 anchored remove/invalidate items whose benchmark",
        "target is the author-specified `INVALID_BOUND_ENTITY` execution outcome.",
        "",
        "| Run | Actionable referential core | Author-specified reject policy |",
        "|---|---:|---:|",
    ]
    for name, values in results.items():
        core = values["actionable_referential_core"]
        reject = values["author_specified_reject_policy"]
        lines.append(
            f"| {name} | {core['correct']}/{core['n']} ({100 * core['accuracy']:.1f}%) "
            f"| {reject['correct']}/{reject['n']} ({100 * reject['accuracy']:.1f}%) |"
        )
    lines.extend(
        [
            "",
            "## Paired template-cluster sensitivity",
            "",
            "```json",
            json.dumps(comparisons, indent=2),
            "```",
            "",
            "The split does not redefine benchmark gold or replace the pre-specified total",
            "accuracy. It prevents the normative invalid-target policy from being interpreted",
            "as if it had the same human support as Preserve/Reevaluate referential judgments.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "reports" / "v3_referential_policy_slices.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=ROOT / "reports" / "v3_referential_policy_slices.md",
    )
    args = parser.parse_args()

    loaded = {name: load(RUNS / filename) for name, filename in DEFAULT_RUNS.items()}
    results = {name: summarize(rows) for name, rows in loaded.items()}
    comparisons = {}
    for model in ("Qwen", "GLM"):
        for baseline_name in ("Generic", "Historical CTA"):
            for reject_policy, slice_name in ((False, "actionable_core"), (True, "reject_policy")):
                key = f"{model}_Gated_minus_{baseline_name.replace(' ', '_')}_{slice_name}"
                comparisons[key] = paired_cluster_difference(
                    loaded[f"{model} {baseline_name}"],
                    loaded[f"{model} Lifecycle-Gated"],
                    reject_policy,
                )
    payload = {
        "status": "post_primary_sensitivity",
        "definition": {
            "actionable_referential_core": "correct_target != INVALID_BOUND_ENTITY",
            "author_specified_reject_policy": "correct_target == INVALID_BOUND_ENTITY",
        },
        "runs": results,
        "comparisons": comparisons,
    }
    args.json_output.write_text(json.dumps(payload, indent=2) + "\n")
    args.markdown_output.write_text(markdown(results, comparisons))


if __name__ == "__main__":
    main()
