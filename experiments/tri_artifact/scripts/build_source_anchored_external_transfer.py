#!/usr/bin/env python3
"""Build and execute the frozen zero-API external transfer gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.source_anchored_external_transfer import (
    attach_source_hashes,
    build_agentdojo_clusters,
    build_manifest,
    build_report,
    build_state_bench_clusters,
    canonical_jsonl,
    materialize_tasks,
    render_markdown,
    verify_source_tools,
)


def parse_args() -> argparse.Namespace:
    artifact = Path(__file__).resolve().parents[1]
    project = artifact.parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--state-bench-root", type=Path, default=project / "external_sources/state-bench"
    )
    parser.add_argument(
        "--agentdojo-root", type=Path, default=project / "external_sources/agentdojo"
    )
    parser.add_argument(
        "--agentdojo-deps-root", type=Path, default=project / "external_sources/agentdojo-deps"
    )
    parser.add_argument(
        "--inventory-out",
        type=Path,
        default=artifact / "data/source_anchored_external_transfer_tasks_v1.jsonl",
    )
    parser.add_argument(
        "--manifest-out",
        type=Path,
        default=artifact / "reports/source_anchored_external_transfer_source_manifest_v1.json",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=artifact / "reports/source_anchored_external_transfer_zero_api_v1.json",
    )
    parser.add_argument(
        "--report-md",
        type=Path,
        default=artifact / "reports/source_anchored_external_transfer_zero_api_v1.md",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    clusters = build_state_bench_clusters(args.state_bench_root)
    clusters.extend(build_agentdojo_clusters(args.agentdojo_root))
    attach_source_hashes(clusters, args.state_bench_root, args.agentdojo_root)
    tasks = materialize_tasks(clusters)
    manifest = build_manifest(clusters, args.state_bench_root, args.agentdojo_root)
    tool_results = verify_source_tools(
        tasks,
        args.state_bench_root,
        args.agentdojo_root,
        args.agentdojo_deps_root,
    )
    report = build_report(clusters, tasks, manifest, tool_results)

    for path in (args.manifest_out, args.report_json, args.report_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report_md.write_text(render_markdown(report), encoding="utf-8")
    if report["gate"] == "GO":
        args.inventory_out.parent.mkdir(parents=True, exist_ok=True)
        args.inventory_out.write_bytes(canonical_jsonl(tasks))
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
