# TRI Current Reproducibility Artifact

This archive corresponds to the current TRI AAAI manuscript. It contains frozen datasets,
raw model outputs, protocols, report generators, tests, external-pilot code, paper source,
and final figure PDFs. It also contains de-identified normalized human responses and aggregate
analysis, while API credentials, private answer mappings, workbooks, coordination forms, and
participant-identifying materials are excluded.

Run `PYTHONPATH=. python3 -m unittest discover -s tests` from `tri_artifact/` for the
included dependency-free scientific tests. The archive-packaging test is intentionally excluded
because it requires the parent submission tree. ToolSandbox tests require the pinned environment documented in
`external_pilots/toolsandbox_tri/README.md`. The downloaded AppWorld package, databases, and
released public trajectories are excluded; setup is documented in
`external_pilots/appworld_tri/README.md`. See `reports/` for frozen protocols and
machine-readable result reports. `SOURCE_MANIFEST.tsv` records the SHA-256 and byte size of
every archived source file.
