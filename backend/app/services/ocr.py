from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError
import pytesseract


class OcrExtractionError(ValueError):
    """Raised when an uploaded image cannot be opened or the OCR engine is unavailable."""


@dataclass(frozen=True)
class ImageOcrExtractionResult:
    """OCR result for a single uploaded image.

    Phase 1-I1 intentionally supports direct image uploads only. Scanned PDF
    OCR remains separate because page rasterisation and layout detection need a
    safer dedicated step.
    """

    text: str
    image_count: int = 1

    @property
    def character_count(self) -> int:
        return len(self.text)

    @property
    def is_text_based(self) -> bool:
        return bool(self.text.strip())

    @property
    def preview(self) -> str:
        normalized = " ".join(self.text.split())
        return normalized[:500]


def _normalize_ocr_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    compact_lines = [line for line in lines if line]
    return "\n".join(compact_lines).strip()


def _prepare_image_for_ocr(image: Image.Image) -> Image.Image:
    """Create a high-contrast image that is friendlier to Tesseract.

    GitHub runners and local machines can produce slightly different OCR output.
    Upscaling, padding, and thresholding make the Phase 1-I1 tests and the actual
    upload path more stable without pretending that OCR is perfect. Humanity can
    keep its shaky screenshots, but at least the code will squint harder.
    """

    normalized = ImageOps.grayscale(image.convert("RGB"))
    normalized = ImageOps.autocontrast(normalized)

    min_width = 1800
    if normalized.width < min_width:
        scale = max(2, int(round(min_width / max(normalized.width, 1))))
        normalized = normalized.resize(
            (normalized.width * scale, normalized.height * scale),
            Image.Resampling.LANCZOS,
        )

    normalized = ImageOps.expand(normalized, border=40, fill="white")
    normalized = normalized.point(lambda value: 0 if value < 170 else 255)
    return normalized


def _run_tesseract(image: Image.Image) -> str:
    configs = (
        "--oem 3 --psm 6",
        "--oem 3 --psm 7",
    )
    for config in configs:
        text = pytesseract.image_to_string(image, lang="eng", config=config)
        normalized = _normalize_ocr_text(text)
        if normalized:
            return normalized
    return ""


def extract_text_from_image_bytes(file_bytes: bytes) -> ImageOcrExtractionResult:
    """Extract English text from a PNG/JPG/WEBP image using Tesseract OCR.

    The project source papers are currently English, so Phase 1-I1 uses the
    English OCR language pack. Arabic OCR and scanned PDF OCR are intentionally
    deferred to keep the phase small and testable.

    Empty OCR output is returned as a normal result rather than an exception.
    The API layer can then store a clear "no readable text" message instead of
    converting weak images into a hard failure.
    """

    if not file_bytes:
        raise OcrExtractionError("ملف الصورة فارغ ولا يمكن استخراج نص منه.")

    try:
        with Image.open(BytesIO(file_bytes)) as image:
            prepared_image = _prepare_image_for_ocr(image)
            text = _run_tesseract(prepared_image)
    except UnidentifiedImageError as exc:
        raise OcrExtractionError("تعذر فتح الملف كصورة صالحة.") from exc
    except pytesseract.TesseractNotFoundError as exc:
        raise OcrExtractionError("محرك OCR غير متاح في بيئة التشغيل الحالية.") from exc
    except Exception as exc:  # pragma: no cover - OCR runtime errors vary
        raise OcrExtractionError("تعذر تشغيل OCR على الصورة الحالية.") from exc

    return ImageOcrExtractionResult(text=text)
