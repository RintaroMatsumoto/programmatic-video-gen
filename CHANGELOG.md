# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-04-19

### Added

- Scaffold templates for a freshly initialized project: `templates/src/Root.tsx`,
  `templates/src/index.ts`, `templates/package.json`, `templates/remotion.config.ts`,
  `templates/tsconfig.json`, `templates/.env.example`, `templates/gitignore.example`.
- Ukiyoe skill now documents the exact `templates/ → project` file mapping.

### Changed

- `TOOLBOX.md` rewritten from the ground up; the previous content was from an
  unrelated VRM project. Now covers Remotion, VOICEVOX, FFmpeg, Claude API, and
  the Python `REPO` resolution convention used by all orchestrator scripts.
- Default Claude model for `generate_script.py` / `translate_subtitles.py`
  changed from the non-existent `claude-opus-4-7` to `claude-sonnet-4-6`.
  Override via `CLAUDE_MODEL` env var.
- README health-check command corrected: run `py scripts\ukiyoe\_healthcheck.py`
  after scaffolding (not `py templates/scripts/_healthcheck.py`).
- `generate.py` docstring now correctly describes MVP as a 4-step pipeline
  (download → script → translate → narration); previously claimed 3 steps.

### Fixed

- Prerequisites now list the plugin's actual default VOICEVOX speaker (16 —
  九州そら ノーマル) alongside the other commonly used IDs, and include
  `src/index.ts`, `tsconfig.json`, `remotion.config.ts` in the expected
  directory tree.

## [0.1.0] - 2026-04-18

### Added

- Initial public release. Two skills: `remotion-scene` (general Remotion scene
  scaffolding) and `ukiyoe-video` (6-section ukiyo-e art-commentary video
  pipeline). Templates for scripts and React components included.

[0.1.1]: https://github.com/RintaroMatsumoto/programmatic-video-gen/releases/tag/v0.1.1
[0.1.0]: https://github.com/RintaroMatsumoto/programmatic-video-gen/releases/tag/v0.1.0
