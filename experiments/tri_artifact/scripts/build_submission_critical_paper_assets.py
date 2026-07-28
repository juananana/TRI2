#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
PAPER = REPOSITORY / "paper"
REPORTS = ROOT / "reports"
GENERATED = PAPER / "generated"
FIGURE_PYTHON = REPOSITORY / ".fig_venv" / "bin" / "python"
MODEL_ORDER = (
    "Qwen/Qwen3.5-122B-A10B",
    "Pro/zai-org/GLM-5.1",
    "deepseek-ai/DeepSeek-V4-Pro",
    "Pro/MiniMaxAI/MiniMax-M2.5",
)
MODEL_LABEL = {
    MODEL_ORDER[0]: "Qwen",
    MODEL_ORDER[1]: "GLM",
    MODEL_ORDER[2]: "DeepSeek",
    MODEL_ORDER[3]: "MiniMax",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:.1f}"


def interval(values: list[float | None]) -> str:
    if len(values) != 2 or values[0] is None or values[1] is None:
        return "NA"
    return f"[{100 * values[0]:.1f},{100 * values[1]:.1f}]"


def fraction(metric: dict[str, Any]) -> str:
    return f"{metric['numerator']}/{metric['denominator']}"


def ordered_models(report: dict[str, Any]) -> list[dict[str, Any]]:
    by_model = {item["model"]: item for item in report["models"]}
    if set(by_model) != set(MODEL_ORDER):
        raise ValueError(f"four complete model cells required; found {sorted(by_model)}")
    return [by_model[model] for model in MODEL_ORDER]


def _effect_text(model: dict[str, Any], family: str) -> str:
    if family == "convention":
        contrast = next(
            item for item in model["paired_differences"] if item["metric"] == "changed_pairacc"
        )
        values = contrast["ci95_state_cluster"]
        estimate = contrast["difference_right_minus_left"]
    else:
        contrast = model["decision_visible_minus_history"]["changed_pairacc"]
        values = contrast["ci95_cluster"]
        estimate = contrast["difference"]
    return f"{100 * estimate:+.1f} {interval(values)}"


def build_main(convention: dict[str, Any], matched: dict[str, Any]) -> str:
    convention_models = ordered_models(convention)
    matched_models = ordered_models(matched)
    convention_estimates = ", ".join(
        f"{MODEL_LABEL[item['model']]} {_effect_text(item, 'convention').split()[0]}"
        for item in convention_models
    )
    matched_estimates = ", ".join(
        f"{MODEL_LABEL[item['model']]} {_effect_text(item, 'matched').split()[0]}"
        for item in matched_models
    )
    convention_failures = sum(item["failures"]["incomplete_tasks"] for item in convention_models)
    matched_failures = sum(item["failures"]["incomplete_tasks"] for item in matched_models)
    return (
        "The equal-call controls separate natural-language convention from executable decision "
        "visibility (Figure~\\ref{fig:submission-critical-effects}). Convention-told effects are "
        f"model-conditional ({convention_estimates} pp), whereas Decision-visible improves changed "
        f"PairAcc for all four models ({matched_estimates} pp). The panels use different frozen "
        "inventories and are not pooled; Convention and decision-block runs contain "
        f"{convention_failures} and {matched_failures} incomplete ITT rows, respectively.\n\n"
        "\\begin{figure}[t]\n"
        "\\centering\n"
        "\\includegraphics[width=0.97\\columnwidth]{Figures/fig_submission_critical_pairacc_effects.pdf}\n"
        "\\caption{Post-primary equal-call contrasts. A: natural-language convention only "
        "(40 changed pairs). B: complete decision block visible to the actor (32 actionable changed "
        "pairs). Bars are cluster-bootstrap 95\\% CIs; inventories are separate and unpooled.}\n"
        "\\label{fig:submission-critical-effects}\n"
        "\\end{figure}\n"
    )


