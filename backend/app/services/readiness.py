from __future__ import annotations

from app.models.project import (
    ProjectReadinessIssue,
    ProjectReadinessReport,
    ProjectSession,
    QuestionStatus,
    ReadinessSeverity,
)


def build_project_readiness_report(project: ProjectSession) -> ProjectReadinessReport:
    """Build a conservative export readiness report.

    Phase 1-J1 does not try to judge scientific correctness. It only prevents the
    very human achievement of exporting an empty or half-reviewed paper while
    wearing the face of confidence.
    """

    issues: list[ProjectReadinessIssue] = []
    active_questions = [question for question in project.questions if question.status != QuestionStatus.deleted]
    translated_questions = [
        question
        for question in active_questions
        if question.translated_text.strip() and question.translated_text.strip() != question.original_text.strip()
    ]
    needs_review_questions = [question for question in active_questions if question.status == QuestionStatus.needs_review]
    deleted_questions = [question for question in project.questions if question.status == QuestionStatus.deleted]
    missing_marks_questions = [question for question in active_questions if question.marks is None]
    empty_translation_questions = [question for question in active_questions if not question.translated_text.strip()]

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

    total_marks = sum(question.marks or 0 for question in active_questions)
    has_blocking_errors = any(issue.severity == ReadinessSeverity.error for issue in issues)

    return ProjectReadinessReport(
        ready=not has_blocking_errors,
        exportable_question_count=len(active_questions),
        translated_question_count=len(translated_questions),
        deleted_question_count=len(deleted_questions),
        total_marks=total_marks,
        issues=issues,
    )
