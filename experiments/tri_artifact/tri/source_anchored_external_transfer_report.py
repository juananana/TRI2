"""Report source-anchored external transfer model results."""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from typing import Any, Iterable


def latest_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        latest[(row["model"], row["controller"], row["task_id"])] = row
    return list(latest.values())


def _row_counts(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    selected = list(rows)
    return {
        "rows": len(selected),
        "valid": sum(row["status"] == "ok" for row in selected),
        "initial_binding_correct": sum(bool(row["initial_binding_correct"]) for row in selected),
        "exact_target_success": sum(bool(row["exact_target_success"]) for row in selected),
        "write_executed": sum(bool(row["write_executed"]) for row in selected),
        "wrong_entity_write": sum(bool(row["wrong_entity_write"]) for row in selected),
        "transport_failure": sum(
            bool(row["first_transport_error"] or row["second_transport_error"])
            for row in selected
        ),
        "parse_or_schema_failure": sum(
            bool(row["first_parse_error"] or row["second_parse_error"])
            for row in selected
        ),
        "source_execution_failure": sum(bool(row["source_execution_error"]) for row in selected),
        "missing_or_rejected_write": sum(
            row.get("predicted_target_id") is None
            and not (row["first_transport_error"] or row["second_transport_error"])
            for row in selected
        ),
        "request_attempts": sum(int(row.get("request_attempts", 0)) for row in selected),
    }


def _grouped(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> dict[str, dict[str, int]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(str(row[field]) for field in fields)].append(row)
    return {
        " | ".join(key): _row_counts(group)
        for key, group in sorted(grouped.items())
    }


def _changed_metrics(rows: list[dict[str, Any]]) -> dict[str, int]:
    changed = [row for row in rows if row["transition"] == "changed"]
    conditional = [
        row
        for row in changed
        if row["initial_binding_correct"]
        and row.get("old_target_present_after_refresh", True)
        and row.get("old_target_action_valid_after_refresh", True)
    ]
    preserve = [row for row in conditional if row["timing"] == "preserve"]
    reevaluate = [row for row in conditional if row["timing"] == "reevaluate"]
    return {
        "changed_rows_itt": len(changed),
        "changed_exact_target_itt": sum(bool(row["exact_target_success"]) for row in changed),
        "conditional_rows": len(conditional),
        "conditional_exact_target": sum(bool(row["exact_target_success"]) for row in conditional),
        "preserve_changed_rows": len(preserve),
        "preserve_unauthorized_substitutions": sum(
            row.get("predicted_target_id") == row.get("refreshed_winner_id")
            and row.get("refreshed_winner_id") != row.get("initial_winner_id")
            for row in preserve
        ),
        "reevaluate_changed_rows": len(reevaluate),
        "reevaluate_failed_substitutions": sum(
            row.get("predicted_target_id") == row.get("initial_winner_id")
            and row.get("refreshed_winner_id") != row.get("initial_winner_id")
            for row in reevaluate
        ),
    }


def _conditional_cells(rows: list[dict[str, Any]]) -> dict[str, int]:
    eligible = [
        row
        for row in rows
        if row["initial_binding_correct"]
        and row.get("old_target_present_after_refresh", True)
        and row.get("old_target_action_valid_after_refresh", True)
    ]
    output: dict[str, int] = {}
    for timing in ("preserve", "reevaluate"):
        for transition in ("stable", "changed"):
            cell = [
                row
                for row in eligible
                if row["timing"] == timing and row["transition"] == transition
            ]
            prefix = f"{timing}_{transition}"
            output[f"{prefix}_rows"] = len(cell)
            output[f"{prefix}_exact"] = sum(bool(row["exact_target_success"]) for row in cell)
    preserve_changed = [
        row
        for row in eligible
        if row["timing"] == "preserve" and row["transition"] == "changed"
    ]
    reevaluate_changed = [
        row
        for row in eligible
        if row["timing"] == "reevaluate" and row["transition"] == "changed"
    ]
    output["preserve_changed_to_refreshed_winner"] = sum(
        row.get("predicted_target_id") == row.get("refreshed_winner_id")
        and row.get("refreshed_winner_id") != row.get("initial_winner_id")
        for row in preserve_changed
    )
    output["reevaluate_changed_kept_initial_winner"] = sum(
        row.get("predicted_target_id") == row.get("initial_winner_id")
        and row.get("refreshed_winner_id") != row.get("initial_winner_id")
        for row in reevaluate_changed
    )
    return output


def _grouped_conditional_cells(
    rows: list[dict[str, Any]], fields: tuple[str, ...]
) -> dict[str, dict[str, int]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(str(row[field]) for field in fields)].append(row)
    return {
        " | ".join(key): _conditional_cells(group)
        for key, group in sorted(grouped.items())
    }


def _changed_pairs(rows: list[dict[str, Any]]) -> dict[str, int]:
    indexed = {
        (row["model"], row["controller"], row["cluster_id"], row["timing"]): row
        for row in rows
        if row["transition"] == "changed"
    }
    bases = {
        (model, controller, cluster)
        for model, controller, cluster, _timing in indexed
    }
    pairs = []
    for base in sorted(bases):
        preserve = indexed.get((*base, "preserve"))
        reevaluate = indexed.get((*base, "reevaluate"))
        if preserve is not None and reevaluate is not None:
            pairs.append((preserve, reevaluate))
    conditional = [
        pair for pair in pairs if pair[0]["initial_binding_correct"] and pair[1]["initial_binding_correct"]
    ]
    return {
        "pairs": len(pairs),
        "both_exact": sum(a["exact_target_success"] and b["exact_target_success"] for a, b in pairs),
        "conditional_pairs": len(conditional),
        "conditional_both_exact": sum(
            a["exact_target_success"] and b["exact_target_success"] for a, b in conditional
        ),
    }


def _shared_eligible(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    by_key: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_key[(row["model"], row["task_id"])][row["controller"]] = row
    output: dict[str, Counter[str]] = defaultdict(Counter)
    for (model, _task_id), controllers in by_key.items():
        ordinary = controllers.get("ordinary_full_history")
        record = controllers.get("execution_record")
        if not ordinary or not record:
            continue
        if not (ordinary["initial_binding_correct"] and record["initial_binding_correct"]):
            continue
        counter = output[model]
        counter["rows"] += 1
        counter["ordinary_exact"] += int(ordinary["exact_target_success"])
        counter["execution_record_exact"] += int(record["exact_target_success"])
        counter["record_better"] += int(
            record["exact_target_success"] and not ordinary["exact_target_success"]
        )
        counter["ordinary_better"] += int(
            ordinary["exact_target_success"] and not record["exact_target_success"]
        )
    return {model: dict(counts) for model, counts in sorted(output.items())}


def _percentile(values: list[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * probability)
    return ordered[index]


def _cluster_bootstrap(rows: list[dict[str, Any]], samples: int = 10_000) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for model in sorted({row["model"] for row in rows}):
        model_rows = [row for row in rows if row["model"] == model]
        clusters = sorted({row["cluster_id"] for row in model_rows})
        effects: dict[str, float] = {}
        for cluster in clusters:
            cluster_rows = [row for row in model_rows if row["cluster_id"] == cluster]
            ordinary = [row["exact_target_success"] for row in cluster_rows if row["controller"] == "ordinary_full_history"]
            record = [row["exact_target_success"] for row in cluster_rows if row["controller"] == "execution_record"]
            if ordinary and record:
                effects[cluster] = sum(record) / len(record) - sum(ordinary) / len(ordinary)
        if not effects:
            continue
        rng = random.Random(20270724)
        names = sorted(effects)
        draws = [
            sum(effects[rng.choice(names)] for _ in names) / len(names)
            for _sample in range(samples)
        ]
        estimate = sum(effects.values()) / len(effects)
        output[model] = {
            "estimand": "execution_record minus ordinary exact-target accuracy",
            "clusters": len(effects),
            "estimate_percentage_points": round(100 * estimate, 3),
            "cluster_bootstrap_95_ci_percentage_points": [
                round(100 * _percentile(draws, 0.025), 3),
                round(100 * _percentile(draws, 0.975), 3),
            ],
            "samples": samples,
            "seed": 20270724,
        }
    return output


def build_report(rows: list[dict[str, Any]], expected_rows: int, smoke: bool) -> dict[str, Any]:
    latest = latest_rows(rows)
    valid = [row for row in latest if row["status"] == "ok"]
    coverage = {
        (row["model"], row["controller"], row["repository"])
        for row in valid
    }
    expected_coverage = {
        (row["model"], row["controller"], repository)
        for row in latest
        for repository in ("STATE-Bench", "AgentDojo")
    }
    valid_rate = len(valid) / len(latest) if latest else 0.0
    smoke_gate = (
        len(latest) == expected_rows
        and valid_rate >= 0.9
        and expected_coverage.issubset(coverage)
    )
    totals = _row_counts(latest)
    repaired_rows = sum("repair_version" in row for row in latest)
    return {
        "mode": "smoke" if smoke else "full",
        "evidence_label": "source-anchored external transfer",
        "expected_rows": expected_rows,
        "raw_serialized_rows": len(rows),
        "unique_rows": len(latest),
        "execution_repair_rows": repaired_rows,
        "model_requests_added_by_repairs": sum(
            int(row.get("model_requests_added_by_repair", 0)) for row in latest
        ),
        "valid_rows": len(valid),
        "valid_rate": valid_rate,
        "smoke_gate": "GO" if smoke_gate else "NO-GO" if smoke else "not_applicable",
        "totals": totals,
        "groups": _grouped(latest, ("model", "controller")),
        "by_repository": _grouped(latest, ("repository", "model", "controller")),
        "by_domain": _grouped(latest, ("domain", "model", "controller")),
        "changed_condition": _changed_metrics(latest),
        "changed_by_repository": {
            key: _changed_metrics(
                [row for row in latest if row["repository"] == key]
            )
            for key in sorted({row["repository"] for row in latest})
        },
        "changed_by_model_controller": {
            key: _changed_metrics(
                [
                    row
                    for row in latest
                    if f"{row['model']} | {row['controller']}" == key
                ]
            )
            for key in sorted(
                {f"{row['model']} | {row['controller']}" for row in latest}
            )
        },
        "conditional_cells_by_repository_model_controller": _grouped_conditional_cells(
            latest, ("repository", "model", "controller")
        ),
        "changed_pairs": _changed_pairs(latest),
        "shared_initial_binding_comparison": _shared_eligible(latest),
        "controller_effect_cluster_bootstrap": _cluster_bootstrap(latest),
        "transport_failures": totals["transport_failure"],
        "parse_or_schema_failures": totals["parse_or_schema_failure"],
        "source_execution_failures": totals["source_execution_failure"],
        "claim_boundary": (
            "Author-adapted matched evaluation on external source states and tools; not native "
            "benchmark prevalence, natural traffic, or an official benchmark score."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    changed = report["changed_condition"]
    pairs = report["changed_pairs"]
    lines = [
        f"# Source-Anchored External Transfer {report['mode'].title()} Report",
        "",
        f"- Rows: {report['unique_rows']}/{report['expected_rows']}",
        f"- Valid: {report['valid_rows']} ({report['valid_rate']:.1%})",
        f"- Smoke gate: {report['smoke_gate']}",
        f"- Exact target (ITT): {report['totals']['exact_target_success']}/{report['unique_rows']}",
        f"- Initial selection: {report['totals']['initial_binding_correct']}/{report['unique_rows']}",
        f"- Wrong-entity writes: {report['totals']['wrong_entity_write']}",
        f"- Transport / parse-schema / source-execution failures: "
        f"{report['transport_failures']} / {report['parse_or_schema_failures']} / "
        f"{report['source_execution_failures']}",
        f"- Offline execution repairs: {report['execution_repair_rows']} rows, "
        f"{report['model_requests_added_by_repairs']} added model requests",
        "",
        "## Changed Conditions",
        "",
        f"- Conditional exact target: {changed['conditional_exact_target']}/{changed['conditional_rows']}",
        f"- Preserve unauthorized substitutions: "
        f"{changed['preserve_unauthorized_substitutions']}/{changed['preserve_changed_rows']}",
        f"- Reevaluate failed substitutions: "
        f"{changed['reevaluate_failed_substitutions']}/{changed['reevaluate_changed_rows']}",
        f"- Changed matched pairs both exact: {pairs['both_exact']}/{pairs['pairs']} "
        f"(conditional {pairs['conditional_both_exact']}/{pairs['conditional_pairs']})",
        "",
        "## Model Conditions",
        "",
        "| Model and condition | Rows | Valid | Initial selection | Exact target | Wrong write |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key, values in report["groups"].items():
        lines.append(
            f"| {key} | {values['rows']} | {values['valid']} | "
            f"{values['initial_binding_correct']} | {values['exact_target_success']} | "
            f"{values['wrong_entity_write']} |"
        )
    lines.extend(["", "## Shared Initial Selection", ""])
    for model, values in report["shared_initial_binding_comparison"].items():
        lines.append(
            f"- {model}: ordinary {values.get('ordinary_exact', 0)}/{values['rows']}; "
            f"execution record {values.get('execution_record_exact', 0)}/{values['rows']}; "
            f"record-better {values.get('record_better', 0)}, "
            f"ordinary-better {values.get('ordinary_better', 0)}."
        )
    lines.extend(["", "## Boundary", "", report["claim_boundary"], ""])
    return "\n".join(lines)


def _fraction(values: dict[str, int], numerator: str, denominator: str) -> str:
    return f"{values[numerator]}/{values[denominator]}"


def render_latex_table(report: dict[str, Any]) -> str:
    model_labels = {
        "Qwen/Qwen3.5-122B-A10B": "Qwen",
        "Pro/zai-org/GLM-5.1": "GLM",
    }
    controller_labels = {
        "ordinary_full_history": "History",
        "execution_record": "Record",
    }
    rows = [
        "% Generated by scripts/report_source_anchored_external_transfer.py.",
        "\\begin{table*}[t]",
        "\\centering",
        "\\small",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{lllrrrrrrrr}",
        "\\toprule",
        "Source & Model & Condition & Exact ITT & Initial & P/S & P/C & R/S & R/C & P/C$\\to$new & R/C$\\to$old \\\\",
        "\\midrule",
    ]
    cells = report["conditional_cells_by_repository_model_controller"]
    totals = report["by_repository"]
    last_source = None
    for key, values in cells.items():
        source, model, controller = key.split(" | ")
        if last_source is not None and source != last_source:
            rows.append("\\midrule")
        total = totals[key]
        rows.append(
            " & ".join(
                [
                    source,
                    model_labels.get(model, model),
                    controller_labels.get(controller, controller),
                    f"{total['exact_target_success']}/{total['rows']}",
                    f"{total['initial_binding_correct']}/{total['rows']}",
                    _fraction(values, "preserve_stable_exact", "preserve_stable_rows"),
                    _fraction(values, "preserve_changed_exact", "preserve_changed_rows"),
                    _fraction(values, "reevaluate_stable_exact", "reevaluate_stable_rows"),
                    _fraction(values, "reevaluate_changed_exact", "reevaluate_changed_rows"),
                    f"{values['preserve_changed_to_refreshed_winner']}/{values['preserve_changed_rows']}",
                    f"{values['reevaluate_changed_kept_initial_winner']}/{values['reevaluate_changed_rows']}",
                ]
            )
            + " \\\\"
        )
        last_source = source
    rows.extend(
        [
            "\\bottomrule",
            "\\end{tabular}%",
            "}",
            "\\caption{Frozen source-anchored external transfer. P/R denote Preserve/Reevaluate; "
            "S/C denote Stable/Changed. Four cell columns condition on a correct observable initial "
            "selection and a surviving action-valid old target. The final columns isolate substitution "
            "to the refreshed winner in Preserve/Changed and retention of the initial winner in "
            "Reevaluate/Changed. ITT retains parse and missing-write failures.}",
            "\\label{tab:supp-source-anchored-transfer}",
            "\\end{table*}",
            "",
        ]
    )
    return "\n".join(rows)
