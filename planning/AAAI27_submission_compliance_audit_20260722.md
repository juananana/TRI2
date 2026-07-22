# AAAI-27 Submission Compliance Audit

**Audit date:** 2026-07-22 (Asia/Shanghai)  
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
| Tables are 9 pt or larger and are not resized | Pass | Both main-paper tables use `\small` (AAAI 9 pt); no `resizebox`, `scalebox`, or table-spacing override remains. |
| Figure strokes and color accessibility | Pass | Minimum scripted stroke is 0.5 pt; text-color contrast is at least 4.57:1; model series also use circle/square shapes and labels. |
| Fonts embedded and no Type 3 fonts | Pass | Recursive page/Form-XObject audit finds 21 font resources, all embedded Type 1 or TrueType; zero Type 3 or unembedded fonts. |
| No embedded links, bookmarks, encryption, or page numbers | Pass | PDF has no annotations or outlines, is unencrypted, and the submission style suppresses page numbers. |
| PDF version and high-resolution format | Pass | PDF version 1.7, US Letter, 369 KB, and vector PDF figures. |
| Forbidden main-paper commands/packages | Pass | No `clearpage`, `setlength`, `resizebox`, `trim`, `clip`, negative spacing, `hyperref`, or geometry package appears in the main source. |
| Undefined references/citations | Pass | No undefined citation/reference or overfull-box warning found in the compiled logs. |
| Supplement and reproducibility checklist build | Pass | Both built successfully in the current workspace. |
| Critical evidence in main text | Pass | Main text includes the closest-neighbor boundary, controls, v3/v7 results, full-history baseline, external nulls, and limitations. |

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
The independent-human external confirmation, independent double coverage audit, and planned
mutation-time verifier remain `planned/unverified` and must not be reported as completed results.
