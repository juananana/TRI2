"""Offline safeguards for an LLM-assisted public-coverage audit.

LLM output may locate passages and propose a rubric label. It is never an
independent reviewer, a source of benchmark facts, or a manuscript result.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


RUBRIC_VERSION = "TRI-public-coverage-v1"
SOURCE_BY_BENCHMARK = {
    "ToolSandbox": "reports/official_toolsandbox_tri_prevalence_audit.json",
    "AppWorld": "reports/appworld_public_trace_tri_audit.json",
    "tau3-bench": "reports/official_tau3_native_tri_audit.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _require_empty_llm(record: dict[str, Any]) -> None:
    assistance = record["llm_assistance"]
    assert assistance["status"] == "not_run"
    assert assistance["provider"] is None
    assert assistance["model_id"] is None
    assert assistance["prompt_sha256"] is None
    assert assistance["output_sha256"] is None
    assert assistance["candidate_labels"] == []


def _require_unreviewed_humans(record: dict[str, Any]) -> None:
    review = record["human_review"]
    assert review["status"] == "unreviewed"
    assert review["reviewer_a"] is None
    assert review["reviewer_b"] is None
    assert review["adjudicator"] is None
    assert review["final_labels"] == []


def build_framework_report(artifact_root: Path, template_path: Path) -> dict[str, Any]:
    """Validate that the shipped template remains framework-only and non-evidential."""
    records = load_records(template_path)
    assert len(records) == len(SOURCE_BY_BENCHMARK)
    seen_benchmarks: set[str] = set()
    seen_ids: set[str] = set()

    for record in records:
        assert record["record_id"] not in seen_ids
        seen_ids.add(record["record_id"])
        benchmark = record["benchmark"]
        assert benchmark in SOURCE_BY_BENCHMARK
        seen_benchmarks.add(benchmark)
        assert record["rubric_version"] == RUBRIC_VERSION
        assert record["source"]["path"] == SOURCE_BY_BENCHMARK[benchmark]
        source_path = artifact_root / record["source"]["path"]
        assert source_path.is_file()
        assert record["source"]["sha256"] == _sha256(source_path)
        assert record["candidate_case"]
        assert record["publication_status"] == "non_evidence"
        _require_empty_llm(record)
        _require_unreviewed_humans(record)

    assert seen_benchmarks == set(SOURCE_BY_BENCHMARK)
    return {
        "study": "LLM-assisted public-benchmark coverage reproducibility framework",
        "status": "planned/unverified; zero-API framework validation",
        "decision": "FRAMEWORK-ONLY / NOT EVIDENCE",
        "rubric_version": RUBRIC_VERSION,
        "record_count": len(records),
        "frozen_source_hashes_verified": True,
        "llm_assistance_completed": 0,
        "human_reviews_completed": 0,
        "claim_boundary": (
            "The template ships with no LLM output and no human review. Future LLM extraction "
            "is a fallible retrieval aid; it cannot count as an independent author, annotator, "
            "or reviewer and cannot change the public-coverage conclusion without separately "
            "recorded human review and adjudication."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# LLM-Assisted Public-Coverage Audit Framework",
            "",
            f"**Decision: {report['decision']}**",
            "",
            "This is a zero-API reproducibility framework, not a new benchmark audit or empirical result.",
            "",
            "## Validation",
            "",
            f"- Frozen source hashes verified: {report['frozen_source_hashes_verified']}",
            f"- Template records: {report['record_count']}",
            f"- LLM-assisted records completed: {report['llm_assistance_completed']}",
            f"- Human reviews completed: {report['human_reviews_completed']}",
            "",
            "## Boundary",
            "",
            report["claim_boundary"],
            "",
        ]
    )
