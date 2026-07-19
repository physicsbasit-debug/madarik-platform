from __future__ import annotations

from collections import defaultdict

from app.models.project import (
    FullExamIntakeReport,
    FullExamTranslationAcceptanceStatus,
    FullExamTranslationCheck,
    FullExamTranslationQuestionSummary,
    FullExamTranslationQuestionStatus,
    FullExamTranslationReport,
    GlossaryTerm,
    QuestionItem,
    QuestionStatus,
    TranslationBatchSummary,
    TranslationItemOutcome,
    TranslationOutcomeStatus,
)
from app.services.ai_provider import (
    validate_arabic_translation_quality,
    validate_glossary_compliance,
    validate_translation_fidelity,
)


def _question_translation_items(
    question: QuestionItem,
) -> list[tuple[str | None, str, str]]:
    """Return the reviewable source/translation pairs for one question."""

    source_parts = [
        part
        for part in sorted(
            question.parts,
            key=lambda item: item.order_index,
        )
        if part.original_text.strip()
    ]
    if source_parts:
        return [
            (
                part.id,
                part.original_text,
                part.translated_text,
            )
            for part in source_parts
        ]

    return [
        (
            None,
            question.original_text,
            question.translated_text,
        )
    ]


def _outcomes_by_question(
    summary: TranslationBatchSummary | None,
) -> dict[str, list[TranslationItemOutcome]]:
    grouped: dict[str, list[TranslationItemOutcome]] = defaultdict(list)
    if summary is None:
        return grouped

    for item in summary.items:
        grouped[item.question_id].append(item)
    return grouped


def _question_message(
    status: FullExamTranslationQuestionStatus,
    *,
    translated_items: int,
    total_items: int,
    failed_items: int,
    urgent_review_items: int,
    glossary_violations: int,
    fidelity_violations: int,
    language_quality_violations: int,
) -> str:
    if status == FullExamTranslationQuestionStatus.deleted:
        return "السؤال محذوف ولا يدخل في قبول الورقة."
    if status == FullExamTranslationQuestionStatus.failed:
        return (
            "تعذر إكمال الترجمة الآلية لهذا السؤال. "
            f"العناصر الفاشلة: {failed_items}."
        )
    if status == FullExamTranslationQuestionStatus.untranslated:
        return (
            "ترجمة السؤال غير مكتملة: "
            f"{translated_items} من {total_items} عناصر."
        )
    if status == FullExamTranslationQuestionStatus.needs_review:
        reasons: list[str] = []
        if urgent_review_items:
            reasons.append(
                f"{urgent_review_items} عناصر مصنفة للمراجعة العاجلة"
            )
        if glossary_violations:
            reasons.append(
                f"{glossary_violations} مخالفات قاموس"
            )
        if fidelity_violations:
            reasons.append(
                f"{fidelity_violations} مخالفات سلامة علمية"
            )
        if language_quality_violations:
            reasons.append(
                f"{language_quality_violations} مخالفات جودة عربية"
            )
        if not reasons:
            reasons.append("اعتماد المعلم لم يكتمل")
        return "يحتاج السؤال إلى مراجعة: " + "، ".join(reasons) + "."

    return "الترجمة مكتملة ومعتمدة لهذا السؤال."


