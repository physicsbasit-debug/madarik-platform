from fastapi.testclient import TestClient

from app.main import app
from app.models.project import ProjectSession, QuestionItem, QuestionStatus
from app.services.quality_tools import build_quality_tools_report

client = TestClient(app)


def test_build_quality_tools_report_returns_pareto_radar_and_fishbone() -> None:
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
                status=QuestionStatus.approved,
            ),
            QuestionItem(
                id="q-2",
                original_number="2",
                original_text="Explain why the current decreases. [2]",
                translated_text="",
                marks=None,
                detected_marks=None,
                order_index=2,
                status=QuestionStatus.needs_review,
            ),
        ]
    )

    report = build_quality_tools_report(project)

    assert report.pareto_items
    assert "اكتمال الترجمة" in report.radar_axes
    assert "الترجمة والمصطلحات" in report.fishbone_causes
    assert report.priority_actions
    assert report.needs_review is True


def test_generate_quality_tools_endpoint_stores_report() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")
    client.post(f"/api/projects/{project_id}/answer-key/draft")
    client.post(f"/api/projects/{project_id}/educational-analysis")

    response = client.post(f"/api/projects/{project_id}/quality-tools")

    assert response.status_code == 200
    project = response.json()
    assert project["quality_tools"]["quality_summary"]
    assert project["quality_tools"]["radar_axes"]
    assert project["quality_tools"]["fishbone_causes"]


def test_clear_quality_tools_endpoint_removes_report() -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")
    client.post(f"/api/projects/{project_id}/quality-tools")

    response = client.delete(f"/api/projects/{project_id}/quality-tools")

    assert response.status_code == 200
    assert response.json()["quality_tools"] is None
