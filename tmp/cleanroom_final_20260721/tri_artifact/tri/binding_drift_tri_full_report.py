"""Report the frozen full-v7 Binding Drift author adaptation."""

from __future__ import annotations

from collections import defaultdict
import json
import random
from pathlib import Path

from tri.binding_drift_tri_adapter import (
    entity_lock_target,
    file_sha256,
    load_predictions,
    score_target,
    summarize,
)


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def indexed_targets(path: Path) -> dict[str, str | None]:
    return load_predictions(path)


def scored_rows(tasks: list[dict], targets: dict[str, str | None], method: str) -> list[dict]:
    expected = {task["id"] for task in tasks}
    if set(targets) != expected:
        missing = sorted(expected.difference(targets))
        extra = sorted(set(targets).difference(expected))
        raise ValueError(f"{method}: mismatched task IDs; missing={missing[:5]}, extra={extra[:5]}")
    return [
        {"method": method, "task": task, "result": score_target(task, targets[task["id"]])}
        for task in tasks
    ]


def slice_summary(rows: list[dict]) -> dict:
    output = summarize(rows)
    output["by_update"] = {}
    for update in ("flip", "stable", "name_collision"):
        subset = [row for row in rows if row["task"]["update"] == update]
        output["by_update"][update] = {
            "n": len(subset),
            "correct": sum(row["result"]["success"] for row in subset),
        }

    pairs: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        key = (row["task"]["state_cluster_id"], row["task"]["update"])
        pairs[key].append(row)
    if len(pairs) != 120 or any(len(pair) != 2 for pair in pairs.values()):
        raise ValueError("Expected 120 complete Preserve/Reevaluate pairs")
    if any({row["task"]["binding"] for row in pair} != {"anchored", "dynamic"} for pair in pairs.values()):
        raise ValueError("A matched pair lacks Preserve or Reevaluate")
    output["paired_authorization"] = {
        "n": len(pairs),
        "both_correct": sum(all(row["result"]["success"] for row in pair) for pair in pairs.values()),
    }
    return output


def _percentile(values: list[float], fraction: float) -> float:
    values = sorted(values)
    index = (len(values) - 1) * fraction
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    weight = index - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def cluster_bootstrap_delta(
    cta_rows: list[dict], reverify_rows: list[dict], draws: int = 10_000, seed: int = 20260721
) -> dict:
    cta = {row["task"]["id"]: row for row in cta_rows}
    reverify = {row["task"]["id"]: row for row in reverify_rows}
    if set(cta) != set(reverify):
        raise ValueError("CTA and reverify task IDs differ")
    clusters: dict[str, list[str]] = defaultdict(list)
    for task_id, row in cta.items():
        clusters[row["task"]["state_cluster_id"]].append(task_id)
    if len(clusters) != 40 or any(len(ids) != 6 for ids in clusters.values()):
        raise ValueError("Expected 40 complete six-task clusters")
    names = sorted(clusters)

    def delta(ids: list[str]) -> float:
        return sum(
            int(cta[task_id]["result"]["success"])
            - int(reverify[task_id]["result"]["success"])
            for task_id in ids
        ) / len(ids)

    rng = random.Random(seed)
    samples = []
    for _ in range(draws):
        ids = [task_id for _ in names for task_id in clusters[rng.choice(names)]]
        samples.append(delta(ids))
    all_ids = sorted(cta)
    return {
        "estimand": "CTA minus GLM reverify exact-target accuracy",
        "delta": delta(all_ids),
        "cluster_bootstrap_ci95": [_percentile(samples, 0.025), _percentile(samples, 0.975)],
        "clusters": 40,
        "draws": draws,
        "seed": seed,
    }


def classify_gate(cta: dict, reverify: dict) -> str:
    overall_gap = abs(cta["accuracy"] - reverify["accuracy"])
    mode_gaps = [
        abs(cta[mode]["correct"] / cta[mode]["n"] - reverify[mode]["correct"] / reverify[mode]["n"])
        for mode in ("anchored", "dynamic")
    ]
    pair_gap = abs(
        cta["paired_authorization"]["both_correct"] / cta["paired_authorization"]["n"]
        - reverify["paired_authorization"]["both_correct"] / reverify["paired_authorization"]["n"]
    )
    both_nonzero = all(reverify[mode]["correct"] > 0 for mode in ("anchored", "dynamic"))
    if overall_gap <= 0.05 and both_nonzero and max(mode_gaps) <= 0.10 and pair_gap <= 0.10:
        return "substitution_supported"
    mode_rates = [reverify[mode]["correct"] / reverify[mode]["n"] for mode in ("anchored", "dynamic")]
    pair_rate = reverify["paired_authorization"]["both_correct"] / reverify["paired_authorization"]["n"]
    if abs(mode_rates[0] - mode_rates[1]) >= 0.40 and pair_rate <= 0.50:
        return "complementary_policy_result"
    if (reverify["other_visible_target"] + reverify["api_or_parse_errors"]) / reverify["n"] >= 0.20:
        return "grounding_limited_result"
    return "mixed_result"


