from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
PAPER = REPOSITORY / "paper"
SUBMISSION = REPOSITORY / "submission"

ROOTS = (
    "data",
    "runs",
    "reports",
    "tri",
    "scripts",
    "tests",
    "external_pilots",
    "human_validation",
)
TOP_LEVEL = ("README.md", "PROTOCOL.md")
PAPER_FILES = (
    "AnonymousSubmission2027.tex",
    "aaai2027.bib",
    "aaai2027.bst",
    "aaai2027.sty",
    "ReproducibilityChecklist.tex",
    "supplementary_material.tex",
)

HUMAN_PUBLIC_FILES = {
    Path("human_validation/analysis.json"),
    Path("human_validation/analysis.md"),
    Path("human_validation/model_human_subset.json"),
    Path("human_validation/model_human_subset.md"),
    Path("human_validation/paraphrase_authoring.csv"),
    Path("human_validation/selected_sources.jsonl"),
    Path("human_validation/natural_elicitation_writer_form_zh.csv"),
    Path("human_validation/natural_elicitation_annotator_form_zh.csv"),
}

SECRET_PATTERN = re.compile(rb"sk-[A-Za-z0-9_-]{20,}")
LOCAL_HOME_PATTERN = re.compile(rb"/Users/[^/\s\"']+")
INTERNAL_REPORT_PREFIXES = (
    "AAAI",
    "TRI_AAAI",
    "TRI_paper_introduction_for_review",
    "paper_iteration_blueprint",
)
PACKAGING_ONLY = {
    Path("scripts/build_current_supplement.py"),
    Path("tests/test_build_current_supplement.py"),
}


def excluded(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    parts = set(relative.parts)
    if relative.parts[:2] == ("external_pilots", "appworld_runtime"):
        return True
    if parts & {"__pycache__", ".pytest_cache", ".git"}:
        return True
    if path.name.startswith(".") or path.suffix in {".pyc", ".xlsx"}:
        return True
    if relative in PACKAGING_ONLY:
        return True
    if relative.parts[0] == "runs" and path.stat().st_size == 0:
        return True
    if relative.parts[0] == "reports" and path.name.startswith(INTERNAL_REPORT_PREFIXES):
        return True
    if relative.parts[0] == "human_validation":
        return not (
            relative in HUMAN_PUBLIC_FILES
            or relative.parts[:2] == ("human_validation", "normalized_returns")
        )
    return False


def submission_clean_data(source: Path) -> bytes:
    data = source.read_bytes()
    relative = source.relative_to(ROOT) if source.is_relative_to(ROOT) else None
    drop_columns: set[str] = set()
    if relative and relative.parts[:2] == ("human_validation", "normalized_returns"):
        drop_columns = {"comment"}
    elif relative == Path("human_validation/paraphrase_authoring.csv"):
        drop_columns = {"author_notes"}
    if drop_columns:
        reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
        fieldnames = [name for name in (reader.fieldnames or []) if name not in drop_columns]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in reader:
            writer.writerow({name: row.get(name, "") for name in fieldnames})
        data = output.getvalue().encode()
    if b"\x00" not in data:
        data = LOCAL_HOME_PATTERN.sub(b"$HOME", data)
    if SECRET_PATTERN.search(data):
        raise ValueError(f"possible API key in {source}")
    if b"/Users/" in data:
        raise ValueError(f"non-anonymous local path in {source}")
    return data


def source_files() -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for name in TOP_LEVEL:
        source = ROOT / name
        files.append((source, Path("tri_artifact") / name))
    for root_name in ROOTS:
        source_root = ROOT / root_name
        for source in sorted(source_root.rglob("*")):
            if source.is_file() and not excluded(source):
                files.append((source, Path("tri_artifact") / source.relative_to(ROOT)))
    for name in PAPER_FILES:
        source = PAPER / name
        files.append((source, Path("tri_artifact") / "paper" / name))
    for source in sorted((PAPER / "Figures").glob("*.pdf")):
        files.append((source, Path("tri_artifact") / "paper" / "Figures" / source.name))
    return files


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(output: Path) -> None:
    files = source_files()
    seen: set[Path] = set()
    manifest_rows = ["sha256\tbytes\tpath"]
    payloads: list[tuple[Path, bytes]] = []
    for source, archive_path in files:
        if archive_path in seen:
            raise ValueError(f"duplicate archive path: {archive_path}")
        seen.add(archive_path)
        data = submission_clean_data(source)
        payloads.append((archive_path, data))
        manifest_rows.append(f"{digest(data)}\t{len(data)}\t{archive_path.as_posix()}")

    readme = """# TRI Current Reproducibility Artifact

This archive corresponds to the current TRI AAAI manuscript. It contains frozen datasets,
raw model outputs, protocols, report generators, tests, external-pilot code, paper source,
and final figure PDFs. It also contains de-identified normalized human responses and aggregate
analysis, while API credentials, private answer mappings, workbooks, coordination forms, and
participant-identifying materials are excluded.

Run `PYTHONPATH=. python3 -m unittest discover -s tests` from `tri_artifact/` for the
included dependency-free scientific tests. The archive-packaging test is intentionally excluded
because it requires the parent submission tree. ToolSandbox tests require the pinned environment documented in
`external_pilots/toolsandbox_tri/README.md`. The downloaded AppWorld package, databases, and
released public trajectories are excluded; setup is documented in
`external_pilots/appworld_tri/README.md`. See `reports/` for frozen protocols and
machine-readable result reports. `SOURCE_MANIFEST.tsv` records the SHA-256 and byte size of
every archived source file.
""".encode()
    readme_path = Path("tri_artifact") / "ARTIFACT_README.md"
    payloads.append((readme_path, readme))
    manifest_rows.append(f"{digest(readme)}\t{len(readme)}\t{readme_path.as_posix()}")
    manifest = ("\n".join(manifest_rows) + "\n").encode()

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for archive_path, data in payloads:
                archive.writestr(archive_path.as_posix(), data)
            archive.writestr("tri_artifact/SOURCE_MANIFEST.tsv", manifest)
        with zipfile.ZipFile(temporary) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"corrupt archive member: {bad}")
            names = set(archive.namelist())
            required = {
                "tri_artifact/data/temporal_referent_v3_language_clusters.jsonl",
                "tri_artifact/tri/run_models.py",
                "tri_artifact/paper/AnonymousSubmission2027.tex",
                "tri_artifact/SOURCE_MANIFEST.tsv",
            }
            missing = required - names
            if missing:
                raise ValueError(f"missing required artifact files: {sorted(missing)}")
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(f"{output} ({output.stat().st_size} bytes; {len(payloads)} payload files)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(SUBMISSION / "tri_anonymous_artifact_current.zip"),
    )
    args = parser.parse_args()
    build(Path(args.output))


if __name__ == "__main__":
    main()
