from fastapi.testclient import TestClient

from app.main import app
from app.models.project import PdfLayoutAssetInfo
from app.services.session_store import project_store


client = TestClient(app)


def _create_project_with_question_and_asset():
    project_id = client.post("/api/projects", json={}).json()["id"]

    demo_response = client.post(
        f"/api/projects/{project_id}/demo-content"
    )
    assert demo_response.status_code == 200

    question_id = demo_response.json()["questions"][0]["id"]

    asset = PdfLayoutAssetInfo(
        name="page-1.png",
        size=10,
        type="image/png",
        data_base64="dGVzdA==",
        page_number=1,
    )

    updated = project_store.set_layout_assets(project_id, [asset])
    assert updated is not None

    return project_id, question_id, asset.id


def test_link_layout_asset_endpoint() -> None:
    project_id, question_id, asset_id = (
        _create_project_with_question_and_asset()
    )

    response = client.post(
        f"/api/projects/{project_id}"
        f"/questions/{question_id}"
        f"/layout-assets/{asset_id}"
    )

    assert response.status_code == 200
    question = response.json()["questions"][0]
    assert question["linked_layout_asset_ids"] == [asset_id]


def test_link_layout_asset_endpoint_is_idempotent() -> None:
    project_id, question_id, asset_id = (
        _create_project_with_question_and_asset()
    )

    route = (
        f"/api/projects/{project_id}"
        f"/questions/{question_id}"
        f"/layout-assets/{asset_id}"
    )

    assert client.post(route).status_code == 200
    second_response = client.post(route)

    assert second_response.status_code == 200
    question = second_response.json()["questions"][0]
    assert question["linked_layout_asset_ids"] == [asset_id]


def test_link_layout_asset_endpoint_rejects_missing_asset() -> None:
    project_id, question_id, _ = (
        _create_project_with_question_and_asset()
    )

    response = client.post(
        f"/api/projects/{project_id}"
        f"/questions/{question_id}"
        "/layout-assets/missing-asset"
    )

    assert response.status_code == 404


def test_link_layout_asset_endpoint_rejects_missing_question() -> None:
    project_id, _, asset_id = (
        _create_project_with_question_and_asset()
    )

    response = client.post(
        f"/api/projects/{project_id}"
        "/questions/missing-question"
        f"/layout-assets/{asset_id}"
    )

    assert response.status_code == 404


def test_unlink_layout_asset_endpoint() -> None:
    project_id, question_id, asset_id = (
        _create_project_with_question_and_asset()
    )

    route = (
        f"/api/projects/{project_id}"
        f"/questions/{question_id}"
        f"/layout-assets/{asset_id}"
    )

    assert client.post(route).status_code == 200

    delete_response = client.delete(route)

    assert delete_response.status_code == 200
    question = delete_response.json()["questions"][0]
    assert question["linked_layout_asset_ids"] == []


def test_unlink_layout_asset_endpoint_rejects_missing_link() -> None:
    project_id, question_id, asset_id = (
        _create_project_with_question_and_asset()
    )

    response = client.delete(
        f"/api/projects/{project_id}"
        f"/questions/{question_id}"
        f"/layout-assets/{asset_id}"
    )

    assert response.status_code == 404
