import copy
import json
from pathlib import Path

import pytest

from tri.crossed_cluster_sensitivity import (
    build_report,
    index_rows,
    prepare_pairs,
    sensitivity_intervals,
)


ROOT = Path(__file__).resolve().parents[1]


def make_rows() -> tuple[list[dict], list[dict]]:
    generic = []
    gated = []
    for domain_index, domain in enumerate(("mail", "calendar")):
        for template_index, template in enumerate(("t1", "t2", "t3")):
            task = {
                "id": f"{domain}-{template}",
                "domain": domain,
                "template_id": template,
                "instruction": f"instruction-{domain_index}-{template_index}",
            }
            generic.append(
                {"status": "ok", "task": copy.deepcopy(task), "result": {"success": False}}
            )
            gated.append(
                {"status": "ok", "task": copy.deepcopy(task), "result": {"success": True}}
            )
    return generic, gated


def test_prepare_pairs_validates_complete_cross_and_metadata() -> None:
    generic, gated = make_rows()
    pairs = prepare_pairs(
        generic,
        gated,
        expected_tasks=6,
        expected_domains=2,
        expected_templates=3,
    )
    assert len(pairs) == 6
    assert {(pair.domain, pair.template_id) for pair in pairs} == {
        (domain, template)
        for domain in ("mail", "calendar")
        for template in ("t1", "t2", "t3")
    }

    mismatched = copy.deepcopy(gated)
    mismatched[0]["task"]["instruction"] = "changed"
    with pytest.raises(ValueError, match="metadata"):
        prepare_pairs(
            generic,
            mismatched,
            expected_tasks=6,
            expected_domains=2,
            expected_templates=3,
        )


def test_index_rows_rejects_duplicate_ids(tmp_path: Path) -> None:
    generic, _ = make_rows()
    path = tmp_path / "duplicate.jsonl"
    path.write_text(
        "\n".join(json.dumps(row) for row in [generic[0], generic[0]]) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate task.id"):
        index_rows(path, expected_tasks=2)


def test_prepare_pairs_rejects_id_mismatch() -> None:
    generic, gated = make_rows()
    gated[-1]["task"]["id"] = "replacement-id"
    with pytest.raises(ValueError, match="different task.id sets"):
        prepare_pairs(
            generic,
            gated,
            expected_tasks=6,
            expected_domains=2,
            expected_templates=3,
        )


def test_three_bootstraps_are_deterministic_and_share_point_estimate() -> None:
    generic, gated = make_rows()
    pairs = prepare_pairs(
        generic,
        gated,
        expected_tasks=6,
        expected_domains=2,
        expected_templates=3,
    )
    first = sensitivity_intervals(pairs, draws=200, seed=20260725)
    second = sensitivity_intervals(pairs, draws=200, seed=20260725)
    assert first == second
    assert set(first) == {"language_template", "domain", "two_way_pigeonhole"}
    for result in first.values():
        assert result["point_estimate"] == 1.0
        assert result["ci95"] == [1.0, 1.0]
        assert result["width"] == 0.0


def test_real_report_uses_complete_primary_inventory() -> None:
    report = build_report(ROOT / "runs", draws=100, seed=20260725)
    assert report["evidence_status"] == "post-primary replication/audit"
    assert report["zero_api"] is True
    assert report["draws"] == 100
    assert [row["model"] for row in report["models"]] == ["Qwen3.5", "GLM-5.1"]
    assert [row["source_run_evidence_status"] for row in report["models"]] == [
        "primary/frozen",
        "post-primary replication/audit",
    ]
    assert len({row["task_inventory_sha256"] for row in report["models"]}) == 1
    for row in report["models"]:
        assert row["matched_tasks"] == 160
        assert row["domains"] == 8
        assert row["language_template_clusters"] == 20
        assert row["cross_cells"] == 160
        assert set(row["methods"]) == {
            "language_template",
            "domain",
            "two_way_pigeonhole",
        }
        assert row["point_estimate"] > 0.25
