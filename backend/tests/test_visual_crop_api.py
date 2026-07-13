from __future__ import annotations

import base64
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image as PILImage

from app.api.projects import project_store
from app.main import app
from app.models.project import (
    PdfLayoutAssetInfo,
    QuestionItem,
)


client = TestClient(app)


def _build_page_image_base64() -> str:
    image = PILImage.new(
        "RGB",
        (120, 80),
        (255, 0, 0),
    )

    for x in range(60, 120):
        for y in range(80):
            image.putpixel(
                (x, y),
                (0, 0, 255),
            )

    output = BytesIO()
    image.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("ascii")


def _seed_crop_project(*, linked: bool = True) -> str:
    response = client.post("/api/projects")
    assert response.status_code == 201
    project_id = response.json()["id"]

    project = project_store.get(project_id)
    assert project is not None

    page_data = _build_page_image_base64()

    project.questions = [
        QuestionItem(
            id="question-1",
            original_number="1",
            original_text="Original question",
            translated_text="السؤال المترجم",
            order_index=1,
            linked_layout_asset_ids=(
                ["layout-1"]
                if linked
                else []
            ),
        )
    ]

    project.layout_assets = [
        PdfLayoutAssetInfo(
            id="layout-1",
            name="page-1.png",
            size=len(base64.b64decode(page_data)),
            type="image/png",
            data_base64=page_data,
            page_number=1,
            source="pdf_layout",
            note="لقطة الصفحة الأولى",
        )
    ]

    project_store.touch(project_id)
    return project_id


def test_crop_linked_layout_asset_creates_question_attachment() -> None:
    project_id = _seed_crop_project()

    response = client.post(
        (
            f"/api/projects/{project_id}"
            "/questions/question-1"
            "/layout-assets/layout-1/crop"
        ),
        json={
            "x": 0.5,
            "y": 0,
            "width": 0.5,
            "height": 1,
            "name": "شكل الكرة والمضرب",
        },
    )

    assert response.status_code == 200

    question = response.json()["questions"][0]
    assert len(question["attachments"]) == 1

    attachment = question["attachments"][0]

    assert attachment["name"] == "شكل الكرة والمضرب.png"
    assert attachment["type"] == "image/png"
    assert attachment["size"] > 0
    assert attachment["id"].startswith("pdf-crop-")

    image_bytes = base64.b64decode(
        attachment["data_base64"]
    )

    with PILImage.open(BytesIO(image_bytes)) as image:
        image.load()

        assert image.size == (60, 80)
        assert image.getpixel((10, 10))[:3] == (
            0,
            0,
            255,
        )


def test_crop_requires_layout_asset_to_be_linked() -> None:
    project_id = _seed_crop_project(linked=False)

    response = client.post(
        (
            f"/api/projects/{project_id}"
            "/questions/question-1"
            "/layout-assets/layout-1/crop"
        ),
        json={
            "x": 0,
            "y": 0,
            "width": 0.5,
            "height": 0.5,
        },
    )

    assert response.status_code == 400
    assert "ربط لقطة PDF" in response.json()["detail"]


def test_crop_rejects_area_outside_image_bounds() -> None:
    project_id = _seed_crop_project()

    response = client.post(
        (
            f"/api/projects/{project_id}"
            "/questions/question-1"
            "/layout-assets/layout-1/crop"
        ),
        json={
            "x": 0.8,
            "y": 0,
            "width": 0.3,
            "height": 0.5,
        },
    )

    assert response.status_code == 400
    assert "تتجاوز حدود الصورة" in response.json()["detail"]


def test_crop_returns_404_for_missing_layout_asset() -> None:
    project_id = _seed_crop_project()

    response = client.post(
        (
            f"/api/projects/{project_id}"
            "/questions/question-1"
            "/layout-assets/missing-layout/crop"
        ),
        json={
            "x": 0,
            "y": 0,
            "width": 0.5,
            "height": 0.5,
        },
    )

    assert response.status_code == 404
    assert "layout asset" in response.json()["detail"].lower()
