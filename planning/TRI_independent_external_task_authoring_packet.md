# TRI Independent External Task-Authoring Packet

**Status:** recruitment and handoff material only. This packet creates no tasks, records no
evidence, and does not authorize model/API calls. A completed inventory remains
`planned/unverified` until it passes the frozen external-confirmation gate.

## Purpose and Boundary

This packet is for a future, independent **human** contributor to author ordinary tool-use
workflows for the protocol in
`experiments/tri_artifact/reports/TRI_low_intervention_external_confirmation_v2_protocol.md`.
It is designed to test whether the controlled result survives ordinary tool interfaces while
excluding the alternative explanation that the TRI team constructed the linguistic contrast.

An automated agent, an LLM-generated task, a task written by a TRI author, or an author paraphrase
of an existing TRI task does not satisfy this packet. Such material may be useful for internal
engineering only and must not be represented as independently authored evidence.

The resulting paper may describe qualifying material as independently authored without publishing
personal names, subject to the venue's disclosure rules. The private provenance record described
below must nevertheless exist and be available for a legitimate audit.

## Eligibility and Separation

Each contributor must attest, before seeing the author brief, that they:

1. are a human contributor, not a TRI paper author, and have not helped design TRI tasks, rules,
   labels, prompts, scoring, analyses, or the current manuscript;
2. have not received the TRI inventory, model outputs, desired result direction, or a request to
   make failures likely;
3. will author the workflow text and its substantive state transition themselves, without LLM
   generation or TRI-team rewriting; ordinary spelling or grammar correction is allowed only when
   it does not change task semantics and is logged;
4. will disclose any prior exposure that could defeat this separation. Disclosure makes the
   contributor ineligible for the independent inventory, rather than creating a hidden exception.

The study steward keeps the identity-to-token mapping outside the anonymous submission archive.
The task file and all public reports use only a random `writer_id`; it must not encode a name,
institution, email address, or account handle.

## Blinded Author Brief

Give contributors only the following operational brief. Do not expose the terms TRI, temporal
referent integrity, authorization, Preserve, Reevaluate, binding drift, gold target, or existing
results.

> Create realistic, self-contained tasks for an ordinary tool-using assistant in one application
> you know well. Each workflow must have: (a) an initial search or selection that returns one
> stable record ID, (b) a normal synchronization, refresh, or externally caused update, and (c) a
> later action that changes one record and whose final state reveals which record was changed.
> Write four natural user requests for the same workflow: two requests where the earlier selected
> record remains the intended action object after the update, and two requests where the user asks
> the assistant to act on whichever record satisfies the current criterion after the update. For
> each type, provide one case where the selected record remains the current winner and one where a
> different, still-valid record becomes the current winner. Do not use research vocabulary, answer
> labels, special control fields, or artificial phrases that name the distinction.

Contributors must submit the four requests and supporting operational information in a separate
private handoff. They must not see a gold label, model response, aggregate result, or correction
from the TRI team before submission. The steward must not ask them to rewrite a task after a model
outcome is known.

## Required Inventory

The frozen inventory must contain at least 80 rows arranged as 20 distinct workflow clusters.
Each cluster contains exactly these four rows before any execution:

| Natural-language intent | Post-update selector | Required rows per cluster |
|---|---|---:|
| Earlier selected record remains intended | Same winner | 1 |
| Earlier selected record remains intended | Different valid winner | 1 |
| Act on the current criterion | Same winner | 1 |
| Act on the current criterion | Different valid winner | 1 |

The inventory must cover at least four applications. Target five workflow clusters per application
to make the minimum balanced; any uneven allocation still requires four applications, 20 clusters,
and 80 complete rows. A cluster is one independently conceived workflow, not four paraphrases of a
single existing TRI template.

Every row must have all of the following:

- a normal selector API whose observed result includes one stable ID;
- a binding before the update for the earlier-selected intent and a refresh before mutation;
- a real or faithfully documented application-style transition after selection;
- a surviving, action-valid old record in the different-winner earlier-selected row;
- a distinct refreshed selector winner in every different-winner row;
- a mutation and final-state diff that identify the modified record;
- ordinary task wording with no prohibited research/control fields.

Rows involving an invalid old record may be retained as additional safety cases, but they do not
enter the conditional TRI denominator and cannot replace any required four-row cell.

