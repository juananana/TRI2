# AAAI-27 Submission Compliance Audit

**Audit date:** 2026-07-24 (Asia/Shanghai)

**Scope:** current anonymous main PDF, source, supplement, and reproducibility checklist.

**Official sources:**

- [AAAI-27 Main Technical Track Call](https://aaai.org/conference/aaai/aaai-27/main-technical-track-call/)
- [AAAI-27 Submission Instructions](https://aaai.org/conference/aaai/aaai-27/submission-instructions/)
- [AAAI-27 Supplementary Material](https://aaai.org/conference/aaai/aaai-27/supplementary-material/)
- AAAI-27 Author Kit, local official copy: `AuthorKit27/AnonymousSubmission2027.tex`

This is a format and submission-readiness audit, not a scientific endorsement or a replacement
for the final anonymous-archive audit.

## Verified From Local Artifacts

| Requirement | Status | Evidence |
|---|---|---|
| Main PDF has at most 9 pages | Pass | `AnonymousSubmission2027.pdf` has 9 Letter pages. |
| Pages 8-9 are references only | Pass | Rendered pages 8 and 9 contain bibliography entries only. |
| Main content is within 7 pages | Pass | Body ends on page 7; bibliography begins on page 8. |
| US Letter two-column AAAI style | Pass | 612 x 792 pt PDF and `aaai2027.sty` build. |
| Anonymous author block and no acknowledgements | Pass | Main and supplement use `Anonymous Submission`; no acknowledgement section or author-identifying URL was found in TeX. |
| Figure labels and callouts are at least 9 pt | Pass | All three main-paper figure PDFs use 9.2 pt or larger source text; final inclusion scales retain at least 9 pt. |
| Figure captions are 10 pt roman | Pass | Captions use the unmodified AAAI caption setup; no local caption sizing or styling override is present. |
| Tables are 9 pt or larger and are not resized | Pass | All three main-paper tables use `\small` (AAAI 9 pt); no `resizebox`, `scalebox`, or table-spacing override remains. |
| Figure strokes and color accessibility | Pass | Minimum scripted stroke is 0.5 pt; text-color contrast is at least 4.57:1; model series also use circle/square shapes and labels. |
| Fonts embedded and no Type 3 fonts | Pass | Recursive page/Form-XObject audit finds 21 font resources, all embedded Type 1 or TrueType; zero Type 3 or unembedded fonts. |
| No embedded links, bookmarks, encryption, or page numbers | Pass | PDF has no annotations or outlines, is unencrypted, and the submission style suppresses page numbers. |
| PDF version and high-resolution format | Pass | PDF version 1.7, US Letter, approximately 379 KB, and vector PDF figures. |
| Forbidden main-paper commands/packages | Pass | No `clearpage`, `setlength`, `resizebox`, `trim`, `clip`, negative spacing, `hyperref`, or geometry package appears in the main source. |
| Undefined references/citations | Pass | No undefined citation/reference or overfull-box warning found in the compiled logs. |
| Supplement and reproducibility checklist build | Pass | Both built successfully in the current workspace. |
| Critical evidence in main text | Pass | Main text includes the closest-neighbor boundary, policy-identifiability table, controls, v3/v7 results, full-history baseline, mixed external evidence, and limitations. |
| Terminology, chronology, and cross-reference consistency | Pass | Static audit checks first-use expansions for nine abbreviations, all citation keys, all cross-references, table terminology, primary/post-primary chronology, and abstract/conclusion scope boundaries. |
| AI-assistance disclosure | Pass | The supplement discloses language editing, code assistance, and internal review; it excludes authorship, citation, annotation, and independent-human-evidence roles. |

## Current Clean-Room Artifact Status

- Rebuilt `submission/tri_anonymous_artifact_current.zip` from the revised paper and artifact
  sources: 1,066 payload files, 4,129,751 bytes; SHA-256
  `866a3368e4a535c58d2d3baa64a828a8427ed7765cb9c2b7f7c34897917267ee`.
- Extracted the exact ZIP into a fresh temporary directory and ran the documented pytest suite in
  the validated Python 3.12/pytest 9.1.1 environment: 216 archived tests passed. The development
  tree has one additional packaging-only test, for 217 local tests total. The machine's bare
  Homebrew Python 3.14 lacks pytest, consistent with the README's stated pytest prerequisite.
- Verified every `SOURCE_MANIFEST.tsv` SHA-256 entry and the ZIP CRC for every member.
- Scanned extracted content for author names, API-key patterns, and `/Users/` paths; no match was
  found.
- Verified that the completed external public-candidate annotation inventory, protocol, raw JSONL,
  and final report are required archive members; the final report has 160/160 pairs and zero
  strict-positive union/intersection.
- Verified the four paper-facing 96-task conditions directly from the archived reports
  (70/73/64/87 opportunities; 6/13/5/4 wrong writes; zero conditional mechanism errors). The
  unmatched Qwen-only sensitivity remains disclosed in the artifact and is not pooled with them.
- Verified the 320-row source-anchored transfer report and raw run are required archive members:
  306 rows are valid, 14 retained GLM parse/schema failures are reported, and the strict
  Preserve/Changed signal is limited to 2/7 Qwen ordinary-history AgentDojo rows versus 0/7 Stable.
- The clean-room pass exposed and repaired two packaging defects before this recorded pass: the
  generated README previously claimed a standard-library-only unittest command despite pytest
  imports, and the main-paper evidence audit assumed the development repository's paper path.

## Required Human Checks Before Upload

1. **OpenReview consistency:** Compare the actual registered title and abstract to the final PDF.
   AAAI warns that substantial abstract changes after registration can be rejected without review.
   Do not assume the local draft proves the registration was changed.
2. **Author/reviewer obligations:** Confirm every author is registered with the same OpenReview
   account and available for the reviewer pool unless an approved exception applies.
3. **Submission integrity:** Confirm this work is not under review elsewhere, is not a
   near-duplicate of an overlapping submission, and has no undisclosed author-identity leak in
   code, data, filenames, PDF metadata, or archived artifacts.
4. **Anonymous reproducibility package:** Clean-room extract the exact archive, run the documented
   smoke tests, verify all reported evidence has source-derived data/scripts, and scan every
   archive member for credentials and identity. Do not rely on a future-release statement.
5. **Checklist upload:** Upload the completed reproducibility checklist separately in the
   designated OpenReview field; it is not part of the 9-page main PDF.
6. **Existing human validation:** The AAAI-27 reproducibility checklist does not request an IRB,
   ethics-review, exemption, or protocol number. Report the verifiable protections: adult
   volunteers, informed consent, no sensitive personal data, de-identified released responses,
   and non-contingent compensation. Do not claim approval, exemption, or an institutional
   determination unless written documentation is later obtained. If an applicable institutional
   rule or a direct reviewer question requires the approval status, answer it accurately.

For checklist terminology, the separately uploaded anonymous artifact is the submission's
code/data appendix. The supplement's Artifact Map identifies its datasets, raw outputs, protocols,
scripts, manifests, and tests; these materials are not claimed to be embedded inside the PDF.

## Figure Review

The Author Kit states that text inside illustrations must be at least 9 pt, captions must be 10 pt
roman, lines must be at least 0.5 pt, color contrast must exceed 4.5:1, and figures must remain
decipherable without color. The earlier figures violated the 9 pt requirement. They were redrawn
rather than enlarged mechanically:

- Figure 1 now uses a compact one-column minimal-pair layout with a 9.2 pt minimum after scaling.
- Figure 2(a) uses a numbered 9.2 pt key instead of overlapping small labels.
- Figure 2(b) uses circle/square markers and removes redundant small numeric callouts.
- Orange and green text meet WCAG contrast on both white and tinted backgrounds.

No external paper artwork was copied or traced. All chart values remain source-derived.

## Corrected Violations

The following issues were present before this audit and are now corrected:

1. Figure text at approximately 5--6 pt, below the Author Kit's 9 pt minimum.
2. Main-paper tables set with `\scriptsize`, below the permitted 9 pt table minimum.
3. Two local `\setlength{\tabcolsep}` commands and a forced `\clearpage`, all listed as forbidden.
4. ReportLab's default unembedded Helvetica resource in included figure PDFs.
5. A 0.45 pt grid stroke and one green-on-tint contrast ratio below 4.5:1.

## Remaining Scientific Boundaries

The controlled diagnosis, public-suite coverage audit, and its limitations are properly visible.
Independent external confirmation and a double coverage audit are not being pursued for the
current submission. They remain future evidence needs and must not be reported as completed results.
