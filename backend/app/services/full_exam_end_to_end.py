from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

from app.models.project import (
    ExportFormat,
    FullExamEndToEndAcceptanceStatus,
    FullExamEndToEndCheck,
    FullExamEndToEndReport,
    FullExamEndToEndStageKey,
    FullExamEndToEndStageStatus,
    FullExamEndToEndStageSummary,
    FullExamExportAcceptanceStatus,
    FullExamExportArtifactStatus,
    FullExamExportReport,
    FullExamIntakeReport,
    FullExamIntakeStatus,
    FullExamTranslationAcceptanceStatus,
    FullExamTranslationReport,
    GlossaryTermStatus,
    ProjectReadinessReport,
    ProjectSession,
    QuestionStatus,
    ReadinessSeverity,
)
from app.services.export import (
    build_project_docx_bytes,
    build_project_pdf_bytes,
)
from app.services.full_exam_export import build_full_exam_export_report
from app.services.full_exam_intake import build_full_exam_intake_report
from app.services.full_exam_translation import (
    build_full_exam_translation_report,
)
from app.services.readiness import build_project_readiness_report


@dataclass(frozen=True)
class FullExamEndToEndRunResult:
    """Reports produced by one non-destructive acceptance gate run."""

    report: FullExamEndToEndReport
    intake_report: FullExamIntakeReport | None
    translation_report: FullExamTranslationReport | None
    readiness_report: ProjectReadinessReport
    export_report: FullExamExportReport | None


_STAGE_LABELS = {
    FullExamEndToEndStageKey.intake: "إدخال الورقة",
    FullExamEndToEndStageKey.layout_assets: "لقطات صفحات PDF",
    FullExamEndToEndStageKey.glossary: "القاموس العلمي",
    FullExamEndToEndStageKey.translation: "الترجمة والمراجعة",
    FullExamEndToEndStageKey.readiness: "جاهزية التصدير",
    FullExamEndToEndStageKey.docx_export: "تصدير DOCX",
    FullExamEndToEndStageKey.pdf_export: "تصدير PDF",
    FullExamEndToEndStageKey.final_consistency: "الاتساق النهائي",
}


def _elapsed_ms(started_at: float) -> float:
    return round(max(0.0, (perf_counter() - started_at) * 1000), 2)


def _unique_formats(formats: Iterable[ExportFormat]) -> list[ExportFormat]:
    result: list[ExportFormat] = []
    for item in formats:
        if item not in result:
            result.append(item)
    return result


def _active_questions(project: ProjectSession):
    return sorted(
        (
            question
            for question in project.questions
            if question.status != QuestionStatus.deleted
        ),
        key=lambda question: question.order_index,
    )


def _stage(
    stage: FullExamEndToEndStageKey,
    status: FullExamEndToEndStageStatus,
    started_at: float,
    message: str,
    *,
    checks: list[FullExamEndToEndCheck] | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
) -> FullExamEndToEndStageSummary:
    return FullExamEndToEndStageSummary(
        stage=stage,
        status=status,
        duration_ms=_elapsed_ms(started_at),
        message=message,
        checks=checks or [],
        warnings=warnings or [],
        errors=errors or [],
    )


def _intake_stage(
    project: ProjectSession,
) -> tuple[FullExamIntakeReport | None, FullExamEndToEndStageSummary]:
    started_at = perf_counter()
    extracted = project.extracted_text

    if extracted and extracted.pages:
        report = build_full_exam_intake_report(
            extracted.pages,
            questions=project.questions or None,
        )
    else:
        report = project.full_exam_intake_report

    if report is None:
        return None, _stage(
            FullExamEndToEndStageKey.intake,
            FullExamEndToEndStageStatus.pending,
            started_at,
            "لا يوجد تقرير قبول محفوظ لبنية ورقة كاملة.",
            checks=[
                FullExamEndToEndCheck(
                    code="intake_report_available",
                    passed=False,
                    message="تقرير قبول الإدخال غير متاح.",
                )
            ],
            warnings=[
                "ارفع PDF نصيًا كاملًا ثم نفّذ تقسيم الأسئلة قبل تشغيل البوابة."
            ],
        )

    if report.status == FullExamIntakeStatus.accepted:
        stage_status = FullExamEndToEndStageStatus.accepted
    elif report.status == FullExamIntakeStatus.needs_review:
        stage_status = FullExamEndToEndStageStatus.needs_review
    else:
        stage_status = FullExamEndToEndStageStatus.failed

    return report, _stage(
        FullExamEndToEndStageKey.intake,
        stage_status,
        started_at,
        (
            f"تم رصد {report.detected_question_count} سؤالًا في "
            f"{report.page_count} صفحة."
        ),
        checks=[
            FullExamEndToEndCheck(
                code=f"intake_{check.code}",
                passed=check.passed,
                message=check.message,
            )
            for check in report.checks
        ],
        warnings=list(report.warnings),
        errors=(
            ["تقرير إدخال الورقة انتهى بحالة rejected."]
            if report.status == FullExamIntakeStatus.rejected
            else []
        ),
    )


