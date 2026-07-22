from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/analyze_v7_run_cost.py"
SPEC = importlib.util.spec_from_file_location("analyze_v7_run_cost", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_v7_cost_report_uses_recorded_provider_usage(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    row = {
        "model": "model",
        "status": "ok",
        "api_request_attempts": 2,
        "api_retries": 0,
        "latency_s": 3.5,
        "api_usage": [
            {"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14},
            {"prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10},
        ],
        "result": {"mode": "compile_then_act", "success": True},
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    result = MODULE.summarize(path)
    assert result["api_request_attempts"] == 2
    assert result["latency_s"] == 3.5
    assert result["prompt_tokens"] == 17
    assert result["completion_tokens"] == 7
    assert result["total_tokens"] == 24
