from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def failed_task_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {
        row["task"]["id"]
        for row in rows
        if row.get("status") != "ok" or bool(row.get("result", {}).get("errors"))
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    ids = failed_task_ids(load(Path(args.run)))
    tasks = [row for row in load(Path(args.data)) if row["id"] in ids]
    if len(tasks) != len(ids):
        raise ValueError("Not every failed task ID was found in the source data")
    with Path(args.output).open("w", encoding="utf-8") as handle:
        for task in tasks:
            handle.write(json.dumps(task, ensure_ascii=False) + "\n")
    print(f"{args.output}: {len(tasks)} transport-failure tasks")


if __name__ == "__main__":
    main()
