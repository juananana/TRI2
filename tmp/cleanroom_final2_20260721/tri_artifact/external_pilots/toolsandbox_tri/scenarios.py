from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
from typing import Literal


ReferenceMode = Literal["preserve", "reevaluate"]
Transition = Literal["flip", "stable", "invalidate", "remove"]


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    instruction: str
    reference_mode: ReferenceMode
    transition: Transition
    initial_target_id: str
    refreshed_target_id: str | None
    correct_target_id: str | None
    selector: str = "the editable reminder due earliest"
    rank_field: Literal["reminder_timestamp", "creation_timestamp", "content"] = (
        "reminder_timestamp"
    )
    descending: bool = False
    invalidity_policy: Literal["reject"] = "reject"
    postpone_seconds: float = 86_400.0
    paraphrase_id: str = "canonical"
    cluster_id: str = ""
    require_binding_record: bool = False


def build_pilot_scenarios() -> list[Scenario]:
    """Return the preregistration smoke set, before language expansion."""
    return [
        Scenario(
            scenario_id="ts-reminder-preserve-flip",
            instruction=(
                "Find the reminder that is currently due earliest. Sync the reminders, "
                "then postpone the reminder you found by 24 hours."
            ),
            reference_mode="preserve",
            transition="flip",
            initial_target_id="REM-A",
            refreshed_target_id="REM-B",
            correct_target_id="REM-A",
        ),
        Scenario(
            scenario_id="ts-reminder-reevaluate-flip",
            instruction=(
                "Sync the reminders first. Then find the reminder due earliest and "
                "postpone it by 24 hours."
            ),
            reference_mode="reevaluate",
            transition="flip",
            initial_target_id="REM-A",
            refreshed_target_id="REM-B",
            correct_target_id="REM-B",
        ),
        Scenario(
            scenario_id="ts-reminder-preserve-invalidate",
            instruction=(
                "Find the reminder that is currently due earliest. Sync the reminders, "
                "then postpone the reminder you found by 24 hours. If it has become "
                "locked, do not modify another reminder."
            ),
            reference_mode="preserve",
            transition="invalidate",
            initial_target_id="REM-A",
            refreshed_target_id="REM-A",
            correct_target_id=None,
        ),
        Scenario(
            scenario_id="ts-reminder-preserve-remove",
            instruction=(
                "Find the reminder that is currently due earliest. Sync the reminders, "
                "then postpone the reminder you found by 24 hours. If it no longer "
                "exists, do not modify another reminder."
            ),
            reference_mode="preserve",
            transition="remove",
            initial_target_id="REM-A",
            refreshed_target_id="REM-C",
            correct_target_id=None,
        ),
    ]


SELECTORS = [
    ("due-earliest", "the editable reminder due earliest", "reminder_timestamp", False),
    ("due-latest", "the editable reminder due latest", "reminder_timestamp", True),
    ("newest-created", "the newest-created editable reminder", "creation_timestamp", True),
    ("oldest-created", "the oldest-created editable reminder", "creation_timestamp", False),
    ("alpha-first", "the alphabetically first editable reminder", "content", False),
    ("alpha-last", "the alphabetically last editable reminder", "content", True),
]


PRESERVE_SINGLE_TURN = [
    "Find {selector} in the reminders as they are now. Sync the reminders, then postpone the reminder you found by 24 hours.",
    "Before synchronizing, identify {selector}. After the sync, move that same reminder one day later.",
    "Using the current list, choose {selector}. Refresh the list and then delay the one you chose by 24 hours.",
    "First determine which reminder is {selector}; next synchronize the reminders; finally postpone that previously determined reminder for one day.",
]

REEVALUATE_SINGLE_TURN = [
    "Sync the reminders first. Then find {selector} in the synchronized list and postpone it by 24 hours.",
    "Refresh the reminder list before choosing. Afterward, identify {selector} and move that reminder one day later.",
    "First synchronize the reminders; using the updated list, choose {selector} and delay it by 24 hours.",
    "Bring the reminders up to date, then determine which reminder is {selector}, and finally postpone the resulting reminder for one day.",
]


def _instruction(selector: str, mode: ReferenceMode) -> str:
    if mode == "preserve":
        return (
            f"Find {selector} now. Sync the reminders, then postpone the reminder you "
            "found by 24 hours. If that reminder is gone or no longer editable, do not "
            "modify a replacement."
        )
    return (
        f"Sync the reminders first. Then find {selector} in the synchronized state and "
        "postpone it by 24 hours."
    )


