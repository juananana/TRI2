# SiliconFlow External Public-Dataset Annotation Addendum

**Frozen:** 2026-07-24, after the zero-API Go decision and before the first model request.
**Evidence status:** post-primary model-assisted candidate annotation; completed.
**Parent protocol:** `reports/TRI_external_public_dataset_opportunity_audit_protocol.md`

## Claim and Boundary

The annotation tests whether two independent model families agree that the 80 deterministically
retrieved external workflows expose the source evidence required by the frozen rubric. It is a
candidate-retrieval and structured-extraction audit. A model `strict=yes` label is not a benchmark
fact, independent review, behavioral result, or prevalence estimate; it only nominates a source
case for deterministic/author verification.

The alternative explanation being excluded is that deterministic tool-name and ID-linkage
heuristics admit workflows whose actual dialogue/state does not contain a same-role selection and
later mutation.

## Frozen Inventory and Prompts

- Candidates: `data/external_public_annotation_candidates_v1.jsonl`
- Candidate rows: 80 (BFCL 57; ToolTalk 23)
- Candidate SHA-256: `7cde3ba06ee3aac3d45d89b9b3963aaeaf7af90828296700bb99b8ac1ae11e29`
- Candidate bytes: 251,047
- System prompt: `reports/prompts/tri_external_public_annotator_v1.txt`
- System-prompt SHA-256: `72396dddec5899cba2f8c0cb9b1884af5bfc8d9d42b612f3bb6c1ffc1525cb08`
- User prefix: `Annotate this frozen public-dataset candidate. Return JSON only.\n<CANDIDATE>\n`
- Runner: `scripts/run_external_public_annotation.py`
- Frozen runner SHA-256: `e001e4d6ddd1c3bc26ae59fa54cb8cb4dcd1c2e1945b0badcf65c9097a696c97`

The payload preserves public source text and stable IDs but replaces password, token, secret,
credential, session-token, and API-key fields with `<REDACTED>` before transmission.

## Endpoint and Models

- Endpoint: `https://api.siliconflow.cn/v1/chat/completions`
- Models: `Qwen/Qwen3.5-122B-A10B` and `Pro/zai-org/GLM-5.1`
- Temperature: 0
- Thinking: disabled
- Output cap: 700 tokens
- Timeout: 180 seconds
- Workers: 4
- Retry: at most one retry for transport/HTTP/timeout failure; no retry for content or parse failure
- Credentials: environment only (`SILICONFLOW_API_KEY` or `LLM_API_KEY`); never written

Each of the 80 candidates is sent once to each model. All attempted rows, raw content, parse
failures, response IDs, usage, and request counts are retained under ITT.

## Bounded Smoke Gate

The smoke uses the first two lexicographically sorted candidates from each dataset, for four
candidates and eight model-candidate rows. It passes only if:

1. all eight attempted rows are present;
2. at least six rows have valid exact-schema JSON;
3. each model has at least one valid row in each dataset.

If the smoke fails, the full run stops. Prompt, parser, model, and output cap are not tuned on the
smoke. A transport-only repair may resume the identical frozen protocol.

## Transport Repair, Interruption, and Completion

**Added:** 2026-07-24 after the smoke/full process was interrupted. This section records execution
history; it does not change the inventory, prompt, models, decoding, labels, or outcome rules.

The original `e001e4...` runner attempted all eight smoke pairs inside the restricted sandbox. All
eight rows failed with the same DNS-resolution `URLError`, before any provider response. Under the
pre-specified transport-repair allowance, the runner was changed only to (i) append a retry for a
prior transport/HTTP/timeout failure and (ii) skip every successful or content/parse-failed pair.
The report was changed to use the latest row per pair while retaining every raw attempt. The repaired
runner SHA-256 is `7c4abb65c97276cf1367b315de1e0135040664b3ba6e5444c0e7c9a3cc19a6b9`.
Candidate and system-prompt hashes remain exactly as frozen above.

The repaired smoke produced eight valid latest rows and passed the frozen gate. The full run then
started without changing the prompt or candidates but was interrupted after 84/160 unique pairs.
That checkpoint contained 92 raw rows: eight original DNS failures, 78 exact-schema valid latest
rows, five latest JSON parse failures, and one latest invalid-enum row. Content, parse, and schema
failures were not retried. The interrupted state remains serialized in
`reports/external_public_annotation_partial_v1.{json,md}` for failure accounting; it is superseded
by the completed report and must not be cited as the final candidate-label result.

The unchanged repaired runner later requested only the 76 previously missing pairs and reached the
frozen stopping rule: 160/160 unique model--candidate pairs and no missing pairs. The retained JSONL
has 168 raw attempts, including the eight superseded sandbox-DNS failures. In the latest-pair view,
145 rows are exact-schema valid and 15 are failed or invalid (Qwen 79/80 valid; GLM 66/80 valid).
Sixty-five candidates have two valid labels, with 24 two-model disagreements. The strict-positive
union and intersection are both zero, so the protocol triggers no strict-positive source
verification. The broader source-eligible union contains 25 candidates and the intersection one;
these labels remain fallible candidate annotations, not verified native opportunities.

Completion artifacts and SHA-256 hashes are:

- raw JSONL: `db9530e744f643fd1cba3d585f08324bd1217406e15362a9a16611705caabfad`;
- JSON report: `6f9382de7f4a3d07ea4b7f4efd91f78e024d4c8715e522023a7cc1a7c8a01ff9`;
- Markdown report: `35c9f769679415f54dead59a18b21fa068066fbefece11e526a5d1fea0022656`.

## Stopping Rule

After a passing smoke, run every remaining model-candidate pair exactly once under the retry rule.
Stop when all 160 unique pairs are present. Do not delete failures, select cases by labels, or add
new candidates after seeing outputs.

## Outcomes

- Agreement on source-anchored eligibility strengthens the deterministic candidate inventory but
  does not establish native TRI.
- Candidate `strict=yes` labels trigger source verification of every cited feature; only verified
  source facts can change the external-opportunity report.
- No strict candidates narrows the search result and is retained.
- If most deterministic candidates are rejected, the heuristic gate is reported as low precision;
  no replacement tasks are generated.
- No result changes the v3 primary or establishes natural prevalence, ordinary-agent failure, or
  CTA superiority.

## Required Outputs

- `runs/external_public_annotation_siliconflow_v1.jsonl`
- `reports/external_public_annotation_v1.json`
- `reports/external_public_annotation_v1.md`
- complete failure accounting and source verification for all strict-positive candidates
- provenance and registry updates after completion
