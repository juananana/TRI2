from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from tri.independent_language_holdout import (
    MODEL_PRELABELERS,
    build_blind_prelabel_tasks,
    jsonl_bytes,
    load_assignments,
    load_jsonl,
    sha256_path,
    validate_pairs,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build blinded model-assisted prelabel packets for later human review."
    )
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--private-scenario-key", type=Path, required=True)
    parser.add_argument("--authored", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    assignments = load_assignments(args.packet / "writer_allocation.csv")
    pairs = load_jsonl(args.private_scenario_key)
    validate_pairs(pairs)
    authored = load_jsonl(args.authored)
    args.output.mkdir(parents=True, exist_ok=False)

    packet_hashes = {}
    review_rows = []
    for prelabeler in MODEL_PRELABELERS:
        tasks = build_blind_prelabel_tasks(authored, pairs, assignments, prelabeler)
        path = args.output / f"model_prelabel_{prelabeler}.jsonl"
        path.write_bytes(jsonl_bytes(tasks))
        packet_hashes[path.name] = sha256_path(path)
        review_rows.extend(
            {
                "model_prelabeler_id": prelabeler,
                "blind_item_id": row["blind_item_id"],
            }
            for row in tasks
        )

    review_path = args.output / "human_review_template.csv"
    with review_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "model_prelabeler_id",
            "blind_item_id",
            "model_target",
            "model_confidence",
            "human_target",
            "human_confidence",
            "human_accepts_model_consensus",
            "human_notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(review_rows)

    manifest = {
        "status": "inputs only; no model labels collected",
        "evidence_allowed": False,
        "human_substitution_forbidden": True,
        "model_prelabelers": list(MODEL_PRELABELERS),
        "rows_per_packet": 120,
        "review_rows": 360,
        "packet_sha256": packet_hashes,
        "review_template_sha256": sha256_path(review_path),
        "authored_sha256": sha256_path(args.authored),
        "hidden_fields": [
            "item_id",
            "writer_id",
            "writer_intent",
            "writer_confidence",
            "mode",
            "pair_id",
            "design_target",
            "gold",
        ],
        "use_boundary": (
            "Outputs may prioritize human review but never count as independent annotators, "
            "agreement, or clarity-gate evidence."
        ),
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
