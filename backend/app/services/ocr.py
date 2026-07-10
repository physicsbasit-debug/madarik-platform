from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError
import pytesseract


class OcrExtractionError(ValueError):
    """Raised when an uploaded image cannot be processed by OCR."""


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


def extract_text_from_image_bytes(file_bytes: bytes) -> ImageOcrExtractionResult:
    """Extract English text from a PNG/JPG/WEBP image using Tesseract OCR.

    The project source papers are currently English, so Phase 1-I1 uses the
    English OCR language pack. Arabic OCR and scanned PDF OCR are intentionally
    deferred to keep the phase small and testable.
    """

    if not file_bytes:
        raise OcrExtractionError("ملف الصورة فارغ ولا يمكن استخراج نص منه.")

    try:
        with Image.open(BytesIO(file_bytes)) as image:
            normalized_image = ImageOps.grayscale(image.convert("RGB"))
            normalized_image = ImageOps.autocontrast(normalized_image)
            text = pytesseract.image_to_string(normalized_image, lang="eng")
    except UnidentifiedImageError as exc:
        raise OcrExtractionError("تعذر فتح الملف كصورة صالحة.") from exc
    except pytesseract.TesseractNotFoundError as exc:
        raise OcrExtractionError("محرك OCR غير متاح في بيئة التشغيل الحالية.") from exc
    except Exception as exc:  # pragma: no cover - OCR runtime errors vary
        raise OcrExtractionError("تعذر تشغيل OCR على الصورة الحالية.") from exc

    return ImageOcrExtractionResult(text=_normalize_ocr_text(text))
