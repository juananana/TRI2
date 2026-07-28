# Style Extraction: ChatGPT Image Jul 28, 2026, 08_42_19 PM.png

## 1. Palette
| role | extracted / chosen hex | used on |
|---|---|---|
| background | `#FFFFFF` | page |
| panel fill | `#FBFBFA` | major regions |
| primary ink | `#264A56` | headings and neutral structure |
| border stroke | `#B8C7C9` | panels and readout blocks |
| Preserve | `#E56D4E` / `#FCEDE8` | committed path |
| Reevaluate | `#248D82` / `#E8F5F2` | deferred path |
| refresh | `#EABC6B` / `#FBF2DE` | shared transition |
| valid execution | `#60AA84` / `#EDF7F1` | action-valid and state diff |
| muted text | `#66747A` | slice and boundary labels |

The reference clusters around `#318990`, `#F16555`, `#EFD0AB`, near-white, charcoal, and gray.
The candidate deliberately maps those roles onto the established TRI palette rather than copying
the raster's brighter red and cyan values.

## 2. Typography
- Heading font: Arial, 34 px, bold.
- Subheading font: Arial, 28 px, bold.
- Body text: Arial, 24-26 px.
- Small label: Arial, 21-22 px; no label below 20 px in the candidate.
- Formula variables: Arial italic where supported; otherwise plain math-like labels.

## 3. Shape Language
- Corner radius: 12-16 px.
- Panel stroke: 2 px; semantic trajectories: 4 px.
- Dashed pattern: 10 8 for Reevaluate and eligible-slice groups.
- No shadows; pale fills at full opacity.

## 4. Layout Rhythm
- Canvas: 1800 x 720 px.
- Outer margin: 24 px.
- Major panel gaps: 16 px.
- Internal padding: 18-24 px.
- Grid: 8 px rhythm.

## 5. Arrow Grammar
- Arrow type: filled classic.
- Routing: straight for temporal trajectories; orthogonal for probe I/O.
- Coral solid = Preserve; teal dashed = Reevaluate; amber = shared refresh; green = executed change.
- Direct labels rather than a separate legend.

## 6. Icon Language
- Minimal editable primitives: entity circles, clock, lock marker, controller rectangle, database
  cylinder, document/state-diff box.
- Icons are semantic only; no decorative gear or robot.

## 7. Density And Composition
- Three major panels A/B/C.
- Medium-dense, wide landscape.
- Moderate whitespace; panel labels A/B/C.
- No embedded caption.

## Semantic Justification
| element | visual form | meaning | unit | justified? |
|---|---|---|---|---|
| A/B entity circles | labeled circles | selector winners and action targets | one circle = one entity ID | yes |
| solid/dashed paths | arrows | bound versus deferred resolution | one line = one pair member | yes |
| clock | circle plus hands | refresh boundary | one icon = shared refresh event | yes |
| controller box | neutral rectangle | black-box controller probe | one box = same tested interface | yes |
| database and diff | cylinder and document | executed tool mutation and state change | one icon = one recorded stage | yes |

