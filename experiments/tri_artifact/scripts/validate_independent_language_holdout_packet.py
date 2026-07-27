from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from tri.independent_language_holdout import (
    PAIRS,
    WRITERS,
    build_assignments,
    load_jsonl,
    sha256_path,
    validate_assignments,
    validate_pairs,
)


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "human_studies" / "independent_language_holdout_v1"


def main() -> None:
    pairs = load_jsonl(PACKET / "private_scenario_key.jsonl")
    validate_pairs(pairs)
    assignments = build_assignments(pairs)
    validate_assignments(assignments)
    for writer in WRITERS:
        for batch in (1, 2):
            stage_a = (PACKET / f"writer_{writer}_stage_a_part_{batch}_wjx.txt").read_text(
                encoding="utf-8"
            )
            stage_b = (PACKET / f"writer_{writer}_stage_b_part_{batch}_wjx.txt").read_text(
                encoding="utf-8"
            )
            assert stage_a.count("[填空题]") == 10
            assert len(re.findall(r"【情境 \d{2}｜IH-[A-Z]+-\d{2}-[PR]】", stage_a)) == 10
            assert stage_a.count("当前可见记录：") == 10
            assert "同步后的记录：" not in stage_a
            assert "pre_refresh_target" not in stage_a and "post_refresh_target" not in stage_a
            assert stage_b.count("你在已提交的英文请求中打算操作哪个对象") == 10
            assert stage_b.count("你对这个意图判断有多确定") == 10
            assert len(re.findall(r"【意图判断 \d{2}｜IH-[A-Z]+-\d{2}-[PR]】", stage_b)) == 10
            assert "writer_intent" not in stage_b
        combined = (PACKET / f"writer_{writer}_combined_wjx.txt").read_text(
            encoding="utf-8"
        )
        assert combined.count("[填空题]") == 20
        assert combined.count("根据这条原句，你原本打算操作哪个对象") == 20
        assert combined.count("你对这个意图判断有多确定") == 20
        assert combined.count("[分页栏]") == 7
        assert combined.index("【B 阶段｜第 1/4 页】") > combined.rindex("[填空题]")
        assert "负责人" not in combined and "可执行" not in combined
        assert all(combined.count(f"[q{question}]") == 1 for question in range(4, 24))

    allocation = Counter(row["writer_id"] for row in assignments)
    assert allocation == Counter({writer: 20 for writer in WRITERS})
    manifest = json.loads((PACKET / "freeze_manifest.json").read_text(encoding="utf-8"))
    assert manifest["pairs"] == PAIRS and manifest["instructions"] == 2 * PAIRS
    for name, digest in manifest["files"].items():
        assert sha256_path(PACKET / name) == digest
    print("PASS: 6 writers; split and combined WJX forms; 60 disjoint pairs")


if __name__ == "__main__":
    main()
