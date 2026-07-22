from pathlib import Path

from tri.appworld_tri_multicluster_report import build_report, load_rows


ROOT = Path(__file__).resolve().parents[1]


def test_multicluster_report_keeps_wrong_write_outside_tri_denominator() -> None:
    rows = load_rows(
        [
            ROOT / "runs/appworld_tri_Qwen_Qwen3.5-122B-A10B_full_history_full_v1.jsonl",
            ROOT / "runs/appworld_tri_Pro_zai-org_GLM-5.1_full_history_full_v1.jsonl",
            ROOT
            / "runs/appworld_tri_simple_note_Qwen_Qwen3.5-122B-A10B_full_history_full_v1.jsonl",
            ROOT
            / "runs/appworld_tri_simple_note_Pro_zai-org_GLM-5.1_full_history_full_v1.jsonl",
        ]
    )
    report = build_report(rows)
    assert report["cluster_count"] == 2
    assert report["combined"]["rows"] == 32
    assert report["combined"]["wrong_entity_writes"] == 1
    assert report["combined"]["conditional_tri_errors"] == 0
    assert report["combined"]["wrong_writes_without_prior_auditable_binding"] == 1
