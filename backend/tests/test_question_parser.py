from fastapi.testclient import TestClient

from app.main import app
from app.services.question_parser import parse_questions_from_text
from tests.test_pdf_text_extraction import SAMPLE_TEXT_PDF


def test_parse_questions_from_numbered_text() -> None:
    text = """
    1. State the function of the cell membrane. [1]
    2 Explain why the current decreases when resistance increases. [2]
    3) Calculate the speed of a wave. (3 marks)
    """

    questions = parse_questions_from_text(text)

    assert len(questions) == 3
    assert questions[0].original_number == "1"
    assert questions[0].detected_marks == 1
    assert questions[1].original_number == "2"
    assert questions[1].marks == 2
    assert questions[2].original_number == "3"
    assert questions[2].marks == 3
    assert all(question.status == "needs_review" for question in questions)


def test_parse_questions_fallback_when_no_markers() -> None:
    questions = parse_questions_from_text("State the function of the cell membrane. [1]")

    assert len(questions) == 1
    assert questions[0].original_number == "1"
    assert questions[0].marks == 1
    assert "cell membrane" in questions[0].original_text


def test_parse_questions_endpoint_after_pdf_upload() -> None:
    client = TestClient(app)
    project_id = client.post("/api/projects", json={}).json()["id"]

    upload_response = client.post(
        f"/api/projects/{project_id}/upload-pdf",
        files={"file": ("sample.pdf", SAMPLE_TEXT_PDF, "application/pdf")},
    )
    assert upload_response.status_code == 200

    parse_response = client.post(f"/api/projects/{project_id}/parse-questions")

    assert parse_response.status_code == 200
    body = parse_response.json()
    assert body["current_step"] == "review"
    assert len(body["questions"]) >= 1
    assert body["questions"][0]["status"] == "needs_review"
    assert "cell membrane" in body["questions"][0]["original_text"]


def test_parse_questions_endpoint_requires_extracted_text() -> None:
    client = TestClient(app)
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(f"/api/projects/{project_id}/parse-questions")

    assert response.status_code == 400
