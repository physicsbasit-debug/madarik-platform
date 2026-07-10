from pathlib import Path

from fastapi.testclient import TestClient

from app.api import auth as auth_api
from app.api import projects as projects_api
from app.main import app
from app.services.auth_repository import AuthRepository
from app.services.project_repository import ProjectRepository
from app.services.session_store import InMemoryProjectStore

client = TestClient(app)


def test_owned_project_requires_access_token(monkeypatch, tmp_path: Path) -> None:
    auth_repository = AuthRepository(tmp_path / "ownership-auth.sqlite3")
    project_store = InMemoryProjectStore(ProjectRepository(tmp_path / "ownership-projects.sqlite3"))
    monkeypatch.setattr(auth_api, "auth_repository", auth_repository)
    monkeypatch.setattr(projects_api, "auth_repository", auth_repository)
    monkeypatch.setattr(projects_api, "project_store", project_store)

    bootstrap = client.post(
        "/api/auth/bootstrap",
        json={"username": "owner", "display_name": "مالك المنصة", "password": "123456"},
    )
    assert bootstrap.status_code == 201
    token = bootstrap.json()["token"]
    account_id = bootstrap.json()["account"]["id"]

    created = client.post(
        "/api/projects",
        json={"paper_title": "مشروع مملوك"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert created.status_code == 201
    project = created.json()
    assert project["owner_account_id"] == account_id

    anonymous_open = client.get(f"/api/projects/{project['id']}")
    assert anonymous_open.status_code == 403

    owner_open = client.get(f"/api/projects/{project['id']}", headers={"Authorization": f"Bearer {token}"})
    assert owner_open.status_code == 200
    assert owner_open.json()["id"] == project["id"]


def test_project_library_filters_owned_projects_for_anonymous_users(monkeypatch, tmp_path: Path) -> None:
    auth_repository = AuthRepository(tmp_path / "library-auth.sqlite3")
    project_store = InMemoryProjectStore(ProjectRepository(tmp_path / "library-projects.sqlite3"))
    monkeypatch.setattr(auth_api, "auth_repository", auth_repository)
    monkeypatch.setattr(projects_api, "auth_repository", auth_repository)
    monkeypatch.setattr(projects_api, "project_store", project_store)

    bootstrap = client.post(
        "/api/auth/bootstrap",
        json={"username": "owner", "display_name": "مالك المنصة", "password": "123456"},
    )
    token = bootstrap.json()["token"]

    unowned = client.post("/api/projects", json={"paper_title": "مشروع قديم بلا مالك"}).json()
    owned = client.post(
        "/api/projects",
        json={"paper_title": "مشروع خاص"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    anonymous_list = client.get("/api/projects?limit=20")
    assert anonymous_list.status_code == 200
    anonymous_ids = {project["id"] for project in anonymous_list.json()}
    assert unowned["id"] in anonymous_ids
    assert owned["id"] not in anonymous_ids

    owner_list = client.get("/api/projects?limit=20", headers={"Authorization": f"Bearer {token}"})
    assert owner_list.status_code == 200
    owner_ids = {project["id"] for project in owner_list.json()}
    assert unowned["id"] in owner_ids
    assert owned["id"] in owner_ids
