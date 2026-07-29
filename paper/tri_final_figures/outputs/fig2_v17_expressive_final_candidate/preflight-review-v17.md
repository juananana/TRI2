# Figure 2 v17 Draw.io Preflight Review

The final preflight has zero FAIL findings. Five WARN findings remain and were reviewed:

| warning | decision | reason |
|---|---|---|
| horizontal spacing variance near Preserve | retain | the route is intentionally asymmetric around the shared transition rather than a regular pipeline grid |
| horizontal spacing variance near Reevaluate | retain | the deferred route uses a longer semantic arc to the shared refresh and S1 |
| vertical spacing variance near the fixed icon | retain | title, contract, and instruction layers have different hierarchy and therefore different vertical intervals |
| probe `P` token marked as solitary decoration | retain | it is the Preserve member of the independently replayed matched pair |
| probe `R` token marked as solitary decoration | retain | it is the Reevaluate member of the independently replayed matched pair |

No remaining warning represents overflow, collision, missing semantics, or decorative noise.
