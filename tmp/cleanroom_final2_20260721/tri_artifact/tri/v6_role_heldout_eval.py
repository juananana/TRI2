from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .v5_stress_eval import stress_rows, write


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def select_balanced(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["template_id"]].append(row)
    selected: list[dict[str, Any]] = []
    for index, template_id in enumerate(sorted(groups)):
        group = sorted(groups[template_id], key=lambda row: row["domain"])
        if len(group) != 4:
            raise ValueError(f"Expected four unseen domains for {template_id}, found {len(group)}")
        selected.extend([group[index % 4], group[(index + 2) % 4]])
    if len(selected) != 40:
        raise ValueError(f"Expected 40 held-out sources, found {len(selected)}")
    counts = Counter(row["domain"] for row in selected)
    if set(counts.values()) != {10}:
        raise ValueError(f"Held-out domain imbalance: {counts}")
    return sorted(selected, key=lambda row: row["id"])


def heldout_rows(source: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = stress_rows(select_balanced(source))
    for row in rows:
        row["id"] = row["id"].replace("tri-v3-unseen", "tri-v6-role-heldout")
        row["candidate"] = "tri-v6-role-heldout"
        row["source_split"] = "v3-unseen-schemas"
    return rows


def smoke_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    picks: list[dict[str, Any]] = []
    for binding in ("anchored", "dynamic"):
        subset = [row for row in rows if row["binding"] == binding]
        for update in ("flip", "remove"):
            picks.append(next(row for row in subset if row["update"] == update))
    return picks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="data/temporal_referent_v3_unseen_domains.jsonl")
    parser.add_argument("--output", default="data/temporal_referent_v6_role_heldout.jsonl")
    parser.add_argument("--smoke-output", default="data/temporal_referent_v6_role_heldout_smoke.jsonl")
    args = parser.parse_args()
    rows = heldout_rows(load(Path(args.source)))
    write(Path(args.output), rows)
    write(Path(args.smoke_output), smoke_rows(rows))
    print(args.output)
    print(args.smoke_output)


if __name__ == "__main__":
    main()
