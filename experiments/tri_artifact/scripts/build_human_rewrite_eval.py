from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", required=True)
    parser.add_argument("--rewrites", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    sources = {}
    with Path(args.sources).open(encoding="utf-8") as handle:
        for line in handle:
            task = json.loads(line)
            sources[task["id"]] = task
    with Path(args.rewrites).open(encoding="utf-8-sig", newline="") as handle:
        rewrite_rows = list(csv.DictReader(handle))
    rewrites = {row["source_task_id"]: row["rewrite_instruction"].strip() for row in rewrite_rows}

    if set(sources) != set(rewrites):
        raise ValueError(
            f"Source/rewrite mismatch: missing={sorted(set(sources) - set(rewrites))}, "
            f"extra={sorted(set(rewrites) - set(sources))}"
        )
    if any(not value for value in rewrites.values()):
        raise ValueError("Every selected source must have a non-empty human rewrite")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for task_id in sorted(sources):
            task = dict(sources[task_id])
            task["source_instruction"] = task["instruction"]
            task["instruction"] = rewrites[task_id]
            task["text_variant"] = "independent_human_rewrite"
            handle.write(json.dumps(task, ensure_ascii=False) + "\n")

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(json.dumps({"tasks": len(sources), "output": str(output), "sha256": digest}, indent=2))


if __name__ == "__main__":
    main()
