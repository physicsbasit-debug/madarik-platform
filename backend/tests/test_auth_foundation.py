from pathlib import Path

from fastapi.testclient import TestClient

from app.api import auth as auth_api
from app.main import app
from app.services.auth_repository import AuthRepository

client = TestClient(app)


def test_auth_repository_bootstrap_login_and_token_lookup(tmp_path: Path) -> None:
    repository = AuthRepository(tmp_path / "auth-test.sqlite3")

    assert repository.accounts_exist() is False
    owner = repository.create_owner_if_empty("owner", "مالك المنصة", "123456")
    assert owner is not None
    assert owner.role == "owner"
    assert repository.accounts_exist() is True

    duplicate = repository.create_owner_if_empty("another", "آخر", "123456")
    assert duplicate is None

    authenticated = repository.authenticate("owner", "123456")
    assert authenticated is not None
    token, account = authenticated
    assert account.username == "owner"

    current = repository.get_account_by_token(token)
    assert current is not None
    assert current.id == account.id

    assert repository.logout(token) is True
    assert repository.get_account_by_token(token) is None


def test_auth_api_bootstrap_login_me_and_logout(monkeypatch, tmp_path: Path) -> None:
    repository = AuthRepository(tmp_path / "auth-api-test.sqlite3")
    monkeypatch.setattr(auth_api, "auth_repository", repository)

    status_response = client.get("/api/auth/status")
    assert status_response.status_code == 200
    assert status_response.json()["requires_bootstrap"] is True

    bootstrap_response = client.post(
        "/api/auth/bootstrap",
        json={"username": "owner", "display_name": "مالك منصة مدارك", "password": "123456"},
    )
    assert bootstrap_response.status_code == 201
    bootstrap_body = bootstrap_response.json()
    assert bootstrap_body["account"]["role"] == "owner"
    token = bootstrap_body["token"]

    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "owner"

    logout_response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_response.status_code == 200
    assert logout_response.json()["logged_out"] is True

    expired_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert expired_response.status_code == 401
