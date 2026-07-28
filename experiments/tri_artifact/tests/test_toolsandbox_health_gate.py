from __future__ import annotations

import json
from pathlib import Path

from tri.toolsandbox_health_gate import evaluate


def test_health_gate_requires_task_coverage_but_not_model_accuracy(tmp_path: Path) -> None:
    path = tmp_path / "health.jsonl"
    rows = []
    for mode in ("preserve", "reevaluate"):
        for transition in ("stable", "flip"):
            for index in range(2):
                rows.append(
                    {
                        "model": "m",
                        "controller": "full_history",
                        "scenario_id": f"{mode}-{transition}-{index}",
                        "reference_mode": mode,
                        "transition": transition,
                        "errors": [],
                        "tri_opportunity": index == 0,
                    }
                )
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    assert evaluate(path)["passed"]
    rows[0]["tri_opportunity"] = False
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    result = evaluate(path)
    assert result["passed"]
    assert result["opportunities_by_cell"]["preserve_stable"] == 0

    for row in rows:
        if row["reference_mode"] == "preserve" and row["transition"] == "stable":
            row["transition"] = "flip"
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    assert not evaluate(path)["passed"]
