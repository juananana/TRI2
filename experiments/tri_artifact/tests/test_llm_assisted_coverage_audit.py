from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tri.llm_assisted_coverage_audit import build_framework_report, load_records


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "data" / "llm_assisted_public_coverage_audit_template.jsonl"


def test_blank_template_is_explicitly_not_evidence() -> None:
    report = build_framework_report(ROOT, TEMPLATE)
    assert report["decision"] == "FRAMEWORK-ONLY / NOT EVIDENCE"
    assert report["record_count"] == 3
    assert report["frozen_source_hashes_verified"]
    assert report["llm_assistance_completed"] == 0
    assert report["human_reviews_completed"] == 0


def test_template_rejects_an_llm_only_result(tmp_path: Path) -> None:
    records = copy.deepcopy(load_records(TEMPLATE))
    records[0]["llm_assistance"]["status"] = "complete"
    template = tmp_path / "invalid.jsonl"
    template.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(AssertionError):
        build_framework_report(ROOT, template)
