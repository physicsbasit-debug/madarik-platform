from fastapi.testclient import TestClient

from app.main import app
from app.models.project import QuestionStatus

client = TestClient(app)


def test_project_readiness_blocks_empty_project_export() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.get(f"/api/projects/{project_id}/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["ready"] is False
    assert any(issue["code"] == "missing_questions" for issue in body["issues"])


def test_project_readiness_is_ready_with_demo_content() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")

    response = client.get(f"/api/projects/{project_id}/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["ready"] is True
    assert body["exportable_question_count"] > 0
    assert body["total_marks"] > 0


def test_project_readiness_blocks_when_all_questions_deleted() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    project = client.post(f"/api/projects/{project_id}/demo-content").json()

    for question in project["questions"]:
        client.patch(
            f"/api/projects/{project_id}/questions/{question['id']}",
            json={"status": QuestionStatus.deleted.value},
        )

    response = client.get(f"/api/projects/{project_id}/readiness")

    assert response.status_code == 200
    body = response.json()
    assert body["ready"] is False
    assert any(issue["code"] == "all_questions_deleted" for issue in body["issues"])
