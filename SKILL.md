---
name: images-to-pdf
description: Convert multiple image files into a single PDF with deterministic ordering, EXIF orientation correction, alpha flattening, and page layout controls. Use when the user asks to merge several image files into one PDF, convert scanned images into a PDF, or bundle screenshots/photos into a printable document.
---

# Images to PDF

Create a single PDF from multiple image files.

## Workflow

1. Validate that all inputs are files and supported image formats.
2. Sort inputs if the user requests a sort mode; otherwise preserve the given order.
3. Normalize each image:
   - Apply EXIF orientation.
   - Convert alpha images to RGB on a white background.
   - Keep aspect ratio.
4. Render one PDF page per image.
5. Verify that the output PDF exists and has the expected page count when practical.

## Default behavior

- Accept file inputs only.
- Use A4 page size by default.
- Use automatic orientation by default.
- Preserve aspect ratio.
- Derive the output path from the first input file when `--output` is omitted.
- Fail fast on invalid or unreadable images unless `--skip-invalid` is set.

## Script

Use `scripts/images_to_pdf.py`.

### Example

```bash
python scripts/images_to_pdf.py page1.jpg page2.png page3.webp --output result.pdf
```

### Useful options

- `--output <path>`: Set output PDF path. If omitted, derive `<first-input>.pdf`.
- `--sort name|mtime|natural`: Sort files before rendering.
- `--page-size a4|letter|fit-image`: Choose page sizing.
- `--orientation auto|portrait|landscape`: Control page orientation.
- `--margin <points>`: Set page margin in PDF points.
- `--skip-invalid`: Skip unreadable image files and continue.
- `--jpeg-quality <1-100>`: Control embedded image JPEG quality.
- `--title <text>`: Set PDF title metadata.
- `--author <text>`: Set PDF author metadata.
- `--subject <text>`: Set PDF subject metadata.

## Validation checklist

- Confirm the output PDF was created.
- Confirm the PDF page count matches the number of processed input images.
- Review the printed summary for processed and skipped counts.
- If conversion fails, check for unsupported formats, corrupted files, or unwritable output paths.
