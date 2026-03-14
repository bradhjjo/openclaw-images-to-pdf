#!/usr/bin/env python3
"""Convert multiple image files into a single PDF."""

from __future__ import annotations

import argparse
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
PAGE_SIZES = {
    "a4": A4,
    "letter": LETTER,
}


@dataclass(frozen=True)
class Layout:
    page_width: float
    page_height: float
    draw_width: float
    draw_height: float
    x: float
    y: float


@dataclass(frozen=True)
class RenderSummary:
    output_path: Path
    processed_count: int
    skipped_count: int


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="Input image files")
    parser.add_argument("--output", help="Output PDF path")
    parser.add_argument(
        "--sort",
        choices=("name", "mtime", "natural"),
        default=None,
        help="Sort mode for input files",
    )
    parser.add_argument(
        "--page-size",
        choices=("a4", "letter", "fit-image"),
        default="a4",
        help="Target page size",
    )
    parser.add_argument(
        "--orientation",
        choices=("auto", "portrait", "landscape"),
        default="auto",
        help="Page orientation",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=20.0,
        help="Page margin in PDF points",
    )
    parser.add_argument(
        "--skip-invalid",
        action="store_true",
        help="Skip unreadable or invalid image files instead of failing fast",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=95,
        help="JPEG quality for embedded images (1-100)",
    )
    parser.add_argument(
        "--title",
        help="Optional PDF title metadata",
    )
    return parser.parse_args(argv)


def validate_input_files(inputs: Iterable[str]) -> list[Path]:
    paths = [Path(item) for item in inputs]
    if not paths:
        raise ValueError("At least one input file is required.")

    validated: list[Path] = []
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"Input file not found: {path}")
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported image format: {path}")
        validated.append(path)
    return validated


def default_output_path(image_paths: Sequence[Path]) -> Path:
    if not image_paths:
        raise ValueError("At least one input file is required to derive an output path.")
    first = image_paths[0]
    return first.with_suffix(".pdf")


def _natural_sort_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def sort_images(paths: Sequence[Path], mode: str | None = None) -> list[Path]:
    if mode is None:
        return list(paths)
    if mode == "name":
        return sorted(paths, key=lambda item: item.name.lower())
    if mode == "mtime":
        return sorted(paths, key=lambda item: item.stat().st_mtime)
    if mode == "natural":
        return sorted(paths, key=_natural_sort_key)
    raise ValueError(f"Unsupported sort mode: {mode}")


def load_and_normalize_image(path: Path) -> Image.Image:
    with Image.open(path) as source:
        normalized = ImageOps.exif_transpose(source)
        if normalized.mode in {"RGBA", "LA"}:
            background = Image.new("RGB", normalized.size, "white")
            alpha = normalized.getchannel("A") if "A" in normalized.getbands() else None
            background.paste(normalized.convert("RGBA"), mask=alpha)
            return background
        if normalized.mode != "RGB":
            return normalized.convert("RGB")
        return normalized.copy()


def image_to_reader(image: Image.Image, jpeg_quality: int = 95) -> ImageReader:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=jpeg_quality, optimize=True)
    buffer.seek(0)
    return ImageReader(buffer)


def resolve_page_size(image_size: tuple[int, int], page_size: str, orientation: str) -> tuple[float, float]:
    if page_size == "fit-image":
        width, height = image_size
        page_width = float(width)
        page_height = float(height)
    else:
        page_width, page_height = PAGE_SIZES[page_size]

    if orientation == "portrait":
        return (min(page_width, page_height), max(page_width, page_height))
    if orientation == "landscape":
        return (max(page_width, page_height), min(page_width, page_height))
    if orientation == "auto":
        image_width, image_height = image_size
        image_landscape = image_width > image_height
        page_landscape = page_width > page_height
        if image_landscape != page_landscape:
            return (page_height, page_width)
        return (page_width, page_height)
    raise ValueError(f"Unsupported orientation: {orientation}")


def compute_page_layout(
    image_size: tuple[int, int],
    page_size: str = "a4",
    margin: float = 20.0,
    orientation: str = "auto",
) -> Layout:
    page_width, page_height = resolve_page_size(image_size, page_size, orientation)
    available_width = max(page_width - (2 * margin), 1)
    available_height = max(page_height - (2 * margin), 1)

    image_width, image_height = image_size
    scale = min(available_width / image_width, available_height / image_height)
    draw_width = image_width * scale
    draw_height = image_height * scale
    x = (page_width - draw_width) / 2
    y = (page_height - draw_height) / 2

    return Layout(
        page_width=page_width,
        page_height=page_height,
        draw_width=draw_width,
        draw_height=draw_height,
        x=x,
        y=y,
    )


def render_pdf(
    image_paths: Sequence[Path],
    output_path: Path,
    page_size: str = "a4",
    margin: float = 20.0,
    orientation: str = "auto",
    skip_invalid: bool = False,
    jpeg_quality: int = 95,
    title: str | None = None,
) -> RenderSummary:
    if not image_paths:
        raise ValueError("At least one image is required to render a PDF.")
    if not 1 <= jpeg_quality <= 100:
        raise ValueError("JPEG quality must be between 1 and 100.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path))
    if title:
        pdf.setTitle(title)

    processed_count = 0
    skipped_count = 0

    for image_path in image_paths:
        try:
            image = load_and_normalize_image(image_path)
        except Exception:
            if skip_invalid:
                skipped_count += 1
                continue
            raise

        layout = compute_page_layout(
            image_size=image.size,
            page_size=page_size,
            margin=margin,
            orientation=orientation,
        )
        pdf.setPageSize((layout.page_width, layout.page_height))
        pdf.drawImage(
            image_to_reader(image, jpeg_quality=jpeg_quality),
            layout.x,
            layout.y,
            width=layout.draw_width,
            height=layout.draw_height,
            preserveAspectRatio=True,
            anchor="c",
        )
        pdf.showPage()
        processed_count += 1

    if processed_count == 0:
        raise ValueError("No valid images were processed.")

    pdf.save()
    return RenderSummary(
        output_path=output_path,
        processed_count=processed_count,
        skipped_count=skipped_count,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    image_paths = validate_input_files(args.inputs)
    ordered_images = sort_images(image_paths, args.sort)
    output_path = Path(args.output) if args.output else default_output_path(ordered_images)
    summary = render_pdf(
        image_paths=ordered_images,
        output_path=output_path,
        page_size=args.page_size,
        margin=args.margin,
        orientation=args.orientation,
        skip_invalid=args.skip_invalid,
        jpeg_quality=args.jpeg_quality,
        title=args.title,
    )
    print(
        f"Output: {summary.output_path}\n"
        f"Processed: {summary.processed_count}\n"
        f"Skipped: {summary.skipped_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
