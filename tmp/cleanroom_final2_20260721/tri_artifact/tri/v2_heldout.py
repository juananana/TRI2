from __future__ import annotations

import argparse
import json
from pathlib import Path

from .v2_tasks import DATA, scalar_rows


HELDOUT_TEMPLATES = {
    "explicit_anchor": (
        "Before synchronizing the {app}, determine {selector}. Once synchronization finishes, "
        "{action} the {entity} you had selected."
    ),
    "implicit_anchor": (
        "Take note of {selector} in the current {app}. Reload the view, then {action} it."
    ),
    "explicit_dynamic": (
        "Synchronize the {app}. Only afterward choose {selector}, and {action} that {entity}."
    ),
    "implicit_dynamic": (
        "Do not settle on a target until the {app} has reloaded. From the new results, locate "
        "{selector} and {action} it."
    ),
}


def heldout_rows() -> list[dict]:
    rows: list[dict] = []
    for source in scalar_rows():
        row = dict(source)
        style = row["style"]
        row["id"] = row["id"].replace("v2-", "v2h-", 1)
        row["candidate"] = "temporal_referent_v2_heldout_paraphrase"
        row["split"] = "heldout"
        row["paraphrase"] = f"heldout_{style}"
        row["instruction"] = HELDOUT_TEMPLATES[style].format(**row)
        rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(DATA / "temporal_referent_v2_heldout.jsonl"))
    args = ap.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in heldout_rows():
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(path)


if __name__ == "__main__":
    main()
