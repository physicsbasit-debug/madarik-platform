from __future__ import annotations

import base64
from dataclasses import dataclass

import fitz

from app.models.project import PdfLayoutAssetInfo


class PdfLayoutAssetExtractionError(ValueError):
    """Raised when PDF layout assets cannot be extracted safely."""


@dataclass(frozen=True)
class PdfLayoutAssetExtractionResult:
    assets: list[PdfLayoutAssetInfo]
    page_count: int
    processed_pages: int
    message: str


def extract_pdf_layout_assets_from_bytes(
    file_bytes: bytes,
    *,
    max_pages: int = 3,
    zoom: float = 1.15,
) -> PdfLayoutAssetExtractionResult:
    """Render low-resolution page snapshots as reviewable PDF layout assets.

    Phase 2-D1 intentionally starts with page snapshots rather than pretending
    that every PDF will politely hand us separated diagrams and tables. PDFs are
    layout goblins. We begin with something deterministic and reviewable.
    """

    if not file_bytes:
        raise PdfLayoutAssetExtractionError("ملف PDF فارغ.")

    try:
        document = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:  # pragma: no cover - exact PyMuPDF errors vary
        raise PdfLayoutAssetExtractionError("تعذر فتح PDF لاستخراج التخطيط.") from exc

    try:
        page_count = document.page_count
        if page_count == 0:
            raise PdfLayoutAssetExtractionError("PDF لا يحتوي على صفحات.")

        processed_pages = min(max_pages, page_count)
        assets: list[PdfLayoutAssetInfo] = []
        matrix = fitz.Matrix(zoom, zoom)

        for page_index in range(processed_pages):
            page = document.load_page(page_index)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            png_bytes = pixmap.tobytes("png")
            assets.append(
                PdfLayoutAssetInfo(
                    name=f"pdf-page-{page_index + 1}.png",
                    size=len(png_bytes),
                    type="image/png",
                    data_base64=base64.b64encode(png_bytes).decode("ascii"),
                    page_number=page_index + 1,
                    source="page_snapshot",
                    note="لقطة تخطيط منخفضة الدقة من صفحة PDF للمراجعة وربط الرسوم/الجداول يدويًا.",
                )
            )

        return PdfLayoutAssetExtractionResult(
            assets=assets,
            page_count=page_count,
            processed_pages=processed_pages,
            message=f"تم استخراج {len(assets)} لقطة تخطيط من أول {processed_pages} صفحة في PDF.",
        )
    finally:
        document.close()
