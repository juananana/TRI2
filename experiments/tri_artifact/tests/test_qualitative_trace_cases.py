from tri.qualitative_trace_cases import build_report


def test_selected_cases_are_source_validated() -> None:
    report = build_report()
    v7 = report["v7_sqlite_conditional_tri"]
    assert v7["ledger_selected_id"] == v7["authorized_target"]
    assert v7["generic_final_target"] == v7["refreshed_winner"]
    assert v7["sqlite_action_status"] == "wrong_entity_write"
    assert v7["cta_final_target"] == v7["authorized_target"]

    external = report["appworld_correct_opportunity"]
    assert external["initial_target"] != external["refreshed_target"]
    assert external["written_target"] == external["initial_target"]

    prebind = report["appworld_prebinding_error"]
    assert not prebind["initial_binding_correct"]
    assert not prebind["binding_timing_correct"]
    assert not prebind["conditional_tri"]
