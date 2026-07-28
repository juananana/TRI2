# TRI Public Opportunity Recall-Calibrated Audit

**Status:** planned/unverified until the candidate/population inventory and blind human labels are frozen.

This audit covers only the six pinned public benchmark versions already used by TRI. It does not use private workflow logs or estimate traffic outside those versions.

## Sampling frame

Reconcile the existing 80 retrieval candidates with the 72-record model-assisted triage by deterministic dataset/unit-key deduplication before annotation. Include every deduplicated candidate. For each dataset, uniformly sample 100 units without replacement from the non-candidate population, or the full remainder when fewer than 100 exist. Record dataset population size, sample size, inclusion probability, RNG seed `20260729`, source commit, and source-unit hashes.

Interleave the existing 30 strict-positive and 30 hard-negative injected controls. Controls are attention and implementation checks only and are excluded from prevalence, recall, and confidence interval calculations.

## Human labels and estimands

Three independent annotators label strict eligibility using the six frozen fields: observable correct initial binding, completed independent refresh, old target present and action-valid after refresh, distinct refreshed winner, and target-level outcome observability. A 2/3 majority is the unit label. Report item agreement, per-dataset weighted prevalence, finite-population bootstrap intervals, and weighted candidate-retrieval sensitivity when natural positives exist.

If no natural positives are found, report a one-sided 95% upper bound `3 / estimated population size` for each dataset and mark retrieval sensitivity as not identifiable. Never describe zero audited positives as proof of systematic benchmark undercoverage.

## Required artifacts

Retain the deduplicated candidate ledger, sampled-unit ledger with inclusion probabilities, all annotator labels, controls and outcomes, machine-readable and Markdown reports, source hashes, and tests for weighting, deduplication, majority labels, control exclusion, and zero-positive handling. Annotator identity and compensation records remain private.
