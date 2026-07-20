from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_official_toolsandbox_tasks.py"
REPORT = ROOT / "reports" / "official_toolsandbox_tri_prevalence_audit.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("toolsandbox_audit", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_classifier_does_not_promote_structural_match_without_review() -> None:
    module = _load_module()
    record = {
        "scenario_name": "unreviewed",
        "entity_selection_milestone_indices": [0],
        "entity_mutation_milestone_indices": [1, 2],
        "mutation_entity_id_fields": ["person_id"],
        "milestone_edges": [[0, 1], [1, 2]],
    }
    classified = module.classify_record(record)
    assert classified["classification"] == "manual_review_required"
    assert not classified["strict_tri_eligible"]
    assert not classified["tri_like_eligible"]


def test_frozen_official_audit_counts() -> None:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    assert payload["semantic_scenario_family_count"] == 129
    assert payload["official_augmented_instance_count"] == 1032
    assert payload["strict_tri_eligible_count"] == 0
    assert payload["tri_like_eligible_count"] == 1
    included = [
        row["scenario_name"] for row in payload["scenarios"] if row["tri_like_eligible"]
    ]
    assert included == [
        "update_contact_relationship_with_relationship_twice_multiple_user_turn"
    ]