def _layout_stage(
    project: ProjectSession,
    intake_report: FullExamIntakeReport | None,
) -> FullExamEndToEndStageSummary:
    started_at = perf_counter()
    active_questions = _active_questions(project)
    asset_pages = {
        asset.page_number
        for asset in project.layout_assets
    }

    expected_pages: set[int] = set()
    if intake_report and intake_report.page_count:
        expected_pages = set(range(1, intake_report.page_count + 1))
    elif project.extracted_text:
        expected_pages = set(range(1, project.extracted_text.page_count + 1))

    missing_pages = sorted(expected_pages - asset_pages)
    assets_by_id = {asset.id: asset for asset in project.layout_assets}
    questions_missing_links: list[str] = []

    for question in active_questions:
        if not question.source_page_numbers:
            continue
        linked_pages = {
            assets_by_id[asset_id].page_number
            for asset_id in question.linked_layout_asset_ids
            if asset_id in assets_by_id
        }
        if not set(question.source_page_numbers).issubset(linked_pages):
            questions_missing_links.append(question.original_number)

    checks = [
        FullExamEndToEndCheck(
            code="layout_assets_available",
            passed=bool(project.layout_assets),
            message=(
                f"تم حفظ {len(project.layout_assets)} لقطة صفحة."
                if project.layout_assets
                else "لا توجد لقطات صفحات PDF محفوظة."
            ),
        ),
        FullExamEndToEndCheck(
            code="all_pdf_pages_covered",
            passed=not expected_pages or not missing_pages,
            message=(
                "تغطي اللقطات جميع صفحات PDF."
                if not missing_pages
                else "الصفحات غير المغطاة باللقطات: "
                + "، ".join(str(value) for value in missing_pages)
            ),
        ),
        FullExamEndToEndCheck(
            code="question_page_links_preserved",
            passed=not questions_missing_links,
            message=(
                "روابط صفحات المصدر محفوظة لكل سؤال."
                if not questions_missing_links
                else "أسئلة تحتاج استكمال روابط الصفحات: "
                + "، ".join(questions_missing_links)
            ),
        ),
    ]

    if not project.layout_assets:
        status = FullExamEndToEndStageStatus.pending
    elif missing_pages or questions_missing_links:
        status = FullExamEndToEndStageStatus.needs_review
    else:
        status = FullExamEndToEndStageStatus.accepted

    warnings: list[str] = []
    if missing_pages:
        warnings.append(
            f"لم تُنشأ لقطات لعدد {len(missing_pages)} من صفحات المصدر."
        )
    if questions_missing_links:
        warnings.append(
            f"تحتاج {len(questions_missing_links)} أسئلة إلى استكمال روابط اللقطات."
        )

    return _stage(
        FullExamEndToEndStageKey.layout_assets,
        status,
        started_at,
        (
            f"اللقطات المحفوظة: {len(project.layout_assets)}، "
            f"الصفحات المتوقعة: {len(expected_pages)}."
        ),
        checks=checks,
        warnings=warnings,
    )


