# Strengthened Handcrafted Discourse-Rule Baseline Protocol

Version: v2, defined after inspecting v1 unresolved cases on the v3, human-rewrite, and v7
inventories on 2026-07-21.

This is an explicitly post-hoc, benchmark-aware upper baseline. It does not replace
the frozen v1 result and is not confirmatory evidence. Its purpose is adversarial:
measure how much of the benchmark can be solved by expanding a hand-written event
vocabulary and by handling the deterministic single-candidate case correctly.

The allowed and forbidden inputs are unchanged from
`TRI_deterministic_discourse_rule_protocol.md`. In particular, v2 still cannot read
`binding`, `selector`, any pre/post/gold target, update label, style, or new leader.

Relative to v1, v2 makes exactly two changes:

1. The target-selection event vocabulary additionally recognizes `record`, `resolve`,
   `look over/through`, `note`, `inspect`, `settle on`, `show me`, and `refind`, as
   observed in benchmark language. `longest` is added as a maximum-ranking cue.
2. If action-precondition filtering leaves exactly one entity, the selector returns
   that entity without requiring a varying ranking field.

No further rules will be added after running v2. All v1 and v2 results and protocols
must be retained together. A high v2 score shows benchmark solvability by a tailored
program; it does not establish natural-language generalization. A lower score on the
independent human rewrites is the relevant evidence for the remaining value of semantic
compilation.
