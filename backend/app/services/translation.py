from dataclasses import dataclass
import re
from uuid import uuid4

from app.models.project import (
    GlossaryTerm,
    GlossaryTermStatus,
    ProjectMetadata,
    QuestionItem,
    QuestionPart,
    QuestionStatus,
    TranslationBatchStatus,
    TranslationBatchSummary,
    TranslationItemOutcome,
    TranslationItemType,
    TranslationOutcomeStatus,
)
from app.services.ai_provider import (
    TranslationPromptContext,
    TranslationProviderResult,
    translate_with_optional_external_provider,
)


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
        if term.status == GlossaryTermStatus.approved and english and arabic:
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
    """Return the deterministic local fallback translation.

    This path remains conservative and review-first. Phase 4-A4 uses it whenever
    the external provider is unavailable or keeps violating glossary or fidelity guards.
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


@dataclass(frozen=True)
class TranslationBatchResult:
    """Translated questions plus a persisted Phase 4-A5 batch summary."""

    questions: list[QuestionItem]
    summary: TranslationBatchSummary


def _translate_text_with_provider(
    original_text: str,
    glossary: list[GlossaryTerm],
    *,
    context: TranslationPromptContext | None = None,
) -> TranslationProviderResult:
    """Translate one text block through the configured provider with fallback."""

    fallback_translation = translate_question_text(original_text, glossary)
    return translate_with_optional_external_provider(
        original_text=original_text,
        glossary=glossary,
        fallback_translation=fallback_translation,
        context=context,
    )


def _minimal_safe_translation(
    original_text: str,
    current_translation: str = "",
) -> str:
    """Preserve prior work or expose the source safely when every translator fails."""

    existing = current_translation.strip()
    if existing:
        return existing

    source = original_text.strip()
    return (
        f"ترجمة أولية تحتاج مراجعة عاجلة: {source}"
        if source
        else "ترجمة غير متاحة؛ يحتاج هذا العنصر إلى مراجعة عاجلة."
    )


def _translate_text_safely(
    original_text: str,
    glossary: list[GlossaryTerm],
    *,
    current_translation: str = "",
    context: TranslationPromptContext | None = None,
) -> TranslationProviderResult:
    """Isolate one provider/local failure so the remaining batch can continue."""

    try:
        return _translate_text_with_provider(
            original_text,
            glossary,
            context=context,
        )
    except Exception as provider_error:
        try:
            fallback_translation = translate_question_text(
                original_text,
                glossary,
            )
        except Exception as fallback_error:
            return TranslationProviderResult(
                translated_text=_minimal_safe_translation(
                    original_text,
                    current_translation,
                ),
                provider="mock",
                used_external_provider=False,
                note=(
                    "تعذر إكمال هذا العنصر عبر المزود والترجمة المحلية، "
                    "فتم حفظه دون إسقاط بقية الدفعة. "
                    f"الأخطاء: {provider_error.__class__.__name__} / "
                    f"{fallback_error.__class__.__name__}."
                ),
                outcome=TranslationOutcomeStatus.failed_safely,
            )

        return TranslationProviderResult(
            translated_text=fallback_translation,
            provider="mock",
            used_external_provider=False,
            note=(
                "حدث خطأ غير متوقع في طبقة المزود لهذا العنصر، "
                "فتم عزله واستخدام fallback المحلي دون إيقاف بقية الدفعة. "
                f"السبب: {provider_error.__class__.__name__}."
            ),
            outcome=TranslationOutcomeStatus.local_fallback,
        )


def _build_prompt_context(
    metadata: ProjectMetadata | None,
    *,
    question_number: str = "",
    part_label: str = "",
    question_stem: str = "",
    parent_part_text: str = "",
) -> TranslationPromptContext:
    return TranslationPromptContext(
        subject=metadata.subject if metadata else "",
        grade=metadata.grade if metadata else "",
        semester=metadata.semester if metadata else "",
        question_number=question_number,
        part_label=part_label,
        question_stem=question_stem,
        parent_part_text=parent_part_text,
    )


def _build_item_outcome(
    *,
    question: QuestionItem,
    result: TranslationProviderResult | None = None,
    item_type: TranslationItemType = TranslationItemType.question,
    part: QuestionPart | None = None,
    status: TranslationOutcomeStatus | None = None,
    message: str = "",
) -> TranslationItemOutcome:
    resolved_status = status or (
        result.outcome
        if result is not None
        else TranslationOutcomeStatus.skipped
    )
    urgent_review = resolved_status in {
        TranslationOutcomeStatus.local_fallback,
        TranslationOutcomeStatus.failed_safely,
    }

    return TranslationItemOutcome(
        question_id=question.id,
        question_number=question.original_number,
        item_type=item_type,
        part_id=part.id if part else None,
        part_label=part.label if part else None,
        status=resolved_status,
        provider=result.provider if result is not None else "mock",
        used_external_provider=(
            result.used_external_provider
            if result is not None
            else False
        ),
        urgent_review=urgent_review,
        message=(
            result.note
            if result is not None and result.note
            else message
        ),
    )


def _translate_question_parts(
    question: QuestionItem,
    glossary: list[GlossaryTerm],
    *,
    metadata: ProjectMetadata | None = None,
) -> tuple[
    list[QuestionPart],
    list[str],
    list[str],
    list[TranslationItemOutcome],
]:
    """Translate every part independently and isolate failures per part."""

    translated_parts: list[QuestionPart] = []
    providers: list[str] = []
    notes: list[str] = []
    outcomes: list[TranslationItemOutcome] = []
    parts_by_id = {part.id: part for part in question.parts}

    for part in sorted(question.parts, key=lambda item: item.order_index):
        original_text = part.original_text.strip()
        if not original_text:
            translated_parts.append(part)
            outcomes.append(
                _build_item_outcome(
                    question=question,
                    item_type=TranslationItemType.part,
                    part=part,
                    status=TranslationOutcomeStatus.skipped,
                    message="تم تجاوز جزء فارغ مع الحفاظ على موقعه الهرمي.",
                )
            )
            continue

        parent_part = (
            parts_by_id.get(part.parent_id)
            if part.parent_id
            else None
        )
        context = _build_prompt_context(
            metadata,
            question_number=question.original_number,
            part_label=part.label,
            question_stem=question.original_text,
            parent_part_text=(
                parent_part.original_text
                if parent_part
                else ""
            ),
        )
        provider_result = _translate_text_safely(
            original_text,
            glossary,
            current_translation=part.translated_text,
            context=context,
        )
        translated_parts.append(
            part.model_copy(
                update={
                    "translated_text": provider_result.translated_text,
                }
            )
        )
        providers.append(provider_result.provider)
        if provider_result.note:
            notes.append(provider_result.note)
        outcomes.append(
            _build_item_outcome(
                question=question,
                result=provider_result,
                item_type=TranslationItemType.part,
                part=part,
            )
        )

    return translated_parts, providers, notes, outcomes


def _question_part_depth(
    part: QuestionPart,
    parts: list[QuestionPart],
) -> int:
    """Return a cycle-safe hierarchy depth for one structured part."""

    parts_by_id = {
        item.id: item
        for item in parts
    }
    depth = 0
    current = part
    visited = {part.id}

    while current.parent_id:
        parent = parts_by_id.get(current.parent_id)

        if parent is None or parent.id in visited:
            break

        visited.add(parent.id)
        depth += 1
        current = parent

    return depth


def _build_combined_parts_translation(parts: list[QuestionPart]) -> str:
    """Build a readable question-level translation from translated parts."""

    lines: list[str] = []
    parent_ids = {
        part.parent_id
        for part in parts
        if part.parent_id is not None
    }

    for part in sorted(parts, key=lambda item: item.order_index):
        translated_text = part.translated_text.strip()

        if not translated_text and part.id not in parent_ids:
            continue

        label = part.label.strip()
        indentation = "  " * _question_part_depth(
            part,
            parts,
        )
        line = f"{label} {translated_text}".strip()
        lines.append(f"{indentation}{line}")

    return "\n".join(lines)


def _question_review_note(
    *,
    question: QuestionItem,
    providers: list[str],
    provider_notes: list[str],
    translated_parts: list[QuestionPart],
) -> str:
    providers_used = sorted(set(providers)) or ["mock"]
    translated_part_count = sum(
        1
        for part in translated_parts
        if part.original_text.strip() and part.translated_text.strip()
    )
    parts_note = (
        " تمت ترجمة أجزاء السؤال بصورة مستقلة "
        f"(العدد: {translated_part_count})."
        if translated_part_count
        else ""
    )

    review_note = (
        "ترجمة Phase 4-A5 بدفعة معزولة العناصر، "
        "مع فرض القاموس وحارس سلامة المحتوى العلمي. "
        f"المزود المستخدم: {', '.join(providers_used)}."
        f"{parts_note} "
        "راجع الترجمة قبل التصدير."
    )
    for provider_note in dict.fromkeys(provider_notes):
        review_note = f"{review_note}\n{provider_note}"
    if question.review_notes:
        review_note = f"{question.review_notes}\n{review_note}"
    return review_note


def _build_batch_summary(
    questions: list[QuestionItem],
    outcomes: list[TranslationItemOutcome],
) -> TranslationBatchSummary:
    counts = {
        status: sum(1 for item in outcomes if item.status == status)
        for status in TranslationOutcomeStatus
    }
    failed_count = counts[TranslationOutcomeStatus.failed_safely]
    fallback_count = counts[TranslationOutcomeStatus.local_fallback]

    if failed_count:
        batch_status = TranslationBatchStatus.completed_with_failures
    elif fallback_count:
        batch_status = TranslationBatchStatus.completed_with_fallbacks
    else:
        batch_status = TranslationBatchStatus.completed

    return TranslationBatchSummary(
        status=batch_status,
        total_questions=len(questions),
        active_questions=sum(
            1
            for question in questions
            if question.status != QuestionStatus.deleted
        ),
        deleted_questions=sum(
            1
            for question in questions
            if question.status == QuestionStatus.deleted
        ),
        total_items=len(outcomes),
        external_success_count=counts[
            TranslationOutcomeStatus.external_success
        ],
        corrected_success_count=counts[
            TranslationOutcomeStatus.corrected_success
        ],
        local_fallback_count=fallback_count,
        skipped_count=counts[TranslationOutcomeStatus.skipped],
        failed_safely_count=failed_count,
        urgent_review_count=sum(
            1
            for item in outcomes
            if item.urgent_review
        ),
        items=outcomes,
    )


def _failed_question_after_unexpected_error(
    question: QuestionItem,
    error: Exception,
) -> tuple[QuestionItem, TranslationItemOutcome]:
    """Preserve one question safely if orchestration itself raises."""

    preserved_parts = question.parts
    try:
        combined_existing = _build_combined_parts_translation(
            preserved_parts
        ).strip()
    except Exception:
        combined_existing = ""

    translated_text = (
        question.translated_text.strip()
        or combined_existing
        or _minimal_safe_translation(question.original_text)
    )
    failure_note = (
        "تعذر إكمال هذا السؤال بسبب خطأ غير متوقع في تنسيق الدفعة، "
        "فتم حفظه للمراجعة دون إسقاط الأسئلة الأخرى. "
        f"السبب: {error.__class__.__name__}."
    )
    review_note = (
        f"{question.review_notes}\n{failure_note}"
        if question.review_notes
        else failure_note
    )
    updated_question = question.model_copy(
        update={
            "translated_text": translated_text,
            "status": QuestionStatus.needs_review,
            "review_notes": review_note,
        }
    )
    outcome = TranslationItemOutcome(
        question_id=question.id,
        question_number=question.original_number,
        item_type=TranslationItemType.question,
        status=TranslationOutcomeStatus.failed_safely,
        provider="mock",
        used_external_provider=False,
        urgent_review=True,
        message=failure_note,
    )
    return updated_question, outcome


def translate_questions_batch_with_glossary(
    questions: list[QuestionItem],
    glossary: list[GlossaryTerm],
    metadata: ProjectMetadata | None = None,
) -> TranslationBatchResult:
    """Translate a complete paper without letting one item abort the batch."""

    translated_questions: list[QuestionItem] = []
    outcomes: list[TranslationItemOutcome] = []

    for question in questions:
        if question.status == QuestionStatus.deleted:
            translated_questions.append(question)
            outcomes.append(
                _build_item_outcome(
                    question=question,
                    status=TranslationOutcomeStatus.skipped,
                    message="تم تجاوز السؤال المحذوف دون إرسال أي طلب خارجي.",
                )
            )
            continue

        try:
            translated_parts: list[QuestionPart] = []
            provider_names: list[str] = []
            provider_notes: list[str] = []
            question_outcomes: list[TranslationItemOutcome] = []

            if question.parts:
                (
                    translated_parts,
                    provider_names,
                    provider_notes,
                    question_outcomes,
                ) = _translate_question_parts(
                    question,
                    glossary,
                    metadata=metadata,
                )
                translated_text = _build_combined_parts_translation(
                    translated_parts
                )

                # Preserve the established whole-question fallback when every
                # structured part is only a blank heading.
                if not translated_text:
                    provider_result = _translate_text_safely(
                        question.original_text,
                        glossary,
                        current_translation=question.translated_text,
                        context=_build_prompt_context(
                            metadata,
                            question_number=question.original_number,
                        ),
                    )
                    translated_text = provider_result.translated_text
                    provider_names.append(provider_result.provider)
                    if provider_result.note:
                        provider_notes.append(provider_result.note)
                    question_outcomes.append(
                        _build_item_outcome(
                            question=question,
                            result=provider_result,
                        )
                    )
            else:
                provider_result = _translate_text_safely(
                    question.original_text,
                    glossary,
                    current_translation=question.translated_text,
                    context=_build_prompt_context(
                        metadata,
                        question_number=question.original_number,
                    ),
                )
                translated_text = provider_result.translated_text
                provider_names.append(provider_result.provider)
                if provider_result.note:
                    provider_notes.append(provider_result.note)
                question_outcomes.append(
                    _build_item_outcome(
                        question=question,
                        result=provider_result,
                    )
                )

            update_data: dict[str, object] = {
                "translated_text": translated_text,
                "status": QuestionStatus.needs_review,
                "review_notes": _question_review_note(
                    question=question,
                    providers=provider_names,
                    provider_notes=provider_notes,
                    translated_parts=translated_parts,
                ),
            }
            if question.parts:
                update_data["parts"] = translated_parts

            translated_questions.append(
                question.model_copy(update=update_data)
            )
            outcomes.extend(question_outcomes)
        except Exception as error:
            failed_question, failed_outcome = (
                _failed_question_after_unexpected_error(
                    question,
                    error,
                )
            )
            translated_questions.append(failed_question)
            outcomes.append(failed_outcome)

    return TranslationBatchResult(
        questions=translated_questions,
        summary=_build_batch_summary(questions, outcomes),
    )


def translate_questions_with_glossary(
    questions: list[QuestionItem],
    glossary: list[GlossaryTerm],
    metadata: ProjectMetadata | None = None,
) -> list[QuestionItem]:
    """Backward-compatible wrapper returning only translated question cards."""

    return translate_questions_batch_with_glossary(
        questions,
        glossary,
        metadata,
    ).questions


def build_translation_preview_id() -> str:
    """Small utility used by tests when they need stable non-empty provider metadata later."""

    return f"mock-translation-{uuid4()}"
