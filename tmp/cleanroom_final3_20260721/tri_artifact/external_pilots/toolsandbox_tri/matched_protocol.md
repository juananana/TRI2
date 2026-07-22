# Matched Autonomous Compiler Pilot

The inline-state v1 development run showed that asking one actor to maintain
state while choosing its next tool confounds representation with update timing.
This matched protocol moves compilation to a separate call immediately after
the actor's first autonomous reminder search.

All three controllers share:

1. the same autonomous navigator and tools;
2. the same first-search compilation boundary;
3. exactly one compiler call;
4. persistent, immutable compiler output during subsequent actor calls; and
5. the same ToolSandbox state and final-database evaluator.

The only controller-specific components are the compiler output contract and
the actor's instructions for interpreting that contract. Generic uses a
fact-and-ID task record, untyped uses one free-form plan string, and lifecycle
uses the four-field typed record.

The 24 v1 tasks have already been exposed during controller development. They
may be used for debugging only. A paper-facing matched evaluation requires a
new frozen paraphrase set after the architecture and prompts pass a development
smoke test.

## Frozen held-out v1

- 24 tasks; 12 Preserve and 12 Reevaluate.
- Task JSONL SHA-256: `a090ef7c5f1509934d570928b3983a0b997ef34bf51d9636c55e69a7b611c87c`
- Matched runner SHA-256: `107b1b5f0bde4bd9ff149e026b001d47106665cce53f3993cbafc147bed0cb9a`
- Environment SHA-256: `8a342a64e3c770758a809caa37ea5a57b9e4d012b3b88d2fa758617a738c9931`
- Evaluator SHA-256: `67e7ad33d7885a061efdc09755a1badfbbc62de5f455f4bb4826fe9b7e700bc5`
- ToolSandbox upstream commit: `165848b9a78cead7ca7fe7c89c688b58e6501219`
