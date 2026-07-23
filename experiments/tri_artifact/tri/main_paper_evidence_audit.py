"""Rebuild and cross-check the manuscript's critical evidence chain."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .identifiability_regimes import load_jsonl, summarize
from .v7_leave_group_out import RUNS
from .v7_shared_eligible_pairacc import shared_eligible


ROOT = Path(__file__).resolve().parents[1]


def default_paper_path(root: Path = ROOT) -> Path:
    """Locate the manuscript in either the archive or development layout."""
    archive_path = root / "paper" / "AnonymousSubmission2027.tex"
    repository_path = root.parents[1] / "paper" / "AnonymousSubmission2027.tex"
    return archive_path if archive_path.is_file() else repository_path


PAPER = default_paper_path()

EXTERNAL_EXTENSION_REPORTS = (
    "toolsandbox_single_turn_qwen_full_history_full_v1.json",
    "toolsandbox_single_turn_glm_full_history_full_v1.json",
    "toolsandbox_single_turn_matched_generic_qwen_full_v1.json",
    "toolsandbox_single_turn_matched_generic_glm_full_v1.json",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_audit_rows(root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    reports = [
        load_json(root / "reports/v7_write_audit.json"),
        load_json(root / "reports/v7_deepseek_write_audit_v1.json"),
    ]
    rows = {}
    for report in reports:
        for row in report["summary"]:
            rows[(row["model"], row["controller"])] = row
    return rows


def v7_rows(root: Path, paper_text: str) -> list[dict[str, Any]]:
    writes = write_audit_rows(root)
    output = []
    for model, (generic_name, cta_name) in RUNS.items():
        generic_rows = load_jsonl(root / "runs" / generic_name)
        cta_rows = load_jsonl(root / "runs" / cta_name)
        shared = shared_eligible(generic_rows, cta_rows)
        for label, rows, write_controller in (
            ("Generic", generic_rows, "generic_structured_ledger_then_act"),
            ("CTA", cta_rows, "compile_then_act"),
        ):
            summary = summarize(rows)
            pair = summary["changed_pairacc"]
            conditional = summary["conditional_changed_winner"]
            write = writes[(model, write_controller)]
            paper_model = {"Qwen3.5": "Qwen", "GLM-5.1": "GLM"}.get(model, model)
            paper_controller = label
            latex_row = (
                f"{paper_model} / {paper_controller} & {pair['both_correct']}/{pair['pairs']} & "
                f"{conditional['drift_to_refreshed_winner']}/{conditional['eligible']} & "
                f"{write['core_tri_writes']}/{write['all_wrong_writes']} \\\\"
            )
            output.append(
                {
                    "model": model,
                    "controller": label,
                    "pairacc": [pair["both_correct"], pair["pairs"]],
                    "conditional_substitution": [
                        conditional["drift_to_refreshed_winner"],
                        conditional["eligible"],
                    ],
                    "core_substitution_writes": write["core_tri_writes"],
                    "all_wrong_writes": write["all_wrong_writes"],
                    "shared_eligible": shared["eligible"],
                    "shared_generic_substitutions": shared["generic_substitutions"],
                    "shared_cta_substitutions": shared["cta_substitutions"],
                    "latex_row": latex_row,
                    "latex_row_present": latex_row in paper_text,
                }
            )
    return output


def primary_summary(root: Path) -> dict[str, Any]:
    output = {}
    for model, name in (
        ("Qwen3.5", "v3_qwen_language_cluster.json"),
        ("GLM-5.1", "v3_glm_language_cluster.json"),
    ):
        report = load_json(root / "reports" / name)
        generic = next(row for row in report["runs"] if row["mode"] == "generic_structured_ledger_then_act")
        gated = next(row for row in report["runs"] if row["mode"] == "factorized_hybrid_compile_then_act")
        pair = report["pairs"][0]
        output[model] = {
            "generic_accuracy": generic["task_accuracy"],
            "gated_accuracy": gated["task_accuracy"],
            "delta": pair["delta_b_minus_a"],
            "cluster_bootstrap_ci95": [
                pair["cluster_bootstrap_ci95_low"],
                pair["cluster_bootstrap_ci95_high"],
            ],
        }
    return output


def external_extension_summary(root: Path) -> list[dict[str, Any]]:
    output = []
    for name in EXTERNAL_EXTENSION_REPORTS:
        report = load_json(root / "reports" / name)
        output.append(
            {
                "report": name,
                "rows": report["inventory"]["rows"],
                "opportunities": sum(cell["tri_opportunities"] for cell in report["cells"]),
                "mechanism_errors": sum(
                    cell["unauthorized_rebindings"] + cell["premature_locks"]
                    for cell in report["cells"]
                ),
                "wrong_writes": sum(cell["wrong_entity_writes"] for cell in report["cells"]),
            }
        )
    return output


def build_report(root: Path = ROOT, paper_path: Path = PAPER) -> dict[str, Any]:
    paper_text = paper_path.read_text(encoding="utf-8")
    rows = v7_rows(root, paper_text)
    primary = primary_summary(root)
    human = load_json(root / "human_validation/analysis.json")["groups"]
    coverage = load_json(root / "reports/public_suite_coverage_funnel_v1.json")
    external_extension = external_extension_summary(root)
    selection_regret = load_json(root / "reports/evaluation_selection_regret_v1.json")
    selection_summary = selection_regret["summary"]

    checks = {
        "all_table2_rows_match_frozen_sources": (
            "Core/all writes" in paper_text
            and all(row["latex_row_present"] for row in rows)
        ),
        "shared_qwen_claim_present": "41/66 versus 0/66" in paper_text,
        "shared_glm_claim_present": "30/70 versus 0/70" in paper_text,
        "shared_deepseek_claim_present": "50/69 versus\n0/69" in paper_text,
        "qwen_primary_claim_present": all(
            token in paper_text for token in ("157/160", "103/160", "98.1\\% vs. 64.4\\%")
        ),
        "glm_primary_claim_present": all(
            token in paper_text for token in ("160/160", "115/160", "100.0\\% vs. 71.9\\%")
        ),
        "human_agreement_claim_present": (
            "Fleiss' $\\kappa=.708$" in paper_text
            and "Krippendorff's $\\alpha=.709$" in paper_text
        ),
        "coverage_scope_present": (
            "ToolSandbox (129 families)" in paper_text
            and "AppWorld (244 families)" in paper_text
            and "$\\tau^3$ (2,449 tasks" in paper_text
        ),
        "external_extension_four_condition_scope_matches_sources": (
            len(external_extension) == 4
            and [row["rows"] for row in external_extension] == [96, 96, 96, 96]
            and [row["opportunities"] for row in external_extension] == [70, 73, 64, 87]
            and [row["mechanism_errors"] for row in external_extension] == [0, 0, 0, 0]
            and [row["wrong_writes"] for row in external_extension] == [6, 13, 5, 4]
            and "Four conditions in a frozen 96-task extension" in paper_text
            and "64--87 eligible opportunities" in paper_text
        ),
        "selection_regret_claim_matches_report": (
            selection_summary["proxy_evaluations"] == 20
            and selection_summary["one_sided_or_stable_evaluations"] == 15
            and selection_summary["one_sided_or_stable_zero_pairacc_rows"] == 15
            and selection_summary["aggregate_suboptimal_rows"] == 1
            and abs(selection_summary["maximum_worst_case_selection_regret"] - 0.96875) < 1e-12
            and "all 15 Stable-only or one-sided maximizer sets include a zero-PairAcc extreme" in paper_text
            and "loses 6.2 points in the fifth" in paper_text
            and "regret reaches 96.9 points" in paper_text
        ),
        "generic_core_writes_equal_conditional_substitutions": all(
            row["core_substitution_writes"] == row["conditional_substitution"][0]
            for row in rows
            if row["controller"] == "Generic"
        ),
        "cta_core_writes_zero_but_all_wrong_reported": all(
            row["core_substitution_writes"] == 0 and row["all_wrong_writes"] > 0
            for row in rows
            if row["controller"] == "CTA"
        ),
    }
    try:
        displayed_paper_path = paper_path.relative_to(root)
    except ValueError:
        displayed_paper_path = paper_path.relative_to(root.parents[1])
    return {
        "status": "zero-API audit rebuilt from frozen outputs and source reports",
        "paper": str(displayed_paper_path),
        "v7_diagnostic_table": rows,
        "v3_primary": primary,
        "human_validation": {
            "n": human["all"]["n_items"],
            "fleiss_kappa": human["all"]["fleiss_kappa"],
            "krippendorff_alpha": human["all"]["krippendorff_alpha_nominal"],
            "majority_gold_accuracy": human["all"]["majority_gold_accuracy"],
            "reject_majority_gold_accuracy": human["anchored_reject"]["majority_gold_accuracy"],
        },
        "public_coverage": coverage["suites"],
        "external_extension": external_extension,
        "selection_regret": selection_summary,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "boundaries": [
            "The audit checks numerical and provenance consistency, not natural prevalence.",
            "Human and public-suite classifications retain the limitations stated in the paper.",
            "Provider inference cannot be reproduced exactly because immutable serving revisions are unavailable.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Main-Paper Evidence Audit",
        "",
        f"**Status:** {report['status']}.",
        "",
        "| Check | Pass |",
        "|---|---:|",
    ]
    lines.extend(
        f"| {name.replace('_', ' ')} | {'yes' if passed else 'NO'} |"
        for name, passed in report["checks"].items()
    )
    lines.extend(
        [
            "",
            "| Model/controller | PairAcc | Conditional substitution | Core writes | All wrong writes | Shared G/CTA |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["v7_diagnostic_table"]:
        pair = row["pairacc"]
        conditional = row["conditional_substitution"]
        lines.append(
            f"| {row['model']} / {row['controller']} | {pair[0]}/{pair[1]} | "
            f"{conditional[0]}/{conditional[1]} | {row['core_substitution_writes']} | "
            f"{row['all_wrong_writes']} | {row['shared_generic_substitutions']}/"
            f"{row['shared_cta_substitutions']} of {row['shared_eligible']} |"
        )
    lines.extend(
        [
            "",
            "| 96-task paper-facing condition | Rows | Opportunities | Mechanism errors | Wrong writes |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["external_extension"]:
        lines.append(
            f"| {row['report']} | {row['rows']} | {row['opportunities']} | "
            f"{row['mechanism_errors']} | {row['wrong_writes']} |"
        )
    lines.extend(["", *[f"- {item}" for item in report["boundaries"]], ""])
    return "\n".join(lines)


def validate(report: dict[str, Any]) -> None:
    failed = [name for name, passed in report["checks"].items() if not passed]
    if failed:
        raise ValueError(f"main-paper evidence audit failed: {', '.join(failed)}")
