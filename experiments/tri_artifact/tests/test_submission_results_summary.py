from __future__ import annotations

import json
from pathlib import Path

from scripts.build_submission_results_summary import FIGURES, REPORTS, build


def test_submission_results_summary_contains_all_declared_files(tmp_path: Path) -> None:
    output = tmp_path / "summary"
    manifest = build(output)
    assert len(manifest["entries"]) == len(REPORTS) + len(FIGURES)
    assert (output / "README.md").is_file()
    stored = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert stored["status"] == "source-derived submission evidence summary"
    assert all((output / entry["file"]).is_file() for entry in stored["entries"])
