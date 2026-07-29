#!/usr/bin/env python3
"""Audit the four selected TRI result figures and their formal paper assets."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PAPER = ROOT.parent


@dataclass(frozen=True)
class FigureAsset:
    name: str
    formal: Path
    candidate: Path
    manifest: Path
    grayscale: Path
    deuteranopia: Path


FIGURES = (
    FigureAsset(
        "Figure 3",
        PAPER / "Figures" / "result_policy_discrimination.pdf",
        ROOT / "outputs" / "figure3_palette_final_v3" / "figure3_palette_d_forest_ember.pdf",
        ROOT / "outputs" / "figure3_palette_final_v3" / "manifest.json",
        ROOT / "outputs" / "figure3_palette_final_v3" / "figure3_palette_d_forest_ember_grayscale.png",
        ROOT / "outputs" / "figure3_palette_final_v3" / "figure3_palette_d_forest_ember_deuteranopia.png",
    ),
    FigureAsset(
        "Figure 4",
        PAPER / "Figures" / "fig3_substitution_flow.pdf",
        ROOT / "outputs" / "result_closure_v6" / "result_conditional_pairing_ab.pdf",
        ROOT / "outputs" / "result_closure_v6" / "result_conditional_pairing_ab-manifest.json",
        ROOT / "outputs" / "result_closure_v6" / "result_conditional_pairing_ab-grayscale.png",
        ROOT / "outputs" / "result_closure_v6" / "result_conditional_pairing_ab-deuteranopia.png",
    ),
    FigureAsset(
        "Figure 5",
        PAPER / "Figures" / "fig4_sqlite_outcome_tree.pdf",
        ROOT / "outputs" / "figure5_integrated_profile_v1" / "figure5_integrated_profile.pdf",
        ROOT / "outputs" / "figure5_integrated_profile_v1" / "figure5_integrated_profile-manifest.json",
        ROOT / "outputs" / "figure5_integrated_profile_v1" / "figure5_integrated_profile-grayscale.png",
        ROOT / "outputs" / "figure5_integrated_profile_v1" / "figure5_integrated_profile-deuteranopia.png",
    ),
    FigureAsset(
        "Figure 6",
        PAPER / "Figures" / "fig_submission_critical_pairacc_effects.pdf",
        ROOT / "outputs" / "fig_submission_critical_pairacc_effects_v1.pdf",
        ROOT / "outputs" / "fig_submission_critical_pairacc_effects_v1-manifest.json",
        ROOT / "outputs" / "fig_submission_critical_pairacc_effects_v1-grayscale.png",
        ROOT / "outputs" / "fig_submission_critical_pairacc_effects_v1-deuteranopia.png",
    ),
)


def run(*command: str) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_file(path: Path, errors: list[str]) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        errors.append(f"missing or empty: {path}")


def audit_pdf(path: Path, errors: list[str]) -> None:
    font_output = run("pdffonts", str(path))
    font_lines = font_output.splitlines()[2:]
    if not font_lines:
        errors.append(f"no fonts reported: {path}")
    if "Type 3" in font_output:
        errors.append(f"Type 3 font: {path}")
    if any(re.search(r"\bno\b", line) for line in font_lines):
        errors.append(f"unembedded or unsubstituted font: {path}")

    info = run("pdfinfo", str(path))
    match = re.search(r"^Pages:\s+(\d+)$", info, flags=re.MULTILINE)
    if not match or int(match.group(1)) != 1:
        errors.append(f"expected one-page figure PDF: {path}")

    image_output = run("pdfimages", "-list", str(path))
    if any(re.match(r"^\s*\d+\s+\d+\s+", line) for line in image_output.splitlines()):
        errors.append(f"raster image embedded in vector figure: {path}")


def audit_figure(asset: FigureAsset) -> list[str]:
    errors: list[str] = []
    for path in (
        asset.formal,
        asset.candidate,
        asset.candidate.with_suffix(".svg"),
        asset.candidate.with_suffix(".png"),
        asset.manifest,
        asset.grayscale,
        asset.deuteranopia,
    ):
        require_file(path, errors)
    if errors:
        return errors

    if sha256(asset.formal) != sha256(asset.candidate):
        errors.append(f"formal asset differs from selected candidate: {asset.name}")

    manifest = json.loads(asset.manifest.read_text(encoding="utf-8"))
    minimum_text = float(manifest.get("minimum_text_pt", 0.0))
    if minimum_text < 7.0:
        errors.append(f"minimum text below 7 pt ({minimum_text:g}): {asset.name}")

    audit_pdf(asset.formal, errors)
    return errors


def main() -> None:
    all_errors: list[str] = []
    for asset in FIGURES:
        errors = audit_figure(asset)
        if errors:
            all_errors.extend(errors)
            print(f"FAIL {asset.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {asset.name}: hash, vector PDF, embedded fonts, >=7 pt, grayscale/CVD")

    if all_errors:
        raise SystemExit(1)
    print("PASS result figure system")


if __name__ == "__main__":
    main()
