#!/usr/bin/env python3
"""Freeze one balanced task from every v7 state cluster for repeatability runs."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "temporal_referent_v7_core_replication.jsonl"
OUTPUT = ROOT / "data" / "temporal_referent_v7_repeat_stability_v1.jsonl"
UPDATE_ORDER = {"stable": 0, "flip": 1, "name_collision": 2}


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def freeze(rows: list[dict]) -> list[dict]:
    clusters: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        clusters[row["state_cluster_id"]].append(row)
    if len(clusters) != 40 or any(len(group) != 6 for group in clusters.values()):
        raise ValueError("Expected 40 complete six-task state clusters")

    targets = (20, 20, 14, 13)
    paths: dict[tuple[int, int, int, int], list[dict]] = {(0, 0, 0, 0): []}
    for cluster in sorted(clusters):
        next_paths: dict[tuple[int, int, int, int], list[dict]] = {}
        candidates = sorted(
            clusters[cluster],
            key=lambda row: (
                row["binding"], row["phenomenon"], UPDATE_ORDER[row["update"]], row["id"]
            ),
        )
        for state, path in paths.items():
            for row in candidates:
                anchored, explicit, stable, flip = state
                updated = (
                    anchored + int(row["binding"] == "anchored"),
                    explicit + int(row["phenomenon"] == "explicit"),
                    stable + int(row["update"] == "stable"),
                    flip + int(row["update"] == "flip"),
                )
                if any(value > target for value, target in zip(updated, targets)):
                    continue
                name_collisions = len(path) + 1 - updated[2] - updated[3]
                if name_collisions > 13:
                    continue
                next_paths.setdefault(updated, path + [row])
        paths = next_paths
    if targets not in paths:
        raise ValueError("No subset satisfies the frozen balance constraints")
    return paths[targets]


def validate(rows: list[dict]) -> dict:
    summary = {
        "tasks": len(rows),
        "state_clusters": len({row["state_cluster_id"] for row in rows}),
        "domains": len({row["domain"] for row in rows}),
        "binding": Counter(row["binding"] for row in rows),
        "phenomenon": Counter(row["phenomenon"] for row in rows),
        "update": Counter(row["update"] for row in rows),
    }
    if summary["tasks"] != 40 or summary["state_clusters"] != 40 or summary["domains"] != 10:
        raise ValueError(f"Incomplete repeatability subset: {summary}")
    if summary["binding"] != {"anchored": 20, "dynamic": 20}:
        raise ValueError(f"Unbalanced binding: {summary['binding']}")
    if summary["phenomenon"] != {"explicit": 20, "implicit": 20}:
        raise ValueError(f"Unbalanced phenomenon: {summary['phenomenon']}")
    if max(summary["update"].values()) - min(summary["update"].values()) > 1:
        raise ValueError(f"Unbalanced updates: {summary['update']}")
    return summary


def main() -> None:
    selected = freeze(load(SOURCE))
    summary = validate(selected)
    payload = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in selected)
    OUTPUT.write_text(payload, encoding="utf-8")
    print(OUTPUT)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    print(hashlib.sha256(payload.encode()).hexdigest())


if __name__ == "__main__":
    main()
