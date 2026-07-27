from __future__ import annotations

from tri.source_anchored_external_transfer import (
    _make_cluster,
    build_report,
    materialize_tasks,
    validate_cluster,
)


def _cluster(repository: str, cluster_id: str) -> dict[str, object]:
    return _make_cluster(
        cluster_id=cluster_id,
        repository=repository,
        domain="test",
        source_relpath="state.json",
        read_tool="list_records",
        write_tool="update_record",
        selector_text="the unique lowest-priced record",
        ranking_field="price",
        direction="min",
        entities=[
            {"entity_id": "old", "price": 10, "label": "old"},
            {"entity_id": "new", "price": 20, "label": "new"},
        ],
        action="update",
        action_instruction="Update the selected record.",
        refresh_values={"stable": 11, "changed": 9},
    )


def test_materialized_four_cells_have_matched_targets() -> None:
    cluster = _cluster("A", "a-1")
    cluster["source_sha256"] = "abc"
    tasks = materialize_tasks([cluster])
    assert len(tasks) == 4
    targets = {(task["timing"], task["transition"]): task["expected_target_id"] for task in tasks}
    assert targets[("preserve", "stable")] == "old"
    assert targets[("preserve", "changed")] == "old"
    assert targets[("reevaluate", "stable")] == "old"
    assert targets[("reevaluate", "changed")] == "new"
    assert all(not task["forbidden_prompt_terms_found"] for task in tasks)


def test_cluster_validation_rejects_non_flipping_changed_patch() -> None:
    cluster = _cluster("A", "a-1")
    cluster["refresh_patches"]["changed"]["new_value"] = 12
    assert "changed refresh did not create the frozen distinct winner" in validate_cluster(cluster)


def test_gate_requires_both_repositories_and_clean_tool_checks() -> None:
    clusters = [_cluster("A", f"a-{index}") for index in range(4)]
    clusters += [_cluster("B", f"b-{index}") for index in range(4)]
    for cluster in clusters:
        cluster["source_sha256"] = "abc"
    tasks = materialize_tasks(clusters)
    manifest = {
        "sources": {
            "A": {"commit_matches": True},
            "B": {"commit_matches": True},
        }
    }
    checks = [{"task_id": task["task_id"], "passed": True, "error": None} for task in tasks]
    report = build_report(clusters, tasks, manifest, checks)
    assert report["gate"] == "GO"
    checks[0] = {"task_id": tasks[0]["task_id"], "passed": False, "error": "write failed"}
    assert build_report(clusters, tasks, manifest, checks)["gate"] == "NO-GO"
