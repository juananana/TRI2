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
    cluster_id: str = "simple-note-alphabetical-first"
    selector: str = "the alphabetically first TRI experiment note"


PRESERVE = [
    (
        "Find the alphabetically first note tagged tri-experiment in Simple Note as "
        "the notes are now. Synchronize Simple Note, then append 'reviewed' to the note "
        "you found."
    ),
    (
        "Before synchronizing Simple Note, identify the first tri-experiment note in "
        "alphabetical title order. After synchronization, append 'reviewed' to that same note."
    ),
]

REEVALUATE = [
    (
        "Synchronize Simple Note first. Then find the alphabetically first note tagged "
        "tri-experiment and append 'reviewed' to it."
    ),
    (
        "Refresh Simple Note before choosing a note. From the updated tri-experiment notes, "
        "identify the first title alphabetically and append 'reviewed' to that note."
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
                            f"appworld-simple-note-p{paraphrase_index + 1}-{mode}-{transition}"
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
