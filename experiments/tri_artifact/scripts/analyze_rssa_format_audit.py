from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from tri.referential_ssa import parse_rssa_program
from tri.rssa_smoke import score_program_structure, strict_json_object


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/temporal_referent_method_upgrade_smoke_v1.jsonl"
DEFAULT_RUN = ROOT / "runs/rssa_smoke_glm_v1.jsonl"


def _load(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def unwrap_single_markdown_fence(text: str) -> tuple[str, bool]:
    stripped = text.strip()
    lines = stripped.splitlines()
    if len(lines) >= 3 and lines[0].strip() in {"```", "```json"} and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]), True
    return text, False


def audit(run_path: Path = DEFAULT_RUN) -> dict[str, Any]:
    tasks = {row["id"]: row for row in _load(MANIFEST)}
    rows = _load(run_path)
    if len(rows) != 20 or len({row["task_id"] for row in rows}) != 20:
        raise ValueError("format audit requires the complete 20-row GLM run")
    counts: Counter[str] = Counter()
    details: list[dict[str, Any]] = []
    for row in rows:
        task = tasks[row["task_id"]]
        raw = row["raw_compiler_output"]
        candidate, fenced = unwrap_single_markdown_fence(raw)
        counts["fenced_outputs"] += fenced
        detail: dict[str, Any] = {
            "task_id": row["task_id"],
            "smoke_index": row["smoke_index"],
            "fenced": fenced,
            "relaxed_schema_valid": False,
            "scores": None,
            "error": None,
        }
        try:
            program = parse_rssa_program(strict_json_object(candidate))
            scores = score_program_structure(task, program)
            detail["relaxed_schema_valid"] = True
            detail["scores"] = scores
            counts["relaxed_schema_valid"] += 1
            for name, value in scores.items():
                counts[name] += bool(value)
            all_correct = all(scores.values())
            counts["format_only_failures"] += all_correct
            counts["semantic_structure_failures"] += not all_correct
            if row["smoke_source"] == "v6_role_heldout":
                counts["composition_role_correct"] += scores["role_correct"]
        except Exception as exc:
            detail["error"] = str(exc)
            counts["still_invalid_after_unwrap"] += 1
        details.append(detail)
    return {
        "kind": "post_hoc_rssa_glm_markdown_fence_audit",
        "status": "post-hoc; does not replace prospective ITT",
        "run_file": str(run_path.resolve().relative_to(ROOT)),
        "tasks": len(rows),
        "counts": dict(sorted(counts.items())),
        "rows": details,
        "interpretation": (
            "Only one outer Markdown fence is removed. No field, value, task, prompt, or model "
            "response is repaired. Grounder and actor performance remain unmeasured for GLM."
        ),
    }


def markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    total = report["tasks"]
    return "\n".join([
        "# Post-Hoc GLM R-SSA Format Audit",
        "",
        "Status: **post-hoc; does not replace the prospective 0/20 strict-schema ITT result**.",
        "",
        "| Diagnostic | Count |",
        "|---|---:|",
        f"| Markdown-fenced outputs | {counts.get('fenced_outputs', 0)}/{total} |",
        f"| Valid after removing one outer fence | {counts.get('relaxed_schema_valid', 0)}/{total} |",
        f"| Correct refresh count | {counts.get('refresh_count_correct', 0)}/{total} |",
        f"| Correct action-binding epoch | {counts.get('action_binding_epoch_correct', 0)}/{total} |",
        f"| Correct producer edge | {counts.get('producer_edge_correct', 0)}/{total} |",
        f"| Correct binding inventory | {counts.get('binding_inventory_correct', 0)}/{total} |",
        f"| Correct composition roles | {counts.get('composition_role_correct', 0)}/4 |",
        f"| Format-only structural failures | {counts.get('format_only_failures', 0)}/{total} |",
        f"| Semantic structure failures after unwrap | {counts.get('semantic_structure_failures', 0)}/{total} |",
        "",
        "The audit removes only one outer Markdown fence. It does not repair generated IR. GLM",
        "grounding, Free execution, and Enforced execution were not called after strict parser",
        "failure and therefore remain unmeasured.",
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument(
        "--json-output", type=Path, default=ROOT / "reports/rssa_glm_format_audit_v1.json"
    )
    parser.add_argument(
        "--md-output", type=Path, default=ROOT / "reports/rssa_glm_format_audit_v1.md"
    )
    args = parser.parse_args()
    report = audit(args.run)
    args.json_output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.md_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({
        "json": str(args.json_output), "markdown": str(args.md_output),
        "counts": report["counts"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
