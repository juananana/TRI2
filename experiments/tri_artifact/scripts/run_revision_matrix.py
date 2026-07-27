#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.run_revision_matched_audit import MODEL_IDS, load_frozen, validate_smoke
from tri.revision_matched_audit import load_jsonl, validate_run_row


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT.parents[1] / ".venv-toolsandbox" / "bin" / "python"
MATRIX = {
    "full_diagnostic": ("qwen", "glm"),
    "human_rewrite": ("qwen", "glm"),
    "source_grounded": ("qwen", "glm", "deepseek"),
}


def output_path(audit: str, model: str, stage: str) -> Path:
    return ROOT / "runs" / f"revision_{audit}_{model}_{stage.replace('-', '_')}_v1.jsonl"


def validate_existing(path: Path, audit: str, model: str, stage: str) -> bool:
    tasks, _, _ = load_frozen(audit)
    rows = load_jsonl(path)
    expected = 4 if stage == "health-smoke" else len(tasks)
    selected = tasks[:expected]
    if len(rows) > expected or any(row.get("model") != MODEL_IDS[model] for row in rows):
        raise ValueError(f"existing output has the wrong scope: {path}")
    if [row.get("task", {}).get("id") for row in rows] != [
        task["id"] for task in selected[: len(rows)]
    ]:
        raise ValueError(f"existing output is not the ordered frozen prefix: {path}")
    if len(rows) < expected:
        for row in rows:
            validate_run_row(row, require_complete=True)
        return False
    if stage == "health-smoke":
        validate_smoke(rows, tasks, MODEL_IDS[model])
    else:
        for row in rows:
            validate_run_row(row)
    return True


def run_stage(audit: str, model: str, stage: str, smoke: Path | None = None) -> Path:
    output = output_path(audit, model, stage)
    if output.exists():
        if validate_existing(output, audit, model, stage):
            print(f"validated existing {output.relative_to(ROOT)}", flush=True)
            return output
        print(f"resuming validated prefix {output.relative_to(ROOT)}", flush=True)
    command = [
        str(PYTHON),
        "scripts/run_revision_matched_audit.py",
        "--audit",
        audit,
        "--model",
        model,
        "--stage",
        stage,
        "--output",
        str(output),
    ]
    if smoke is not None:
        command.extend(["--health-smoke", str(smoke)])
    if output.exists():
        command.append("--resume")
    subprocess.run(command, cwd=ROOT, env={**os.environ, "PYTHONPATH": ".", "PYTHONDONTWRITEBYTECODE": "1"}, check=True)
    if not validate_existing(output, audit, model, stage):
        raise ValueError(f"run did not complete the frozen scope: {output}")
    return output


def main() -> None:
    if not (os.environ.get("LLM_API_KEY") or os.environ.get("SILICONFLOW_API_KEY")):
        raise SystemExit("Set LLM_API_KEY or SILICONFLOW_API_KEY before starting the matrix.")
    for audit, models in MATRIX.items():
        full_outputs = []
        for model in models:
            smoke = run_stage(audit, model, "health-smoke")
            full_outputs.append(run_stage(audit, model, "full", smoke))
        subprocess.run(
            [
                str(PYTHON),
                "scripts/report_revision_matched_audit.py",
                "--audit",
                audit,
                *[str(path) for path in full_outputs],
            ],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": ".", "PYTHONDONTWRITEBYTECODE": "1"},
            check=True,
        )


if __name__ == "__main__":
    main()
