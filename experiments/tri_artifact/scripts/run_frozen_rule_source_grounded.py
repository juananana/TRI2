#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from tri.deterministic_discourse_rule_v2 import predict_task_v2
from tri.revision_matched_audit import load_jsonl, sha256_path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reports" / "revision_matched_audits_manifest_v1.json"
TASKS = ROOT / "data" / "revision_source_grounded_v1.jsonl"
RAW = ROOT / "runs" / "revision_source_grounded_rule_star_frozen_v1.jsonl"
JSON_REPORT = ROOT / "reports" / "revision_source_grounded_rule_star_frozen_v1.json"
MD_REPORT = ROOT / "reports" / "revision_source_grounded_rule_star_frozen_v1.md"


def write_frozen(path: Path, payload: bytes) -> None:
    if path.exists() and path.read_bytes() != payload:
        raise SystemExit(f"Refusing to overwrite different frozen Rule* output: {path}")
    path.write_bytes(payload)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if sha256_path(ROOT / "tri" / "deterministic_discourse_rule_v2.py") != manifest["frozen_rule_star_sha256"]:
        raise SystemExit("Rule* source changed after the revision freeze")
    if sha256_path(TASKS) != manifest["inventories"]["source_grounded"]["sha256"]:
        raise SystemExit("source-grounded inventory changed after the revision freeze")
    tasks = load_jsonl(TASKS)
    rows = []
    for task in tasks:
        prediction = predict_task_v2(task)
        rows.append(
            {
                "run_version": "TRI-frozen-rule-source-grounded-v1",
                "evidence_status": "post-hoc Rule* frozen before this source-grounded application",
                "rule_sha256": manifest["frozen_rule_star_sha256"],
                "task_file_sha256": manifest["inventories"]["source_grounded"]["sha256"],
                "task": task,
                "prediction": prediction,
                "correct": prediction["predicted_target"] == task["correct_target"],
            }
        )
    by_pair = defaultdict(list)
    for row in rows:
        by_pair[row["task"]["pair_id"]].append(row)
    pair_correct = {
        pair_id: len(pair) == 2 and all(row["correct"] for row in pair)
        for pair_id, pair in by_pair.items()
    }
    by_source = {}
    for source in sorted({row["task"]["source"] for row in rows}):
        subset = [row for row in rows if row["task"]["source"] == source]
        pair_ids = {row["task"]["pair_id"] for row in subset}
        by_source[source] = {
            "row_accuracy": [sum(row["correct"] for row in subset), len(subset)],
            "pairacc": [sum(pair_correct[pair_id] for pair_id in pair_ids), len(pair_ids)],
            "errors": dict(sorted(Counter(row["prediction"]["error"] or "wrong_target" for row in subset if not row["correct"]).items())),
        }
    report = {
        "report_version": "TRI-frozen-rule-source-grounded-report-v1",
        "evidence_status": "post-hoc Rule* frozen before this source-grounded application",
        "rows": len(rows),
        "row_accuracy": [sum(row["correct"] for row in rows), len(rows)],
        "pairacc": [sum(pair_correct.values()), len(pair_correct)],
        "by_source": by_source,
        "rule_sha256": manifest["frozen_rule_star_sha256"],
        "task_file_sha256": manifest["inventories"]["source_grounded"]["sha256"],
        "boundary": "The rule is post-hoc to authored TRI analyses but byte-frozen before this source-grounded application.",
    }
    raw_payload = ("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n").encode("utf-8")
    write_frozen(RAW, raw_payload)
    write_frozen(JSON_REPORT, (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    lines = [
        "# Frozen Rule* on Source-Grounded Contrasts",
        "",
        f"Rows correct: {report['row_accuracy'][0]}/{report['row_accuracy'][1]}.",
        f"PairAcc: {report['pairacc'][0]}/{report['pairacc'][1]}.",
        "",
        "| Source | Row accuracy | PairAcc | Errors |",
        "|---|---:|---:|---|",
    ]
    for source, values in by_source.items():
        lines.append(
            f"| {source} | {values['row_accuracy'][0]}/{values['row_accuracy'][1]} | "
            f"{values['pairacc'][0]}/{values['pairacc'][1]} | {values['errors']} |"
        )
    lines.extend(["", report["boundary"], ""])
    write_frozen(MD_REPORT, "\n".join(lines).encode("utf-8"))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
