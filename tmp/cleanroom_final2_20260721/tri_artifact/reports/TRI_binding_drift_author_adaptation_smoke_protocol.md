# Binding Drift Author-Adaptation Symmetric Smoke Protocol

Frozen: 2026-07-21, before any adapted re-verifier API output.

## Question

How do an entity-lock policy, a practical Binding Drift-style re-resolution prompt, and TRI CTA
behave on matched post-update Preserve/Reevaluate pairs? This is not an official Binding Drift
benchmark rerun and does not test repair of initially wrong bindings.

## Source and frozen task set

- Official source repository: `shashank-indukuri/binding-drift`.
- Verified official commit: `0e040e0954b18d4621a6f9b16f6e6e9591c822e1`.
- Official code license: MIT.
- TRI source: unchanged `temporal_referent_v7_core_replication.jsonl`.
- Frozen smoke: `binding_drift_tri_symmetric_smoke_v1.jsonl`.
- SHA-256: `dbd44407f91fc2fc919d6b450d75f53950768dbf9a7a1ac3f8966b0d6b7bbcf7`.

The smoke contains ten state clusters, one per v7 domain. Each cluster contributes an
Anchored/Preserve and Dynamic/Reevaluate Flip pair with identical initial state, refreshed state,
selector, and action. It contains 10 Preserve and 10 Reevaluate tasks; explicit and implicit
language each occur in both modes.

Selection rule: sort domains, choose the first sorted state cluster in each domain, and retain its
two Flip rows. The rule and generator are frozen in `tri/binding_drift_tri_adapter.py`.

## Methods

1. `Entity Lock analogue`: retain the pre-refresh ID. This is deterministic and corresponds in
   spirit to the official lock, but is not labeled an official run.
2. `Self reverify adaptation`: use the official `LLM_REVERIFY_PROMPT` text and the tested model to
   resolve the original full instruction against refreshed candidates.
3. `Cross reverify adaptation`: use the other model family as verifier. Because the verifier
   response depends only on the instruction and candidates, Qwen/GLM self outputs are reused as
   GLM/Qwen cross outputs; no duplicate calls are made.
4. `Exact CTA`: reuse the already frozen v7 CTA rows for the exact same 20 task IDs. No prompt or
   model rerun is allowed after seeing reverify outputs.

Only the API transport is adapted from AWS Bedrock to SiliconFlow's OpenAI-compatible endpoint.
The official re-verification prompt wording is copied unchanged. Gold target, TRI mode label,
benchmark selector field, and CTA ledger are not supplied to the verifier.

The official dataset supplies a short noun phrase as `step1_referent`. TRI cannot use only its
selector phrase because doing so would remove the temporal authorization distinction being tested.
The adaptation therefore places the complete TRI instruction in the official prompt's `Original
request` slot. This preserves the research variable but is an explicit interface difference; any
selector-grounding failures will be separated from old/new-target choices.

Models: `Qwen/Qwen3.5-122B-A10B` and `Pro/zai-org/GLM-5.1`; temperature 0; thinking disabled;
300 output tokens; maximum three transport retries. The API key is passed only through
`LLM_API_KEY` and must not be stored.

## Metrics

- exact authorized-target accuracy;
- Preserve and Reevaluate accuracy;
- Preserve substitution to refreshed winner;
- Reevaluate premature retention of the old target;
- clarify/ambiguous rate;
- request attempts, retries, token usage, and latency.

The two modes are reported separately. No method is claimed to dominate Binding Drift's original
initial-misbinding benchmark.

## Smoke gate and expansion decision

Operational pass requires 20 unique expected rows per verifier model, at most one final API/parse
failure, and no systematic invalid response format. Accuracy direction is not a gate. After the
complete smoke, expansion to 160 or 240 tasks will be decided from information gain, cost, and
whether the adaptation meaningfully distinguishes lock, re-resolution, and CTA.
