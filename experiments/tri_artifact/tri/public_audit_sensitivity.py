from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from tri.revision_matched_audit import canonical_json, sha256_bytes, sha256_path


SUITES = ("ToolSandbox", "AppWorld", "tau3-bench", "API-Bank", "BFCL", "ToolTalk")
FEATURES = (
    "stable_entity_id",
    "observable_pre_refresh_binding",
    "independent_post_binding_transition",
    "competing_same_role_entity",
    "changed_selector_winner",
    "old_entity_remains_actionable",
    "later_target_mutation",
    "evaluable_authorized_target",
)


def strict_label(features: dict[str, bool]) -> bool:
    if set(features) != set(FEATURES):
        raise ValueError("sensitivity control has an incomplete feature schema")
    return all(features[name] is True for name in FEATURES)


def build_controls(checklist: Path, structural: Path) -> list[dict[str, Any]]:
    checklist_data = json.loads(checklist.read_text(encoding="utf-8"))
    structural_data = json.loads(structural.read_text(encoding="utf-8"))
    known = {row["benchmark"] for row in checklist_data["benchmarks"]}
    known.update(structural_data["dataset_results"])
    if known != set(SUITES):
        raise ValueError(f"unexpected public-suite inventory: {sorted(known)}")
    rows: list[dict[str, Any]] = []
    for suite in SUITES:
        for index in range(5):
            positive = {feature: True for feature in FEATURES}
            rows.append(
                {
                    "control_id": f"{suite}-strict-positive-{index + 1}",
                    "suite": suite,
                    "control_kind": "strict_positive",
                    "expected_strict": True,
                    "features": positive,
                    "injection_note": "Known-label schema-shaped control; not an upstream benchmark unit.",
                }
            )
            missing = FEATURES[(SUITES.index(suite) + index) % len(FEATURES)]
            negative = dict(positive)
            negative[missing] = False
            rows.append(
                {
                    "control_id": f"{suite}-hard-negative-{index + 1}",
                    "suite": suite,
                    "control_kind": "one-feature-missing",
                    "expected_strict": False,
                    "missing_feature": missing,
                    "features": negative,
                    "injection_note": "Known-label schema-shaped control; not an upstream benchmark unit.",
                }
            )
    return rows


def build_report(rows: list[dict[str, Any]], checklist: Path, structural: Path) -> dict[str, Any]:
    if len(rows) != 60 or Counter(row["suite"] for row in rows) != {suite: 10 for suite in SUITES}:
        raise ValueError("sensitivity controls must contain ten rows per public suite")
    scored = []
    for row in rows:
        observed = strict_label(row["features"])
        scored.append({**row, "observed_strict": observed, "correct": observed == row["expected_strict"]})
    positives = [row for row in scored if row["expected_strict"]]
    negatives = [row for row in scored if not row["expected_strict"]]
    by_suite = {}
    for suite in SUITES:
        subset = [row for row in scored if row["suite"] == suite]
        by_suite[suite] = {
            "positive_recall": sum(row["observed_strict"] for row in subset if row["expected_strict"]) / 5,
            "hard_negative_exclusion": sum(not row["observed_strict"] for row in subset if not row["expected_strict"]) / 5,
            "errors": [row["control_id"] for row in subset if not row["correct"]],
        }
    return {
        "report_version": "TRI-public-audit-injected-sensitivity-v1",
        "evidence_status": "post-primary zero-API implementation sensitivity check",
        "inputs": {
            "benchmark_coverage_checklist_sha256": sha256_path(checklist),
            "external_public_opportunity_audit_sha256": sha256_path(structural),
        },
        "controls_sha256": sha256_bytes(
            ("\n".join(canonical_json(row) for row in rows) + "\n").encode("utf-8")
        ),
        "strict_positive_recall": {
            "numerator": sum(row["observed_strict"] for row in positives),
            "denominator": len(positives),
        },
        "hard_negative_exclusion": {
            "numerator": sum(not row["observed_strict"] for row in negatives),
            "denominator": len(negatives),
        },
        "by_suite": by_suite,
        "missing_feature_counts": dict(
            sorted(Counter(row.get("missing_feature") for row in negatives).items())
        ),
        "boundary": (
            "This checks the deterministic checklist implementation on known-label injected controls. "
            "It does not estimate recall on natural benchmark opportunities, validate semantic retrieval, "
            "or establish systematic benchmark undercoverage."
        ),
        "rows": scored,
    }


def render_markdown(report: dict[str, Any]) -> str:
    positive = report["strict_positive_recall"]
    negative = report["hard_negative_exclusion"]
    lines = [
        "# Public-Audit Injected Sensitivity Check",
        "",
        f"**Evidence status:** {report['evidence_status']}.",
        "",
        f"Strict-positive controls recovered: {positive['numerator']}/{positive['denominator']}.",
        f"One-feature-missing controls excluded: {negative['numerator']}/{negative['denominator']}.",
        "",
        "| Suite | Positive recall | Hard-negative exclusion | Errors |",
        "|---|---:|---:|---|",
    ]
    for suite, row in report["by_suite"].items():
        lines.append(
            f"| {suite} | {100 * row['positive_recall']:.0f}% | "
            f"{100 * row['hard_negative_exclusion']:.0f}% | {', '.join(row['errors']) or 'none'} |"
        )
    lines.extend(["", report["boundary"], ""])
    return "\n".join(lines)
