from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


LEXICAL_FEATURES: tuple[tuple[str, str], ...] = (
    ("same_exact", r"\b(?:same|exact|specific|original|previously|already)\b"),
    ("deictic", r"\b(?:it|that|this|those|them)\b"),
    ("keep", r"\b(?:keep|retain|preserve|continue|stick)\w*\b"),
    ("after_then", r"\b(?:after|afterward|following|once|then)\b"),
    ("refresh", r"\b(?:refresh|reload|sync|update)\w*\b"),
    ("current_latest", r"\b(?:current|latest|new|now)\b"),
    ("selection", r"\b(?:select|choose|pick|find|identify|locate|decide|check)\w*\b"),
)
REFRESH = re.compile(r"\b(?:refresh|reload|sync|update)\w*\b")
SELECTION = re.compile(r"\b(?:select|choose|pick|find|identify|locate|decide|check)\w*\b")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def feature_names(include_order: bool) -> list[str]:
    names = [name for name, _ in LEXICAL_FEATURES]
    if include_order:
        names.extend(["selection_before_refresh", "refresh_before_selection"])
    return names


def featurize(instruction: str, include_order: bool) -> list[float]:
    text = " ".join(instruction.lower().split())
    values = [float(len(re.findall(pattern, text))) for _, pattern in LEXICAL_FEATURES]
    if include_order:
        refresh = REFRESH.search(text)
        selection = SELECTION.search(text)
        values.extend(
            [
                float(bool(refresh and selection and selection.start() < refresh.start())),
                float(bool(refresh and selection and refresh.start() < selection.start())),
            ]
        )
    return values


def sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-values))


def fit_logistic(
    features: np.ndarray,
    targets: np.ndarray,
    l2: float = 1.0,
    iterations: int = 100,
) -> np.ndarray:
    x = np.column_stack([np.ones(len(features)), features.astype(float)])
    y = targets.astype(float)
    beta = np.zeros(x.shape[1], dtype=float)
    penalty = np.eye(x.shape[1], dtype=float)
    penalty[0, 0] = 0.0
    for _ in range(iterations):
        probabilities = sigmoid(x @ beta)
        weights = np.maximum(probabilities * (1.0 - probabilities), 1e-7)
        gradient = x.T @ (y - probabilities) - l2 * penalty @ beta
        information = (x.T * weights) @ x + l2 * penalty + 1e-8 * np.eye(x.shape[1])
        step = np.linalg.solve(information, gradient)
        beta += step
        if float(np.max(np.abs(step))) < 1e-9:
            break
    return beta


def predict_probabilities(beta: np.ndarray, features: np.ndarray) -> np.ndarray:
    x = np.column_stack([np.ones(len(features)), features.astype(float)])
    return sigmoid(x @ beta)


def accuracy(targets: np.ndarray, probabilities: np.ndarray) -> float:
    return float(np.mean((probabilities >= 0.5) == targets))


def auc(targets: np.ndarray, probabilities: np.ndarray) -> float | None:
    positives = probabilities[targets == 1]
    negatives = probabilities[targets == 0]
    if not len(positives) or not len(negatives):
        return None
    wins = sum(float(left > right) + 0.5 * float(left == right) for left in positives for right in negatives)
    return wins / (len(positives) * len(negatives))


def grouped_cv(
    features: np.ndarray,
    targets: np.ndarray,
    groups: list[str],
) -> np.ndarray:
    probabilities = np.zeros(len(targets), dtype=float)
    for group in sorted(set(groups)):
        test = np.array([value == group for value in groups], dtype=bool)
        train = ~test
        beta = fit_logistic(features[train], targets[train])
        probabilities[test] = predict_probabilities(beta, features[test])
    return probabilities


def mode_target(task: dict[str, Any]) -> int:
    return int(task["binding"] == "dynamic")


def human_majority_mode(task: dict[str, Any]) -> int | None:
    metadata = task.get("metadata", {})
    if not metadata.get("human_majority_determinate"):
        return None
    pre = task["pre_refresh_target"]
    post = task["post_refresh_target"]
    majority = metadata.get("human_majority")
    if pre == post:
        return None
    if majority == pre:
        return 0
    if majority == post:
        return 1
    return None