def _glossary_stage(project: ProjectSession) -> FullExamEndToEndStageSummary:
    started_at = perf_counter()
    approved = [
        term
        for term in project.glossary
        if (
            term.status == GlossaryTermStatus.approved
            and term.english_term.strip()
            and term.arabic_term.strip()
        )
    ]
    pending = [
        term
        for term in project.glossary
        if term not in approved
    ]

    checks = [
        FullExamEndToEndCheck(
            code="glossary_available",
            passed=bool(project.glossary),
            message=(
                f"يتضمن القاموس {len(project.glossary)} مصطلحًا."
                if project.glossary
                else "لم يُنشأ قاموس علمي للمشروع."
            ),
        ),
        FullExamEndToEndCheck(
            code="glossary_review_complete",
            passed=bool(project.glossary) and not pending,
            message=(
                "جميع مصطلحات القاموس معتمدة."
                if project.glossary and not pending
                else f"توجد {len(pending)} مصطلحات غير مكتملة الاعتماد."
            ),
        ),
    ]

    if not project.glossary:
        status = FullExamEndToEndStageStatus.pending
        warnings = ["لم يُنشأ قاموس علمي قبل الترجمة."]
    elif pending:
        status = FullExamEndToEndStageStatus.needs_review
        warnings = [
            f"توجد {len(pending)} مصطلحات تحتاج مراجعة أو استكمال النص."
        ]
    else:
        status = FullExamEndToEndStageStatus.accepted
        warnings = []

    return _stage(
        FullExamEndToEndStageKey.glossary,
        status,
        started_at,
        f"المصطلحات المعتمدة: {len(approved)} من {len(project.glossary)}.",
        checks=checks,
        warnings=warnings,
    )


def _translation_stage(
    project: ProjectSession,
    intake_report: FullExamIntakeReport | None,
) -> tuple[
    FullExamTranslationReport | None,
    FullExamEndToEndStageSummary,
]:
    started_at = perf_counter()

    if not project.questions:
        return None, _stage(
            FullExamEndToEndStageKey.translation,
            FullExamEndToEndStageStatus.pending,
            started_at,
            "لا توجد أسئلة لبناء تقرير ترجمة كامل.",
            checks=[
                FullExamEndToEndCheck(
                    code="translation_questions_available",
                    passed=False,
                    message="لا توجد بطاقات أسئلة.",
                )
            ],
            warnings=["قسّم النص المستخرج إلى أسئلة قبل تشغيل الترجمة."],
        )

    report = build_full_exam_translation_report(
        project.questions,
        project.glossary,
        project.translation_batch_summary,
        intake_report,
    )

    if report.status == FullExamTranslationAcceptanceStatus.accepted:
        stage_status = FullExamEndToEndStageStatus.accepted
    elif report.status in {
        FullExamTranslationAcceptanceStatus.needs_review,
        FullExamTranslationAcceptanceStatus.incomplete,
    }:
        stage_status = FullExamEndToEndStageStatus.needs_review
    else:
        stage_status = FullExamEndToEndStageStatus.failed

    return report, _stage(
        FullExamEndToEndStageKey.translation,
        stage_status,
        started_at,
        (
            f"اكتملت ترجمة {report.translated_questions} من "
            f"{report.active_questions} أسئلة نشطة "
            f"({report.completion_percent:.0f}%)."
        ),
        checks=[
            FullExamEndToEndCheck(
                code=f"translation_{check.code}",
                passed=check.passed,
                message=check.message,
            )
            for check in report.checks
        ],
        warnings=list(report.warnings),
        errors=(
            ["تقرير الترجمة انتهى بحالة failed."]
            if report.status == FullExamTranslationAcceptanceStatus.failed
            else []
        ),
    )


def _readiness_stage(
    project: ProjectSession,
) -> tuple[ProjectReadinessReport, FullExamEndToEndStageSummary]:
    started_at = perf_counter()
    report = build_project_readiness_report(project)
    errors = [
        issue.message
        for issue in report.issues
        if issue.severity == ReadinessSeverity.error
    ]
    warnings = [
        issue.message
        for issue in report.issues
        if issue.severity == ReadinessSeverity.warning
    ]

    if errors:
        stage_status = FullExamEndToEndStageStatus.failed
    elif warnings:
        stage_status = FullExamEndToEndStageStatus.needs_review
    else:
        stage_status = FullExamEndToEndStageStatus.accepted

    return report, _stage(
        FullExamEndToEndStageKey.readiness,
        stage_status,
        started_at,
        (
            f"الأسئلة القابلة للتصدير: {report.exportable_question_count}، "
            f"مجموع الدرجات: {report.total_marks}."
        ),
        checks=[
            FullExamEndToEndCheck(
                code="readiness_no_blocking_errors",
                passed=not errors,
                message=(
                    "لا توجد ملاحظات مانعة من التصدير."
                    if not errors
                    else f"توجد {len(errors)} ملاحظات مانعة."
                ),
            ),
            FullExamEndToEndCheck(
                code="readiness_translation_coverage",
                passed=(
                    report.exportable_question_count > 0
                    and report.translated_question_count
                    == report.exportable_question_count
                ),
                message=(
                    f"الأسئلة المترجمة: {report.translated_question_count} "
                    f"من {report.exportable_question_count}."
                ),
            ),
        ],
        warnings=warnings,
        errors=errors,
    )


