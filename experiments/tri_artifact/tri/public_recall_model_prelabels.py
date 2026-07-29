from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from tri.end_to_end_decision_decomposition import (
    canonical_json,
    load_jsonl,
    sha256_path,
    sha256_text,
)
from tri.public_recall_calibrated_audit import (
    MODEL_PRELABELERS,
    RUBRIC_FIELDS,
    validate_annotation_return,
)


RUN_VERSION = "TRI-public-recall-model-prelabels-v1"
REPORT_VERSION = "TRI-public-recall-model-prelabel-review-v1"
EVIDENCE_STATUS = "model-assisted provisional labels; never independent-human evidence"
MODEL_IDS = {
    "M1": "Qwen/Qwen3.5-122B-A10B",
    "M2": "Pro/zai-org/GLM-5.1",
    "M3": "deepseek-ai/DeepSeek-V4-Pro",
}
ENDPOINT = "https://api.siliconflow.cn/v1"
RUN_SETTINGS = {
    "temperature": 0.0,
    "max_tokens": 700,
    "timeout_seconds": 180,
    "max_retries": 2,
    "retry_backoff_seconds": 2.0,
    "thinking_parameter": "disabled",
}
SYSTEM_PROMPT = (
    "Audit one public tool-workflow unit against the supplied eight-field TRI opportunity rubric. "
    "Use only source_evidence. Label each field yes, no, or partial; do not infer missing events or "
    "identities. strict_eligible is true only when all eight labels are yes. If false, choose one "
    "non-yes field as primary_exclusion_reason; otherwise use NONE. Confidence is an integer 1-5. "
    "Return one JSON object only with exactly these keys: feature_labels, strict_eligible, "
    "primary_exclusion_reason, confidence, notes."
)


def prompt_hash() -> str:
    return sha256_text(SYSTEM_PROMPT)


def settings_hash() -> str:
    return sha256_text(canonical_json({"endpoint": ENDPOINT, "settings": RUN_SETTINGS}))


def load_packet(packet: Path, packet_manifest: Path, labeler: str) -> list[dict[str, Any]]:
    if labeler not in MODEL_PRELABELERS:
        raise ValueError(f"unknown model prelabeler: {labeler}")
    manifest = json.loads(packet_manifest.read_text(encoding="utf-8"))
    relative = f"model_prelabels/model_prelabel_{labeler}.jsonl"
    if (
        manifest.get("audit_version") != "TRI-public-recall-blind-packets-v4"
        or manifest.get("rows_per_labeler") != 699
        or manifest.get("model_prelabels_are_human_evidence") is not False
        or manifest.get("packet_sha256", {}).get(relative) != sha256_path(packet)
    ):
        raise ValueError("model-prelabel packet manifest validation failed")
    rows = load_jsonl(packet)
    if len(rows) != 699 or len({row.get("blind_unit_id") for row in rows}) != 699:
        raise ValueError("model-prelabel packet must contain 699 unique blind units")
    for row in rows:
        if row.get("labeler_id") != labeler:
            raise ValueError("model-prelabel packet labeler mismatch")
        if tuple(row.get("rubric_fields", ())) != RUBRIC_FIELDS:
            raise ValueError("model-prelabel packet rubric mismatch")
        if row.get("evidence_status") != "model-assisted prelabel; never human evidence":
            raise ValueError("model-prelabel packet evidence boundary mismatch")
    return rows


def actor_payload(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_evidence": task["source_evidence"],
        "rubric_fields": task["rubric_fields"],
        "response_schema": task["response_schema"],
    }


def parse_model_prelabel(text: str, task: dict[str, Any]) -> dict[str, Any]:
    from tri.end_to_end_decision_decomposition import _strict_object

    value = _strict_object(text)
    required = {
        "feature_labels",
        "strict_eligible",
        "primary_exclusion_reason",
        "confidence",
        "notes",
    }
    if set(value) != required:
        raise ValueError(f"schema_error: prelabel keys must be exactly {sorted(required)}")
    return validate_annotation_return(
        {
            **value,
            "labeler_id": task["labeler_id"],
            "blind_unit_id": task["blind_unit_id"],
        },
        task["labeler_id"],
    )


