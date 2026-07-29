#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tri.unified_environment_holdout import (
    derive_execution_rows,
    freeze_manifest,
    read_jsonl,
    select_clear_clusters,
    validate_candidate_rows,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze the unified environment holdout after the human gate.")
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--human-provenance", type=Path, required=True)
    parser.add_argument("--rule-star-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidates = read_jsonl(args.candidates)
    validate_candidate_rows(candidates)
    selected = select_clear_clusters(candidates)
    rows = derive_execution_rows(selected)
    candidate_sha256 = hashlib.sha256(args.candidates.read_bytes()).hexdigest()
    human_provenance = json.loads(args.human_provenance.read_text(encoding="utf-8"))
    manifest = freeze_manifest(
        candidates,
        selected,
        rows,
        human_provenance,
        candidate_sha256,
    )
    args.output.mkdir(parents=True, exist_ok=False)
    locked = args.output / "locked_execution_rows.jsonl"
    locked.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows), encoding="utf-8")
    manifest["human_provenance_file_sha256"] = hashlib.sha256(
        args.human_provenance.read_bytes()
    ).hexdigest()
    manifest["rule_star_source_sha256"] = hashlib.sha256(
        args.rule_star_source.read_bytes()
    ).hexdigest()
    manifest["locked_execution_sha256"] = hashlib.sha256(locked.read_bytes()).hexdigest()
    (args.output / "freeze_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
