from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


FORMS = tuple("ABCDEF")
LABELS_PER_ITEM = 5
ITEMS_PER_FORM = 12
EVIDENCE_STATUS = "post-primary human construct audit"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def load_key(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    required = {
        "public_item_id",
        "source_task_id",
        "form",
        "position",
        "category",
        "discourse_referent_gold",
        "execution_gold",
    }
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"answer key is missing columns: {sorted(required - set(rows[0] if rows else {}))}")
    if len(rows) != 72 or Counter(row["form"] for row in rows) != Counter({form: 12 for form in FORMS}):
        raise ValueError("answer key must contain 12 unique items for each of six forms")
    if len({row["public_item_id"] for row in rows}) != 72:
        raise ValueError("answer key item IDs are not unique")
    return rows


def load_allocation(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv(path)
    allocation = {row["participant_code"]: row for row in rows}
    if len(allocation) != 36:
        raise ValueError("allocation must contain 30 primary and six reserve codes")
    if Counter(row["valid_status"] for row in rows) != Counter({"primary": 30, "reserve": 6}):
        raise ValueError("allocation role counts differ from the frozen design")
    return allocation


def _question_number(header: str) -> int | None:
    match = re.match(r"\s*(\d{1,2})\s*[.、:：]", header)
    return int(match.group(1)) if match else None


def _yes(value: str) -> bool:
    value = value.strip().lower()
    return value in {"yes", "y", "true", "1", "是"} or value.startswith("我已阅读")


def _no(value: str) -> bool:
    return value.strip().lower() in {"no", "n", "false", "0", "否", "没有"}


def _referent(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    if "无法唯一确定" in value or value.upper() in {"AMBIGUOUS", "CLARIFY"}:
        return "AMBIGUOUS"
    match = re.search(r"(?:对象\s*)?([A-Za-z][A-Za-z0-9_-]*-\d+[A-Za-z0-9_-]*)", value)
    return match.group(1) if match else value


def _execution(value: str) -> str | None:
    value = value.strip()
    if not value:
        return None
    if "拒绝" in value or value.upper() == "REJECT":
        return "REJECT"
    if "澄清" in value or value.upper() == "CLARIFY":
        return "CLARIFY"
    match = re.search(r"(?:执行\s*)?([A-Za-z][A-Za-z0-9_-]*-\d+[A-Za-z0-9_-]*)", value)
    return match.group(1) if match else value


def _confidence(value: str) -> int | None:
    if not value.strip():
        return None
    digits = re.findall(r"[1-5]", value)
    return int(digits[-1]) if digits else None


def normalize_export_row(
    raw: dict[str, str],
    *,
    key_rows: list[dict[str, str]],
    allocation: dict[str, dict[str, str]],
    participant_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    participant_map = participant_map or {}
    participant_code = raw.get("participant_code", "").strip()
    if not participant_code:
        response_id = raw.get("response_id") or raw.get("答卷编号") or raw.get("序号") or ""
        participant_code = participant_map.get(str(response_id).strip(), "")
    if participant_code not in allocation:
        raise ValueError(f"unassigned participant code: {participant_code or '<missing>'}")
    assigned = allocation[participant_code]
    form = (raw.get("form") or assigned["form"]).strip().upper()
    if form != assigned["form"]:
        raise ValueError(f"participant {participant_code} submitted the wrong form")

    numbered = {_question_number(key): value for key, value in raw.items() if _question_number(key)}
    submitted = (
        raw.get("submitted_at")
        or raw.get("提交答卷时间")
        or raw.get("提交时间")
        or raw.get("开始时间")
        or ""
    )
    items = sorted((row for row in key_rows if row["form"] == form), key=lambda row: int(row["position"]))
    responses: dict[str, dict[str, Any]] = {}
    for offset, item in enumerate(items):
        base = 4 + 3 * offset
        item_id = item["public_item_id"]
        responses[item_id] = {
            "referent": _referent(raw.get(f"{item_id}_referent", "") or numbered.get(base, "")),
            "execution": _execution(raw.get(f"{item_id}_execution", "") or numbered.get(base + 1, "")),
            "confidence": _confidence(raw.get(f"{item_id}_confidence", "") or numbered.get(base + 2, "")),
        }
    return {
        "participant_code": participant_code,
        "form": form,
        "allocation_role": assigned["valid_status"],
        "submitted_at": submitted,
        "age_18": _yes(raw.get("age_18", "") or numbered.get(1, "")),
        "english_independent": _yes(raw.get("english_independent", "") or numbered.get(2, "")),
        "consent": _yes(raw.get("consent", "") or numbered.get(3, "")),
        "used_assistance": not _no(raw.get("used_assistance", "") or numbered.get(40, "")),
        "technical_issue": not _no(raw.get("technical_issue", "") or numbered.get(41, "")),
        "end_check_complete": bool(raw.get("english_difficulty", "") or numbered.get(42, "")),
        "responses": responses,
    }


def is_valid_submission(row: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons = []
    for field in ("age_18", "english_independent", "consent", "end_check_complete"):
        if not row[field]:
            reasons.append(field)
    if row["used_assistance"]:
        reasons.append("used_assistance")
    if row["technical_issue"]:
        reasons.append("technical_issue")
    if any(
        answer["referent"] is None
        or answer["execution"] is None
        or answer["confidence"] is None
        for answer in row["responses"].values()
    ):
        reasons.append("incomplete_items")
    return not reasons, reasons


def _time_key(value: str) -> tuple[int, str]:
    if not value:
        return (1, "")
    try:
        return (0, datetime.fromisoformat(value.replace("/", "-")).isoformat())
    except ValueError:
        return (0, value)


def select_frozen_sample(rows: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = list(rows)
    selected: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    for form in FORMS:
        form_rows = sorted(
            (row for row in rows if row["form"] == form),
            key=lambda row: (_time_key(row["submitted_at"]), row["participant_code"]),
        )
        valid_primary = []
        valid_reserve = []
        seen_codes = set()
        for row in form_rows:
            if row["participant_code"] in seen_codes:
                raise ValueError(f"duplicate submission for {row['participant_code']}")
            seen_codes.add(row["participant_code"])
            valid, reasons = is_valid_submission(row)
            ledger.append(
                {
                    "participant_code": row["participant_code"],
                    "form": form,
                    "allocation_role": row["allocation_role"],
                    "valid": valid,
                    "exclusion_reasons": reasons,
                }
            )
            if valid and row["allocation_role"] == "primary":
                valid_primary.append(row)
            elif valid and row["allocation_role"] == "reserve":
                valid_reserve.append(row)
        chosen = valid_primary[:5]
        chosen.extend(valid_reserve[: 5 - len(chosen)])
        if len(chosen) != 5:
            raise ValueError(f"form {form} has only {len(chosen)} valid submissions")
        selected.extend(chosen)
    return selected, ledger


def _majority(labels: list[str]) -> str | None:
    counts = Counter(labels)
    label, count = counts.most_common(1)[0]
    if count < math.floor(len(labels) / 2) + 1:
        return None
    if sum(value == count for value in counts.values()) > 1:
        return None
    return label


def fleiss_kappa(label_sets: list[list[str]]) -> float:
    if not label_sets or len({len(labels) for labels in label_sets}) != 1:
        raise ValueError("Fleiss kappa requires a nonempty fixed-label matrix")
    n = len(label_sets[0])
    categories = sorted({label for labels in label_sets for label in labels})
    totals = Counter(label for labels in label_sets for label in labels)
    p_bar = sum(
        sum(count * count for count in Counter(labels).values()) - n
        for labels in label_sets
    ) / (len(label_sets) * n * (n - 1))
    p_e = sum((totals[label] / (len(label_sets) * n)) ** 2 for label in categories)
    return (p_bar - p_e) / (1 - p_e) if p_e < 1 else 1.0


def krippendorff_alpha_nominal(label_sets: list[list[str]]) -> float:
    values = [label for labels in label_sets for label in labels]
    if not values:
        raise ValueError("alpha requires labels")
    observed_disagreement = sum(
        sum(a != b for i, a in enumerate(labels) for b in labels[i + 1 :])
        / (len(labels) * (len(labels) - 1) / 2)
        for labels in label_sets
    ) / len(label_sets)
    counts = Counter(values)
    total = len(values)
    expected_disagreement = 1 - sum((count / total) ** 2 for count in counts.values())
    return 1 - observed_disagreement / expected_disagreement if expected_disagreement else 1.0


def _pair_id(source_task_id: str) -> str:
    return re.sub(r"-(explicit|implicit)_(anchor|dynamic)-", r"-\1_MODE-", source_task_id)


def analyze(selected: list[dict[str, Any]], key_rows: list[dict[str, str]]) -> dict[str, Any]:
    if len(selected) != 30:
        raise ValueError("analysis requires exactly 30 selected participants")
    key = {row["public_item_id"]: row for row in key_rows}
    labels: dict[str, dict[str, list[Any]]] = {
        item_id: {"referent": [], "execution": [], "confidence": []} for item_id in key
    }
    for participant in selected:
        expected = {item_id for item_id, item in key.items() if item["form"] == participant["form"]}
        if set(participant["responses"]) != expected:
            raise ValueError(f"form {participant['form']} item set differs from the frozen key")
        for item_id, answers in participant["responses"].items():
            for field in labels[item_id]:
                labels[item_id][field].append(answers[field])
    if any(len(values[field]) != LABELS_PER_ITEM for values in labels.values() for field in values):
        raise ValueError("every item must have exactly five labels")

    item_results = []
    for item_id, item_labels in labels.items():
        item = key[item_id]
        referent_majority = _majority(item_labels["referent"])
        execution_majority = _majority(item_labels["execution"])
        item_results.append(
            {
                "public_item_id": item_id,
                "source_task_id": item["source_task_id"],
                "form": item["form"],
                "category": item["category"],
                "pair_id": _pair_id(item["source_task_id"]) if item["category"] == "changed" else None,
                "referent_gold": item["discourse_referent_gold"],
                "execution_gold": item["execution_gold"],
                "referent_labels": item_labels["referent"],
                "execution_labels": item_labels["execution"],
                "confidence_labels": item_labels["confidence"],
                "referent_majority": referent_majority,
                "execution_majority": execution_majority,
                "referent_majority_gold": referent_majority == item["discourse_referent_gold"],
                "execution_majority_gold": execution_majority == item["execution_gold"],
                "referent_unanimous": len(set(item_labels["referent"])) == 1,
                "execution_unanimous": len(set(item_labels["execution"])) == 1,
                "identity_correct_execution_disagrees": (
                    referent_majority == item["discourse_referent_gold"]
                    and execution_majority != item["execution_gold"]
                ),
            }
        )

    changed = [row for row in item_results if row["category"] == "changed"]
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in changed:
        by_pair[row["pair_id"]].append(row)
    if len(by_pair) != 18 or any(len(rows) != 2 for rows in by_pair.values()):
        raise ValueError("changed slice must contain 18 complete matched pairs")

    execution_counts = Counter(row["execution_majority"] or "NO_MAJORITY" for row in item_results)
    return {
        "evidence_status": EVIDENCE_STATUS,
        "participants": len(selected),
        "items": len(item_results),
        "labels_per_item": LABELS_PER_ITEM,
        "complete_changed_pairs": len(by_pair),
        "referent": {
            "majority_gold": sum(row["referent_majority_gold"] for row in item_results),
            "unanimous": sum(row["referent_unanimous"] for row in item_results),
            "fleiss_kappa": fleiss_kappa([row["referent_labels"] for row in item_results]),
            "krippendorff_alpha": krippendorff_alpha_nominal(
                [row["referent_labels"] for row in item_results]
            ),
            "pair_majority_correct": sum(
                all(row["referent_majority_gold"] for row in rows) for rows in by_pair.values()
            ),
            "pair_denominator": len(by_pair),
        },
        "execution": {
            "majority_gold": sum(row["execution_majority_gold"] for row in item_results),
            "unanimous": sum(row["execution_unanimous"] for row in item_results),
            "fleiss_kappa": fleiss_kappa([row["execution_labels"] for row in item_results]),
            "krippendorff_alpha": krippendorff_alpha_nominal(
                [row["execution_labels"] for row in item_results]
            ),
            "majority_distribution": dict(sorted(execution_counts.items())),
            "clarify_majorities": execution_counts["CLARIFY"],
            "identity_correct_execution_disagrees": sum(
                row["identity_correct_execution_disagrees"] for row in item_results
            ),
        },
        "items_detail": item_results,
    }


def dump_report(report: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
