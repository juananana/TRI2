#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tri.model_authored_linguistic_stress import (
    AUTHOR_SYSTEM_PROMPT,
    JUDGE_SYSTEM_PROMPT,
    build_semantic_specs,
    build_tasks,
    jsonl_bytes,
    load_jsonl,
    sha256_bytes,
    sha256_path,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPECS = ROOT / "data/model_authored_linguistic_semantics_v1.jsonl"
DEFAULT_AUTHORING = ROOT / "runs/model_authored_linguistic_author_full_v1.jsonl"
DEFAULT_TASKS = ROOT / "data/model_authored_linguistic_stress_v1.jsonl"
DEFAULT_PROTOCOL = ROOT / "reports/TRI_model_authored_linguistic_stress_protocol.md"
DEFAULT_MANIFEST = ROOT / "reports/model_authored_linguistic_stress_freeze_manifest_v1.json"
RUN_MODELS = ROOT / "tri/run_models.py"
RULE = ROOT / "tri/deterministic_discourse_rule_v2.py"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("semantics", "tasks"), required=True)
    parser.add_argument("--specs", type=Path, default=DEFAULT_SPECS)
    parser.add_argument("--authoring", type=Path, default=DEFAULT_AUTHORING)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    if args.stage == "semantics":
        rows = build_semantic_specs()
        args.specs.write_bytes(jsonl_bytes(rows))
        output = args.specs
    else:
        rows = build_tasks(load_jsonl(args.specs), load_jsonl(args.authoring))
        args.tasks.write_bytes(jsonl_bytes(rows))
        output = args.tasks
        manifest = {
            "evidence_status": "post-primary model-authored linguistic stress test",
            "freeze_stage": "after_model_authoring_before_judging_or_controller_evaluation",
            "semantic_specs": {"path": str(args.specs.relative_to(ROOT)), "sha256": sha256_path(args.specs), "rows": 24},
            "authoring_run": {"path": str(args.authoring.relative_to(ROOT)), "sha256": sha256_path(args.authoring), "rows": 24},
            "task_inventory": {"path": str(args.tasks.relative_to(ROOT)), "sha256": sha256_path(args.tasks), "rows": 48, "pairs": 24},
            "protocol": {"path": str(args.protocol.relative_to(ROOT)), "sha256": sha256_path(args.protocol)},
            "prompts": {
                "author_sha256": sha256_bytes(AUTHOR_SYSTEM_PROMPT.encode("utf-8")),
                "judge_sha256": sha256_bytes(JUDGE_SYSTEM_PROMPT.encode("utf-8")),
            },
            "frozen_implementations": {
                "controllers_sha256": sha256_path(RUN_MODELS),
                "rule_v2_sha256": sha256_path(RULE),
            },
            "generation_valid_rows": sum(row["generation_valid"] for row in rows),
            "generation_failed_rows": sum(not row["generation_valid"] for row in rows),
        }
        args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print({"output": str(output), "rows": len(rows), "sha256": sha256_path(output)})


if __name__ == "__main__":
    main()
