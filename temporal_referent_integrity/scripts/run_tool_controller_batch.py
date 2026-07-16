from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--modes", nargs="+", required=True)
    ap.add_argument("--split", default="dev", choices=["dev", "heldout", "all"])
    ap.add_argument("--paraphrase", default="p0", choices=["p0", "p1", "p2", "p3", "p4", "all"])
    ap.add_argument("--condition", default="all", choices=[
        "all",
        "anchored-flip",
        "anchored-stable",
        "dynamic-flip",
        "dynamic-stable",
        "anchored-removed",
        "dynamic-removed",
    ])
    ap.add_argument("--domains", default="all")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--timeout", type=int, default=90)
    args = ap.parse_args()

    env = os.environ.copy()
    env["LLM_API_KEY"] = load_key(Path(args.key_file))
    env["LLM_BASE_URL"] = args.base_url
    env["PYTHONPATH"] = str(ROOT)

    for model in args.models:
        for mode in args.modes:
            cmd = [
                sys.executable,
                "-m",
                "tri.run_tool_controllers",
                "--model",
                model,
                "--mode",
                mode,
                "--split",
                args.split,
                "--paraphrase",
                args.paraphrase,
                "--condition",
                args.condition,
                "--domains",
                args.domains,
                "--timeout",
                str(args.timeout),
            ]
            if args.limit:
                cmd.extend(["--limit", str(args.limit)])
            subprocess.run(cmd, cwd=ROOT, env=env, check=True)


if __name__ == "__main__":
    main()
