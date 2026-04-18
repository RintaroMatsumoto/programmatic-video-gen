#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add English translations (narration_en, subtitle_en) to each scene in the
ukiyoe scene JSON using Claude.

Usage:
    python scripts/ukiyoe/translate_subtitles.py kanagawa_wave
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from anthropic import Anthropic
except ImportError:
    print("[error] pip install anthropic python-dotenv")
    sys.exit(2)

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-7")


SYSTEM = (
    "You are a professional translator specializing in Japanese art and culture. "
    "Translate Japanese narration and subtitles into natural, literary English "
    "suitable for a YouTube audience. Keep the tone calm and intellectual. "
    "Return ONLY a JSON object of the translations, no code fences."
)


def translate_scenes(client: Anthropic, scenes: list[dict]) -> list[dict]:
    payload = [
        {
            "id": s["id"],
            "narration_ja": s.get("narration_ja", ""),
            "subtitle_ja": s.get("subtitle_ja", ""),
        }
        for s in scenes
    ]
    prompt = (
        "Translate each entry's narration_ja and subtitle_ja into English.\n"
        "- narration_en: natural full sentences, same meaning\n"
        "- subtitle_en: concise, ≤80 chars, 1-2 lines\n"
        "Return a JSON array of objects: {id, narration_en, subtitle_en}.\n\n"
        f"Source:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n"
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    script_path = repo / "src" / "data" / "ukiyoe_scenes" / f"{args.name}.json"
    if not script_path.exists():
        print(f"[error] scene JSON not found: {script_path}")
        return 1

    data = json.loads(script_path.read_text(encoding="utf-8"))
    scenes = data.get("scenes", [])
    if not scenes:
        print("[error] no scenes in JSON")
        return 1

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[error] ANTHROPIC_API_KEY not set")
        return 2

    client = Anthropic(api_key=api_key)
    print(f"[claude] translating {len(scenes)} scenes ...")
    translations = translate_scenes(client, scenes)

    by_id = {t["id"]: t for t in translations}
    for s in scenes:
        t = by_id.get(s["id"])
        if t:
            s["narration_en"] = t.get("narration_en", "")
            s["subtitle_en"] = t.get("subtitle_en", "")

    script_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[ok] updated {script_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
