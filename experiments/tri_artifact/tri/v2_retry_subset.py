from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .v2_model_report import is_api_failure


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def failed_ids(rows: list[dict[str, Any]], failure: str) -> set[str]:
    out: set[str] = set()
    for row in rows:
        task = row.get("task", {})
        task_id = task.get("id")
        if not task_id:
            continue
        if failure == "api" and is_api_failure(row):
            out.add(task_id)
        elif failure == "incorrect" and not is_api_failure(row) and not row.get("result", {}).get("success"):
            out.add(task_id)
        elif failure == "all" and (is_api_failure(row) or not row.get("result", {}).get("success")):
            out.add(task_id)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(DATA / "temporal_referent_v2_api_scalar.jsonl"))
    ap.add_argument("--run", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--failure", choices=["api", "incorrect", "all"], default="api")
    args = ap.parse_args()

    data_rows = load_jsonl(Path(args.data))
    id_to_task = {row["id"]: row for row in data_rows}
    retry_ids = failed_ids(load_jsonl(Path(args.run)), args.failure)
    missing = sorted(retry_ids - set(id_to_task))
    retry_rows = [id_to_task[task_id] for task_id in sorted(retry_ids) if task_id in id_to_task]
    write_jsonl(Path(args.output), retry_rows)
    print(json.dumps({
        "run": args.run,
        "failure": args.failure,
        "n_retry": len(retry_rows),
        "output": args.output,
        "missing_ids": missing[:10],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
