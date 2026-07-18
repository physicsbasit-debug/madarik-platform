from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.models.project import (
    FullExamIntakeReport,
    FullExamIntakeStatus,
    FullExamQuestionSpan,
    FullExamTranslationAcceptanceStatus,
    FullExamTranslationQuestionStatus,
    GlossaryTerm,
    ProjectMetadata,
    QuestionItem,
    QuestionStatus,
    TranslationBatchStatus,
    TranslationBatchSummary,
    TranslationItemOutcome,
    TranslationItemType,
    TranslationOutcomeStatus,
)
from app.services.ai_provider import TranslationProviderResult
from app.services.full_exam_translation import (
    build_full_exam_translation_report,
)
from app.services.session_store import project_store
from app.services.translation import (
    merge_translation_retry_summary,
    translate_questions_batch_with_glossary,
)


client = TestClient(app)


def _question(
    question_id: str,
    number: str,
    original_text: str,
    *,
    translated_text: str = "",
    status: QuestionStatus = QuestionStatus.approved,
    pages: list[int] | None = None,
    linked_assets: list[str] | None = None,
) -> QuestionItem:
    return QuestionItem(
        id=question_id,
        original_number=number,
        original_text=original_text,
        translated_text=translated_text,
        status=status,
        order_index=int(number),
        source_page_numbers=pages or [],
        source_page_start=(pages or [None])[0],
        source_page_end=(pages or [None])[-1],
        linked_layout_asset_ids=linked_assets or [],
    )


def _intake_report() -> FullExamIntakeReport:
    return FullExamIntakeReport(
        status=FullExamIntakeStatus.accepted,
        page_count=3,
        content_page_count=3,
        question_page_count=2,
        detected_question_count=2,
        detected_question_numbers=["1", "2"],
        question_spans=[
            FullExamQuestionSpan(
                question_number="1",
                page_numbers=[2],
                page_start=2,
                page_end=2,
                detected_total_marks=1,
                linked_layout_asset_count=1,
            ),
            FullExamQuestionSpan(
                question_number="2",
                page_numbers=[3],
                page_start=3,
                page_end=3,
                detected_total_marks=1,
                linked_layout_asset_count=1,
            ),
        ],
    )


def test_phase4_a6b_untranslated_full_paper_is_incomplete():
    questions = [
        _question(
            "q-1",
            "1",
            "State the force. [1]",
            pages=[2],
            linked_assets=["page-2"],
        ),
        _question(
            "q-2",
            "2",
            "State the energy. [1]",
            pages=[3],
            linked_assets=["page-3"],
        ),
    ]

    report = build_full_exam_translation_report(
        questions,
        [],
        intake_report=_intake_report(),
    )

    assert report.status == FullExamTranslationAcceptanceStatus.incomplete
    assert report.completion_percent == 0
    assert report.untranslated_questions == 2
    assert report.failed_questions == 0
    assert all(
        item.status
        == FullExamTranslationQuestionStatus.untranslated
        for item in report.questions
    )


def test_phase4_a6b_completed_translation_needs_teacher_review_then_accepts(
    monkeypatch,
):
    def fake_provider(original_text, glossary, *, context=None):
        translated = (
            "اذكر القوة. [1]"
            if "force" in original_text
            else "اذكر الطاقة. [1]"
        )
        return TranslationProviderResult(
            translated_text=translated,
            provider="fixture",
            used_external_provider=True,
            outcome=TranslationOutcomeStatus.external_success,
        )

    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        fake_provider,
    )

    questions = [
        _question(
            "q-1",
            "1",
            "State the force. [1]",
            pages=[2],
            linked_assets=["page-2"],
        ),
        _question(
            "q-2",
            "2",
            "State the energy. [1]",
            pages=[3],
            linked_assets=["page-3"],
        ),
    ]
    batch = translate_questions_batch_with_glossary(
        questions,
        [],
        ProjectMetadata(subject="فيزياء"),
    )

    review_report = build_full_exam_translation_report(
        batch.questions,
        [],
        batch.summary,
        _intake_report(),
    )

    assert review_report.status == (
        FullExamTranslationAcceptanceStatus.needs_review
    )
    assert review_report.completion_percent == 100
    assert review_report.translated_questions == 2
    assert review_report.accepted_questions == 0
    assert review_report.needs_review_questions == 2
    assert review_report.glossary_violation_count == 0
    assert review_report.fidelity_violation_count == 0

    approved_questions = [
        question.model_copy(
            update={"status": QuestionStatus.approved}
        )
        for question in batch.questions
    ]
    accepted_report = build_full_exam_translation_report(
        approved_questions,
        [],
        batch.summary,
        _intake_report(),
    )

    assert accepted_report.status == (
        FullExamTranslationAcceptanceStatus.accepted
    )
    assert accepted_report.accepted_questions == 2
    assert all(check.passed for check in accepted_report.checks)


