from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_FILES = {
    "phase": "matched_pairacc_and_marginals.csv",
    "flow": "v7_shared_eligible_pairacc_and_substitution.csv",
    "writes": "v7_e2e_wrong_writes.csv",
    "gains": "revision_decision_visible_gains.csv",
    "transfer": "revision_source_grounded_by_source.csv",
    "enforcement": "revision_enforcement_and_failures.csv",
}


def load_tables(data_dir: Path) -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    for key, filename in REQUIRED_FILES.items():
        path = data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing required data file: {path}")
        tables[key] = pd.read_csv(path)
    return tables