## Private Handoff Schema

The contributor sends one package per cluster. The steward assigns `writer_id` only after receipt.
The public-facing inventory must contain no direct identifier. The private attestation and mapping
must be access-controlled and excluded from the paper, supplement, code release, and model prompts.

```text
cluster_id: <application>-<opaque cluster token>
writer_id: <random opaque token assigned by steward>
application: <application/tool substrate>
workflow_summary: <ordinary one-paragraph description>
source_provenance: <public documentation URL/version, or a local mock specification>
authoring_timestamp_utc: <timestamp>
authoring_attestation_sha256: <hash of signed private eligibility attestation>
ai_assistance: none | nonsemantic proofreading (describe)
rows:
  - row_id: <opaque token>
    user_request: <natural language only>
    selector_tool: <normal tool name and returned stable-ID field>
    initial_state: <reproducible state>
    external_transition: <reproducible synchronization/update>
    refreshed_state: <reproducible state>
    mutation_tool: <normal tool name and action-validity preconditions>
    final_state_or_diff_oracle: <deterministic evidence of affected ID>
    intended_action_timing: earlier-selected | current-criterion
    winner_relation: same | different-valid
    contributor_notes: <ordinary operational clarification; no research labels>
```

`intended_action_timing` and `winner_relation` are private intake metadata for deterministic
validation. They are not included in the participant-facing author brief, model prompt, or
public-facing task text. A second, blinded reviewer should independently derive these fields from
the submitted text and trace before the labels are revealed.

## Handoff and Acceptance Sequence

1. The steward records the eligibility attestation and gives the blinded brief. No task examples,
   labels, results, or model prompts are shared.
2. The contributor submits a completed cluster once. The steward time-stamps and hashes the
   received package before opening it for semantic review.
3. A blinded reviewer checks that the request, tool trace, stable IDs, transition, and final-state
   oracle are internally coherent. The reviewer records accept/reject and a reason without seeing
   any model outcome.
4. The steward runs deterministic validation. Rejected clusters may be discarded, but they may not
   be rewritten by a TRI author or selectively replaced after a model result. Any contributor
   revision must be logged as a new version and accepted before the inventory freeze.
5. When all required clusters are accepted, concatenate the full inventory, compute its SHA-256,
   freeze the prompt/endpoint/metrics/retry/stopping rule, and rerun the zero-API gate. Only `GO`
   permits the four-task transport smoke specified in the frozen protocol.

## Acceptance Tests Before the Gate

All tests below are required and their outputs must be retained with the incoming inventory:

1. **Independence:** every `writer_id` has a valid private attestation; no contributor is a TRI
   author or prior TRI task/rule contributor; no undisclosed semantic LLM generation.
2. **Structure:** at least 4 applications, 20 cluster IDs, 80 rows, and all four intent/winner
   cells in every cluster; no duplicate row text, stable-ID collision, or duplicated cluster.
3. **Observable mechanism:** deterministic replay confirms the selector binding, completed update,
   action-valid old record where required, distinct refreshed winner where required, mutation
   validity, and final-state affected ID.
4. **Blinding and leakage:** task text, tool schemas, and prompts contain none of `TRI`,
   `authorization`, `Preserve`, `Reevaluate`, `reference mode`, or `gold target`; no model result
   predates the package hash and inventory freeze.
5. **Pairing:** an independent reviewer agrees with the private timing/winner metadata for every
   row, or a documented adjudication occurs before the final freeze. Disagreement rates are
   reported, rather than silently resolved.
6. **Protocol compatibility:** `PYTHONPATH=. ../../.venv-toolsandbox/bin/pytest -q tests` and
   `scripts/audit_external_confirmation_gate.py` pass on the frozen inventory. A `NO-GO` result
   stops the process; it is not a request to add author-written or LLM-generated material.

## Reporting Rule

Until all acceptance tests, the inventory gate, and the subsequent frozen execution have completed,
describe this work only as `planned/unverified`. A qualifying completed study is post-primary
evidence: it can assess the external-occurrence claim but cannot replace or relabel the primary
controlled TRI evidence. Null results, pre-binding errors, invalid attempts, rejections, and API
or parse failures must be retained and reported separately.
