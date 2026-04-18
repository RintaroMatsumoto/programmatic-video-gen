---
name: remotion-scene
description: Use when the user wants to build a Remotion scene or short video from scratch — Ken Burns camera over a still image, bilingual or single-language subtitles, synchronized narration audio. Covers scaffolding a new composition, hooking up audio, registering it in Root.tsx, and rendering to MP4. Triggers include "Remotion scene", "video from an image", "explainer slide", "Ken Burns", "字幕付き動画", or general programmatic-video requests that are not ukiyo-e specific.
---

# Remotion Scene Builder

Scaffold a Remotion composition that plays narration audio, runs a Ken Burns zoom/pan over a still image, and displays subtitles. For ukiyo-e art commentary specifically, prefer the `ukiyoe-video` skill.

## When to use

Use this skill when the user asks for:

- A single-scene or multi-scene narrated video built on a still image.
- A Ken Burns effect over a photograph or illustration.
- A subtitle-driven explainer that the `ukiyoe-video` skill is too specific for.
- A template for their own programmatic-video pipeline.

## Prerequisites

Same as `ukiyoe-video`:

- Node.js 18+, Python 3.11+
- Remotion installed (`npm install remotion @remotion/cli @remotion/bundler react react-dom`)
- FFmpeg on PATH
- For narration: either a TTS service (VOICEVOX for JP, OpenAI/ElevenLabs/Edge for others) or pre-rendered WAV/MP3

## Building blocks (copy from `templates/src/components/`)

| File                        | Purpose                                                                 |
| --------------------------- | ----------------------------------------------------------------------- |
| `KenBurns.tsx`              | Zoom + pan + optional tilt driven by cubic-ease-out over scene length.  |
| `BilingualSubtitle.tsx`     | Two-tier caption (primary + secondary language).                        |
| `ParallaxScene.tsx`         | Optional 2.5D parallax when you have segmented depth layers.            |

All three are framework-agnostic inside the project — they take props, not global state.

## Step-by-step

1. **Copy components into the user's repo.** If `src/components/KenBurns.tsx` and `BilingualSubtitle.tsx` don't exist, copy them from this plugin's `templates/src/components/`.

2. **Create a composition file** at `src/compositions/<Name>.tsx`. Pattern:

   ```tsx
   import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
   import { KenBurns } from "../components/KenBurns";
   import { BilingualSubtitle } from "../components/BilingualSubtitle";

   export const MyScene: React.FC<{ src: string; narrationUrl?: string }> = ({ src, narrationUrl }) => (
     <AbsoluteFill style={{ backgroundColor: "#000" }}>
       <KenBurns src={src} fromZoom={1.0} toZoom={1.15} fromXY={[0.5, 0.5]} toXY={[0.5, 0.5]} />
       {narrationUrl && <Audio src={narrationUrl} />}
       <BilingualSubtitle primary="..." secondary="..." />
     </AbsoluteFill>
   );
   ```

3. **Register in `src/Root.tsx`:**

   ```tsx
   <Composition
     id="MyScene"
     component={MyScene}
     durationInFrames={300}
     fps={30}
     width={1920}
     height={1080}
     defaultProps={{ src: staticFile("images/photo.jpg") }}
   />
   ```

4. **Preview:** `npx remotion studio` and open `http://localhost:3000`.

5. **Render a short slice first** — 10 seconds to confirm camera and subtitle timing:

   ```
   npx remotion render MyScene output/myscene_preview.mp4 --frames=0-299
   ```

6. **Render full:**

   ```
   npx remotion render MyScene output/myscene.mp4
   ```

## Camera guidelines

Ken Burns is about restraint. Motion should reveal, not distract.

- Zoom range: 1.0 to 1.15 for wide establishment, 1.2–1.6 for detail focus.
- Pan speed: cross at most 30% of the frame per 10 seconds.
- Hold tilt near 0°. Use rotation only for dream/memory beats.
- Always ease in and out. Linear Ken Burns reads as mechanical.

## Subtitle guidelines

- Primary language: under 30 JP chars or 60 EN/latin chars per line.
- Secondary language: same cap, one size smaller.
- Keep on-screen for the full narration of that scene, fade out 10 frames before the scene ends.
- Semi-transparent background (55–72% alpha black) — never solid.

## Audio

If the user has pre-recorded narration, drop the files into `public/<project>/audio/` and reference via `staticFile("<project>/audio/scene_01.wav")`.

If they need generation:

- **Japanese**: point them at VOICEVOX Engine (free, local). See `templates/scripts/synthesize_narration.py` in this plugin.
- **English**: OpenAI TTS, ElevenLabs, or Edge TTS (free).

## Common pitfalls

- JSON import strict TS error → cast `json as unknown as MyDataType`.
- `durationInFrames` mismatch with audio length → always compute from data, never hardcode.
- Render taking forever → always preview with `--frames=0-299` first.
- Black frames at scene boundaries → add 10–15 frame padding at the end of each `Sequence`.
- Subtitle pops in/out abruptly → spring-in on first frame, linear fade-out 10 frames before scene end.
