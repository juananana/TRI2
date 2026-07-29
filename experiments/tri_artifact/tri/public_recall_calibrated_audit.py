from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from typing import Any

SEED = 20260729
ANNOTATORS = ("A1", "A2", "A3")
MODEL_PRELABELERS = ("M1", "M2", "M3")
CONTROL_ROLE = "injected_control"
RUBRIC_FIELDS = (
    "stable_entity_id",
    "observable_pre_refresh_binding",
    "independent_post_binding_transition",
    "competing_same_role_entity",
    "changed_selector_winner",
    "old_entity_remains_actionable",
    "later_target_mutation",
    "evaluable_authorized_target",
)


def blind_public_unit_id(row: dict[str, Any]) -> str:
    source_id = (
        f"control::{row['control_id']}"
        if row.get("audit_role") == CONTROL_ROLE
        else unit_key(row)
    )
    digest = __import__("hashlib").sha256(f"{SEED}:{source_id}".encode()).hexdigest()
    return "PU-" + digest[:16].upper()


def build_blind_public_annotation_payload(
    row: dict[str, Any], labeler_id: str
) -> dict[str, Any]:
    if labeler_id not in set(ANNOTATORS) | set(MODEL_PRELABELERS):
        raise ValueError(f"unknown public-audit labeler: {labeler_id}")
    control = row.get("audit_role") == CONTROL_ROLE
    evidence = _blind_source_evidence(row)
    payload = {
        "labeler_id": labeler_id,
        "blind_unit_id": blind_public_unit_id(row),
        "display_dataset": str(row.get("dataset") or row.get("suite") or "benchmark"),
        "source_evidence": evidence,
        "rubric_fields": list(RUBRIC_FIELDS),
        "response_schema": {
            "feature_labels": "object with every rubric field labeled yes/no/partial",
            "strict_eligible": "boolean; true only when every rubric field is yes",
            "primary_exclusion_reason": "one rubric field or NONE",
            "confidence": "integer 1-5",
            "notes": "brief source-grounded rationale",
        },
        "evidence_status": (
            "independent human label"
            if labeler_id in ANNOTATORS
            else "model-assisted prelabel; never human evidence"
        ),
    }
    forbidden = {
        "audit_role",
        "inclusion_probability",
        "sample_seed",
        "expected_strict",
        "expected_strict_positive",
        "candidate_basis",
        "candidate_id",
        "unit_id",
        "cluster_id",
        "audit_unit_id",
        "control_id",
        "source_path",
        "source_unit_sha256",
    }
    if forbidden.intersection(payload):
        raise ValueError("blind public annotation payload leaked sampling or source identity")
    return payload


def _control_scenario_text(row: dict[str, Any]) -> str:
    features = {field: bool((row.get("features") or {}).get(field)) for field in RUBRIC_FIELDS}
    stable_ids = features["stable_entity_id"]
    competing = features["competing_same_role_entity"]
    bound = features["observable_pre_refresh_binding"]
    transition = features["independent_post_binding_transition"]
    changed = features["changed_selector_winner"]
    actionable = features["old_entity_remains_actionable"]
    mutation = features["later_target_mutation"]
    evaluable = features["evaluable_authorized_target"]
    sentences = [
        (
            "The workflow records persistent entity IDs REC-A and REC-B across observations."
            if stable_ids
            else "The observations provide no persistent identifier linking entities across time."
        ),
        (
            "The initial list contains editable same-role records REC-A at priority 1 and REC-B at priority 2."
            if competing
            else "The initial list contains only one editable record."
        ),
        (
            "Before any refresh, the agent applies the lowest-numeric-priority selector and records REC-A as selected."
            if bound
            else "No entity is selected or recorded before the later observation."
        ),
        (
            "An independent refresh then occurs before the requested update."
            if transition
            else "No independent post-selection transition is observed."
        ),
        (
            "After refresh, REC-B has priority 1 and REC-A has priority 2, so the selector winner changes."
            if changed and competing
            else "After the later observation, the selector winner does not change."
        ),
        (
            "REC-A remains present and editable after refresh."
            if actionable
            else "The earlier record is missing or no longer editable after refresh."
        ),
        (
            "A later update operation is completed."
            if mutation
            else "No later target-level mutation is attempted."
        ),
        (
            "The execution log identifies REC-A as the update target."
            if evaluable and mutation
            else "The final outcome does not identify which entity was targeted."
        ),
    ]
    return " ".join(sentences)


