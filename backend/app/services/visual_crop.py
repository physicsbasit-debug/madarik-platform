from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from io import BytesIO
import math

from PIL import Image as PILImage
from PIL import UnidentifiedImageError


MAX_SOURCE_BYTES = 12_000_000
MIN_CROP_PIXELS = 2


class VisualCropError(ValueError):
    """Raised when a visual crop request is invalid or cannot be processed."""


@dataclass(frozen=True)
class VisualCropResult:
    data_base64: str
    size: int
    width: int
    height: int
    mime_type: str = "image/png"


def _validate_normalized_crop_box(
    *,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    values = (x, y, width, height)

    if not all(math.isfinite(value) for value in values):
        raise VisualCropError("إحداثيات القص يجب أن تكون أرقامًا محددة.")

    if x < 0 or y < 0:
        raise VisualCropError("موضع القص لا يمكن أن يكون سالبًا.")

    if width <= 0 or height <= 0:
        raise VisualCropError("عرض القص وارتفاعه يجب أن يكونا أكبر من صفر.")

    if x >= 1 or y >= 1:
        raise VisualCropError("بداية القص يجب أن تكون داخل الصورة.")

    tolerance = 1e-9
    if x + width > 1 + tolerance or y + height > 1 + tolerance:
        raise VisualCropError("منطقة القص تتجاوز حدود الصورة.")


def crop_image_base64(
    data_base64: str,
    *,
    x: float,
    y: float,
    width: float,
    height: float,
) -> VisualCropResult:
    """Crop an image using normalized coordinates and return a PNG result.

    Coordinates are expressed from 0 to 1:
    - x/y: top-left position.
    - width/height: selected area size.
    """

    _validate_normalized_crop_box(
        x=x,
        y=y,
        width=width,
        height=height,
    )

    if not data_base64:
        raise VisualCropError("الصورة المصدر فارغة.")

    try:
        source_bytes = base64.b64decode(
            data_base64,
            validate=True,
        )
    except (binascii.Error, ValueError) as exc:
        raise VisualCropError("بيانات الصورة المصدر غير صالحة.") from exc

    if not source_bytes:
        raise VisualCropError("الصورة المصدر فارغة.")

    if len(source_bytes) > MAX_SOURCE_BYTES:
        raise VisualCropError("حجم الصورة المصدر أكبر من الحد المسموح للقص.")

    try:
        with PILImage.open(BytesIO(source_bytes)) as source:
            source.load()

            source_width, source_height = source.size
            if source_width < MIN_CROP_PIXELS or source_height < MIN_CROP_PIXELS:
                raise VisualCropError("أبعاد الصورة المصدر صغيرة جدًا.")

            left = max(0, min(source_width, round(x * source_width)))
            top = max(0, min(source_height, round(y * source_height)))
            right = max(
                0,
                min(
                    source_width,
                    round((x + width) * source_width),
                ),
            )
            bottom = max(
                0,
                min(
                    source_height,
                    round((y + height) * source_height),
                ),
            )

            crop_width = right - left
            crop_height = bottom - top

            if (
                crop_width < MIN_CROP_PIXELS
                or crop_height < MIN_CROP_PIXELS
            ):
                raise VisualCropError(
                    "منطقة القص صغيرة جدًا. حدّد مساحة أوضح حول الشكل.",
                )

            normalized_source = (
                source.convert("RGBA")
                if "A" in source.getbands()
                else source.convert("RGB")
            )
            cropped = normalized_source.crop(
                (left, top, right, bottom),
            )

            output = BytesIO()
            cropped.save(
                output,
                format="PNG",
                optimize=True,
            )
            output_bytes = output.getvalue()

    except VisualCropError:
        raise
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ) as exc:
        raise VisualCropError(
            "تعذر قراءة الصورة المصدر أو قصها.",
        ) from exc

    return VisualCropResult(
        data_base64=base64.b64encode(output_bytes).decode("ascii"),
        size=len(output_bytes),
        width=crop_width,
        height=crop_height,
    )
