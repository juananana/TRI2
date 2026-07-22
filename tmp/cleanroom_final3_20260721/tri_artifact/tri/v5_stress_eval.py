from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ANCHOR_EXPLICIT = (
    "Choose {selector} from the current {app} as the {action} target. Refresh the data. "
    "Separately note the current {selector} as a monitoring reference, without replacing the "
    "action target. Count the records, refresh once more, then {action} the action target chosen "
    "before either refresh. If it is no longer actionable, stop."
)
ANCHOR_IMPLICIT = (
    "Settle on {selector} in the current {app}. Refresh and check which {entity} now fits that "
    "description for the status log. Count the records, refresh again, and {action} the one you "
    "settled on at the start if it can still receive that action; otherwise stop."
)
DYNAMIC_EXPLICIT = (
    "Refresh the {app} and note the current {selector} for monitoring only. Count the records and "
    "refresh again. Do not choose the {action} target until this second refresh; then select "
    "{selector} from the final state and {action} it."
)
DYNAMIC_IMPLICIT = (
    "Reload the {app}; inspect {selector} for the status log. Count the records and reload once "
    "more. Based only on the final view, work out {selector} and {action} it."
)


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def stress_rows(source: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, original in enumerate(source):
        row = deepcopy(original)
        anchored = row["binding"] == "anchored"
        implicit = row["style"].startswith("implicit")
        if anchored:
            template = ANCHOR_IMPLICIT if implicit else ANCHOR_EXPLICIT
            intermediate = deepcopy(row["refreshed_state"])
        else:
            template = DYNAMIC_IMPLICIT if implicit else DYNAMIC_EXPLICIT
            intermediate = deepcopy(row["initial_state"])
        row.update({
            "id": row["id"].replace("tri-v3-language", "tri-v5-stress"),
            "candidate": "tri-v5-stress",
            "instruction": template.format(**row),
            "intermediate_state": intermediate,
            "final_state": deepcopy(row["refreshed_state"]),
            "trajectory_shape": "query-refresh-monitor-count-refresh-mutate",
            "distractor_referent": "intermediate selector winner used only for monitoring",
            "source_task_id": original["id"],
            "stress_index": index,
        })
        rows.append(row)
    if len(rows) != 40:
        raise ValueError(f"Expected 40 SQLite source tasks, found {len(rows)}")
    return rows


def write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def smoke_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    anchored = [row for row in rows if row["binding"] == "anchored"]
    dynamic = [row for row in rows if row["binding"] == "dynamic"]
    anchored_updates = ["flip", "remove", "invalidate", "name_collision"]
    dynamic_updates = ["stable", "flip", "remove", "invalidate"]
    return [next(row for row in anchored if row["update"] == update) for update in anchored_updates] + [
        next(row for row in dynamic if row["update"] == update) for update in dynamic_updates
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="data/temporal_referent_v3_sqlite_trajectory.jsonl")
    parser.add_argument("--output", default="data/temporal_referent_v5_multirefresh_sqlite.jsonl")
    parser.add_argument("--smoke-output", default="data/temporal_referent_v5_multirefresh_sqlite_smoke.jsonl")
    args = parser.parse_args()
    rows = stress_rows(load(Path(args.source)))
    write(Path(args.output), rows)
    write(Path(args.smoke_output), smoke_rows(rows))
    print(args.output)
    print(args.smoke_output)


if __name__ == "__main__":
    main()
