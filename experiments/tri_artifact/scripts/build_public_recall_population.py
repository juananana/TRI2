#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from tri.public_recall_calibrated_audit import unit_key


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d ()-]{6,}\d)(?!\w)")
SENSITIVE_KEY_PARTS = ("api_key", "credential", "password", "secret", "session_token", "token")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def redact_text(value: Any) -> str:
    text = str(value or "")
    text = EMAIL_RE.sub("<EMAIL>", text)
    return PHONE_RE.sub("<PHONE>", text)


def redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): (
                "<REDACTED>"
                if any(part in str(key).lower() for part in SENSITIVE_KEY_PARTS)
                else redact_value(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def git_commit(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def toolsandbox_population(report_path: Path) -> list[dict[str, Any]]:
    report = read_json(report_path)
    rows = []
    for source in report["scenarios"]:
        unit_id = str(source["scenario_name"])
        summary = {
            "source_group": source["source_group"],
            "official_user_task": redact_text(source["official_user_task"]),
            "tool_allow_list": source["tool_allow_list"],
            "milestones": source["milestones"],
            "classification": source["classification"],
        }
        rows.append(
            {
                "dataset": "ToolSandbox",
                "audit_unit_id": unit_id,
                "cluster_id": unit_id,
                "source_path": "reports/official_toolsandbox_tri_prevalence_audit.json",
                "source_unit_sha256": sha256_bytes(canonical_json(source).encode()),
                "source_summary": summary,
            }
        )
    return rows


def appworld_population(tasks_root: Path) -> list[dict[str, Any]]:
    by_family: dict[str, list[Path]] = defaultdict(list)
    for task_dir in tasks_root.iterdir():
        if task_dir.is_dir() and "_" in task_dir.name:
            by_family[task_dir.name.split("_", 1)[0]].append(task_dir)
    rows = []
    for family, task_dirs in sorted(by_family.items()):
        specs = []
        source_hashes = {}
        for task_dir in sorted(task_dirs):
            path = task_dir / "specs.json"
            payload = read_json(path)
            specs.append(redact_text(payload.get("instruction")))
            source_hashes[task_dir.name] = sha256_bytes(path.read_bytes())
        rows.append(
            {
                "dataset": "AppWorld",
                "audit_unit_id": family,
                "cluster_id": family,
                "source_path": "external_pilots/appworld_runtime/data/tasks/<family>_<instance>/specs.json",
                "source_unit_sha256": sha256_bytes(canonical_json(source_hashes).encode()),
                "source_summary": {
                    "task_instances": sorted(path.name for path in task_dirs),
                    "instructions": sorted(set(specs)),
                },
            }
        )
    return rows


def _tau_actions(task: dict[str, Any]) -> list[dict[str, Any]]:
    return (task.get("evaluation_criteria") or {}).get("actions") or []


def tau_population(upstream: Path) -> tuple[list[dict[str, Any]], set[str]]:
    rows = []
    near_match_keys = set()
    for domain in ("airline", "retail", "telecom"):
        path = upstream / "data" / "tau2" / "domains" / domain / "tasks.json"
        for task in read_json(path):
            task_id = str(task["id"])
            unit_id = f"{domain}:{task_id}"
            actions = _tau_actions(task)
            names = [str(action.get("name", "")) for action in actions]
            if domain == "telecom" and {"make_payment", "resume_line"}.issubset(names):
                near_match_keys.add(f"tau3-bench::{unit_id}")
            summary_actions = []
            for action in actions:
                arguments = action.get("arguments") or {}
                summary_actions.append(
                    {
                        "requestor": action.get("requestor", "assistant"),
                        "name": action.get("name"),
                        "argument_keys": sorted(arguments),
                        "stable_id_fields": sorted(
                            key
                            for key in arguments
                            if key.endswith("_id") or key.endswith("_ids")
                        ),
                    }
                )
            description = task.get("description") or {}
            instructions = (task.get("user_scenario") or {}).get("instructions") or {}
            rows.append(
                {
                    "dataset": "tau3-bench",
                    "audit_unit_id": unit_id,
                    "cluster_id": unit_id,
                    "source_path": str(path.relative_to(upstream)),
                    "source_unit_sha256": sha256_bytes(canonical_json(task).encode()),
                    "source_summary": {
                        "domain": domain,
                        "purpose": redact_text(description.get("purpose")),
                        "reason_for_call": redact_text(instructions.get("reason_for_call")),
                        "evaluation_actions": summary_actions,
                    },
                }
            )
    return rows, near_match_keys


def external_population(path: Path, external_root: Path) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in read_jsonl(path):
        grouped[f"{row['dataset']}::{row['cluster_id']}"] .append(row)
    json_cache: dict[Path, Any] = {}

    def raw_record(row: dict[str, Any]) -> dict[str, Any]:
        dataset = row["dataset"]
        if dataset == "API-Bank":
            source = external_root / "api-bank" / row["source_path"]
            if source not in json_cache:
                json_cache[source] = read_json(source)
            payload = json_cache[source]
            index = int(str(row["unit_id"]).rsplit(":", 1)[1])
            record = payload[index]
            return redact_value(
                {
                    "instruction": record.get("instruction"),
                    "input": record.get("input"),
                    "expected_output": record.get("expected_output"),
                }
            )
        if dataset == "BFCL":
            source = external_root / "bfcl" / row["source_path"]
            if source not in json_cache:
                json_cache[source] = {
                    str(item["id"]): item
                    for item in read_jsonl(source)
                }
            payload = json_cache[source]
            record = payload[str(row["unit_id"])]
            involved = record.get("involved_classes", [])
            initial = record.get("initial_config", {})
            return redact_value(
                {
                    "question": record.get("question", []),
                    "tool_sequence": record.get("path", []),
                    "involved_classes": involved,
                    "initial_config": {
                        name: initial.get(name, {}) for name in involved
                    },
                }
            )
        if dataset == "ToolTalk":
            source = external_root / "tooltalk" / row["source_path"]
            if source not in json_cache:
                json_cache[source] = read_json(source)
            record = json_cache[source]
            return redact_value(
                {
                    "scenario": record.get("scenario"),
                    "conversation": record.get("conversation", []),
                    "apis_used": record.get("apis_used", []),
                    "suites_used": record.get("suites_used", []),
                }
            )
        raise ValueError(f"unknown external dataset: {dataset}")

    rows = []
    for key, members in sorted(grouped.items()):
        dataset, cluster_id = key.split("::", 1)
        rows.append(
            {
                "dataset": dataset,
                "audit_unit_id": cluster_id,
                "cluster_id": cluster_id,
                "source_path": sorted({str(row["source_path"]) for row in members}),
                "source_unit_sha256": sha256_bytes(canonical_json(members).encode()),
                "source_summary": {
                    "source_records": [raw_record(row) for row in members],
                },
            }
        )
    return rows


def candidate_basis(
    annotation_candidates: list[dict[str, Any]],
    triage: list[dict[str, Any]],
    tau_near_matches: set[str],
) -> dict[str, list[str]]:
    basis: dict[str, set[str]] = defaultdict(set)
    for row in annotation_candidates:
        key = f"{row['dataset']}::{row['cluster_id']}"
        basis[key].add("payload_backed_retrieval_candidate")
    for row in triage:
        source_kind = row.get("source_kind")
        suite = str(row.get("suite"))
        if source_kind == "external_structural_candidate":
            cluster = (row.get("source_excerpt") or {}).get("cluster_id")
            basis[f"{suite}::{cluster}"].add("cross_suite_external_triage")
        elif suite == "ToolSandbox" and source_kind in {
            "closest_case",
            "stratified_official_audit",
        }:
            basis[f"ToolSandbox::{row['case_id']}"] .add(
                f"cross_suite_{source_kind}"
            )
        elif suite == "AppWorld":
            basis["AppWorld::8ce6779"].add(f"cross_suite_{source_kind}")
    for key in tau_near_matches:
        basis[key].add("source_audit_near_match")
    return {key: sorted(values) for key, values in basis.items()}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the six-suite public recall population.")
    parser.add_argument(
        "--appworld-tasks",
        type=Path,
        default=ROOT / "external_pilots" / "appworld_runtime" / "data" / "tasks",
    )
    parser.add_argument(
        "--tau-root", type=Path, default=REPOSITORY / "external_sources" / "tau2-bench"
    )
    parser.add_argument(
        "--external-root", type=Path, default=REPOSITORY / "external_sources"
    )
    parser.add_argument(
        "--population", type=Path, default=ROOT / "data" / "public_recall_population_v1.jsonl"
    )
    parser.add_argument(
        "--candidates", type=Path, default=ROOT / "data" / "public_recall_candidate_census_v1.jsonl"
    )
    parser.add_argument(
        "--report", type=Path, default=ROOT / "reports" / "public_recall_population_v1.json"
    )
    args = parser.parse_args()

    population = []
    population.extend(
        toolsandbox_population(ROOT / "reports" / "official_toolsandbox_tri_prevalence_audit.json")
    )
    population.extend(appworld_population(args.appworld_tasks))
    tau_rows, tau_near_matches = tau_population(args.tau_root)
    population.extend(tau_rows)
    population.extend(
        external_population(
            ROOT / "data" / "external_public_opportunity_candidates_v1.jsonl",
            args.external_root,
        )
    )
    population = sorted(population, key=unit_key)
    keys = [unit_key(row) for row in population]
    if len(keys) != len(set(keys)):
        raise ValueError("public recall population contains duplicate audit units")

    basis = candidate_basis(
        read_jsonl(ROOT / "data" / "external_public_annotation_candidates_v1.jsonl"),
        read_jsonl(ROOT / "data" / "model_assisted_public_recall_triage_v1.jsonl"),
        tau_near_matches,
    )
    population_by_key = {unit_key(row): row for row in population}
    if not set(basis).issubset(population_by_key):
        missing = sorted(set(basis) - set(population_by_key))
        raise ValueError(f"candidate census does not map to the population: {missing[:10]}")
    candidates = [
        {**population_by_key[key], "candidate_basis": basis[key]}
        for key in sorted(basis)
    ]
    write_jsonl(args.population, population)
    write_jsonl(args.candidates, candidates)

    counts: dict[str, int] = defaultdict(int)
    candidate_counts: dict[str, int] = defaultdict(int)
    for row in population:
        counts[row["dataset"]] += 1
    for row in candidates:
        candidate_counts[row["dataset"]] += 1
    external_report = read_json(ROOT / "reports" / "external_public_opportunity_audit_v1.json")
    report = {
        "audit_version": "TRI-public-recall-population-v1",
        "evidence_status": "frozen sampling frame input; no human labels",
        "population_rows": len(population),
        "candidate_rows": len(candidates),
        "population_by_dataset": dict(sorted(counts.items())),
        "candidates_by_dataset": dict(sorted(candidate_counts.items())),
        "population_sha256": sha256_bytes(args.population.read_bytes()),
        "candidate_sha256": sha256_bytes(args.candidates.read_bytes()),
        "commits": {
            "ToolSandbox": git_commit(REPOSITORY / "external_sources" / "ToolSandbox_official"),
            "AppWorld": git_commit(REPOSITORY / "external_sources" / "AppWorld_official"),
            "tau3-bench": git_commit(args.tau_root),
            **external_report["manifest_commits"],
        },
        "unit_definition": {
            "ToolSandbox": "semantic scenario family",
            "AppWorld": "generator family (three released task instances)",
            "tau3-bench": "core task definition",
            "API-Bank": "released test unit",
            "BFCL": "multi-turn task cluster across variants",
            "ToolTalk": "released dialogue",
        },
        "model_calls_allowed": False,
        "next_gate": "freeze stratified sample and collect three independent human labels",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
