from __future__ import annotations

from pathlib import Path

from tri.revision_matched_audit import load_jsonl
from tri.revision_repeat_stability import build_repeat_report


ROOT = Path(__file__).resolve().parents[1]


def test_identical_source_passes_have_exact_target_agreement_without_inflating_pairs():
    rows = load_jsonl(ROOT / "runs" / "revision_source_grounded_qwen_full_v1.jsonl")
    report = build_repeat_report(
        [("historical", rows)], [("repeat-copy", rows)], samples=100
    )
    assert len(report["passes"]) == 2
    assert all(item["clusters"] == 30 for item in report["passes"])
    agreement = report["target_agreement"][0]["conditions"]
    assert all(metric == {"numerator": 60, "denominator": 60, "rate": 1.0} for metric in agreement.values())