def build_full_exam_translation_report(
    questions: list[QuestionItem],
    glossary: list[GlossaryTerm],
    batch_summary: TranslationBatchSummary | None = None,
    intake_report: FullExamIntakeReport | None = None,
) -> FullExamTranslationReport:
    """Build a deterministic full-paper translation and review acceptance report."""

    outcomes_by_question = _outcomes_by_question(batch_summary)
    intake_spans = {
        span.question_number: span
        for span in (intake_report.question_spans if intake_report else [])
    }

    question_summaries: list[FullExamTranslationQuestionSummary] = []
    total_items = 0
    translated_items = 0
    urgent_review_items = 0
    glossary_violation_count = 0
    fidelity_violation_count = 0
    language_quality_violation_count = 0
    source_page_linked_questions = 0
    multi_page_questions = 0
    structure_preserved = True

    for question in sorted(
        questions,
        key=lambda item: item.order_index,
    ):
        translation_items = _question_translation_items(question)
        question_total_items = len(translation_items)
        question_translated_items = 0
        question_glossary_violations = 0
        question_fidelity_violations = 0
        question_language_quality_violations = 0

        for _part_id, original_text, translated_text in translation_items:
            if translated_text.strip():
                question_translated_items += 1
                glossary_result = validate_glossary_compliance(
                    original_text,
                    translated_text,
                    glossary,
                )
                fidelity_result = validate_translation_fidelity(
                    original_text,
                    translated_text,
                )
                question_glossary_violations += len(
                    glossary_result.missing_terms
                )
                question_fidelity_violations += len(
                    fidelity_result.missing_tokens
                )
                language_quality_result = validate_arabic_translation_quality(
                    original_text,
                    translated_text,
                )
                if not language_quality_result.is_compliant:
                    question_language_quality_violations += 1

        question_outcomes = outcomes_by_question.get(question.id, [])
        failed_items = sum(
            1
            for item in question_outcomes
            if item.status == TranslationOutcomeStatus.failed_safely
        )
        question_urgent_review_items = sum(
            1
            for item in question_outcomes
            if item.urgent_review
        )

        if question.status == QuestionStatus.deleted:
            question_status = FullExamTranslationQuestionStatus.deleted
        elif (
            failed_items > 0
            and question.status != QuestionStatus.approved
        ):
            question_status = FullExamTranslationQuestionStatus.failed
        elif question_translated_items < question_total_items:
            question_status = (
                FullExamTranslationQuestionStatus.untranslated
            )
        elif (
            question_glossary_violations > 0
            or question_fidelity_violations > 0
            or question_language_quality_violations > 0
            or question_urgent_review_items > 0
            or question.status != QuestionStatus.approved
        ):
            question_status = (
                FullExamTranslationQuestionStatus.needs_review
            )
        else:
            question_status = FullExamTranslationQuestionStatus.accepted

        expected_span = intake_spans.get(question.original_number)
        if expected_span is not None:
            if (
                question.source_page_numbers
                != expected_span.page_numbers
                or len(question.linked_layout_asset_ids)
                < expected_span.linked_layout_asset_count
            ):
                structure_preserved = False

        if question.status != QuestionStatus.deleted:
            total_items += question_total_items
            translated_items += question_translated_items
            urgent_review_items += question_urgent_review_items
            glossary_violation_count += (
                question_glossary_violations
            )
            fidelity_violation_count += (
                question_fidelity_violations
            )
            language_quality_violation_count += (
                question_language_quality_violations
            )
            if (
                question.source_page_numbers
                and question.linked_layout_asset_ids
            ):
                source_page_linked_questions += 1
            if len(question.source_page_numbers) > 1:
                multi_page_questions += 1

        question_summaries.append(
            FullExamTranslationQuestionSummary(
                question_id=question.id,
                question_number=question.original_number,
                status=question_status,
                total_items=question_total_items,
                translated_items=question_translated_items,
                urgent_review_items=question_urgent_review_items,
                failed_items=failed_items,
                glossary_violation_count=(
                    question_glossary_violations
                ),
                fidelity_violation_count=(
                    question_fidelity_violations
                ),
                language_quality_violation_count=(
                    question_language_quality_violations
                ),
                source_page_numbers=question.source_page_numbers,
                linked_layout_asset_count=len(
                    question.linked_layout_asset_ids
                ),
                message=_question_message(
                    question_status,
                    translated_items=question_translated_items,
                    total_items=question_total_items,
                    failed_items=failed_items,
                    urgent_review_items=(
                        question_urgent_review_items
                    ),
                    glossary_violations=(
                        question_glossary_violations
                    ),
                    fidelity_violations=(
                        question_fidelity_violations
                    ),
                    language_quality_violations=(
                        question_language_quality_violations
                    ),
                ),
            )
        )

    if intake_report is not None:
        active_question_numbers = {
            question.original_number
            for question in questions
            if question.status != QuestionStatus.deleted
        }
        expected_question_numbers = {
            span.question_number
            for span in intake_report.question_spans
        }
        if active_question_numbers != expected_question_numbers:
            structure_preserved = False

    active_summaries = [
        item
        for item in question_summaries
        if item.status != FullExamTranslationQuestionStatus.deleted
    ]
    accepted_questions = sum(
        1
        for item in active_summaries
        if item.status == FullExamTranslationQuestionStatus.accepted
    )
    needs_review_questions = sum(
        1
        for item in active_summaries
        if item.status
        == FullExamTranslationQuestionStatus.needs_review
    )
    untranslated_questions = sum(
        1
        for item in active_summaries
        if item.status
        == FullExamTranslationQuestionStatus.untranslated
    )
    failed_questions = sum(
        1
        for item in active_summaries
        if item.status == FullExamTranslationQuestionStatus.failed
    )

    active_questions = len(active_summaries)
    deleted_questions = len(question_summaries) - active_questions
    translated_questions = sum(
        1
        for item in active_summaries
        if item.translated_items == item.total_items
    )
    completion_percent = (
        round((translated_questions / active_questions) * 100, 2)
        if active_questions
        else 0.0
    )

    if not active_questions:
        report_status = (
            FullExamTranslationAcceptanceStatus.incomplete
        )
    elif failed_questions:
        report_status = FullExamTranslationAcceptanceStatus.failed
    elif untranslated_questions:
        report_status = (
            FullExamTranslationAcceptanceStatus.incomplete
        )
    elif (
        needs_review_questions
        or urgent_review_items
        or glossary_violation_count
        or fidelity_violation_count
        or language_quality_violation_count
    ):
        report_status = (
            FullExamTranslationAcceptanceStatus.needs_review
        )
    else:
        report_status = FullExamTranslationAcceptanceStatus.accepted

    checks = [
        FullExamTranslationCheck(
            code="active_questions_available",
            passed=active_questions > 0,
            message=(
                f"توجد {active_questions} أسئلة نشطة."
                if active_questions
                else "لا توجد أسئلة نشطة للترجمة."
            ),
        ),
        FullExamTranslationCheck(
            code="translation_complete",
            passed=(
                active_questions > 0
                and untranslated_questions == 0
                and failed_questions == 0
            ),
            message=(
                f"اكتملت ترجمة {translated_questions} من "
                f"{active_questions} أسئلة نشطة."
            ),
        ),
        FullExamTranslationCheck(
            code="glossary_compliant",
            passed=glossary_violation_count == 0,
            message=(
                "لا توجد مخالفات قاموس في النصوص الحالية."
                if glossary_violation_count == 0
                else (
                    "تم اكتشاف "
                    f"{glossary_violation_count} مخالفات قاموس."
                )
            ),
        ),
        FullExamTranslationCheck(
            code="scientific_fidelity_compliant",
            passed=fidelity_violation_count == 0,
            message=(
                "جميع القيم والوحدات والرموز العلمية المحمية موجودة."
                if fidelity_violation_count == 0
                else (
                    "تم اكتشاف "
                    f"{fidelity_violation_count} مخالفات سلامة علمية."
                )
            ),
        ),
        FullExamTranslationCheck(
            code="arabic_language_quality_compliant",
            passed=language_quality_violation_count == 0,
            message=(
                "لا توجد بقايا نثر إنجليزي غير مفسرة في وضع العربية."
                if language_quality_violation_count == 0
                else (
                    "تم اكتشاف "
                    f"{language_quality_violation_count} عناصر ترجمة مختلطة أو غير عربية بما يكفي."
                )
            ),
        ),
        FullExamTranslationCheck(
            code="external_translation_only",
            passed=urgent_review_items == 0,
            message=(
                "لا توجد عناصر fallback أو فشل محفوظ بأمان في الدفعة الحالية."
                if urgent_review_items == 0
                else (
                    f"توجد {urgent_review_items} عناصر fallback أو فشل؛ "
                    "ولا يمكن قبولها نهائيًا حتى بعد اعتماد المعلم."
                )
            ),
        ),
        FullExamTranslationCheck(
            code="source_structure_preserved",
            passed=structure_preserved,
            message=(
                "حُفظت صفحات المصدر وروابط لقطات PDF بعد الترجمة."
                if structure_preserved
                else (
                    "تغيرت صفحات المصدر أو روابط اللقطات مقارنة "
                    "بتقرير قبول الإدخال."
                )
            ),
        ),
        FullExamTranslationCheck(
            code="teacher_review_complete",
            passed=(
                active_questions > 0
                and accepted_questions == active_questions
            ),
            message=(
                f"اعتمد المعلم {accepted_questions} من "
                f"{active_questions} أسئلة نشطة."
            ),
        ),
    ]

    warnings: list[str] = []
    if not active_questions:
        warnings.append("لا توجد أسئلة نشطة لبناء قبول ترجمة كامل.")
    if failed_questions:
        warnings.append(
            f"فشلت ترجمة {failed_questions} أسئلة وتحتاج إلى إعادة محاولة."
        )
    if untranslated_questions:
        warnings.append(
            f"بقيت {untranslated_questions} أسئلة غير مكتملة الترجمة."
        )
    if needs_review_questions:
        warnings.append(
            f"تحتاج {needs_review_questions} أسئلة إلى اعتماد المعلم."
        )
    if glossary_violation_count:
        warnings.append(
            f"توجد {glossary_violation_count} مخالفات للمصطلحات المعتمدة."
        )
    if fidelity_violation_count:
        warnings.append(
            f"توجد {fidelity_violation_count} مخالفات للمحتوى العلمي المحمي."
        )
    if language_quality_violation_count:
        warnings.append(
            f"توجد {language_quality_violation_count} عناصر ترجمة مختلطة أو غير عربية بما يكفي."
        )
    if urgent_review_items:
        warnings.append(
            f"توجد {urgent_review_items} عناصر fallback أو فشل لا يمكن اعتمادها نهائيًا."
        )
    if intake_report is None:
        warnings.append(
            "لا يوجد تقرير قبول إدخال كامل لمقارنة بنية صفحات المصدر."
        )
    elif not structure_preserved:
        warnings.append(
            "لم تُحفظ بنية صفحات المصدر أو روابط اللقطات كما كانت."
        )

    return FullExamTranslationReport(
        status=report_status,
        total_questions=len(question_summaries),
        active_questions=active_questions,
        deleted_questions=deleted_questions,
        translated_questions=translated_questions,
        accepted_questions=accepted_questions,
        needs_review_questions=needs_review_questions,
        untranslated_questions=untranslated_questions,
        failed_questions=failed_questions,
        completion_percent=completion_percent,
        total_items=total_items,
        translated_items=translated_items,
        urgent_review_items=urgent_review_items,
        glossary_violation_count=glossary_violation_count,
        fidelity_violation_count=fidelity_violation_count,
        language_quality_violation_count=language_quality_violation_count,
        source_page_linked_questions=source_page_linked_questions,
        multi_page_questions=multi_page_questions,
        questions=question_summaries,
        checks=checks,
        warnings=warnings,
    )
