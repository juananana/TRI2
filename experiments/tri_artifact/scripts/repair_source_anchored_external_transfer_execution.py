#!/usr/bin/env python3
"""Replay source writes for rows affected by the missing-checkout smoke failure.

This script makes no model or network request. It preserves every model-facing
field and recomputes only source execution and derived scoring fields.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from scripts.run_source_anchored_external_transfer import _execute_source_write, load_jsonl


REPAIR_VERSION = "TRI-source-execution-path-repair-v1"


def canonical_sha256(row: dict[str, Any]) -> str:
    payload = json.dumps(row, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def repair_row(
    row: dict[str, Any],
    task: dict[str, Any],
    state_root: Path,
    agentdojo_root: Path,
) -> dict[str, Any]:
    repaired = dict(row)
    predicted = row.get("predicted_target_id")
    eligible_for_execution = (
        predicted is not None
        and row.get("first_transport_error") is None
        and row.get("second_transport_error") is None
        and row.get("first_parse_error") is None
        and row.get("second_parse_error") is None
    )
    if eligible_for_execution:
        write_executed, execution_error = _execute_source_write(
            task, str(predicted), state_root, agentdojo_root
        )
    else:
        write_executed = False
        execution_error = None
    valid = eligible_for_execution and write_executed
    repaired.update(
        {
            "repair_version": REPAIR_VERSION,
            "repair_reason": "source checkouts and temporary dependencies were absent after model return",
            "parent_raw_row_sha256": canonical_sha256(row),
            "model_requests_added_by_repair": 0,
            "write_executed": write_executed,
            "source_execution_error": execution_error,
            "initial_winner_id": task["initial_winner_id"],
            "refreshed_winner_id": task["refreshed_winner_id"],
            "old_target_present_after_refresh": task["old_target_present_after_refresh"],
            "old_target_action_valid_after_refresh": task["old_target_action_valid_after_refresh"],
            "exact_target_success": valid and str(predicted) == task["expected_target_id"],
            "wrong_entity_write": write_executed and str(predicted) != task["expected_target_id"],
            "status": "ok" if valid else "failed",
        }
    )
    return repaired


def parse_args() -> argparse.Namespace:
    artifact = Path(__file__).resolve().parents[1]
    project = artifact.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=artifact / "runs/source_anchored_external_transfer_siliconflow_v1.jsonl",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=artifact / "data/source_anchored_external_transfer_tasks_v1.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=artifact
        / "runs/source_anchored_external_transfer_smoke_infrastructure_repair_v1.jsonl",
    )
    parser.add_argument(
        "--state-bench-root", type=Path, default=project / "external_sources/state-bench"
    )
    parser.add_argument(
        "--agentdojo-root", type=Path, default=project / "external_sources/agentdojo"
    )
    parser.add_argument(
        "--agentdojo-deps-root", type=Path, default=project / "external_sources/agentdojo-deps"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for path in (args.agentdojo_deps_root, args.agentdojo_root / "src", args.state_bench_root):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    tasks = {task["task_id"]: task for task in load_jsonl(args.inventory)}
    rows = load_jsonl(args.input)
    repaired = [
        repair_row(row, tasks[row["task_id"]], args.state_bench_root, args.agentdojo_root)
        for row in rows
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in repaired),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "repair_version": REPAIR_VERSION,
                "input_rows": len(rows),
                "output_rows": len(repaired),
                "model_requests_added": 0,
                "source_execution_failures": sum(
                    bool(row["source_execution_error"]) for row in repaired
                ),
                "valid_rows": sum(row["status"] == "ok" for row in repaired),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
