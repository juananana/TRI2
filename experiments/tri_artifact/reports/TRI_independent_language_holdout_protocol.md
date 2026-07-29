# TRI Independently Authored Controlled-Language Holdout

## Status and prospective amendment

This protocol is planned/unverified until human collection, blind annotation, and the frozen
analysis finish. It prospectively replaces the obsolete six-writer, 20-item, eight-page plan with
the deployed packet design: 12 writers, 10 items per writer, and one two-page questionnaire per
writer. No writer return had been collected when this amendment was recorded. If completed, the
study is post-primary evidence frozen before its own model calls.

The study tests transfer beyond author-written instruction templates. It remains a controlled
intervention and does not estimate native-workflow prevalence. Human writers and annotators cannot
be replaced by an LLM. Model-assisted form checking may be reported only as engineering QA and
never contributes to participant counts, agreement, or the clarity gate. Any model prelabels use
the separate `M1`--`M3` namespace and opaque item IDs; the formal validator accepts only human
`A1`--`A3` labels with a locked independent-human provenance manifest stating that annotators did
not see model suggestions before submission.

## Ethics and recruitment gate

The 12 questionnaires remain unavailable for recruitment until the study team records the
applicable institutional approval, exemption, or policy determination and completes the
recruitment check. The private collection ledger records anonymous participant code, role,
consent, adulthood, completion status, compensation category, completion time, and the applicable
ethics determination. Identity-bearing records do not enter the artifact.

Every valid writer return must confirm adulthood, English task ability, consent, no use of
generative AI/search/machine translation/other people, no understanding-affecting technical issue,
and completion of both stages. These eligibility fields must be present in the WJX export or an
associated collection record. For the deployed 1--33 question forms, the final three checks may be
collected from the same writer in a short follow-up and joined through the WJX response ID. The
processor requires a complete 12-row private sidecar, checks response-ID equality and uniqueness,
and records its hash. Missing fields are not interpreted as consent or eligibility.

## Participants and inventory

Twelve English-proficient writers who have not seen TRI templates, the earlier construct
questionnaire, Rule* errors, or model outputs each author 10 instructions. Three additional,
independent annotators later label all 120 instructions. The inventory contains 60
shared-transition opposite-gold pairs across ten domains.

Each writer receives five Preserve-order and five Reevaluate-order cards. The two members of every
pair are assigned to different writers. Writers see a neutral initial state, tool capability,
selector, action, and required operation order. They receive no example TRI instruction, alternate
pair member, refreshed state during Stage A, gold label, Rule* vocabulary, or model output.

## Two-page writer procedure

Each writer completes one questionnaire. Page 1 contains all 10 Stage A writing cards. Page 2
contains the corresponding Stage B intent judgments. The same person completes both stages. Stage
B dynamically displays that writer's Stage A sentence, action, selector, and refreshed state, then
records the intended target or CLARIFY and confidence from 1 to 5. Pairing and target scoring use
the exact Stage A string hashed before Stage B fields are processed.

The participant is instructed not to return to Stage A after seeing Stage B. WJX is configured
with previous-page navigation disabled. Because the platform does not provide a verified immutable
page lock, this remains a procedural control and study limitation.

## Return validation and freeze

Processing uses the frozen 12-writer allocation and a private scenario key. Exactly one complete,
eligible return is required for every writer code W1--W12. Every return must contain the assigned
10 Stage A strings, 10 Stage B intents, and 10 confidence judgments. Duplicate writer submissions,
shared participant identifiers across writer codes, missing rows, invalid target IDs, invalid
confidence values, or Stage A hash mismatches stop processing.

Only after all 120 rows pass validation may the processor write the locked authored-instruction
file and generate annotator forms. It randomizes a separate 120-item order for each annotator and
keeps the two members of every pair non-adjacent. Forms use opaque `BI-*` item IDs; condition- and
pair-bearing source IDs remain only in a private sidecar stored outside the distributable form
directory. Writer intent, condition, pair membership, design gold, and model outputs are hidden
from annotators.

## Blind interpretation and clarity gate

Each annotator labels all 120 instructions exactly once. Allowed responses are the entity IDs shown
in the refreshed state or CLARIFY, with confidence from 1 to 5. Annotator IDs must be unique and
must match the three frozen roles.

An item is clear when writer intent is determinate, matches the target implied by its assigned
operation order, and at least two of three annotators choose that intent. The design-fidelity
requirement prevents a writer's inverted or otherwise noncompliant interpretation from silently
changing the intended Preserve/Reevaluate contrast. A pair is clear only when both members are
clear. At least 40 clear complete pairs are
required before any model call. If the gate fails, the collection is reported only as a semantic
boundary analysis. All 120 rows remain in all-item sensitivity reports.

## Frozen model evaluation

After the human-only clarity computation is frozen, Qwen, GLM, and DeepSeek run on all 120 rows
under intention-to-treat scoring. The primary equal-call contrast is History-only versus
Decision-visible. Calls, base actor payloads, state, and tool schema are matched. Timing-reminder,
CTA, and the unchanged Rule* are secondary frozen baselines.

The primary endpoint is changed-pair PairAcc on clear complete pairs. Secondary outcomes are
all-row E2E, Preserve conditional substitution, initial-binding error, database wrong
writes, and Rule* exact accuracy. Pair-cluster bootstrap is primary; writer and scenario-family
crossed sensitivity is supplementary. API, transport, parse, and incomplete outputs count as
intention-to-treat errors.

The executable primary report uses 10,000 pair-ID cluster resamples with seed 20260728. All-row E2E
scores determinate items against writer target and indeterminate items against the writer's CLARIFY
judgment, and remains separate from clear-pair PairAcc. Preserve conditional substitution is
restricted to actionable Preserve rows with the observable initial ID correctly bound, a
surviving/actionable old target, and a distinct refreshed winner. Compiler parse/schema failure,
API failure, mode error, and Preserve bound-ID error are reported separately. Deterministic SQLite
wrong-write rates use all actionable rows; missing output and rejection remain ITT E2E errors but
are not relabeled as writes.

## Frozen interpretation and claim-promotion gates

The human construct claim and model-transfer claim are separate. Passing the clarity gate permits
the statement that independently authored controlled language supports the actionable
Preserve/Reevaluate distinction. It does not by itself show that Decision-visible improves model
behavior.

An abstract-level open-language intervention-transfer claim is permitted only when all three
model-specific Decision-visible minus History-only PairAcc point estimates are positive, at least
two of their pair-cluster bootstrap 95% intervals exclude zero, and the Decision-visible minus
History-only wrong-write rate is no greater than +5 percentage points for every model. The
five-point margin is a reporting gate, not a non-inferiority test. If the direction or interval
gate fails, results remain model-specific. If only the wrong-write gate fails, the accuracy effect
must be reported together with the adverse execution tradeoff and cannot enter the abstract as an
unqualified improvement.

No threshold may be changed after the first eligible writer return. The model stage remains
forbidden until the human-only clarity report is frozen and the minimum 40-pair gate passes.

## Reporting boundary

Human clarity is computed without access to model predictions. Negative, null, and adverse results
are retained. The study may be called an independently authored controlled-language holdout only
after all human gates pass. It must not be called natural traffic, a native benchmark result, or a
prevalence study.
