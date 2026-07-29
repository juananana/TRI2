# TRI Public Opportunity Recall-Calibrated Audit

**Status:** the population, candidate census, and blind frame are frozen; the audit remains
planned/unverified until three independent human return files and their provenance are hash-locked.

This audit covers only the six pinned public benchmark versions already used by TRI. It does not use private workflow logs or estimate traffic outside those versions.

## Sampling frame

Reconcile the existing 80 payload-backed retrieval candidates with the 72-record model-assisted
triage by deterministic dataset/unit-key deduplication before annotation. Preserve each triage
source role: closest cases, domain summaries, released-trace samples, stratified audit rows, and
external structural candidates are audit units but are not automatically one candidate stratum.
Freeze the candidate census only after this routing is explicit. For each dataset, uniformly sample
100 units without replacement from the non-candidate population, or the full remainder when fewer
than 100 exist. Record dataset population size, sample size, inclusion probability, RNG seed
`20260729`, source commit, and source-unit hashes.

Interleave the existing 30 strict-positive and 30 hard-negative injected controls. Controls are attention and implementation checks only and are excluded from prevalence, recall, and confidence interval calculations.

## Human labels and estimands

Three independent annotators label strict eligibility using eight frozen fields: stable entity ID,
observable pre-refresh binding, independent post-binding transition, a competing same-role entity,
changed selector winner, an old entity that remains actionable, later target mutation, and an
evaluable authorized target. A 2/3 majority is the unit label. Report field-level unanimous and
pairwise agreement, strict-label agreement, per-dataset weighted prevalence, finite-population
bootstrap intervals, and weighted candidate-retrieval sensitivity when natural positives exist.

Human packet v4 uses opaque IDs, removes derived retrieval classifications, and serializes both
natural units and suite-native controls through one `source_evidence.document` schema; it hides
sampling role, source-unit identity, and control gold. The three human return
files must be complete and hash-locked with independent-human provenance before ingestion. Model
prelabels use the separate M1--M3 namespace, are descriptive only, and never enter the human
majority or unlock the evidence status.

A private role registry assigns one stable, high-entropy participant token to each natural person
and stores only its SHA-256. A person assigned to two roles must reuse that token, making the overlap
detectable. Q1 is the author-QA reviewer who sees model suggestions; A1--A3 must be different people
and remain blind to those suggestions until their returns are locked.
The coordinator attests person-level separation in the locked private registry. Formal ingestion
then verifies that the four registered token hashes are distinct and binds each A1--A3 provenance
record to its registered hash. It also requires the completed Q1 reviewed manifest and rejects any
role-registry hash that differs between Q1 and A1--A3 ingestion. Names, raw tokens, contact details,
and compensation records stay outside the anonymous artifact.

If no natural positives are found, compute a one-sided exact 95% hypergeometric upper bound from
the actual candidate-census size, random non-candidate sample size, and finite population. Mark
retrieval sensitivity as not identifiable. Never substitute `3 / population size` when only a
sample of non-candidates was reviewed, and never describe zero audited positives as proof of
systematic benchmark undercoverage.

## Required artifacts

Retain the deduplicated candidate ledger, sampled-unit ledger with inclusion probabilities, all
annotator labels, controls and outcomes, machine-readable and Markdown reports, source hashes, and
tests for weighting, deduplication, blind return ingestion, provenance locking, majority labels,
control exclusion, and zero-positive handling. Annotator identity and compensation records remain
private.
