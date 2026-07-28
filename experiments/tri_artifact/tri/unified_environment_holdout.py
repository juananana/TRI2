from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


RUN_VERSION = "TRI-unified-environment-holdout-v1"
EVIDENCE_STATUS = "planned/unverified"
ENVIRONMENT_COMMITS = {
    "AgentDojo": "089ed468cf3ed0322acc66b0211f26d9d90dbf60",
    "ToolSandbox": "165848b9a78cead7ca7fe7c89c688b58e6501219",
}
ENVIRONMENTS = tuple(ENVIRONMENT_COMMITS)
WRITERS = tuple(f"W{i}" for i in range(1, 13))
ANNOTATORS = tuple(f"A{i}" for i in range(1, 4))
TARGET_PAIRS_PER_ENV = 20
TARGET_CLUSTERS = 40


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _ids(state: Any) -> set[str]:
    if not isinstance(state, list):
        raise ValueError("state snapshot must be a list")
    ids = {str(item.get("id")) for item in state if isinstance(item, dict) and item.get("id") is not None}
    if len(ids) != len(state):
        raise ValueError("state IDs must be unique and non-null")
    return ids


def _winner(row: dict[str, Any], suffix: str) -> str:
    value = row.get(f"{suffix}_winner")
    if value is None:
        raise ValueError(f"missing {suffix}_winner for {row.get('cluster_id')}")
    return str(value)


def validate_candidate_rows(rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("candidate inventory is empty")
    seen_items: set[str] = set()
    by_cluster: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        cluster = str(row.get("cluster_id", ""))
        item_id = str(row.get("item_id", ""))
        if not cluster or not item_id or item_id in seen_items:
            raise ValueError(f"duplicate or missing item_id/cluster_id: {item_id}/{cluster}")
        seen_items.add(item_id)
        environment = row.get("environment")
        if environment not in ENVIRONMENTS:
            raise ValueError(f"unknown environment: {environment}")
        if row.get("environment_commit") != ENVIRONMENT_COMMITS[environment]:
            raise ValueError(f"environment commit mismatch for {cluster}")
        for key in ("selector", "action", "action_schema", "s0_state", "s1_changed_state", "s1_stable_state"):
            if key not in row:
                raise ValueError(f"missing {key} for {cluster}")
        s0 = _ids(row["s0_state"])
        changed = _ids(row["s1_changed_state"])
        stable = _ids(row["s1_stable_state"])
        old = _winner(row, "pre_refresh")
        new = _winner(row, "post_refresh")
        if old not in s0 or old not in changed or new not in changed:
            raise ValueError(f"changed row target linkage failed for {cluster}")
        if old == new:
            raise ValueError(f"changed row has no winner change for {cluster}")
        if old not in stable:
            raise ValueError(f"stable state must retain old target for {cluster}")
        by_cluster[cluster].append(row)
    if any(len(members) != 2 for members in by_cluster.values()):
        raise ValueError("each candidate cluster must contain exactly two instruction members")


def validate_writer_assignment(rows: list[dict[str, Any]]) -> None:
    if len(rows) != 2:
        raise ValueError("each candidate cluster needs two instruction members")
    writers = {str(row.get("writer_id")) for row in rows}
    if len(writers) != 2 or not writers.issubset(WRITERS):
        raise ValueError("pair members must use two distinct frozen writers")
    modes = {str(row.get("reference_mode")) for row in rows}
    if modes != {"preserve", "reevaluate"}:
        raise ValueError("candidate pair must contain Preserve and Reevaluate")


def _majority(values: list[str]) -> str | None:
    counts = Counter(value for value in values if value)
    if not counts:
        return None
    value, count = counts.most_common(1)[0]
    return value if count >= 2 else None


def annotate_clear(row: dict[str, Any]) -> dict[str, Any]:
    required = {"writer_intent", "adjudications", "writer_id", "reference_mode"}
    if not required.issubset(row):
        raise ValueError(f"missing human fields for {row.get('item_id')}")
    adjudications = row["adjudications"]
    if not isinstance(adjudications, dict) or set(adjudications) != set(ANNOTATORS):
        raise ValueError(f"exactly three annotators required for {row.get('item_id')}")
    labels = [str(adjudications[key]) for key in ANNOTATORS]
    majority = _majority(labels)
    writer_intent = str(row["writer_intent"])
    clear = majority is not None and majority == writer_intent and writer_intent in {
        "preserve",
        "reevaluate",
    }
    return {
        **row,
        "annotator_majority": majority,
        "clear": clear,
        "adjudication_agreement": sum(label == majority for label in labels) / 3 if majority else 0.0,
    }


def select_clear_clusters(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["cluster_id"])].append(annotate_clear(row))
    clear_by_env: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cluster_id, members in grouped.items():
        if len(members) != 2:
            raise ValueError(f"cluster {cluster_id} does not have two members")
        validate_writer_assignment(members)
        if all(member["clear"] for member in members):
            environment = members[0]["environment"]
            clear_by_env[environment].append({"cluster_id": cluster_id, "members": members})
    for environment in ENVIRONMENTS:
        if len(clear_by_env[environment]) < TARGET_PAIRS_PER_ENV:
            raise RuntimeError(
                f"clear-cluster gate failed for {environment}: "
                f"{len(clear_by_env[environment])}/{TARGET_PAIRS_PER_ENV}"
            )
    selected = []
    for environment in ENVIRONMENTS:
        selected.extend(clear_by_env[environment][:TARGET_PAIRS_PER_ENV])
    if len(selected) != TARGET_CLUSTERS:
        raise AssertionError("selection did not produce exactly 40 clusters")
    return selected


