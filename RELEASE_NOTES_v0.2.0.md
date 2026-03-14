# images-to-pdf v0.2.0

## Highlights

This release improves the OpenClaw `images-to-pdf` skill for real-world agent use.

### Added
- `--skip-invalid` to continue processing when some images are broken or unreadable
- automatic output path generation when `--output` is omitted
- CLI summary logging for output path, processed count, and skipped count
- `--jpeg-quality` to control embedded image quality
- `--title` to set PDF title metadata

### Existing core capabilities
- deterministic file ordering with `name`, `mtime`, and `natural` sort modes
- EXIF orientation correction
- alpha flattening onto a white background
- page sizing, orientation, and margin controls
- file-only input policy for predictable agent behavior

### Validation
- 16 automated tests passing
- skill validation and packaging completed successfully

## Recommended use cases
- merge multiple scanned photos into one PDF
- combine homework page images into a submission document
- bundle screenshots into a printable PDF

## Known limitations
- no directory input mode
- no OCR/text extraction
- no author/subject metadata yet
- no custom background color yet
