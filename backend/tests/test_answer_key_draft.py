from fastapi.testclient import TestClient

from app.main import app
from app.models.project import QuestionItem, QuestionStatus
from app.services.answer_key import build_answer_key_draft

client = TestClient(app)


def test_build_answer_key_draft_skips_deleted_questions() -> None:
    questions = [
        QuestionItem(
            id="q-1",
            original_number="1",
            original_text="State the function of the cell membrane. [1]",
            translated_text="اذكر وظيفة غشاء الخلية. [1]",
            marks=1,
            detected_marks=1,
            order_index=1,
        ),
        QuestionItem(
            id="q-2",
            original_number="2",
            original_text="Describe a reaction. [2]",
            translated_text="",
            marks=2,
            detected_marks=2,
            order_index=2,
            status=QuestionStatus.deleted,
        ),
    ]

    answer_key = build_answer_key_draft(questions)

    assert len(answer_key) == 1
    assert answer_key[0].question_id == "q-1"
    assert "غشاء الخلية" in answer_key[0].draft_answer
    assert answer_key[0].needs_review is True


def test_generate_answer_key_draft_endpoint_stores_key() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    demo_response = client.post(f"/api/projects/{project_id}/demo-content")
    assert demo_response.status_code == 200

    response = client.post(f"/api/projects/{project_id}/answer-key/draft")

    assert response.status_code == 200
    project = response.json()
    assert len(project["answer_key"]) >= 1
    assert project["answer_key"][0]["draft_answer"]
    assert project["answer_key"][0]["needs_review"] is True


def test_clear_answer_key_endpoint_removes_key() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")
    client.post(f"/api/projects/{project_id}/answer-key/draft")

    response = client.delete(f"/api/projects/{project_id}/answer-key")

    assert response.status_code == 200
    assert response.json()["answer_key"] == []
