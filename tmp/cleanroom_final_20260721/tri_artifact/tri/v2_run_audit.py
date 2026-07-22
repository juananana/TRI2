from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def is_internal_api_error(row: dict[str, Any]) -> bool:
    if row.get("status") != "ok":
        return False
    result = row.get("result", {})
    errors = [str(err) for err in result.get("errors", [])]
    if any(
        "HTTP Error" in err
        or "URLError" in err
        or "timed out" in err.lower()
        or err.startswith("api_call_error:")
        for err in errors
    ):
        return True
    return bool(errors) and not result.get("raw_outputs") and result.get("predicted_target") is None


def audit_file(path: Path, expected_ids: set[str]) -> dict[str, Any]:
    rows = load_jsonl(path)
    ids = [row.get("task", {}).get("id") for row in rows if row.get("task")]
    id_counts = Counter(ids)
    duplicates = sorted([task_id for task_id, count in id_counts.items() if count > 1])
    seen = set(ids)
    missing = sorted(expected_ids - seen)
    extra = sorted(seen - expected_ids)
    status_counts = Counter(
        "api_internal_error" if is_internal_api_error(row) else row.get("status", "missing")
        for row in rows
    )
    internal_error_counts = Counter(
        str(err)
        for row in rows
        if is_internal_api_error(row)
        for err in row.get("result", {}).get("errors", [])
    )
    success = sum(
        1
        for row in rows
        if row.get("status") == "ok"
        and not is_internal_api_error(row)
        and row.get("result", {}).get("success")
    )
    model = rows[0].get("model") if rows else None
    mode = rows[0].get("result", {}).get("mode") if rows else None
    return {
        "file": str(path),
        "model": model,
        "mode": mode,
        "n_rows": len(rows),
        "n_expected": len(expected_ids),
        "complete": seen == expected_ids and not duplicates,
        "n_missing": len(missing),
        "n_extra": len(extra),
        "n_duplicates": len(duplicates),
        "status_counts": dict(status_counts),
        "internal_error_counts": dict(internal_error_counts),
        "success_count": success,
        "accuracy_if_complete_rows": success / len(rows) if rows else None,
        "missing_first10": missing[:10],
        "extra_first10": extra[:10],
        "duplicates_first10": duplicates[:10],
        "first_task": ids[0] if ids else None,
        "last_task": ids[-1] if ids else None,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# TRI Run Audit",
        "",
        "| File | Model | Mode | Rows | Complete | Missing | Extra | Duplicates | Status |",
        "|---|---|---|---:|---|---:|---:|---:|---|",
    ]
    for row in report["files"]:
        name = Path(row["file"]).name
        lines.append(
            f"| {name} | {row['model']} | {row['mode']} | {row['n_rows']}/{row['n_expected']} | "
            f"{row['complete']} | {row['n_missing']} | {row['n_extra']} | {row['n_duplicates']} | "
            f"{row['status_counts']} |"
        )
        if row["n_missing"]:
            lines.append(f"| missing |  |  |  |  | {', '.join(row['missing_first10'])} |  |  |  |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(DATA / "temporal_referent_v2_api_scalar.jsonl"))
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--output", default=str(REPORTS / "v2_run_audit.json"))
    args = ap.parse_args()
    expected = {row["id"] for row in load_jsonl(Path(args.data))}
    report = {
        "data": args.data,
        "n_expected": len(expected),
        "files": [audit_file(Path(p), expected) for p in args.input],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(markdown(report))


if __name__ == "__main__":
    main()
