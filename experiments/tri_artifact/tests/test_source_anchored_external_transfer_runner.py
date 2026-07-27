from __future__ import annotations

from scripts.run_source_anchored_external_transfer import parse_object, select_smoke
from tri.source_anchored_external_transfer_report import build_report, render_latex_table


def test_parse_object_accepts_fenced_json() -> None:
    parsed, error = parse_object('```json\n{"selected_target_id":"A"}\n```')
    assert error is None
    assert parsed == {"selected_target_id": "A"}


def test_smoke_selects_one_complete_cluster_per_repository() -> None:
    tasks = []
    for repository in ("A", "B"):
        for cluster in ("1", "2"):
            for cell in range(4):
                tasks.append({"repository": repository, "cluster_id": cluster, "cell": cell})
    selected = select_smoke(tasks)
    assert len(selected) == 8
    assert {task["cluster_id"] for task in selected} == {"1"}


def test_smoke_report_requires_ninety_percent_and_both_repositories() -> None:
    rows = []
    for model in ("M1", "M2"):
        for controller in ("ordinary_full_history", "execution_record"):
            for repository in ("STATE-Bench", "AgentDojo"):
                for index in range(4):
                    rows.append(
                        {
                            "model": model,
                            "controller": controller,
                            "repository": repository,
                            "task_id": f"{repository}-{index}",
                            "status": "ok",
                            "initial_binding_correct": True,
                            "exact_target_success": True,
                            "wrong_entity_write": False,
                            "first_transport_error": None,
                            "second_transport_error": None,
                            "first_parse_error": None,
                            "second_parse_error": None,
                            "source_execution_error": None,
                            "write_executed": True,
                            "timing": "preserve" if index < 2 else "reevaluate",
                            "transition": "stable" if index % 2 == 0 else "changed",
                            "cluster_id": f"{repository}-cluster",
                            "domain": repository.lower(),
                            "predicted_target_id": "old",
                            "initial_winner_id": "old",
                            "refreshed_winner_id": "new" if index % 2 else "old",
                            "old_target_present_after_refresh": True,
                            "old_target_action_valid_after_refresh": True,
                            "write_executed": True,
                            "request_attempts": 2,
                        }
                    )
    assert build_report(rows, expected_rows=32, smoke=True)["smoke_gate"] == "GO"
    rows[0]["status"] = "failed"
    rows[1]["status"] = "failed"
    rows[2]["status"] = "failed"
    rows[3]["status"] = "failed"
    assert build_report(rows, expected_rows=32, smoke=True)["smoke_gate"] == "NO-GO"


def test_latex_table_is_generated_from_conditional_cells() -> None:
    rows = []
    for repository in ("STATE-Bench", "AgentDojo"):
        for model in ("M1", "M2"):
            for controller in ("ordinary_full_history", "execution_record"):
                for index, (timing, transition) in enumerate(
                    (("preserve", "stable"), ("preserve", "changed"),
                     ("reevaluate", "stable"), ("reevaluate", "changed"))
                ):
                    rows.append(
                        {
                            "model": model,
                            "controller": controller,
                            "repository": repository,
                            "domain": repository.lower(),
                            "task_id": f"{repository}-{model}-{controller}-{index}",
                            "cluster_id": f"{repository}-cluster",
                            "timing": timing,
                            "transition": transition,
                            "status": "ok",
                            "initial_binding_correct": True,
                            "exact_target_success": True,
                            "write_executed": True,
                            "wrong_entity_write": False,
                            "first_transport_error": None,
                            "second_transport_error": None,
                            "first_parse_error": None,
                            "second_parse_error": None,
                            "source_execution_error": None,
                            "predicted_target_id": "old" if timing == "preserve" else "new",
                            "initial_winner_id": "old",
                            "refreshed_winner_id": "new" if transition == "changed" else "old",
                            "old_target_present_after_refresh": True,
                            "old_target_action_valid_after_refresh": True,
                            "request_attempts": 2,
                        }
                    )
    latex = render_latex_table(build_report(rows, expected_rows=32, smoke=True))
    assert "P/C$\\to$new" in latex
    assert "STATE-Bench" in latex
