from __future__ import annotations

import json
from pathlib import Path

from tri.independent_holdout_model_experiment import freeze_prompt_hash
from tri.independent_language_holdout import load_jsonl, sha256_path, validate_model_tasks


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "independent_language_holdout_v1.jsonl"
PROTOCOL = ROOT / "reports" / "TRI_independent_language_holdout_protocol.md"
OUTPUT = ROOT / "reports" / "independent_language_holdout_model_freeze_v1.json"
IMPLEMENTATIONS = (
    ROOT / "tri" / "independent_language_holdout.py",
    ROOT / "tri" / "independent_holdout_model_experiment.py",
    ROOT / "tri" / "deterministic_discourse_rule_v2.py",
    ROOT / "scripts" / "run_independent_holdout_model_experiment.py",
)


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite {OUTPUT}")
    if not TASKS.exists():
        raise SystemExit("Human-authored model tasks do not exist yet")
    tasks = load_jsonl(TASKS)
    validate_model_tasks(tasks)
    manifest = {
        "manifest_version": "TRI-independent-language-holdout-model-freeze-v1",
        "evidence_status": "planned/unverified before model calls",
        "task_path": str(TASKS.relative_to(ROOT)),
        "task_sha256": sha256_path(TASKS),
        "rows": len(tasks),
        "pairs": len({row["pair_id"] for row in tasks}),
        "clear_complete_pairs": len(
            {row["pair_id"] for row in tasks if row["clear_complete_pair"]}
        ),
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": sha256_path(PROTOCOL),
        "prompt_sha256": freeze_prompt_hash(),
        "implementation_sha256": {
            str(path.relative_to(ROOT)): sha256_path(path) for path in IMPLEMENTATIONS
        },
        "models": [
            "Qwen/Qwen3.5-122B-A10B",
            "Pro/zai-org/GLM-5.1",
            "deepseek-ai/DeepSeek-V4-Pro",
        ],
        "primary_conditions": ["history_only", "decision_visible"],
        "secondary_conditions": ["timing_reminder", "cta", "rule_star"],
        "stopping_rule": "health smoke must have four complete rows; full retains every attempted row",
        "retry_rule": "two retries; API, transport, parse, and incomplete outputs count as ITT errors",
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
