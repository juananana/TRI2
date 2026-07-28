from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from tri.independent_language_holdout import (
    INSTRUCTIONS,
    PAIRS,
    WRITERS,
    load_assignments,
    sha256_path,
    validate_assignments,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "human_studies" / "independent_language_holdout_12w_final"
ITEM_PATTERN = r"IH-[A-Z]+-\d{2}-[PR]"


def validate_form(writer_id: str, path: Path, assigned_items: set[str]) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    stage_a = re.findall(rf"【情境 \d{{2}}｜({ITEM_PATTERN})】", text)
    stage_b = re.findall(rf"【意图确认 \d{{2}}/10｜({ITEM_PATTERN})】", text)
    echoes = [int(value) for value in re.findall(r"\[q(\d+)\]", text)]
    questions = [int(value) for value in re.findall(r"(?m)^(\d+)\. ", text)]

    if len(stage_a) != 10 or len(set(stage_a)) != 10 or set(stage_a) != assigned_items:
        raise ValueError(f"{writer_id}: Stage A does not match its 10 allocated items")
    if len(stage_b) != 10 or len(set(stage_b)) != 10 or set(stage_b) != assigned_items:
        raise ValueError(f"{writer_id}: Stage B does not match its 10 allocated items")
    if len(echoes) != 10 or set(echoes) != set(range(4, 14)):
        raise ValueError(f"{writer_id}: expected one dynamic echo for every Stage A field")
    if questions != list(range(1, 34)):
        raise ValueError(f"{writer_id}: expected contiguous core questions 1-33")
    checks = {
        "pages": text.count("[分页栏]") + 1,
        "stage_a_text_inputs": text.count("[填空题]"),
        "stage_b_intents": text.count("根据这条原句，你原本打算操作哪个对象"),
        "stage_b_confidence": text.count("你对这个意图判断有多确定"),
        "dynamic_echoes": len(echoes),
    }
    if checks != {
        "pages": 2,
        "stage_a_text_inputs": 10,
        "stage_b_intents": 10,
        "stage_b_confidence": 10,
        "dynamic_echoes": 10,
    }:
        raise ValueError(f"{writer_id}: unexpected page or field counts: {checks}")
    if text.index("【B 阶段｜第 1/1 页】") < text.rindex("[填空题]"):
        raise ValueError(f"{writer_id}: Stage B appears before Stage A is complete")
    return checks


def main() -> None:
    manifest = json.loads((PACKET / "manifest.json").read_text(encoding="utf-8"))
    assignments = load_assignments(PACKET / "writer_allocation.csv")
    validate_assignments(assignments)
    if len(assignments) != INSTRUCTIONS or len({row["pair_id"] for row in assignments}) != PAIRS:
        raise ValueError("allocation must contain 120 items and 60 pairs")
    if sha256_path(PACKET / "writer_allocation.csv") != manifest["allocation_sha256"]:
        raise ValueError("writer allocation hash differs from manifest")

    by_writer: dict[str, set[str]] = defaultdict(set)
    by_pair: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        by_writer[row["writer_id"]].add(row["item_id"])
        by_pair[row["pair_id"]].append(row)
    if Counter(row["writer_id"] for row in assignments) != Counter({writer: 10 for writer in WRITERS}):
        raise ValueError("each writer must have exactly 10 items")
    if any(Counter(row["mode"] for row in assignments if row["writer_id"] == writer)
           != Counter({"preserve": 5, "reevaluate": 5}) for writer in WRITERS):
        raise ValueError("each writer must have five Preserve and five Reevaluate items")
    if any(len(rows) != 2 or len({row["writer_id"] for row in rows}) != 2 for rows in by_pair.values()):
        raise ValueError("every pair must be complete and assigned to different writers")

    expected_forms = {f"writer_{writer}_two_page_final_wjx.txt" for writer in WRITERS}
    if set(manifest["forms"]) != expected_forms:
        raise ValueError("manifest must list exactly the 12 final writer forms")
    form_checks = {}
    for writer_id in WRITERS:
        name = f"writer_{writer_id}_two_page_final_wjx.txt"
        path = PACKET / name
        if sha256_path(path) != manifest["forms"][name]:
            raise ValueError(f"form hash differs from manifest: {name}")
        form_checks[writer_id] = validate_form(writer_id, path, by_writer[writer_id])

    print(
        json.dumps(
            {
                "status": "PASS",
                "packet": str(PACKET),
                "writers": len(WRITERS),
                "instructions": INSTRUCTIONS,
                "pairs": PAIRS,
                "forms": form_checks,
                "collection_gate": "ethics/recruitment checks and real eligibility fields remain required",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