def _control_suite_summary(row: dict[str, Any]) -> dict[str, Any]:
    dataset = str(row.get("suite") or row.get("dataset"))
    scenario = _control_scenario_text(row)
    if dataset == "ToolSandbox":
        return {
            "milestones": [
                {"index": 0, "tool_names": ["search_records"], "entity_mutations": []},
                {"index": 1, "tool_names": ["refresh_records"], "entity_mutations": []},
                {"index": 2, "tool_names": ["update_record"], "entity_mutations": []},
            ],
            "official_user_task": scenario,
            "source_group": "multi_tool_call",
            "tool_allow_list": ["search_records", "refresh_records", "update_record"],
        }
    if dataset == "AppWorld":
        return {
            "instructions": [scenario, scenario],
            "task_instances": ["7f13a21_1", "7f13a21_2"],
        }
    if dataset == "tau3-bench":
        return {
            "domain": "records",
            "evaluation_actions": [
                {
                    "argument_keys": ["record_id"],
                    "name": "update_record",
                    "requestor": "assistant",
                    "stable_id_fields": ["record_id"],
                }
            ],
            "purpose": scenario,
            "reason_for_call": "Review and update the authorized record after a refresh.",
        }
    if dataset == "API-Bank":
        return {
            "source_records": [{
                "expected_output": "The authorized record was updated.",
                "input": scenario,
                "instruction": "Generate a response from the supplied workflow and API trace.",
            }]
        }
    if dataset == "BFCL":
        return {
            "source_records": [{
                "initial_config": {"RecordStore": {"description": scenario}},
                "involved_classes": ["RecordStore"],
                "question": [[{"content": scenario, "role": "user"}]],
                "tool_sequence": ["RecordStore.search", "RecordStore.refresh", "RecordStore.update"],
            }]
        }
    if dataset == "ToolTalk":
        return {
            "source_records": [{
                "apis_used": ["SearchRecords", "RefreshRecords", "UpdateRecord"],
                "conversation": [
                    {"index": 0, "role": "user", "text": scenario},
                    {"index": 1, "role": "assistant", "text": "The workflow is complete."},
                ],
                "scenario": scenario,
                "suites_used": ["RecordAPI"],
            }]
        }
    raise ValueError(f"unknown control dataset: {dataset}")


def _sanitize_natural_summary(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _sanitize_natural_summary(item)
            for key, item in value.items()
            if key not in {"classification", "candidate_basis", "retrieval_label"}
        }
    if isinstance(value, list):
        return [_sanitize_natural_summary(item) for item in value]
    if isinstance(value, str) and (
        value.startswith("excluded_") or value.startswith("tri_like_")
    ):
        return "<DERIVED_LABEL_REMOVED>"
    return value


def _blind_source_evidence(row: dict[str, Any]) -> dict[str, str]:
    summary = (
        _control_suite_summary(row)
        if row.get("audit_role") == CONTROL_ROLE
        else _sanitize_natural_summary(row.get("source_summary", {}))
    )
    return {
        "document": json.dumps(summary, sort_keys=True, ensure_ascii=False)
    }


