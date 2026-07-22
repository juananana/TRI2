from __future__ import annotations

from collections import Counter

from tri.v7_core_replication import SCHEMAS, task_rows


def test_v7_inventory_and_balance() -> None:
    rows = task_rows()
    assert len(rows) == 240
    assert len({row["id"] for row in rows}) == 240
    assert len({row["state_cluster_id"] for row in rows}) == 40
    assert len({row["domain"] for row in rows}) == 10
    assert Counter(row["binding"] for row in rows) == {"anchored": 120, "dynamic": 120}
    assert Counter(row["update"] for row in rows) == {
        "flip": 80,
        "stable": 80,
        "name_collision": 80,
    }
    assert Counter(row["phenomenon"] for row in rows) == {"explicit": 120, "implicit": 120}


def test_v7_gold_is_rule_derived_and_core_only() -> None:
    for row in task_rows():
        assert row["bound_entity_present_after_refresh"]
        assert row["bound_entity_actionable_after_refresh"]
        if row["update"] == "stable":
            assert row["pre_refresh_target"] == row["post_refresh_target"]
        else:
            assert row["pre_refresh_target"] != row["post_refresh_target"]
        expected = (
            row["pre_refresh_target"]
            if row["binding"] == "anchored"
            else row["post_refresh_target"]
        )
        assert row["correct_target"] == expected


def test_v7_schemas_are_disjoint_from_previous_domains() -> None:
    previous = {
        "mail", "calendar", "commerce", "support", "docs", "crm", "repo", "shipping",
        "projects", "expenses", "inventory", "deployments",
    }
    assert not ({schema["domain"] for schema in SCHEMAS} & previous)
