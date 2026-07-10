from fastapi.testclient import TestClient

from app.main import app
from app.models.project import GlossaryTerm, QuestionItem
from app.services.translation import translate_question_text, translate_questions_with_glossary

client = TestClient(app)


def test_translate_question_uses_exam_command_and_glossary():
    glossary = [
        GlossaryTerm(id="t-current", english_term="current", arabic_term="شدة التيار", subject="فيزياء"),
        GlossaryTerm(id="t-resistance", english_term="resistance", arabic_term="المقاومة", subject="فيزياء"),
    ]

    translated = translate_question_text(
        "Explain why the current decreases when the resistance increases. [2]",
        glossary,
    )

    assert translated == "فسّر لماذا تقل شدة التيار عندما تزداد المقاومة. [2]"


def test_translate_questions_skips_deleted_cards():
    questions = [
        QuestionItem(
            id="q-1",
            original_number="1",
            original_text="State the function of the cell membrane. [1]",
            translated_text="",
            marks=1,
            detected_marks=1,
            order_index=1,
        ),
        QuestionItem(
            id="q-2",
            original_number="2",
            original_text="Calculate the speed of a wave with frequency 50 Hz and wavelength 0.40 m. [2]",
            translated_text="old",
            marks=2,
            detected_marks=2,
            order_index=2,
            status="deleted",
        ),
    ]
    glossary = [GlossaryTerm(id="t-cell", english_term="cell membrane", arabic_term="غشاء الخلية", subject="أحياء")]

    translated_questions = translate_questions_with_glossary(questions, glossary)

    assert translated_questions[0].translated_text == "اذكر وظيفة غشاء الخلية. [1]"
    assert translated_questions[0].status == "needs_review"
    assert translated_questions[1].translated_text == "old"
    assert translated_questions[1].status == "deleted"


def test_translate_questions_endpoint_updates_project_cards():
    create_response = client.post("/api/projects")
    project_id = create_response.json()["id"]

    demo_response = client.post(f"/api/projects/{project_id}/demo-content")
    assert demo_response.status_code == 200

    response = client.post(f"/api/projects/{project_id}/translate-questions")

    assert response.status_code == 200
    project = response.json()
    assert project["current_step"] == "review"
    assert any("فسّر" in question["translated_text"] for question in project["questions"])
    assert all(
        question["status"] in {"needs_review", "deleted"}
        for question in project["questions"]
    )
