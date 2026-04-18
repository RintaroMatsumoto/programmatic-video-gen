#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download a public-domain ukiyoe image to public/ukiyoe/<name>/original.jpg.

Source priority:
1. Hardcoded high-resolution Wikimedia Commons URLs for known works.
2. Metropolitan Museum of Art Open Access API (CC0).

Usage:
    python scripts/ukiyoe/download_source.py kanagawa_wave
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import requests

sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# Known works registry. URLs are Wikimedia Commons "Special:FilePath" links
# that redirect to the full-resolution original.
# ---------------------------------------------------------------------------
WORKS: dict[str, dict] = {
    "kanagawa_wave": {
        "title_ja": "神奈川沖浪裏",
        "title_en": "Under the Wave off Kanagawa",
        "artist": "葛飾北斎",
        "year": 1831,
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/0a/The_Great_Wave_off_Kanagawa.jpg",
        "source": "Wikimedia Commons (PD)",
        "license": "public domain",
    },
    "gaifu_kaisei": {
        "title_ja": "凱風快晴",
        "title_en": "Fine Wind, Clear Morning",
        "artist": "葛飾北斎",
        "year": 1831,
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Red_Fuji_southern_wind_clear_morning.jpg",
        "source": "Wikimedia Commons (PD)",
        "license": "public domain",
    },
    "yamashita_hakuu": {
        "title_ja": "山下白雨",
        "title_en": "Storm below Mount Fuji",
        "artist": "葛飾北斎",
        "year": 1831,
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/dd/Katsushika_Hokusai_-_Thirty-six_Views_of_Mount_Fuji-_Rainstorm_Beneath_the_Summit_%28Sanka_hakuu%29_-_2008.238_-_Cleveland_Museum_of_Art.tiff",
        "source": "Wikimedia Commons (PD)",
        "license": "public domain",
    },
}


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def download_image(url: str, dest: Path) -> None:
    """Stream-download an image with a browser-like UA (Wikimedia blocks python-requests default)."""
    headers = {
        "User-Agent": "ProgrammaticVideoGen/0.1 (https://github.com/RintaroMatsumoto/ProgrammaticVideoGen)"
    }
    with requests.get(url, stream=True, headers=headers, timeout=60) as r:
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 16):
                f.write(chunk)


def save_metadata(work: dict, meta_path: Path) -> None:
    import json
    meta_path.write_text(
        json.dumps(work, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Work name (e.g. kanagawa_wave)")
    parser.add_argument("--list", action="store_true", help="List known works")
    args = parser.parse_args()

    if args.list:
        for k, v in WORKS.items():
            print(f"{k:20s} {v['title_ja']}  ({v['artist']}, {v['year']})")
        return 0

    if args.name not in WORKS:
        print(f"[error] unknown work: {args.name}")
        print("Run with --list to see known works.")
        return 1

    work = WORKS[args.name]
    out_dir = get_repo_root() / "public" / "ukiyoe" / args.name
    out_dir.mkdir(parents=True, exist_ok=True)

    # determine extension from URL
    ext = Path(work["url"]).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".tiff"):
        ext = ".jpg"

    dest = out_dir / f"original{ext}"
    if dest.exists():
        print(f"[skip] already exists: {dest}")
    else:
        print(f"[fetch] {work['url']}")
        download_image(work["url"], dest)
        print(f"[ok] saved to {dest}")

    # If tiff, convert to jpg for Remotion compatibility
    if ext == ".tiff":
        try:
            from PIL import Image
            jpg_dest = out_dir / "original.jpg"
            with Image.open(dest) as im:
                im.convert("RGB").save(jpg_dest, "JPEG", quality=95)
            print(f"[convert] TIFF → JPG: {jpg_dest}")
        except Exception as e:
            print(f"[warn] TIFF→JPG failed: {e}")

    meta_path = out_dir / "metadata.json"
    save_metadata(work, meta_path)
    print(f"[ok] metadata: {meta_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
