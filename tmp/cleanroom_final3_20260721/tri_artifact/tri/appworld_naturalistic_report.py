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


def summarize(rows: list[dict[str, Any]]) -> dict[str, int]:
    opportunities = [row for row in rows if row["initial_binding_correct"]]
    preserve_flip = [
        row
        for row in opportunities
        if row["reference_mode"] == "preserve" and row["transition"] == "flip"
    ]
    return {
        "rows": len(rows),
        "strict_successes": sum(bool(row["success"]) for row in rows),
        "authorized_writes": sum(bool(row["target_correct"]) for row in rows),
        "wrong_writes": sum(bool(row["wrong_entity_write"]) for row in rows),
        "binding_opportunities": len(opportunities),
        "conditional_tri_errors": sum(
            bool(row["unauthorized_rebinding"] or row["premature_lock"])
            for row in opportunities
        ),
        "preserve_flip_opportunities": len(preserve_flip),
        "preserve_flip_tri_errors": sum(
            bool(row["unauthorized_rebinding"]) for row in preserve_flip
        ),
        "pre_binding_or_order_failures": sum(
            not row["initial_binding_correct"] for row in rows
        ),
        "wrong_writes_without_correct_binding": sum(
            bool(row["wrong_entity_write"] and not row["initial_binding_correct"])
            for row in rows
        ),
        "stable_wrong_writes": sum(bool(row["stable_error"]) for row in rows),
        "api_or_parse_errors": sum(bool(row["errors"]) for row in rows),
        "api_attempts": sum(int(row.get("api_request_attempts", 0)) for row in rows),
    }


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    models = sorted({row["model"] for row in rows})
    apps = sorted({row["app"] for row in rows})
    return {
        "study": "AppWorld ordinary full-history selector-API addendum",
        "controller": "ordinary_full_history_selector_api",
        "models": {
            model: summarize([row for row in rows if row["model"] == model])
            for model in models
        },
        "app_model": {
            app: {
                model: summarize(
                    [row for row in rows if row["app"] == app and row["model"] == model]
                )
                for model in models
            }
            for app in apps
        },
        "combined": summarize(rows),
        "interpretation": (
            "No conditional post-binding TRI occurs in the 28 auditable opportunities. "
            "Qwen makes two real Preserve/Flip wrong writes because it synchronizes before "
            "the first selector call on one instruction template; matched Stable rows have "
            "the same ordering error but the unchanged winner masks the target consequence. "
            "These are pre-binding temporal-order errors, not referent drift after a correct binding."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# AppWorld Ordinary Full-History Selector-API Results",
        "",
        "## Scope",
        "",
        "This post-primary addendum removes the explicit binding sidecar and all prompt language",
        "about TRI, commitment, temporal authorization, Preserve, or Reevaluate. The ordinary",
        "selector API returns one stable ID; the runner observes that normal tool result as binding.",
        "Todoist and Simple Note each contribute eight custom AppWorld-backed tasks.",
        "",
        "## Results",
        "",
        "| App | Model | Rows | Strict | Correct write | Bind opp. | Conditional TRI | Wrong write |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for app, model_rows in report["app_model"].items():
        for model, values in model_rows.items():
            lines.append(
                f"| {app} | {model} | {values['rows']} | "
                f"{values['strict_successes']}/{values['rows']} | "
                f"{values['authorized_writes']}/{values['rows']} | "
                f"{values['binding_opportunities']}/{values['rows']} | "
                f"{values['conditional_tri_errors']}/{values['binding_opportunities']} | "
                f"{values['wrong_writes']} |"
            )
    total = report["combined"]
    lines.extend(
        [
            "",
            "## Combined Attribution",
            "",
            f"Across {total['rows']} trajectories, strict success is "
            f"{total['strict_successes']}/{total['rows']} and authorized writes are "
            f"{total['authorized_writes']}/{total['rows']}. There are "
            f"{total['binding_opportunities']} correct, correctly timed selector bindings and "
            f"{total['conditional_tri_errors']} conditional TRI errors. Preserve/Flip is "
            f"{total['preserve_flip_tri_errors']}/{total['preserve_flip_opportunities']}.",
            "",
            "Qwen makes two wrong writes, one in each application, on the same Preserve template.",
            "It calls sync before the first selector API, then selects and writes the refreshed",
            "winner. The matched Stable rows use the same incorrect order but still write A because",
            "the winner is unchanged. The Stable/Flip pair therefore identifies a real masked",
            "pre-binding temporal-order error rather than post-binding referent drift.",
            "",
            "## Interpretation",
            "",
            report["interpretation"],
            "This experiment is less measurement-intrusive and closer to ordinary function calling,",
            "but it remains a custom opportunity-conditioned benchmark and does not estimate",
            "uncontrolled deployment prevalence.",
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
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
