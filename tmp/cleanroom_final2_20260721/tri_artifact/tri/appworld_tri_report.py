from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    opportunities = [row for row in rows if row["initial_binding_correct"]]
    preserve_flip = [
        row
        for row in opportunities
        if row["reference_mode"] == "preserve" and row["transition"] == "flip"
    ]
    return {
        "rows": len(rows),
        "strict_successes": sum(row["success"] for row in rows),
        "authorized_target_writes": sum(row["target_correct"] for row in rows),
        "wrong_entity_writes": sum(row["wrong_entity_write"] for row in rows),
        "stable_errors": sum(row["stable_error"] for row in rows),
        "binding_opportunities": len(opportunities),
        "conditional_tri_errors": sum(row["wrong_entity_write"] for row in opportunities),
        "preserve_flip_opportunities": len(preserve_flip),
        "preserve_flip_unauthorized_rebindings": sum(
            row["unauthorized_rebinding"] for row in preserve_flip
        ),
        "binding_or_tool_order_failures": sum(
            not row["initial_binding_correct"] for row in rows
        ),
        "api_or_parse_error_rows": sum(bool(row["errors"]) for row in rows),
        "api_request_attempts": sum(row.get("api_request_attempts", 0) for row in rows),
    }


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    models = sorted({row["model"] for row in rows})
    by_model = {
        model: summarize_group([row for row in rows if row["model"] == model])
        for model in models
    }
    return {
        "study": "custom AppWorld Todoist TRI case study",
        "appworld_version": sorted({row["appworld_version"] for row in rows}),
        "base_appworld_task_ids": sorted({row["base_appworld_task_id"] for row in rows}),
        "models": by_model,
        "combined": summarize_group(rows),
        "cluster_count": len({row["cluster_id"] for row in rows}),
        "interpretation": (
            "No post-binding TRI or wrong-entity write was observed. The two Qwen strict "
            "failures are precondition/tool-order failures: it omitted record_binding before "
            "sync, then recovered and wrote the authorized old ID. This custom case study is "
            "not an AppWorld leaderboard or prevalence result."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AppWorld TRI Custom Case-Study Results",
        "",
        "## Scope",
        "",
        "This result uses AppWorld's Todoist database and native create/show/update APIs, but the",
        "eight TRI tasks, mid-trajectory synchronization, binding instrumentation, and evaluator",
        "are custom. It is not an AppWorld TGC/SGC or leaderboard result. All tasks share one",
        "selector cluster, so row-level confidence intervals are intentionally omitted.",
        "",
        "## Results",
        "",
        "| Model/controller | Rows | Strict success | Correct final write | Auditable binding | Conditional TRI | Wrong writes | Stable errors |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for model, values in report["models"].items():
        lines.append(
            f"| {model} / full-history | {values['rows']} | "
            f"{values['strict_successes']}/{values['rows']} | "
            f"{values['authorized_target_writes']}/{values['rows']} | "
            f"{values['binding_opportunities']}/{values['rows']} | "
            f"{values['conditional_tri_errors']}/{values['binding_opportunities']} | "
            f"{values['wrong_entity_writes']} | {values['stable_errors']} |"
        )
    combined = report["combined"]
    lines.extend(
        [
            f"| Combined | {combined['rows']} | {combined['strict_successes']}/{combined['rows']} | "
            f"{combined['authorized_target_writes']}/{combined['rows']} | "
            f"{combined['binding_opportunities']}/{combined['rows']} | "
            f"{combined['conditional_tri_errors']}/{combined['binding_opportunities']} | "
            f"{combined['wrong_entity_writes']} | {combined['stable_errors']} |",
            "",
            "The primary Preserve/Flip slice contains "
            f"{combined['preserve_flip_unauthorized_rebindings']}/"
            f"{combined['preserve_flip_opportunities']} unauthorized rebindings after a correct,"
            " correctly timed binding.",
            "",
            "## Error Attribution",
            "",
            "Qwen's two strict failures are not TRI failures. On one Preserve instruction template,",
            "it searched A but synchronized before calling the required sidecar binding tool. Its",
            "first write attempt was rejected; it then recorded A, retried, and modified A. Thus all",
            "16 trajectories ultimately wrote the authorized ID, while 14/16 satisfy the complete",
            "trajectory protocol. There are no API or parse-error rows.",
            "",
            "## Interpretation",
            "",
            "This is negative external evidence against a universal failure claim. It shows that the",
            "TRI distinction can be instantiated and deterministically audited in a richer public",
            "application database, but it does not independently demonstrate a positive TRI failure",
            "for ordinary full-history agents. The controlled TRI-v3/v7 experiments remain the positive",
            "mechanism diagnosis; this study narrows its external-validity boundary.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()
    report = build_report(load_rows(args.inputs))
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
