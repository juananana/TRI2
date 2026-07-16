# Round 2 Protocol: Temporal Referent Integrity

## Research claim

LLM agents often store user goals as re-evaluable descriptions rather than as
typed temporal references. In dynamic environments, this can cause an entity
selected before a refresh to drift to a different entity after the refresh.

## Minimal falsifiable effect

For at least two model families:

- anchored + flip accuracy is low, with most errors selecting the refreshed
  post-refresh target;
- dynamic + flip accuracy remains high;
- stable controls are high, ruling out generic two-turn execution failure.

## Diagnostic split

- Direct mode: the model sees both states at once and resolves the target.
- Interactive mode: the model first refreshes, then chooses after observing the
  refreshed state.

Direct success with interactive failure supports the identity-persistence
mechanism. Direct failure suggests a binding-time inference failure.

## Method criterion

A reference-compiler intervention must improve anchored + flip by at least
15 percentage points without reducing dynamic + flip by more than 10 percentage
points. If it over-binds dynamic references, the method is only a prototype.