def _export_stage(
    project: ProjectSession,
    artifact_format: ExportFormat,
    existing_report: FullExamExportReport | None,
    *,
    requested: bool,
    readiness_report: ProjectReadinessReport,
) -> tuple[
    FullExamExportReport | None,
    FullExamEndToEndStageSummary,
]:
    started_at = perf_counter()
    stage_key = (
        FullExamEndToEndStageKey.docx_export
        if artifact_format == ExportFormat.docx
        else FullExamEndToEndStageKey.pdf_export
    )

    if not requested:
        return existing_report, _stage(
            stage_key,
            FullExamEndToEndStageStatus.skipped,
            started_at,
            f"صيغة {artifact_format.value.upper()} غير مطلوبة في إعدادات المشروع.",
        )

    if not readiness_report.ready:
        return existing_report, _stage(
            stage_key,
            FullExamEndToEndStageStatus.skipped,
            started_at,
            "تم تجاوز إنشاء الملف بسبب ملاحظات جاهزية مانعة.",
            warnings=[
                f"لم يُنشأ {artifact_format.value.upper()} لأن الجاهزية غير مكتملة."
            ],
        )

    try:
        artifact_bytes = (
            build_project_docx_bytes(project)
            if artifact_format == ExportFormat.docx
            else build_project_pdf_bytes(project)
        )
        report = build_full_exam_export_report(
            project,
            artifact_format,
            artifact_bytes,
            existing_report,
        )
        summary = next(
            (
                item
                for item in report.formats
                if item.format == artifact_format
            ),
            None,
        )
        if summary is None:
            raise RuntimeError(
                "لم يُنشأ ملخص فحص للصيغة المطلوبة."
            )

        if summary.status == FullExamExportArtifactStatus.accepted:
            stage_status = FullExamEndToEndStageStatus.accepted
        elif summary.status == FullExamExportArtifactStatus.needs_review:
            stage_status = FullExamEndToEndStageStatus.needs_review
        else:
            stage_status = FullExamEndToEndStageStatus.failed

        return report, _stage(
            stage_key,
            stage_status,
            started_at,
            (
                f"تم إنشاء {artifact_format.value.upper()} بحجم "
                f"{summary.byte_size} بايت وفحص بنيته."
            ),
            checks=[
                FullExamEndToEndCheck(
                    code=f"{artifact_format.value}_{check.code}",
                    passed=check.passed,
                    message=check.message,
                )
                for check in summary.checks
            ],
            warnings=list(summary.warnings),
            errors=(
                [f"فشل فحص ملف {artifact_format.value.upper()}."]
                if summary.status == FullExamExportArtifactStatus.failed
                else []
            ),
        )
    except Exception as exc:  # pragma: no cover - guarded by API tests
        return existing_report, _stage(
            stage_key,
            FullExamEndToEndStageStatus.failed,
            started_at,
            f"تعذر إنشاء أو فحص {artifact_format.value.upper()}.",
            errors=[str(exc)],
        )


