from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from .reference_lifecycle import INVALID
from .run_models import is_success, target_satisfies_schema
from .v2_model_report import is_api_failure
from .v3_sqlite_replay import SQLiteWriteEnvironment


def derive_language(row: dict[str, Any]) -> dict[str, Any]:
    derived = copy.deepcopy(row)
    result = derived.get("result", {})
    result["mode"] = "generic_validity_gated_ledger_then_act"
    if not is_api_failure(row):
        target = result.get("predicted_target")
        if target != INVALID and not target_satisfies_schema(target, row["task"]):
            target = INVALID
            result["predicted_target"] = target
        result["target_schema_valid"] = target_satisfies_schema(target, row["task"])
        result["success"] = is_success(target, row["task"])
    result["derived_from_same_actor_output"] = True
    return derived


def derive_sqlite(row: dict[str, Any]) -> dict[str, Any]:
    derived = copy.deepcopy(row)
    result = derived.get("result", {})
    result["mode"] = "sqlite_generic_validity_gated"
    if is_api_failure(row):
        result["derived_from_same_actor_output"] = True
        return derived

    task = row["task"]
    target = result.get("predicted_target")
    if target != INVALID and not target_satisfies_schema(target, task):
        target = INVALID

    env = SQLiteWriteEnvironment(task)
    try:
        env.query()
        env.refresh()
        action = env.act(target)
        acted_ids = env.acted_ids()
        gold = task["correct_target"]
        result.update({
            "predicted_target": target,
            "success": target == gold,
            "final_state_success": (
                (gold == INVALID and not acted_ids)
                or (gold != INVALID and acted_ids == [gold])
            ),
            "action_status": action["status"],
            "acted_ids": acted_ids,
            "collateral_modifications": len(
                [target_id for target_id in acted_ids if target_id != gold]
            ),
            "tool_trace": env.trace,
            "derived_from_same_actor_output": True,
        })
    finally:
        env.close()
    return derived


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sqlite", action="store_true")
    args = parser.parse_args()

    transform = derive_sqlite if args.sqlite else derive_language
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with input_path.open(encoding="utf-8") as source, output_path.open("w", encoding="utf-8") as sink:
        for line in source:
            if line.strip():
                sink.write(json.dumps(transform(json.loads(line)), ensure_ascii=False) + "\n")
    print(output_path)


if __name__ == "__main__":
    main()
