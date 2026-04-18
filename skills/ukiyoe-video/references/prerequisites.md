# Prerequisites

Everything that must exist before `py scripts\ukiyoe\generate.py` will run end-to-end.

## Runtime

| Tool       | Version | Check                      |
| ---------- | ------- | -------------------------- |
| Node.js    | 18+     | `node --version`           |
| npm        | 9+      | `npm --version`            |
| Python     | 3.11+   | `py --version`             |
| FFmpeg     | 6+      | `ffmpeg -version` (on PATH) |

## Python packages

```
pip install --upgrade requests Pillow anthropic python-dotenv
```

Optional (Phase 2 only):

```
pip install torch diffusers accelerate transformers segment-anything
```

## Node packages

Inside the project directory:

```
npm install
```

The project must contain Remotion in `node_modules/`. If not, `npm install remotion @remotion/cli @remotion/bundler react react-dom`.

## VOICEVOX Engine (Japanese TTS)

Download the engine from https://voicevox.hiroshiba.jp/ and run it locally. Default endpoint: `http://127.0.0.1:50021`.

Confirm:

```
curl http://127.0.0.1:50021/version
```

Speaker IDs commonly used:

- `16` — 九州そら ノーマル (plugin default — calm, lower-register narration)
- `8`  — 春日部つむぎ ノーマル
- `3`  — ずんだもん ノーマル
- `1`  — 四国めたん ノーマル
- `13` — 青山龍星

Pass `--speaker <id>` to `synthesize_narration.py`, or set `scenes[i].speaker` in the scene JSON to override per-scene.

## Anthropic API key

Create `.env` at the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

The scripts read this via `python-dotenv`. The key is also honored from `os.environ`.

## Directory layout expected by the pipeline

```
<repo-root>/
├── .env
├── package.json
├── tsconfig.json
├── remotion.config.ts
├── scripts/
│   └── ukiyoe/
│       ├── generate.py
│       ├── download_source.py
│       ├── generate_script.py
│       ├── translate_subtitles.py
│       ├── synthesize_narration.py
│       └── _healthcheck.py
├── src/
│   ├── index.ts             # registerRoot(RemotionRoot)
│   ├── Root.tsx             # Composition registration
│   ├── components/
│   │   ├── KenBurns.tsx
│   │   └── BilingualSubtitle.tsx
│   ├── compositions/
│   │   └── UkiyoeAnimation.tsx
│   └── data/
│       └── ukiyoe_scenes/
│           └── <slug>.json
└── public/
    └── ukiyoe/
        └── <slug>/
            ├── original.jpg        # downloaded source
            └── audio/              # generated narration
```

Run `py scripts\ukiyoe\_healthcheck.py` before the first invocation — it validates all of the above.
