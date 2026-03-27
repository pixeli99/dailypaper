# Daily Paper Reader

A lightweight reader for Hugging Face Daily Papers, designed around short daily digests plus per-paper notes.

## What is in this repo

- `knowledge/`
  - Daily digest markdown files.
  - Per-paper reading notes.
- `scripts/daily_papers_digest.py`
  - Fetches Hugging Face Daily Papers, prepares arXiv source, and writes markdown notes.
- `scripts/build_github_pages.py`
  - Builds the static reader site into `docs/`.
- `docs/`
  - GitHub Pages output.

## Update workflow

Run the digest builder for a day and rebuild the site:

```bash
python3 scripts/daily_papers_digest.py --date 2026-03-27 --build-site
```

Or rebuild the site only:

```bash
python3 scripts/build_github_pages.py
```

## Publishing

This repository is set up for GitHub Pages deployment from GitHub Actions.
