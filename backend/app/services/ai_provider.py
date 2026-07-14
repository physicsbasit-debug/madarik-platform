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


def _provider_api_mode(provider: str) -> str:
    if provider == "openai":
        return "responses"
    if provider == "openai-compatible":
        return "chat_completions"
    return "mock"


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
        "api_mode": _provider_api_mode(provider),
        "base_url_configured": bool(settings.ai_base_url.strip()) if provider != "mock" else False,
        "timeout_seconds": settings.ai_timeout_seconds,
        "max_input_chars": settings.ai_max_input_chars,
        "max_output_tokens": settings.ai_max_output_tokens,
        "temperature": settings.ai_temperature,
        "supported_providers": sorted(SUPPORTED_EXTERNAL_PROVIDERS | {"mock"}),
        "fallback": decision.fallback,
        # Madarik never asks OpenAI to retain translated exam content.
        "stores_responses": False,
    }


def build_translation_prompts(original_text: str, glossary: list[GlossaryTerm]) -> tuple[str, str]:
    """Build strict system/user prompts for scientific exam translation."""

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
        "لا تضف شرحًا، ولا نموذج إجابة، ولا تلميحات، ولا تحل السؤال. "
        "حافظ على معنى السؤال وفعل الأمر الامتحاني والرموز والمتغيرات والمعادلات "
        "والوحدات والأرقام والدرجات كما هي. "
        "طبّق قاموس الورقة عند وجوده، وأعد الترجمة العربية فقط دون مقدمات أو تنسيق Markdown."
    )
    user_prompt = (
        "قاموس أوامر السؤال المعتمد:\n"
        f"{command_text}\n\n"
        "قاموس مصطلحات الورقة المعتمد:\n"
        f"{glossary_text}\n\n"
        "السؤال المطلوب ترجمته:\n"
        f"{original_text.strip()}"
    )
    return system_prompt, user_prompt


def build_translation_messages(original_text: str, glossary: list[GlossaryTerm]) -> list[dict[str, str]]:
    """Build Chat Completions messages for OpenAI-compatible providers."""

    system_prompt, user_prompt = build_translation_prompts(original_text, glossary)
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


def _extract_openai_responses_content(payload: dict[str, Any]) -> str:
    direct_output = payload.get("output_text")
    if isinstance(direct_output, str) and direct_output.strip():
        return direct_output.strip()

    output = payload.get("output")
    if not isinstance(output, list):
        return ""

    collected: list[str] = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for content_item in content:
            if not isinstance(content_item, dict) or content_item.get("type") != "output_text":
                continue
            text = content_item.get("text")
            if isinstance(text, str) and text.strip():
                collected.append(text.strip())
    return "\n".join(collected).strip()


def _chat_completions_url() -> str:
    return f"{settings.ai_base_url.rstrip('/')}/chat/completions"


def _responses_url() -> str:
    return f"{settings.ai_base_url.rstrip('/')}/responses"


def _fallback_result(fallback_translation: str, provider: str, note: str) -> TranslationProviderResult:
    return TranslationProviderResult(
        translated_text=fallback_translation,
        provider="mock",
        used_external_provider=False,
        note=note if note else f"تعذر استخدام المزود {provider}؛ تم استخدام fallback.",
    )


def _post_openai_responses(original_text: str, glossary: list[GlossaryTerm]) -> httpx.Response:
    system_prompt, user_prompt = build_translation_prompts(original_text, glossary)
    return httpx.post(
        _responses_url(),
        headers={
            "Authorization": f"Bearer {settings.ai_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.ai_model,
            "instructions": system_prompt,
            "input": user_prompt,
            "temperature": settings.ai_temperature,
            "max_output_tokens": settings.ai_max_output_tokens,
            # Exam content is sent for this one translation request only.
            "store": False,
        },
        timeout=settings.ai_timeout_seconds,
    )


def _post_openai_compatible_chat(original_text: str, glossary: list[GlossaryTerm]) -> httpx.Response:
    return httpx.post(
        _chat_completions_url(),
        headers={
            "Authorization": f"Bearer {settings.ai_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.ai_model,
            "messages": build_translation_messages(original_text, glossary),
            "temperature": settings.ai_temperature,
            "max_tokens": settings.ai_max_output_tokens,
        },
        timeout=settings.ai_timeout_seconds,
    )


def translate_with_optional_external_provider(
    original_text: str,
    glossary: list[GlossaryTerm],
    fallback_translation: str,
) -> TranslationProviderResult:
    """Use the configured real provider and preserve a safe local fallback."""

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
        if decision.provider == "openai":
            response = _post_openai_responses(original_text, glossary)
            extract_content = _extract_openai_responses_content
        else:
            response = _post_openai_compatible_chat(original_text, glossary)
            extract_content = _extract_openai_chat_content

        response.raise_for_status()
        translated_text = extract_content(response.json())
        if translated_text:
            api_label = "Responses API" if decision.provider == "openai" else "Chat Completions"
            return TranslationProviderResult(
                translated_text=translated_text,
                provider=decision.provider,
                used_external_provider=True,
                note=(
                    f"تم توليد الترجمة عبر {decision.provider} باستخدام {api_label}. "
                    "تبقى الترجمة قابلة لمراجعة المعلم."
                ),
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
