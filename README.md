# images-to-pdf

Convert multiple image files into a single PDF with deterministic ordering, EXIF orientation correction, alpha flattening, and page layout controls.

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

## Tests

```bash
.venv/bin/python -m pytest -q
```

## Repo layout

```text
images-to-pdf/
├── SKILL.md
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

## License

MIT
