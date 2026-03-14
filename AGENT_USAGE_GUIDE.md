# Agent Usage Guide

Use this guide when another OpenClaw agent needs to apply the `images-to-pdf` skill reliably.

## What this skill does

Convert multiple image files into a single PDF.

It is best for:
- scanned document photos
- homework pages captured as images
- screenshots that need to be bundled into one PDF
- receipt or note images that should become a printable/shareable document

## When to use it

Use this skill when the user asks for any of the following:
- merge several image files into one PDF
- convert multiple JPG/PNG/WebP files into a PDF
- bundle scanned images into a document
- turn phone photos of pages into a PDF

Do **not** use it when:
- the input is already a PDF
- the user wants OCR/text extraction rather than PDF bundling
- the user wants heavy PDF editing after creation
- the user gives a directory path and expects recursive discovery (current policy is files only)

## Current behavior summary

- Accept file inputs only
- Support common raster formats: jpg, jpeg, png, webp, bmp, tif, tiff
- Apply EXIF orientation correction
- Flatten alpha channels to white background
- Preserve aspect ratio
- Support page size, orientation, margin, sorting, skip-invalid, JPEG quality, and title/author/subject metadata
- Auto-generate output path from the first input file when `--output` is omitted

## Script entrypoint

```bash
python scripts/images_to_pdf.py <image1> <image2> ... [options]
```

## Core options

- `--output <path>`: explicit output PDF path
- `--sort name|mtime|natural`: sort inputs before rendering
- `--page-size a4|letter|fit-image`: page sizing policy
- `--orientation auto|portrait|landscape`: page orientation policy
- `--margin <points>`: page margin in PDF points
- `--skip-invalid`: skip unreadable images instead of failing fast
- `--jpeg-quality <1-100>`: JPEG quality for embedded images
- `--title <text>`: set PDF title metadata
- `--author <text>`: set PDF author metadata
- `--subject <text>`: set PDF subject metadata

## Recommended operating procedure

1. Confirm the user provided image files, not a folder.
2. Preserve the given order unless the user explicitly asks for sorting.
3. Use `--skip-invalid` when the user is likely mixing screenshots/scans from uncertain sources.
4. Set `--title` when the output is a named deliverable, such as homework or notes.
5. After rendering, verify:
   - output file exists
   - page count matches processed image count
   - CLI summary looks correct

## Safe default command

Use this when the user only wants images merged into a PDF and gave a clean ordered list:

```bash
python scripts/images_to_pdf.py page1.jpg page2.jpg page3.jpg --output merged.pdf
```

## Resilient command

Use this when user input may contain broken or inconsistent files:

```bash
python scripts/images_to_pdf.py page1.jpg broken.jpg page2.jpg \
  --skip-invalid \
  --jpeg-quality 85 \
  --title "Merged Images" \
  --output merged.pdf
```

## Decision rules

### Ordering
- If the user sends files in chat order and does not ask for sorting, preserve that order.
- If filenames imply page sequence but are not pre-sorted, use `--sort natural`.
- If the user says "latest first" or "in the order created", use `--sort mtime`.

### Page size
- Use `a4` for general documents and notes.
- Use `letter` for U.S.-centric printable documents.
- Use `fit-image` when exact original image dimensions matter more than paper layout.

### Orientation
- Use `auto` unless the user explicitly requests portrait or landscape.
- Force `portrait` when all pages should have consistent print layout.
- Force `landscape` for wide screenshots or slides.

### Error handling
- Default behavior is fail-fast.
- Use `--skip-invalid` only when partial completion is preferable to hard failure.
- If every image is invalid, the script should still fail instead of creating an empty PDF.

## Example user requests and mapping

### Example 1
User: "이 이미지 4개 pdf로 묶어줘"

Action:
- Use the 4 files in given order
- Choose explicit output path

```bash
python scripts/images_to_pdf.py a.jpg b.jpg c.jpg d.jpg --output merged.pdf
```

### Example 2
User: "스캔 이미지들인데 한두 장 깨졌을 수도 있어"

Action:
- Use `--skip-invalid`
- Prefer moderate compression

```bash
python scripts/images_to_pdf.py scan1.jpg scan2.jpg scan3.jpg \
  --skip-invalid \
  --jpeg-quality 85 \
  --output scans.pdf
```

### Example 3
User: "숙제 사진들 하나의 PDF로 만들고 제목은 Homework 5로 넣어줘"

Action:
- Set title metadata

```bash
python scripts/images_to_pdf.py hw1.jpg hw2.jpg hw3.jpg \
  --title "Homework 5" \
  --output homework-5.pdf
```

## Validation checklist for agents

Before reporting success, confirm all of the following:
- the command exited successfully
- the output PDF exists
- processed count is correct
- skipped count is expected
- if practical, PDF page count matches processed count

## Known limitations

- No directory input mode
- No recursive discovery
- No OCR/text extraction
- No advanced PDF editing after generation
- No background color customization yet beyond white alpha flattening
- No author/subject metadata yet

## Suggested handoff wording

When reporting back to the user, prefer concise completion text such as:
- "PDF로 묶었다. 총 5장 처리했고 1장은 손상돼서 스킵했다."
- "변환 끝. 출력 파일은 `merged.pdf`다."

## Future expansion areas

Likely next features:
- `--author`
- `--subject`
- custom background color
- max-dimension downscaling
- captions or footers
