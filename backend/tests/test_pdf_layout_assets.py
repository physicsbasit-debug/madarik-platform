from io import BytesIO

from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.main import app
from app.services.pdf_layout_assets import extract_pdf_layout_assets_from_bytes

client = TestClient(app)


def _build_simple_pdf() -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 14)
    pdf.drawString(72, 760, "1. State the function of the cell membrane. [1]")
    pdf.rect(72, 680, 180, 45)
    pdf.drawString(82, 700, "Diagram placeholder")
    pdf.showPage()
    pdf.drawString(72, 760, "2. Calculate the speed of a wave. [2]")
    pdf.save()
    return buffer.getvalue()


def _build_pdf_with_pages(page_count: int) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)
    for page_number in range(1, page_count + 1):
        pdf.drawString(72, 760, f"Question page {page_number}")
        if page_number < page_count:
            pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def test_extract_pdf_layout_assets_from_bytes_renders_page_snapshots() -> None:
    result = extract_pdf_layout_assets_from_bytes(_build_simple_pdf(), max_pages=2)

    assert result.page_count == 2
    assert result.processed_pages == 2
    assert len(result.assets) == 2
    assert result.assets[0].page_number == 1
    assert result.assets[0].type == "image/png"
    assert result.assets[0].data_base64


def test_extract_pdf_layout_assets_default_limit_remains_three_pages() -> None:
    result = extract_pdf_layout_assets_from_bytes(_build_pdf_with_pages(5))

    assert result.page_count == 5
    assert result.processed_pages == 3
    assert [asset.page_number for asset in result.assets] == [1, 2, 3]


def test_pdf_layout_assets_endpoint_stores_assets_on_project() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/layout-assets/pdf",
        files={"file": ("layout.pdf", _build_simple_pdf(), "application/pdf")},
    )

    assert response.status_code == 200
    project = response.json()
    assert len(project["layout_assets"]) >= 1
    assert project["layout_assets"][0]["page_number"] == 1


def test_pdf_layout_assets_endpoint_renders_all_pages_within_safe_cap() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/layout-assets/pdf",
        files={
            "file": (
                "five-page-layout.pdf",
                _build_pdf_with_pages(5),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    assets = response.json()["layout_assets"]
    assert len(assets) == 5
    assert [asset["page_number"] for asset in assets] == [1, 2, 3, 4, 5]


def test_delete_pdf_layout_asset_endpoint_removes_asset() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    response = client.post(
        f"/api/projects/{project_id}/layout-assets/pdf",
        files={"file": ("layout.pdf", _build_simple_pdf(), "application/pdf")},
    )
    asset_id = response.json()["layout_assets"][0]["id"]

    delete_response = client.delete(
        f"/api/projects/{project_id}/layout-assets/{asset_id}"
    )

    assert delete_response.status_code == 200
    remaining_ids = [
        asset["id"] for asset in delete_response.json()["layout_assets"]
    ]
    assert asset_id not in remaining_ids
