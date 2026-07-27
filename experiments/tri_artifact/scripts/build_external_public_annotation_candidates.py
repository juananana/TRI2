#!/usr/bin/env python3
"""Build the frozen redacted candidate inventory for external AI annotation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tri.external_public_annotation import build_annotation_candidates


def parse_args() -> argparse.Namespace:
    artifact_root = Path(__file__).resolve().parents[1]
    project_root = artifact_root.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audit-records",
        type=Path,
        default=artifact_root / "data" / "external_public_opportunity_candidates_v1.jsonl",
    )
    parser.add_argument("--external-root", type=Path, default=project_root / "external_sources")
    parser.add_argument(
        "--output",
        type=Path,
        default=artifact_root / "data" / "external_public_annotation_candidates_v1.jsonl",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = build_annotation_candidates(
        args.audit_records,
        args.external_root / "bfcl",
        args.external_root / "tooltalk",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in candidates
    )
    args.output.write_text(payload, encoding="utf-8")
    by_dataset: dict[str, int] = {}
    for row in candidates:
        by_dataset[row["dataset"]] = by_dataset.get(row["dataset"], 0) + 1
    print(
        json.dumps(
            {
                "output": str(args.output),
                "records": len(candidates),
                "by_dataset": by_dataset,
                "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
                "bytes": len(payload.encode("utf-8")),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
