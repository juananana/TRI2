from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


def replay_lifecycle_gate(row: dict[str, Any]) -> dict[str, Any]:
    if row["controller"] != "matched_lifecycle":
        raise ValueError("gate replay requires a matched_lifecycle row")
    output = copy.deepcopy(row)
    output["controller"] = "matched_lifecycle_gate_replay"
    output["source_controller"] = row["controller"]
    output["source_success"] = row["success"]
    state = row.get("compiled_state")
    gate_applied = bool(
        state
        and state.get("reference_mode") == "preserve"
        and row.get("order_success")
        and not row.get("errors")
    )
    output["gate_applied"] = gate_applied
    if not gate_applied:
        return output

    bound_id = state.get("bound_target_id")
    present_ids = {item["reminder_id"] for item in row["post_sync_snapshot"]}
    actionable = bound_id in present_ids and not (
        row["transition"] == "invalidate" and bound_id == "REM-A"
    )
    writes = [bound_id] if actionable and bound_id else []
    expected = row["expected_target_id"]
    wrong_writes = [target for target in writes if target != expected]
    output.update(
        {
            "attempted_target_ids": writes,
            "written_target_ids": writes,
            "wrong_write_ids": wrong_writes,
            "wrong_entity_write": bool(wrong_writes),
            "invalid_attempts": 0,
            "unnecessary_rejection": expected is not None and not writes,
            "final_state_success": writes == ([] if expected is None else [expected]),
            "finished": True,
        }
    )
    output["success"] = bool(
        output["final_state_success"]
        and output["order_success"]
        and not output["unnecessary_rejection"]
        and not output["errors"]
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8") as handle:
        source = [json.loads(line) for line in handle if line.strip()]
    rows = [replay_lifecycle_gate(row) for row in source if row["controller"] == "matched_lifecycle"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{sum(row['success'] for row in rows)}/{len(rows)} successful")
    print(args.output)


if __name__ == "__main__":
    main()
