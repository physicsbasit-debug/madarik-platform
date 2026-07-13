from fastapi.testclient import TestClient

from app.main import app
from app.models.project import GlossaryTerm, QuestionItem, QuestionPart
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


def test_translate_questions_translates_parts_independently():
    question = QuestionItem(
        id="q-parts",
        original_number="4",
        original_text="Multipart question raw text",
        translated_text="",
        order_index=1,
        parts=[
            QuestionPart(
                id="part-b",
                label="(b)",
                original_text="Calculate the speed of a wave with frequency 50 Hz and wavelength 0.40 m. [2]",
                marks=2,
                order_index=2,
            ),
            QuestionPart(
                id="part-a",
                label="(a)",
                original_text="State the function of the cell membrane. [1]",
                marks=1,
                order_index=1,
            ),
        ],
    )
    glossary = [
        GlossaryTerm(
            id="t-cell",
            english_term="cell membrane",
            arabic_term="غشاء الخلية",
            subject="أحياء",
        )
    ]

    translated_question = translate_questions_with_glossary(
        [question],
        glossary,
    )[0]

    assert [part.label for part in translated_question.parts] == ["(a)", "(b)"]
    assert translated_question.parts[0].translated_text == "اذكر وظيفة غشاء الخلية. [1]"
    assert "احسب سرعة موجة" in translated_question.parts[1].translated_text
    assert translated_question.parts[0].marks == 1
    assert translated_question.parts[1].marks == 2
    assert translated_question.translated_text.startswith("(a) اذكر وظيفة غشاء الخلية")
    assert "(b) احسب سرعة موجة" in translated_question.translated_text
    assert "تمت ترجمة أجزاء السؤال بصورة مستقلة (العدد: 2)" in (
        translated_question.review_notes or ""
    )


def test_translate_questions_preserves_blank_manual_part():
    question = QuestionItem(
        id="q-blank-part",
        original_number="5",
        original_text="Multipart question",
        translated_text="",
        order_index=1,
        parts=[
            QuestionPart(
                id="part-empty",
                label="(a)",
                original_text="",
                translated_text="",
                marks=None,
                order_index=1,
            )
        ],
    )

    translated_question = translate_questions_with_glossary([question], [])[0]

    assert translated_question.parts[0].translated_text == ""
    assert translated_question.translated_text


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


def test_translate_questions_endpoint_updates_structured_parts():
    project_id = client.post("/api/projects").json()["id"]
    project = client.post(f"/api/projects/{project_id}/demo-content").json()
    question_id = project["questions"][0]["id"]

    patch_response = client.patch(
        f"/api/projects/{project_id}/questions/{question_id}",
        json={
            "parts": [
                {
                    "id": "part-a",
                    "label": "(a)",
                    "original_text": "State the function of the cell membrane. [1]",
                    "translated_text": "",
                    "marks": 1,
                    "order_index": 1,
                },
                {
                    "id": "part-b",
                    "label": "(b)",
                    "original_text": "Explain why the current decreases when the resistance increases. [2]",
                    "translated_text": "",
                    "marks": 2,
                    "order_index": 2,
                },
            ]
        },
    )
    assert patch_response.status_code == 200

    response = client.post(f"/api/projects/{project_id}/translate-questions")

    assert response.status_code == 200
    translated_question = next(
        question
        for question in response.json()["questions"]
        if question["id"] == question_id
    )
    assert translated_question["parts"][0]["translated_text"].startswith("اذكر")
    assert translated_question["parts"][1]["translated_text"].startswith("فسّر")
    assert "(a)" in translated_question["translated_text"]
    assert "(b)" in translated_question["translated_text"]
