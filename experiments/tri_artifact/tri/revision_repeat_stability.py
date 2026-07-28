from __future__ import annotations

from collections import defaultdict
from typing import Any

from tri.revision_matched_audit import CONDITIONS, build_report, exact_target


REPORT_VERSION = "TRI-revision-repeat-stability-report-v1"


def _targets(rows: list[dict[str, Any]], condition: str) -> dict[str, str | None]:
    return {
        row["task"]["id"]: exact_target(row.get("outcomes", {}).get(condition)) for row in rows
    }


def exact_target_agreement(
    historical: list[dict[str, Any]], repeat: list[dict[str, Any]], condition: str
) -> dict[str, Any]:
    left, right = _targets(historical, condition), _targets(repeat, condition)
    common = sorted(set(left) & set(right))
    count = sum(left[task_id] == right[task_id] for task_id in common)
    return {
        "numerator": count,
        "denominator": len(common),
        "rate": count / len(common) if common else None,
    }


def _one_pass(rows: list[dict[str, Any]], label: str, samples: int) -> dict[str, Any]:
    report = build_report(rows, samples=samples)
    if report["audit_id"] != "source_grounded" or len(report["models"]) != 1:
        raise ValueError("each repeat input must be one source_grounded model pass")
    model = report["models"][0]
    if model["rows"] != 60:
        raise ValueError(f"source-grounded pass must contain 60 rows, found {model['rows']}")
    return {
        "label": label,
        "model": model["model"],
        "rows": model["rows"],
        "clusters": model["clusters"],
        "metrics": model["metrics"],
        "decision_visible_minus_history": model["decision_visible_minus_history"],
        "failures": model["failures"],
        "logical_calls": model["logical_calls"],
    }


def build_repeat_report(
    historical_passes: list[tuple[str, list[dict[str, Any]]]],
    new_passes: list[tuple[str, list[dict[str, Any]]]],
    samples: int = 10_000,
) -> dict[str, Any]:
    historical_by_model: dict[str, tuple[str, list[dict[str, Any]]]] = {}
    passes: list[dict[str, Any]] = []
    for label, rows in historical_passes:
        one = _one_pass(rows, label, samples)
        if one["model"] in historical_by_model:
            raise ValueError("duplicate historical pass for one model")
        historical_by_model[one["model"]] = (label, rows)
        passes.append(one)
    agreements: list[dict[str, Any]] = []
    for label, rows in new_passes:
        one = _one_pass(rows, label, samples)
        passes.append(one)
        if one["model"] in historical_by_model:
            historical_label, historical_rows = historical_by_model[one["model"]]
            agreements.append(
                {
                    "model": one["model"],
                    "historical_label": historical_label,
                    "new_label": label,
                    "conditions": {
                        condition: exact_target_agreement(historical_rows, rows, condition)
                        for condition in CONDITIONS
                    },
                }
            )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in passes:
        grouped[item["model"]].append(item)
    return {
        "report_version": REPORT_VERSION,
        "evidence_status": "post-primary replication/audit",
        "audit_id": "source_grounded",
        "passes": passes,
        "target_agreement": agreements,
        "models": sorted(grouped),
        "boundary": (
            "Temperature-zero repeats measure endpoint repeatability on the same 30 source-derived "
            "pairs. They do not increase the independent pair count or establish native behavior."
        ),
    }


def _fraction(metric: dict[str, Any]) -> str:
    return f"{metric['numerator']}/{metric['denominator']}"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Source-Derived Matched-Call Repeat Stability",
        "",
        "Evidence status: **post-primary replication/audit**.",
        "",
        report["boundary"],
        "",
        "| Model | Pass | History PairAcc | Visible PairAcc | Effect | History E2E | Visible E2E | Incomplete |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["passes"]:
        history = item["metrics"]["history_only"]
        visible = item["metrics"]["decision_visible"]
        effect = item["decision_visible_minus_history"]["changed_pairacc"]["difference"]
        effect_text = "NA" if effect is None else f"{100 * effect:.1f} pp"
        lines.append(
            f"| {item['model']} | {item['label']} | {_fraction(history['changed_pairacc'])} | "
            f"{_fraction(visible['changed_pairacc'])} | {effect_text} | "
            f"{_fraction(history['actionable_e2e'])} | {_fraction(visible['actionable_e2e'])} | "
            f"{item['failures']['incomplete_tasks']} |"
        )
    lines.extend(["", "## Exact-target agreement with the historical pass", ""])
    if not report["target_agreement"]:
        lines.append("No model has both a historical and new pass.")
    for item in report["target_agreement"]:
        values = ", ".join(
            f"{condition} {_fraction(metric)}"
            for condition, metric in item["conditions"].items()
        )
        lines.append(f"- {item['model']}: {values}.")
    lines.append("")
    return "\n".join(lines)

