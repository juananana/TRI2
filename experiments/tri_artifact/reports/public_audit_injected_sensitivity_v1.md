# Public-Audit Injected Sensitivity Check

**Evidence status:** post-primary zero-API implementation sensitivity check.

Strict-positive controls recovered: 30/30.
One-feature-missing controls excluded: 30/30.

| Suite | Positive recall | Hard-negative exclusion | Errors |
|---|---:|---:|---|
| ToolSandbox | 100% | 100% | none |
| AppWorld | 100% | 100% | none |
| tau3-bench | 100% | 100% | none |
| API-Bank | 100% | 100% | none |
| BFCL | 100% | 100% | none |
| ToolTalk | 100% | 100% | none |

This checks the deterministic checklist implementation on known-label injected controls. It does not estimate recall on natural benchmark opportunities, validate semantic retrieval, or establish systematic benchmark undercoverage.
