# images-to-pdf

[![Tests](https://github.com/bradhjjo/openclaw-images-to-pdf/actions/workflows/python-tests.yml/badge.svg)](https://github.com/bradhjjo/openclaw-images-to-pdf/actions/workflows/python-tests.yml)
[![Release](https://img.shields.io/github/v/release/bradhjjo/openclaw-images-to-pdf)](https://github.com/bradhjjo/openclaw-images-to-pdf/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

OpenClaw skill for converting multiple image files into a single PDF with deterministic ordering, EXIF orientation correction, alpha flattening, and page layout controls.

## Why this exists

This skill is designed for agents and operators who need a predictable way to turn multiple page images into one PDF without re-implementing the workflow each time.

Use it for:
- scanned document photos
- homework pages captured as images
- screenshots that should become one PDF
- note or receipt images that need bundling into a shareable document

## Features

- Merge multiple image files into one PDF
- Preserve input order or sort by `name`, `mtime`, or `natural`
- Apply EXIF orientation correction
- Flatten alpha channels onto a white background
- Control page size, orientation, and margin
- Skip invalid images with `--skip-invalid`
- Control embedded JPEG quality with `--jpeg-quality`
- Set PDF title metadata with `--title`
- Auto-generate output path when `--output` is omitted

## Requirements

- Python 3.10+
- Dependencies from `requirements-dev.txt`

## Install dependencies

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

## Usage

### Basic

```bash
python scripts/images_to_pdf.py img1.jpg img2.jpg img3.png --output merged.pdf
```

### Auto-generate output name

```bash
python scripts/images_to_pdf.py receipt1.jpg receipt2.jpg
```

### Skip invalid images

```bash
python scripts/images_to_pdf.py good1.jpg broken.jpg good2.jpg --skip-invalid --output merged.pdf
```

### Set title metadata

```bash
python scripts/images_to_pdf.py a.jpg b.jpg --title "Homework 5" --output hw5.pdf
```

### Full example

```bash
python scripts/images_to_pdf.py \
  page10.jpg page2.jpg broken.jpg page1.jpg \
  --sort natural \
  --skip-invalid \
  --jpeg-quality 85 \
  --title "Scanned Notes" \
  --output notes.pdf
```

## Options

- `--output <path>`: explicit output PDF path
- `--sort name|mtime|natural`: sort inputs before rendering
- `--page-size a4|letter|fit-image`: page sizing policy
- `--orientation auto|portrait|landscape`: page orientation policy
- `--margin <points>`: page margin in PDF points
- `--skip-invalid`: skip unreadable images instead of failing fast
- `--jpeg-quality <1-100>`: JPEG quality for embedded images
- `--title <text>`: set PDF title metadata

## Tests

```bash
.venv/bin/python -m pytest -q
```

## For other agents

If you want another OpenClaw agent to use this skill reliably, see:

- `SKILL.md` for the installed skill instructions
- `AGENT_USAGE_GUIDE.md` for higher-level operating guidance

## Repo layout

```text
images-to-pdf/
├── SKILL.md
├── AGENT_USAGE_GUIDE.md
├── scripts/
│   └── images_to_pdf.py
├── tests/
│   └── test_images_to_pdf.py
└── requirements-dev.txt
```

## Packaging

Use the OpenClaw skill packager:

```bash
python /path/to/package_skill.py /path/to/images-to-pdf ./dist
```

## ClawHub / registry preparation

This repository is ready for GitHub distribution and OpenClaw skill packaging.

Before publishing to a registry such as ClawHub, verify:
- `SKILL.md` remains the canonical skill entrypoint
- the packaged `.skill` artifact is regenerated from the latest commit
- release notes match the packaged version

## License

MIT