def build_report(data: Path, glm_reverify: Path, glm_cta: Path, rule_v2: Path) -> dict:
    tasks = load_jsonl(data)
    if len(tasks) != 240 or len({task["id"] for task in tasks}) != 240:
        raise ValueError("Expected 240 unique v7 tasks")
    methods = {
        "entity_lock_analogue": scored_rows(
            tasks, {task["id"]: entity_lock_target(task) for task in tasks}, "entity_lock_analogue"
        ),
        "glm_self_reverify_author_adaptation": scored_rows(
            tasks, indexed_targets(glm_reverify), "glm_self_reverify_author_adaptation"
        ),
        "exact_cta_frozen": scored_rows(tasks, indexed_targets(glm_cta), "exact_cta_frozen"),
        "handcrafted_rule_v2_post_hoc": scored_rows(
            tasks, indexed_targets(rule_v2), "handcrafted_rule_v2_post_hoc"
        ),
    }
    summaries = {name: slice_summary(rows) for name, rows in methods.items()}
    raw = load_jsonl(glm_reverify)
    audit = {
        "rows": len(raw),
        "sha256": file_sha256(glm_reverify),
        "request_attempts": sum(row.get("api_request_attempts", 0) for row in raw),
        "retries": sum(row.get("api_retries", 0) for row in raw),
        "tokens": sum(
            sum((usage or {}).get("total_tokens", 0) or 0 for usage in row.get("usage", []))
            for row in raw
        ),
        "latency_s": sum(row.get("latency_s", 0.0) for row in raw),
    }
    return {
        "protocol": "reports/TRI_binding_drift_author_adaptation_v7_full_protocol.md",
        "status": "post_primary_author_adaptation",
        "dataset_sha256": file_sha256(data),
        "n_tasks": len(tasks),
        "summaries": summaries,
        "paired_comparison": cluster_bootstrap_delta(
            methods["exact_cta_frozen"], methods["glm_self_reverify_author_adaptation"]
        ),
        "interpretation_gate": classify_gate(
            summaries["exact_cta_frozen"], summaries["glm_self_reverify_author_adaptation"]
        ),
        "post_run_information_audit": {
            "status": "not_information_matched_to_cta",
            "verifier_inputs": ["instruction", "refreshed_state"],
            "omitted_inputs": ["initial_state", "resolved_pre_refresh_id"],
            "preserve_changed_winner_tasks": sum(
                task["binding"] == "anchored"
                and task["pre_refresh_target"] != task["post_refresh_target"]
                for task in tasks
            ),
            "performance_comparison_is_confirmatory": False,
            "reason": (
                "Unlike Binding Drift's uniquely identifying step1 referent, a TRI ranking "
                "selector does not recover its former winner from the refreshed state alone."
            ),
        },
        "run_audit": audit,
    }


def markdown(report: dict) -> str:
    lines = [
        "# Binding Drift Author-Adaptation Full v7 Report",
        "",
        "This is a post-primary author adaptation on TRI tasks, not an official Binding Drift result.",
        "",
        "| Method | Overall | Preserve | Reevaluate | Pair success | Flip | Stable | Name collision | Other visible | Errors |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method, row in report["summaries"].items():
        pair = row["paired_authorization"]
        updates = row["by_update"]
        lines.append(
            f"| {method} | {row['correct']}/{row['n']} | "
            f"{row['anchored']['correct']}/{row['anchored']['n']} | "
            f"{row['dynamic']['correct']}/{row['dynamic']['n']} | "
            f"{pair['both_correct']}/{pair['n']} | "
            f"{updates['flip']['correct']}/{updates['flip']['n']} | "
            f"{updates['stable']['correct']}/{updates['stable']['n']} | "
            f"{updates['name_collision']['correct']}/{updates['name_collision']['n']} | "
            f"{row['other_visible_target']} | {row['api_or_parse_errors']} |"
        )
    comparison = report["paired_comparison"]
    lo, hi = comparison["cluster_bootstrap_ci95"]
    lines.extend([
        "",
        "## Frozen interpretation gate",
        "",
        f"- Outcome: `{report['interpretation_gate']}`.",
        f"- CTA minus reverify: {100 * comparison['delta']:.1f} points; "
        f"cluster-bootstrap 95% CI [{100 * lo:.1f}, {100 * hi:.1f}].",
        "",
        "## Post-run information audit",
        "",
        "The frozen gate describes the observed output pattern but is not a fair CTA performance",
        "comparison. The adapted verifier receives the instruction and refreshed state, but",
        "neither the initial state nor the resolved pre-refresh ID. Unlike Binding Drift's",
        "uniquely identifying step-1 referent, a TRI ranking selector cannot recover its former",
        "winner from the refreshed state after a changed-winner transition. We therefore retain",
        "this result as an interface audit; the matched full-history and Generic-ledger conditions",
        "are the information-matched baselines.",
        "",
        "## Mechanism errors",
        "",
        "| Method | Preserve substitutions | Reevaluate premature locks |",
        "|---|---:|---:|",
    ])
    for method, row in report["summaries"].items():
        lines.append(
            f"| {method} | {row['anchored']['drift_to_refreshed_winner']} | "
            f"{row['dynamic']['premature_lock']} |"
        )
    lines.extend([
        "",
        "## Run audit",
        "",
        f"- Rows: {report['run_audit']['rows']}",
        f"- Requests/retries: {report['run_audit']['request_attempts']}/{report['run_audit']['retries']}",
        f"- Tokens: {report['run_audit']['tokens']}",
        f"- Total recorded latency: {report['run_audit']['latency_s']:.1f} seconds",
        "",
        "This disclosed interface difference and the use of TRI tasks prevent interpreting the",
        "result as an official reproduction, an information-matched CTA comparison, or evidence",
        "about Binding Drift's original initial-misbinding benchmark.",
    ])
    return "\n".join(lines) + "\n"
