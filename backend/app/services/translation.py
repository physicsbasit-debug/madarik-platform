import re
from uuid import uuid4

from app.models.project import GlossaryTerm, QuestionItem, QuestionStatus


COMMAND_TRANSLATIONS: list[tuple[str, str]] = [
    (r"^\s*state\b", "اذكر"),
    (r"^\s*describe\b", "صف"),
    (r"^\s*explain\b", "فسّر"),
    (r"^\s*calculate\b", "احسب"),
    (r"^\s*compare\b", "قارن"),
    (r"^\s*suggest\b", "اقترح"),
    (r"^\s*determine\b", "حدّد"),
    (r"^\s*identify\b", "حدّد"),
    (r"^\s*give a reason\b", "أعط سببًا"),
    (r"^\s*complete\b", "أكمل"),
    (r"^\s*label\b", "سمِّ"),
    (r"^\s*draw\b", "ارسم"),
    (r"^\s*predict\b", "تنبّأ"),
    (r"^\s*justify\b", "برّر"),
    (r"^\s*evaluate\b", "قيّم"),
]

DEFAULT_TERM_TRANSLATIONS: dict[str, str] = {
    "cell membrane": "غشاء الخلية",
    "current": "شدة التيار",
    "resistance": "المقاومة",
    "rate of reaction": "معدل التفاعل",
    "temperature": "درجة الحرارة",
    "speed": "السرعة",
    "wave": "موجة",
    "frequency": "التردد",
    "wavelength": "الطول الموجي",
    "function": "وظيفة",
    "bulb": "المصباح",
    "circuit": "الدائرة الكهربائية",
    "force": "القوة",
    "resultant force": "القوة المحصلة",
    "diffusion": "الانتشار",
    "photosynthesis": "البناء الضوئي",
    "potential difference": "فرق الجهد",
    "voltage": "فرق الجهد",
    "reaction": "التفاعل",
    "solution": "المحلول",
    "enzyme": "الإنزيم",
    "concentration": "التركيز",
    "mass": "الكتلة",
    "distance": "المسافة",
    "time": "الزمن",
}

COMMON_WORD_TRANSLATIONS: list[tuple[str, str]] = [
    (r"\bwhy\b", "لماذا"),
    (r"\bhow\b", "كيف"),
    (r"\bthe function of\b", "وظيفة"),
    (r"\bfunction of\b", "وظيفة"),
    (r"\bwhen\b", "عندما"),
    (r"\bincreases\b", "تزداد"),
    (r"\bincreased\b", "تزداد"),
    (r"\bdecreases\b", "تقل"),
    (r"\bchanges\b", "يتغير"),
    (r"\bwith\b", "مع"),
    (r"\band\b", "و"),
    (r"\bof\b", "لـ"),
    (r"\ba\b", ""),
    (r"\ban\b", ""),
    (r"\bthe\b", ""),
]


def _strip_question_number(text: str) -> str:
    return re.sub(r"^\s*(?:question\s*)?\d+[\.)\:\-]?\s*", "", text, flags=re.IGNORECASE).strip()


