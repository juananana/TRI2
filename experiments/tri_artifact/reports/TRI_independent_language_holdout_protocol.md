# TRI Independently Authored Controlled-Language Holdout

## Status and claim

This protocol is planned/unverified until the human collection and frozen analysis finish. If
completed, its evidence status is post-primary and frozen before its own model calls. The study
tests transfer beyond author-written templates. It remains a controlled intervention and does not
estimate native-workflow prevalence.

## Participants and inventory

Six English-proficient writers who have not seen TRI templates, the current construct questionnaire,
Rule* errors, or model outputs each author 20 instructions. Three additional blind annotators label
all instructions. The inventory contains 60 shared-transition opposite-gold pairs across ten
domains, for 120 instructions total.

Each writer receives ten Preserve-order and ten Reevaluate-order cards. The two members of every
pair go to different writers. Writers see a neutral initial state, tool capabilities, selector,
action, and required operation order. They receive no example instruction, TRI terminology,
alternate pair member, gold label, refreshed state, Rule* vocabulary, or model output.

## Paginated collection

Each writer receives one questionnaire with eight task pages. The first four pages contain the 20
Stage A writing cards. The last four contain the corresponding Stage B intent judgments. Pagination
keeps the refreshed state out of view until all Stage A requests have been entered. The writer must
not return to or revise Stage A after entering Stage B. Each Stage B item dynamically displays the
writer's corresponding Stage A sentence, action, and selector before showing the refreshed state;
the required workflow order is not repeated. This removes long-delay recall from the intent measure
without revealing the design target. Each blind annotator's form is generated only
after the six writer questionnaires are complete because it embeds the collected instructions. Pair
members are never adjacent in an annotator's frozen order.

The forms use compact, separately rendered blocks for the task, selection criterion, visible state,
and operation order. Owner and uniformly actionable fields are omitted because they do not affect
the target decision. Each page contains five experimental items. A format-only weather/reminder
example demonstrates the expected short English response without exposing a TRI task template.
The legacy split forms remain in
the packet as an operational fallback; the combined form is the collection instrument.

## Irreversible two-stage writer procedure

Stage A stores the original instruction. Stage B then reveals the synchronized state and records
the writer's intended target or CLARIFY. The collector hashes the exact Stage A string. The return
validator rejects any record whose stored instruction hash does not match the Stage A response.
Required pagination prevents access to Stage B until all Stage A fields are complete. Participant
instructions prohibit returning to Stage A after refreshed-state disclosure. The platform does not
provide a verified immutable page lock, so this procedural control is recorded as a study
limitation.

## Blind interpretation and clarity gate

Each annotator sees the initial state, original instruction, synchronized state, action, and target
options in a randomized order. They do not see writer intent, condition, pair membership, model
outputs, or benchmark gold. Each response includes a target or CLARIFY and confidence from 1 to 5.

An item is clear when writer intent is determinate and at least two of three annotators choose that
intent. A pair is clear only when both members are clear. At least 40 clear complete pairs are
required before this study can replace the small rewrite PairAcc result in the main paper.
Otherwise, it remains a semantic-boundary analysis. All 120 rows remain in all-item sensitivity
reports.

## Frozen model evaluation

Qwen, GLM, and DeepSeek run on all 120 rows under intention-to-treat scoring. The primary equal-call
contrast is History-only versus Decision-visible. Calls, base actor payloads, state, and tool schema
are matched. Timing-reminder, CTA, and unchanged Rule* are secondary frozen baselines.

The primary endpoint is changed-pair PairAcc on clear complete pairs. Secondary outcomes are
all-item actionable E2E, Preserve conditional substitution, initial-binding error, database wrong
writes, and Rule* exact accuracy. Pair-cluster bootstrap is primary; writer and scenario-family
crossed sensitivity is supplementary. API, transport, parse, and incomplete outputs count as
intention-to-treat errors.

## Reporting boundary

Results enter the paper only after human clarity is computed without access to model predictions.
Negative, null, and adverse results are retained. The study may be called an independently authored
controlled-language holdout. It must not be called natural traffic, a native benchmark result, or a
prevalence study.
