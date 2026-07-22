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


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    opportunities = [row for row in rows if row["initial_binding_correct"]]
    preserve_flip = [
        row
        for row in opportunities
        if row["reference_mode"] == "preserve" and row["transition"] == "flip"
    ]
    wrong_without_opportunity = [
        row for row in rows if row["wrong_entity_write"] and not row["initial_binding_correct"]
    ]
    return {
        "rows": len(rows),
        "strict_successes": sum(bool(row["success"]) for row in rows),
        "authorized_target_writes": sum(bool(row["target_correct"]) for row in rows),
        "wrong_entity_writes": sum(bool(row["wrong_entity_write"]) for row in rows),
        "stable_errors": sum(bool(row["stable_error"]) for row in rows),
        "binding_opportunities": len(opportunities),
        "conditional_tri_errors": sum(
            bool(row["wrong_entity_write"]) for row in opportunities
        ),
        "preserve_flip_opportunities": len(preserve_flip),
        "preserve_flip_unauthorized_rebindings": sum(
            bool(row["unauthorized_rebinding"]) for row in preserve_flip
        ),
        "binding_or_tool_order_failures": sum(
            not row["initial_binding_correct"] for row in rows
        ),
        "wrong_writes_without_prior_auditable_binding": len(wrong_without_opportunity),
        "api_or_parse_error_rows": sum(bool(row["errors"]) for row in rows),
        "api_request_attempts": sum(row.get("api_request_attempts", 0) for row in rows),
    }


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    models = sorted({row["model"] for row in rows})
    clusters = sorted({row["cluster_id"] for row in rows})
    by_model = {
        model: summarize([row for row in rows if row["model"] == model])
        for model in models
    }
    by_cluster_model = {
        cluster: {
            model: summarize(
                [
                    row
                    for row in rows
                    if row["cluster_id"] == cluster and row["model"] == model
                ]
            )
            for model in models
        }
        for cluster in clusters
    }
    return {
        "study": "custom AppWorld two-application TRI boundary case study",
        "appworld_version": sorted({row["appworld_version"] for row in rows}),
        "base_appworld_task_ids": sorted({row["base_appworld_task_id"] for row in rows}),
        "models": by_model,
        "cluster_model_results": by_cluster_model,
        "combined": summarize(rows),
        "cluster_count": len(clusters),
        "clusters": clusters,
        "interpretation": (
            "No post-binding TRI was observed after a correct, correctly timed binding. "
            "One Qwen Simple Note trajectory made a real wrong-entity write, but it refreshed "
            "and rebound before the sidecar recorded an initial commitment, so it is a delayed-"
            "binding/tool-order error outside the conditional TRI denominator. The study is a "
            "custom AppWorld-backed boundary case study, not a leaderboard or prevalence result."
        ),
    }


def _fraction(values: dict[str, Any], numerator: str, denominator: str = "rows") -> str:
    return f"{values[numerator]}/{values[denominator]}"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AppWorld TRI Two-Application Boundary Results",
        "",
        "## Scope",
        "",
        "The custom case study uses AppWorld 0.1.3.post1 databases and native APIs for two",
        "independent selector clusters: Todoist earliest-due tasks and Simple Note alphabetical",
        "titles. Each cluster crosses Preserve/Reevaluate, Stable/Flip, and two paraphrases.",
        "The 16 task definitions, synchronization operators, sidecar binding instrument, and",
        "evaluators are custom. These are not AppWorld leaderboard results. The Simple Note",
        "cluster was added after the Todoist result and is reported as a post-primary extension.",
        "",
        "## Results by Application and Model",
        "",
        "| Cluster | Model/controller | Rows | Strict success | Correct write | Auditable binding | Conditional TRI | Wrong writes |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for cluster, model_results in report["cluster_model_results"].items():
        for model, values in model_results.items():
            lines.append(
                f"| {cluster} | {model} / full-history | {values['rows']} | "
                f"{_fraction(values, 'strict_successes')} | "
                f"{_fraction(values, 'authorized_target_writes')} | "
                f"{_fraction(values, 'binding_opportunities')} | "
                f"{_fraction(values, 'conditional_tri_errors', 'binding_opportunities')} | "
                f"{values['wrong_entity_writes']} |"
            )
    combined = report["combined"]
    lines.extend(
        [
            "",
            "## Combined Boundary",
            "",
            f"Across {report['cluster_count']} clusters and {combined['rows']} trajectories, strict",
            f"success is {combined['strict_successes']}/{combined['rows']} and authorized-target",
            f"writes are {combined['authorized_target_writes']}/{combined['rows']}. A correct,",
            f"correctly timed initial binding is observable in {combined['binding_opportunities']}",
            f"trajectories; conditional TRI is {combined['conditional_tri_errors']}/"
            f"{combined['binding_opportunities']}. The Preserve/Flip slice contains",
            f"{combined['preserve_flip_unauthorized_rebindings']}/"
            f"{combined['preserve_flip_opportunities']} unauthorized rebindings after such a binding.",
            "",
            "There is one real wrong-entity database write. Qwen searches the correct Simple Note A,",
            "synchronizes without recording a commitment, searches again, binds new winner B, and",
            "writes B. The matched Stable trajectory has the same delayed-binding order but writes A",
            "because the winner does not change. This is a selector-sensitive tool-order failure, not",
            "post-binding drift, and is excluded from the conditional TRI numerator by the frozen rule.",
            "",
            "## Interpretation",
            "",
            report["interpretation"],
            "The sidecar is scientifically useful because it prevents final-target errors from being",
            "misclassified as TRI, but its omission in 8/32 trajectories also shows that explicit",
            "binding instrumentation changes the autonomous workflow. The external result therefore",
            "bounds universality; the controlled benchmark remains the positive mechanism diagnosis.",
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
    args.json.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    args.markdown.write_text(render_markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
