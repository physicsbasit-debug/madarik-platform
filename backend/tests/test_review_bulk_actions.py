from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_bulk_status_approves_active_questions_without_restoring_deleted() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    project = client.post(f"/api/projects/{project_id}/demo-content").json()

    first_question = project["questions"][0]
    second_question = project["questions"][1]

    client.patch(
        f"/api/projects/{project_id}/questions/{first_question['id']}",
        json={"status": "deleted"},
    )
    client.patch(
        f"/api/projects/{project_id}/questions/{second_question['id']}",
        json={"status": "needs_review"},
    )

    response = client.post(
        f"/api/projects/{project_id}/questions/bulk-status",
        json={"status": "approved", "include_deleted": False},
    )

    assert response.status_code == 200
    questions = response.json()["questions"]
    deleted_question = next(question for question in questions if question["id"] == first_question["id"])
    active_questions = [question for question in questions if question["id"] != first_question["id"]]

    assert deleted_question["status"] == "deleted"
    assert all(question["status"] == "approved" for question in active_questions)


def test_bulk_status_can_restore_deleted_questions_when_requested() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    project = client.post(f"/api/projects/{project_id}/demo-content").json()

    for question in project["questions"]:
        client.patch(
            f"/api/projects/{project_id}/questions/{question['id']}",
            json={"status": "deleted"},
        )

    response = client.post(
        f"/api/projects/{project_id}/questions/bulk-status",
        json={"status": "needs_review", "include_deleted": True},
    )

    assert response.status_code == 200
    questions = response.json()["questions"]
    assert questions
    assert all(question["status"] == "needs_review" for question in questions)
