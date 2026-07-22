# TRI Natural Instruction Elicitation and Ordinary-Agent Protocol

**Status:** prospective protocol. Freeze all scenario cards, forms, exclusion rules, and analysis
code before collecting any response. Do not include prospective numbers in the paper until the
study is complete.

## Research Question

When people are not taught Preserve/Reevaluate terminology or shown author-written instruction
templates, how often do they naturally produce a selector--sync--mutation workflow, what target do
they intend after a selector-changing refresh, how identifiable is that intent to other people,
and how often do ordinary tool-calling Agents act on a different entity after a correct initial
selection?

This study addresses natural-language construct validity and ordinary-Agent behavior. It does not
estimate prevalence in deployed traffic because participants are still recruited into scenarios
where synchronization is available.

## Participants and Minimum Sample

- Writers: at least 20 independent English-proficient participants, five scenario cards each,
  yielding at least 100 independently authored instructions.
- Annotators: three additional participants who did not write instructions and are blind to writer
  intent, benchmark labels, model outputs, and controller identity.
- No author responses enter the primary analysis.
- A strong LLM may be reported as a secondary annotator, but cannot replace the human writer-intent
  record or the three primary annotators.

Record consent, age eligibility, language proficiency, prior AI-assistant familiarity, completion
time, and compensation. Store names/contact information separately from response IDs. Obtain the
institutionally appropriate ethics determination before recruitment.

## Stage A: Unprimed Instruction Elicitation

Each writer receives a realistic application screen containing 3--6 entities, a desired mutation
such as postpone/reply/remove/approve, and this neutral capability note:

> The assistant can inspect the currently visible records, synchronize the application once, and
> modify exactly one record. Write the single message you would naturally send to make it complete
> the task. There is no required wording.

Do not mention binding, reference mode, Preserve, Reevaluate, selector winner, temporal integrity,
or possible answer labels. Do not require a particular operation order. Scenario cards cover at
least six domains and selectors (earliest due, highest priority, largest amount, oldest unresolved,
most expensive, and first alphabetically). Assignment is balanced by writer and scenario family.

The writer submits the instruction before seeing the synchronized state.

## Stage B: Writer-Intent Elicitation

After submission, reveal the exact Stable and Flip outcomes in randomized order and ask separately:

1. Which concrete record should the assistant modify?
2. If neither record is clearly intended, choose `CLARIFY`.
3. Explain the choice in one optional sentence.

This post-instruction response is the writer-intent reference. It does not alter the already saved
instruction. A determinate Preserve intent selects the pre-sync winner in Flip; Reevaluate selects
the post-sync winner. Stable is a masking control because both policies select the same ID.

## Stage C: Independent Interpretation

Three blind annotators see the original screen, writer-authored instruction, and one synchronized
outcome. They choose the intended stable ID or `CLARIFY` and rate confidence 1--5. Items and outcome
order are randomized independently for each annotator.

Primary language-quality metrics:

- fraction of instructions that naturally request selection, synchronization, and mutation;
- writer-intent Preserve/Reevaluate/Clarify distribution;
- majority and unanimous writer-intent agreement;
- Fleiss' kappa and Krippendorff's alpha;
- ambiguity rate and confidence;
- mixed-effects or cluster-bootstrap intervals grouping by writer and scenario family.

The model experiment's primary clear-language subset requires determinate writer intent and at
least two of three annotators agreeing with that intent. Report all-item sensitivity separately.

## Stage D: Ordinary-Agent Execution

Run each clear instruction in paired Stable and Flip worlds using a normal full-history
function-calling Agent:

- no ledger, lifecycle tuple, reference-mode field, commitment reminder, or gate;
- no system-prompt explanation of temporal authorization;
- normal selector API returns one entity and stable ID, which the runner logs automatically;
- real database mutation and snapshot-diff scoring;
- at least four model families and, where possible, two independent API providers;
- temperature zero primary run; a smaller repeated-run sensitivity may measure stochasticity.

The strict conditional TRI denominator requires a correct pre-sync selector result for writer-
intended Preserve or a correct post-sync selector result for Reevaluate, a completed refresh, and
an attempted mutation. Initial selection, tool-order, parse/API, policy, and collateral errors are
reported separately.

## Primary Outcomes

1. Natural TRI-opportunity rate within the elicitation context.
2. Human ambiguity and communicative identifiability of naturally authored instructions.
3. Conditional post-binding TRI rate in Flip after a verified correct binding.
4. Stable masking rate: the same process/order defect that appears correct when the winner does not
   change.
5. Wrong-entity database-write rate and collateral modification count.

Use writer- and scenario-cluster bootstrap intervals. Never treat paired Stable/Flip rows or
multiple instructions from one writer as independent observations.

## Decision Rules

- If few writers request synchronization naturally, report that TRI opportunities are rare in this
  elicitation context and narrow the paper's motivation.
- If human writer intent is frequently ambiguous, reposition the method as clarification-aware
  authorization rather than deterministic semantic recovery.
- If ordinary Agents have zero conditional TRI on the clear subset, retain TRI as a controlled
  controller-specific diagnosis and report the null.
- If conditional TRI appears across independent writers, scenarios, and model providers, this is
  the strongest available evidence short of consented production logs.

## Prohibited Claims

This study must not be described as uncontrolled production traffic, a population prevalence
estimate, or evidence that every LLM exhibits TRI. The defensible label is **human-authored,
naturalistic, opportunity-conditioned evaluation**.
