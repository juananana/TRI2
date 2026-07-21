from scripts.build_benchmark_coverage_checklist import build_report


def test_checklist_is_source_guarded_and_has_no_strict_benchmark() -> None:
    report = build_report()
    assert len(report["benchmarks"]) == 3
    by_name = {row["benchmark"]: row for row in report["benchmarks"]}
    assert by_name["ToolSandbox"]["features"]["independent_post_binding_transition"]["status"] == "no"
    assert by_name["AppWorld"]["features"]["changed_selector_winner"]["status"] == "partial"
    assert by_name["tau3-bench"]["features"]["competing_same_role_entity"]["status"] == "no"
    for benchmark in report["benchmarks"]:
        assert all(item["evidence"] for item in benchmark["features"].values())
