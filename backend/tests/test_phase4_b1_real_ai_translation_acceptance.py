from __future__ import annotations

import httpx

from app.core.config import settings
from app.models.project import (
    FullExamTranslationAcceptanceStatus,
    QuestionItem,
    QuestionStatus,
    TranslationBatchStatus,
    TranslationBatchSummary,
    TranslationItemOutcome,
    TranslationOutcomeStatus,
)
from app.services.ai_provider import (
    TranslationProviderResult,
    get_ai_provider_status,
    translate_with_optional_external_provider,
    validate_arabic_translation_quality,
)
from app.services.full_exam_translation import build_full_exam_translation_report


def _configure_external_provider(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ai_provider", "openai")
    monkeypatch.setattr(settings, "ai_api_key", "secret-never-print")
    monkeypatch.setattr(settings, "ai_model", "test-model")
    monkeypatch.setattr(settings, "ai_external_enabled", True)
    monkeypatch.setattr(settings, "ai_max_input_chars", 4000)


def _response(text: str) -> httpx.Response:
    return httpx.Response(
        200,
        request=httpx.Request("POST", "https://provider.example/test"),
        json={"text": text},
    )


def _extract(payload: dict[str, object]) -> str:
    value = payload.get("text")
    return value if isinstance(value, str) else ""


def _question(translated_text: str, *, status: QuestionStatus = QuestionStatus.approved) -> QuestionItem:
    return QuestionItem(
        id="q-1",
        original_number="1",
        original_text="Explain why the current decreases. [2]",
        translated_text=translated_text,
        status=status,
        order_index=1,
    )


def test_phase4_b1_quality_gate_accepts_arabic_with_scientific_symbols() -> None:
    result = validate_arabic_translation_quality(
        "Calculate V = IR when I = 2 A. [2]",
        "احسب V = IR عندما تكون I = 2 A. [2]",
    )

    assert result.is_compliant is True
    assert result.unexplained_latin_words == ()
    assert result.arabic_letter_ratio == 1.0


def test_phase4_b1_quality_gate_rejects_mixed_english_prose() -> None:
    result = validate_arabic_translation_quality(
        "Explain why the current decreases. [2]",
        "فسّر why the current decreases. [2]",
    )

    assert result.is_compliant is False
    assert "current" in result.unexplained_latin_words
    assert result.issues


def test_phase4_b1_mixed_first_response_is_corrected_once(monkeypatch) -> None:
    _configure_external_provider(monkeypatch)
    responses = iter(
        [
            "فسّر why the current decreases. [2]",
            "فسّر لماذا تقل شدة التيار. [2]",
        ]
    )

    def fake_post(*args, **kwargs):
        return _response(next(responses)), _extract, "mocked Responses API"

    monkeypatch.setattr(
        "app.services.ai_provider._post_provider_request",
        fake_post,
    )

    result = translate_with_optional_external_provider(
        original_text="Explain why the current decreases. [2]",
        glossary=[],
        fallback_translation="فسّر why the current decreases. [2]",
    )

    assert result.outcome == TranslationOutcomeStatus.corrected_success
    assert result.used_external_provider is True
    assert result.translated_text == "فسّر لماذا تقل شدة التيار. [2]"
    assert "جودة العربية" in result.note


def test_phase4_b1_persistent_mixed_output_falls_back(monkeypatch) -> None:
    _configure_external_provider(monkeypatch)

    def fake_post(*args, **kwargs):
        return _response("Explain why the current decreases. [2]"), _extract, "mocked"

    monkeypatch.setattr(
        "app.services.ai_provider._post_provider_request",
        fake_post,
    )

    result = translate_with_optional_external_provider(
        original_text="Explain why the current decreases. [2]",
        glossary=[],
        fallback_translation="فسّر why the current decreases. [2]",
    )

    assert result.outcome == TranslationOutcomeStatus.local_fallback
    assert result.used_external_provider is False
    assert result.provider == "mock"
    assert "جودة العربية" in result.note


def test_phase4_b1_fallback_cannot_be_accepted_after_teacher_approval() -> None:
    question = _question("فسّر لماذا تقل شدة التيار. [2]")
    summary = TranslationBatchSummary(
        status=TranslationBatchStatus.completed_with_fallbacks,
        total_questions=1,
        active_questions=1,
        total_items=1,
        local_fallback_count=1,
        urgent_review_count=1,
        items=[
            TranslationItemOutcome(
                question_id=question.id,
                question_number=question.original_number,
                status=TranslationOutcomeStatus.local_fallback,
                provider="mock",
                urgent_review=True,
                message="fallback",
            )
        ],
    )

    report = build_full_exam_translation_report([question], [], summary)

    assert report.status == FullExamTranslationAcceptanceStatus.needs_review
    assert report.accepted_questions == 0
    assert report.urgent_review_items == 1
    assert any(
        check.code == "external_translation_only" and not check.passed
        for check in report.checks
    )


def test_phase4_b1_mixed_manual_translation_cannot_be_accepted() -> None:
    question = _question("فسّر why the current decreases. [2]")
    summary = TranslationBatchSummary(
        status=TranslationBatchStatus.completed,
        total_questions=1,
        active_questions=1,
        total_items=1,
        external_success_count=1,
        items=[
            TranslationItemOutcome(
                question_id=question.id,
                question_number=question.original_number,
                status=TranslationOutcomeStatus.external_success,
                provider="openai",
                used_external_provider=True,
            )
        ],
    )

    report = build_full_exam_translation_report([question], [], summary)

    assert report.status == FullExamTranslationAcceptanceStatus.needs_review
    assert report.language_quality_violation_count == 1
    assert report.questions[0].language_quality_violation_count == 1


def test_phase4_b1_clean_external_translation_can_be_accepted() -> None:
    question = _question("فسّر لماذا تقل شدة التيار. [2]")
    summary = TranslationBatchSummary(
        status=TranslationBatchStatus.completed,
        total_questions=1,
        active_questions=1,
        total_items=1,
        external_success_count=1,
        items=[
            TranslationItemOutcome(
                question_id=question.id,
                question_number=question.original_number,
                status=TranslationOutcomeStatus.external_success,
                provider="openai",
                used_external_provider=True,
            )
        ],
    )

    report = build_full_exam_translation_report([question], [], summary)

    assert report.status == FullExamTranslationAcceptanceStatus.accepted
    assert report.accepted_questions == 1
    assert report.language_quality_violation_count == 0




def test_phase4_b1_gemini_requires_explicit_model(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ai_provider", "gemini")
    monkeypatch.setattr(settings, "ai_api_key", "")
    monkeypatch.setattr(settings, "ai_model", "")
    monkeypatch.setattr(settings, "gemini_api_key", "secret")
    monkeypatch.setattr(settings, "gemini_model", "")
    monkeypatch.setattr(settings, "ai_external_enabled", True)

    status = get_ai_provider_status()

    assert status["configured"] is False
    assert status["ready"] is False
    assert status["reason"] == "missing_credentials"
    assert status["model"] == ""


def test_phase4_b1_storage_control_is_reported_without_claiming_gemini_store_flag(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ai_provider", "gemini")
    monkeypatch.setattr(settings, "ai_api_key", "")
    monkeypatch.setattr(settings, "ai_model", "")
    monkeypatch.setattr(settings, "gemini_api_key", "secret")
    monkeypatch.setattr(settings, "gemini_model", "test-gemini-model")
    monkeypatch.setattr(settings, "ai_external_enabled", True)

    status = get_ai_provider_status()

    assert status["provider_storage_control"] == "not_available"

def test_phase4_b1_provider_status_declares_acceptance_guard_without_secret(monkeypatch) -> None:
    _configure_external_provider(monkeypatch)

    status = get_ai_provider_status()

    assert status["acceptance_guard"] == "arabic_language_quality"
    assert status["fallback_can_be_accepted"] is False
    assert "secret-never-print" not in str(status)
