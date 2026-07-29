# Figure 2 v18 Preflight Review

Final report: `preflight-v18.json`

Result: 0 FAIL, 6 WARN, passed.

| rule | element | review | disposition |
|---|---|---|---|
| `spacing-inconsistent-h` | `preserve` row | The checker groups instruction, state, gold, run token, probe, and output chip into one row even though they are four semantic regions. Their gaps intentionally widen at region boundaries. | Accepted. Within-region alignment is consistent in `drawio-final.png`. |
| `spacing-inconsistent-h` | `reevaluate` row | The row includes an instruction at left and gold/probe/output elements at right, separated by the shared transition field. Uniform spacing would erase the semantic grouping. | Accepted. The route supplies continuity across the intentional gap. |
| `solitary-decoration-block` | `refresh` | The amber hollow lens is the only shared refresh event; it is not decoration. | Accepted. External `REFRESH` label and incoming/outgoing shared rail name its role. |
| `solitary-decoration-block` | `probe-p` | The coral `P` circle identifies the Preserve invocation of the same probe. | Accepted. It maps to the Preserve row and solid path. |
| `solitary-decoration-block` | `probe-r` | The teal `R` circle identifies the Reevaluate invocation of the same probe. | Accepted. It maps to the Reevaluate row and dashed path. |
| `orphan-empty-box` | `refresh` | The lens is intentionally icon-like and hollow to avoid crowding; its label is adjacent rather than inside. | Accepted. The final screenshot shows no ambiguity or missing label. |

The earlier `text-overflow-vertical` warning for `execution-flow` was resolved by changing the editable source from `target ID -> tool write -> state diff` to `ID -> write -> state diff`. No warning remains for text fit.

Visual evidence:

- `drawio-final.png`: complete 1920x800 canvas-only export of the editable source.
- `fig2_tri_diagnostic_workflow_v18_paper_readable.png`: rich standalone export.
- `fig2_tri_diagnostic_workflow_v18_paper_readable_grayscale.png`: grayscale standalone export.
- `tmp/fig2_upgrade_audit/manuscript_page5_v18.png`: final paper-scale placement.
- `tmp/fig2_upgrade_audit/manuscript_page5_v18_gray.png`: final paper-scale grayscale placement.
