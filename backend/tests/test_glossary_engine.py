from fastapi.testclient import TestClient

from app.main import app
from app.models.project import QuestionItem
from app.services.glossary import extract_glossary_terms_from_questions


def test_extract_glossary_terms_from_questions_detects_known_science_terms() -> None:
    questions = [
        QuestionItem(
            id="q-1",
            original_number="1",
            original_text="Explain why the current decreases when resistance increases in a circuit. [2]",
            translated_text="",
            marks=2,
            detected_marks=2,
            status="needs_review",
            order_index=1,
        ),
        QuestionItem(
            id="q-2",
            original_number="2",
            original_text="State the function of the cell membrane. [1]",
            translated_text="",
            marks=1,
            detected_marks=1,
            status="needs_review",
            order_index=2,
        ),
    ]

    terms = extract_glossary_terms_from_questions(questions)
    english_terms = {term.english_term for term in terms}

    assert "current" in english_terms
    assert "resistance" in english_terms
    assert "circuit" in english_terms
    assert "cell membrane" in english_terms
    assert all(term.source == "detected" for term in terms)
    assert all(term.status == "needs_review" for term in terms)


def test_generate_glossary_endpoint_from_demo_questions() -> None:
    client = TestClient(app)
    project_id = client.post("/api/projects", json={}).json()["id"]
    client.post(f"/api/projects/{project_id}/demo-content")

    response = client.post(f"/api/projects/{project_id}/glossary/generate")

    assert response.status_code == 200
    body = response.json()
    assert body["current_step"] == "glossary"
    assert len(body["glossary"]) >= 4
    english_terms = {term["english_term"] for term in body["glossary"]}
    assert "cell membrane" in english_terms
    assert "current" in english_terms
    assert "rate of reaction" in english_terms
    assert all(term["source"] == "detected" for term in body["glossary"])


def test_generate_glossary_endpoint_requires_questions() -> None:
    client = TestClient(app)
    project_id = client.post("/api/projects", json={}).json()["id"]

    response = client.post(f"/api/projects/{project_id}/glossary/generate")

    assert response.status_code == 400
