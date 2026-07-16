from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path


DEFAULT_KEY_FILE = Path("/Users/chu/Downloads/硅基流动密钥.rtf")
DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1"


def load_key(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"sk-[A-Za-z0-9_\-]{20,}", text)
    if not match:
        raise SystemExit(f"No API key matching sk-* found in {path}")
    return match.group(0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--key-file", default=str(DEFAULT_KEY_FILE))
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--contains", default="")
    args = ap.parse_args()
    key = load_key(Path(args.key_file))
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