def trigger_audit(root: Path) -> dict[str, Any]:
    v3 = load_jsonl(root / "data/temporal_referent_v3_language_clusters.jsonl")
    rewrites = load_jsonl(root / "data/revision_human_rewrite_v1.jsonl")
    human_rows = [row for row in rewrites if human_majority_mode(row) is not None]
    y_train = np.array([mode_target(row) for row in v3], dtype=int)
    groups = [str(row["template_id"]) for row in v3]
    y_human = np.array([human_majority_mode(row) for row in human_rows], dtype=int)

    models: dict[str, Any] = {}
    for label, include_order in (("trigger_only", False), ("trigger_plus_event_order", True)):
        x_train = np.array([featurize(row["instruction"], include_order) for row in v3])
        x_human = np.array([featurize(row["instruction"], include_order) for row in human_rows])
        cv_probabilities = grouped_cv(x_train, y_train, groups)
        beta = fit_logistic(x_train, y_train)
        human_probabilities = predict_probabilities(beta, x_human)
        names = ["intercept", *feature_names(include_order)]
        models[label] = {
            "feature_names": names,
            "coefficients": {name: float(value) for name, value in zip(names, beta)},
            "v3_leave_template_out": {
                "n": len(v3),
                "accuracy": accuracy(y_train, cv_probabilities),
                "auc": auc(y_train, cv_probabilities),
            },
            "human_majority_changed_rewrites": {
                "n": len(human_rows),
                "accuracy": accuracy(y_human, human_probabilities),
                "auc": auc(y_human, human_probabilities),
                "preserve_n": int(sum(y_human == 0)),
                "reevaluate_n": int(sum(y_human == 1)),
                "majority_class_accuracy": float(max(np.mean(y_human == 0), np.mean(y_human == 1))),
            },
        }
    human_analysis = json.loads((root / "human_validation/analysis.json").read_text(encoding="utf-8"))
    return {
        "status": "post_hoc_zero_api_construct_diagnostic",
        "training_inventory": "v3 authored instructions; design binding labels",
        "external_diagnostic": "determinate human-majority changed rewrites; stable rows excluded",
        "models": models,
        "existing_human_agreement": {
            "n_items": human_analysis["groups"]["all"]["n_items"],
            "fleiss_kappa": human_analysis["groups"]["all"]["fleiss_kappa"],
            "krippendorff_alpha": human_analysis["groups"]["all"]["krippendorff_alpha_nominal"],
        },
        "boundary": (
            "The cue lexicon and model specification were developed post hoc. Human rewrites adapt "
            "authored tasks and do not form an independent open-language holdout."
        ),
    }


def overlap_counts(rule_correct: list[bool], model_correct: list[bool]) -> dict[str, Any]:
    if len(rule_correct) != len(model_correct):
        raise ValueError("Rule/model arrays must have equal length")
    both_correct = sum(rule and model for rule, model in zip(rule_correct, model_correct))
    rule_only = sum(rule and not model for rule, model in zip(rule_correct, model_correct))
    model_only = sum(not rule and model for rule, model in zip(rule_correct, model_correct))
    both_wrong = sum(not rule and not model for rule, model in zip(rule_correct, model_correct))
    model_errors = rule_only + both_wrong
    rule_errors = model_only + both_wrong
    return {
        "n": len(rule_correct),
        "both_correct": both_correct,
        "rule_only": rule_only,
        "model_only": model_only,
        "both_wrong": both_wrong,
        "model_errors_rule_solvable": rule_only,
        "model_errors": model_errors,
        "model_error_rule_solvable_rate": rule_only / model_errors if model_errors else None,
        "rule_errors_model_solvable": model_only,
        "rule_errors": rule_errors,
        "rule_error_model_solvable_rate": model_only / rule_errors if rule_errors else None,
    }


