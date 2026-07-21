from __future__ import annotations

import json
from pathlib import Path

from scripts.analyze_rssa_smoke import analyze, markdown


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


def test_rssa_report_accepts_cli_relative_paths_and_reproduces_no_go(
    monkeypatch,
) -> None:
    monkeypatch.chdir(ROOT)
    report = analyze([
        Path("runs/rssa_smoke_qwen_v1.jsonl"),
        Path("runs/rssa_smoke_glm_v1.jsonl"),
    ])

    assert report["run_files"] == [
        "runs/rssa_smoke_qwen_v1.jsonl",
        "runs/rssa_smoke_glm_v1.jsonl",
    ]
    assert report["decision"] == "NO-GO"
    assert not report["promote_to_expansion"]
    groups = {group["label"]: group for group in report["groups"]}
    assert groups["Qwen"]["n"] == 20
    assert groups["GLM"]["n"] == 20
    assert groups["Qwen"]["counts"]["schema_valid"] == 20
    assert groups["GLM"]["counts"]["schema_valid"] == 0
    assert groups["Qwen"]["counts"]["producer_edge_correct"] == 20
    assert "Decision: **NO-GO**" in markdown(report)

    for filename in ("rssa_smoke_qwen_v1.jsonl", "rssa_smoke_glm_v1.jsonl"):
        rows = [json.loads(line) for line in (RUNS / filename).read_text(
            encoding="utf-8"
        ).splitlines() if line.strip()]
        assert len(rows) == 20
        assert len({row["task_id"] for row in rows}) == 20
