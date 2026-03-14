from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from images_to_pdf import (  # noqa: E402
    compute_page_layout,
    default_output_path,
    main,
    render_pdf,
    sort_images,
    validate_input_files,
)


def create_image(path: Path, size=(100, 200), color="blue", mode="RGB") -> Path:
    image = Image.new(mode, size, color)
    image.save(path)
    return path


def test_validate_input_files_accepts_supported_images(tmp_path: Path) -> None:
    image_path = create_image(tmp_path / "sample.jpg")
    result = validate_input_files([str(image_path)])
    assert result == [image_path]


def test_validate_input_files_rejects_unsupported_extension(tmp_path: Path) -> None:
    bad_path = tmp_path / "notes.txt"
    bad_path.write_text("nope", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported image format"):
        validate_input_files([str(bad_path)])


def test_sort_images_by_name(tmp_path: Path) -> None:
    path_b = create_image(tmp_path / "b.jpg")
    path_a = create_image(tmp_path / "a.jpg")
    result = sort_images([path_b, path_a], mode="name")
    assert result == [path_a, path_b]


def test_sort_images_by_natural_order(tmp_path: Path) -> None:
    path_10 = create_image(tmp_path / "page10.jpg")
    path_2 = create_image(tmp_path / "page2.jpg")
    result = sort_images([path_10, path_2], mode="natural")
    assert result == [path_2, path_10]


def test_sort_images_by_mtime(tmp_path: Path) -> None:
    older = create_image(tmp_path / "older.jpg")
    newer = create_image(tmp_path / "newer.jpg")
    os.utime(older, (100, 100))
    os.utime(newer, (200, 200))
    result = sort_images([newer, older], mode="mtime")
    assert result == [older, newer]


def test_compute_page_layout_respects_margin() -> None:
    layout = compute_page_layout((1000, 500), page_size="a4", margin=20, orientation="portrait")
    assert layout.x >= 20
    assert layout.y >= 20
    assert layout.draw_width <= layout.page_width - 40
    assert layout.draw_height <= layout.page_height - 40


def test_compute_page_layout_preserves_aspect_ratio() -> None:
    layout = compute_page_layout((1000, 500), page_size="a4", margin=20, orientation="portrait")
    assert pytest.approx(layout.draw_width / layout.draw_height, rel=1e-3) == 2.0


def test_default_output_path_uses_first_input_name(tmp_path: Path) -> None:
    image1 = create_image(tmp_path / "receipt-01.jpg")
    output = default_output_path([image1])
    assert output.name == "receipt-01.pdf"
    assert output.parent == tmp_path


def test_render_pdf_from_multiple_images(tmp_path: Path) -> None:
    image1 = create_image(tmp_path / "one.jpg", size=(400, 300), color="red")
    image2 = create_image(tmp_path / "two.png", size=(300, 400), color="green")
    output = tmp_path / "result.pdf"

    render_pdf([image1, image2], output)

    assert output.exists()
    reader = PdfReader(str(output))
    assert len(reader.pages) == 2


def test_render_pdf_fails_on_invalid_image(tmp_path: Path) -> None:
    bad = tmp_path / "broken.jpg"
    bad.write_bytes(b"not-a-real-image")
    output = tmp_path / "result.pdf"

    with pytest.raises(Exception):
        render_pdf([bad], output)


def test_render_pdf_skips_invalid_image_when_enabled(tmp_path: Path) -> None:
    good = create_image(tmp_path / "good.jpg")
    bad = tmp_path / "broken.jpg"
    bad.write_bytes(b"not-a-real-image")
    output = tmp_path / "result.pdf"

    summary = render_pdf([good, bad], output, skip_invalid=True)

    assert output.exists()
    assert summary.processed_count == 1
    assert summary.skipped_count == 1
    reader = PdfReader(str(output))
    assert len(reader.pages) == 1


def test_render_pdf_writes_title_metadata(tmp_path: Path) -> None:
    image1 = create_image(tmp_path / "one.jpg")
    output = tmp_path / "titled.pdf"

    render_pdf([image1], output, title="Homework 5")

    reader = PdfReader(str(output))
    assert reader.metadata.title == "Homework 5"


def test_render_pdf_writes_author_and_subject_metadata(tmp_path: Path) -> None:
    image1 = create_image(tmp_path / "one.jpg")
    output = tmp_path / "meta.pdf"

    render_pdf([image1], output, title="Homework 5", author="Franky", subject="AI Assignment")

    reader = PdfReader(str(output))
    assert reader.metadata.title == "Homework 5"
    assert reader.metadata.author == "Franky"
    assert reader.metadata.subject == "AI Assignment"


def test_main_creates_output_pdf(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    image1 = create_image(tmp_path / "one.jpg")
    image2 = create_image(tmp_path / "two.jpg")
    output = tmp_path / "merged.pdf"

    code = main(
        [
            str(image1),
            str(image2),
            "--output",
            str(output),
            "--title",
            "Demo PDF",
            "--author",
            "Franky",
            "--subject",
            "Merged Notes",
        ]
    )

    assert code == 0
    assert output.exists()
    reader = PdfReader(str(output))
    assert len(reader.pages) == 2
    assert reader.metadata.title == "Demo PDF"
    assert reader.metadata.author == "Franky"
    assert reader.metadata.subject == "Merged Notes"
    out = capsys.readouterr().out
    assert "Processed: 2" in out
    assert "Skipped: 0" in out


def test_main_auto_generates_output_when_missing(tmp_path: Path) -> None:
    image1 = create_image(tmp_path / "receipt-01.jpg")

    code = main([str(image1)])

    assert code == 0
    assert (tmp_path / "receipt-01.pdf").exists()


def test_main_skip_invalid_reports_summary(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    good = create_image(tmp_path / "good.jpg")
    bad = tmp_path / "broken.jpg"
    bad.write_bytes(b"not-a-real-image")
    output = tmp_path / "merged.pdf"

    code = main([str(good), str(bad), "--output", str(output), "--skip-invalid"])

    assert code == 0
    out = capsys.readouterr().out
    assert "Processed: 1" in out
    assert "Skipped: 1" in out
    assert str(output) in out


def test_main_requires_at_least_one_input(tmp_path: Path) -> None:
    output = tmp_path / "merged.pdf"
    with pytest.raises(SystemExit):
        main(["--output", str(output)])
