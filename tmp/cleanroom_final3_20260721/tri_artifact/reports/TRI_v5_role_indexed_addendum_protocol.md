# TRI-v5 Role-Indexed Repair Addendum

Frozen after observing the scalar lifecycle failure on TRI-v5 and before any model call to the
role-indexed controller. This is an explicitly exploratory repair, not a preregistered primary
comparison.

## Motivation and fixed hypothesis

The scalar lifecycle compiler conflated an observation-only monitoring referent with the action
referent on 12/40 TRI-v5 tasks. The repair represents references as a set keyed by discourse role.
Only the unique `action_target` record can authorize mutation; `monitoring_reference` is never
read by the mutation gate.

The fixed hypothesis is that role indexing improves dynamic-task target accuracy and reduces
wrong-entity writes relative to the scalar lifecycle controller without reducing anchored-task
accuracy.

## Development and stop rule

Use the existing eight-task TRI-v5 smoke set only to verify JSON compliance, role validation, and
tool-trace completeness. Stop before a full run if there is any wrong write, more than one
API/parse failure, or fewer than 7/8 correct targets. No prompt change is permitted after passing
smoke. A full TRI-v5 result is reported as post-hoc development evidence and is not used as an
unbiased generalization estimate.

## Metrics

Report all 40 tasks intention-to-treat: target accuracy, final-state accuracy, anchored/dynamic
accuracy, wrong writes, unnecessary rejections, API/parse failures, and paired differences from
both scalar Lifecycle and Generic. Any later confirmatory validation must use newly generated,
frozen compositional templates not inspected during development.
