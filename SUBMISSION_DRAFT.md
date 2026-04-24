> これは Anthropic の Claude Plugins 公式ディレクトリ提出フォームに手動で貼り付けるためのドラフトである。各フィールドはフォーム項目に 1:1 対応している。
>
> 提出順の推奨: **3 番目**（demo の実地キャプチャ（Hokusai walkthrough）を撮影し README の demo 参照を差し替えてから提出）

---

## programmatic-video-gen

- **Plugin name** (kebab-case): programmatic-video-gen
- **Public repository URL**: https://github.com/RintaroMatsumoto/programmatic-video-gen
- **Latest tag**: v0.1.1
- **Author**: Rintaro Matsumoto
- **License**: MIT
- **Homepage**: https://github.com/RintaroMatsumoto/programmatic-video-gen
- **Category (candidate)**: creative — the output is narrated, subtitled MP4 video for educators and content teams, which is squarely creative tooling rather than developer-infrastructure.
- **Keywords (5-8)**: remotion, video, explainer, narration, subtitles, voicevox, ken-burns, ukiyoe

### Short tagline (<=60 chars, English)
Turn a topic or image into a narrated, subtitled Remotion MP4.

### Description (plain English, ~450 chars)
A Claude Code plugin that turns a topic or a single image into a narrated, subtitled explainer video using Remotion. Two skills ship: `remotion-scene` scaffolds a generic composition around a still image with Ken Burns camera, synchronized narration, and optional bilingual subtitles; `ukiyoe-video` runs a six-scene art-commentary pipeline (title, overview, composition, technique, history, outro) for a single ukiyo-e print with Japanese and English VOICEVOX narration and bilingual captions, rendered at 1920x1080 / 30 fps. Both skills write scene JSON, scaffold the composition, register it in `src/Root.tsx`, and hand back the exact `npx remotion render` command.

### Differentiators (3, English)
- Video as code: scenes are diff-able JSON plus React/Remotion components, so output is reproducible and reviewable in PR.
- Narration and subtitles are first-class: skills emit time-aligned audio cues and bilingual captions instead of muted slideshows.
- Ships a complete domain pipeline (`ukiyoe-video`) alongside the generic template, so reviewers can see an end-to-end 4-minute render, not just a toy scene.

### Included skills (from plugin.json / skills/)
- remotion-scene - Generic Remotion composition from a still image with Ken Burns, subtitles, narration, MP4.
- ukiyoe-video - Six-scene ukiyo-e commentary pipeline with JP+EN VOICEVOX narration and bilingual captions.

### Reviewer trial path (<=5 lines)
1. `/plugin install programmatic-video-gen` and run `npm install` in the host Remotion project.
2. Place a source image and ensure VOICEVOX is running locally for the ukiyo-e path.
3. Say "make a Remotion scene from this image with bilingual subtitles".
4. Or say "make a commentary video about The Great Wave off Kanagawa".
5. Run the printed `npx remotion render` command to produce the MP4.

### Notes / Caveats
- Requires Node.js 18+ and a Remotion host project; the plugin scaffolds into that project.
- `ukiyoe-video` requires VOICEVOX running locally for Japanese TTS.
