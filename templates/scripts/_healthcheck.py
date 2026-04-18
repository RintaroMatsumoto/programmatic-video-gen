#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick health check for the ukiyoe pipeline environment."""
from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent.parent


def check_env() -> bool:
    env_file = REPO / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("ANTHROPIC_API_KEY="):
                v = line.split("=", 1)[1].strip()
                if v and v not in ("", '""', "''"):
                    print("[ok] ANTHROPIC_API_KEY present in .env")
                    return True
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("[ok] ANTHROPIC_API_KEY present in env")
        return True
    print("[ng] ANTHROPIC_API_KEY not set (.env or env)")
    return False


def check_voicevox() -> bool:
    try:
        r = urllib.request.urlopen(
            "http://127.0.0.1:50021/version", timeout=3
        )
        print(f"[ok] VOICEVOX {r.status} {r.read().decode().strip()}")
        return True
    except Exception as e:
        print(f"[ng] VOICEVOX unreachable: {e}")
        return False


def check_pydeps() -> bool:
    missing = []
    for mod in ("requests", "PIL", "anthropic", "dotenv"):
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)
    if missing:
        print(f"[ng] missing Python deps: {missing}")
        return False
    print("[ok] core python deps present")
    return True


def check_node() -> bool:
    nm = REPO / "node_modules" / "remotion"
    if nm.exists():
        print("[ok] node_modules/remotion present")
        return True
    print("[ng] node_modules missing — run `npm install`")
    return False


def main() -> int:
    checks = [check_pydeps(), check_env(), check_voicevox(), check_node()]
    if all(checks):
        print("\n[summary] all good — ready to run generate.py")
        return 0
    print("\n[summary] fix the [ng] items above, then retry")
    return 1


if __name__ == "__main__":
    sys.exit(main())
