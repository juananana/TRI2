# R-SSA 20-Task Smoke: Run-Completion Amendment

Recorded: 2026-07-22, after Qwen completed and after the GLM process stopped following task 12.

The frozen protocol remains `TRI_rssa_20task_protocol.md` with original SHA-256
`6d8ee0da432b6133e7cfabd4b65ec156939ff0ffa1dc8bf07143b67fd8dbfe93`.

## Observed transport state

- Qwen output contains the complete ordered 20-task manifest.
- GLM output contains the first 12 ordered manifest tasks and no duplicate task IDs.
- Each retained GLM row records one completed compiler request.
- The existing 12 rows are immutable attempted observations and remain in the ITT denominator.
- No grounder or actor request was made for those rows because strict compiler parsing failed.

## Mechanical recovery

The runner gains `--resume`. It verifies that an existing output file is an exact prefix of the
frozen manifest, with matching model and dataset hash, then opens the file in append mode and runs
only the missing suffix. It refuses gaps, reorderings, duplicate IDs, model mismatches, hash
mismatches, or an already complete file with extra rows.

This recovery does not change the task inventory, prompts, parser, endpoint, model settings,
retry policy, scoring, or stopping rule. It does not retry or replace any of the first 12 GLM
responses. In particular, Markdown-fenced compiler responses remain strict schema failures under
the preregistered analysis.

Any relaxed parsing of retained raw responses must be reported separately as a post-hoc semantic
format audit and cannot replace the prospective ITT result.
