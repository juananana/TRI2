from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


REPRESENTATIONS = [
    "latest_state_selector",
    "bound_name_only",
    "bound_id_only",
    "binding_time_only",
    "time_plus_id",
    "full_lifecycle_ledger",
]


def load_tasks(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _name_fields(item: dict) -> list[str]:
    return [
        str(item[k])
        for k in ("name", "display", "attachment", "service")
        if k in item
    ]


def _pre_entity(task: dict) -> dict:
    return next(x for x in task["initial_state"] if x["id"] == task["pre_refresh_target"])


def _after_entity(task: dict, target_id: str) -> dict | None:
    return next((x for x in task["refreshed_state"] if x["id"] == target_id), None)


def resolve_bound_name_only(task: dict) -> str:
    names = set(_name_fields(_pre_entity(task)))
    if not names:
        return task["post_refresh_target"]
    matches = [
        x["id"]
        for x in task["refreshed_state"]
        if names.intersection(_name_fields(x))
    ]
    if len(matches) == 1:
        return matches[0]
    return task["post_refresh_target"]


def predict(task: dict, representation: str) -> str:
    binding = task["binding"]
    pre = task["pre_refresh_target"]
    post = task["post_refresh_target"]

    if representation == "latest_state_selector":
        return post
    if representation == "bound_name_only":
        return resolve_bound_name_only(task)
    if representation == "bound_id_only":
        return pre
    if representation == "binding_time_only":
        return post if binding == "dynamic" else "UNKNOWN"
    if representation == "time_plus_id":
        return pre if binding == "anchored" else post
    if representation == "full_lifecycle_ledger":
        if binding == "dynamic":
            return post
        if _after_entity(task, pre) is None:
            return "INVALID_BOUND_ENTITY"
        if not task.get("bound_entity_actionable_after_refresh", True):
            return "INVALID_BOUND_ENTITY"
        return pre
    raise ValueError(representation)


def summarize(rows: list[dict]) -> dict:
    groups = defaultdict(lambda: {"n": 0, "correct": 0})
    scenario_groups = defaultdict(lambda: {"n": 0, "correct": 0})
    errors = []
    for task in rows:
        for rep in REPRESENTATIONS:
            pred = predict(task, rep)
            ok = pred == task["correct_target"]
            key = (rep, task["binding"])
            groups[key]["n"] += 1
            groups[key]["correct"] += int(ok)
            skey = (rep, task["lifecycle_scenario"], task["binding"])
            scenario_groups[skey]["n"] += 1
            scenario_groups[skey]["correct"] += int(ok)
            if not ok:
                errors.append({
                    "representation": rep,
                    "task_id": task["id"],
                    "scenario": task["lifecycle_scenario"],
                    "binding": task["binding"],
                    "prediction": pred,
                    "correct": task["correct_target"],
                })
    return {
        "representations": REPRESENTATIONS,
        "overall": [
            {
                "representation": rep,
                "binding": binding,
                **stats,
                "accuracy": stats["correct"] / stats["n"] if stats["n"] else None,
            }
            for (rep, binding), stats in sorted(groups.items())
        ],
        "by_scenario": [
            {
                "representation": rep,
                "scenario": scenario,
                "binding": binding,
                **stats,
                "accuracy": stats["correct"] / stats["n"] if stats["n"] else None,
            }
            for (rep, scenario, binding), stats in sorted(scenario_groups.items())
        ],
        "errors": errors,
    }


def pct(correct: int, total: int) -> str:
    return "NA" if total == 0 else f"{100 * correct / total:.1f}"


def markdown(report: dict) -> str:
    lines = [
        "# Lifecycle Representation Ablation",
        "",
        "## Overall",
        "",
        "| Representation | Binding | n | Accuracy |",
        "|---|---|---:|---:|",
    ]
    for row in report["overall"]:
        lines.append(
            f"| {row['representation']} | {row['binding']} | "
            f"{row['n']} | {pct(row['correct'], row['n'])} |"
        )
    lines.extend([
        "",
        "## By Scenario",
        "",
        "| Representation | Scenario | Binding | n | Accuracy |",
        "|---|---|---|---:|---:|",
    ])
    for row in report["by_scenario"]:
        lines.append(
            f"| {row['representation']} | {row['scenario']} | {row['binding']} | "
            f"{row['n']} | {pct(row['correct'], row['n'])} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(DATA / "lifecycle_referent.jsonl"))
    ap.add_argument("--output", default=str(REPORTS / "lifecycle_ablation.json"))
    args = ap.parse_args()

    report = summarize(load_tasks(Path(args.input)))
    out = Path(args.output)
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
