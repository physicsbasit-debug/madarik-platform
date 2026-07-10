from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.models.project import GlossaryTerm


SUPPORTED_EXTERNAL_PROVIDERS = {"openai", "openai-compatible"}


@dataclass(frozen=True)
class TranslationProviderResult:
    """Result returned by the optional external AI provider layer."""

    translated_text: str
    provider: str
    used_external_provider: bool
    note: str = ""


@dataclass(frozen=True)
class ProviderDecision:
    """Explains whether external AI can be used for one request."""

    provider: str
    can_use_external: bool
    reason: str
    fallback: str


EXAM_COMMAND_GUIDE = {
    "State": "اذكر",
    "Describe": "صف",
    "Explain": "فسّر",
    "Calculate": "احسب",
    "Compare": "قارن",
    "Suggest": "اقترح",
    "Determine": "حدّد",
    "Identify": "حدّد / عرّف حسب السياق",
    "Give a reason": "أعط سببًا",
    "Complete": "أكمل",
    "Label": "سمِّ",
    "Draw": "ارسم",
    "Predict": "تنبّأ",
    "Justify": "برّر",
    "Evaluate": "قيّم",
}


def normalise_provider_name(provider: str) -> str:
    value = provider.strip().lower()
    if value in {"", "mock", "none", "fallback"}:
        return "mock"
    if value in {"openai", "openai-compatible", "openai_compatible"}:
        return "openai-compatible" if value != "openai" else "openai"
    return value


def evaluate_provider_decision(input_text: str = "") -> ProviderDecision:
    """Return a safe decision for whether external AI may be used."""

    provider = normalise_provider_name(settings.ai_provider)
    configured = bool(settings.ai_api_key.strip() and settings.ai_model.strip())
    input_length = len(input_text or "")

    if provider == "mock":
        return ProviderDecision(provider="mock", can_use_external=False, reason="provider_mock", fallback="mock")

    if provider not in SUPPORTED_EXTERNAL_PROVIDERS:
        return ProviderDecision(provider=provider, can_use_external=False, reason="unsupported_provider", fallback="mock")

    if not settings.ai_external_enabled:
        return ProviderDecision(provider=provider, can_use_external=False, reason="external_disabled", fallback="mock")

    if not configured:
        return ProviderDecision(provider=provider, can_use_external=False, reason="missing_credentials", fallback="mock")

    if input_length > settings.ai_max_input_chars:
        return ProviderDecision(provider=provider, can_use_external=False, reason="input_too_long", fallback="mock")

    return ProviderDecision(provider=provider, can_use_external=True, reason="ready", fallback="none")


def get_ai_provider_status() -> dict[str, object]:
    """Return safe provider metadata for UI/tests without exposing secrets."""

    decision = evaluate_provider_decision()
    configured = bool(settings.ai_api_key.strip() and settings.ai_model.strip())
    provider = normalise_provider_name(settings.ai_provider)
    return {
        "provider": provider,
        "configured": configured if provider != "mock" else False,
        "external_enabled": settings.ai_external_enabled,
        "ready": decision.can_use_external,
        "reason": decision.reason,
        "model": settings.ai_model if provider != "mock" and settings.ai_model else "",
        "base_url_configured": bool(settings.ai_base_url.strip()) if provider != "mock" else False,
        "timeout_seconds": settings.ai_timeout_seconds,
        "max_input_chars": settings.ai_max_input_chars,
        "temperature": settings.ai_temperature,
        "supported_providers": sorted(SUPPORTED_EXTERNAL_PROVIDERS | {"mock"}),
        "fallback": decision.fallback,
    }


