from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .v5_stress_report import cluster_delta_ci, exact_mcnemar


def load(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        task_id = row["task"]["id"]
        if task_id in output:
            raise ValueError(f"Duplicate task id: {task_id}")
        output[task_id] = row
    return output


def _slice_counts(rows: list[dict[str, Any]]) -> dict[str, dict[str, list[int]]]:
    slices: dict[str, dict[str, list[int]]] = {}
    for field in ("binding", "style", "update", "domain"):
        counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for row in rows:
            key = str(row["task"][field])
            counts[key][0] += int(bool(row["result"].get("success")))
            counts[key][1] += 1
        slices[field] = dict(sorted(counts.items()))
    return slices


def controller_summary(rows_by_id: dict[str, dict[str, Any]], label: str) -> dict[str, Any]:
    rows = [rows_by_id[key] for key in sorted(rows_by_id)]
    statuses = Counter(str(row["result"].get("action_status")) for row in rows)
    return {
        "label": label,
        "n": len(rows),
        "success": sum(bool(row["result"].get("success")) for row in rows),
        "final_state_success": sum(bool(row["result"].get("final_state_success")) for row in rows),
        "action_status": dict(sorted(statuses.items())),
        "collateral_modifications": sum(int(row["result"].get("collateral_modifications", 0)) for row in rows),
        "api_errors": sum(row.get("status") != "ok" for row in rows),
        "internal_errors": sum(bool(row["result"].get("errors")) for row in rows),
        "error_rows": sum(
            row.get("status") != "ok" or bool(row["result"].get("errors"))
            for row in rows
        ),
        "requests": sum(int(row.get("api_request_attempts", 0)) for row in rows),
        "retries": sum(int(row.get("api_retries", 0)) for row in rows),
        "slices": _slice_counts(rows),
    }


def paired_report(
    scalar_rows: list[dict[str, Any]],
    role_rows: list[dict[str, Any]],
    *,
    label: str,
    scalar_label: str = "Scalar lifecycle",
    role_label: str = "Role-indexed lifecycle",
) -> dict[str, Any]:
    scalar = by_id(scalar_rows)
    role = by_id(role_rows)
    if set(scalar) != set(role):
        missing_scalar = sorted(set(role) - set(scalar))
        missing_role = sorted(set(scalar) - set(role))
        raise ValueError(f"Mismatched task ids; missing scalar={missing_scalar}, missing role={missing_role}")
    ids = sorted(scalar)
    scalar_only = sum(
        bool(scalar[i]["result"].get("success")) and not bool(role[i]["result"].get("success"))
        for i in ids
    )
    role_only = sum(
        bool(role[i]["result"].get("success")) and not bool(scalar[i]["result"].get("success"))
        for i in ids
    )
    ci = cluster_delta_ci(scalar, role)
    return {
        "label": label,
        "controllers": [
            controller_summary(scalar, scalar_label),
            controller_summary(role, role_label),
        ],
        "paired": {
            "delta_percentage_points": 100.0 * (role_only - scalar_only) / len(ids),
            "cluster_ci95": list(ci),
            "scalar_only": scalar_only,
            "role_only": role_only,
            "mcnemar_exact_p": exact_mcnemar(scalar_only, role_only),
        },
    }


def _status(row: dict[str, Any], key: str) -> int:
    return int(row["action_status"].get(key, 0))


def _ratio(success: int, n: int) -> str:
    return f"{success}/{n}"


def markdown(value: dict[str, Any]) -> str:
    lines = [
        "# TRI-v6 Matched Scalar-vs-Role Addendum",
        "",
        "This post-freeze addendum compares the existing role-indexed controller against a matched",
        "scalar lifecycle controller with the same actor, action schema, preserve/invalidity gate,",
        "mutation boundary, and call policy. The remaining treatment difference is the compiler",
        "record: one scalar action-target record versus role-indexed action and monitoring records.",
        "",
    ]
    for section in value["sections"]:
        lines.extend([
            f"## {section['label']}",
            "",
            "| Controller | Target correct | Final state | Wrong writes | Invalid attempts | Unneeded reject | Requests | Errors |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in section["controllers"]:
            lines.append(
                f"| {row['label']} | {_ratio(row['success'], row['n'])} | "
                f"{_ratio(row['final_state_success'], row['n'])} | "
                f"{_status(row, 'wrong_entity_write')} | "
                f"{_status(row, 'invalid_target_attempt')} | "
                f"{_status(row, 'unnecessary_rejection')} | "
                f"{row['requests']} | {row['error_rows']} |"
            )
        paired = section["paired"]
        lines.extend([
            "",
            f"Role-indexed minus scalar: {paired['delta_percentage_points']:+.1f} points, "
            f"template-cluster 95% CI [{paired['cluster_ci95'][0]:+.1f}, "
            f"{paired['cluster_ci95'][1]:+.1f}].",
            f"Discordant pairs: {paired['role_only']} role-only and {paired['scalar_only']} scalar-only; "
            f"exact McNemar p={paired['mcnemar_exact_p']:.6g}.",
            "",
            "| Controller | Anchored | Dynamic | Explicit | Implicit |",
            "|---|---:|---:|---:|---:|",
        ])
        for row in section["controllers"]:
            binding = row["slices"]["binding"]
            explicit = [0, 0]
            implicit = [0, 0]
            for style, pair in row["slices"]["style"].items():
                target = explicit if style.startswith("explicit") else implicit
                target[0] += pair[0]
                target[1] += pair[1]
            lines.append(
                f"| {row['label']} | {_ratio(*binding['anchored'])} | "
                f"{_ratio(*binding['dynamic'])} | {_ratio(*explicit)} | {_ratio(*implicit)} |"
            )
        lines.append("")
    lines.extend([
        "The GLM ITT comparison includes transport-contaminated role-indexed rows from the original",
        "concurrent run. The transport-recovered comparison replaces only automatically selected",
        "failed rows with serial retries and is reported as an availability sensitivity analysis.",
    ])
    return "\n".join(lines) + "\n"


def build(args: argparse.Namespace) -> dict[str, Any]:
    sections = [
        paired_report(
            load(Path(args.qwen_scalar)),
            load(Path(args.qwen_role)),
            label="Qwen matched held-out",
        ),
        paired_report(
            load(Path(args.glm_scalar)),
            load(Path(args.glm_role_itt)),
            label="GLM matched held-out, conservative ITT",
        ),
        paired_report(
            load(Path(args.glm_scalar)),
            load(Path(args.glm_role_recovered)),
            label="GLM matched held-out, transport-recovered sensitivity",
        ),
    ]
    return {"sections": sections}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qwen-scalar", default="runs/v6_qwen_scalar_lifecycle_full.jsonl")
    parser.add_argument("--qwen-role", default="runs/v6_qwen_role_indexed_full.jsonl")
    parser.add_argument("--glm-scalar", default="runs/v6_glm_scalar_lifecycle_full.jsonl")
    parser.add_argument("--glm-role-itt", default="runs/v6_glm_role_indexed_full.jsonl")
    parser.add_argument("--glm-role-recovered", default="runs/v6_glm_role_indexed_transport_recovered.jsonl")
    parser.add_argument("--output-json", default="reports/v6_matched_scalar_role_report.json")
    parser.add_argument("--output-md", default="reports/v6_matched_scalar_role_report.md")
    args = parser.parse_args()
    value = build(args)
    Path(args.output_json).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(markdown(value), encoding="utf-8")
    print(args.output_json)
    print(args.output_md)


if __name__ == "__main__":
    main()
