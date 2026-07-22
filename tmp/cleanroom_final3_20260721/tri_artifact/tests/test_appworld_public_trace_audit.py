from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/appworld_public_trace_tri_audit.json"


def test_public_trace_audit_is_conditioned_and_nonzero() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    combined = report["combined"]
    assert report["strict_exogenous_tri_opportunity_count"] == 0
    assert report["tri_like_generator_family_count"] == 1
    assert combined["released_trajectory_count"] > 0
    assert combined["post_binding_opportunities"] > 0
    assert combined["same_id_preservations"] <= combined["post_binding_opportunities"]
