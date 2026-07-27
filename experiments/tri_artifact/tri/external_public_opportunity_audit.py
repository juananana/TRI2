"""Deterministic structural audit of external multi-turn tool datasets.

The audit can identify source-anchored workflow candidates. It deliberately
cannot promote a record to a strict native TRI opportunity without observable
pre/post selector states, timing authorization, and a distinct refreshed winner.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


AUDIT_VERSION = "TRI-external-public-opportunity-v1"

QUERY_TOKENS = {
    "check",
    "find",
    "forecast",
    "get",
    "historic",
    "list",
    "query",
    "retrieve",
    "search",
    "view",
}
MUTATION_TOKENS = {
    "activate",
    "add",
    "book",
    "cancel",
    "close",
    "comment",
    "complete",
    "copy",
    "cp",
    "create",
    "delete",
    "edit",
    "echo",
    "fill",
    "fund",
    "lock",
    "modify",
    "move",
    "mv",
    "place",
    "post",
    "purchase",
    "register",
    "remove",
    "resolve",
    "retweet",
    "rm",
    "send",
    "set",
    "start",
    "touch",
    "update",
}
UPDATE_LANGUAGE = re.compile(
    r"\b(refresh|reload|sync|synchroniz(?:e|ed|ing|ation)|meanwhile|"
    r"externally|in the meantime|new (?:item|record|entry|message|event)s? arriv)\w*\b",
    re.IGNORECASE,
)
PRESERVE_LANGUAGE = re.compile(
    r"\b(the same|that (?:one|item|record|entry|file|message|event|order|ticket)|"
    r"the one (?:selected|chosen|found)|keep (?:it|that)|still use it)\b",
    re.IGNORECASE,
)
REEVALUATE_LANGUAGE = re.compile(
    r"\b(refresh|reload|sync|synchronize)\b.{0,80}\b(then|after(?:ward)?)\b.{0,40}"
    r"\b(find|choose|select|query|search)\b",
    re.IGNORECASE | re.DOTALL,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_name(name: str) -> str:
    base = name.rsplit(".", 1)[-1]
    base = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", base)
    return re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")


def _tokens(name: str) -> list[str]:
    return [token for token in _normalized_name(name).split("_") if token]


def is_query(name: str) -> bool:
    tokens = _tokens(name)
    return bool(tokens and (tokens[0] in QUERY_TOKENS or any(t in QUERY_TOKENS for t in tokens[:2])))


def is_mutation(name: str) -> bool:
    tokens = _tokens(name)
    return bool(tokens and tokens[0] in MUTATION_TOKENS)


def _is_id_key(key: str) -> bool:
    normalized = _normalized_name(key)
    return normalized == "id" or normalized.endswith("_id")


def _id_values(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if _is_id_key(str(key)) and isinstance(item, (str, int)):
                found.add(str(item))
            found.update(_id_values(item))
    elif isinstance(value, list):
        for item in value:
            found.update(_id_values(item))
    return found


def _id_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if _is_id_key(str(key)):
                found.add(_normalized_name(str(key)))
            found.update(_id_keys(item))
    elif isinstance(value, list):
        for item in value:
            found.update(_id_keys(item))
    return found


def _timing_label(text: str) -> str:
    preserve = bool(PRESERVE_LANGUAGE.search(text))
    reevaluate = bool(REEVALUATE_LANGUAGE.search(text))
    if preserve and not reevaluate:
        return "preserve_candidate"
    if reevaluate and not preserve:
        return "reevaluate_candidate"
    if preserve or reevaluate:
        return "ambiguous_candidate"
    return "absent"


def _query_before_mutation(names: list[str]) -> tuple[bool, list[int], list[int]]:
    query_positions = [index for index, name in enumerate(names) if is_query(name)]
    mutation_positions = [index for index, name in enumerate(names) if is_mutation(name)]
    ordered = any(q < m for q in query_positions for m in mutation_positions)
    return ordered, query_positions, mutation_positions


def _strict_fields() -> dict[str, bool]:
    # None of the three source formats natively exposes both selector states,
    # an independently authorized timing contrast, and a changed winner.
    return {
        "observable_correct_initial_binding": False,
        "completed_independent_refresh": False,
        "old_target_present_after_refresh": False,
        "old_target_action_valid_after_refresh": False,
        "distinct_refreshed_winner": False,
        "target_level_outcome_observable": False,
    }


def _base_record(dataset: str, unit_id: str, cluster_id: str, source_path: str, raw: Any) -> dict[str, Any]:
    return {
        "audit_version": AUDIT_VERSION,
        "dataset": dataset,
        "unit_id": unit_id,
        "cluster_id": cluster_id,
        "source_path": source_path,
        "source_unit_sha256": hashlib.sha256(
            json.dumps(raw, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest(),
        "strict_native_opportunity": False,
        "strict_fields": _strict_fields(),
    }


def _read_json_lines(path: Path) -> list[Any]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def audit_bfcl(root: Path) -> list[dict[str, Any]]:
    data_root = root / "berkeley-function-call-leaderboard" / "bfcl_eval" / "data"
    records: list[dict[str, Any]] = []
    for path in sorted(data_root.glob("BFCL_v4_multi_turn_*.json")):
        variant = path.stem.removeprefix("BFCL_v4_multi_turn_")
        for raw in _read_json_lines(path):
            unit_id = str(raw["id"])
            suffix = unit_id.rsplit("_", 1)[-1]
            cluster_id = f"bfcl-multi-turn-{suffix}"
            names = [str(name) for name in raw.get("path", [])]
            ordered, query_positions, mutation_positions = _query_before_mutation(names)
            initial_config = raw.get("initial_config", {})
            id_keys = sorted(_id_keys(initial_config))
            text = "\n".join(
                str(message.get("content", ""))
                for turn in raw.get("question", [])
                for message in turn
                if isinstance(message, dict)
            )
            eligible_classes = sorted(
                {
                    names[q].split(".", 1)[0]
                    for q in query_positions
                    for m in mutation_positions
                    if q < m
                    and names[q].split(".", 1)[0] == names[m].split(".", 1)[0]
                    and isinstance(initial_config, dict)
                    and _id_keys(initial_config.get(names[q].split(".", 1)[0], {}))
                }
            )
            source_eligible = bool(eligible_classes)
            record = _base_record("BFCL", unit_id, cluster_id, str(path.relative_to(root)), raw)
            record.update(
                {
                    "variant": variant,
                    "tool_sequence": names,
                    "query_before_mutation": ordered,
                    "stable_id_keys": id_keys,
                    "eligible_classes": eligible_classes,
                    "exact_id_linkage": False,
                    "native_update_language": bool(UPDATE_LANGUAGE.search(text)),
                    "timing_label": _timing_label(text),
                    "source_anchored_eligible": source_eligible,
                    "eligibility_basis": (
                        "query-before-mutation in one executable class whose own state exposes a stable ID"
                        if source_eligible
                        else "missing ordered same-class query/mutation or stable-ID state"
                    ),
                }
            )
            records.append(record)
    return records


def _flatten_tooltalk_calls(raw: dict[str, Any]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for turn in raw.get("conversation", []):
        for api in turn.get("apis", []) or []:
            request = api.get("request", {}) or {}
            calls.append(
                {
                    "name": str(request.get("api_name", "")),
                    "request": request.get("parameters", {}) or {},
                    "response": api.get("response", {}) or {},
                    "turn_index": turn.get("index"),
                }
            )
    return calls


def _linked_query_mutation(calls: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    linked: set[str] = set()
    for query_index, query in enumerate(calls):
        if not is_query(query["name"]):
            continue
        response_ids = _id_values(query["response"])
        for mutation in calls[query_index + 1 :]:
            if not is_mutation(mutation["name"]):
                continue
            linked.update(response_ids & _id_values(mutation["request"]))
    return bool(linked), sorted(linked)


def audit_tooltalk(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((root / "data" / "tooltalk").glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or "conversation" not in raw:
            continue
        unit_id = str(raw.get("name", path.stem))
        calls = _flatten_tooltalk_calls(raw)
        names = [call["name"] for call in calls]
        ordered, _, _ = _query_before_mutation(names)
        exact_linkage, linked_ids = _linked_query_mutation(calls)
        text = "\n".join(str(turn.get("text", "")) for turn in raw.get("conversation", []))
        id_keys = sorted(_id_keys([call["response"] for call in calls]))
        source_eligible = bool(ordered and exact_linkage)
        record = _base_record("ToolTalk", unit_id, unit_id, str(path.relative_to(root)), raw)
        record.update(
            {
                "tool_sequence": names,
                "query_before_mutation": ordered,
                "stable_id_keys": id_keys,
                "exact_id_linkage": exact_linkage,
                "linked_id_count": len(linked_ids),
                "native_update_language": bool(UPDATE_LANGUAGE.search(text)),
                "timing_label": _timing_label(text),
                "source_anchored_eligible": source_eligible,
                "eligibility_basis": (
                    "query response stable ID is consumed by a later mutation"
                    if source_eligible
                    else "missing query-before-mutation with exact stable-ID linkage"
                ),
            }
        )
        records.append(record)
    return records


def _api_bank_units(path: Path) -> Iterable[tuple[str, dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        return
    for index, item in enumerate(raw):
        if isinstance(item, dict):
            yield f"{path.stem}:{index}", item


def audit_api_bank(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    response_files = [
        root / "test-data" / "level-1-response.json",
        root / "test-data" / "level-2-response.json",
        root / "test-data" / "level-3.json",
    ]
    for path in response_files:
        for unit_id, raw in _api_bank_units(path):
            calls = [call for call in raw.get("apis", []) if isinstance(call, dict)]
            normalized_calls = [
                {
                    "name": str(call.get("api_name", "")),
                    "request": call.get("input", {}) or {},
                    "response": call.get("output", {}) or {},
                }
                for call in calls
            ]
            names = [call["name"] for call in normalized_calls]
            ordered, _, _ = _query_before_mutation(names)
            exact_linkage, linked_ids = _linked_query_mutation(normalized_calls)
            text = f"{raw.get('requirement', '')}\n{raw.get('response', '')}"
            id_keys = sorted(_id_keys([call["response"] for call in normalized_calls]))
            source_eligible = bool(ordered and exact_linkage)
            record = _base_record("API-Bank", unit_id, unit_id, str(path.relative_to(root)), raw)
            record.update(
                {
                    "tool_sequence": names,
                    "query_before_mutation": ordered,
                    "stable_id_keys": id_keys,
                    "exact_id_linkage": exact_linkage,
                    "linked_id_count": len(linked_ids),
                    "native_update_language": bool(UPDATE_LANGUAGE.search(text)),
                    "timing_label": _timing_label(text),
                    "source_anchored_eligible": source_eligible,
                    "eligibility_basis": (
                        "query response stable ID is consumed by a later mutation"
                        if source_eligible
                        else "missing query-before-mutation with exact stable-ID linkage"
                    ),
                }
            )
            records.append(record)
    return records


def build_source_manifest(sources: dict[str, Path], commits: dict[str, str]) -> dict[str, Any]:
    manifest: dict[str, Any] = {"audit_version": AUDIT_VERSION, "sources": {}}
    for dataset, root in sources.items():
        if dataset == "BFCL":
            files = sorted(
                (root / "berkeley-function-call-leaderboard" / "bfcl_eval" / "data").glob(
                    "BFCL_v4_multi_turn_*.json"
                )
            )
            files += sorted(
                (root / "berkeley-function-call-leaderboard" / "bfcl_eval" / "data" / "multi_turn_func_doc").glob("*.json")
            )
        elif dataset == "ToolTalk":
            files = sorted((root / "data" / "tooltalk").glob("*.json"))
            files += sorted((root / "data" / "databases").glob("*.json"))
            files += sorted((root / "data" / "easy").glob("*.json"))
        else:
            files = sorted((root / "test-data").glob("*.json"))
        manifest["sources"][dataset] = {
            "commit": commits[dataset],
            "file_count": len(files),
            "total_bytes": sum(path.stat().st_size for path in files),
            "files": [
                {
                    "path": str(path.relative_to(root)),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
                for path in files
            ],
        }
    return manifest


def build_report(records: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_dataset[record["dataset"]].append(record)

    dataset_rows: dict[str, Any] = {}
    eligible_clusters_by_dataset: dict[str, set[str]] = {}
    for dataset, rows in sorted(by_dataset.items()):
        eligible_clusters = {
            row["cluster_id"] for row in rows if row["source_anchored_eligible"]
        }
        eligible_clusters_by_dataset[dataset] = eligible_clusters
        dataset_rows[dataset] = {
            "units": len(rows),
            "unique_clusters": len({row["cluster_id"] for row in rows}),
            "query_before_mutation_units": sum(bool(row["query_before_mutation"]) for row in rows),
            "exact_id_linkage_units": sum(bool(row["exact_id_linkage"]) for row in rows),
            "native_update_language_units": sum(bool(row["native_update_language"]) for row in rows),
            "timing_labels": dict(sorted(Counter(row["timing_label"] for row in rows).items())),
            "source_anchored_eligible_units": sum(bool(row["source_anchored_eligible"]) for row in rows),
            "source_anchored_eligible_clusters": len(eligible_clusters),
            "strict_native_opportunities": 0,
        }

    eligible_datasets = [
        dataset for dataset, clusters in eligible_clusters_by_dataset.items() if clusters
    ]
    total_eligible_clusters = sum(len(clusters) for clusters in eligible_clusters_by_dataset.values())
    go = len(eligible_datasets) >= 2 and total_eligible_clusters >= 8
    return {
        "audit_version": AUDIT_VERSION,
        "status": "post-primary zero-API structural audit",
        "dataset_results": dataset_rows,
        "strict_native_opportunities": 0,
        "source_anchored_eligible_datasets": eligible_datasets,
        "source_anchored_eligible_clusters": total_eligible_clusters,
        "siliconflow_annotation_gate": "GO" if go else "NO-GO",
        "gate_requirements": {
            "minimum_datasets": 2,
            "minimum_clusters": 8,
            "observed_datasets": len(eligible_datasets),
            "observed_clusters": total_eligible_clusters,
        },
        "manifest_commits": {
            dataset: entry["commit"] for dataset, entry in manifest["sources"].items()
        },
        "claim_boundary": (
            "Deterministic structure can nominate source-anchored workflow candidates. "
            "It found no strict native TRI opportunity because the released units do not "
            "jointly expose pre/post selector states, an independent refresh, a surviving "
            "old target, and an instruction-conditioned changed winner."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# External Public-Dataset TRI Opportunity Audit",
        "",
        f"**Status:** {report['status']}",
        "",
        "| Dataset | Units | Clusters | Query→mutation | Exact ID link | Eligible clusters | Strict native |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for dataset, row in report["dataset_results"].items():
        lines.append(
            f"| {dataset} | {row['units']} | {row['unique_clusters']} | "
            f"{row['query_before_mutation_units']} | {row['exact_id_linkage_units']} | "
            f"{row['source_anchored_eligible_clusters']} | {row['strict_native_opportunities']} |"
        )
    lines += [
        "",
        "## SiliconFlow annotation gate",
        "",
        f"**Decision: {report['siliconflow_annotation_gate']}**",
        "",
        f"- Eligible external datasets: {report['gate_requirements']['observed_datasets']} "
        f"(minimum {report['gate_requirements']['minimum_datasets']})",
        f"- Eligible workflow clusters: {report['gate_requirements']['observed_clusters']} "
        f"(minimum {report['gate_requirements']['minimum_clusters']})",
        "",
        "## Boundary",
        "",
        report["claim_boundary"],
        "",
        "The gate authorizes only frozen candidate annotation. It does not turn eligible "
        "workflows into native TRI positives or authorize a behavioral model run.",
        "",
    ]
    return "\n".join(lines)
