# programmatic-video-gen

A Claude Code plugin for generating narrated explainer videos programmatically
with [Remotion](https://www.remotion.dev/). It ships two skills: a general
Remotion scene scaffolder, and a specialized ukiyo-e (Japanese woodblock print)
art-commentary pipeline that produces a four-minute bilingual (JP/EN) MP4 from a
single source image. The plugin exists so that, given a topic and an image,
Claude can write the scene JSON, register the Remotion composition, synthesize
narration through VOICEVOX, and hand you a ready-to-render project.

## Installation

### Manual (from git, today)

```bash
git clone https://github.com/RintaroMatsumoto/programmatic-video-gen.git
```

Then place it under your Claude Code plugins directory, or reference it from
`~/.claude/plugins.json` / your marketplace config.

### From the Anthropic marketplace (future)

Once the plugin is accepted into `anthropics/claude-plugins-official`:

```
/plugin install programmatic-video-gen
```

Skills are auto-loaded once the plugin is enabled; simply describing the task in
chat (e.g. "make a video about Hokusai's Great Wave") will trigger the correct
skill.

## Skills

| Skill            | One-line description                                                                                           |
| ---------------- | -------------------------------------------------------------------------------------------------------------- |
| `remotion-scene` | Scaffold a generic Remotion scene — Ken Burns camera over a still image, synchronized narration, subtitles.   |
| `ukiyoe-video`   | Six-section art-commentary pipeline for a single ukiyo-e print: title → overview → composition → technique → history → outro, with JP + EN narration and bilingual subtitles. |

## Quick start

### `remotion-scene`

In a Remotion project, ask Claude:

> "Build a 20-second Remotion scene using `assets/mountain.jpg` with narration
> from `assets/narration.wav` and English subtitles from `assets/subs.json`."

The skill will copy `KenBurns` and `BilingualSubtitle` from
`templates/src/components/`, create a new composition under
`src/compositions/`, register it in `src/Root.tsx`, and suggest the
`npx remotion render` command.

### `ukiyoe-video`

1. In a Remotion-ready project, run the health check:

   ```bash
   py templates/scripts/_healthcheck.py
   ```

2. Start VOICEVOX Engine at `http://127.0.0.1:50021` and set
   `ANTHROPIC_API_KEY` in `.env`.

3. Ask Claude:

   > "神奈川沖浪裏の解説動画を作って"

   The skill writes `src/data/ukiyoe_scenes/<slug>.json`, registers the
   composition in `src/Root.tsx`, runs
   `python scripts/ukiyoe/generate.py <slug> --mvp`, and then proposes the
   final `npx remotion render` command.

A ready-made scene JSON for *The Great Wave off Kanagawa* ships at
`templates/src/data/ukiyoe_scenes/kanagawa_wave.json` as a reference.

## Requirements

| Tool              | Why                                                         |
| ----------------- | ----------------------------------------------------------- |
| Node.js 18+       | Remotion runtime                                            |
| Python 3.10+      | Orchestrator scripts (`generate.py`, `_healthcheck.py`, …) |
| VOICEVOX Engine   | Free Japanese TTS (runs locally at `127.0.0.1:50021`)       |
| FFmpeg            | MP4 muxing and post-processing                              |
| Anthropic API key | Script generation and EN translation                        |

See `skills/ukiyoe-video/references/prerequisites.md` for version-pinning and
platform notes.

## Philosophy

- **MVP only, for now**: SAM2 + Depth + FLUX 2.5D parallax is intentionally
  not bundled. Ship the reliable Ken-Burns-plus-narration route first.
- **Health check first**: always run `_healthcheck.py` before the first
  pipeline attempt. Any `[ng]` output must be fixed before rendering.
- **Render small**: the full 4-minute render takes 60 – 90 minutes. Preview
  with `--frames=0-299` (10 s) first.

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgments

- [Remotion](https://www.remotion.dev/) — the React-based programmatic video
  framework that makes the whole pipeline possible.
- [VOICEVOX](https://voicevox.hiroshiba.jp/) — free, locally-run Japanese TTS.
- Katsushika Hokusai (1760 – 1849) — the ukiyo-e reference images used by the
  sample scene (*The Great Wave off Kanagawa*) are in the public domain and
  sourced from the [Metropolitan Museum of Art](https://www.metmuseum.org/) and
  [Wikimedia Commons](https://commons.wikimedia.org/).

## Author

Rintaro Matsumoto (松本倫太郎) —
[github.com/RintaroMatsumoto](https://github.com/RintaroMatsumoto)