def _final_consistency_stage(
    project: ProjectSession,
    intake_report: FullExamIntakeReport | None,
    translation_report: FullExamTranslationReport | None,
    readiness_report: ProjectReadinessReport,
    export_report: FullExamExportReport | None,
    requested_formats: list[ExportFormat],
) -> FullExamEndToEndStageSummary:
    started_at = perf_counter()
    active_questions = _active_questions(project)
    active_count = len(active_questions)

    intake_count_matches = (
        intake_report is not None
        and intake_report.detected_question_count == active_count
    )
    translation_count_matches = (
        translation_report is not None
        and translation_report.active_questions == active_count
    )
    export_count_matches = (
        export_report is not None
        and export_report.active_question_count == active_count
    )
    marks_match = (
        export_report is not None
        and export_report.expected_total_marks == readiness_report.total_marks
    )
    requested_formats_accepted = (
        export_report is not None
        and all(
            item in export_report.accepted_formats
            for item in requested_formats
        )
    )

    checks = [
        FullExamEndToEndCheck(
            code="question_count_matches_intake",
            passed=intake_count_matches,
            message=(
                "عدد الأسئلة النشطة يطابق تقرير الإدخال."
                if intake_count_matches
                else "عدد الأسئلة النشطة لا يطابق تقرير الإدخال."
            ),
        ),
        FullExamEndToEndCheck(
            code="question_count_matches_translation",
            passed=translation_count_matches,
            message=(
                "عدد الأسئلة يطابق تقرير الترجمة."
                if translation_count_matches
                else "عدد الأسئلة لا يطابق تقرير الترجمة."
            ),
        ),
        FullExamEndToEndCheck(
            code="question_count_matches_export",
            passed=export_count_matches,
            message=(
                "عدد الأسئلة يطابق تقرير التصدير."
                if export_count_matches
                else "عدد الأسئلة لا يطابق تقرير التصدير."
            ),
        ),
        FullExamEndToEndCheck(
            code="total_marks_consistent",
            passed=marks_match,
            message=(
                "مجموع الدرجات ثابت بين الجاهزية والتصدير."
                if marks_match
                else "مجموع الدرجات غير متسق بين الجاهزية والتصدير."
            ),
        ),
        FullExamEndToEndCheck(
            code="requested_formats_accepted",
            passed=requested_formats_accepted,
            message=(
                "اجتازت جميع صيغ التصدير المطلوبة الفحص."
                if requested_formats_accepted
                else "لم تجتز جميع صيغ التصدير المطلوبة الفحص."
            ),
        ),
    ]

    if all(check.passed for check in checks):
        status = FullExamEndToEndStageStatus.accepted
        warnings: list[str] = []
        errors: list[str] = []
    elif (
        export_report is None
        or export_report.status
        in {
            FullExamExportAcceptanceStatus.incomplete,
            FullExamExportAcceptanceStatus.needs_review,
        }
    ):
        status = FullExamEndToEndStageStatus.needs_review
        warnings = [
            "لم يكتمل الاتساق النهائي بين تقارير الإدخال والترجمة والتصدير."
        ]
        errors = []
    else:
        status = FullExamEndToEndStageStatus.failed
        warnings = []
        errors = [
            "فشلت واحدة أو أكثر من فحوص الاتساق النهائي."
        ]

    return _stage(
        FullExamEndToEndStageKey.final_consistency,
        status,
        started_at,
        (
            f"تمت مقارنة {active_count} سؤالًا و"
            f"{readiness_report.total_marks} درجة عبر التقارير."
        ),
        checks=checks,
        warnings=warnings,
        errors=errors,
    )


def _prefixed_messages(
    stages: list[FullExamEndToEndStageSummary],
    attribute: str,
) -> list[str]:
    messages: list[str] = []
    for stage in stages:
        stage_label = _STAGE_LABELS[stage.stage]
        values = getattr(stage, attribute)
        for value in values:
            message = f"{stage_label}: {value}"
            if message not in messages:
                messages.append(message)
    return messages


