"""Post-hoc residual audit on rows missed by deterministic Rule*."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report(rule_path: Path, runs: dict[str, Path]) -> dict:
    rule_rows = load_jsonl(rule_path)
    hard_ids = {
        row["task"]["id"]
        for row in rule_rows
        if row["result"].get("predicted_target") != row["task"]["correct_target"]
    }
    pairs: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in rule_rows:
        task = row["task"]
        pairs[(task["state_cluster_id"], task["update"])].append(task["id"])

    results = {}
    for label, path in runs.items():
        rows = [row for row in load_jsonl(path) if row["task"]["id"] in hard_ids]
        if {row["task"]["id"] for row in rows} != hard_ids:
            raise ValueError(f"{label}: residual IDs do not match Rule*-hard rows")
        results[label] = {
            "correct": sum(bool(row["result"].get("success")) for row in rows),
            "n": len(rows),
            "preserve_correct": sum(
                bool(row["result"].get("success"))
                for row in rows
                if row["task"]["binding"] == "anchored"
            ),
            "preserve_n": sum(row["task"]["binding"] == "anchored" for row in rows),
            "reevaluate_correct": sum(
                bool(row["result"].get("success"))
                for row in rows
                if row["task"]["binding"] == "dynamic"
            ),
            "reevaluate_n": sum(row["task"]["binding"] == "dynamic" for row in rows),
            "source": path.name,
            "sha256": sha256(path),
        }
    return {
        "status": "post_hoc_residual_audit_zero_api",
        "selection": "Rows on which benchmark-aware Rule* v2 predicts the wrong exact target",
        "rule_source": rule_path.name,
        "rule_sha256": sha256(rule_path),
        "rule_hard_rows": len(hard_ids),
        "preserve_rows": sum(
            row["task"]["id"] in hard_ids and row["task"]["binding"] == "anchored"
            for row in rule_rows
        ),
        "reevaluate_rows": sum(
            row["task"]["id"] in hard_ids and row["task"]["binding"] == "dynamic"
            for row in rule_rows
        ),
        "complete_rule_hard_pairs": sum(
            len(ids) == 2 and all(task_id in hard_ids for task_id in ids)
            for ids in pairs.values()
        ),
        "results": results,
        "boundary": (
            "The subset is selected after observing Rule* errors and contains no complete "
            "Preserve/Reevaluate pair; row accuracy is descriptive and PairAcc is undefined."
        ),
    }


def markdown(report: dict) -> str:
    lines = [
        "# Rule*-Hard Residual Audit",
        "",
        f"Status: `{report['status']}`.",
        "",
        f"Rule*-hard rows: {report['rule_hard_rows']} "
        f"({report['preserve_rows']} Preserve, {report['reevaluate_rows']} Reevaluate).",
        f"Complete residual pairs: {report['complete_rule_hard_pairs']}.",
        "",
        "| Model / method | Correct | Preserve | Reevaluate |",
        "|---|---:|---:|---:|",
    ]
    for label, row in report["results"].items():
        lines.append(
            f"| {label} | {row['correct']}/{row['n']} | "
            f"{row['preserve_correct']}/{row['preserve_n']} | "
            f"{row['reevaluate_correct']}/{row['reevaluate_n']} |"
        )
    lines.extend(["", report["boundary"], ""])
    return "\n".join(lines)