def _extract_marks_suffix(text: str) -> str:
    match = re.search(r"(\[\s*\d+\s*\]|\(\s*\d+\s*marks?\s*\)|\b\d+\s*marks?\b)\s*$", text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _remove_marks_suffix(text: str) -> str:
    return re.sub(r"(\[\s*\d+\s*\]|\(\s*\d+\s*marks?\s*\)|\b\d+\s*marks?\b)\s*$", "", text, flags=re.IGNORECASE).strip()


def _normalise_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _command_translation(text: str) -> str | None:
    for pattern, translation in COMMAND_TRANSLATIONS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return translation
    return None


def _build_term_map(glossary: list[GlossaryTerm]) -> dict[str, str]:
    term_map = dict(DEFAULT_TERM_TRANSLATIONS)
    for term in glossary:
        english = term.english_term.strip().lower()
        arabic = term.arabic_term.strip()
        if english and arabic:
            term_map[english] = arabic
    return term_map


def _replace_terms(text: str, term_map: dict[str, str]) -> str:
    result = text
    for english, arabic in sorted(term_map.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = re.compile(rf"\b{re.escape(english)}\b", re.IGNORECASE)
        result = pattern.sub(arabic, result)
    return result


def _replace_common_words(text: str) -> str:
    result = text
    for pattern, arabic in COMMON_WORD_TRANSLATIONS:
        result = re.sub(pattern, arabic, result, flags=re.IGNORECASE)
    return _normalise_space(result)


def _clean_mixed_translation(text: str) -> str:
    result = text
    result = result.replace(" .", ".").replace(" ؟", "؟")
    result = re.sub(r"\s+", " ", result)
    result = re.sub(r"\s+([\.,؛:])", r"\1", result)
    return result.strip()


def _pattern_based_translation(core_text: str, term_map: dict[str, str]) -> str | None:
    lower = core_text.lower().strip()

    if re.match(r"^state\s+the\s+function\s+of\s+the\s+cell\s+membrane\.?$", lower):
        return "اذكر وظيفة غشاء الخلية."

    if re.match(r"^explain\s+why\s+the\s+current\s+decreases\s+when\s+the\s+resistance\s+increases\.?$", lower):
        return "فسّر لماذا تقل شدة التيار عندما تزداد المقاومة."

    speed_match = re.match(
        r"^calculate\s+the\s+speed\s+of\s+a\s+wave\s+with\s+frequency\s+(.+?)\s+and\s+wavelength\s+(.+?)\.?$",
        lower,
    )
    if speed_match:
        frequency = speed_match.group(1).strip()
        wavelength = speed_match.group(2).strip()
        return f"احسب سرعة موجة ترددها {frequency} وطولها الموجي {wavelength}."

    if re.match(r"^describe\s+how\s+the\s+rate\s+of\s+reaction\s+changes\s+when\s+the\s+temperature\s+is\s+increased\.?$", lower):
        return "صف كيف يتغير معدل التفاعل عند زيادة درجة الحرارة."

    command = _command_translation(core_text)
    if command is None:
        return None

    without_command = core_text
    for pattern, _translation in COMMAND_TRANSLATIONS:
        without_command = re.sub(pattern, "", without_command, flags=re.IGNORECASE).strip()
        if without_command != core_text:
            break

    replaced = _replace_terms(without_command, term_map)
    replaced = _replace_common_words(replaced)
    replaced = _clean_mixed_translation(replaced)
    if replaced:
        return f"{command} {replaced}".strip().replace("..", ".")
    return command


def translate_question_text(original_text: str, glossary: list[GlossaryTerm]) -> str:
    """Return a deterministic Phase 1-E2 draft translation.

    This is intentionally conservative and review-first. It is not a final AI translation.
    The real AI provider is deferred until the API key and deployment policy are fixed.
    """

    marks_suffix = _extract_marks_suffix(original_text)
    core_text = _remove_marks_suffix(_strip_question_number(original_text))
    term_map = _build_term_map(glossary)

    translated = _pattern_based_translation(core_text, term_map)
    if translated is None:
        replaced = _replace_terms(core_text, term_map)
        replaced = _replace_common_words(replaced)
        translated = _clean_mixed_translation(replaced)
        if translated == core_text or not re.search(r"[\u0600-\u06FF]", translated):
            translated = f"ترجمة أولية تحتاج مراجعة: {core_text}"

    translated = _clean_mixed_translation(translated)
    if not translated.endswith((".", "؟", "!", ":")):
        translated = f"{translated}."

    if marks_suffix and marks_suffix not in translated:
        translated = f"{translated} {marks_suffix}"
    return translated


def translate_questions_with_glossary(questions: list[QuestionItem], glossary: list[GlossaryTerm]) -> list[QuestionItem]:
    """Translate non-deleted questions using the reviewed glossary and command map."""

    translated_questions: list[QuestionItem] = []
    for question in questions:
        if question.status == QuestionStatus.deleted:
            translated_questions.append(question)
            continue

        translated_text = translate_question_text(question.original_text, glossary)
        review_note = "ترجمة Phase 1-E2 أولية قابلة للمراجعة قبل التصدير."
        if question.review_notes:
            review_note = f"{question.review_notes}\n{review_note}"

        translated_questions.append(
            question.model_copy(
                update={
                    "translated_text": translated_text,
                    "status": QuestionStatus.needs_review,
                    "review_notes": review_note,
                }
            )
        )
    return translated_questions


def build_translation_preview_id() -> str:
    """Small utility used by tests when they need stable non-empty provider metadata later."""

    return f"mock-translation-{uuid4()}"
