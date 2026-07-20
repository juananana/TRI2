# TRI Human-Rewrite Execution Log

This log records deviations and failures without treating them as model behavior.

## Frozen inputs

- Dataset: `data/temporal_referent_human_rewrites_v1.jsonl`
- Expected tasks: 50
- Frozen SHA-256: `9cd91c908fb9e76938277459a5ec8a78e7c406d91c77034e203084d719697e39`
- Models and controllers are those in `TRI_human_rewrite_model_protocol.md`.

## Pre-call runner failures

1. The first smoke attempt on 2026-07-18 produced eight zero-row files because the matrix
   wrapper omitted `--split all --paraphrase all`. The task loader filtered all rows before
   creating the API client loop, so these files contain no model responses and are excluded
   from evidence and the public archive.
2. The first full-matrix attempt on 2026-07-18 stopped before its first API call because macOS
   Bash 3.2 treats an empty array expansion as unbound under `set -u`. The wrapper was changed
   to a Bash-3.2-safe optional expansion. The empty output is excluded from evidence and the
   public archive.

Neither failure changed data, prompts, parsers, scoring, or interpretation rules.

## Smoke deviation

The protocol requested a four-item balanced smoke. `LIMIT=4` selected the first four frozen
rows, which are all calendar/explicit-anchored rather than balanced. All 32 resulting
model-controller rows had `status=ok`; compiled controllers were 4/4 and Generic was 1/4 for
both models. These results are endpoint/parser health checks only and are not used as evidence.
No prompt or parser changed after inspection. The full 50-task inventory remains the sole
reported human-rewrite model result.

## Completeness rule

The corrected wrapper now passes `--split all --paraphrase all` and exits nonzero unless every
output has exactly `LIMIT` rows or, without a limit, all 50 rows. The analysis script also
rejects missing, duplicate, extra, or incomplete task inventories. API errors remain rows and
count as failures.

## Completed full matrix

The corrected full matrix completed on 2026-07-19 local time. Each of the eight run files has
exactly 50 unique expected task IDs; all 400 rows have `status=ok` and zero API retries. Frozen
analysis is in `human_rewrite_model_results.json` and `.md`. No data, prompt, parser, runner,
or scoring rule changed after the first non-empty response.
