from tri.qualitative_trace_cases import build_report, markdown_zh


def test_selected_cases_are_source_validated() -> None:
    report = build_report()
    v7 = report["v7_sqlite_conditional_tri"]
    assert v7["ledger_selected_id"] == v7["authorized_target"]
    assert v7["generic_final_target"] == v7["refreshed_winner"]
    assert v7["generic_final_target"] in v7["generic_actor_response"]
    assert v7["sqlite_action_status"] == "wrong_entity_write"
    assert v7["cta_final_target"] == v7["authorized_target"]

    toolsandbox = report["toolsandbox_compatible_positive"]
    assert toolsandbox["initial_binding"] == toolsandbox["authorized_target"]
    assert toolsandbox["generic_written_target"][0] in toolsandbox["generic_actor_response"]
    assert toolsandbox["lifecycle_written_target"][0] in toolsandbox["lifecycle_actor_response"]

    external = report["appworld_correct_opportunity"]
    assert external["initial_target"] != external["refreshed_target"]
    assert external["written_target"] == external["initial_target"]
    assert external["written_target"] in external["model_action"]

    prebind = report["appworld_prebinding_error"]
    assert not prebind["initial_binding_correct"]
    assert not prebind["binding_timing_correct"]
    assert not prebind["conditional_tri"]
    assert prebind["written_target"] in prebind["model_action"]

    chinese = markdown_zh(report)
    assert "条件 TRI 错写" in chinese
    assert v7["instruction"] in chinese
    assert toolsandbox["generic_actor_response"] in chinese
