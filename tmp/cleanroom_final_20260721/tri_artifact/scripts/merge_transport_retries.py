from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def failed(row: dict[str, Any]) -> bool:
    return row.get("status") != "ok" or bool(row.get("result", {}).get("errors"))


def merge(base: list[dict[str, Any]], retries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    retry_by_id = {row["task"]["id"]: row for row in retries}
    expected = {row["task"]["id"] for row in base if failed(row)}
    if set(retry_by_id) != expected:
        raise ValueError("Retry task IDs must exactly equal base transport failures")
    if any(failed(row) for row in retries):
        raise ValueError("A transport retry still failed")
    output: list[dict[str, Any]] = []
    for row in base:
        task_id = row["task"]["id"]
        if task_id not in retry_by_id:
            output.append(row)
            continue
        replacement = dict(retry_by_id[task_id])
        replacement["transport_recovery"] = {
            "original_status": row.get("status"),
            "original_errors": row.get("result", {}).get("errors", []),
            "original_api_request_attempts": row.get("api_request_attempts", 0),
            "policy": "single serial retry of automatically selected transport failures",
        }
        output.append(replacement)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--retry", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = merge(load(Path(args.base)), load(Path(args.retry)))
    with Path(args.output).open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{args.output}: {len(rows)} rows")


if __name__ == "__main__":
    main()
