from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "figure_ready"
OUTPUT = ROOT / "data" / "key_results_long.csv"
FIELDS = [
    "experiment",
    "dataset",
    "model",
    "condition",
    "metric",
    "numerator",
    "denominator",
    "value",
    "unit",
    "ci95_low",
    "ci95_high",
    "evidence_status",
    "source_file",
    "notes",
]


def read(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def add(
    out: list[dict[str, str]],
    *,
    experiment: str,
    dataset: str,
    model: str,
    condition: str,
    metric: str,
    numerator: str = "",
    denominator: str = "",
    value: str = "",
    unit: str = "percent",
    ci95_low: str = "",
    ci95_high: str = "",
    evidence_status: str,
    source_file: str,
    notes: str = "",
) -> None:
    values = locals().copy()
    out.append({field: values[field] for field in FIELDS})


def split_fraction(value: str) -> tuple[str, str]:
    if not value or "/" not in value:
        return "", ""
    return tuple(value.split("/", 1))  # type: ignore[return-value]


def main() -> None:
    out: list[dict[str, str]] = []

    name = "matched_pairacc_and_marginals.csv"
    for row in read(name):
        common = dict(
            experiment="PairAcc / identifiability",
            dataset=row["dataset"],
            model=row["model"],
            condition=f"{row['controller']}:{row['slice']}",
            evidence_status="post-primary replication/audit; zero API",
            source_file=name,
        )
        for metric, num, val in (
            ("preserve_accuracy", row["preserve_correct"], row["preserve_accuracy_pct"]),
            ("reevaluate_accuracy", row["reevaluate_correct"], row["reevaluate_accuracy_pct"]),
            ("pairacc", row["both_correct"], row["pairacc_pct"]),
        ):
            add(out, metric=metric, numerator=num, denominator=row["pairs"], value=val, **common)

    name = "main_figure_paired_scores.csv"
    for row in read(name):
        if row["panel"] not in {"pairacc", "e2e"}:
            continue
        add(
            out,
            experiment="Matched-call decision visibility",
            dataset=row["dataset"],
            model=row["model"],
            condition=f"{row['left_condition']}->{row['right_condition']}",
            metric=f"{row['metric']}_effect",
            numerator=f"{row['left_num']}->{row['right_num']}",
            denominator=row["left_den"],
            value=row["difference_pp"],
            unit="percentage_points",
            ci95_low=row["ci95_low_pp"],
            ci95_high=row["ci95_high_pp"],
            evidence_status="post-primary replication/audit",
            source_file=name,
            notes="PairAcc and E2E intervals are separate, not a joint confidence region.",
        )

    name = "revision_decision_visible_gains.csv"
    for row in read(name):
        add(
            out,
            experiment=row["audit_id"],
            dataset=row["audit_label"],
            model=row["model"],
            condition=f"{row['left_condition']}->{row['right_condition']}",
            metric=f"{row['metric']}_effect",
            value=row["difference_pp"],
            unit="percentage_points",
            ci95_low=row["ci95_low_pp"],
            ci95_high=row["ci95_high_pp"],
            evidence_status="post-primary replication/audit",
            source_file=name,
            notes=f"rows={row['rows']}; clusters={row['clusters']}",
        )

    name = "revision_source_grounded_by_source.csv"
    for row in read(name):
        add(
            out,
            experiment=row["audit_id"],
            dataset=row["source_slice"],
            model=row["model"],
            condition=row["condition"],
            metric=row["metric"],
            numerator=row["numerator"],
            denominator=row["denominator"],
            value=row["rate_pct"],
            ci95_low=row["ci95_low_pct"],
            ci95_high=row["ci95_high_pct"],
            evidence_status="post-primary source-derived controlled contrast",
            source_file=name,
            notes="Not a native benchmark score or prevalence estimate.",
        )

    name = "v7_e2e_wrong_writes.csv"
    for row in read(name):
        common = dict(
            experiment="v7 core replication and deterministic replay",
            dataset=row["dataset"],
            model=row["model"],
            condition=row["controller"],
            evidence_status="post-primary replication/audit",
            source_file=name,
        )
        add(
            out,
            metric="e2e_accuracy",
            denominator=row["n_tasks"],
            value=row["e2e_accuracy_pct"],
            **common,
        )
        for metric, field in (
            ("pairacc", "pairacc"),
            ("conditional_substitution", "conditional_substitution"),
        ):
            num, den = split_fraction(row[field])
            value = str(100 * int(num) / int(den)) if den else ""
            add(out, metric=metric, numerator=num, denominator=den, value=value, **common)
        for metric, field in (
            ("core_substitution_writes", "core_substitution_writes"),
            ("all_wrong_writes", "all_wrong_writes"),
            ("non_core_wrong_writes", "non_core_wrong_writes"),
        ):
            add(out, metric=metric, numerator=row[field], unit="count", **common)

    name = "v7_shared_eligible_pairacc_and_substitution.csv"
    for row in read(name):
        common = dict(
            experiment="v7 shared eligibility",
            dataset="v7",
            model=row["model"],
            condition=row["controller"],
            evidence_status="post-primary replication/audit; zero API",
            source_file=name,
        )
        if row["substitutions"]:
            add(
                out,
                metric="shared_eligible_substitution",
                numerator=row["substitutions"],
                denominator=row["shared_eligible"],
                value=row["substitution_rate_pct"],
                **common,
            )
        add(
            out,
            metric="pairacc",
            numerator=row["pairacc_both_correct"],
            denominator=row["pairacc_pairs"],
            value=row["pairacc_pct"],
            ci95_low=row["pairacc_ci95_low_pct"],
            ci95_high=row["pairacc_ci95_high_pct"],
            **common,
        )

    name = "sqlite_model_facing_outcomes.csv"
    for row in read(name):
        common = dict(
            experiment="40-task model-facing SQLite",
            dataset="SQLite trajectory test",
            model=row["model"],
            condition=row["controller"],
            evidence_status="secondary frozen execution test",
            source_file=name,
        )
        for metric, field in (
            ("correct_final_state", "correct_final_state"),
            ("core_tri_write", "core_tri_write"),
            ("fallback_wrong_write", "fallback_wrong_write"),
            ("unneeded_reject", "unneeded_reject"),
        ):
            add(
                out,
                metric=metric,
                numerator=row[field],
                denominator=row["tasks"],
                value=str(100 * int(row[field]) / int(row["tasks"])),
                **common,
            )
        for prefix in ("strict_core", "stable"):
            num = row[f"{prefix}_writes"]
            den = row[f"{prefix}_opportunities"]
            add(
                out,
                metric=f"{prefix}_write_rate",
                numerator=num,
                denominator=den,
                value=str(100 * int(num) / int(den)),
                **common,
            )

    name = "revision_enforcement_and_failures.csv"
    for row in read(name):
        common = dict(
            experiment=row["audit_id"],
            dataset=row["audit_label"],
            model=row["model"],
            condition="decision_enforced vs decision_visible",
            evidence_status="post-primary zero-call enforcement audit",
            source_file=name,
            notes=f"rows={row['rows']}; clusters={row['clusters']}",
        )
        for metric in (
            "repairs",
            "harms",
            "compiler_failures",
            "history_actor_failures",
            "visible_actor_failures",
            "incomplete_tasks",
        ):
            add(out, metric=metric, numerator=row[metric], unit="count", **common)

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(out)
    print(f"wrote {len(out)} normalized result rows to {OUTPUT}")


if __name__ == "__main__":
    main()
