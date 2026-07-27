from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from tri.independent_language_holdout import (
    build_assignments,
    build_scenario_pairs,
    writer_combined_wjx,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "temporal_referent_v7_core_replication.jsonl"
OUTPUT = ROOT / "human_studies" / "independent_language_holdout_12w_prototype"
WRITERS = tuple(f"W{index}" for index in range(1, 13))


def main() -> None:
    pairs = build_scenario_pairs(SOURCE)
    pair_map = {row["pair_id"]: row for row in pairs}
    assignments = build_assignments(pairs, WRITERS)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / "writer_allocation.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(assignments[0]))
        writer.writeheader()
        writer.writerows(assignments)
    form = writer_combined_wjx(
        "W1",
        assignments,
        pair_map,
        page_size=10,
        title_suffix="12人版两页预览",
    )
    form_path = OUTPUT / "writer_W1_two_page_prototype_wjx.txt"
    form_path.write_text(form, encoding="utf-8")
    counts = Counter(row["writer_id"] for row in assignments)
    manifest = {
        "status": "prototype; do not collect before user approval",
        "writers": len(WRITERS),
        "instructions": len(assignments),
        "items_per_writer": dict(sorted(counts.items())),
        "prototype_writer": "W1",
        "prototype_pages": 2,
    }
    (OUTPUT / "prototype_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
