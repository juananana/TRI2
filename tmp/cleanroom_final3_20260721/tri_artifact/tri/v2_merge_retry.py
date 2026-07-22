from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .v2_model_report import is_api_failure


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def task_id(row: dict[str, Any]) -> str | None:
    return row.get("task", {}).get("id")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--retry", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--replace-with-api-failures", action="store_true")
    args = ap.parse_args()

    base_path = Path(args.base)
    base_rows = load_jsonl(base_path)
    retry_by_id: dict[str, tuple[Path, dict[str, Any]]] = {}
    for retry_name in args.retry:
        retry_path = Path(retry_name)
        for row in load_jsonl(retry_path):
            row_id = task_id(row)
            if not row_id:
                continue
            if args.replace_with_api_failures or not is_api_failure(row):
                retry_by_id[row_id] = (retry_path, row)

    merged: list[dict[str, Any]] = []
    replaced = 0
    remaining_api_failures = 0
    for row in base_rows:
        row_id = task_id(row)
        replacement = retry_by_id.get(row_id or "")
        if row_id and is_api_failure(row) and replacement:
            retry_path, retry_row = replacement
            retry_row = dict(retry_row)
            retry_row["retry_provenance"] = {
                "base_file": str(base_path),
                "retry_file": str(retry_path),
                "replaced_api_failure": True,
            }
            merged.append(retry_row)
            replaced += 1
        else:
            merged.append(row)
            remaining_api_failures += int(is_api_failure(row))

    write_jsonl(Path(args.output), merged)
    print(json.dumps({
        "base": args.base,
        "retry": args.retry,
        "output": args.output,
        "n_base": len(base_rows),
        "n_replaced": replaced,
        "remaining_api_failures": remaining_api_failures,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
