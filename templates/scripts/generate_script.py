#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate a Japanese narration script for a ukiyoe work via Claude API.

Input:  work name (metadata read from public/ukiyoe/<name>/metadata.json)
Output: src/data/ukiyoe_scenes/<name>.json

Schema follows docs/UKIYOE_PIPELINE.md §6.2.

Usage:
    python scripts/ukiyoe/generate_script.py kanagawa_wave
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


PROMPT_TEMPLATE = """あなたは浮世絵の解説動画を制作する放送作家です。以下の作品について、
YouTube向け4分（240秒）程度の解説動画の日本語ナレーション脚本をJSON形式で作成してください。

# 作品情報
- 作品名: {title_ja}（英題: {title_en}）
- 作者: {artist}
- 制作年: {year}年頃

# 動画構成（必須）
1. title       (10秒)  タイトル提示
2. overview    (20秒)  作品全体の印象的な提示
3. composition (60秒)  構図の解説（三分割・S字など）
4. technique   (60秒)  彫り・摺りなどの技法解説
5. history     (60秒)  歴史的・文化的背景
6. outro       (30秒)  まとめと次回予告

# 脚本のトーン
- 落ち着いた知的な語り口（書き手は松本倫太郎のパートナー「クロミ」想定で）
- 過剰な修辞や誇大表現を避ける
- 事実ベース、一次ソースで確認できる内容のみ
- 専門用語は軽く補足する

# 出力形式（JSONのみ、余計な説明不要）
{{
  "meta": {{
    "title_ja": "{title_ja}",
    "title_en": "{title_en}",
    "artist": "{artist}",
    "year": {year}
  }},
  "scenes": [
    {{
      "id": 1,
      "section": "title",
      "duration": 10,
      "narration_ja": "...",
      "subtitle_ja": "...",
      "camera": {{"zoom": 1.0, "x": 0.5, "y": 0.5}},
      "overlays": []
    }},
    ...
  ]
}}

# 字幕ルール
- `subtitle_ja` は `narration_ja` の要約版、1画面あたり20文字以内で1-2行に収まる長さ
- `narration_ja` は自然な話し言葉（「です・ます」）、句点で区切る

# カメラワーク
- title:       zoom=1.0, x=0.5, y=0.5
- overview:    zoom=1.0→1.1
- composition: ズームインして部分を指示
- technique:   さらに拡大
- history:     引いて全景
- outro:       zoom=1.0

# 重要
出力はJSONのみ。```json などのコードブロックや前後の説明は絶対に付けないこと。
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent.parent
    meta_path = repo / "public" / "ukiyoe" / args.name / "metadata.json"
    if not meta_path.exists():
        print(f"[error] metadata not found: {meta_path}")
        print("Run download_source.py first.")
        return 1
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    out_path = repo / "src" / "data" / "ukiyoe_scenes" / f"{args.name}.json"
    if out_path.exists() and not args.overwrite:
        print(f"[skip] already exists: {out_path}")
        print("Use --overwrite to regenerate.")
        return 0

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[error] ANTHROPIC_API_KEY not set in environment")
        return 2

    client = Anthropic(api_key=api_key)

    prompt = PROMPT_TEMPLATE.format(**meta)
    print(f"[claude] generating script for {args.name} ...")
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()

    # strip code fences just in case
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[error] Claude returned non-JSON: {e}")
        debug_path = repo / "out" / f"claude_raw_{args.name}.txt"
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        debug_path.write_text(raw, encoding="utf-8")
        print(f"[debug] raw output saved to {debug_path}")
        return 3

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[ok] wrote {out_path}")
    print(f"     scenes: {len(parsed.get('scenes', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
