# programmatic-video-gen

A Claude Code plugin that turns a topic or a single image into a narrated, subtitled explainer video using [Remotion](https://www.remotion.dev/). Built for developers, educators, and content teams who want video output as code — reproducible, diff-able, and scriptable.

## Demo

A recorded end-to-end walkthrough (Hokusai explainer, title scene → render) is planned for v0.2.0 — see [`docs/DEMO_GIF_PLAN.md`](docs/DEMO_GIF_PLAN.md) for the capture script.

## What you get

Two skills ship with the plugin. Both are activated automatically once the plugin is enabled; you invoke them by describing the task in chat.

| Skill            | Produces                                                                                                                                                   |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `remotion-scene` | A generic Remotion composition built around a still image: Ken Burns camera, optional bilingual subtitles, synchronized narration audio, rendered to MP4. |
| `ukiyoe-video`   | A full six-scene art-commentary pipeline for a single ukiyo-e print — title, overview, composition, technique, history, outro — with JP + EN narration from VOICEVOX and bilingual on-screen captions. Output is a 1920x1080 / 30 fps MP4 of roughly four minutes. |

Both skills write scene JSON, scaffold the composition file, register it in `src/Root.tsx`, and hand you the exact `npx remotion render` command to run. No template cloning by hand.

## Quick start

### Install

#### From git (today)

```bash
git clone https://github.com/RintaroMatsumoto/programmatic-video-gen.git
```

Place the clone under your Claude Code plugins directory, or reference it from `~/.claude/plugins.json` / your marketplace config. Skills are auto-loaded once the plugin is enabled.

#### From the Anthropic marketplace (once accepted)

```
/plugin install programmatic-video-gen
```

### Invocation patterns

You do not type a slash command for the skills themselves — describe the task and Claude will pick the right skill.

For a generic scene:

> "Build a 20-second Remotion scene using `assets/mountain.jpg` with narration from `assets/narration.wav` and English subtitles from `assets/subs.json`."

For ukiyo-e commentary (Japanese or English both work):

> "神奈川沖浪裏の解説動画を作って"

> "Make a four-minute explainer video about Hokusai's Great Wave off Kanagawa."

Claude will route to `ukiyoe-video`, write `src/data/ukiyoe_scenes/<slug>.json`, register the composition in `src/Root.tsx`, run `python scripts/ukiyoe/generate.py <slug> --mvp` to handle download + script + translation + narration synthesis, and then propose the final render command.

A fully worked reference scene for *The Great Wave off Kanagawa* ships at `templates/src/data/ukiyoe_scenes/kanagawa_wave.json`.

### First-run checklist (ukiyoe-video)

1. Scaffold the templates into your project, then run the bundled health check from the scaffolded location:

   ```bash
   py scripts\ukiyoe\_healthcheck.py
   ```

   Any `[ng]` output must be fixed before the pipeline will succeed.

2. Start VOICEVOX Engine at `http://127.0.0.1:50021` (free, local Japanese TTS).

3. Set `ANTHROPIC_API_KEY` in `.env` — used for script generation and EN translation.

4. Preview before you commit to a full render. A 10-second sanity slice:

   ```
   npx remotion render UkiyoeKanagawaWave output/kanagawa_preview.mp4 --frames=0-299
   ```

   A full 4-minute render takes 60 to 90 minutes on CPU.

## Requirements

| Tool              | Why                                                       |
| ----------------- | --------------------------------------------------------- |
| Node.js 18+       | Remotion runtime                                          |
| Python 3.11+      | Orchestrator scripts (`generate.py`, `_healthcheck.py`, ...) |
| VOICEVOX Engine   | Free Japanese TTS, runs locally at `127.0.0.1:50021`      |
| FFmpeg on PATH    | MP4 muxing and post-processing                            |
| Anthropic API key | Script generation and EN translation                      |

See `skills/ukiyoe-video/references/prerequisites.md` for version pins and platform notes.

## Why this exists

Most AI video tools ship a black-box renderer and a web UI. This plugin takes the opposite bet: the video is a Remotion project you own — every scene, camera move, and caption lives in code, diff-able and editable. The ukiyo-e pipeline is the flagship use case because it stresses everything that makes code-generated video useful: long-form structure, bilingual subtitles, slow Ken Burns reveals on high-resolution stills, and reproducibility across episodes in a series. The generic `remotion-scene` skill is the same machinery stripped to one scene.

## Design notes

- **MVP first.** The plugin currently ships the reliable Ken-Burns-plus-narration route. SAM2 segmentation and Depth Anything V2 parallax are intentionally not bundled — they are a Phase 2 add-on for when a user explicitly asks for 2.5D.
- **Health check first.** Always run `_healthcheck.py` before the first pipeline attempt. Missing FFmpeg or a stopped VOICEVOX engine are the two most common failures, and the check catches both.
- **Render small, then render full.** Every skill nudges you to render a 10-second preview before committing CPU hours.
- **Subtitle restraint.** Bilingual captions cap at 30 JP / 60 latin characters per line, sit on a 55 to 72 percent-alpha background, and fade out 10 frames before the scene ends. Guidelines live in `skills/remotion-scene/SKILL.md`.

## Project layout

```
.claude-plugin/plugin.json       Plugin manifest
skills/
  remotion-scene/SKILL.md        Generic scene builder
  ukiyoe-video/SKILL.md          Six-scene ukiyo-e pipeline
  ukiyoe-video/references/       Scene JSON schema, prerequisites
templates/
  scripts/                       Python orchestrator + TTS + translate
  src/Root.tsx                   Remotion root with Composition registration
  src/index.ts                   Entry point (registerRoot)
  src/components/                KenBurns, BilingualSubtitle, ParallaxScene
  src/compositions/              UkiyoeAnimation.tsx
  src/data/ukiyoe_scenes/        Reference scene JSON (kanagawa_wave)
  package.json                   Node deps (Remotion 4.x, React 18)
  remotion.config.ts             Remotion CLI config
  tsconfig.json                  Strict TS + resolveJsonModule
  .env.example                   Copy to .env and fill ANTHROPIC_API_KEY
  gitignore.example              Rename to .gitignore in scaffolded project
docs/                            Demo GIF and supporting docs
TOOLBOX.md                       Implementation notes (Remotion / VOICEVOX / FFmpeg)
```

## Acknowledgments

- [Remotion](https://www.remotion.dev/) — the React-based programmatic video framework that makes the whole pipeline possible.
- [VOICEVOX](https://voicevox.hiroshiba.jp/) — free, locally-run Japanese TTS.
- Katsushika Hokusai (1760 - 1849) — the sample scene uses public-domain reproductions of *The Great Wave off Kanagawa* from the [Metropolitan Museum of Art](https://www.metmuseum.org/) and [Wikimedia Commons](https://commons.wikimedia.org/).

## License

MIT. See [LICENSE](LICENSE).

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for scope, coding conventions, and how to propose a new skill.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history. Current version: 0.1.1.

## Author

Rintaro Matsumoto (松本倫太郎) — [github.com/RintaroMatsumoto](https://github.com/RintaroMatsumoto)