def rule_model_overlap(root: Path) -> dict[str, Any]:
    rule_rows = load_jsonl(root / "runs/deterministic_discourse_rule_v2_v7.jsonl")
    rule = {row["task"]["id"]: row for row in rule_rows}
    runs = {
        "Qwen / History-only": "v7_qwen_interactive_matched_full_v1.jsonl",
        "Qwen / Timing-reminder": "v7_qwen_full_history_once_matched_full_v1.jsonl",
        "Qwen / CTA": "v7_qwen_compile_then_act_full.jsonl",
        "GLM / History-only": "v7_glm_interactive_matched_full_v1.jsonl",
        "GLM / Timing-reminder": "v7_glm_full_history_once_matched_full_v1.jsonl",
        "GLM / CTA": "v7_glm_compile_then_act_full.jsonl",
        "DeepSeek / History-only": "v7_deepseek_interactive_matched_full_v1.jsonl",
        "DeepSeek / Timing-reminder": "v7_deepseek_full_history_once_matched_full_v1.jsonl",
        "DeepSeek / CTA": "v7_deepseek_compile_then_act_full_v1.jsonl",
    }
    results: dict[str, Any] = {}
    for label, filename in runs.items():
        model_rows = load_jsonl(root / "runs" / filename)
        model = {row["task"]["id"]: row for row in model_rows}
        common = sorted(set(rule) & set(model))
        rule_correct = [rule[item]["result"]["predicted_target"] == rule[item]["task"]["correct_target"] for item in common]
        model_correct = [model[item]["result"]["predicted_target"] == model[item]["task"]["correct_target"] for item in common]

        changed = [
            item for item in common if rule[item]["task"]["update"] in {"flip", "name_collision"}
        ]
        row_overlap = overlap_counts(
            [rule[item]["result"]["predicted_target"] == rule[item]["task"]["correct_target"] for item in changed],
            [model[item]["result"]["predicted_target"] == model[item]["task"]["correct_target"] for item in changed],
        )

        pairs: dict[str, list[str]] = defaultdict(list)
        for item in changed:
            task = rule[item]["task"]
            pairs[f"{task['state_cluster_id']}::{task['update']}"] .append(item)
        if any(len(items) != 2 for items in pairs.values()):
            raise ValueError(f"Incomplete changed pairs in {label}")
        rule_pair = [all(rule[item]["result"]["predicted_target"] == rule[item]["task"]["correct_target"] for item in items) for items in pairs.values()]
        model_pair = [all(model[item]["result"]["predicted_target"] == model[item]["task"]["correct_target"] for item in items) for items in pairs.values()]
        results[label] = {
            "source": f"runs/{filename}",
            "all_rows": overlap_counts(rule_correct, model_correct),
            "changed_rows": row_overlap,
            "changed_pairs": overlap_counts(rule_pair, model_pair),
        }
    return {
        "status": "post_hoc_zero_api_full_inventory_overlap",
        "rule": "Rule* v2",
        "inventory": "v7; 240 rows and 80 changed-winner pairs per model/controller",
        "results": results,
        "boundary": (
            "Rule* was developed after authored error inspection. Overlap is descriptive and does "
            "not establish a learned mechanism or confirmatory residual superiority."
        ),
    }


def markdown(report: dict[str, Any]) -> str:
    trigger = report["trigger_logistic"]
    overlap = report["rule_model_overlap"]
    lines = [
        "# Trigger/Order and Rule--Model Overlap Audit",
        "",
        "Evidence status: **post-hoc, zero API**. No new model output is used.",
        "",
        "## Trigger and event-order logistic",
        "",
        "| Model | v3 leave-template-out acc. | v3 AUC | Human-majority changed rewrites | Acc. | AUC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, values in trigger["models"].items():
        v3 = values["v3_leave_template_out"]
        human = values["human_majority_changed_rewrites"]
        lines.append(
            f"| {name} | {v3['accuracy']:.1%} | {v3['auc']:.3f} | {human['n']} "
            f"({human['preserve_n']}/{human['reevaluate_n']}) | {human['accuracy']:.1%} | "
            f"{human['auc']:.3f} |"
        )
    agreement = trigger["existing_human_agreement"]
    human_example = next(iter(trigger["models"].values()))["human_majority_changed_rewrites"]
    lines.extend(
        [
            "",
            f"The human-majority rewrite majority-class baseline is "
            f"{human_example['majority_class_accuracy']:.1%}.",
            "",
            f"Existing three-annotator agreement on 100 items is Fleiss kappa "
            f"{agreement['fleiss_kappa']:.3f} and Krippendorff alpha "
            f"{agreement['krippendorff_alpha']:.3f}.",
            "",
            trigger["boundary"],
            "",
            "## Rule* and frozen model-error overlap",
            "",
            "`rule-only` means Rule* is correct and the model is wrong. `model-only` is the reverse.",
            "",
            "| Model/controller | Unit | Both correct | Rule-only | Model-only | Both wrong | Model errors rule-solvable |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for label, values in overlap["results"].items():
        for unit in ("all_rows", "changed_rows", "changed_pairs"):
            row = values[unit]
            rate = row["model_error_rule_solvable_rate"]
            rate_text = "NA" if rate is None else f"{rate:.1%}"
            lines.append(
                f"| {label} | {unit} (n={row['n']}) | {row['both_correct']} | "
                f"{row['rule_only']} | {row['model_only']} | {row['both_wrong']} | {rate_text} |"
            )
    lines.extend(["", overlap["boundary"], ""])
    return "\n".join(lines)


def build_report(root: Path) -> dict[str, Any]:
    return {
        "trigger_logistic": trigger_audit(root),
        "rule_model_overlap": rule_model_overlap(root),
    }
