from __future__ import annotations

import argparse
import json
from pathlib import Path

from .v2_tasks import task_rows


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(DATA / "temporal_referent_v2_api_scalar.jsonl"))
    args = ap.parse_args()
    rows = [
        row for row in task_rows()
        if row["task_type"] == "scalar" and row["binding"] in {"anchored", "dynamic"}
    ]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} scalar API-compatible v2 tasks to {out}")


if __name__ == "__main__":
    main()
