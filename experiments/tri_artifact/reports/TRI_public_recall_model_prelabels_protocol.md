# TRI Public Recall Model-Prelabel Protocol

**Status:** provisional model-assisted annotation for human review; never independent-human
evidence and never an input to prevalence or recall claims.

M1, M2, and M3 use the frozen public-recall packet v4 and map respectively to Qwen, GLM, and
DeepSeek. Each sees only the opaque blind unit, the shared `source_evidence` payload, the eight
rubric fields, and the response schema. Sampling role, source-unit key, control gold, and the
private annotation key remain hidden.

Each model labels all 699 units after an eight-row health smoke. Temperature is zero, thinking is
disabled, maximum completion is 700 tokens, and transport retries are limited to two for the same
retryable conditions used by Decision Decomposition v2. All attempts, raw responses, parse errors,
usage, prompt/settings hashes, and task hashes are retained. Missing or invalid rows remain
incomplete; the review report requires 699/699 complete rows for all three models.

The report produces only a model-consensus summary and an author-QA queue. Any rubric-field
disagreement is reviewed first, followed by provisional positives and low-confidence unanimous
negatives. The QA reviewer must not be one of the later independent A1--A3 annotators. Model or
author-QA labels cannot satisfy A1--A3 provenance, enter a human majority, unlock the public audit,
or appear in the paper as prevalence, recall, independent annotation, or human agreement.
