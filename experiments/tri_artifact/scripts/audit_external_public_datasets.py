#!/usr/bin/env python3
"""Run the frozen zero-API external public-dataset opportunity audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.external_public_opportunity_audit import (
    audit_api_bank,
    audit_bfcl,
    audit_tooltalk,
    build_report,
    build_source_manifest,
    render_markdown,
)


COMMITS = {
    "BFCL": "6ea57973c7a6097fd7c5915698c54c17c5b1b6c8",
    "ToolTalk": "e05f4ce6132c80ed33392b81535b077d56ab28fd",
    "API-Bank": "12e8158b7628c168f07e8f31fbbe3445e99f44cf",
}


def parse_args() -> argparse.Namespace:
    artifact_root = Path(__file__).resolve().parents[1]
    project_root = artifact_root.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-root", type=Path, default=project_root / "external_sources")
    parser.add_argument(
        "--candidates-out",
        type=Path,
        default=artifact_root / "data" / "external_public_opportunity_candidates_v1.jsonl",
    )
    parser.add_argument(
        "--manifest-out",
        type=Path,
        default=artifact_root / "reports" / "external_public_source_manifest_v1.json",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=artifact_root / "reports" / "external_public_opportunity_audit_v1.json",
    )
    parser.add_argument(
        "--report-md",
        type=Path,
        default=artifact_root / "reports" / "external_public_opportunity_audit_v1.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = {
        "BFCL": args.external_root / "bfcl",
        "ToolTalk": args.external_root / "tooltalk",
        "API-Bank": args.external_root / "api-bank",
    }
    missing = [dataset for dataset, path in sources.items() if not path.is_dir()]
    if missing:
        raise SystemExit(f"missing external source directories: {', '.join(missing)}")

    manifest = build_source_manifest(sources, COMMITS)
    records = audit_bfcl(sources["BFCL"])
    records.extend(audit_tooltalk(sources["ToolTalk"]))
    records.extend(audit_api_bank(sources["API-Bank"]))
    report = build_report(records, manifest)

    for path in (args.candidates_out, args.manifest_out, args.report_json, args.report_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.candidates_out.write_text(
        "".join(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n" for record in records),
        encoding="utf-8",
    )
    args.manifest_out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
