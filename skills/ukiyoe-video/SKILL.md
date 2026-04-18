---
name: ukiyoe-video
description: Use when the user wants to generate a narrated art-commentary video about a specific ukiyo-e print (e.g., "Great Wave off Kanagawa", "神奈川沖浪裏", "富嶽三十六景"). Orchestrates a six-scene pipeline — title, overview, composition, technique, history, outro — with Japanese + English narration, Ken Burns camera work, and bilingual subtitles. Produces a Remotion-renderable 4-minute MP4. Triggers include phrases like "make a video about this print", "浮世絵の解説動画を作って", "Hokusai explainer", or any reference to a specific ukiyo-e work combined with video/narration intent.
---

# Ukiyo-e Explainer Video

Generate a four-minute art-commentary video about a single ukiyo-e print. The output is a Remotion composition that renders to 1920×1080 MP4 with Japanese narration, English narration, and bilingual on-screen subtitles.

## When to use this skill

Invoke when the user asks for any of:

- A narrated video about a specific ukiyo-e print (Hokusai, Hiroshige, Utamaro, Sharaku, etc.).
- An "art explainer" pipeline for Japanese woodblock prints.
- Bilingual (JP/EN) art commentary with title → overview → composition → technique → history → outro structure.

If the user wants a generic Remotion scene (not ukiyo-e), use the `remotion-scene` skill instead.

## Prerequisites

Before running anything, confirm these are installed and configured. Details in `references/prerequisites.md`.

- Node.js 18+ and npm
- Python 3.11+
- `ANTHROPIC_API_KEY` in `.env` or shell env
- VOICEVOX Engine running locally at `http://127.0.0.1:50021` (for Japanese TTS)
- A working directory with Remotion installed (or willing to scaffold one)

Run the health check before the first attempt:

```
py scripts\ukiyoe\_healthcheck.py
```

If any check returns `[ng]`, stop and fix it before continuing.

## The pipeline

```
download_source  →  generate_script  →  translate_subtitles  →  synthesize_narration  →  (optional: segment + depth)
```

MVP uses the first four steps. Phase 2 adds SAM2 segmentation and Depth Anything V2 for 2.5D parallax — use it only when the user explicitly asks for parallax.

### Step-by-step

1. **Scaffold files into the user's workspace.** Copy this plugin's `templates/` directory into the user's repo with the following mapping:

   - `templates/scripts/*.py`        → `scripts/ukiyoe/*.py`
   - `templates/src/components/*`    → `src/components/*`
   - `templates/src/compositions/*`  → `src/compositions/*`
   - `templates/src/Root.tsx`        → `src/Root.tsx` (skip if already present)
   - `templates/src/index.ts`        → `src/index.ts` (skip if already present)
   - `templates/package.json`        → `package.json` (skip if already present)
   - `templates/remotion.config.ts`  → `remotion.config.ts` (skip if already present)
   - `templates/tsconfig.json`       → `tsconfig.json` (skip if already present)
   - `templates/.env.example`        → `.env.example` (never overwrite `.env`)
   - `templates/gitignore.example`   → `.gitignore` (skip if already present — note the dot)

   The Python orchestrator resolves `REPO` from its own location, so the scripts must live at `scripts/ukiyoe/` — not elsewhere.

2. **Create a scene JSON.** Write `src/data/ukiyoe_scenes/<slug>.json` following `references/scene-json-schema.md`. Six scenes: title (10s), overview (20s), composition (60s), technique (60s), history (60s), outro (30s). Every scene needs `narration_ja`, `subtitle_ja`, `narration_en`, `subtitle_en`, `camera { zoom, x, y, endZoom, endX, endY }`.

3. **Register the composition in `src/Root.tsx`.** Import the JSON, compute duration via `computeUkiyoeDuration`, add a `<Composition>` with `id="Ukiyoe<CamelCaseName>"`, `width: 1920`, `height: 1080`, `fps: 30`.

4. **Run the orchestrator.**

   ```
   py scripts\ukiyoe\generate.py <slug> --mvp
   ```

   This runs download → script → translate → narration in sequence and aborts on the first failure.

5. **Preview in Remotion Studio.**

   ```
   npx remotion studio
   ```

6. **Render.** For a quick sanity check, render 10 seconds first:

   ```
   npx remotion render Ukiyoe<CamelCaseName> output/<slug>_preview.mp4 --frames=0-299
   ```

   Full render only after the preview looks right — a 4-minute video takes 60–90 minutes on CPU.

## Writing good narration

Narration scripts should be factual, specific, and load-bearing. Every scene must earn its runtime.

- **title**: Artwork name + artist + series. No filler.
- **overview**: One-sentence first impression. Motion vs. stillness. Subject vs. scale.
- **composition**: Rule of thirds, diagonals, gaze guidance, negative space. Name the technique.
- **technique**: Pigments (e.g., Prussian Blue / ベロ藍), carving, printing order, paper.
- **history**: Year, cultural context (e.g., Edo-era pilgrimage culture, Japonisme, Debussy's *La Mer*).
- **outro**: One memorable sentence. Tease the next episode if there is one.

Avoid generic praise ("amazing", "beautiful"). Name what the viewer should notice and why it matters.

## Camera work (Ken Burns)

Each scene's `camera` block drives a slow zoom/pan. Guidelines:

- Start zoom 1.0–1.2, end 1.05–1.6.
- Focal point `(x, y)` is in 0..1 normalized coordinates, where the camera centers on.
- For composition/technique scenes, zoom in on the relevant detail (e.g., Fuji, the foam claws, a signature).
- For title/overview/outro, keep movement minimal.

## Output

Final deliverable: `output/<slug>.mp4`. Summarize what's in it (scene count, total duration, language pair) and point the user at Remotion Studio for iteration.

## Common failure modes

- `ANTHROPIC_API_KEY` missing → `generate_script.py` stops with a clear error. Tell the user to edit `.env`.
- VOICEVOX not running → `synthesize_narration.py` hangs or 404s. Start VOICEVOX Engine first.
- Full render is too slow → always render `--frames=0-299` first, then commit to full.
- Strict TypeScript fails on JSON import → cast via `as unknown as UkiyoeData`.
- Scene totals mismatch durationInFrames → ensure `computeUkiyoeDuration` is used, not a hardcoded number.

## References

- `references/scene-json-schema.md` — exact schema for scene JSON with examples.
- `references/prerequisites.md` — environment setup, VOICEVOX install, `.env` template.
