import json
from pathlib import Path

from tri.binding_drift_tri_report import build_report


ROOT = Path(__file__).resolve().parents[1]


def write_adapted(path: Path, tasks: list[dict], use_post: bool) -> None:
    rows = []
    for task in tasks:
        target = task["post_refresh_target"] if use_post else task["pre_refresh_target"]
        rows.append({"task": task, "result": {"predicted_target": target, "success": target == task["correct_target"], "ambiguous_or_clarify": False, "drift_to_refreshed_winner": task["binding"] == "anchored" and target == task["post_refresh_target"], "premature_lock": task["binding"] == "dynamic" and target == task["pre_refresh_target"], "other_visible_target": False, "errors": []}})
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_report_has_four_methods_per_model(tmp_path: Path) -> None:
    data = ROOT / "data" / "binding_drift_tri_symmetric_smoke_v1.jsonl"
    tasks = [json.loads(line) for line in data.read_text().splitlines()]
    qwen = tmp_path / "qwen.jsonl"
    glm = tmp_path / "glm.jsonl"
    write_adapted(qwen, tasks, True)
    write_adapted(glm, tasks, False)
    report = build_report(data, qwen, glm, ROOT / "runs" / "v7_qwen_compile_then_act_full.jsonl", ROOT / "runs" / "v7_glm_compile_then_act_full.jsonl")
    assert len(report["conditions"]) == 8
    assert all(row["n"] == 20 for row in report["conditions"])
    lock = [row for row in report["conditions"] if row["method"] == "entity_lock_analogue"]
    assert all(row["anchored"]["correct"] == 10 and row["dynamic"]["correct"] == 0 for row in lock)
