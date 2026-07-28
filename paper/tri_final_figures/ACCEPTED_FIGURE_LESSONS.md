# Figure Lessons From Recent Accepted Work

The current TRI figure design was checked against recent accepted evaluation and agent papers,
including AAAI-24 ExpeL, AAAI-26 MetaEval, AAAI-26 MCP-AgentBench, ICLR-24 AgentBench, NeurIPS-24
AgentDojo, and Findings of NAACL-25 ToolSandbox. The local `draw_learning/` packet also contains
phase-space, trajectory, attribution, and clustering references used for visual study.

## Recurring Patterns

- Result figures use position, slope, uncertainty, density, or area before explanatory prose.
- Phase maps work well when two endpoints jointly define a behavioral regime.
- Small multiples and slope plots show repeated controller/model contrasts without a large legend.
- Heatmaps or proportional flows are used for structured decompositions; full exact matrices stay
  in tables.
- Direct labels are short. Captions carry definitions, denominator qualifications, and caveats.
- Complex box-and-arrow diagrams are reserved for system construction or mechanism overviews.

## TRI Mapping

- Figure 1 remains the shared-transition mechanism overview.
- Figure 2 uses a Preserve/Reevaluate policy phase map with PairAcc annotations.
- Figure 3 uses uncertainty-aware Generic-to-CTA slopes for conditional substitution.
- Figure 4 combines complete SQLite outcome accounting with the Stable/Changed strict-case slope.
- Figure 5 uses an effect-and-CI matrix for authored and source-derived transfer.

## Rejected Patterns

- Long titles, subtitles, and sentence-like labels inside result graphics.
- Repeated rounded boxes for numerical outcomes.
- A figure that reproduces a table cell by cell.
- Connecting unrelated datasets or denominators as if they were a continuous trajectory.
- Decorative complexity that does not encode an estimand, comparison, hierarchy, or uncertainty.

## Unified Result-Figure Refinement

- Do not force boundary estimates into symmetric error bars. For a 0% binomial estimate, retain the
  one-sided Wilson interval and expose its lower cap beyond the marker so the endpoint is visibly
  complete without implying an impossible negative rate.
- Keep markers subordinate to the interval and comparison geometry. A 3--4 pt endpoint is enough
  at single-column size when color, shape, and fill provide redundant identification.
- Let adjacent panels divide the argument. One panel should show the paired within-model change;
  the next can group by controller to show cross-model consistency instead of repeating the same
  pairing with a second legend.
- When adjacent figures already use several endpoint-and-interval comparisons, a compact effect
  matrix can expose cross-metric heterogeneity without another forest or dumbbell panel.
- Direct-label only a sparse set of decisive values. Rounded percentages can sit above six bars;
  exact counts and denominator qualifications belong in the caption and frozen table.
- Remove arrows unless direction itself is an estimand or process relation. Ordered axes and linked
  endpoints already communicate a Generic-to-CTA contrast.
- Vary form only when the data structure changes. The SQLite Stable/Changed comparison retains a
  slope because the transition is the result; transfer uses a two-column effect matrix because its
  ten estimates form a model-by-endpoint comparison. Each matrix cell still carries its effect and
  CI, with fill and border style indicating whether the interval excludes zero.
