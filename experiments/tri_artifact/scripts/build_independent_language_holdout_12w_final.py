from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from tri.independent_language_holdout import (
    build_assignments,
    build_scenario_pairs,
    sha256_path,
    writer_combined_wjx,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "temporal_referent_v7_core_replication.jsonl"
OUTPUT = ROOT / "human_studies" / "independent_language_holdout_12w_final"
WRITERS = tuple(f"W{index}" for index in range(1, 13))


def main() -> None:
    pairs = build_scenario_pairs(SOURCE)
    pair_map = {row["pair_id"]: row for row in pairs}
    assignments = build_assignments(pairs, WRITERS)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    allocation_path = OUTPUT / "writer_allocation.csv"
    with allocation_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(assignments[0]))
        writer.writeheader()
        writer.writerows(assignments)

    form_paths = []
    for writer_id in WRITERS:
        form = writer_combined_wjx(
            writer_id,
            assignments,
            pair_map,
            page_size=10,
            title_suffix="12人版最终",
        )
        form_path = OUTPUT / f"writer_{writer_id}_two_page_final_wjx.txt"
        form_path.write_text(form, encoding="utf-8")
        form_paths.append(form_path)

    counts = Counter(row["writer_id"] for row in assignments)
    manifest = {
        "status": "post-primary human collection packet; uncollected",
        "writers": len(WRITERS),
        "instructions": len(assignments),
        "items_per_writer": dict(sorted(counts.items())),
        "pages_per_writer": 2,
        "allocation_sha256": sha256_path(allocation_path),
        "forms": {
            path.name: sha256_path(path)
            for path in form_paths
        },
    }
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