def build_frozen_scenarios() -> list[Scenario]:
    """Build 24 paired tasks: six selectors and two transition pairs each."""
    scenarios: list[Scenario] = []
    secondary = ["stable", "stable", "invalidate", "invalidate", "remove", "remove"]
    for index, (slug, selector, rank_field, descending) in enumerate(SELECTORS):
        for transition in ("flip", secondary[index]):
            for mode in ("preserve", "reevaluate"):
                refreshed_target = "REM-B" if transition == "flip" else "REM-A"
                if transition in {"invalidate", "remove"}:
                    refreshed_target = "REM-C"
                correct_target = "REM-A" if mode == "preserve" else refreshed_target
                if mode == "preserve" and transition in {"invalidate", "remove"}:
                    correct_target = None
                scenarios.append(
                    Scenario(
                        scenario_id=f"ts-{slug}-{mode}-{transition}",
                        instruction=_instruction(selector, mode),
                        reference_mode=mode,
                        transition=transition,  # type: ignore[arg-type]
                        initial_target_id="REM-A",
                        refreshed_target_id=refreshed_target,
                        correct_target_id=correct_target,
                        selector=selector,
                        rank_field=rank_field,  # type: ignore[arg-type]
                        descending=descending,
                    )
                )
    assert len(scenarios) == 24
    assert len({scenario.scenario_id for scenario in scenarios}) == 24
    return scenarios


def build_single_turn_2x2_scenarios() -> list[Scenario]:
    """Build the frozen 96-task existence study with 24 tasks in each 2x2 cell."""
    scenarios: list[Scenario] = []
    for slug, selector, rank_field, descending in SELECTORS:
        for paraphrase_index in range(4):
            for transition in ("stable", "flip"):
                for mode in ("preserve", "reevaluate"):
                    templates = (
                        PRESERVE_SINGLE_TURN
                        if mode == "preserve"
                        else REEVALUATE_SINGLE_TURN
                    )
                    refreshed_target = "REM-A" if transition == "stable" else "REM-B"
                    correct_target = (
                        "REM-A" if mode == "preserve" else refreshed_target
                    )
                    scenarios.append(
                        Scenario(
                            scenario_id=(
                                f"ts3-{slug}-p{paraphrase_index + 1}-{mode}-{transition}"
                            ),
                            instruction=templates[paraphrase_index].format(selector=selector),
                            reference_mode=mode,  # type: ignore[arg-type]
                            transition=transition,  # type: ignore[arg-type]
                            initial_target_id="REM-A",
                            refreshed_target_id=refreshed_target,
                            correct_target_id=correct_target,
                            selector=selector,
                            rank_field=rank_field,  # type: ignore[arg-type]
                            descending=descending,
                            paraphrase_id=f"p{paraphrase_index + 1}",
                            cluster_id=slug,
                            require_binding_record=True,
                        )
                    )
    assert len(scenarios) == 96
    assert len({scenario.scenario_id for scenario in scenarios}) == 96
    cells = {
        (mode, transition): sum(
            scenario.reference_mode == mode and scenario.transition == transition
            for scenario in scenarios
        )
        for mode in ("preserve", "reevaluate")
        for transition in ("stable", "flip")
    }
    assert set(cells.values()) == {24}
    return scenarios


PRESERVE_HELDOUT = [
    "Before synchronizing, check which entry is {selector}. Once synchronization finishes, move that reminder one day later. If the entry disappeared or is read-only, stop instead of switching entries.",
    "Identify {selector} in the list as it stands. Update the list from the server, then delay the one just identified by a day. Do nothing if that entry is missing or cannot be edited.",
    "From the reminders shown now, determine {selector}. Next, synchronize. Put the reminder you determined off for 24 hours, unless it is gone or locked; never substitute another.",
    "Take note of {selector} before refreshing the reminders. After the refresh, postpone it by one day. If that particular entry is absent or non-editable, leave all reminders unchanged.",
]

REEVALUATE_HELDOUT = [
    "Bring the reminder list up to date, then choose {selector} from the synchronized list and move it one day later.",
    "Do not choose an entry yet. Synchronize first; afterward identify {selector} and delay that reminder by 24 hours.",
    "After the reminder refresh has completed, determine {selector} and postpone the resulting entry for one day.",
    "Using only the synchronized reminder list, identify {selector}; refresh before making that choice, then put the chosen reminder off by 24 hours.",
]


def build_matched_heldout_scenarios() -> list[Scenario]:
    scenarios = []
    for index, scenario in enumerate(build_frozen_scenarios()):
        templates = (
            PRESERVE_HELDOUT
            if scenario.reference_mode == "preserve"
            else REEVALUATE_HELDOUT
        )
        instruction = templates[index % len(templates)].format(selector=scenario.selector)
        scenarios.append(
            replace(
                scenario,
                scenario_id=scenario.scenario_id.replace("ts-", "ts2-", 1),
                instruction=instruction,
            )
        )
    assert len(scenarios) == 24
    assert len({scenario.instruction for scenario in scenarios}) == 24
    return scenarios


def write_scenarios(path: Path, scenarios: list[Scenario]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for scenario in scenarios:
            handle.write(json.dumps(asdict(scenario), ensure_ascii=False) + "\n")


def load_scenarios(path: Path) -> list[Scenario]:
    with path.open(encoding="utf-8") as handle:
        return [Scenario(**json.loads(line)) for line in handle if line.strip()]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--set", choices=["v1", "matched-heldout", "single-turn-2x2"], default="v1"
    )
    args = parser.parse_args()
    output = Path(args.output)
    if args.set == "matched-heldout":
        scenarios = build_matched_heldout_scenarios()
    elif args.set == "single-turn-2x2":
        scenarios = build_single_turn_2x2_scenarios()
    else:
        scenarios = build_frozen_scenarios()
    write_scenarios(output, scenarios)
    print(output)
