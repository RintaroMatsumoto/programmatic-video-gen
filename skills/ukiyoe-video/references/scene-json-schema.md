# Scene JSON schema

The data contract between narration and Remotion. One JSON file per ukiyo-e work, saved as `src/data/ukiyoe_scenes/<slug>.json`.

## Top-level shape

```json
{
  "meta": {
    "title_ja": "神奈川沖浪裏",
    "title_en": "The Great Wave off Kanagawa",
    "artist": "葛飾北斎",
    "year": 1831
  },
  "scenes": [ /* six Scene objects, see below */ ]
}
```

## Scene object

```json
{
  "id": 3,
  "section": "composition",
  "duration": 60,
  "narration_ja": "...",
  "subtitle_ja": "...",
  "narration_en": "...",
  "subtitle_en": "...",
  "camera": {
    "zoom": 1.15,
    "x": 0.3,
    "y": 0.35,
    "endZoom": 1.25,
    "endX": 0.7,
    "endY": 0.65,
    "tilt": 0
  },
  "overlays": [],
  "audio_path": "public/ukiyoe/kanagawa_wave/audio/scene_03.wav"
}
```

### Fields

| Field          | Type    | Notes                                                                                               |
| -------------- | ------- | --------------------------------------------------------------------------------------------------- |
| `id`           | int     | 1-indexed, matches order.                                                                           |
| `section`      | string  | One of `title`, `overview`, `composition`, `technique`, `history`, `outro`.                         |
| `duration`     | number  | Seconds. Scene renders for `Math.round(duration * fps) + 15` frames (15-frame padding).             |
| `narration_*`  | string  | Full narration text. Passed to TTS. Keep under ~180 JP chars / ~220 EN chars for natural pacing.    |
| `subtitle_*`   | string  | Short on-screen caption. Under 30 JP chars / 60 EN chars.                                           |
| `camera.zoom`  | number  | Starting zoom. 1.0 = no zoom.                                                                       |
| `camera.x,y`   | number  | Starting focal point in 0..1 normalized image coords.                                               |
| `camera.end*`  | number  | Optional ending values for pan/zoom. Omit for a static shot.                                        |
| `camera.tilt`  | number  | Optional degrees of rotation over the scene. Default 0.                                             |
| `overlays`     | array   | Reserved for future highlight shapes. Leave `[]` for now.                                           |
| `audio_path`   | string  | Set by `synthesize_narration.py` after TTS. Relative to repo root.                                  |

## Section cadence

| Section       | Duration | Purpose                                                        |
| ------------- | -------- | -------------------------------------------------------------- |
| `title`       | 10 s     | Artwork name + artist. Minimal camera movement.                |
| `overview`    | 20 s     | First impression, dominant subject, scale.                     |
| `composition` | 60 s     | Visual structure — rule of thirds, diagonals, gaze guidance.   |
| `technique`   | 60 s     | Pigments, printing technique, line work.                       |
| `history`     | 60 s     | Year, cultural context, later influence.                       |
| `outro`       | 30 s     | Closing line + teaser for next episode.                        |

Total: 240 seconds (4 minutes).

## Example: full Kanagawa wave scene 3

```json
{
  "id": 3,
  "section": "composition",
  "duration": 60,
  "narration_ja": "画面を三分割すると、大波が左上、富士が右下に配置されています。波の爪のような飛沫が、観る者の視線を富士へと導きます。対角線を使った見事な導線です。",
  "subtitle_ja": "三分割構図 ― 波の爪が富士へ導く",
  "narration_en": "Using the rule of thirds, the wave dominates the upper-left, while Fuji anchors the lower-right. The foam claws guide the eye diagonally toward the mountain.",
  "subtitle_en": "The rule of thirds, guided by the wave's claws",
  "camera": {
    "zoom": 1.15, "x": 0.3, "y": 0.35,
    "endZoom": 1.25, "endX": 0.7, "endY": 0.65
  },
  "overlays": []
}
```
