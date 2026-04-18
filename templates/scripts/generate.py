#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ukiyoe pipeline orchestrator.

単一作品に対して、パイプライン各段を順に走らせる。
失敗したステップで停止する。スキップしたい段階は --skip で除外。

MVPでは以下3ステップで完結:
    download → script → narration

フルパイプライン:
    download → script → translate → narration → segment → depth

Usage:
    python scripts/ukiyoe/generate.py kanagawa_wave
    python scripts/ukiyoe/generate.py kanagawa_wave --skip segment depth
    python scripts/ukiyoe/generate.py kanagawa_wave --mvp
    python scripts/ukiyoe/generate.py kanagawa_wave --full
    python scripts/ukiyoe/generate.py kanagawa_wave --render
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

REPO = Path(__file__).resolve().parent.parent.parent
PY = sys.executable

MVP_STEPS = ["download", "script", "translate", "narration"]
FULL_STEPS = ["download", "script", "translate", "narration", "segment", "depth"]

STEP_SCRIPTS = {
    "download":  REPO / "scripts" / "ukiyoe" / "download_source.py",
    "script":    REPO / "scripts" / "ukiyoe" / "generate_script.py",
    "translate": REPO / "scripts" / "ukiyoe" / "translate_subtitles.py",
    "narration": REPO / "scripts" / "ukiyoe" / "synthesize_narration.py",
    "segment":   REPO / "scripts" / "ukiyoe" / "segment_layers.py",
    "depth":     REPO / "scripts" / "ukiyoe" / "estimate_depth.py",
}


def run_step(step: str, name: str, extra: list[str]) -> int:
    script = STEP_SCRIPTS[step]
    if not script.exists():
        print(f"[warn] {step}: script missing → {script}")
        return 0
    print(f"\n===== [{step}] {script.name} =====")
    cmd = [PY, str(script), name, *extra]
    res = subprocess.run(cmd, cwd=REPO)
    return res.returncode


def remotion_render(composition_id: str, out_name: str) -> int:
    """
    npx remotion render を呼び出す薄いラッパ。
    事前に Root.tsx 側でコンポジション登録が必要。
    """
    out_dir = REPO / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{out_name}.mp4"
    print(f"\n===== [render] {composition_id} → {out_path} =====")
    cmd = ["npx", "remotion", "render", composition_id, str(out_path)]
    res = subprocess.run(cmd, cwd=REPO, shell=(sys.platform == "win32"))
    return res.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--mvp", action="store_true", help="MVP 4-step path (default)")
    parser.add_argument("--full", action="store_true", help="Phase-2 full path (SAM + Depth)")
    parser.add_argument("--skip", nargs="*", default=[],
                        help="Skip steps (names from: %(default)s)")
    parser.add_argument("--render", action="store_true",
                        help="After pipeline, call Remotion render")
    parser.add_argument("--composition",
                        help="Remotion composition id for --render")
    args = parser.parse_args()

    if args.full:
        steps = FULL_STEPS
    else:
        steps = MVP_STEPS

    steps = [s for s in steps if s not in args.skip]
    print(f"[plan] {args.name} → {' → '.join(steps)}")

    for step in steps:
        rc = run_step(step, args.name, [])
        if rc != 0:
            print(f"\n[fail] step '{step}' returned {rc}. aborting.")
            return rc

    if args.render:
        comp_id = args.composition
        if not comp_id:
            # 既定: <Name> をキャメル化して接頭に Ukiyoe
            parts = [p.capitalize() for p in args.name.split("_")]
            comp_id = "Ukiyoe" + "".join(parts)
        rc = remotion_render(comp_id, args.name)
        if rc != 0:
            print(f"\n[fail] remotion render returned {rc}")
            return rc

    print(f"\n[done] pipeline for '{args.name}' completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
