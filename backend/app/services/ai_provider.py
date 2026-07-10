from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.models.project import GlossaryTerm


@dataclass(frozen=True)
class TranslationProviderResult:
    """Result returned by the optional external AI provider layer."""

    translated_text: str
    provider: str
    used_external_provider: bool
    note: str = ""


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


def get_ai_provider_status() -> dict[str, object]:
    """Return safe provider metadata for UI/tests without exposing secrets."""

    provider = settings.ai_provider.strip().lower()
    configured = bool(settings.ai_api_key.strip() and settings.ai_model.strip())
    return {
        "provider": provider,
        "configured": configured if provider != "mock" else False,
        "model": settings.ai_model if provider != "mock" and settings.ai_model else "",
        "fallback": "mock" if provider == "mock" or not configured else "none",
    }


def build_translation_messages(original_text: str, glossary: list[GlossaryTerm]) -> list[dict[str, str]]:
    """Build a strict, review-first prompt for future external AI translation."""

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


def translate_with_optional_external_provider(
    original_text: str,
    glossary: list[GlossaryTerm],
    fallback_translation: str,
) -> TranslationProviderResult:
    """Use an optional external provider when configured; otherwise return fallback.

    Phase 1-G1 deliberately keeps mock fallback as the safe default so CI and local
    development do not require paid API keys or secrets. External provider failures
    never break the user flow; the teacher still receives a reviewable draft.
    """

    provider = settings.ai_provider.strip().lower()
    if provider in {"", "mock"}:
        return TranslationProviderResult(
            translated_text=fallback_translation,
            provider="mock",
            used_external_provider=False,
            note="استخدمت الترجمة التجريبية لأن مزود الذكاء الاصطناعي غير مفعل.",
        )

    if provider != "openai":
        return TranslationProviderResult(
            translated_text=fallback_translation,
            provider="mock",
            used_external_provider=False,
            note=f"مزود الذكاء الاصطناعي '{provider}' غير مدعوم بعد؛ تم استخدام fallback.",
        )

    if not settings.ai_api_key.strip() or not settings.ai_model.strip():
        return TranslationProviderResult(
            translated_text=fallback_translation,
            provider="mock",
            used_external_provider=False,
            note="لم يتم ضبط MADARIK_AI_API_KEY وMADARIK_AI_MODEL؛ تم استخدام fallback.",
        )

    try:
        response = httpx.post(
            f"{settings.ai_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.ai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.ai_model,
                "messages": build_translation_messages(original_text, glossary),
                "temperature": 0.1,
            },
            timeout=settings.ai_timeout_seconds,
        )
        response.raise_for_status()
        translated_text = _extract_openai_chat_content(response.json())
        if translated_text:
            return TranslationProviderResult(
                translated_text=translated_text,
                provider="openai",
                used_external_provider=True,
                note="تم توليد الترجمة عبر مزود ذكاء اصطناعي خارجي، وتبقى قابلة للمراجعة.",
            )
    except Exception as exc:  # pragma: no cover - exact network errors vary by runtime
        return TranslationProviderResult(
            translated_text=fallback_translation,
            provider="mock",
            used_external_provider=False,
            note=f"تعذر استخدام مزود الذكاء الاصطناعي الخارجي؛ تم استخدام fallback. السبب: {exc.__class__.__name__}",
        )

    return TranslationProviderResult(
        translated_text=fallback_translation,
        provider="mock",
        used_external_provider=False,
        note="عاد مزود الذكاء الاصطناعي باستجابة فارغة؛ تم استخدام fallback.",
    )
