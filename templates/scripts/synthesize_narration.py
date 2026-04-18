#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Synthesize narration WAV files for each scene via VOICEVOX HTTP API.

Requires a running VOICEVOX engine (default: http://127.0.0.1:50021).

Default speaker: 16 (九州そら・ノーマル) —落ち着いた女性声。
変更するには --speaker 引数、または scenes[i].speaker 属性で。

Usage:
    python scripts/ukiyoe/synthesize_narration.py kanagawa_wave
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_ENGINE = "http://127.0.0.1:50021"
DEFAULT_SPEAKER = 16  # 九州そら ノーマル


def synth_one(text: str, speaker: int, engine: str) -> bytes:
    q = requests.post(
        f"{engine}/audio_query",
        params={"text": text, "speaker": speaker},
        timeout=30,
    )
    q.raise_for_status()
    query = q.json()
    # slight pacing tweaks for narration
    query["speedScale"] = 0.96
    query["prePhonemeLength"] = 0.2
    query["postPhonemeLength"] = 0.3

    s = requests.post(
        f"{engine}/synthesis",
        params={"speaker": speaker},
        json=query,
        timeout=60,
    )
    s.raise_for_status()
    return s.content


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--engine", default=DEFAULT_ENGINE)
    parser.add_argument("--speaker", type=int, default=DEFAULT_SPEAKER)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    scene_path = repo / "src" / "data" / "ukiyoe_scenes" / f"{args.name}.json"
    if not scene_path.exists():
        print(f"[error] scene JSON not found: {scene_path}")
        return 1
    data = json.loads(scene_path.read_text(encoding="utf-8"))

    out_dir = repo / "public" / "ukiyoe" / args.name / "audio"
    out_dir.mkdir(parents=True, exist_ok=True)

    # health check
    try:
        requests.get(f"{args.engine}/version", timeout=5)
    except Exception as e:
        print(f"[error] VOICEVOX engine not reachable at {args.engine}: {e}")
        print("Start VOICEVOX first (voicevox_engine/run.exe).")
        return 2

    for scene in data["scenes"]:
        text = scene.get("narration_ja", "").strip()
        if not text:
            continue
        speaker = scene.get("speaker", args.speaker)
        out_wav = out_dir / f"scene_{scene['id']:02d}.wav"
        if out_wav.exists():
            print(f"[skip] {out_wav.name}")
            continue
        print(f"[synth] scene {scene['id']:02d}  speaker={speaker}  chars={len(text)}")
        wav_bytes = synth_one(text, speaker, args.engine)
        out_wav.write_bytes(wav_bytes)
        scene["audio_path"] = f"ukiyoe/{args.name}/audio/{out_wav.name}"

    # write back with audio_path annotations
    scene_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[ok] audio written to {out_dir}")
    print(f"[ok] updated {scene_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
