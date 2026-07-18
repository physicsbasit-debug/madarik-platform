from fastapi.testclient import TestClient

from app.main import app
from app.models.project import (
    GlossaryTerm,
    GlossaryTermStatus,
    ProjectMetadata,
    QuestionItem,
    QuestionPart,
)
from app.services.ai_provider import TranslationProviderResult
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


def test_translate_questions_preserves_hierarchy_and_empty_parent_heading():
    question = QuestionItem(
        id="q-hierarchy",
        original_number="5",
        original_text="Hierarchical multipart question",
        translated_text="",
        order_index=1,
        parts=[
            QuestionPart(
                id="part-e",
                label="(e)",
                original_text="",
                translated_text="",
                marks=None,
                order_index=1,
            ),
            QuestionPart(
                id="part-i",
                label="(i)",
                original_text="State the function of the cell membrane. [1]",
                translated_text="",
                marks=1,
                parent_id="part-e",
                order_index=2,
            ),
        ],
    )
    glossary = [
        GlossaryTerm(
            id="t-cell-hierarchy",
            english_term="cell membrane",
            arabic_term="غشاء الخلية",
            subject="أحياء",
        )
    ]

    translated_question = translate_questions_with_glossary(
        [question],
        glossary,
    )[0]

    assert translated_question.parts[0].parent_id is None
    assert translated_question.parts[1].parent_id == "part-e"
    assert translated_question.parts[1].translated_text.startswith("اذكر")
    assert translated_question.translated_text.splitlines()[0] == "(e)"
    assert translated_question.translated_text.splitlines()[1].startswith(
        "  (i) اذكر"
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
                    "parent_id": "part-a",
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
    assert translated_question["parts"][1]["parent_id"] == "part-a"
    assert "(a)" in translated_question["translated_text"]
    assert "(b)" in translated_question["translated_text"]


def test_translate_questions_passes_project_and_parent_context(monkeypatch):
    captured_contexts = []

    def fake_translate_with_provider(
        original_text,
        glossary,
        fallback_translation,
        context=None,
    ):
        captured_contexts.append(context)
        return TranslationProviderResult(
            translated_text=f"ترجمة: {original_text}",
            provider="openai",
            used_external_provider=True,
            note="",
        )

    monkeypatch.setattr(
        "app.services.translation.translate_with_optional_external_provider",
        fake_translate_with_provider,
    )

    question = QuestionItem(
        id="q-context",
        original_number="7",
        original_text="A circuit contains a cell and a resistor.",
        translated_text="",
        order_index=1,
        parts=[
            QuestionPart(
                id="part-a",
                label="(a)",
                original_text="The current in the circuit is 2 A.",
                marks=1,
                order_index=1,
            ),
            QuestionPart(
                id="part-i",
                label="(i)",
                original_text="Calculate the potential difference. [2]",
                marks=2,
                parent_id="part-a",
                order_index=2,
            ),
        ],
    )
    metadata = ProjectMetadata(
        subject="فيزياء",
        grade="الصف العاشر",
        semester="الفصل الدراسي الثاني",
    )

    translated = translate_questions_with_glossary(
        [question],
        [],
        metadata,
    )[0]

    assert len(captured_contexts) == 2
    parent_context, child_context = captured_contexts
    assert parent_context.subject == "فيزياء"
    assert parent_context.grade == "الصف العاشر"
    assert parent_context.semester == "الفصل الدراسي الثاني"
    assert parent_context.question_number == "7"
    assert parent_context.part_label == "(a)"
    assert parent_context.question_stem == question.original_text
    assert parent_context.parent_part_text == ""
    assert child_context.part_label == "(i)"
    assert child_context.parent_part_text == "The current in the circuit is 2 A."
    assert translated.parts[1].parent_id == "part-a"
    assert translated.translated_text.splitlines()[1].startswith("  (i) ترجمة:")
    assert "Phase 4-A5" in (translated.review_notes or "")


def test_phase4_a3_local_fallback_uses_only_approved_glossary_terms():
    source = "State the momentum. [1]"
    approved_translation = translate_question_text(
        source,
        [
            GlossaryTerm(
                id="momentum-approved",
                english_term="momentum",
                arabic_term="كمية الحركة",
                status=GlossaryTermStatus.approved,
            )
        ],
    )
    review_translation = translate_question_text(
        source,
        [
            GlossaryTerm(
                id="momentum-review",
                english_term="momentum",
                arabic_term="كمية الحركة",
                status=GlossaryTermStatus.needs_review,
            )
        ],
    )

    assert "كمية الحركة" in approved_translation
    assert "كمية الحركة" not in review_translation


def test_phase4_a4_review_note_reports_scientific_fidelity_guard(monkeypatch):
    def fake_translate_with_provider(
        original_text,
        glossary,
        fallback_translation,
        context=None,
    ):
        return TranslationProviderResult(
            translated_text="احسب V = IR عندما تكون I = 2 A. [2]",
            provider="gemini",
            used_external_provider=True,
            note=(
                "فحص القاموس: لا توجد مصطلحات معتمدة مطابقة في النص المصدر. "
                "فحص الأمان العلمي: التزم الناتج بجميع عناصر المحتوى العلمي المحمي."
            ),
        )

    monkeypatch.setattr(
        "app.services.translation.translate_with_optional_external_provider",
        fake_translate_with_provider,
    )

    question = QuestionItem(
        id="q-a4-note",
        original_number="1",
        original_text="Calculate V = IR when I = 2 A. [2]",
        translated_text="",
        order_index=1,
    )
    translated = translate_questions_with_glossary([question], [])[0]

    assert "Phase 4-A5" in (translated.review_notes or "")
    assert "حارس سلامة المحتوى العلمي" in (translated.review_notes or "")
    assert "دفعة معزولة العناصر" in (translated.review_notes or "")
    assert "فحص الأمان العلمي" in (translated.review_notes or "")
