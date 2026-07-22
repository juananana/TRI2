from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from tri.event_graph_controller import (
    ReferentialCapability,
    VersionedEntityStore,
    compile_oracle_event_graph,
    compile_oracle_selector,
    derive_reference_mode,
    execute_event_graph,
    execute_selector,
    issue_capability,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    "temporal_referent_v3_language_clusters.jsonl",
    "temporal_referent_v7_core_replication.jsonl",
    "temporal_referent_v6_role_heldout.jsonl",
)


def load(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_dataset(path: Path) -> dict[str, Any]:
    rows = load(path)
    counts: Counter[str] = Counter()
    for task in rows:
        graph = compile_oracle_event_graph(task)
        selector = compile_oracle_selector(task)
        expected_mode = "preserve" if task["binding"] == "anchored" else "reevaluate"
        expected_capability = (
            task["pre_refresh_target"]
            if task["binding"] == "anchored"
            else task["post_refresh_target"]
        )
        capability = issue_capability(task, graph, selector)
        counts["mode_correct"] += derive_reference_mode(graph) == expected_mode
        counts["selector_initial_correct"] += (
            execute_selector(selector, task["initial_state"]) == task["pre_refresh_target"]
        )
        counts["selector_final_correct"] += (
            execute_selector(selector, task.get("final_state", task["refreshed_state"]))
            == task["post_refresh_target"]
        )
        counts["authorized_target_correct"] += (
            execute_event_graph(task, graph, selector) == task["correct_target"]
        )
        counts["capability_binding_correct"] += capability.target_id == expected_capability
    return {
        "dataset": path.name,
        "sha256": sha256(path),
        "tasks": len(rows),
        **{key: counts[key] for key in (
            "mode_correct", "selector_initial_correct", "selector_final_correct",
            "authorized_target_correct", "capability_binding_correct",
        )},
    }


def evaluate_concurrency(repeats: int = 20) -> dict[str, Any]:
    statuses: Counter[str] = Counter()
    legal_writes = 0
    false_blocks = 0
    wrong_writes = 0
    mutations = (
        "legal", "unrelated_update", "target_version", "invalidate", "delete", "id_alias"
    )
    for index in range(repeats):
        base = [
            {"id": "T-1", "display": "Target", "status": "pending", "actionable": True},
            {"id": "T-2", "display": "Other", "status": "pending", "actionable": True},
        ]
        for mutation in mutations:
            store = VersionedEntityStore(base)
            capability = ReferentialCapability(
                target_id="T-1",
                action="approve",
                source_event="E1",
                binding_epoch="initial",
                action_preconditions=(("actionable", True), ("status", "pending")),
                expected_version=store.version("T-1"),
            )
            if mutation == "unrelated_update":
                store.update("T-2", note=index)
            elif mutation == "target_version":
                store.update("T-1", note=index)
            elif mutation == "invalidate":
                store.update("T-1", actionable=False)
            elif mutation == "delete":
                store.delete("T-1")
            elif mutation == "id_alias":
                store.delete("T-1")
                store.add({
                    "id": f"ALIAS-{index}", "display": "Target",
                    "status": "pending", "actionable": True,
                })
            result = store.atomic_write(capability, "approve")
            statuses[result.status] += 1
            legal = mutation in {"legal", "unrelated_update"}
            legal_writes += legal and result.status == "written"
            false_blocks += legal and result.status != "written"
            wrong_writes += result.written_id not in {None, "T-1"}
    return {
        "sequences": repeats * len(mutations),
        "mutations": list(mutations),
        "statuses": dict(sorted(statuses.items())),
        "legal_writes": legal_writes,
        "false_blocks": false_blocks,
        "wrong_writes": wrong_writes,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Event Graph Oracle and Atomic Gate Report",
        "",
        "## Oracle datasets",
        "",
        "| Dataset | Tasks | Mode | Selector initial | Selector final | Authorized target | Capability binding |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["datasets"]:
        total = row["tasks"]
        lines.append(
            f"| {row['dataset']} | {total} | {row['mode_correct']}/{total} | "
            f"{row['selector_initial_correct']}/{total} | {row['selector_final_correct']}/{total} | "
            f"{row['authorized_target_correct']}/{total} | "
            f"{row['capability_binding_correct']}/{total} |"
        )
    concurrency = report["concurrency"]
    lines.extend([
        "",
        "## Atomic gate",
        "",
        f"- Deterministic sequences: {concurrency['sequences']}",
        f"- Legal writes: {concurrency['legal_writes']}",
        f"- False blocks: {concurrency['false_blocks']}",
        f"- Wrong writes: {concurrency['wrong_writes']}",
        f"- Status counts: `{json.dumps(concurrency['statuses'], sort_keys=True)}`",
        "",
        "This is a zero-API implementation check. It does not measure learned compiler accuracy.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=ROOT / "reports/event_graph_oracle_v1.json")
    parser.add_argument("--md-output", type=Path, default=ROOT / "reports/event_graph_oracle_v1.md")
    args = parser.parse_args()
    report = {
        "kind": "zero_api_oracle_and_atomic_gate",
        "datasets": [evaluate_dataset(ROOT / "data" / name) for name in DATASETS],
        "concurrency": evaluate_concurrency(),
    }
    args.json_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.md_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
