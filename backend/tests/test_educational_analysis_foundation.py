from fastapi.testclient import TestClient

from app.main import app
from app.models.project import ProjectSession, QuestionItem, AnswerKeyItem
from app.services.educational_analysis import build_educational_analysis

client = TestClient(app)


def test_build_educational_analysis_counts_commands_and_marks() -> None:
    project = ProjectSession(
        questions=[
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
                original_text="Calculate the speed of a wave. [2]",
                translated_text="احسب سرعة موجة. [2]",
                marks=2,
                detected_marks=2,
                order_index=2,
            ),
        ],
        answer_key=[
            AnswerKeyItem(question_id="q-1", question_number="1", draft_answer="إجابة", marks=1)
        ],
    )

    analysis = build_educational_analysis(project)

    assert analysis.question_count == 2
    assert analysis.total_marks == 3
    assert analysis.average_marks == 1.5
    assert analysis.command_distribution["تذكر مباشر"] == 1
    assert analysis.command_distribution["حساب"] == 1
    assert analysis.answer_key_items_count == 1
    assert analysis.recommendations


def test_generate_educational_analysis_endpoint_stores_report() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")
    client.post(f"/api/projects/{project_id}/answer-key/draft")

    response = client.post(f"/api/projects/{project_id}/educational-analysis")

    assert response.status_code == 200
    project = response.json()
    assert project["educational_analysis"]["question_count"] >= 1
    assert project["educational_analysis"]["educational_summary"]
    assert project["educational_analysis"]["recommendations"]


def test_clear_educational_analysis_endpoint_removes_report() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")
    client.post(f"/api/projects/{project_id}/educational-analysis")

    response = client.delete(f"/api/projects/{project_id}/educational-analysis")

    assert response.status_code == 200
    assert response.json()["educational_analysis"] is None