def build_supplement(convention: dict[str, Any], matched: dict[str, Any]) -> str:
    convention_models = ordered_models(convention)
    matched_models = ordered_models(matched)
    lines = [
        "\\subsection{Submission-critical convention and model-coverage audit}",
        "The following post-primary matrices were frozen in the submission-critical addendum. "
        "They retain authored gold and do not constitute independent-language evidence.",
        "",
        "\\begin{table}[H]",
        "\\centering",
        "\\small",
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "Model & Plain PairAcc & Convention PairAcc & Difference (95\\% CI) \\\\",
        "\\midrule",
    ]
    for item in convention_models:
        plain = item["metrics"]["plain_history"]["changed_pairacc"]
        told = item["metrics"]["convention_told"]["changed_pairacc"]
        lines.append(
            f"{MODEL_LABEL[item['model']]} & {fraction(plain)} & {fraction(told)} & "
            f"{_effect_text(item, 'convention')} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Convention-told natural-history control on 40 authored changed pairs. Both "
            "conditions make one actor call with byte-matched user payloads and receive no structured "
            "ID record, reference mode, compiler output, or gold. Differences are Convention minus Plain.}",
            "\\label{tab:supp-convention-told}",
            "\\end{table}",
            "",
            "\\begin{table}[H]",
            "\\centering",
            "\\small",
            "\\begin{tabular}{lrrr}",
            "\\toprule",
            "Model & History PairAcc & Visible PairAcc & Difference (95\\% CI) \\\\",
            "\\midrule",
        ]
    )
    for item in matched_models:
        history = item["metrics"]["history_only"]["changed_pairacc"]
        visible = item["metrics"]["decision_visible"]["changed_pairacc"]
        lines.append(
            f"{MODEL_LABEL[item['model']]} & {fraction(history)} & {fraction(visible)} & "
            f"{_effect_text(item, 'matched')} \\\\"
        )
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\caption{Four-model full-diagnostic matched-call audit on 32 actionable changed pairs. "
            "Decision-visible jointly exposes the compiler mode, bound ID, and selector restatement; "
            "the contrast is not an individual-field effect.}",
            "\\label{tab:supp-four-model-matched}",
            "\\end{table}",
            "",
        ]
    )
    source = REPORTS / "revision_source_grounded_repeat_v1.json"
    if source.is_file():
        repeat = load(source)
        lines.extend(
            [
                "\\paragraph{Source-derived repeat stability.}",
                "Temperature-zero repeats use the same 30 source-derived pairs and therefore measure "
                "endpoint repeatability rather than additional independent sample size.",
                "\\begin{table}[H]",
                "\\centering",
                "\\small",
                "\\begin{tabular}{llrrr}",
                "\\toprule",
                "Model & Pass & History & Visible & Difference \\\\",
                "\\midrule",
            ]
        )
        for item in repeat["passes"]:
            history = item["metrics"]["history_only"]["changed_pairacc"]
            visible = item["metrics"]["decision_visible"]["changed_pairacc"]
            effect = item["decision_visible_minus_history"]["changed_pairacc"]["difference"]
            lines.append(
                f"{MODEL_LABEL[item['model']]} & {item['label']} & {fraction(history)} & "
                f"{fraction(visible)} & {pct(effect)} pp \\\\"
            )
        lines.extend(
            [
                "\\bottomrule",
                "\\end{tabular}",
                "\\caption{Source-derived matched-call passes. Repeated passes do not increase the "
                "30-pair denominator; MiniMax is a first pass rather than a repeat.}",
                "\\label{tab:supp-source-repeat}",
                "\\end{table}",
                "",
            ]
        )
    external_paths = sorted(REPORTS.glob("toolsandbox_single_turn_*_repeat_v2.json"))
    if len(external_paths) == 4:
        lines.extend(
            [
                "\\paragraph{ToolSandbox-style null repeat.}",
                "The four versioned repeat cells preserve the original conditional denominator and "
                "keep upstream/process errors and wrong writes separate.",
                "\\begin{table}[H]",
                "\\centering",
                "\\small",
                "\\begin{tabular}{llrrrr}",
                "\\toprule",
                "Model & Interface & Rows & Opportunities & Mechanism errors & Wrong writes \\\\",
                "\\midrule",
            ]
        )
        for path in external_paths:
            report = load(path)
            cells = report["cells"]
            model = cells[0]["model"]
            controller = cells[0]["controller"]
            opportunities = sum(item["tri_opportunities"] for item in cells)
            errors = sum(item["unauthorized_rebindings"] + item["premature_locks"] for item in cells)
            writes = sum(item["wrong_entity_writes"] for item in cells)
            lines.append(
                f"{MODEL_LABEL[model]} & {controller.replace('_', ' ')} & 96 & {opportunities} & "
                f"{errors} & {writes} \\\\"
            )
        lines.extend(
            [
                "\\bottomrule",
                "\\end{tabular}",
                "\\caption{Repeat of the four paper-facing ToolSandbox-style cells. These are "
                "controlled external-style trajectories, not official ToolSandbox tasks or prevalence estimates.}",
                "\\label{tab:supp-toolsandbox-null-repeat}",
                "\\end{table}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build paper assets from complete submission-critical reports.")
    parser.add_argument(
        "--convention",
        type=Path,
        default=REPORTS / "convention_told_natural_history_v1.json",
    )
    parser.add_argument(
        "--matched",
        type=Path,
        default=REPORTS / "revision_full_diagnostic_four_model_v1.json",
    )
    args = parser.parse_args()
    convention, matched = load(args.convention), load(args.matched)
    ordered_models(convention)
    ordered_models(matched)
    if not FIGURE_PYTHON.is_file():
        raise FileNotFoundError(f"Figure environment not found: {FIGURE_PYTHON}")
    figure_script = PAPER / "tri_final_figures" / "plot_submission_critical_effects.py"
    subprocess.run(
        [
            str(FIGURE_PYTHON),
            str(figure_script),
            "--convention",
            str(args.convention),
            "--matched",
            str(args.matched),
        ],
        cwd=REPOSITORY,
        check=True,
    )
    figure_source = (
        PAPER / "tri_final_figures/outputs/fig_submission_critical_pairacc_effects_v1.pdf"
    )
    figure_destination = PAPER / "Figures/fig_submission_critical_pairacc_effects.pdf"
    shutil.copy2(figure_source, figure_destination)
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "submission_critical_main.tex").write_text(
        build_main(convention, matched), encoding="utf-8"
    )
    (GENERATED / "submission_critical_supplement.tex").write_text(
        build_supplement(convention, matched), encoding="utf-8"
    )
    print(GENERATED / "submission_critical_main.tex")
    print(GENERATED / "submission_critical_supplement.tex")
    print(figure_destination)


if __name__ == "__main__":
    main()
