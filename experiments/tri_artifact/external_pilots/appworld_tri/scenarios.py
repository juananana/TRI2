from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Literal


ReferenceMode = Literal["preserve", "reevaluate"]
Transition = Literal["stable", "flip"]


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    instruction: str
    reference_mode: ReferenceMode
    transition: Transition
    paraphrase_id: str
    cluster_id: str = "todoist-earliest-due"
    selector: str = "the incomplete Todoist task due earliest"


PRESERVE = [
    (
        "Find the incomplete Todoist task due earliest in the list as it is now. "
        "Synchronize Todoist, then postpone the task you found by one day."
    ),
    (
        "Before synchronizing Todoist, identify its earliest-due incomplete task. "
        "After synchronization, move that same task one day later."
    ),
]

REEVALUATE = [
    (
        "Synchronize Todoist first. Then find the incomplete task due earliest in "
        "the synchronized list and postpone it by one day."
    ),
    (
        "Refresh Todoist before choosing a task. From the updated list, identify the "
        "earliest-due incomplete task and move it one day later."
    ),
]


def build_scenarios() -> list[Scenario]:
    scenarios: list[Scenario] = []
    for paraphrase_index in range(2):
        for transition in ("stable", "flip"):
            for mode in ("preserve", "reevaluate"):
                instruction = (PRESERVE if mode == "preserve" else REEVALUATE)[
                    paraphrase_index
                ]
                scenarios.append(
                    Scenario(
                        scenario_id=(
                            f"appworld-todoist-p{paraphrase_index + 1}-{mode}-{transition}"
                        ),
                        instruction=instruction,
                        reference_mode=mode,  # type: ignore[arg-type]
                        transition=transition,  # type: ignore[arg-type]
                        paraphrase_id=f"p{paraphrase_index + 1}",
                    )
                )
    assert len(scenarios) == 8
    assert len({scenario.scenario_id for scenario in scenarios}) == 8
    return scenarios


def write_scenarios(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for scenario in build_scenarios():
            handle.write(json.dumps(asdict(scenario), ensure_ascii=True) + "\n")


def load_scenarios(path: Path) -> list[Scenario]:
    with path.open(encoding="utf-8") as handle:
        return [Scenario(**json.loads(line)) for line in handle if line.strip()]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    write_scenarios(args.output)
    print(args.output)