def derive_execution_rows(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(clusters) != TARGET_CLUSTERS:
        raise ValueError("execution freeze requires exactly 40 clear clusters")
    rows: list[dict[str, Any]] = []
    for cluster in clusters:
        members = cluster["members"]
        preserve = next(row for row in members if row["reference_mode"] == "preserve")
        reevaluate = next(row for row in members if row["reference_mode"] == "reevaluate")
        base = {
            "cluster_id": cluster["cluster_id"],
            "environment": preserve["environment"],
            "environment_commit": preserve["environment_commit"],
            "selector": preserve["selector"],
            "action": preserve["action"],
            "action_schema": preserve["action_schema"],
            "s0_state": preserve["s0_state"],
            "adjudications": {row["item_id"]: row["adjudications"] for row in members},
        }
        for row_kind, instruction_row, state_key, changed in (
            ("changed_preserve", preserve, "s1_changed_state", True),
            ("changed_reevaluate", reevaluate, "s1_changed_state", True),
            ("stable_preserve", preserve, "s1_stable_state", False),
        ):
            execution = {
                **base,
                "row_id": f"{cluster['cluster_id']}::{row_kind}",
                "row_kind": row_kind,
                "instruction": instruction_row["instruction"],
                "reference_mode_gold": instruction_row["reference_mode"],
                "s1_state": instruction_row[state_key],
                "pre_refresh_target": instruction_row["pre_refresh_winner"],
                "post_refresh_target": instruction_row["post_refresh_winner"] if changed else instruction_row["pre_refresh_winner"],
                "changed_winner": changed,
                "writer_id": instruction_row["writer_id"],
            }
            rows.append(execution)
    if len(rows) != 120:
        raise AssertionError("execution freeze did not produce 120 rows")
    return rows


def freeze_manifest(candidates: list[dict[str, Any]], selected: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = "".join(canonical_json(row) + "\n" for row in rows).encode("utf-8")
    return {
        "run_version": RUN_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "candidate_rows": len(candidates),
        "selected_clusters": len(selected),
        "execution_rows": len(rows),
        "environment_commits": ENVIRONMENT_COMMITS,
        "selected_cluster_ids": [cluster["cluster_id"] for cluster in selected],
        "execution_rows_sha256": sha256_bytes(payload),
        "model_calls_allowed": True,
    }


def selection_maximizers(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        raise ValueError("controller result table is empty")
    required = {"environment", "model", "controller", "e2e", "pairacc", "wrong_writes"}
    if any(not required.issubset(row) for row in results):
        raise ValueError("selection results are missing required fields")
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        groups[(str(row["environment"]), str(row["model"]))].append(row)
    output = []
    for key, rows in sorted(groups.items()):
        max_e2e = max(float(row["e2e"]) for row in rows)
        max_pairacc = max(float(row["pairacc"]) for row in rows)
        e2e_set = sorted(row["controller"] for row in rows if float(row["e2e"]) == max_e2e)
        pair_set = sorted(row["controller"] for row in rows if float(row["pairacc"]) == max_pairacc)
        pair_rows = [row for row in rows if row["controller"] in pair_set]
        e2e_rows = [row for row in rows if row["controller"] in e2e_set]
        output.append({
            "environment": key[0],
            "model": key[1],
            "e2e_maximizers": e2e_set,
            "pairacc_maximizers": pair_set,
            "strong_selection_change": not set(e2e_set).intersection(pair_set),
            "pairacc_wrong_writes_max": max(float(row["wrong_writes"]) for row in pair_rows),
            "e2e_wrong_writes_min": min(float(row["wrong_writes"]) for row in e2e_rows),
            "tie_regret": max_e2e - max_pairacc,
        })
    return {
        "cells": output,
        "promote_practical_selection": sum(
            cell["strong_selection_change"]
            and cell["pairacc_wrong_writes_max"] <= cell["e2e_wrong_writes_min"]
            for cell in output
        ) >= 2,
    }


def build_writer_forms(rows: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    """Write redacted writer cards; S1, gold, alternate members, and annotations are omitted."""
    validate_candidate_rows(rows)
    by_writer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_writer[str(row["writer_id"])].append(row)
    if set(by_writer) - set(WRITERS):
        raise ValueError("unknown writer in candidate inventory")
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest = {"run_version": RUN_VERSION, "evidence_status": EVIDENCE_STATUS, "forms": {}}
    for writer_id in sorted(by_writer):
        assigned = list(by_writer[writer_id])
        random.Random(20260729 + int(writer_id[1:])).shuffle(assigned)
        lines = [
            f"# Unified environment writing form {writer_id}",
            "",
            "Write one natural English request per card. Do not use external tools, search, AI, or another person.",
            "Only the current records and the required operation order are shown.",
            "",
        ]
        for index, row in enumerate(assigned, 1):
            lines.extend([
                f"## Card {index:02d} [{row['item_id']}]",
                f"Environment: {row['environment']}",
                f"Available action: {row['action']}",
                f"Selection criterion: {row['selector']}",
                "Current records:",
                "```json",
                json.dumps(row["s0_state"], ensure_ascii=True, sort_keys=True),
                "```",
                "Required order: " + (
                    "select one object before refresh, then act on that same object"
                    if row["reference_mode"] == "preserve"
                    else "refresh first, then select one object and act on it"
                ) + ".",
                "Your English request:",
                "",
                "____________________________________________________________",
                "",
            ])
        path = output_dir / f"writer_{writer_id}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        manifest["forms"][writer_id] = sha256_bytes(path.read_bytes())
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return manifest


def build_annotator_form(rows: list[dict[str, Any]], annotator: str, output: Path) -> dict[str, Any]:
    """Write a blind refreshed-state labeling form after writer strings are locked."""
    if annotator not in ANNOTATORS:
        raise ValueError(f"unknown annotator: {annotator}")
    ordered = list(rows)
    random.Random(20260801 + int(annotator[1:])).shuffle(ordered)
    lines = [f"# Blind target annotation form {annotator}", "", "Choose one target ID or CLARIFY. Do not infer pair membership or gold.", ""]
    for index, row in enumerate(ordered, 1):
        lines.extend([
            f"## Item {index:03d}",
            "Instruction:",
            row["instruction"],
            "Refreshed records:",
            "```json",
                json.dumps(row.get("s1_state") or row["s1_changed_state"], ensure_ascii=True, sort_keys=True),
            "```",
            "Target ID or CLARIFY:",
            "",
        ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return {"annotator": annotator, "items": len(rows), "sha256": sha256_bytes(output.read_bytes())}
