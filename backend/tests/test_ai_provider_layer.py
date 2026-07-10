from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.models.project import GlossaryTerm
from app.services.ai_provider import (
    build_translation_messages,
    get_ai_provider_status,
    translate_with_optional_external_provider,
)

client = TestClient(app)


def test_ai_provider_status_defaults_to_mock(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "mock")
    monkeypatch.setattr(settings, "ai_api_key", "")
    monkeypatch.setattr(settings, "ai_model", "")

    status = get_ai_provider_status()

    assert status["provider"] == "mock"
    assert status["configured"] is False
    assert status["fallback"] == "mock"


def test_translation_provider_status_endpoint_does_not_expose_secret(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "openai")
    monkeypatch.setattr(settings, "ai_api_key", "secret-value-that-must-not-leak")
    monkeypatch.setattr(settings, "ai_model", "test-model")

    response = client.get("/api/projects/translation-provider/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "openai"
    assert payload["configured"] is True
    assert payload["model"] == "test-model"
    assert "secret-value-that-must-not-leak" not in str(payload)


def test_build_translation_messages_includes_glossary_and_commands():
    glossary = [GlossaryTerm(id="t-force", english_term="resultant force", arabic_term="القوة المحصلة")]

    messages = build_translation_messages("State the resultant force. [1]", glossary)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "القوة المحصلة" in messages[1]["content"]
    assert "State = اذكر" in messages[1]["content"]


def test_provider_falls_back_when_openai_is_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "openai")
    monkeypatch.setattr(settings, "ai_api_key", "")
    monkeypatch.setattr(settings, "ai_model", "")

    result = translate_with_optional_external_provider(
        original_text="Explain why the current decreases. [2]",
        glossary=[],
        fallback_translation="فسّر لماذا تقل شدة التيار. [2]",
    )

    assert result.translated_text == "فسّر لماذا تقل شدة التيار. [2]"
    assert result.provider == "mock"
    assert result.used_external_provider is False
    assert "fallback" in result.note



def test_provider_status_reports_hardening_fields(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "openai-compatible")
    monkeypatch.setattr(settings, "ai_api_key", "secret-value-that-must-not-leak")
    monkeypatch.setattr(settings, "ai_model", "test-model")
    monkeypatch.setattr(settings, "ai_external_enabled", True)
    monkeypatch.setattr(settings, "ai_max_input_chars", 2400)
    monkeypatch.setattr(settings, "ai_temperature", 0.2)

    status = get_ai_provider_status()

    assert status["provider"] == "openai-compatible"
    assert status["configured"] is True
    assert status["ready"] is True
    assert status["reason"] == "ready"
    assert status["max_input_chars"] == 2400
    assert status["temperature"] == 0.2
    assert "openai-compatible" in status["supported_providers"]
    assert "secret-value-that-must-not-leak" not in str(status)


def test_provider_falls_back_when_external_disabled(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "openai")
    monkeypatch.setattr(settings, "ai_api_key", "secret")
    monkeypatch.setattr(settings, "ai_model", "test-model")
    monkeypatch.setattr(settings, "ai_external_enabled", False)

    result = translate_with_optional_external_provider(
        original_text="State the function of the cell membrane. [1]",
        glossary=[],
        fallback_translation="اذكر وظيفة غشاء الخلية. [1]",
    )

    assert result.provider == "mock"
    assert result.used_external_provider is False
    assert "تعطيل" in result.note


def test_provider_falls_back_when_input_too_long(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", "openai")
    monkeypatch.setattr(settings, "ai_api_key", "secret")
    monkeypatch.setattr(settings, "ai_model", "test-model")
    monkeypatch.setattr(settings, "ai_external_enabled", True)
    monkeypatch.setattr(settings, "ai_max_input_chars", 10)

    result = translate_with_optional_external_provider(
        original_text="Explain why the current decreases when resistance increases. [2]",
        glossary=[],
        fallback_translation="فسّر لماذا تقل شدة التيار. [2]",
    )

    assert result.provider == "mock"
    assert result.used_external_provider is False
    assert "أطول من الحد" in result.note