def run_full_exam_end_to_end_acceptance(
    project: ProjectSession,
) -> FullExamEndToEndRunResult:
    """Validate the current full-exam project without invoking an AI provider.

    The gate recomputes phase reports from the current project, creates and
    inspects the requested export artifacts in memory, and persists only reports.
    It never silently translates text or overwrites teacher-reviewed content.
    """

    total_started_at = perf_counter()
    working = project.model_copy(deep=True)
    stages: list[FullExamEndToEndStageSummary] = []

    intake_report, intake_stage = _intake_stage(working)
    working.full_exam_intake_report = intake_report
    stages.append(intake_stage)

    stages.append(_layout_stage(working, intake_report))
    stages.append(_glossary_stage(working))

    translation_report, translation_stage = _translation_stage(
        working,
        intake_report,
    )
    working.full_exam_translation_report = translation_report
    stages.append(translation_stage)

    readiness_report, readiness_stage = _readiness_stage(working)
    stages.append(readiness_stage)

    requested_formats = _unique_formats(
        working.metadata.export_formats
        or [ExportFormat.docx, ExportFormat.pdf]
    )
    export_report: FullExamExportReport | None = None

    for artifact_format in (ExportFormat.docx, ExportFormat.pdf):
        export_report, export_stage = _export_stage(
            working,
            artifact_format,
            export_report,
            requested=artifact_format in requested_formats,
            readiness_report=readiness_report,
        )
        working.full_exam_export_report = export_report
        stages.append(export_stage)

    stages.append(
        _final_consistency_stage(
            working,
            intake_report,
            translation_report,
            readiness_report,
            export_report,
            requested_formats,
        )
    )

    required_stage_keys = {
        FullExamEndToEndStageKey.intake,
        FullExamEndToEndStageKey.layout_assets,
        FullExamEndToEndStageKey.glossary,
        FullExamEndToEndStageKey.translation,
        FullExamEndToEndStageKey.readiness,
        FullExamEndToEndStageKey.final_consistency,
    }
    if ExportFormat.docx in requested_formats:
        required_stage_keys.add(FullExamEndToEndStageKey.docx_export)
    if ExportFormat.pdf in requested_formats:
        required_stage_keys.add(FullExamEndToEndStageKey.pdf_export)

    required_stages = [
        stage
        for stage in stages
        if stage.stage in required_stage_keys
    ]

    if any(
        stage.status == FullExamEndToEndStageStatus.failed
        for stage in required_stages
    ):
        status = FullExamEndToEndAcceptanceStatus.rejected
    elif any(
        stage.status
        in {
            FullExamEndToEndStageStatus.needs_review,
            FullExamEndToEndStageStatus.pending,
        }
        for stage in required_stages
    ):
        status = FullExamEndToEndAcceptanceStatus.needs_review
    else:
        status = FullExamEndToEndAcceptanceStatus.accepted

    all_required_completed = all(
        stage.status
        not in {
            FullExamEndToEndStageStatus.pending,
            FullExamEndToEndStageStatus.skipped,
        }
        for stage in required_stages
    )
    all_required_accepted = all(
        stage.status == FullExamEndToEndStageStatus.accepted
        for stage in required_stages
    )
    errors = _prefixed_messages(stages, "errors")
    warnings = _prefixed_messages(stages, "warnings")

    report = FullExamEndToEndReport(
        status=status,
        total_duration_ms=_elapsed_ms(total_started_at),
        page_count=(
            intake_report.page_count
            if intake_report
            else (
                working.extracted_text.page_count
                if working.extracted_text
                else 0
            )
        ),
        active_question_count=len(_active_questions(working)),
        total_marks=readiness_report.total_marks,
        translation_completion_percent=(
            translation_report.completion_percent
            if translation_report
            else 0
        ),
        requested_formats=requested_formats,
        generated_formats=(
            list(export_report.generated_formats)
            if export_report
            else []
        ),
        accepted_formats=(
            list(export_report.accepted_formats)
            if export_report
            else []
        ),
        stages=stages,
        checks=[
            FullExamEndToEndCheck(
                code="required_stages_completed",
                passed=all_required_completed,
                message=(
                    "اكتملت جميع مراحل القبول المطلوبة."
                    if all_required_completed
                    else "توجد مراحل قبول مطلوبة لم تكتمل."
                ),
            ),
            FullExamEndToEndCheck(
                code="required_stages_accepted",
                passed=all_required_accepted,
                message=(
                    "اجتازت جميع مراحل القبول المطلوبة."
                    if all_required_accepted
                    else "توجد مراحل لم تصل إلى حالة accepted."
                ),
            ),
            FullExamEndToEndCheck(
                code="no_pipeline_errors",
                passed=not errors,
                message=(
                    "لم تسجل البوابة أخطاء تنفيذ."
                    if not errors
                    else f"سجلت البوابة {len(errors)} أخطاء."
                ),
            ),
            FullExamEndToEndCheck(
                code="requested_formats_generated",
                passed=(
                    export_report is not None
                    and all(
                        item in export_report.generated_formats
                        for item in requested_formats
                    )
                ),
                message=(
                    "تم إنشاء جميع صيغ التصدير المطلوبة."
                    if export_report is not None
                    and all(
                        item in export_report.generated_formats
                        for item in requested_formats
                    )
                    else "لم تُنشأ جميع صيغ التصدير المطلوبة."
                ),
            ),
        ],
        warnings=warnings,
        errors=errors,
    )

    return FullExamEndToEndRunResult(
        report=report,
        intake_report=intake_report,
        translation_report=translation_report,
        readiness_report=readiness_report,
        export_report=export_report,
    )
