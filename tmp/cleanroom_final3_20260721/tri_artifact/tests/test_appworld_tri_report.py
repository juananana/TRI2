from __future__ import annotations

import json
from pathlib import Path

from tri.appworld_tri_report import build_report


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_appworld_result_summary() -> None:
    paths = [
        ROOT / "runs/appworld_tri_Qwen_Qwen3.5-122B-A10B_full_history_full_v1.jsonl",
        ROOT / "runs/appworld_tri_Pro_zai-org_GLM-5.1_full_history_full_v1.jsonl",
    ]
    rows = [
        json.loads(line)
        for path in paths
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    report = build_report(rows)
    assert report["combined"]["rows"] == 16
    assert report["combined"]["strict_successes"] == 14
    assert report["combined"]["authorized_target_writes"] == 16
    assert report["combined"]["binding_opportunities"] == 14
    assert report["combined"]["conditional_tri_errors"] == 0
    assert report["combined"]["wrong_entity_writes"] == 0