def validate_run_row(
    row: dict[str, Any],
    task: dict[str, Any],
    index: int,
    expected_scope: str,
    expected_packet_sha256: str,
    expected_protocol_sha256: str,
    expected_health_smoke_sha256: str | None,
) -> None:
    if row.get("run_version") != RUN_VERSION or row.get("evidence_status") != EVIDENCE_STATUS:
        raise ValueError("model-prelabel run version or evidence status mismatch")
    labeler = task["labeler_id"]
    if row.get("labeler_id") != labeler or row.get("model") != MODEL_IDS[labeler]:
        raise ValueError("model-prelabel model mapping mismatch")
    if row.get("run_scope") != expected_scope:
        raise ValueError("model-prelabel run scope mismatch")
    if (
        row.get("packet_sha256") != expected_packet_sha256
        or row.get("protocol_sha256") != expected_protocol_sha256
    ):
        raise ValueError("model-prelabel packet or protocol provenance mismatch")
    if row.get("health_smoke_sha256") != expected_health_smoke_sha256:
        raise ValueError("model-prelabel health-smoke provenance mismatch")
    if (
        row.get("task_index") != index
        or row.get("task") != task
        or row.get("task_sha256") != sha256_text(canonical_json(task))
    ):
        raise ValueError("model-prelabel task identity mismatch")
    if row.get("prompt_sha256") != prompt_hash() or row.get("settings_sha256") != settings_hash():
        raise ValueError("model-prelabel prompt or settings mismatch")
    component = row.get("component") or {}
    parsed = component.get("parsed")
    if row.get("complete") != (parsed is not None):
        raise ValueError("model-prelabel completion mismatch")
    attempts = component.get("attempts") or []
    if not attempts or len(attempts) > RUN_SETTINGS["max_retries"] + 1:
        raise ValueError("model-prelabel row requires retained bounded request attempts")
    for attempt_index, attempt in enumerate(attempts):
        if attempt.get("attempt_index") != attempt_index:
            raise ValueError("model-prelabel attempt sequence mismatch")
        if attempt.get("logical_call") != "public_recall_model_prelabel":
            raise ValueError("model-prelabel logical call mismatch")
        request = attempt.get("request") or {}
        messages = request.get("messages") or []
        if (
            set(request) != {
                "model", "messages", "temperature", "max_tokens", "enable_thinking"
            }
            or request.get("model") != MODEL_IDS[labeler]
            or request.get("temperature") != RUN_SETTINGS["temperature"]
            or request.get("max_tokens") != RUN_SETTINGS["max_tokens"]
            or request.get("enable_thinking") is not False
            or len(messages) != 2
            or messages[0] != {"role": "system", "content": SYSTEM_PROMPT}
            or json.loads(messages[1].get("content", "null")) != actor_payload(task)
        ):
            raise ValueError("model-prelabel recorded payload mismatch")
    if parsed is not None:
        if (
            attempts[-1].get("status") != "success"
            or not isinstance(attempts[-1].get("raw_content"), str)
            or component.get("error") is not None
            or component.get("error_kind") is not None
        ):
            raise ValueError("completed model-prelabel row lacks a successful raw response")
        if parse_model_prelabel(attempts[-1]["raw_content"], task) != parsed:
            raise ValueError("model-prelabel parsed output does not match retained raw response")
        validate_annotation_return(parsed, labeler)
        if parsed["blind_unit_id"] != task["blind_unit_id"]:
            raise ValueError("model-prelabel parsed blind ID mismatch")


