from __future__ import annotations

from pathlib import Path

from app.models.assessment import (
    AssessmentDraft,
    AssessmentExportResponse,
    AssessmentStudentPaperPreview,
    AssessmentStudentPaperQuestion,
    AssessmentStudentPaperSection,
)
from app.services.assessment_builder import (
    build_assessment_detail,
)
from app.services.question_bank_repository import (
    QuestionBankRepository,
)


EXPORT_DIR = Path("data/exports/assessments")


def build_student_paper_preview(
    draft: AssessmentDraft,
    question_bank_repository: QuestionBankRepository,
) -> AssessmentStudentPaperPreview:
    detail = build_assessment_detail(
        draft,
        question_bank_repository,
    )

    section_map = {
        section.id: AssessmentStudentPaperSection(
            id=section.id,
            title=section.title,
            instructions=section.instructions,
            order_index=section.order_index,
        )
        for section in sorted(
            draft.sections,
            key=lambda section: section.order_index,
        )
    }

    fallback_section = AssessmentStudentPaperSection(
        id="unsectioned",
        title="أسئلة دون قسم",
        order_index=9999,
    )

    for number, question in enumerate(
        sorted(
            detail.questions,
            key=lambda item: item.order_index,
        ),
        start=1,
    ):
        target = (
            section_map.get(question.section_id)
            if question.section_id
            else None
        ) or fallback_section

        target.questions.append(
            AssessmentStudentPaperQuestion(
                bank_item_id=question.bank_item_id,
                number=number,
                question_number=question.question_number,
                text=question.text,
                marks=question.marks,
                section_id=question.section_id,
                section_title=target.title,
            )
        )

    sections = [
        section
        for section in sorted(
            section_map.values(),
            key=lambda section: section.order_index,
        )
        if section.questions
    ]
    if fallback_section.questions:
        sections.append(fallback_section)

    issues: list[str] = []
    if not draft.blueprint.title.strip():
        issues.append("عنوان الاختبار غير موجود.")
    if not sections:
        issues.append("لا توجد أسئلة في المسودة.")
    if detail.balance.selected_marks != draft.blueprint.total_marks:
        issues.append(
            "مجموع درجات الأسئلة لا يطابق الدرجة الكلية."
        )
    if len(detail.questions) != draft.blueprint.target_question_count:
        issues.append(
            "عدد الأسئلة الفعلي لا يطابق العدد المستهدف."
        )

    return AssessmentStudentPaperPreview(
        draft_id=draft.id,
        title=draft.blueprint.title,
        grade=draft.blueprint.grade,
        science_domain=draft.blueprint.science_domain,
        subject_id=draft.blueprint.subject_id,
        duration_minutes=draft.blueprint.duration_minutes,
        total_marks=draft.blueprint.total_marks,
        question_count=len(detail.questions),
        sections=sections,
        export_ready=not issues,
        issues=issues,
    )


def _render_plain_text(
    preview: AssessmentStudentPaperPreview,
) -> str:
    lines = [
        preview.title,
        f"الصف: {preview.grade}",
        f"الزمن: {preview.duration_minutes} دقيقة",
        f"الدرجة الكلية: {preview.total_marks}",
        "",
    ]

    for section in preview.sections:
        lines.append(section.title)
        if section.instructions:
            lines.append(section.instructions)
        lines.append("")

        for question in section.questions:
            lines.append(
                f"{question.number}. "
                f"{question.text} "
                f"({question.marks} درجات)"
            )
            lines.append("")

    lines.append("صفحة الإجابة")
    lines.append("")
    for section in preview.sections:
        for question in section.questions:
            lines.append(
                f"{question.number}. "
                + "_" * 60
            )

    return "\n".join(lines)


def export_assessment_foundation(
    draft: AssessmentDraft,
    question_bank_repository: QuestionBankRepository,
    output_format: str,
) -> AssessmentExportResponse:
    preview = build_student_paper_preview(
        draft,
        question_bank_repository,
    )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = (
        draft.blueprint.title.strip().replace("/", "-")
        or "assessment"
    )
    suffix = (
        ".docx.txt"
        if output_format == "docx"
        else ".pdf.txt"
    )
    filename = f"{safe_title}-{draft.id}{suffix}"
    path = EXPORT_DIR / filename

    path.write_text(
        _render_plain_text(preview),
        encoding="utf-8",
    )

    return AssessmentExportResponse(
        draft_id=draft.id,
        format=output_format,
        filename=filename,
        path=str(path),
        export_ready=preview.export_ready,
        issues=preview.issues,
    )
