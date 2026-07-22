from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any


REJECT_VALUES = {"REJECT", "INVALID_BOUND_ENTITY"}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    return "REJECT" if text in REJECT_VALUES else text


def majority(values: list[str]) -> str | None:
    value, count = Counter(values).most_common(1)[0]
    return value if count >= 2 else None


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, center - radius), min(1.0, center + radius)]


def load_run(path: Path) -> dict[str, dict[str, Any]]:
    rows = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            rows[row["task"]["id"]] = row
    return rows


def exact_mcnemar(generic: list[bool], treatment: list[bool]) -> dict[str, Any]:
    generic_only = sum(a and not b for a, b in zip(generic, treatment))
    treatment_only = sum(b and not a for a, b in zip(generic, treatment))
    discordant = generic_only + treatment_only
    if discordant == 0:
        p_value = 1.0
    else:
        tail = sum(math.comb(discordant, k) for k in range(min(generic_only, treatment_only) + 1))
        p_value = min(1.0, 2 * tail / (2**discordant))
    return {
        "generic_only": generic_only,
        "treatment_only": treatment_only,
        "exact_mcnemar_p": p_value,
    }


def paired_cluster_bootstrap(
    generic: list[bool],
    treatment: list[bool],
    clusters: list[str],
    samples: int = 10_000,
    seed: int = 20260718,
) -> dict[str, Any]:
    cluster_ids = sorted(set(clusters))
    members = {
        cluster: [index for index, value in enumerate(clusters) if value == cluster]
        for cluster in cluster_ids
    }
    effects = [float(treatment[i]) - float(generic[i]) for i in range(len(generic))]
    rng = random.Random(seed)
    draws = []
    for _ in range(samples):
        selected = [rng.choice(cluster_ids) for _ in cluster_ids]
        indices = [index for cluster in selected for index in members[cluster]]
        draws.append(sum(effects[index] for index in indices) / len(indices))
    draws.sort()
    lower = draws[int(0.025 * samples)]
    upper = draws[min(samples - 1, int(0.975 * samples))]
    return {
        "difference": sum(effects) / len(effects),
        "cluster_95_interval": [lower, upper],
        "n_clusters": len(cluster_ids),
        "samples": samples,
        "seed": seed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forms", nargs=3, required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--run", action="append", nargs=2, metavar=("NAME", "PATH"), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()

    keys = {row["item_id"]: row for row in load_csv(Path(args.key))}
    responses: dict[str, list[str]] = {item_id: [] for item_id in keys}
    for form_path in args.forms:
        for row in load_csv(Path(form_path)):
            responses[row["item_id"]].append(normalize(row["response"]))

    original_ids = [item_id for item_id, key in keys.items() if key["variant"] == "original"]
    determinate = {
        keys[item_id]["source_task_id"]: majority(responses[item_id])
        for item_id in original_ids
        if majority(responses[item_id]) is not None
    }
    majority_gold_sources = {
        keys[item_id]["source_task_id"]
        for item_id in original_ids
        if majority(responses[item_id]) == normalize(keys[item_id]["gold_target"])
    }
    unanimous_gold_sources = {
        keys[item_id]["source_task_id"]
        for item_id in original_ids
        if len(set(responses[item_id])) == 1
        and responses[item_id][0] == normalize(keys[item_id]["gold_target"])
    }

    run_rows = {name: load_run(Path(path)) for name, path in args.run}
    metrics = {}
    correctness: dict[str, list[bool]] = {}
    ordered_sources = sorted(determinate)
    first_run = next(iter(run_rows.values()))
    clusters = [first_run[source]["task"]["template_id"] for source in ordered_sources]
    for rows in run_rows.values():
        observed = [rows[source]["task"]["template_id"] for source in ordered_sources]
        if observed != clusters:
            raise ValueError("Run files disagree on template-cluster identity")
    for name, rows in run_rows.items():
        missing = sorted(set(ordered_sources) - set(rows))
        if missing:
            raise ValueError(f"Run {name} is missing {missing}")
        human_correct = [
            normalize(rows[source]["result"].get("predicted_target")) == determinate[source]
            for source in ordered_sources
        ]
        correctness[name] = human_correct
        majority_gold_correct = [
            bool(rows[source]["result"].get("success")) for source in sorted(majority_gold_sources)
        ]
        unanimous_correct = [
            bool(rows[source]["result"].get("success")) for source in sorted(unanimous_gold_sources)
        ]
        metrics[name] = {
            "human_majority_n": len(human_correct),
            "human_majority_correct": sum(human_correct),
            "human_majority_accuracy": sum(human_correct) / len(human_correct),
            "human_majority_wilson_95": wilson(sum(human_correct), len(human_correct)),
            "majority_gold_subset_n": len(majority_gold_correct),
            "majority_gold_subset_accuracy": sum(majority_gold_correct) / len(majority_gold_correct),
            "unanimous_gold_subset_n": len(unanimous_correct),
            "unanimous_gold_subset_accuracy": sum(unanimous_correct) / len(unanimous_correct),
        }

    comparisons = {}
    for model in ("qwen", "glm"):
        generic_name = f"{model}_generic"
        gated_name = f"{model}_gated"
        if generic_name in correctness and gated_name in correctness:
            comparison = paired_cluster_bootstrap(
                correctness[generic_name], correctness[gated_name], clusters
            )
            comparison["secondary_task_level_mcnemar"] = exact_mcnemar(
                correctness[generic_name], correctness[gated_name]
            )
            comparisons[f"{model}_gated_vs_generic_human_majority"] = comparison

    report = {
        "original_items": len(original_ids),
        "determinate_human_majority_items": len(determinate),
        "majority_supports_gold_items": len(majority_gold_sources),
        "unanimous_supports_gold_items": len(unanimous_gold_sources),
        "runs": metrics,
        "comparisons": comparisons,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Model Results on Human-Validated TRI Subsets",
        "",
        f"Original human items: {len(original_ids)}; determinate majorities: {len(determinate)}; "
        f"majority supports benchmark gold: {len(majority_gold_sources)}; unanimous support: "
        f"{len(unanimous_gold_sources)}.",
        "",
        "| Run | Human-majority accuracy | Majority-gold subset | Unanimous-gold subset |",
        "|---|---:|---:|---:|",
    ]
    for name, row in metrics.items():
        lines.append(
            f"| {name} | {row['human_majority_correct']}/{row['human_majority_n']} "
            f"({row['human_majority_accuracy']:.1%}) | "
            f"{row['majority_gold_subset_accuracy']:.1%} (n={row['majority_gold_subset_n']}) | "
            f"{row['unanimous_gold_subset_accuracy']:.1%} (n={row['unanimous_gold_subset_n']}) |"
        )
    lines.extend(
        [
            "",
            "## Paired comparisons",
            "",
            "Template-cluster bootstrap is primary for this sensitivity; task-level exact",
            "McNemar is retained as a secondary descriptive analysis.",
            "",
            "```json",
            json.dumps(comparisons, indent=2),
            "```",
            "",
        ]
    )
    Path(args.markdown_output).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