def test_phase4_a6b_detects_glossary_and_fidelity_violations():
    question = _question(
        "q-1",
        "1",
        "State the current when V = 2 V. [1]",
        translated_text="اذكر القيمة.",
        status=QuestionStatus.approved,
    )
    glossary = [
        GlossaryTerm(
            id="term-current",
            english_term="current",
            arabic_term="شدة التيار",
            subject="فيزياء",
        )
    ]

    report = build_full_exam_translation_report(
        [question],
        glossary,
    )

    assert report.status == (
        FullExamTranslationAcceptanceStatus.needs_review
    )
    assert report.glossary_violation_count == 1
    assert report.fidelity_violation_count > 0
    assert report.questions[0].status == (
        FullExamTranslationQuestionStatus.needs_review
    )


def test_phase4_a6b_retry_replaces_failed_question_outcomes(monkeypatch):
    question = _question(
        "q-retry",
        "1",
        "State the force. [1]",
        translated_text="ترجمة محفوظة. [1]",
        status=QuestionStatus.needs_review,
    )
    failed_summary = TranslationBatchSummary(
        status=TranslationBatchStatus.completed_with_failures,
        total_questions=1,
        active_questions=1,
        total_items=1,
        failed_safely_count=1,
        urgent_review_count=1,
        items=[
            TranslationItemOutcome(
                question_id=question.id,
                question_number="1",
                item_type=TranslationItemType.question,
                status=TranslationOutcomeStatus.failed_safely,
                urgent_review=True,
            )
        ],
    )
    failed_report = build_full_exam_translation_report(
        [question],
        [],
        failed_summary,
    )
    assert failed_report.status == (
        FullExamTranslationAcceptanceStatus.failed
    )

    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        lambda *args, **kwargs: TranslationProviderResult(
            translated_text="اذكر القوة. [1]",
            provider="fixture",
            used_external_provider=True,
            outcome=TranslationOutcomeStatus.external_success,
        ),
    )
    retry_result = translate_questions_batch_with_glossary(
        [question],
        [],
    )
    retried_question = retry_result.questions[0]
    merged_summary = merge_translation_retry_summary(
        [retried_question],
        failed_summary,
        retry_result,
        question.id,
    )
    retried_report = build_full_exam_translation_report(
        [retried_question],
        [],
        merged_summary,
    )

    assert merged_summary.failed_safely_count == 0
    assert merged_summary.external_success_count == 1
    assert retried_report.failed_questions == 0
    assert retried_report.completion_percent == 100
    assert retried_report.status == (
        FullExamTranslationAcceptanceStatus.needs_review
    )


def test_phase4_a6b_api_translates_retries_and_accepts_full_paper(
    monkeypatch,
):
    project_id = client.post("/api/projects").json()["id"]
    questions = [
        _question("q-1", "1", "State the force. [1]"),
        _question("q-2", "2", "State the energy. [1]"),
    ]
    project_store.set_parsed_questions(project_id, questions)

    def first_provider(original_text, glossary, *, context=None):
        return TranslationProviderResult(
            translated_text=(
                "اذكر القوة. [1]"
                if "force" in original_text
                else "اذكر الطاقة. [1]"
            ),
            provider="fixture",
            used_external_provider=True,
            outcome=TranslationOutcomeStatus.external_success,
        )

    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        first_provider,
    )

    translated_response = client.post(
        f"/api/projects/{project_id}/translate-questions"
    )
    assert translated_response.status_code == 200
    translated_project = translated_response.json()
    report = translated_project["full_exam_translation_report"]
    assert report["completion_percent"] == 100
    assert report["status"] == "needs_review"

    q1_before = translated_project["questions"][0]["translated_text"]
    q2_before = translated_project["questions"][1]["translated_text"]

    monkeypatch.setattr(
        "app.services.translation._translate_text_with_provider",
        lambda *args, **kwargs: TranslationProviderResult(
            translated_text="إعادة ترجمة السؤال. [1]",
            provider="fixture-retry",
            used_external_provider=True,
            outcome=TranslationOutcomeStatus.external_success,
        ),
    )

    retry_response = client.post(
        f"/api/projects/{project_id}/questions/q-2/retry-translation"
    )
    assert retry_response.status_code == 200
    retried_project = retry_response.json()
    assert retried_project["questions"][0]["translated_text"] == q1_before
    assert retried_project["questions"][1]["translated_text"] != q2_before
    assert (
        retried_project["translation_batch_summary"][
            "external_success_count"
        ]
        == 2
    )

    approve_response = client.post(
        f"/api/projects/{project_id}/questions/bulk-status",
        json={"status": "approved", "include_deleted": False},
    )
    assert approve_response.status_code == 200
    accepted_project = approve_response.json()
    assert (
        accepted_project["full_exam_translation_report"]["status"]
        == "accepted"
    )
    assert (
        accepted_project["full_exam_translation_report"][
            "accepted_questions"
        ]
        == 2
    )

    client.delete(f"/api/projects/{project_id}")