def validate_run_inventory(
    rows: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    labeler: str,
    expected_scope: str,
    expected_packet_sha256: str,
    expected_protocol_sha256: str,
    expected_health_smoke_sha256: str | None = None,
) -> None:
    if len(rows) != len(tasks):
        raise ValueError(f"expected {len(tasks)} model-prelabel rows, observed {len(rows)}")
    if expected_scope == "smoke":
        expected_health_smoke_sha256 = None
    elif expected_scope == "full" and expected_health_smoke_sha256 is None:
        observed = {row.get("health_smoke_sha256") for row in rows}
        if len(observed) != 1 or None in observed or "" in observed:
            raise ValueError("full model-prelabel run requires one health-smoke hash")
        expected_health_smoke_sha256 = next(iter(observed))
    for index, (row, task) in enumerate(zip(rows, tasks)):
        if task.get("labeler_id") != labeler:
            raise ValueError("model-prelabel inventory labeler mismatch")
        validate_run_row(
            row,
            task,
            index,
            expected_scope,
            expected_packet_sha256,
            expected_protocol_sha256,
            expected_health_smoke_sha256,
        )


def build_review_report(
    runs: dict[str, list[dict[str, Any]]],
    packets: dict[str, list[dict[str, Any]]],
    packet_sha256: dict[str, str],
    protocol_sha256: str,
    health_smoke_sha256: dict[str, str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if set(runs) != set(MODEL_PRELABELERS) or set(packets) != set(MODEL_PRELABELERS):
        raise ValueError("review report requires complete M1-M3 inputs")
    parsed_by_labeler: dict[str, dict[str, dict[str, Any]]] = {}
    task_by_id: dict[str, dict[str, Any]] = {}
    for labeler in MODEL_PRELABELERS:
        validate_run_inventory(
            runs[labeler],
            packets[labeler],
            labeler,
            "full",
            packet_sha256[labeler],
            protocol_sha256,
            health_smoke_sha256[labeler],
        )
        if any(not row["complete"] for row in runs[labeler]):
            raise ValueError(f"{labeler} model-prelabel run contains incomplete rows")
        parsed_by_labeler[labeler] = {
            row["component"]["parsed"]["blind_unit_id"]: row["component"]["parsed"]
            for row in runs[labeler]
        }
        for task in packets[labeler]:
            blind_id = task["blind_unit_id"]
            previous = task_by_id.setdefault(blind_id, task)
            if (
                previous["display_dataset"] != task["display_dataset"]
                or previous["source_evidence"] != task["source_evidence"]
                or previous["rubric_fields"] != task["rubric_fields"]
                or previous["response_schema"] != task["response_schema"]
            ):
                raise ValueError("M1-M3 packets disagree on shared blind-unit content")
    blind_ids = set(task_by_id)
    if len(blind_ids) != 699 or any(set(values) != blind_ids for values in parsed_by_labeler.values()):
        raise ValueError("model-prelabel runs do not cover one shared 699-unit inventory")

    queue = []
    for blind_id in sorted(blind_ids):
        labels = {name: parsed_by_labeler[name][blind_id] for name in MODEL_PRELABELERS}
        positives = sum(item["strict_eligible"] for item in labels.values())
        unanimous = len({item["strict_eligible"] for item in labels.values()}) == 1
        rubric_disagreement_fields = [
            field
            for field in RUBRIC_FIELDS
            if len({item["feature_labels"][field] for item in labels.values()}) > 1
        ]
        mean_confidence = sum(item["confidence"] for item in labels.values()) / 3
        priority = (
            0
            if rubric_disagreement_fields or not unanimous
            else 1
            if positives
            else 2
            if mean_confidence < 4
            else 3
        )
        queue.append(
            {
                "review_priority": priority,
                "blind_unit_id": blind_id,
                "display_dataset": task_by_id[blind_id]["display_dataset"],
                "source_evidence": task_by_id[blind_id]["source_evidence"],
                "model_labels": labels,
                "strict_positive_votes": positives,
                "strict_unanimous": unanimous,
                "rubric_disagreement_fields": rubric_disagreement_fields,
                "rubric_unanimous": not rubric_disagreement_fields,
                "provisional_majority_strict": positives >= 2,
                "mean_model_confidence": mean_confidence,
                "author_qa_strict_eligible": None,
                "author_qa_feature_labels": None,
                "author_qa_notes": None,
                "evidence_allowed": False,
            }
        )
    queue.sort(key=lambda row: (row["review_priority"], row["blind_unit_id"]))
    report = {
        "report_version": REPORT_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "rows": len(queue),
        "strict_vote_histogram": dict(sorted(Counter(row["strict_positive_votes"] for row in queue).items())),
        "unanimous_rows": sum(row["strict_unanimous"] for row in queue),
        "disagreement_rows": sum(not row["strict_unanimous"] for row in queue),
        "rubric_disagreement_rows": sum(not row["rubric_unanimous"] for row in queue),
        "provisional_majority_positive_rows": sum(row["provisional_majority_strict"] for row in queue),
        "author_qa_required": True,
        "author_qa_must_not_overlap_independent_annotators": True,
        "independent_human_evidence": False,
        "prevalence_or_recall_claim_allowed": False,
    }
    return report, queue


def build_incomplete_review_report(
    runs: dict[str, list[dict[str, Any]]],
    packets: dict[str, list[dict[str, Any]]],
    packet_sha256: dict[str, str],
    protocol_sha256: str,
    health_smoke_sha256: dict[str, str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Build a failure-aware QA queue without treating missing model labels as votes."""
    if set(runs) != set(MODEL_PRELABELERS) or set(packets) != set(MODEL_PRELABELERS):
        raise ValueError("partial review report requires complete M1-M3 run files")
    parsed_by_labeler: dict[str, dict[str, dict[str, Any]]] = {}
    task_by_id: dict[str, dict[str, Any]] = {}
    coverage: dict[str, dict[str, int]] = {}
    for labeler in MODEL_PRELABELERS:
        validate_run_inventory(
            runs[labeler],
            packets[labeler],
            labeler,
            "full",
            packet_sha256[labeler],
            protocol_sha256,
            health_smoke_sha256[labeler],
        )
        parsed_by_labeler[labeler] = {
            row["component"]["parsed"]["blind_unit_id"]: row["component"]["parsed"]
            for row in runs[labeler]
            if row["component"].get("parsed") is not None
        }
        coverage[labeler] = {
            "rows": len(runs[labeler]),
            "complete": len(parsed_by_labeler[labeler]),
            "incomplete": len(runs[labeler]) - len(parsed_by_labeler[labeler]),
        }
        for task in packets[labeler]:
            blind_id = task["blind_unit_id"]
            previous = task_by_id.setdefault(blind_id, task)
            if (
                previous["display_dataset"] != task["display_dataset"]
                or previous["source_evidence"] != task["source_evidence"]
                or previous["rubric_fields"] != task["rubric_fields"]
                or previous["response_schema"] != task["response_schema"]
            ):
                raise ValueError("M1-M3 packets disagree on shared blind-unit content")
    if len(task_by_id) != 699:
        raise ValueError("partial review report requires the shared 699-unit inventory")

    queue = []
    for blind_id in sorted(task_by_id):
        labels = {
            labeler: values[blind_id]
            for labeler, values in parsed_by_labeler.items()
            if blind_id in values
        }
        missing = sorted(set(MODEL_PRELABELERS) - set(labels))
        positives = sum(item["strict_eligible"] for item in labels.values())
        complete_panel = not missing
        strict_unanimous = (
            len({item["strict_eligible"] for item in labels.values()}) == 1
            if complete_panel
            else None
        )
        rubric_disagreement_fields = [
            field
            for field in RUBRIC_FIELDS
            if len(
                {
                    item["feature_labels"][field]
                    for item in labels.values()
                }
            )
            > 1
        ]
        mean_confidence = (
            sum(item["confidence"] for item in labels.values()) / len(labels)
            if labels
            else None
        )
        priority = (
            0
            if missing or rubric_disagreement_fields or strict_unanimous is False
            else 1
            if positives
            else 2
            if mean_confidence is not None and mean_confidence < 4
            else 3
        )
        queue.append(
            {
                "review_priority": priority,
                "blind_unit_id": blind_id,
                "display_dataset": task_by_id[blind_id]["display_dataset"],
                "source_evidence": task_by_id[blind_id]["source_evidence"],
                "model_labels": labels,
                "missing_model_labelers": missing,
                "complete_model_panel": complete_panel,
                "strict_positive_votes": positives,
                "strict_unanimous": strict_unanimous,
                "rubric_disagreement_fields": rubric_disagreement_fields,
                "rubric_unanimous": not rubric_disagreement_fields if complete_panel else None,
                "provisional_majority_strict": positives >= 2 if complete_panel else None,
                "mean_model_confidence": mean_confidence,
                "author_qa_strict_eligible": None,
                "author_qa_feature_labels": None,
                "author_qa_notes": None,
                "evidence_allowed": False,
            }
        )
    queue.sort(key=lambda row: (row["review_priority"], row["blind_unit_id"]))
    complete_rows = [row for row in queue if row["complete_model_panel"]]
    report = {
        "report_version": REPORT_VERSION,
        "evidence_status": (
            "incomplete model-prelabel diagnostic for author QA; "
            "no model-consensus or independent-human evidence"
        ),
        "rows": len(queue),
        "model_coverage": coverage,
        "complete_model_panel_rows": len(complete_rows),
        "incomplete_model_panel_rows": len(queue) - len(complete_rows),
        "complete_panel_strict_vote_histogram": dict(
            sorted(Counter(row["strict_positive_votes"] for row in complete_rows).items())
        ),
        "complete_panel_provisional_majority_positive_rows": sum(
            row["provisional_majority_strict"] is True for row in complete_rows
        ),
        "author_qa_required": True,
        "missing_model_labels_are_votes": False,
        "formal_review_report_gate_passed": False,
        "author_qa_must_not_overlap_independent_annotators": True,
        "independent_human_evidence": False,
        "prevalence_or_recall_claim_allowed": False,
    }
    return report, queue


def build_postrun_quality_audit(
    queue: list[dict[str, Any]],
    private_key: list[dict[str, Any]],
    *,
    private_key_sha256: str,
    expected_private_key_sha256: str,
) -> dict[str, Any]:
    """Aggregate blinded model labels by hidden sampling role after all runs finish."""
    if private_key_sha256 != expected_private_key_sha256:
        raise ValueError("private annotation key does not match the frozen manifest hash")
    queue_by_id = {str(row.get("blind_unit_id")): row for row in queue}
    key_by_id = {str(row.get("blind_unit_id")): row for row in private_key}
    if (
        len(queue_by_id) != 699
        or len(key_by_id) != 699
        or set(queue_by_id) != set(key_by_id)
    ):
        raise ValueError("quality audit requires the exact shared 699-unit blind inventory")
    model_quality = {}
    for labeler in MODEL_PRELABELERS:
        available = []
        for blind_id, queue_row in queue_by_id.items():
            label = (queue_row.get("model_labels") or {}).get(labeler)
            if label is not None:
                available.append((label, key_by_id[blind_id]))
        controls = [item for item in available if item[1].get("audit_role") == "injected_control"]
        natural = [item for item in available if item[1].get("audit_role") != "injected_control"]
        positive_controls = [item for item in controls if item[1].get("expected_strict") is True]
        negative_controls = [item for item in controls if item[1].get("expected_strict") is False]
        model_quality[labeler] = {
            "complete": len(available),
            "incomplete": 699 - len(available),
            "strict_positive": sum(item[0]["strict_eligible"] for item in available),
            "natural_strict_positive": sum(item[0]["strict_eligible"] for item in natural),
            "positive_control_correct": sum(item[0]["strict_eligible"] for item in positive_controls),
            "positive_control_available": len(positive_controls),
            "negative_control_correct": sum(not item[0]["strict_eligible"] for item in negative_controls),
            "negative_control_available": len(negative_controls),
        }

    role_summary = {}
    for role in ("retrieved_candidate", "random_non_candidate", "injected_control"):
        rows = [
            queue_by_id[blind_id]
            for blind_id, key_row in key_by_id.items()
            if key_row.get("audit_role") == role
        ]
        complete = [row for row in rows if row.get("complete_model_panel") is True]
        role_summary[role] = {
            "rows": len(rows),
            "complete_model_panels": len(complete),
            "incomplete_model_panels": len(rows) - len(complete),
            "complete_panel_majority_positive": sum(
                row.get("provisional_majority_strict") is True for row in complete
            ),
        }
    positive_controls = [
        queue_by_id[blind_id]
        for blind_id, key_row in key_by_id.items()
        if key_row.get("audit_role") == "injected_control"
        and key_row.get("expected_strict") is True
    ]
    negative_controls = [
        queue_by_id[blind_id]
        for blind_id, key_row in key_by_id.items()
        if key_row.get("audit_role") == "injected_control"
        and key_row.get("expected_strict") is False
    ]
    return {
        "evidence_status": (
            "post-run model-QA diagnostic; not independent-human, prevalence, or recall evidence"
        ),
        "model_quality": model_quality,
        "role_summary": role_summary,
        "complete_panel_positive_control_majority_correct": sum(
            row.get("provisional_majority_strict") is True for row in positive_controls
        ),
        "positive_control_total": len(positive_controls),
        "complete_panel_negative_control_majority_correct": sum(
            row.get("provisional_majority_strict") is False for row in negative_controls
        ),
        "negative_control_total": len(negative_controls),
        "natural_zero_claim_allowed": False,
        "independent_human_evidence": False,
        "prevalence_or_recall_claim_allowed": False,
        "provenance": {
            "private_annotation_key_sha256": private_key_sha256,
            "private_key_in_public_artifact": False,
        },
    }


def build_author_qa_report(
    queue: list[dict[str, Any]], qa_labels: list[dict[str, Any]]
) -> dict[str, Any]:
    queue_by_id = {row["blind_unit_id"]: row for row in queue}
    qa_by_id = {row["blind_unit_id"]: row for row in qa_labels}
    if (
        len(queue_by_id) != len(queue)
        or len(qa_by_id) != len(qa_labels)
        or set(queue_by_id) != set(qa_by_id)
    ):
        raise ValueError("author-QA labels must exactly cover the model review queue")
    for item in qa_labels:
        validate_annotation_return(item, "Q1")
    strict_comparable = [
        blind_id
        for blind_id, row in queue_by_id.items()
        if isinstance(row.get("provisional_majority_strict"), bool)
    ]
    strict_agreement = sum(
        qa_by_id[blind_id]["strict_eligible"]
        == queue_by_id[blind_id]["provisional_majority_strict"]
        for blind_id in strict_comparable
    )
    field_agreement: dict[str, dict[str, int]] = {}
    for field in RUBRIC_FIELDS:
        comparable = 0
        agreed = 0
        for blind_id, queue_row in queue_by_id.items():
            votes = Counter(
                item["feature_labels"][field]
                for item in queue_row["model_labels"].values()
            )
            model_value, count = votes.most_common(1)[0]
            if count >= 2:
                comparable += 1
                agreed += qa_by_id[blind_id]["feature_labels"][field] == model_value
        field_agreement[field] = {"agreed": agreed, "comparable": comparable}
    return {
        "report_version": "TRI-public-recall-author-qa-v1",
        "evidence_status": "author QA of model-assisted labels; not independent-human evidence",
        "rows": len(queue),
        "strict_agreement_with_model_majority": {
            "agreed": strict_agreement,
            "total": len(strict_comparable),
        },
        "missing_model_panel_rows": len(queue) - len(strict_comparable),
        "field_agreement_with_model_majority": field_agreement,
        "author_qa_positive_rows": sum(row["strict_eligible"] for row in qa_labels),
        "independent_human_evidence": False,
        "human_gate_unlocked": False,
        "prevalence_or_recall_claim_allowed": False,
    }
