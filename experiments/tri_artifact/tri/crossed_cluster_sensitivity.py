"""Crossed-dependence sensitivity for the paired TRI-v3 package contrast."""

from __future__ import annotations

import json
import random
from hashlib import sha256
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .v3_cluster_report import percentile, success


DEFAULT_SEED = 20260725
DEFAULT_DRAWS = 10_000
EXPECTED_TASKS = 160
EXPECTED_DOMAINS = 8
EXPECTED_TEMPLATES = 20

RUNS = {
    "Qwen3.5": (
        "20260717T025047Z_Qwen_Qwen3.5-122B-A10B_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl",
        "20260717T030034Z_Qwen_Qwen3.5-122B-A10B_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl",
    ),
    "GLM-5.1": (
        "20260717T032824Z_Pro_zai-org_GLM-5.1_generic_structured_ledger_then_act_v3_language_clusters_nothinking.jsonl",
        "20260717T034201Z_Pro_zai-org_GLM-5.1_factorized_hybrid_compile_then_act_v3_language_clusters_nothinking.jsonl",
    ),
}


@dataclass(frozen=True)
class PairedOutcome:
    task_id: str
    domain: str
    template_id: str
    generic_success: int
    gated_success: int

    @property
    def delta(self) -> int:
        return self.gated_success - self.generic_success


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _index_iterable(
    rows: Iterable[dict[str, Any]], expected_tasks: int
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row_number, row in enumerate(rows, start=1):
        task = row.get("task")
        if not isinstance(task, dict) or not task.get("id"):
            raise ValueError(f"Row {row_number} has no nonempty task.id")
        task_id = str(task["id"])
        if task_id in indexed:
            raise ValueError(f"Duplicate task.id: {task_id}")
        indexed[task_id] = row
    if len(indexed) != expected_tasks:
        raise ValueError(f"Expected {expected_tasks} unique tasks, found {len(indexed)}")
    return indexed


def index_rows(path: Path, expected_tasks: int = EXPECTED_TASKS) -> dict[str, dict[str, Any]]:
    return _index_iterable(load_jsonl(path), expected_tasks)


def prepare_pairs(
    generic_rows: Iterable[dict[str, Any]] | dict[str, dict[str, Any]],
    gated_rows: Iterable[dict[str, Any]] | dict[str, dict[str, Any]],
    expected_tasks: int = EXPECTED_TASKS,
    expected_domains: int = EXPECTED_DOMAINS,
    expected_templates: int = EXPECTED_TEMPLATES,
) -> list[PairedOutcome]:
    generic = (
        generic_rows
        if isinstance(generic_rows, dict)
        else _index_iterable(generic_rows, expected_tasks)
    )
    gated = (
        gated_rows
        if isinstance(gated_rows, dict)
        else _index_iterable(gated_rows, expected_tasks)
    )
    if len(generic) != expected_tasks or len(gated) != expected_tasks:
        raise ValueError(
            f"Expected {expected_tasks} tasks in each run, found {len(generic)} and {len(gated)}"
        )
    if set(generic) != set(gated):
        missing_gated = sorted(set(generic) - set(gated))
        missing_generic = sorted(set(gated) - set(generic))
        raise ValueError(
            "Paired runs have different task.id sets: "
            f"missing from gated={missing_gated[:3]}, missing from generic={missing_generic[:3]}"
        )

    pairs: list[PairedOutcome] = []
    cells: Counter[tuple[str, str]] = Counter()
    for task_id in sorted(generic):
        generic_task = generic[task_id].get("task")
        gated_task = gated[task_id].get("task")
        if generic_task != gated_task:
            raise ValueError(f"Task metadata mismatch for task.id {task_id}")
        domain = str(generic_task.get("domain") or "")
        template_id = str(generic_task.get("template_id") or "")
        if not domain or not template_id:
            raise ValueError(f"Missing domain or template_id for task.id {task_id}")
        cells[(domain, template_id)] += 1
        pairs.append(
            PairedOutcome(
                task_id=task_id,
                domain=domain,
                template_id=template_id,
                generic_success=success(generic[task_id]),
                gated_success=success(gated[task_id]),
            )
        )

    domains = sorted({pair.domain for pair in pairs})
    templates = sorted({pair.template_id for pair in pairs})
    if len(domains) != expected_domains:
        raise ValueError(f"Expected {expected_domains} domains, found {len(domains)}")
    if len(templates) != expected_templates:
        raise ValueError(
            f"Expected {expected_templates} language-template clusters, found {len(templates)}"
        )
    expected_cells = {(domain, template) for domain in domains for template in templates}
    if set(cells) != expected_cells or any(count != 1 for count in cells.values()):
        missing = sorted(expected_cells - set(cells))
        repeated = sorted(cell for cell, count in cells.items() if count != 1)
        raise ValueError(
            "Inventory is not a complete one-row-per-cell domain-template cross: "
            f"missing={missing[:3]}, repeated={repeated[:3]}"
        )
    return pairs


def paired_delta(pairs: list[PairedOutcome]) -> float:
    if not pairs:
        raise ValueError("Cannot compute a paired delta from zero tasks")
    return sum(pair.delta for pair in pairs) / len(pairs)


def _interval(values: list[float]) -> list[float]:
    return [percentile(values, 0.025), percentile(values, 0.975)]


def _one_way_bootstrap(
    pairs: list[PairedOutcome], field: str, draws: int, seed: int
) -> list[float]:
    groups: dict[str, list[PairedOutcome]] = defaultdict(list)
    for pair in pairs:
        groups[str(getattr(pair, field))].append(pair)
    names = sorted(groups)
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(draws):
        sampled = [pair for _ in names for pair in groups[rng.choice(names)]]
        values.append(paired_delta(sampled))
    return values


def _two_way_pigeonhole_bootstrap(
    pairs: list[PairedOutcome], draws: int, seed: int
) -> list[float]:
    domains = sorted({pair.domain for pair in pairs})
    templates = sorted({pair.template_id for pair in pairs})
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(draws):
        domain_counts = Counter(rng.choice(domains) for _ in domains)
        template_counts = Counter(rng.choice(templates) for _ in templates)
        weighted_sum = 0
        total_weight = 0
        for pair in pairs:
            weight = domain_counts[pair.domain] * template_counts[pair.template_id]
            weighted_sum += weight * pair.delta
            total_weight += weight
        if total_weight == 0:
            raise AssertionError("Complete crossed resampling produced zero total weight")
        values.append(weighted_sum / total_weight)
    return values


def sensitivity_intervals(
    pairs: list[PairedOutcome], draws: int = DEFAULT_DRAWS, seed: int = DEFAULT_SEED
) -> dict[str, dict[str, Any]]:
    if draws <= 0:
        raise ValueError("draws must be positive")
    point = paired_delta(pairs)
    distributions = {
        "language_template": _one_way_bootstrap(
            pairs, "template_id", draws=draws, seed=seed
        ),
        "domain": _one_way_bootstrap(pairs, "domain", draws=draws, seed=seed),
        "two_way_pigeonhole": _two_way_pigeonhole_bootstrap(
            pairs, draws=draws, seed=seed
        ),
    }
    units = {
        "language_template": "20 language-template clusters with replacement",
        "domain": "8 domains with replacement",
        "two_way_pigeonhole": (
            "independent domain and language-template resampling with product weights"
        ),
    }
    results: dict[str, dict[str, Any]] = {}
    for method, values in distributions.items():
        ci = _interval(values)
        results[method] = {
            "point_estimate": point,
            "ci95": ci,
            "width": ci[1] - ci[0],
            "resampling_unit": units[method],
        }
    return results


def build_report(
    run_dir: Path, draws: int = DEFAULT_DRAWS, seed: int = DEFAULT_SEED
) -> dict[str, Any]:
    models = []
    widest_candidates = []
    reference_tasks: dict[str, dict[str, Any]] | None = None
    for model, (generic_name, gated_name) in RUNS.items():
        generic = index_rows(run_dir / generic_name)
        gated = index_rows(run_dir / gated_name)
        current_tasks = {task_id: row["task"] for task_id, row in generic.items()}
        if reference_tasks is not None and current_tasks != reference_tasks:
            raise ValueError("Model runs use inconsistent task inventory metadata")
        reference_tasks = current_tasks
        inventory_hash = sha256(
            json.dumps(
                current_tasks, ensure_ascii=True, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        pairs = prepare_pairs(generic, gated)
        methods = sensitivity_intervals(pairs, draws=draws, seed=seed)
        widest_method = max(methods, key=lambda method: methods[method]["width"])
        widest = methods[widest_method]
        row = {
            "model": model,
            "source_run_evidence_status": (
                "primary/frozen" if model == "Qwen3.5" else "post-primary replication/audit"
            ),
            "generic_file": str(Path("runs") / generic_name),
            "lifecycle_gated_file": str(Path("runs") / gated_name),
            "task_inventory_sha256": inventory_hash,
            "matched_tasks": len(pairs),
            "domains": len({pair.domain for pair in pairs}),
            "language_template_clusters": len({pair.template_id for pair in pairs}),
            "cross_cells": len({(pair.domain, pair.template_id) for pair in pairs}),
            "generic_successes": sum(pair.generic_success for pair in pairs),
            "lifecycle_gated_successes": sum(pair.gated_success for pair in pairs),
            "point_estimate": paired_delta(pairs),
            "methods": methods,
            "widest_interval_method": widest_method,
            "widest_ci95": widest["ci95"],
            "widest_width": widest["width"],
        }
        models.append(row)
        widest_candidates.append((widest["width"], model, widest_method, widest["ci95"]))

    width, model, method, ci = max(widest_candidates)
    return {
        "title": "TRI-v3 Crossed-Dependence Statistical Sensitivity Audit",
        "evidence_status": "post-primary replication/audit",
        "designed_after_primary_result": True,
        "zero_api": True,
        "estimand": "Lifecycle-Gated minus Generic paired end-to-end exact-target accuracy",
        "seed": seed,
        "draws": draws,
        "interval": "95% percentile bootstrap interval",
        "primary_ci_replaced": False,
        "confirmatory_multiplicity_adjusted_inference": False,
        "models": models,
        "overall_widest_interval": {
            "model": model,
            "method": method,
            "ci95": ci,
            "width": width,
        },
    }


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def markdown(report: dict[str, Any]) -> str:
    labels = {
        "language_template": "Language-template cluster",
        "domain": "Domain cluster",
        "two_way_pigeonhole": "Two-way pigeonhole",
    }
    lines = [
        f"# {report['title']}",
        "",
        "**Evidence status:** `post-primary replication/audit`; zero API. This analysis was",
        "designed after observing the primary result. It does not replace the primary confidence",
        "interval and does not provide multiplicity-adjusted confirmatory inference.",
        "",
        f"Seed: `{report['seed']}`. Bootstrap draws per method and model: "
        f"`{report['draws']:,}`.",
        "",
        "| Model (source-run status) | Generic | Lifecycle-Gated | Delta | Dependence assumption | 95% interval | Width |",
        "|---|---:|---:|---:|---|---:|---:|",
    ]
    for row in report["models"]:
        for method, result in row["methods"].items():
            lo, hi = result["ci95"]
            lines.append(
                f"| {row['model']} ({row['source_run_evidence_status']}) | "
                f"{row['generic_successes']}/{row['matched_tasks']} | "
                f"{row['lifecycle_gated_successes']}/{row['matched_tasks']} | "
                f"{_pct(row['point_estimate'])} | {labels[method]} | "
                f"[{_pct(lo)}, {_pct(hi)}] | {_pct(result['width'])} |"
            )

    lines.extend(["", "## Widest intervals", ""])
    for row in report["models"]:
        lo, hi = row["widest_ci95"]
        lines.append(
            f"- {row['model']}: {labels[row['widest_interval_method']]}, "
            f"[{_pct(lo)}, {_pct(hi)}], width {_pct(row['widest_width'])}."
        )
    overall = report["overall_widest_interval"]
    lo, hi = overall["ci95"]
    lines.extend(
        [
            "",
            f"The widest interval overall is {overall['model']} under "
            f"{labels[overall['method']]} resampling: [{_pct(lo)}, {_pct(hi)}] "
            f"(width {_pct(overall['width'])}).",
            "",
            "All rows use the same complete 8 x 20 crossed inventory after exact task-ID, full",
            "task-metadata, and cross-model inventory checks. This sensitivity addresses",
            "dependence on authored generator axes. It does not establish natural-world prevalence",
            "or isolate a controller component effect.",
        ]
    )
    return "\n".join(lines) + "\n"
