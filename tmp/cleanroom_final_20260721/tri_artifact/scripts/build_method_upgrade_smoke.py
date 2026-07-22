from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V7 = ROOT / "data/temporal_referent_v7_core_replication.jsonl"
V6 = ROOT / "data/temporal_referent_v6_role_heldout.jsonl"
OUT = ROOT / "data/temporal_referent_method_upgrade_smoke_v1.jsonl"


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    v7 = sorted(load(V7), key=lambda row: row["id"])
    chosen: list[dict] = []
    clusters: set[str] = set()
    for binding in ("anchored", "dynamic"):
        for phenomenon in ("explicit", "implicit"):
            for update in ("flip", "stable", "name_collision"):
                row = next(
                    row for row in v7
                    if row["binding"] == binding
                    and row["phenomenon"] == phenomenon
                    and row["update"] == update
                    and row["state_cluster_id"] not in clusters
                )
                chosen.append(row)
                clusters.add(row["state_cluster_id"])
    for row in v7:
        if len(chosen) >= 16:
            break
        if row["state_cluster_id"] not in clusters:
            chosen.append(row)
            clusters.add(row["state_cluster_id"])

    v6 = sorted(load(V6), key=lambda row: row["id"])
    for binding in ("anchored", "dynamic"):
        for update in ("flip", "remove"):
            chosen.append(next(row for row in v6 if row["binding"] == binding and row["update"] == update))
    if len(chosen) != 20:
        raise AssertionError(f"expected 20 smoke tasks, got {len(chosen)}")

    payload = []
    for index, row in enumerate(chosen, start=1):
        item = dict(row)
        item["smoke_index"] = index
        item["smoke_source"] = "v7_core_replication" if row in v7 else "v6_role_heldout"
        payload.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
    text = "\n".join(payload) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(json.dumps({
        "output": str(OUT),
        "tasks": len(chosen),
        "v7_tasks": sum(row in v7 for row in chosen),
        "v6_tasks": sum(row in v6 for row in chosen),
        "state_clusters": len(clusters),
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "coverage": {
            "bindings": sorted({row["binding"] for row in chosen}),
            "phenomena": sorted({row["phenomenon"] for row in chosen}),
            "updates": sorted({row["update"] for row in chosen}),
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
