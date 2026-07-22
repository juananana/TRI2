from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


CORE_UPDATES = {"flip", "name_collision"}
POLICY_UPDATES = {"invalidate", "remove"}


def load_rows(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def initial_binding_id(row: dict[str, Any]) -> str | None:
    result = row.get("result", {})
    ledger = result.get("compiled_ledger") or {}
    if "generic" in str(result.get("mode", "")):
        return ledger.get("selected_entity_id")
    return ledger.get("bound_target_id")


def initial_binding_correct(row: dict[str, Any]) -> bool:
    return initial_binding_id(row) == row["task"].get("pre_refresh_target")


def core_opportunity(row: dict[str, Any]) -> bool:
    task = row["task"]
    return bool(
        task.get("binding") == "anchored"
        and task.get("update") in CORE_UPDATES
        and task.get("bound_entity_present_after_refresh")
        and task.get("bound_entity_actionable_after_refresh")
        and initial_binding_correct(row)
    )


def policy_opportunity(row: dict[str, Any]) -> bool:
    task = row["task"]
    return bool(
        task.get("binding") == "anchored"
        and task.get("update") in POLICY_UPDATES
        and initial_binding_correct(row)
    )


def wrong_write(row: dict[str, Any]) -> bool:
    return row.get("result", {}).get("action_status") == "wrong_entity_write"


def drifted_to_refreshed_winner(row: dict[str, Any]) -> bool:
    task = row["task"]
    result = row.get("result", {})
    post = task.get("post_refresh_target")
    return bool(
        core_opportunity(row)
        and wrong_write(row)
        and result.get("predicted_target") == post
        and result.get("acted_ids") == [post]
    )


def stable_control(row: dict[str, Any]) -> bool:
    task = row["task"]
    return bool(
        task.get("binding") == "anchored"
        and task.get("update") == "stable"
        and initial_binding_correct(row)
    )


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    core = [row for row in rows if core_opportunity(row)]
    policy = [row for row in rows if policy_opportunity(row)]
    stable = [row for row in rows if stable_control(row)]
    wrong = [row for row in rows if wrong_write(row)]
    classified = [row for row in wrong if drifted_to_refreshed_winner(row)]
    policy_wrong = [row for row in policy if wrong_write(row)]
    return {
        "n": len(rows),
        "anchored_initial_binding_correct": sum(
            row["task"].get("binding") == "anchored" and initial_binding_correct(row)
            for row in rows
        ),
        "anchored_n": sum(row["task"].get("binding") == "anchored" for row in rows),
        "all_wrong_writes": len(wrong),
        "core_opportunities": len(core),
        "core_tri_writes": len(classified),
        "policy_opportunities": len(policy),
        "policy_wrong_writes": len(policy_wrong),
        "stable_controls": len(stable),
        "stable_wrong_writes": sum(wrong_write(row) for row in stable),
        "unclassified_wrong_writes": len(wrong) - len(classified) - len(policy_wrong),
    }


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row.get("model", "")), str(row.get("result", {}).get("mode", "")))].append(row)
    return {
        "definition": {
            "core_tri_write": (
                "anchored instruction; flip or name-collision update; correct pre-refresh binding; "
                "bound entity remains present and actionable; final mutation writes the refreshed "
                "selector winner instead"
            ),
            "policy_wrong_write": (
                "correct pre-refresh anchored binding followed by remove or invalidate; a replacement "
                "is written despite the benchmark's reject policy"
            ),
        },
        "inventory": {"rows": len(rows)},
        "summary": [
            {"model": model, "controller": controller, **summarize_group(group)}
            for (model, controller), group in sorted(groups.items())
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Conditional Audit of SQLite Wrong-Entity Writes",
        "",
        "A core TRI write is counted only when the pre-refresh binding is correct, the instruction",
        "preserves that identity, the old entity remains present and action-valid, and the final",
        "mutation instead writes the refreshed selector winner. Remove/invalidate cases are reported",
        "separately as invalidity-policy errors.",
        "",
        "| Model | Controller | n | Correct anchored binding | All wrong writes | Core opportunities | Core TRI writes | Policy opportunities | Policy wrong writes | Stable wrong writes | Unclassified |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['model']} | {row['controller']} | {row['n']} | "
            f"{row['anchored_initial_binding_correct']}/{row['anchored_n']} | "
            f"{row['all_wrong_writes']} | {row['core_opportunities']} | "
            f"{row['core_tri_writes']} | {row['policy_opportunities']} | "
            f"{row['policy_wrong_writes']} | {row['stable_wrong_writes']}/"
            f"{row['stable_controls']} | {row['unclassified_wrong_writes']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    report = build_report(load_rows(args.inputs))
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown(report), encoding="utf-8")
    print(args.json)
    print(args.markdown)


if __name__ == "__main__":
    main()
