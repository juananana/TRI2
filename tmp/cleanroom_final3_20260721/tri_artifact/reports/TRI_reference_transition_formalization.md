# Post-Binding Temporal Authorization: Formalization Notes

This document freezes the formal claim before the next paper rewrite. It distinguishes the
denotation of a discourse reference from the target that may legally be sent to a tool.

## Objects

- `H_t`: interaction history through time `t`, including user language and tool observations.
- `S_t`: world state observed at time `t`.
- `r`: an action-target reference introduced at time `tau`.
- `d_t(r) in E`: the discourse denotation of `r`. A deleted entity can remain the historical
  denotation even though it is absent from `S_t`.
- `q_r(S)`: the selector associated with `r`, when the instruction licenses evaluation.
- `V_a(e, S)`: whether entity `e` is present and satisfies action `a`'s preconditions in `S`.
- `Gamma_{t+1}(r, e -> e')`: whether the user's language in `H_{t+1}` authorizes replacing
  denotation `e` by `e'` at this transition. Authorization may be unconditional reevaluation or
  conditional on a compiled guard.
- `pi_r`: fallback policy when the committed entity is not action-valid.
- `C_t(r)`: referential control state, either `U(q_r)` for an unresolved query or `B(e)` for a
  bound identity commitment.

The executable lifecycle record `L(r) = (m, e, q, g, pi, V_a)` is one implementation of these
semantics, not the definition itself.

## Temporal Referent Integrity

TRI is a post-binding safety property:

```text
d_{t+1}(r) != d_t(r)  =>  Gamma_{t+1}(r, d_t(r) -> d_{t+1}(r)).
```

The corresponding control-state machine is:

```text
U(q) -- authorized evaluation in S_t --> B(q(S_t))
B(e) -- preserve ---------------------> B(e)
B(e) -- authorized reevaluation ------> B(q(S_{t+1}))
B(e) -- invalid + reject -------------> B(e), emit bottom
```

The last branch separates discourse identity from execution: rejection suppresses an action but
does not silently replace the referent. Returning from `B(e)` to executable query evaluation is a
privileged transition and requires language-derived authorization.

Equivalently, a world transition alone cannot change an established denotation. A selector
changing winner, an entity losing a property, or a display-name collision is evidence about the
world, not authorization to reinterpret the user's earlier reference.

Action execution is governed separately:

```text
Execute(a, e, S_t)  =>  V_a(e, S_t).
```

For a preserved reference, failed validity does not itself change `d_t(r)`. The controller emits
no tool target under a reject policy, or follows an explicitly authorized replacement policy.
Thus identity persistence, action validity, and replacement authorization are three distinct
questions.

## Transition Semantics

For a reference bound to `e` before a refresh:

```text
preserve and V_a(e, S_1)                         -> emit e
preserve and not V_a(e, S_1) and pi = reject    -> emit bottom
conditional and g(e, q, S_1)                    -> emit e
conditional and not g(e, q, S_1)                -> emit q(S_1)
reevaluate                                       -> emit q(S_1)
```

`bottom` is an execution outcome, not necessarily a null discourse denotation.

## Proposition 1: Refreshed-State Indistinguishability

Any deterministic controller whose target decision depends only on `(S_1, q, a)` cannot be
correct on every preserve/reevaluate minimal pair.

**Construction.** Choose states with `q(S_0) = e_0`, `q(S_1) = e_1`, `e_0 != e_1`, and both
entities action-valid in `S_1`. Give one history an instruction that binds `q` before refresh and
later refers back to that entity; give the other an instruction that defers evaluation until
after refresh. The controller receives identical `(S_1, q, a)` in both cases and therefore emits
the same target, but the authorized targets are `e_0` and `e_1`. It must fail at least one.

## Proposition 2: ID-Only State Is Insufficient

Any deterministic controller whose state is only `(e_old, S_1, q, a)` cannot distinguish a
committed old identity from a cached result of a deliberately late-bound selector.

**Construction.** In the pair above, let both controllers cache `e_old = q(S_0) = e_0`. In the
first history the ID is the denotation established by discourse; in the second it is merely a
stale observation made before the licensed decision point. All stored fields are equal while the
authorized outputs differ. A reference-mode or equivalent authorization bit is necessary.

## Proposition 3: Validity Does Not Determine Replacement

Action validity alone cannot determine the correct response to an invalid committed target.

**Construction.** Hold `e`, `S_1`, `q`, and `V_a(e, S_1) = false` fixed. One instruction says to
act on `e` and otherwise stop; another says to use `q(S_1)` if `e` is no longer actionable. Their
correct outputs are `bottom` and `q(S_1)`, respectively. Therefore replacement requires a
language-derived fallback authorization, not merely a precondition check.

## Claim Boundary

These propositions establish informational insufficiency for controller states that omit
post-binding authorization. They do not prove that the proposed fields are mathematically
minimal, that an LLM will compile them correctly, or that a deterministic gate can repair a wrong
mode or bound ID. Compilation, selector grounding, and enforcement remain separately measurable
failure stages.

TRI concerns temporal stability of discourse denotations in agent control, not temporal foreign-
key integrity in databases.
