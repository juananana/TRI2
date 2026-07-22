from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from .tasks import selected_id


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def load_tasks(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def spec_from_task(task: dict) -> dict:
    return {
        "criterion": next(
            key for key in task["initial_state"][0].keys()
            if key != "id" and key not in {"service", "topic", "attachment", "name", "status", "rack", "destination", "metric", "ward", "owner"}
        ),
        "direction": infer_direction(task),
    }


def infer_direction(task: dict) -> str:
    selector = task["selector"].lower()
    if "highest" in selector or "largest" in selector or "most delayed" in selector:
        return "highest"
    if "front" in selector:
        return "front"
    return "true"


def predict(task: dict, representation: str) -> str:
    spec = spec_from_task(task)
    pre = task["pre_refresh_target"]
    post = selected_id(task["refreshed_state"], spec)
    present = task["bound_entity_present_after_refresh"]
    binding = task["binding"]

    if representation == "raw_goal_latest_state":
        return post
    if representation == "selector_memory":
        return post
    if representation == "binding_time_only":
        return post if binding == "dynamic" else "UNKNOWN"
    if representation == "entity_only":
        return pre
    if representation == "time_entity":
        return pre if binding == "anchored" else post
    if representation == "full_ledger":
        if binding == "anchored" and not present:
            return "INVALID_BOUND_ENTITY"
        return pre if binding == "anchored" else post
    raise ValueError(representation)


def summarize(rows: list[dict]) -> dict:
    reps = [
        "raw_goal_latest_state",
        "selector_memory",
        "binding_time_only",
        "entity_only",
        "time_entity",
        "full_ledger",
    ]
    groups = defaultdict(lambda: {"n": 0, "correct": 0})
    for task in rows:
        if task["update"] not in {"flip", "removed", "stable"}:
            continue
        for rep in reps:
            key = (rep, task["binding"], task["update"])
            groups[key]["n"] += 1
            groups[key]["correct"] += int(predict(task, rep) == task["correct_target"])
    return {
        "rows": [
            {
                "representation": rep,
                "binding": binding,
                "update": update,
                "n": stats["n"],
                "accuracy": stats["correct"] / stats["n"] if stats["n"] else None,
            }
            for (rep, binding, update), stats in sorted(groups.items())
        ]
    }


def markdown(report: dict) -> str:
    lines = [
        "| Representation | Binding | Update | n | Accuracy |",
        "|---|---|---|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['representation']} | {row['binding']} | {row['update']} | "
            f"{row['n']} | {100 * row['accuracy']:.1f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(DATA / "temporal_referent.jsonl"))
    ap.add_argument("--output", default=str(REPORTS / "field_ablation.json"))
    args = ap.parse_args()
    report = summarize(load_tasks(Path(args.input)))
    out = Path(args.output)
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()

