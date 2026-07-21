from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from tri.referential_ssa import parse_rssa_program
from tri.rssa_smoke import score_program_structure


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/temporal_referent_method_upgrade_smoke_v1.jsonl"
CTA_REPORT = ROOT / "reports/method_upgrade_closed_loop_v1.json"
EXPECTED_SHA256 = "e651f4db45275877ca09a5e70187baca6d5ee8901bf983bb1ecc3885ef879181"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _model_label(model: str) -> str:
    if "Qwen" in model:
        return "Qwen"
    if "GLM" in model:
        return "GLM"
    return model


def _usage(rows: list[dict[str, Any]]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for row in rows:
        for stage, records in row.get("usage", {}).items():
            for record in records:
                totals[f"{stage}_prompt_tokens"] += int(record.get("prompt_tokens", 0) or 0)
                totals[f"{stage}_completion_tokens"] += int(
                    record.get("completion_tokens", 0) or 0
                )
        for stage, count in row.get("request_attempts", {}).items():
            totals[f"{stage}_request_attempts"] += int(count)
    return dict(sorted(totals.items()))


def _source_error(task: dict[str, Any], target: str | None) -> bool:
    if task["pre_refresh_target"] == task["post_refresh_target"]:
        return False
    unauthorized_alternative = (
        task["post_refresh_target"]
        if task["binding"] == "anchored" else task["pre_refresh_target"]
    )
    return target == unauthorized_alternative and target != task["correct_target"]


def _cta_scores() -> dict[str, dict[str, int]]:
    report = json.loads(CTA_REPORT.read_text(encoding="utf-8"))
    totals: dict[str, Counter[str]] = {}
    for row in report["summary"]:
        if row["method"] != "Exact CTA" or row["source"] not in {"v6", "v7"}:
            continue
        model = row["model"]
        totals.setdefault(model, Counter())
        totals[model]["correct"] += row["correct"]
        totals[model]["n"] += row["n"]
    return {model: dict(values) for model, values in totals.items()}


def summarize(
    rows: list[dict[str, Any]], tasks: dict[str, dict[str, Any]], source: Path | None = None
) -> dict[str, Any]:
    if len(rows) != 20 or len({row["task_id"] for row in rows}) != 20:
        label = f"{source}: " if source is not None else ""
        raise ValueError(
            f"{label}expected 20 unique task rows; found {len(rows)} rows and "
            f"{len({row['task_id'] for row in rows})} unique task IDs"
        )
    if {row["task_id"] for row in rows} != set(tasks):
        raise ValueError("run task IDs do not match the frozen manifest")
    hashes = {row.get("dataset_sha256") for row in rows}
    if hashes != {EXPECTED_SHA256}:
        raise ValueError(f"run dataset hash mismatch: {hashes}")
    model_values = {row["model"] for row in rows}
    if len(model_values) != 1:
        raise ValueError("one input file must contain exactly one model")

    composition = [row for row in rows if row["smoke_source"] == "v6_role_heldout"]
    if len(composition) != 4:
        raise ValueError("run must contain four composition tasks")
    counts: Counter[str] = Counter()
    for row in rows:
        task = tasks[row["task_id"]]
        structural = {
            "refresh_count_correct": False,
            "action_binding_epoch_correct": False,
            "binding_inventory_correct": False,
            "producer_edge_correct": False,
            "role_correct": False,
        }
        if row["schema_valid"] and row.get("compiled_ir") is not None:
            structural = score_program_structure(
                task, parse_rssa_program(row["compiled_ir"])
            )
        counts["schema_valid"] += bool(row["schema_valid"])
        for field, value in structural.items():
            counts[field] += bool(value)
        for field in (
            "grounding_complete", "grounding_correct_for_program",
            "action_grounding_authorized_correct", "pipeline_complete",
            "actor_handle_disagreement",
        ):
            counts[field] += bool(row[field])
        counts["free_success"] += bool(row["pipeline_complete"] and row["free"]["success"])
        counts["enforced_success"] += bool(
            row["pipeline_complete"] and row["enforced"]["success"]
        )
        counts["free_wrong_writes"] += bool(row["free"]["wrong_write"])
        counts["enforced_wrong_writes"] += bool(row["enforced"]["wrong_write"])
        counts["free_false_blocks"] += bool(row["free"]["false_block"])
        counts["enforced_false_blocks"] += bool(row["enforced"]["false_block"])
        counts["free_source_errors"] += _source_error(task, row["free"]["target"])
        counts["enforced_source_errors"] += _source_error(task, row["enforced"]["target"])
        counts["tasks_with_errors"] += bool(row["errors"])
        counts["forbidden_field_errors"] += any(
            "forbidden request fields" in error for error in row["errors"]
        )
        if row["smoke_source"] == "v6_role_heldout":
            counts["composition_role_correct"] += bool(structural["role_correct"])
    return {
        "model": next(iter(model_values)),
        "label": _model_label(next(iter(model_values))),
        "n": len(rows),
        "composition_n": len(composition),
        "counts": dict(sorted(counts.items())),
        "usage": _usage(rows),
    }


def analyze(paths: list[Path]) -> dict[str, Any]:
    paths = [path.resolve() for path in paths]
    manifest_hash = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    if manifest_hash != EXPECTED_SHA256:
        raise ValueError(f"frozen manifest hash changed: {manifest_hash}")
    tasks = {task["id"]: task for task in _load_jsonl(MANIFEST)}
    groups = [summarize(_load_jsonl(path), tasks, path) for path in paths]
    if {group["label"] for group in groups} != {"Qwen", "GLM"}:
        raise ValueError("analysis requires one Qwen and one GLM run")
    cta = _cta_scores()
    by_label = {group["label"]: group for group in groups}
    gates: dict[str, bool] = {}
    for label, group in by_label.items():
        counts = group["counts"]
        gates[f"{label}_schema_at_least_19_of_20"] = counts["schema_valid"] >= 19
        gates[f"{label}_refresh_at_least_19_of_20"] = counts["refresh_count_correct"] >= 19
        gates[f"{label}_epoch_at_least_19_of_20"] = (
            counts["action_binding_epoch_correct"] >= 19
        )
        gates[f"{label}_edge_at_least_19_of_20"] = counts["producer_edge_correct"] >= 19
        gates[f"{label}_composition_roles_4_of_4"] = counts["composition_role_correct"] == 4
        gates[f"{label}_enforced_within_one_of_cta"] = (
            counts["enforced_success"] >= cta[label]["correct"] - 1
        )
        gates[f"{label}_no_forbidden_fields"] = counts["forbidden_field_errors"] == 0
        gates[f"{label}_not_more_false_blocks_than_free"] = (
            counts["enforced_false_blocks"] <= counts["free_false_blocks"]
        )

    source_deltas = {
        label: group["counts"]["free_source_errors"]
        - group["counts"]["enforced_source_errors"]
        for label, group in by_label.items()
    }
    cta_deltas = {
        label: group["counts"]["enforced_success"] - cta[label]["correct"]
        for label, group in by_label.items()
    }
    gates["source_errors_improve_one_and_do_not_worsen_other"] = (
        max(source_deltas.values()) > 0 and min(source_deltas.values()) >= 0
    )
    gates["no_cross_model_cta_direction_reversal"] = not (
        min(cta_deltas.values()) < 0 < max(cta_deltas.values())
    )
    gates["free_and_enforced_not_identical_both_models"] = any(
        group["counts"]["free_success"] != group["counts"]["enforced_success"]
        or group["counts"]["free_source_errors"] != group["counts"]["enforced_source_errors"]
        for group in groups
    )
    promote = all(gates.values())
    return {
        "kind": "rssa_20task_prospective_smoke",
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "manifest_sha256": manifest_hash,
        "run_files": [str(path.relative_to(ROOT)) for path in paths],
        "reused_exact_cta": cta,
        "groups": sorted(groups, key=lambda group: group["label"]),
        "source_error_reduction_enforced_vs_free": source_deltas,
        "enforced_minus_cta": cta_deltas,
        "gates": gates,
        "promote_to_expansion": promote,
        "decision": "GO" if promote else "NO-GO",
    }


def _ratio(value: int, total: int) -> str:
    return f"{value}/{total} ({100 * value / total:.1f}%)"


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# R-SSA Prospective 20-Task Smoke",
        "",
        f"Decision: **{report['decision']}**",
        "",
        "| Model | Schema | Epoch | Edge | Roles | Grounding | Free | Enforced | Free source errors | Enforced source errors | False blocks F/E |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group in report["groups"]:
        counts = group["counts"]
        lines.append(
            f"| {group['label']} | {_ratio(counts['schema_valid'], 20)} | "
            f"{_ratio(counts['action_binding_epoch_correct'], 20)} | "
            f"{_ratio(counts['producer_edge_correct'], 20)} | "
            f"{counts['composition_role_correct']}/4 | "
            f"{_ratio(counts['action_grounding_authorized_correct'], 20)} | "
            f"{_ratio(counts['free_success'], 20)} | "
            f"{_ratio(counts['enforced_success'], 20)} | "
            f"{counts['free_source_errors']} | {counts['enforced_source_errors']} | "
            f"{counts['free_false_blocks']}/{counts['enforced_false_blocks']} |"
        )
    lines.extend(["", "## Frozen gates", ""])
    lines.extend(
        f"- `{name}`: {value}" for name, value in sorted(report["gates"].items())
    )
    lines.extend([
        "",
        "Exact CTA is reused from the prior closed-loop report on the identical task IDs; it is",
        "not rerun. This smoke is post-primary method-feasibility evidence, not a powered final",
        "comparison. A GO permits expansion but does not automatically replace CTA in the paper.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs=2, type=Path)
    parser.add_argument(
        "--json-output", type=Path, default=ROOT / "reports/rssa_smoke_v1.json"
    )
    parser.add_argument(
        "--md-output", type=Path, default=ROOT / "reports/rssa_smoke_v1.md"
    )
    args = parser.parse_args()
    report = analyze(args.runs)
    args.json_output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.md_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({
        "decision": report["decision"],
        "promote_to_expansion": report["promote_to_expansion"],
        "json": str(args.json_output),
        "markdown": str(args.md_output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
