# Contributing

Thanks for your interest in `programmatic-video-gen`. This is a small,
opinionated Claude Code plugin, so the contribution flow is deliberately light.

## Opening issues

- Use GitHub Issues for bugs, crashes, broken renders, or concrete feature
  requests.
- Include your OS, Node version, Python version, VOICEVOX version, and the
  output of `py templates/scripts/_healthcheck.py` when relevant.
- For ideas or open-ended discussion, prefer a GitHub Discussion (or an issue
  clearly tagged `discussion`).

## Pull requests

1. Fork the repo.
2. Create a topic branch off `main` (e.g. `feat/scene-json-validator`).
3. Keep PRs focused — one logical change per PR.
4. For user-visible changes, update `README.md` and add an entry to
   `CHANGELOG.md` under an `[Unreleased]` heading.
5. Open the PR against `main` with a short description of the change and any
   manual test you ran (preview render, health-check output, etc.).

## Style notes

- **Commit messages** follow Conventional Commits: `feat:`, `fix:`, `docs:`,
  `chore:`, `refactor:`, `test:`.
- **TypeScript / React** — match the existing style in `templates/src/`.
  Prefer functional components and Remotion's `useCurrentFrame` /
  `interpolate` idioms over imperative animation.
- **Python** — target 3.10+; type-hint public functions; keep scripts runnable
  with `python scripts/foo.py` (no heavy frameworks).
- **Skills (`SKILL.md`)** — keep the YAML frontmatter `description` under ~300
  characters and written so Claude can reliably decide when to invoke the
  skill.
- Do not commit rendered MP4s, VOICEVOX outputs, `node_modules/`, or anything
  in `out/` / `dist/`.

## Plugin submission note

This repository targets the Anthropic official plugin marketplace
(`anthropics/claude-plugins-official`). The maintainer handles submission
manually — please do not open submission PRs against the marketplace repo on
behalf of this plugin.
