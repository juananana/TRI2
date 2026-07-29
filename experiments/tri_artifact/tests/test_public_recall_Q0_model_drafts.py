from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.build_public_recall_Q0_model_drafts import (
    DEFAULT_QUEUE,
    DEFAULT_TEMPLATE,
    STATUS,
    build,
)
from tri.end_to_end_decision_decomposition import sha256_path
from tri.public_recall_calibrated_audit import RUBRIC_FIELDS


def test_Q0_draft_is_complete_but_cannot_claim_human_evidence(tmp_path: Path) -> None:
    output = tmp_path / "Q0.csv"
    manifest_path = build(DEFAULT_TEMPLATE, DEFAULT_QUEUE, output)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 699
    assert len({row["blind_unit_id"] for row in rows}) == 699
    assert all(row["q0_status"] == STATUS for row in rows)
    assert all(
        row["q0_strict_eligible"] in {"true", "false", "review_required"}
        for row in rows
    )
    for row in rows:
        values = [row[f"q0_feature_{field}"] for field in RUBRIC_FIELDS]
        if row["q0_strict_eligible"] == "true":
            assert values == ["yes"] * len(RUBRIC_FIELDS)
            assert row["q0_primary_exclusion_reason"] == "NONE"
        elif row["q0_strict_eligible"] == "false":
            assert row["q0_primary_exclusion_reason"] in RUBRIC_FIELDS
            assert row[f"q0_feature_{row['q0_primary_exclusion_reason']}"] != "yes"
        else:
            assert "review_required" in values
    assert manifest["draft_csv_sha256"] == sha256_path(output)
    assert manifest["writes_human_Q1_fields"] is False
    assert manifest["human_gate_unlocked"] is False
    assert manifest["independent_human_evidence"] is False
    assert manifest["prevalence_or_recall_claim_allowed"] is False
