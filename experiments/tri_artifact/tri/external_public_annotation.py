"""Build frozen, redacted annotation payloads from external public datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SENSITIVE_KEY_PARTS = ("api_key", "credential", "password", "secret", "session_token", "token")


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                redacted[str(key)] = "<REDACTED>"
            else:
                redacted[str(key)] = redact_sensitive(item)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _bfcl_base_by_id(root: Path) -> dict[str, dict[str, Any]]:
    path = (
        root
        / "berkeley-function-call-leaderboard"
        / "bfcl_eval"
        / "data"
        / "BFCL_v4_multi_turn_base.json"
    )
    return {str(row["id"]): row for row in _read_jsonl(path)}


def build_annotation_candidates(
    audit_records_path: Path,
    bfcl_root: Path,
    tooltalk_root: Path,
) -> list[dict[str, Any]]:
    audit_records = _read_jsonl(audit_records_path)
    bfcl_base = _bfcl_base_by_id(bfcl_root)
    candidates: list[dict[str, Any]] = []

    for record in audit_records:
        if not record.get("source_anchored_eligible"):
            continue
        dataset = record["dataset"]
        if dataset == "BFCL":
            if record.get("variant") != "base":
                continue
            raw = bfcl_base[record["unit_id"]]
            eligible_classes = record.get("eligible_classes", [])
            state_by_class = {
                class_name: redact_sensitive(raw.get("initial_config", {}).get(class_name, {}))
                for class_name in eligible_classes
            }
            source_payload = {
                "questions": [
                    [
                        {"role": message.get("role"), "content": message.get("content")}
                        for message in turn
                    ]
                    for turn in raw.get("question", [])
                ],
                "tool_sequence": raw.get("path", []),
                "eligible_classes": eligible_classes,
                "state_by_class": state_by_class,
            }
        elif dataset == "ToolTalk":
            path = tooltalk_root / record["source_path"]
            raw = json.loads(path.read_text(encoding="utf-8"))
            source_payload = {
                "scenario": raw.get("scenario"),
                "conversation": redact_sensitive(raw.get("conversation", [])),
                "tool_sequence": record.get("tool_sequence", []),
            }
        else:
            continue

        candidates.append(
            {
                "candidate_id": f"{dataset}:{record['cluster_id']}",
                "dataset": dataset,
                "unit_id": record["unit_id"],
                "cluster_id": record["cluster_id"],
                "source_path": record["source_path"],
                "source_unit_sha256": record["source_unit_sha256"],
                "deterministic_flags": {
                    "query_before_mutation": record["query_before_mutation"],
                    "exact_id_linkage": record["exact_id_linkage"],
                    "native_update_language": record["native_update_language"],
                    "timing_label": record["timing_label"],
                    "stable_id_keys": record["stable_id_keys"],
                },
                "source_payload": source_payload,
            }
        )

    candidates.sort(key=lambda row: (row["dataset"], row["cluster_id"]))
    seen = {row["candidate_id"] for row in candidates}
    assert len(seen) == len(candidates)
    return candidates
