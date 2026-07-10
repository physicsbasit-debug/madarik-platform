from pathlib import Path

from fastapi.testclient import TestClient

from app.api import auth as auth_api
from app.main import app
from app.services.auth_repository import AuthRepository

client = TestClient(app)


def _owner_token(repository: AuthRepository) -> str:
    owner = repository.create_owner_if_empty("owner", "مالك المنصة", "123456")
    assert owner is not None
    authenticated = repository.authenticate("owner", "123456")
    assert authenticated is not None
    token, _ = authenticated
    return token


def test_owner_can_create_list_and_disable_account(monkeypatch, tmp_path: Path) -> None:
    repository = AuthRepository(tmp_path / "auth-b3-test.sqlite3")
    monkeypatch.setattr(auth_api, "auth_repository", repository)
    token = _owner_token(repository)

    create_response = client.post(
        "/api/auth/accounts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "teacher1",
            "display_name": "معلم علوم",
            "password": "123456",
            "role": "teacher",
            "is_active": True,
        },
    )
    assert create_response.status_code == 201
    teacher_id = create_response.json()["id"]

    list_response = client.get("/api/auth/accounts", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200
    assert any(account["username"] == "teacher1" for account in list_response.json())

    disable_response = client.patch(
        f"/api/auth/accounts/{teacher_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"is_active": False},
    )
    assert disable_response.status_code == 200
    assert disable_response.json()["is_active"] is False

    assert repository.authenticate("teacher1", "123456") is None


def test_non_owner_cannot_manage_accounts(monkeypatch, tmp_path: Path) -> None:
    repository = AuthRepository(tmp_path / "auth-b3-test.sqlite3")
    monkeypatch.setattr(auth_api, "auth_repository", repository)
    owner_token = _owner_token(repository)
    teacher = repository.create_account("teacher2", "معلم", "123456", role=auth_api.AccountRole.teacher)
    authenticated = repository.authenticate("teacher2", "123456")
    assert authenticated is not None
    teacher_token, _ = authenticated

    response = client.get("/api/auth/accounts", headers={"Authorization": f"Bearer {teacher_token}"})
    assert response.status_code == 403

    owner_self_disable = client.patch(
        f"/api/auth/accounts/{repository.get_account_by_username('owner').id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"is_active": False},
    )
    assert owner_self_disable.status_code == 400
