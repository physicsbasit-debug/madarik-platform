from fastapi.testclient import TestClient

from app.main import app
from app.models.project import (
    ProjectSession,
    QuestionItem,
    QuestionPart,
    QuestionStatus,
    ReadinessSeverity,
)
from app.services.readiness import build_project_readiness_report

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


def _hierarchical_marks_question(*, question_marks: int | None) -> QuestionItem:
    return QuestionItem(
        id="question-marks-guidance",
        original_number="4",
        original_text="Structured multipart question",
        translated_text="سؤال متعدد الأجزاء",
        marks=question_marks,
        order_index=1,
        parts=[
            QuestionPart(
                id="part-e",
                label="(e)",
                original_text="Parent branch",
                translated_text="الفرع الرئيسي",
                marks=3,
                order_index=1,
            ),
            QuestionPart(
                id="part-i",
                label="(i)",
                original_text="First child",
                translated_text="الجزء الفرعي الأول",
                marks=1,
                parent_id="part-e",
                order_index=2,
            ),
            QuestionPart(
                id="part-ii",
                label="(ii)",
                original_text="Second child",
                translated_text="الجزء الفرعي الثاني",
                marks=2,
                parent_id="part-e",
                order_index=3,
            ),
        ],
    )


def test_marks_mismatch_is_warning_only_and_keeps_declared_total() -> None:
    report = build_project_readiness_report(
        ProjectSession(
            questions=[
                _hierarchical_marks_question(question_marks=1),
            ],
        )
    )

    mismatch = next(
        issue
        for issue in report.issues
        if issue.code == "question_parts_marks_mismatch"
    )

    assert report.ready is True
    assert report.total_marks == 1
    assert mismatch.severity == ReadinessSeverity.warning
    assert "(1)" in mismatch.message
    assert "(3)" in mismatch.message
    assert "التصدير متاح" in mismatch.message


def test_missing_question_marks_uses_parts_total_without_missing_marks_warning() -> None:
    report = build_project_readiness_report(
        ProjectSession(
            questions=[
                _hierarchical_marks_question(question_marks=None),
            ],
        )
    )

    issue_codes = {issue.code for issue in report.issues}

    assert report.ready is True
    assert report.total_marks == 3
    assert "question_marks_inferred_from_parts" in issue_codes
    assert "missing_marks" not in issue_codes


def test_matching_question_marks_emits_no_consistency_warning() -> None:
    report = build_project_readiness_report(
        ProjectSession(
            questions=[
                _hierarchical_marks_question(question_marks=3),
            ],
        )
    )

    issue_codes = {issue.code for issue in report.issues}

    assert report.ready is True
    assert report.total_marks == 3
    assert "question_parts_marks_mismatch" not in issue_codes
    assert "question_marks_inferred_from_parts" not in issue_codes

