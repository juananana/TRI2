from __future__ import annotations

import json
from pathlib import Path

from tri.external_public_opportunity_audit import (
    _linked_query_mutation,
    audit_bfcl,
    build_report,
    is_mutation,
    is_query,
)


def test_tool_name_classification() -> None:
    assert is_query("Calendar.QueryCalendar")
    assert is_query("TravelAPI.get_flight_cost")
    assert is_mutation("Calendar.ModifyEvent")
    assert is_mutation("TravelAPI.cancel_booking")
    assert not is_mutation("TravelAPI.get_flight_cost")


def test_exact_id_link_requires_query_response_to_feed_later_mutation() -> None:
    calls = [
        {
            "name": "QueryCalendar",
            "request": {},
            "response": {"events": [{"event_id": "E-1"}]},
        },
        {
            "name": "ModifyEvent",
            "request": {"event_id": "E-1"},
            "response": {"status": "success"},
        },
    ]
    linked, ids = _linked_query_mutation(calls)
    assert linked
    assert ids == ["E-1"]


def test_exact_id_link_rejects_unrelated_mutation() -> None:
    calls = [
        {
            "name": "QueryCalendar",
            "request": {},
            "response": {"events": [{"event_id": "E-1"}]},
        },
        {
            "name": "ModifyEvent",
            "request": {"event_id": "E-2"},
            "response": {"status": "success"},
        },
    ]
    linked, ids = _linked_query_mutation(calls)
    assert not linked
    assert ids == []


def _record(dataset: str, cluster: str, eligible: bool) -> dict[str, object]:
    return {
        "dataset": dataset,
        "cluster_id": cluster,
        "query_before_mutation": eligible,
        "exact_id_linkage": eligible,
        "native_update_language": False,
        "timing_label": "absent",
        "source_anchored_eligible": eligible,
        "strict_native_opportunity": False,
    }


def test_gate_requires_two_datasets_and_eight_clusters() -> None:
    records = [_record("A", f"a-{index}", True) for index in range(4)]
    records += [_record("B", f"b-{index}", True) for index in range(4)]
    manifest = {"sources": {"A": {"commit": "a"}, "B": {"commit": "b"}}}
    report = build_report(records, manifest)
    assert report["strict_native_opportunities"] == 0
    assert report["siliconflow_annotation_gate"] == "GO"


def test_gate_rejects_eight_clusters_from_one_dataset() -> None:
    records = [_record("A", f"a-{index}", True) for index in range(8)]
    manifest = {"sources": {"A": {"commit": "a"}}}
    report = build_report(records, manifest)
    assert report["siliconflow_annotation_gate"] == "NO-GO"


def test_bfcl_requires_id_in_the_same_executable_class(tmp_path: Path) -> None:
    data_root = tmp_path / "berkeley-function-call-leaderboard" / "bfcl_eval" / "data"
    data_root.mkdir(parents=True)
    task = {
        "id": "multi_turn_base_0",
        "question": [[{"role": "user", "content": "Find and move the file."}]],
        "initial_config": {
            "GorillaFileSystem": {"root": {"file.txt": {"content": "x"}}},
            "TwitterAPI": {"tweets": {"1": {"id": 1}}},
        },
        "path": ["GorillaFileSystem.find", "GorillaFileSystem.mv"],
    }
    (data_root / "BFCL_v4_multi_turn_base.json").write_text(
        json.dumps(task) + "\n", encoding="utf-8"
    )
    records = audit_bfcl(tmp_path)
    assert len(records) == 1
    assert not records[0]["source_anchored_eligible"]
