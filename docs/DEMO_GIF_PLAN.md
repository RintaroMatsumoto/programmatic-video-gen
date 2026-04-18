# Demo GIF production plan

This document specifies what `docs/demo.gif` should show and how to produce it. The file is referenced from `README.md` as the hero demo and is what most visitors to the repo will see first.

## Output specification

| Property       | Target                                                              |
| -------------- | ------------------------------------------------------------------- |
| Dimensions     | 1280x720 preferred. 960x540 is acceptable if file size is tight.    |
| Frame rate     | 15 fps (12 fps acceptable for size). 24 fps is overkill for a demo. |
| Duration       | 15 to 20 seconds.                                                   |
| File size      | Under 5 MB. GitHub will inline-render it in the README reliably below that; above 10 MB it stalls on slow connections. |
| Colors         | 256-color palette (GIF native). Use ffmpeg palette-gen for cleaner output. |
| Final path     | `docs/demo.gif` (exactly — the README already points here).         |

## Storyboard (15 to 20 seconds)

| Time      | What the viewer sees                                                                                                      |
| --------- | ------------------------------------------------------------------------------------------------------------------------- |
| 0 - 3s    | Claude Code chat window. User types `神奈川沖浪裏の解説動画を作って` (or the EN equivalent). Show the prompt being submitted. |
| 3 - 7s    | Fast-forward (2x - 4x speed) through Claude's skill activation: scene JSON being written, composition registered in `Root.tsx`, orchestrator log lines streaming past (download, script, translate, narration). |
| 7 - 11s   | Remotion Studio preview window opens, showing the Ken Burns camera moving over the Great Wave print with bilingual subtitles overlaid. |
| 11 - 18s  | Cut to the rendered MP4 playing at normal speed — pick the most visually striking 6 seconds (recommended: the zoom-in on the foam claws during the "composition" scene, with both JP and EN captions visible). |
| 18 - 20s  | Hold on the final frame with the artwork title card, then loop.                                                           |

Keep cursor movement and window-switching minimal. If the recording contains any personal paths, edit the frames out or re-record in a clean workspace.

## Recording tools (Windows)

Both produce GIFs directly — no intermediate video conversion needed. Use whichever you already have.

### ScreenToGif (recommended)

1. Download from https://www.screentogif.com/ and launch the Recorder.
2. Frame the 1280x720 window over the Claude Code UI, set fps to 15, hit Record, run the demo, hit Stop. Use the built-in editor to trim to 15-20 seconds and export as GIF (Encoder: ScreenToGif 2.0, Color quantization: High).

### ShareX

1. Install from https://getsharex.com/. Under `Task settings -> Screen recorder -> Screen recording options`, set output format to GIF, fps to 15, codec libx264 (for the MP4 step), then use `Main window -> Capture -> Screen recording (GIF)`.
2. Select the capture region, run the demo, stop with the ShareX tray icon. ShareX will save the GIF; trim and recompress with the post-processing command below if needed.

## Post-processing (if the GIF exceeds 5 MB)

Re-encode with a generated palette — this typically cuts size by 40 to 70 percent with no visible quality loss. Run from the repo root:

```bash
ffmpeg -y -i docs/demo_raw.gif -vf "fps=15,scale=1280:-1:flags=lanczos,palettegen=max_colors=128" docs/palette.png

ffmpeg -y -i docs/demo_raw.gif -i docs/palette.png -lavfi "fps=15,scale=1280:-1:flags=lanczos [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=5" docs/demo.gif

del docs\demo_raw.gif docs\palette.png
```

If it is still too large, drop `scale=1280:-1` to `scale=960:-1`, lower fps to 12, and/or reduce `max_colors` to 96.

Verify final size:

```bash
dir docs\demo.gif
```

## Placement

Save the finished file as `docs/demo.gif`. The README already contains:

```markdown
![Demo: generating a Hokusai explainer video end-to-end](docs/demo.gif)
```

No README edit is needed once the file is in place — just commit `docs/demo.gif` alongside this plan.
