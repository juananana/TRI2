#!/usr/bin/env python3
import json
from pathlib import Path

from tri.binding_drift_tri_adapter import file_sha256, freeze_smoke


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "temporal_referent_v7_core_replication.jsonl"
OUTPUT = ROOT / "data" / "binding_drift_tri_symmetric_smoke_v1.jsonl"


def main() -> None:
    rows = freeze_smoke(SOURCE)
    OUTPUT.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(f"{OUTPUT} n={len(rows)} sha256={file_sha256(OUTPUT)}")


if __name__ == "__main__":
    main()
