from pathlib import Path

from tri.appworld_naturalistic_report import build_report, load_rows


ROOT = Path(__file__).resolve().parents[1]


def test_naturalistic_report_separates_prebinding_wrong_writes() -> None:
    rows = load_rows(sorted((ROOT / "runs").glob("appworld_naturalistic_*_full_v1.jsonl")))
    report = build_report(rows)
    total = report["combined"]
    assert total["rows"] == 32
    assert total["binding_opportunities"] == 28
    assert total["conditional_tri_errors"] == 0
    assert total["wrong_writes"] == 2
    assert total["wrong_writes_without_correct_binding"] == 2
