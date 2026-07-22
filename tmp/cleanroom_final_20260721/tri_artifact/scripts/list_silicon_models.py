from __future__ import annotations

import argparse
import json
import os
import urllib.request


DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1"


def load_key() -> str:
    key = os.environ.get("LLM_API_KEY", "").strip()
    if not key:
        raise SystemExit("Set LLM_API_KEY before running.")
    return key


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--contains", default="")
    args = ap.parse_args()
    key = load_key()
    req = urllib.request.Request(
        args.base_url.rstrip("/") + "/models",
        method="GET",
        headers={"Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        body = json.load(resp)
    ids = []
    for item in body.get("data", []):
        mid = item.get("id")
        if isinstance(mid, str) and args.contains.lower() in mid.lower():
            ids.append(mid)
    for mid in sorted(ids):
        print(mid)


if __name__ == "__main__":
    main()
