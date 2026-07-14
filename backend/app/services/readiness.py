from __future__ import annotations

from app.models.project import (
    ProjectReadinessIssue,
    ProjectReadinessReport,
    ProjectSession,
    QuestionItem,
    QuestionPart,
    QuestionStatus,
    ReadinessSeverity,
)


def _question_parts_total_marks(question: QuestionItem) -> int | None:
    """Return a hierarchy-safe total for structured question parts.

    A parent mark often summarizes its descendants. To avoid counting the same
    branch twice, marked descendants take precedence; the parent mark is used
    only when the branch has no marked descendants.
    """

    if not question.parts:
        return None

    parts_by_id = {part.id: part for part in question.parts}
    children: dict[str, list[QuestionPart]] = {}

    for part in question.parts:
        if part.parent_id in parts_by_id:
            children.setdefault(part.parent_id, []).append(part)

    roots = [
        part
        for part in question.parts
        if part.parent_id not in parts_by_id
    ]

    def branch_marks(
        part: QuestionPart,
        visited: set[str],
    ) -> int | None:
        if part.id in visited:
            return part.marks

        next_visited = visited | {part.id}
        child_values = [
            branch_marks(child, next_visited)
            for child in children.get(part.id, [])
        ]
        concrete_child_values = [
            value
            for value in child_values
            if value is not None
        ]

        if concrete_child_values:
            return sum(concrete_child_values)

        return part.marks

    totals = [branch_marks(root, set()) for root in roots]
    concrete_totals = [value for value in totals if value is not None]

    return sum(concrete_totals) if concrete_totals else None


def _question_effective_marks(question: QuestionItem) -> int | None:
    """Return the mark value currently used by export/readiness totals."""

    if question.marks is not None:
        return question.marks

    return _question_parts_total_marks(question)


def _question_display_number(question: QuestionItem, index: int) -> str:
    return question.original_number.strip() or str(index)


def build_project_readiness_report(project: ProjectSession) -> ProjectReadinessReport:
    """Build a conservative, non-destructive export readiness report.

    Marks inconsistencies are guidance warnings only. Export remains available,
    while the review step can explicitly adopt the calculated parts total.
    """

    issues: list[ProjectReadinessIssue] = []
    active_questions = [
        question
        for question in project.questions
        if question.status != QuestionStatus.deleted
    ]
    translated_questions = [
        question
        for question in active_questions
        if question.translated_text.strip()
        and question.translated_text.strip() != question.original_text.strip()
    ]
    needs_review_questions = [
        question
        for question in active_questions
        if question.status == QuestionStatus.needs_review
    ]
    deleted_questions = [
        question
        for question in project.questions
        if question.status == QuestionStatus.deleted
    ]

    parts_totals = {
        question.id: _question_parts_total_marks(question)
        for question in active_questions
    }
    missing_marks_questions = [
        question
        for question in active_questions
        if question.marks is None and parts_totals[question.id] is None
    ]
    empty_translation_questions = [
        question
        for question in active_questions
        if not question.translated_text.strip()
    ]

    if not project.uploaded_file:
        issues.append(
            ProjectReadinessIssue(
                code="missing_file",
                severity=ReadinessSeverity.warning,
                message="لم يتم تسجيل ملف مرفوع للمشروع الحالي.",
            )
        )

    if project.extracted_text is None or not project.extracted_text.text.strip():
        issues.append(
            ProjectReadinessIssue(
                code="missing_extracted_text",
                severity=ReadinessSeverity.warning,
                message="لا يوجد نص مستخرج محفوظ في المشروع الحالي.",
            )
        )

    if not project.questions:
        issues.append(
            ProjectReadinessIssue(
                code="missing_questions",
                severity=ReadinessSeverity.error,
                message="لا توجد بطاقات أسئلة للتصدير.",
            )
        )

    if project.questions and not active_questions:
        issues.append(
            ProjectReadinessIssue(
                code="all_questions_deleted",
                severity=ReadinessSeverity.error,
                message="كل الأسئلة محذوفة؛ لا يمكن إنشاء ورقة نهائية فارغة.",
            )
        )

    if active_questions and empty_translation_questions:
        issues.append(
            ProjectReadinessIssue(
                code="empty_translations",
                severity=ReadinessSeverity.error,
                message=f"يوجد {len(empty_translation_questions)} سؤالًا بلا ترجمة عربية.",
            )
        )

    if active_questions and len(translated_questions) < len(active_questions):
        issues.append(
            ProjectReadinessIssue(
                code="translation_may_need_review",
                severity=ReadinessSeverity.warning,
                message="بعض الأسئلة تبدو غير مترجمة أو ترجمتها مطابقة للنص الأصلي.",
            )
        )

    if needs_review_questions:
        issues.append(
            ProjectReadinessIssue(
                code="questions_need_review",
                severity=ReadinessSeverity.warning,
                message=f"يوجد {len(needs_review_questions)} سؤالًا لا يزال بحالة يحتاج مراجعة.",
            )
        )

    if missing_marks_questions:
        issues.append(
            ProjectReadinessIssue(
                code="missing_marks",
                severity=ReadinessSeverity.warning,
                message=f"يوجد {len(missing_marks_questions)} سؤالًا بلا درجة محددة.",
            )
        )

    for index, question in enumerate(active_questions, start=1):
        parts_total = parts_totals[question.id]

        if parts_total is None:
            continue

        question_number = _question_display_number(question, index)

        if question.marks is None:
            issues.append(
                ProjectReadinessIssue(
                    code="question_marks_inferred_from_parts",
                    severity=ReadinessSeverity.warning,
                    message=(
                        f"السؤال {question_number} بلا درجة عامة؛ "
                        f"مجموع أجزائه المحسوب هو {parts_total}. "
                        "سيُستخدم هذا المجموع في التصدير ما لم تُحدَّد درجة عامة."
                    ),
                )
            )
        elif question.marks != parts_total:
            issues.append(
                ProjectReadinessIssue(
                    code="question_parts_marks_mismatch",
                    severity=ReadinessSeverity.warning,
                    message=(
                        f"درجة السؤال {question_number} ({question.marks}) "
                        f"لا تتطابق مع مجموع أجزائه ({parts_total}). "
                        "التصدير متاح وسيستخدم الدرجة العامة الحالية؛ "
                        "يمكن اعتماد مجموع الأجزاء من شاشة المراجعة."
                    ),
                )
            )

    total_marks = sum(
        _question_effective_marks(question) or 0
        for question in active_questions
    )
    has_blocking_errors = any(
        issue.severity == ReadinessSeverity.error
        for issue in issues
    )

    return ProjectReadinessReport(
        ready=not has_blocking_errors,
        exportable_question_count=len(active_questions),
        translated_question_count=len(translated_questions),
        deleted_question_count=len(deleted_questions),
        total_marks=total_marks,
        issues=issues,
    )
