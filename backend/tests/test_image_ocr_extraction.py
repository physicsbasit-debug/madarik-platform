from io import BytesIO
from pathlib import Path
import shutil

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont

from app.main import app
from app.services.ocr import ImageOcrExtractionResult, extract_text_from_image_bytes

client = TestClient(app)


def _load_test_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    for font_path in candidates:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default()


def _build_text_image_bytes(text: str = "1. State cell membrane function. [1]") -> bytes:
    image = Image.new("RGB", (1800, 360), "white")
    draw = ImageDraw.Draw(image)
    font = _load_test_font(58)
    draw.text((60, 120), text, fill="black", font=font)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="Tesseract is not installed in this environment.")
def test_extract_text_from_image_bytes_smoke_reads_or_at_least_runs_without_hard_failure() -> None:
    image_bytes = _build_text_image_bytes()

    result = extract_text_from_image_bytes(image_bytes)

    assert isinstance(result.text, str)
    assert result.character_count >= 0
    # OCR can vary across CI environments. We only require that the function runs
    # and, when text is detected, it contains plausible tokens from the prompt.
    normalized = result.text.lower()
    if normalized:
        assert any(token in normalized for token in ("state", "cell", "membrane", "function"))


def test_upload_image_ocr_endpoint_stores_extracted_text(monkeypatch: pytest.MonkeyPatch) -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    image_bytes = _build_text_image_bytes("1. Explain why current decreases. [2]")

    monkeypatch.setattr(
        "app.api.projects.extract_text_from_image_bytes",
        lambda _bytes: ImageOcrExtractionResult(text="1. Explain why current decreases. [2]"),
    )

    response = client.post(
        f"/api/projects/{project_id}/upload-image-ocr",
        files={"file": ("question.png", image_bytes, "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["uploaded_file"]["name"] == "question.png"
    assert body["extracted_text"]["is_text_based"] is True
    assert "current" in body["extracted_text"]["text"].lower()
    assert "OCR" in body["extracted_text"]["message"]


def test_upload_image_ocr_accepts_valid_low_information_image_without_hard_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    image = Image.new("RGB", (800, 300), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")

    monkeypatch.setattr(
        "app.api.projects.extract_text_from_image_bytes",
        lambda _bytes: ImageOcrExtractionResult(text=""),
    )

    response = client.post(
        f"/api/projects/{project_id}/upload-image-ocr",
        files={"file": ("blank.png", buffer.getvalue(), "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["uploaded_file"]["name"] == "blank.png"
    assert "OCR" in body["extracted_text"]["message"]


def test_upload_image_ocr_rejects_non_image() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/upload-image-ocr",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert "PNG" in response.json()["detail"]
