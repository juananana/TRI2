from pathlib import Path

from tri.external_confirmation_gate import build_gate_report


ROOT = Path(__file__).resolve().parents[1]


def test_existing_low_intervention_inventory_is_no_go() -> None:
    report = build_gate_report(ROOT)
    assert report["decision"] == "NO-GO"
    assert report["available_inventory"]["cluster_count"] == 2
    assert report["available_inventory"]["matched_2x2_clusters"] == 2
    assert not report["available_inventory"]["independent_writers_verified"]
    evidence = report["completed_low_intervention_evidence"]
    assert evidence["binding_opportunities"] == 28
    assert evidence["conditional_tri_errors"] == 0
    assert evidence["wrong_writes_without_correct_binding"] == 2
