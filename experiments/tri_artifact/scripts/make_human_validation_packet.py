from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


SEED = 20260717


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def select_sources(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["style"], row["update"])].append(row)
    rng = random.Random(SEED)
    selected: list[dict[str, Any]] = []
    for index, key in enumerate(sorted(groups)):
        group = sorted(groups[key], key=lambda row: row["id"])
        rng.shuffle(group)
        selected.extend(group[: 3 if index < 10 else 2])
    if len(selected) != 50:
        raise ValueError(f"Expected 50 sources, found {len(selected)}")
    return sorted(selected, key=lambda row: row["id"])


def write_authoring(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "source_task_id", "style", "update", "domain", "original_instruction",
        "rewrite_instruction", "author_notes",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "source_task_id": row["id"],
                "style": row["style"],
                "update": row["update"],
                "domain": row["domain"],
                "original_instruction": row["instruction"],
                "rewrite_instruction": "",
                "author_notes": "",
            })


def load_rewrites(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rewrites = {
        row["source_task_id"]: row["rewrite_instruction"].strip()
        for row in rows if row.get("rewrite_instruction", "").strip()
    }
    if len(rewrites) != 50:
        raise ValueError(
            f"Need 50 completed independent rewrites; found {len(rewrites)} in {path}"
        )
    return rewrites


def item(item_id: str, row: dict[str, Any], instruction: str) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "instruction": instruction,
        "initial_state_json": json.dumps(row["initial_state"], ensure_ascii=False),
        "refreshed_state_json": json.dumps(row["refreshed_state"], ensure_ascii=False),
        "action_schema_json": json.dumps(row.get("action_schema", {}), ensure_ascii=False),
        "candidate_ids": " | ".join(entity["id"] for entity in row["refreshed_state"]),
        "response": "",
        "confidence_1_to_5": "",
        "comment": "",
    }


def write_packets(output_dir: Path, sources: list[dict[str, Any]], rewrites: dict[str, str]) -> None:
    source_variants: list[tuple[dict[str, Any], str, str]] = []
    for row in sources:
        source_variants.extend([
            (row, "original", row["instruction"]),
            (row, "human_rewrite", rewrites[row["id"]]),
        ])
    random.Random(SEED + 100).shuffle(source_variants)

    items: list[dict[str, Any]] = []
    key_rows: list[dict[str, Any]] = []
    for index, (row, variant, instruction) in enumerate(source_variants, 1):
        item_id = f"HV-{index:04d}"
        items.append(item(item_id, row, instruction))
        key_rows.append({
            "item_id": item_id,
            "source_task_id": row["id"],
            "pre_refresh_target": row["pre_refresh_target"],
            "post_refresh_target": row["post_refresh_target"],
            "gold_target": row["correct_target"],
            "binding": row["binding"],
            "update": row["update"],
            "style": row["style"],
            "explicitness": "explicit" if row["style"].startswith("explicit") else "implicit",
            "variant": variant,
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(items[0])
    for annotator in range(1, 4):
        shuffled = list(items)
        random.Random(SEED + annotator).shuffle(shuffled)
        path = output_dir / f"annotator_{annotator}.csv"
        with path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(shuffled)

    with (output_dir / "annotation_key_private.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(key_rows[0]))
        writer.writeheader()
        writer.writerows(key_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/temporal_referent_v3_language_clusters.jsonl")
    parser.add_argument("--output-dir", default="human_validation")
    parser.add_argument("--compile", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    sources = select_sources(load_jsonl(Path(args.data)))
    selected_path = output_dir / "selected_sources.jsonl"
    output_dir.mkdir(parents=True, exist_ok=True)
    with selected_path.open("w", encoding="utf-8") as handle:
        for row in sources:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    authoring_path = output_dir / "paraphrase_authoring.csv"
    if not args.compile:
        write_authoring(authoring_path, sources)
        print(authoring_path)
        return
    write_packets(output_dir, sources, load_rewrites(authoring_path))
    print(output_dir)


if __name__ == "__main__":
    main()
