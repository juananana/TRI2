# Temporal Referent Integrity (TRI)

AAAI-27 paper project for:

> Updating the World Is Not Rebinding the Target: Temporal Referent Integrity in Tool-Using Agents

## Current Project

The current repository is split into three visible working areas:

- `paper/`: manuscript sources, figures, PDFs, and official AAAI-named files.
- `experiments/tri_artifact/`: benchmark data, raw runs, controller code, reports, and tests.
- `submission/`: the anonymous artifact ZIP intended for upload.

- Main paper: `paper/AnonymousSubmission2027.tex`
- Main PDF: `paper/AnonymousSubmission2027.pdf`
- Supplement: `paper/supplementary_material.tex`
- Anonymous artifact: `submission/tri_anonymous_artifact_current.zip`
- Reproducibility source: `experiments/tri_artifact/`
- Chinese structure guide: `paper/项目结构说明.md`
- Paper working-directory guide: `paper/README.md`

The official AAAI filenames are intentionally unchanged for direct Overleaf use.

## Official Template

`AuthorKit27/` is the original AAAI-27 author kit and is retained as a clean reference. The
working manuscript does not modify or rename the official style and bibliography files.

## Repository Policy

- Experimental claims must be traceable to frozen data, raw runs, and analysis reports.
- API credentials must never be committed.
- Participant identities, private annotation mappings, raw workbooks, and coordination forms
  remain local and are excluded by `.gitignore` and by the anonymous artifact builder.
- Obsolete `outputs/` and the early `temporal_referent_integrity/` tree remain recoverable from
  Git history but are not part of the current working tree.