def build_translation_messages(original_text: str, glossary: list[GlossaryTerm]) -> list[dict[str, str]]:
    """Build a strict, review-first prompt for external AI translation."""

    glossary_lines = []
    for term in glossary:
        english = term.english_term.strip()
        arabic = term.arabic_term.strip()
        if english and arabic:
            glossary_lines.append(f"- {english} = {arabic}")

    command_lines = [f"- {english} = {arabic}" for english, arabic in EXAM_COMMAND_GUIDE.items()]
    glossary_text = "\n".join(glossary_lines) if glossary_lines else "لا يوجد قاموس معتمد لهذه الورقة."
    command_text = "\n".join(command_lines)

    system_prompt = (
        "أنت مترجم تربوي متخصص في أسئلة الاختبارات العلمية. "
        "ترجم السؤال إلى عربية فصحى تعليمية مباشرة مناسبة لطلبة سلطنة عمان. "
        "لا تضف شرحًا، ولا نموذج إجابة، ولا تلميحات. "
        "حافظ على معنى السؤال ونوع الأمر الامتحاني والرموز والوحدات والدرجات كما هي. "
        "أعد الترجمة العربية فقط دون مقدمات."
    )
    user_prompt = (
        "قاموس أوامر السؤال المعتمد:\n"
        f"{command_text}\n\n"
        "قاموس مصطلحات الورقة المعتمد:\n"
        f"{glossary_text}\n\n"
        "السؤال المطلوب ترجمته:\n"
        f"{original_text.strip()}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _extract_openai_chat_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return ""
    message = first_choice.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    return content.strip() if isinstance(content, str) else ""


def _chat_completions_url() -> str:
    return f"{settings.ai_base_url.rstrip('/')}/chat/completions"


def _fallback_result(fallback_translation: str, provider: str, note: str) -> TranslationProviderResult:
    return TranslationProviderResult(
        translated_text=fallback_translation,
        provider="mock",
        used_external_provider=False,
        note=note if note else f"تعذر استخدام المزود {provider}؛ تم استخدام fallback.",
    )


def translate_with_optional_external_provider(
    original_text: str,
    glossary: list[GlossaryTerm],
    fallback_translation: str,
) -> TranslationProviderResult:
    """Use an optional external provider when configured; otherwise return fallback.

    External provider failures never break the user flow; the teacher still gets
    a reviewable draft. Humanity may insist on remote APIs, but the lesson here
    is not letting them take the whole app down with them.
    """

    decision = evaluate_provider_decision(original_text)
    if not decision.can_use_external:
        reason_notes = {
            "provider_mock": "استخدمت الترجمة التجريبية لأن مزود الذكاء الاصطناعي غير مفعل.",
            "unsupported_provider": f"مزود الذكاء الاصطناعي '{decision.provider}' غير مدعوم؛ تم استخدام fallback.",
            "external_disabled": "تم تعطيل الاتصال الخارجي بالذكاء الاصطناعي عبر الإعدادات؛ تم استخدام fallback.",
            "missing_credentials": "لم يتم ضبط مفتاح ونموذج مزود الذكاء الاصطناعي؛ تم استخدام fallback.",
            "input_too_long": "نص السؤال أطول من الحد المسموح للإرسال الخارجي؛ تم استخدام fallback.",
        }
        return _fallback_result(fallback_translation, decision.provider, reason_notes.get(decision.reason, ""))

    try:
        response = httpx.post(
            _chat_completions_url(),
            headers={
                "Authorization": f"Bearer {settings.ai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.ai_model,
                "messages": build_translation_messages(original_text, glossary),
                "temperature": settings.ai_temperature,
            },
            timeout=settings.ai_timeout_seconds,
        )
        response.raise_for_status()
        translated_text = _extract_openai_chat_content(response.json())
        if translated_text:
            return TranslationProviderResult(
                translated_text=translated_text,
                provider=decision.provider,
                used_external_provider=True,
                note="تم توليد الترجمة عبر مزود ذكاء اصطناعي خارجي، وتبقى قابلة للمراجعة.",
            )
    except httpx.TimeoutException:
        return _fallback_result(
            fallback_translation,
            decision.provider,
            "انتهت مهلة الاتصال بمزود الذكاء الاصطناعي؛ تم استخدام fallback.",
        )
    except httpx.HTTPStatusError as exc:
        return _fallback_result(
            fallback_translation,
            decision.provider,
            f"رفض مزود الذكاء الاصطناعي الطلب برمز {exc.response.status_code}؛ تم استخدام fallback.",
        )
    except Exception as exc:  # pragma: no cover - exact network/runtime errors vary
        return _fallback_result(
            fallback_translation,
            decision.provider,
            f"تعذر استخدام مزود الذكاء الاصطناعي الخارجي؛ تم استخدام fallback. السبب: {exc.__class__.__name__}",
        )

    return _fallback_result(
        fallback_translation,
        decision.provider,
        "عاد مزود الذكاء الاصطناعي باستجابة فارغة؛ تم استخدام fallback.",
    )
