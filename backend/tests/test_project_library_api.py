from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_project_library_lists_persisted_projects() -> None:
    created = client.post("/api/projects", json={"paper_title": "مشروع مكتبة", "subject": "علوم"}).json()

    response = client.get("/api/projects?limit=20")

    assert response.status_code == 200
    projects = response.json()
    assert any(project["id"] == created["id"] for project in projects)


def test_project_library_opens_persisted_project_after_update() -> None:
    created = client.post("/api/projects", json={"paper_title": "مشروع محفوظ", "subject": "فيزياء"}).json()
    project_id = created["id"]

    update = client.patch(
        f"/api/projects/{project_id}/metadata",
        json={**created["metadata"], "paper_title": "عنوان بعد الحفظ"},
    )
    assert update.status_code == 200

    opened = client.get(f"/api/projects/{project_id}")

    assert opened.status_code == 200
    assert opened.json()["metadata"]["paper_title"] == "عنوان بعد الحفظ"


def test_project_library_delete_removes_project_from_list() -> None:
    created = client.post("/api/projects", json={"paper_title": "مشروع للحذف"}).json()
    project_id = created["id"]

    delete_response = client.delete(f"/api/projects/{project_id}")
    assert delete_response.status_code == 200

    list_response = client.get("/api/projects?limit=100")
    assert list_response.status_code == 200
    assert all(project["id"] != project_id for project in list_response.json())
