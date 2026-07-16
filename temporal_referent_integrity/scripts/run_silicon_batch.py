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


def run_one(
    model: str,
    mode: str,
    split: str,
    para: str,
    condition: str,
    domains: str,
    limit: int | None,
    timeout: int,
    data: str,
    env: dict[str, str],
) -> None:
    cmd = [
        sys.executable,
        "-m",
        "tri.run_models",
        "--model",
        model,
        "--mode",
        mode,
        "--split",
        split,
        "--paraphrase",
        para,
        "--condition",
        condition,
        "--domains",
        domains,
        "--timeout",
        str(timeout),
        "--data",
        data,
    ]
    if limit:
        cmd.extend(["--limit", str(limit)])
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--key-file", default=str(DEFAULT_KEY_FILE))
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--modes", nargs="+", default=["interactive", "direct", "compiler"])
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
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--data", default=str(ROOT / "data" / "temporal_referent.jsonl"))
    args = ap.parse_args()

    env = os.environ.copy()
    env["LLM_API_KEY"] = load_key(Path(args.key_file))
    env["LLM_BASE_URL"] = args.base_url
    env["PYTHONPATH"] = str(ROOT)

    print(
        f"Running {len(args.models)} model(s), modes={args.modes}, "
        f"split={args.split}, paraphrase={args.paraphrase}, "
        f"condition={args.condition}, domains={args.domains}"
    )
    for model in args.models:
        for mode in args.modes:
            run_one(
                model,
                mode,
                args.split,
                args.paraphrase,
                args.condition,
                args.domains,
                args.limit,
                args.timeout,
                args.data,
                env,
            )


if __name__ == "__main__":
    main()
