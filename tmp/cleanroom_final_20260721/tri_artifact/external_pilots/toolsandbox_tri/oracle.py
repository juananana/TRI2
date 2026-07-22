from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .environment import (
    active_scenario,
    postpone_reminder,
    record_binding,
    search_all_reminders,
    sync_reminders,
)
from .evaluation import score_runtime
from .scenarios import Scenario, build_frozen_scenarios, build_pilot_scenarios


def run_oracle(scenario: Scenario) -> dict[str, Any]:
    with active_scenario(scenario) as runtime:
        if scenario.reference_mode == "preserve":
            initial = search_all_reminders()
            bound_id = select_target(initial, scenario)
            if scenario.require_binding_record:
                record_binding(bound_id)
            sync_reminders()
            target_id = bound_id
        else:
            sync_reminders()
            refreshed = search_all_reminders()
            target_id = select_target(refreshed, scenario)
            if scenario.require_binding_record:
                record_binding(target_id)

        if scenario.correct_target_id is not None:
            postpone_reminder(target_id, scenario.postpone_seconds)
        return score_runtime(runtime)


def run_oracle_suite() -> list[dict[str, Any]]:
    return [run_oracle(scenario) for scenario in build_pilot_scenarios()]


def select_target(rows: list[dict[str, Any]], scenario: Scenario) -> str:
    editable = [row for row in rows if row.get("editable", True)]
    selected = sorted(
        editable,
        key=lambda row: (row[scenario.rank_field], row["reminder_id"]),
        reverse=scenario.descending,
    )[0]
    return str(selected["reminder_id"])


def run_frozen_oracle_suite() -> list[dict[str, Any]]:
    return [run_oracle(scenario) for scenario in build_frozen_scenarios()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
