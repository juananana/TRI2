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


def normalize(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    return "REJECT" if text in REJECT_VALUES else text


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def majority(values: list[str]) -> str | None:
    value, count = Counter(values).most_common(1)[0]
    return value if count >= 2 else None


def exact_mcnemar(baseline: list[bool], treatment: list[bool]) -> dict[str, Any]:
    baseline_only = sum(a and not b for a, b in zip(baseline, treatment))
    treatment_only = sum(b and not a for a, b in zip(baseline, treatment))
    discordant = baseline_only + treatment_only
    if discordant == 0:
        p_value = 1.0
    else:
        tail = sum(math.comb(discordant, k) for k in range(min(baseline_only, treatment_only) + 1))
        p_value = min(1.0, 2 * tail / (2**discordant))
    return {
        "baseline_only": baseline_only,
        "treatment_only": treatment_only,
        "exact_mcnemar_p": p_value,
    }


def cluster_bootstrap(
    baseline: list[bool],
    treatment: list[bool],
    clusters: list[str],
    samples: int = 10_000,
    seed: int = 20260719,
) -> dict[str, Any]:
    cluster_ids = sorted(set(clusters))
    members = {
        cluster: [index for index, value in enumerate(clusters) if value == cluster]
        for cluster in cluster_ids
    }
    effects = [float(b) - float(a) for a, b in zip(baseline, treatment)]
    rng = random.Random(seed)
    draws = []
    for _ in range(samples):
        selected = [rng.choice(cluster_ids) for _ in cluster_ids]
        indices = [index for cluster in selected for index in members[cluster]]
        draws.append(sum(effects[index] for index in indices) / len(indices))
    draws.sort()
    return {
        "difference": sum(effects) / len(effects),
        "cluster_95_interval": [draws[int(0.025 * samples)], draws[int(0.975 * samples)]],
        "n_clusters": len(cluster_ids),
        "samples": samples,
        "seed": seed,
        "secondary_task_level_mcnemar": exact_mcnemar(baseline, treatment),
    }


def human_rewrite_majorities(
    forms: list[Path], key_path: Path
) -> tuple[dict[str, str], set[str], set[str]]:
    key_rows = read_csv(key_path)
    key = {row["item_id"]: row for row in key_rows}
    responses: dict[str, list[str]] = {item_id: [] for item_id in key}
    for form in forms:
        for row in read_csv(form):
            responses[row["item_id"]].append(normalize(row["response"]))
    determinate = {}
    majority_gold = set()
    unanimous_gold = set()
    for item_id, row in key.items():
        if row["variant"] != "human_rewrite":
            continue
        values = responses[item_id]
        vote = majority(values)
        if vote is not None:
            determinate[row["source_task_id"]] = vote
            if vote == normalize(row["gold_target"]):
                majority_gold.add(row["source_task_id"])
        if len(set(values)) == 1 and values[0] == normalize(row["gold_target"]):
            unanimous_gold.add(row["source_task_id"])
    return determinate, majority_gold, unanimous_gold


def accuracy(correct: list[bool]) -> dict[str, int | float]:
    return {"n": len(correct), "correct": sum(correct), "accuracy": sum(correct) / len(correct)}


def action_valid(target: str, task: dict[str, Any]) -> bool:
    if normalize(target) == "REJECT":
        return False
    entity = next((item for item in task["refreshed_state"] if item["id"] == target), None)
    if entity is None:
        return False
    return all(
        entity.get(field) == value
        for field, value in task.get("action_schema", {}).get("preconditions", {}).items()
    )


def grouped_accuracy(
    ordered_ids: list[str], tasks: dict[str, dict[str, Any]], correct: list[bool], field: str
) -> dict[str, dict[str, int | float]]:
    groups: dict[str, list[bool]] = {}
    for index, task_id in enumerate(ordered_ids):
        groups.setdefault(str(tasks[task_id][field]), []).append(correct[index])
    return {name: accuracy(values) for name, values in sorted(groups.items())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--forms", nargs=3, required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--run", action="append", nargs=2, metavar=("NAME", "PATH"), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()

    tasks = read_jsonl(Path(args.data))
    expected = {task["id"]: task for task in tasks}
    if len(expected) != 50:
        raise ValueError(f"Expected 50 unique frozen tasks, found {len(expected)}")
    ordered_ids = sorted(expected)
    majorities, majority_gold, unanimous_gold = human_rewrite_majorities(
        [Path(path) for path in args.forms], Path(args.key)
    )

    runs = {}
    correctness = {}
    for name, path_text in args.run:
        rows = read_jsonl(Path(path_text))
        by_id = {row["task"]["id"]: row for row in rows}
        if len(rows) != 50 or len(by_id) != 50 or set(by_id) != set(expected):
            raise ValueError(
                f"{name}: expected exactly 50 unique frozen IDs, got {len(rows)} rows and {len(by_id)} IDs"
            )
        gold = [
            by_id[task_id].get("status") == "ok"
            and bool(by_id[task_id].get("result", {}).get("success"))
            for task_id in ordered_ids
        ]
        correctness[name] = gold
        human_ids = [task_id for task_id in ordered_ids if task_id in majorities]
        human = [
            by_id[task_id].get("status") == "ok"
            and normalize(by_id[task_id].get("result", {}).get("predicted_target"))
            == majorities[task_id]
            for task_id in human_ids
        ]
        human_actionable_ids = [task_id for task_id in human_ids if majorities[task_id] != "REJECT"]
        human_actionable = [
            by_id[task_id].get("status") == "ok"
            and normalize(by_id[task_id].get("result", {}).get("predicted_target"))
            == majorities[task_id]
            for task_id in human_actionable_ids
        ]
        majority_gold_correct = [
            gold[index]
            for index, task_id in enumerate(ordered_ids)
            if task_id in majority_gold
        ]
        unanimous_gold_correct = [
            gold[index]
            for index, task_id in enumerate(ordered_ids)
            if task_id in unanimous_gold
        ]
        actionable = [
            gold[index]
            for index, task_id in enumerate(ordered_ids)
            if expected[task_id]["correct_target"] != "INVALID_BOUND_ENTITY"
        ]
        reject_policy = [
            gold[index]
            for index, task_id in enumerate(ordered_ids)
            if expected[task_id]["correct_target"] == "INVALID_BOUND_ENTITY"
        ]
        statuses = Counter(row.get("status", "missing") for row in rows)
        errors = Counter()
        for task_id in ordered_ids:
            row = by_id[task_id]
            task = expected[task_id]
            predicted = normalize(row.get("result", {}).get("predicted_target"))
            gold_target = normalize(task["correct_target"])
            if predicted != gold_target and predicted != "REJECT":
                errors["wrong_target_attempt"] += 1
            if predicted != "REJECT" and not action_valid(predicted, task):
                errors["invalid_target_attempt"] += 1
            if predicted == "REJECT" and gold_target != "REJECT":
                errors["unnecessary_rejection"] += 1
            if row.get("result", {}).get("drift_to_new_leader"):
                errors["drift_to_new_leader"] += 1
        runs[name] = {
            "path": str(Path(path_text)),
            "gold": accuracy(gold),
            "human_majority": accuracy(human),
            "human_majority_n": len(human_ids),
            "human_majority_actionable": accuracy(human_actionable),
            "majority_gold_subset": accuracy(majority_gold_correct),
            "unanimous_gold_subset": accuracy(unanimous_gold_correct),
            "actionable_core": accuracy(actionable),
            "author_specified_reject_policy": accuracy(reject_policy),
            "statuses": dict(statuses),
            "slices": {
                "binding": grouped_accuracy(ordered_ids, expected, gold, "binding"),
                "explicitness": grouped_accuracy(ordered_ids, expected, gold, "phenomenon"),
                "update": grouped_accuracy(ordered_ids, expected, gold, "update"),
                "template": grouped_accuracy(ordered_ids, expected, gold, "template_id"),
            },
            "errors": dict(errors),
            "api_request_attempts": sum(row.get("api_request_attempts", 0) for row in rows),
            "api_retries": sum(row.get("api_retries", 0) for row in rows),
        }

    clusters = [expected[task_id]["template_id"] for task_id in ordered_ids]
    comparisons = {}
    for model in ("qwen", "glm"):
        generic = f"{model}_generic"
        if generic not in correctness:
            continue
        for treatment in ("cta", "free", "gated"):
            treatment_name = f"{model}_{treatment}"
            if treatment_name in correctness:
                comparisons[f"{treatment_name}_minus_{generic}"] = cluster_bootstrap(
                    correctness[generic], correctness[treatment_name], clusters
                )
        cta_name = f"{model}_cta"
        if cta_name in correctness:
            for typed in ("free", "gated"):
                typed_name = f"{model}_{typed}"
                if typed_name in correctness:
                    comparisons[f"{cta_name}_minus_{typed_name}"] = cluster_bootstrap(
                        correctness[typed_name], correctness[cta_name], clusters
                    )

    report = {
        "protocol_status": "post_human_exploratory_ood",
        "frozen_task_count": len(expected),
        "determinate_human_rewrite_majorities": len(majorities),
        "majority_gold_rewrite_items": len(majority_gold),
        "unanimous_gold_rewrite_items": len(unanimous_gold),
        "runs": runs,
        "comparisons": comparisons,
    }
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# Independent Human-Rewrite Model Results",
        "",
        "This is the frozen post-human exploratory OOD evaluation. API errors and missing rows",
        "count as failures; the analyzer rejects incomplete or duplicate 50-task inventories.",
        "",
        "| Run | Gold | Human majority | Human actionable | Majority-gold | Unanimous-gold | Actionable core | Reject policy |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in runs.items():
        lines.append(
            f"| {name} | {row['gold']['correct']}/{row['gold']['n']} "
            f"({row['gold']['accuracy']:.1%}) | {row['human_majority']['correct']}/"
            f"{row['human_majority']['n']} ({row['human_majority']['accuracy']:.1%}) | "
            f"{row['human_majority_actionable']['accuracy']:.1%} | "
            f"{row['majority_gold_subset']['accuracy']:.1%} | "
            f"{row['unanimous_gold_subset']['accuracy']:.1%} | "
            f"{row['actionable_core']['accuracy']:.1%} | "
            f"{row['author_specified_reject_policy']['accuracy']:.1%} |"
        )
    lines.extend(["", "## Gold slices", ""])
    for name, row in runs.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps({"slices": row["slices"], "errors": row["errors"], "statuses": row["statuses"], "api_retries": row["api_retries"]}, indent=2))
        lines.extend(["```", ""])
    lines.extend(["## Paired cluster comparisons", "", "```json", json.dumps(comparisons, indent=2), "```", ""])
    Path(args.markdown_output).write_text("\n".join(lines))


if __name__ == "__main__":
    main()
