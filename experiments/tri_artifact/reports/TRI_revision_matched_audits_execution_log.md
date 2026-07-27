# Revision Matched Audits: Execution Log

## 2026-07-26 source-grounded interruption

The first Qwen source-grounded full process exited after writing 51 of 60 rows. All 51 rows were
complete and formed the exact ordered prefix of the frozen inventory. The raw file was retained
unchanged.

After the interruption, the runner and matrix wrapper gained an append-only `--resume` path. Before
making a further request, it verifies the existing prefix against the frozen task order, model,
stage, task index, task-file SHA-256, protocol SHA-256, and the complete-row schema. It refuses a
duplicate, reordered, incomplete, hash-mismatched, or already complete prefix. Only the missing
suffix is appended; completed rows are never requested again.

This recovery changes no inventory, prompt, model setting, parser, outcome definition, denominator,
stopping rule, or evidence status. The frozen protocol and manifest hashes remain unchanged. The
interruption and any later API, parsing, or transport failures remain in raw execution provenance
and intention-to-treat reporting.

The resumed Qwen run subsequently completed 60/60 rows. GLM and DeepSeek also completed 60/60;
all three models completed 180/180 planned logical calls with zero retry or final failure. Final
raw SHA-256 values are:

- Qwen: `0bc4e782abd425605baec59669dc7eb60676b8c7cf4a85bf094401e5b26ebb34`
- GLM: `abf87c52db74d7688ff6c1fcf796c2f22824e3a6b75ecb2c011af221d8658d19`
- DeepSeek: `0d52868491a41f747f6db82d38f26e9886b9045942766fc9ec9079d54fc423f6`
