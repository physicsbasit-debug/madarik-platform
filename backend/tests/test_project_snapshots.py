from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_export_project_snapshot_returns_current_project() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")

    response = client.get(f"/api/projects/{project_id}/snapshot")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == project_id
    assert len(body["questions"]) > 0
    assert len(body["glossary"]) > 0


def test_import_project_snapshot_creates_new_project_id() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    original = client.post(f"/api/projects/{project_id}/demo-content").json()

    response = client.post("/api/projects/import-snapshot", json=original)

    assert response.status_code == 201
    imported = response.json()
    assert imported["id"] != original["id"]
    assert imported["metadata"] == original["metadata"]
    assert len(imported["questions"]) == len(original["questions"])
    assert len(imported["glossary"]) == len(original["glossary"])


def test_imported_snapshot_can_still_export_docx() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    original = client.post(f"/api/projects/{project_id}/demo-content").json()

    imported = client.post("/api/projects/import-snapshot", json=original).json()
    imported_id = imported["id"]

    readiness = client.get(f"/api/projects/{imported_id}/readiness")
    assert readiness.status_code == 200
    assert readiness.json()["ready"] is True

    docx_response = client.post(f"/api/projects/{imported_id}/export/docx")
    assert docx_response.status_code == 200
    assert docx_response.content[:2] == b"PK"
