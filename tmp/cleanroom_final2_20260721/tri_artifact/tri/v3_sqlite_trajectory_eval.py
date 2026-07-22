from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .v2_tasks import DOMAINS
from .v3_eval import TEMPLATE_FAMILIES, language_cluster_rows


def trajectory_rows() -> list[dict[str, Any]]:
    """Select 40 frozen tasks balanced across styles, templates, domains, and updates."""
    rows = language_cluster_rows()
    by_key = {
        (row["style"], row["template_id"], row["domain"]): row
        for row in rows
    }
    selected: list[dict[str, Any]] = []
    for style_index, style in enumerate(TEMPLATE_FAMILIES):
        domain_indices = (2 * style_index, 2 * style_index + 1)
        for template_index in range(5):
            template_id = f"{style}-t{template_index + 1}"
            for domain_index in domain_indices:
                domain = DOMAINS[domain_index]["domain"]
                selected.append(by_key[(style, template_id, domain)])
    return selected


def smoke_rows() -> list[dict[str, Any]]:
    rows = trajectory_rows()
    return [rows[index] for index in (0, 3, 13, 18, 20, 27, 32, 37)]


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        default="data/temporal_referent_v3_sqlite_trajectory.jsonl",
    )
    ap.add_argument(
        "--smoke-output",
        default="data/temporal_referent_v3_sqlite_trajectory_smoke.jsonl",
    )
    args = ap.parse_args()
    output = Path(args.output)
    smoke_output = Path(args.smoke_output)
    write_rows(output, trajectory_rows())
    write_rows(smoke_output, smoke_rows())
    print(f"wrote {len(trajectory_rows())} tasks to {output}")
    print(f"wrote {len(smoke_rows())} tasks to {smoke_output}")


if __name__ == "__main__":
    main()
