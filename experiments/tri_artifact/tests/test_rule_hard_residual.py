from pathlib import Path

from tri.rule_hard_residual import build_report


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


def test_rule_hard_residual_retains_negative_and_zero_results() -> None:
    report = build_report(
        RUNS / "deterministic_discourse_rule_v2_v7.jsonl",
        {
            "Qwen / Timing-reminder": RUNS / "v7_qwen_full_history_once_matched_full_v1.jsonl",
            "Qwen / CTA": RUNS / "v7_qwen_compile_then_act_full.jsonl",
            "GLM / Timing-reminder": RUNS / "v7_glm_full_history_once_matched_full_v1.jsonl",
            "GLM / CTA": RUNS / "v7_glm_compile_then_act_full.jsonl",
            "DeepSeek / Timing-reminder": RUNS / "v7_deepseek_full_history_once_matched_full_v1.jsonl",
            "DeepSeek / CTA": RUNS / "v7_deepseek_compile_then_act_full_v1.jsonl",
        },
    )
    assert report["rule_hard_rows"] == 20
    assert report["preserve_rows"] == report["reevaluate_rows"] == 10
    assert report["complete_rule_hard_pairs"] == 0
    assert report["results"]["Qwen / Timing-reminder"]["correct"] == 13
    assert report["results"]["Qwen / CTA"]["correct"] == 13
    assert report["results"]["GLM / Timing-reminder"]["correct"] == 20
    assert report["results"]["GLM / CTA"]["correct"] == 20
    assert report["results"]["DeepSeek / Timing-reminder"]["correct"] == 18
    assert report["results"]["DeepSeek / CTA"]["correct"] == 16
