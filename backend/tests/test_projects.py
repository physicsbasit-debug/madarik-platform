from fastapi.testclient import TestClient

from app.main import app


def test_create_and_delete_project() -> None:
    client = TestClient(app)
    create_response = client.post("/api/projects", json={"school_name": "مدرسة تجريبية"})
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    read_response = client.get(f"/api/projects/{project_id}")
    assert read_response.status_code == 200
    assert read_response.json()["metadata"]["school_name"] == "مدرسة تجريبية"

    delete_response = client.delete(f"/api/projects/{project_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True
