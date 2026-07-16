# AAAI-27 Submission Draft

This directory contains an anonymous AAAI-27 LaTeX draft for the TRI paper.

## Files

- `tri_aaai2027_submission.tex`: single-source anonymous submission draft.
- `tri_references.bib`: bibliography used by the draft.
- `figures/`: generated PDF figures included by the draft.
- `aaai2027.sty`: official AAAI-27 style file copied from `AuthorKit27`.
- `aaai2027.bst`: official AAAI-27 bibliography style copied from `AuthorKit27`.
- `ReproducibilityChecklist.tex`: filled AAAI reproducibility checklist.
- `tri_aaai2027_submission_source.zip`: clean source archive for submission. It intentionally excludes this local README.

## Compile

Run from this directory in a TeX environment:

```bash
pdflatex tri_aaai2027_submission.tex
bibtex tri_aaai2027_submission
pdflatex tri_aaai2027_submission.tex
pdflatex tri_aaai2027_submission.tex
```

In the current Codex environment, the PDF was compiled with TeX Live 2026 via:

```bash
/usr/local/texlive/2026/bin/universal-darwin/pdftex -fmt=pdflatex -interaction=nonstopmode -halt-on-error tri_aaai2027_submission.tex
```

## Checks Already Run

- No citation keys are missing from `tri_references.bib`.
- Static scan found no forbidden packages/commands such as `geometry`, `hyperref`, `times`, `newpage`, or negative `vspace`.
- Project unit tests pass: 8/8.
- Added lifecycle stress-test experiments and generated figure PDFs from run logs.
- Added a single-column lifecycle figure optimized for AAAI two-column layout.
- API key scan found no leaked `sk-*` key in outputs or project files.
