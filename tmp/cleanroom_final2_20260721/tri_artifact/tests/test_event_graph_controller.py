from __future__ import annotations

import json
from pathlib import Path

from tri.event_graph_controller import (
    ReferentialCapability,
    VersionedEntityStore,
    compile_oracle_event_graph,
    compile_oracle_selector,
    derive_reference_mode,
    execute_event_graph,
    execute_selector,
    issue_capability,
)


DATA = Path(__file__).resolve().parents[1] / "data"


def _load(name: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (DATA / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _oracle_rows() -> list[dict]:
    return (
        _load("temporal_referent_v3_language_clusters.jsonl")
        + _load("temporal_referent_v7_core_replication.jsonl")
        + _load("temporal_referent_v6_role_heldout.jsonl")
    )


def test_oracle_event_graph_and_selector_cover_v3_v7_v6() -> None:
    rows = _oracle_rows()
    assert len(rows) == 440
    for task in rows:
        graph = compile_oracle_event_graph(task)
        selector = compile_oracle_selector(task)
        expected_mode = "preserve" if task["binding"] == "anchored" else "reevaluate"
        assert derive_reference_mode(graph) == expected_mode
        assert execute_selector(selector, task["initial_state"]) == task["pre_refresh_target"]
        assert execute_selector(
            selector, task.get("final_state", task["refreshed_state"])
        ) == task["post_refresh_target"]
        assert execute_event_graph(task, graph, selector) == task["correct_target"]


def test_capability_is_bound_to_action_target_role() -> None:
    for task in _oracle_rows():
        graph = compile_oracle_event_graph(task)
        capability = issue_capability(task, graph, compile_oracle_selector(task))
        expected_target = (
            task["pre_refresh_target"]
            if task["binding"] == "anchored"
            else task["post_refresh_target"]
        )
        assert capability.target_id == expected_target
        assert capability.action == task["action"]
        assert capability.binding_epoch == (
            "initial" if task["binding"] == "anchored" else "final"
        )


def _capability(store: VersionedEntityStore) -> ReferentialCapability:
    return ReferentialCapability(
        target_id="T-1",
        action="approve",
        source_event="E1",
        binding_epoch="initial",
        action_preconditions=(("actionable", True), ("status", "pending")),
        expected_version=store.version("T-1"),
    )


def test_atomic_gate_blocks_stale_wrong_writes_without_false_blocks() -> None:
    outcomes: list[tuple[str, str, str | None]] = []
    for index in range(20):
        base = [
            {"id": "T-1", "display": "Target", "status": "pending", "actionable": True},
            {"id": "T-2", "display": "Other", "status": "pending", "actionable": True},
        ]
        for mutation in (
            "legal", "unrelated_update", "target_version", "invalidate", "delete", "id_alias"
        ):
            store = VersionedEntityStore(base)
            capability = _capability(store)
            if mutation == "unrelated_update":
                store.update("T-2", note=index)
            elif mutation == "target_version":
                store.update("T-1", note=index)
            elif mutation == "invalidate":
                store.update("T-1", actionable=False)
            elif mutation == "delete":
                store.delete("T-1")
            elif mutation == "id_alias":
                store.delete("T-1")
                store.add({
                    "id": f"ALIAS-{index}", "display": "Target",
                    "status": "pending", "actionable": True,
                })
            result = store.atomic_write(capability, "approve")
            outcomes.append((mutation, result.status, result.written_id))
            if mutation in {"legal", "unrelated_update"}:
                assert result.status == "written"
                assert result.written_id == "T-1"
            else:
                assert result.status in {"stale_version", "invalid_target", "missing_target"}
                assert result.written_id is None
            assert all(target_id == "T-1" for _, target_id in store.writes)

    assert len(outcomes) == 120
    assert sum(status == "written" for _, status, _ in outcomes) == 40
    assert sum(written_id not in {None, "T-1"} for _, _, written_id in outcomes) == 0
