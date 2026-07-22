# TRI-v6 Role-Indexed Held-Out Protocol

Frozen on 2026-07-17 after the TRI-v5 role-indexed full run and before any model call on TRI-v6.
TRI-v6 is a post-hoc held-out validation, not part of the original v3 confirmatory experiment.

## Fixed data and code

- Full data: `data/temporal_referent_v6_role_heldout.jsonl`
  - SHA-256 `ecf8f19a55ebfa31b9c8414a14ade7a19f264149923819643936aff071613105`
- Smoke data: `data/temporal_referent_v6_role_heldout_smoke.jsonl`
  - SHA-256 `e566ab73030f9bd452656e225279eb96c11e6a8c80701e0b80850afcf6afaafd`
- Role-indexed runner: `tri/run_v5_stress.py`
  - SHA-256 `8e7d12683561a62ee31eeb29d0b4580c463c0227aaed31ab8e6b904822972201`
- Generator: `tri/v6_role_heldout_eval.py`
  - SHA-256 `b1eee463813c7b4c9ae510f493e26d59cac6a4f6218458a0ee44dca4558a9be7`

The 40 tasks use four schemas not present in TRI-v5 development: projects, expenses, inventory,
and deployments (10 each). They contain 20 anchored and 20 dynamic tasks, 10 per language style,
eight per update type, and two instances from each of 20 template clusters. IDs, fields, selectors,
actions, and action preconditions differ from the v5 development domains.

## Frozen controllers

1. The unchanged historical `compile_then_act` implementation in `tri/run_models.py`.
2. The role-indexed controller frozen after the eight-task v5 smoke and used unchanged for the v5
   full run.

No prompt or parser change is permitted after any TRI-v6 response is observed. Qwen is the first
endpoint. A second model family may be run only with the same frozen data and prompts.

## Smoke and stopping

Run the four-task smoke for endpoint and parser health only. Continue if both controllers have at
most one API/parse failure. Smoke outcomes are included in the full set and not reported as a
separate accuracy estimate.

## Metrics and interpretation

Report intention-to-treat target and final-state accuracy, anchored/dynamic and explicit/implicit
slices, wrong writes, unnecessary rejection, API/parse failures, requests, retries, paired
discordances, exact McNemar p, and template-cluster bootstrap confidence intervals.

The role-indexed controller supports a compositional advantage claim only if it improves accuracy
over historical Compile-then-act and does not increase wrong writes. Otherwise TRI-v6 is retained
as a negative or tied result. Population-level language claims remain contingent on independent
human annotation.
