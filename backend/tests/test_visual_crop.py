from __future__ import annotations

import base64
from io import BytesIO

from PIL import Image as PILImage
import pytest

from app.services.visual_crop import (
    VisualCropError,
    crop_image_base64,
)


def _build_test_image_base64() -> str:
    image = PILImage.new(
        "RGB",
        (100, 80),
        (255, 0, 0),
    )

    for x in range(50, 100):
        for y in range(80):
            image.putpixel(
                (x, y),
                (0, 0, 255),
            )

    output = BytesIO()
    image.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("ascii")


def _read_result_image(result_base64: str) -> PILImage.Image:
    raw = base64.b64decode(result_base64)
    image = PILImage.open(BytesIO(raw))
    image.load()
    return image


def test_crop_image_base64_returns_selected_region_as_png() -> None:
    result = crop_image_base64(
        _build_test_image_base64(),
        x=0.5,
        y=0,
        width=0.5,
        height=1,
    )

    cropped = _read_result_image(result.data_base64)

    assert result.mime_type == "image/png"
    assert result.size > 0
    assert result.width == 50
    assert result.height == 80
    assert cropped.size == (50, 80)
    assert cropped.getpixel((10, 10))[:3] == (0, 0, 255)


@pytest.mark.parametrize(
    ("x", "y", "width", "height"),
    [
        (-0.1, 0, 0.5, 0.5),
        (0, -0.1, 0.5, 0.5),
        (0, 0, 0, 0.5),
        (0, 0, 0.5, 0),
        (0.8, 0, 0.3, 0.5),
        (0, 0.8, 0.5, 0.3),
        (1, 0, 0.1, 0.1),
        (0, 1, 0.1, 0.1),
    ],
)
def test_crop_image_base64_rejects_invalid_crop_box(
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    with pytest.raises(VisualCropError):
        crop_image_base64(
            _build_test_image_base64(),
            x=x,
            y=y,
            width=width,
            height=height,
        )


def test_crop_image_base64_rejects_tiny_pixel_selection() -> None:
    with pytest.raises(
        VisualCropError,
        match="صغيرة جدًا",
    ):
        crop_image_base64(
            _build_test_image_base64(),
            x=0,
            y=0,
            width=0.001,
            height=0.001,
        )


def test_crop_image_base64_rejects_invalid_image_data() -> None:
    invalid_data = base64.b64encode(
        b"this-is-not-an-image",
    ).decode("ascii")

    with pytest.raises(
        VisualCropError,
        match="تعذر قراءة",
    ):
        crop_image_base64(
            invalid_data,
            x=0,
            y=0,
            width=1,
            height=1,
        )