def reconcile_candidate_inventories(
    annotation_candidates: list[dict[str, Any]],
    triage_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Reconcile the payload-backed inventory and the cross-suite triage queue."""
    annotation_by_key: dict[str, dict[str, Any]] = {}
    for row in annotation_candidates:
        local_id = row.get("cluster_id") or row.get("unit_id")
        key = f"{row['dataset']}::{local_id}"
        if key in annotation_by_key:
            raise ValueError(f"duplicate annotation candidate: {key}")
        annotation_by_key[key] = row

    natural_triage = [
        row for row in triage_rows if row.get("source_kind") != CONTROL_ROLE
    ]
    triage_by_key: dict[str, dict[str, Any]] = {}
    for row in natural_triage:
        suite = str(row["suite"])
        source_kind = str(row["source_kind"])
        local_id = str(
            (row.get("source_excerpt") or {}).get("cluster_id")
            or (row["case_id"] if source_kind == "external_structural_candidate" else row["record_id"])
        )
        key = f"{suite}::{local_id}"
        if key in triage_by_key:
            raise ValueError(f"duplicate natural triage unit: {key}")
        triage_by_key[key] = row

    keys = sorted(set(annotation_by_key) | set(triage_by_key))
    ledger = []
    for key in keys:
        annotation = annotation_by_key.get(key)
        triage = triage_by_key.get(key)
        dataset = str((annotation or triage)["dataset" if annotation else "suite"])
        ledger.append(
            {
                "audit_unit_key": key,
                "dataset": dataset,
                "in_payload_backed_80": annotation is not None,
                "in_cross_suite_triage_72": triage is not None,
                "triage_source_kind": triage.get("source_kind") if triage else None,
                "candidate_id": annotation.get("candidate_id") if annotation else None,
                "triage_record_id": triage.get("record_id") if triage else None,
                "source_unit_sha256": annotation.get("source_unit_sha256") if annotation else None,
                "reconciliation_status": (
                    "overlap"
                    if annotation is not None and triage is not None
                    else "payload_inventory_only"
                    if annotation is not None
                    else "triage_only"
                ),
            }
        )

    overlap = sum(row["reconciliation_status"] == "overlap" for row in ledger)
    payload_only = sum(
        row["reconciliation_status"] == "payload_inventory_only" for row in ledger
    )
    triage_only = sum(row["reconciliation_status"] == "triage_only" for row in ledger)
    report = {
        "audit_version": "TRI-public-candidate-reconciliation-v1",
        "evidence_status": "inventory reconciliation; not prevalence or recall evidence",
        "payload_backed_inventory": len(annotation_by_key),
        "natural_triage_inventory": len(triage_by_key),
        "overlap": overlap,
        "payload_only": payload_only,
        "triage_only": triage_only,
        "union_audit_units": len(ledger),
        "audit_unit_union_frozen": True,
        "benchmark_population_complete": False,
        "sampling_allowed": False,
        "sampling_blocker": (
            "A source-level population ledger for every pinned benchmark is still required; "
            "the candidate union is not a benchmark denominator."
        ),
    }
    return ledger, report


def unit_key(row: dict[str, Any]) -> str:
    dataset = str(row.get("dataset", ""))
    value = (
        row.get("audit_unit_id")
        or row.get("cluster_id")
        or row.get("unit_id")
        or row.get("candidate_id")
    )
    if not dataset or value is None:
        raise ValueError("audit unit requires dataset and candidate_id/unit_id/cluster_id")
    return f"{dataset}::{value}"


def deduplicate_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        output.setdefault(unit_key(row), dict(row))
    return [output[key] for key in sorted(output)]


def build_sampling_frame(
    population: list[dict[str, Any]], candidates: list[dict[str, Any]],
    controls: list[dict[str, Any]] | None = None, per_dataset: int = 100, seed: int = SEED,
) -> list[dict[str, Any]]:
    if per_dataset <= 0:
        raise ValueError("per_dataset must be positive")
    population_by_key: dict[str, dict[str, Any]] = {}
    for row in population:
        key = unit_key(row)
        if key in population_by_key:
            raise ValueError(f"duplicate population unit: {key}")
        population_by_key[key] = row
    candidate_rows = deduplicate_candidates(candidates)
    candidate_keys = {unit_key(row) for row in candidate_rows}
    if not candidate_keys.issubset(population_by_key):
        raise ValueError("candidate units must exist in the population")
    frame = []
    for row in candidate_rows:
        item = dict(population_by_key[unit_key(row)])
        item.update({"audit_role": "retrieved_candidate", "inclusion_probability": 1.0, "sample_seed": seed})
        frame.append(item)
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in population_by_key.values():
        if unit_key(row) not in candidate_keys:
            by_dataset[str(row["dataset"])].append(row)
    for dataset, rows in sorted(by_dataset.items()):
        rows = sorted(rows, key=unit_key)
        sample_size = min(per_dataset, len(rows))
        rng = random.Random(seed + sum(ord(ch) for ch in dataset))
        probability = sample_size / len(rows) if rows else 0.0
        for row in sorted(rng.sample(rows, sample_size), key=unit_key):
            item = dict(row)
            item.update({"audit_role": "random_non_candidate", "inclusion_probability": probability, "sample_seed": seed})
            frame.append(item)
    for index, row in enumerate(controls or []):
        item = dict(row)
        item.update({"audit_role": CONTROL_ROLE, "inclusion_probability": 1.0, "sample_seed": seed, "control_index": index})
        frame.append(item)
    return frame


def majority_label(adjudications: dict[str, Any]) -> bool:
    if set(adjudications) != set(ANNOTATORS):
        raise ValueError("exactly three annotator labels are required")
    values = [value if isinstance(value, bool) else str(value).lower() in {"true", "yes", "positive", "1"} for value in adjudications.values()]
    return sum(values) >= 2


def attach_adjudication(row: dict[str, Any]) -> dict[str, Any]:
    majority = majority_label(row.get("adjudications", {}))
    values = [value if isinstance(value, bool) else str(value).lower() in {"true", "yes", "positive", "1"} for value in row["adjudications"].values()]
    agreement = max(sum(values), len(values) - sum(values)) / 3
    return {**row, "majority_strict_positive": majority, "item_agreement": agreement}


def _normalize_feature_label(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    normalized = str(value).strip().lower()
    aliases = {"true": "yes", "false": "no", "1": "yes", "0": "no"}
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"yes", "no", "partial"}:
        raise ValueError(f"invalid rubric label: {value!r}")
    return normalized


def validate_annotation_return(
    row: dict[str, Any], expected_labeler: str
) -> dict[str, Any]:
    if row.get("labeler_id") != expected_labeler:
        raise ValueError(f"annotation return labeler mismatch for {expected_labeler}")
    blind_id = row.get("blind_unit_id")
    if not isinstance(blind_id, str) or not blind_id.startswith("PU-"):
        raise ValueError("annotation return requires an opaque blind_unit_id")
    feature_labels = row.get("feature_labels")
    if not isinstance(feature_labels, dict) or set(feature_labels) != set(RUBRIC_FIELDS):
        raise ValueError("annotation return must label every frozen rubric field exactly once")
    normalized_features = {
        field: _normalize_feature_label(feature_labels[field]) for field in RUBRIC_FIELDS
    }
    strict = row.get("strict_eligible")
    if not isinstance(strict, bool):
        raise ValueError("strict_eligible must be boolean")
    derived_strict = all(value == "yes" for value in normalized_features.values())
    if strict != derived_strict:
        raise ValueError("strict_eligible must equal the conjunction of the rubric fields")
    exclusion = row.get("primary_exclusion_reason")
    if strict:
        if exclusion != "NONE":
            raise ValueError("strict-positive rows require primary_exclusion_reason=NONE")
    elif exclusion not in RUBRIC_FIELDS or normalized_features[exclusion] == "yes":
        raise ValueError("strict-negative rows require a non-yes rubric exclusion reason")
    confidence = row.get("confidence")
    if not isinstance(confidence, int) or isinstance(confidence, bool) or not 1 <= confidence <= 5:
        raise ValueError("confidence must be an integer from 1 through 5")
    notes = row.get("notes")
    if not isinstance(notes, str):
        raise ValueError("notes must be a string")
    return {
        "labeler_id": expected_labeler,
        "blind_unit_id": blind_id,
        "feature_labels": normalized_features,
        "strict_eligible": strict,
        "primary_exclusion_reason": exclusion,
        "confidence": confidence,
        "notes": notes.strip(),
    }


def validate_human_annotation_provenance(
    provenance: dict[str, Any],
    private_key_sha256: str,
    return_sha256: dict[str, str],
    role_token_sha256: dict[str, str] | None = None,
) -> None:
    if provenance.get("status") != "complete-locked-before-model-prelabels":
        raise ValueError("human annotation provenance is not complete and locked")
    if provenance.get("private_annotation_key_sha256") != private_key_sha256:
        raise ValueError("human provenance private-key hash mismatch")
    recorded_hashes = provenance.get("annotation_returns_sha256")
    if not isinstance(recorded_hashes, dict) or recorded_hashes != return_sha256:
        raise ValueError("human provenance return hashes do not match the locked files")
    annotators = provenance.get("annotators")
    if not isinstance(annotators, dict) or set(annotators) != set(ANNOTATORS):
        raise ValueError("human provenance requires exactly A1-A3")
    if role_token_sha256 is None:
        raise ValueError("human provenance requires a private role registry")
    for annotator in ANNOTATORS:
        item = annotators[annotator]
        if not isinstance(item, dict) or not (
            item.get("source") == "independent_human"
            and item.get("completed") is True
            and item.get("blind") is True
            and item.get("saw_model_prelabels_before_lock") is False
            and item.get("participant_token_sha256") == role_token_sha256.get(annotator)
        ):
            raise ValueError(f"invalid independent-human provenance for {annotator}")


def merge_public_annotation_returns(
    frame: list[dict[str, Any]],
    private_key: list[dict[str, Any]],
    human_returns: dict[str, list[dict[str, Any]]],
    human_provenance: dict[str, Any],
    private_key_sha256: str,
    human_return_sha256: dict[str, str],
    model_returns: dict[str, list[dict[str, Any]]] | None = None,
    role_token_sha256: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Resolve opaque returns only after the three-human provenance gate passes."""
    validate_human_annotation_provenance(
        human_provenance, private_key_sha256, human_return_sha256, role_token_sha256
    )
    if set(human_returns) != set(ANNOTATORS):
        raise ValueError("exactly three independent-human return files are required")
    frame_by_blind_id = {blind_public_unit_id(row): row for row in frame}
    if len(frame_by_blind_id) != len(frame):
        raise ValueError("frame contains duplicate blind IDs")
    key_by_blind_id = {str(row.get("blind_unit_id")): row for row in private_key}
    if len(key_by_blind_id) != len(private_key) or set(key_by_blind_id) != set(frame_by_blind_id):
        raise ValueError("private annotation key does not exactly cover the frozen frame")
    for blind_id, frame_row in frame_by_blind_id.items():
        key_row = key_by_blind_id[blind_id]
        if (
            key_row.get("audit_role") != frame_row.get("audit_role")
            or float(key_row.get("inclusion_probability", -1))
            != float(frame_row.get("inclusion_probability", -2))
        ):
            raise ValueError(f"private key sampling metadata mismatch for {blind_id}")

    normalized_human: dict[str, dict[str, dict[str, Any]]] = {}
    for annotator in ANNOTATORS:
        values: dict[str, dict[str, Any]] = {}
        for raw in human_returns[annotator]:
            item = validate_annotation_return(raw, annotator)
            blind_id = item["blind_unit_id"]
            if blind_id in values:
                raise ValueError(f"duplicate {annotator} return for {blind_id}")
            values[blind_id] = item
        if set(values) != set(frame_by_blind_id):
            raise ValueError(f"{annotator} return does not exactly cover the frozen frame")
        normalized_human[annotator] = values

    normalized_models: dict[str, dict[str, dict[str, Any]]] = {}
    for labeler, rows in (model_returns or {}).items():
        if labeler not in MODEL_PRELABELERS:
            raise ValueError(f"unknown model prelabeler: {labeler}")
        values: dict[str, dict[str, Any]] = {}
        for raw in rows:
            item = validate_annotation_return(raw, labeler)
            blind_id = item["blind_unit_id"]
            if blind_id in values:
                raise ValueError(f"duplicate {labeler} return for {blind_id}")
            values[blind_id] = item
        if set(values) != set(frame_by_blind_id):
            raise ValueError(f"{labeler} return does not exactly cover the frozen frame")
        normalized_models[labeler] = values

    merged = []
    for blind_id, frame_row in frame_by_blind_id.items():
        human = {
            annotator: normalized_human[annotator][blind_id] for annotator in ANNOTATORS
        }
        models = {
            labeler: values[blind_id] for labeler, values in normalized_models.items()
        }
        merged.append(
            {
                **frame_row,
                "blind_unit_id": blind_id,
                "adjudications": {
                    annotator: human[annotator]["strict_eligible"]
                    for annotator in ANNOTATORS
                },
                "human_annotations": human,
                "model_prelabels": models,
                "human_annotation_provenance_validated": True,
                "model_prelabels_used_for_majority": False,
            }
        )
    return merged


def _agreement_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def agreement(values: list[Any]) -> tuple[bool, float]:
        return len(set(values)) == 1, sum(
            values[left] == values[right]
            for left, right in ((0, 1), (0, 2), (1, 2))
        ) / 3

    output: dict[str, Any] = {}
    for field in (*RUBRIC_FIELDS, "strict_eligible"):
        unanimous = 0
        pairwise = 0.0
        denominator = 0
        for row in rows:
            annotations = row.get("human_annotations") or {}
            if set(annotations) != set(ANNOTATORS):
                continue
            denominator += 1
            values = [
                annotations[name]["strict_eligible"]
                if field == "strict_eligible"
                else annotations[name]["feature_labels"][field]
                for name in ANNOTATORS
            ]
            item_unanimous, item_pairwise = agreement(values)
            unanimous += item_unanimous
            pairwise += item_pairwise
        output[field] = {
            "rows": denominator,
            "unanimous_rate": unanimous / denominator if denominator else None,
            "mean_pairwise_agreement": pairwise / denominator if denominator else None,
        }
    return output


def _hypergeometric_draw(
    rng: random.Random, population: int, positives: int, draws: int
) -> int:
    successes = 0
    remaining = population
    positive_remaining = positives
    for _ in range(draws):
        if remaining <= 0:
            break
        if rng.random() < positive_remaining / remaining:
            successes += 1
            positive_remaining -= 1
        remaining -= 1
    return successes


def _finite_population_bootstrap(
    candidate_positive: int,
    noncandidate_population: int,
    noncandidate_labels: list[bool],
    population_size: int,
    seed: int,
    samples: int,
) -> list[float]:
    if population_size <= 0 or not noncandidate_labels:
        return []
    rng = random.Random(seed)
    sample_size = len(noncandidate_labels)
    observed = sum(noncandidate_labels)
    fitted_positives = round(noncandidate_population * observed / sample_size)
    values = []
    for _ in range(samples):
        sampled_positive = _hypergeometric_draw(
            rng, noncandidate_population, fitted_positives, sample_size
        )
        estimated_noncandidate = (
            noncandidate_population * sampled_positive / sample_size
        )
        values.append((candidate_positive + estimated_noncandidate) / population_size)
    return values


def finite_population_zero_upper_bound(
    population_size: int,
    candidate_census_size: int,
    random_noncandidate_sample_size: int,
    alpha: float = 0.05,
) -> float | None:
    """Exact one-sided upper prevalence bound after zero positives without replacement."""
    noncandidate_population = population_size - candidate_census_size
    if population_size <= 0 or noncandidate_population < 0:
        return None
    if noncandidate_population == 0 or random_noncandidate_sample_size >= noncandidate_population:
        return 0.0
    if random_noncandidate_sample_size <= 0:
        return 1.0
    sample_size = random_noncandidate_sample_size
    denominator = math.lgamma(noncandidate_population + 1) - math.lgamma(
        sample_size + 1
    ) - math.lgamma(noncandidate_population - sample_size + 1)
    upper_positives = 0
    for positives in range(1, noncandidate_population + 1):
        if noncandidate_population - positives < sample_size:
            probability_zero = 0.0
        else:
            numerator = (
                math.lgamma(noncandidate_population - positives + 1)
                - math.lgamma(sample_size + 1)
                - math.lgamma(noncandidate_population - positives - sample_size + 1)
            )
            probability_zero = math.exp(numerator - denominator)
        if probability_zero < alpha:
            break
        upper_positives = positives
    return upper_positives / population_size


def report_audit(
    rows: list[dict[str, Any]],
    population_sizes: dict[str, int],
    seed: int = SEED,
    bootstrap_samples: int = 10_000,
    verified_ingestion: bool = False,
) -> dict[str, Any]:
    labeled = [attach_adjudication(row) for row in rows]
    natural = [row for row in labeled if row.get("audit_role") != CONTROL_ROLE]
    human_gate_passed = verified_ingestion and bool(labeled) and all(
        row.get("human_annotation_provenance_validated") is True
        and row.get("model_prelabels_used_for_majority") is False
        for row in labeled
    )
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in natural:
        by_dataset[str(row["dataset"])].append(row)
    datasets = {}
    for dataset, dataset_rows in sorted(by_dataset.items()):
        candidate_rows = [
            row for row in dataset_rows if row.get("audit_role") == "retrieved_candidate"
        ]
        random_rows = [
            row for row in dataset_rows if row.get("audit_role") == "random_non_candidate"
        ]
        units = []
        candidate_positive = 0
        for row in dataset_rows:
            weight = 1.0 / float(row.get("inclusion_probability", 1.0))
            positive = bool(row["majority_strict_positive"])
            units.append((weight, positive))
            if positive and row.get("audit_role") == "retrieved_candidate":
                candidate_positive += 1
        denominator = sum(weight for weight, _ in units)
        numerator = sum(weight for weight, positive in units if positive)
        population_size = int(population_sizes.get(dataset, 0))
        noncandidate_population = population_size - len(candidate_rows)
        bootstrap = [] if numerator == 0 else sorted(
            _finite_population_bootstrap(
                candidate_positive,
                noncandidate_population,
                [bool(row["majority_strict_positive"]) for row in random_rows],
                population_size,
                seed + sum(ord(ch) for ch in dataset),
                bootstrap_samples,
            )
        )
        ci = [bootstrap[int(0.025 * len(bootstrap))], bootstrap[min(len(bootstrap) - 1, int(0.975 * len(bootstrap)))] ] if bootstrap else [None, None]
        zero_upper = (
            finite_population_zero_upper_bound(
                population_size, len(candidate_rows), len(random_rows)
            )
            if numerator == 0
            else None
        )
        datasets[dataset] = {
            "population_size": population_size, "labeled_units": len(dataset_rows),
            "candidate_census_size": len(candidate_rows),
            "random_noncandidate_sample_size": len(random_rows),
            "weighted_denominator": denominator, "weighted_positive": numerator,
            "prevalence": numerator / denominator if denominator else None,
            "bootstrap_ci95": ci,
            "bootstrap_ci_status": (
                "not reported for zero positives; use exact one-sided bound"
                if numerator == 0
                else "two-sided percentile interval"
            ),
            "bootstrap_design": "candidate census plus finite-population hypergeometric noncandidate resampling",
            "zero_positive_upper_bound_95": zero_upper,
            "zero_positive_bound_method": "exact hypergeometric one-sided 95%",
            "candidate_positive_weight": candidate_positive,
            "retrieval_sensitivity": candidate_positive / numerator if numerator else None,
            "retrieval_sensitivity_identifiable": bool(numerator),
        }
    controls = [row for row in labeled if row.get("audit_role") == CONTROL_ROLE]
    def expected_control(row: dict[str, Any]) -> bool | None:
        value = row.get("expected_strict_positive")
        return row.get("expected_strict") if value is None else value

    model_prelabels: dict[str, Any] = {}
    for labeler in MODEL_PRELABELERS:
        available = [
            row for row in labeled if labeler in (row.get("model_prelabels") or {})
        ]
        if available:
            model_prelabels[labeler] = {
                "evidence_role": "descriptive only; excluded from human majority",
                "rows": len(available),
                "strict_positive": sum(
                    row["model_prelabels"][labeler]["strict_eligible"] for row in available
                ),
                "agreement_with_human_majority": sum(
                    row["model_prelabels"][labeler]["strict_eligible"]
                    == row["majority_strict_positive"]
                    for row in available
                ) / len(available),
            }
    return {
        "audit_version": "TRI-public-recall-calibrated-audit-v1",
        "evidence_status": (
            "post-primary independent-human public benchmark audit"
            if human_gate_passed
            else "planned/unverified"
        ),
        "independent_human_gate_passed": human_gate_passed,
        "model_prelabels_used_for_majority": False,
        "seed": seed, "bootstrap_samples": bootstrap_samples,
        "natural_rows": len(natural), "control_rows": len(controls), "datasets": datasets,
        "natural_positive_found": any(item["weighted_positive"] > 0 for item in datasets.values()),
        "recall_claim_allowed": human_gate_passed and any(
            item["retrieval_sensitivity_identifiable"] for item in datasets.values()
        ),
        "human_agreement": _agreement_summary(natural) if human_gate_passed else None,
        "model_prelabels": model_prelabels,
        "controls": {
            "positive_correct": sum(expected_control(row) is True and row["majority_strict_positive"] for row in controls),
            "positive_total": sum(expected_control(row) is True for row in controls),
            "negative_correct": sum(expected_control(row) is False and not row["majority_strict_positive"] for row in controls),
            "negative_total": sum(expected_control(row) is False for row in controls),
            "by_annotator": {
                annotator: {
                    "correct": sum(
                        row["adjudications"][annotator] == expected_control(row)
                        for row in controls
                    ),
                    "total": len(controls),
                }
                for annotator in ANNOTATORS
            },
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Public Recall-Calibrated Audit",
        "",
        f"Evidence status: `{report['evidence_status']}`. Independent-human gate: `{report['independent_human_gate_passed']}`.",
        "",
        "| Dataset | Population | Labeled | Weighted positive | Prevalence | Zero-positive upper bound | Recall identifiable |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for dataset, item in report["datasets"].items():
        prevalence = "NA" if item["prevalence"] is None else f"{100 * item['prevalence']:.3f}%"
        upper = "NA" if item["zero_positive_upper_bound_95"] is None else f"{100 * item['zero_positive_upper_bound_95']:.3f}%"
        lines.append(f"| {dataset} | {item['population_size']} | {item['labeled_units']} | {item['weighted_positive']:.2f} | {prevalence} | {upper} | {item['retrieval_sensitivity_identifiable']} |")
    lines.extend([
        "",
        f"Natural positives found: `{report['natural_positive_found']}`.",
        f"Recall claim allowed: `{report['recall_claim_allowed']}`.",
        "",
        "Injected controls are excluded from natural estimates. Model prelabels are descriptive only and are excluded from every human majority label.",
    ])
    return "\n".join(lines)
