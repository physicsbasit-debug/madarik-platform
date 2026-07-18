from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.models.project import (
    ExportFormat,
    ExtractedTextInfo,
    FullExamEndToEndAcceptanceStatus,
    FullExamEndToEndStageKey,
    FullExamEndToEndStageStatus,
    FullExamIntakeReport,
    FullExamIntakeStatus,
    FullExamQuestionSpan,
    GlossaryTerm,
    GlossaryTermStatus,
    OutputMode,
    PdfLayoutAssetInfo,
    ProjectMetadata,
    ProjectSession,
    QuestionItem,
    QuestionStatus,
    UploadedFileInfo,
)
from app.services.full_exam_end_to_end import (
    run_full_exam_end_to_end_acceptance,
)
from app.services.session_store import project_store


client = TestClient(app)


def _accepted_intake_report() -> FullExamIntakeReport:
    return FullExamIntakeReport(
        status=FullExamIntakeStatus.accepted,
        page_count=3,
        content_page_count=3,
        blank_page_count=0,
        cover_page_count=1,
        question_page_count=2,
        detected_question_count=2,
        detected_question_numbers=["1", "2"],
        reported_total_marks=5,
        detected_total_marks=5,
        multi_page_question_count=0,
        auto_linked_layout_asset_count=2,
        question_spans=[
            FullExamQuestionSpan(
                question_number="1",
                page_numbers=[2],
                page_start=2,
                page_end=2,
                detected_total_marks=2,
                linked_layout_asset_count=1,
            ),
            FullExamQuestionSpan(
                question_number="2",
                page_numbers=[3],
                page_start=3,
                page_end=3,
                detected_total_marks=3,
                linked_layout_asset_count=1,
            ),
        ],
    )


def _complete_project(
    *,
    export_formats: list[ExportFormat] | None = None,
    question_status: QuestionStatus = QuestionStatus.approved,
) -> ProjectSession:
    return ProjectSession(
        metadata=ProjectMetadata(
            paper_title="Phase 4-A6d acceptance fixture",
            subject="الفيزياء",
            grade="العاشر",
            total_marks="5",
            output_mode=OutputMode.bilingual,
            export_formats=(
                export_formats
                if export_formats is not None
                else [ExportFormat.docx, ExportFormat.pdf]
            ),
        ),
        uploaded_file=UploadedFileInfo(
            name="exam.pdf",
            size=1200,
            type="application/pdf",
        ),
        extracted_text=ExtractedTextInfo(
            text=(
                "1 State the force. [2]\n"
                "2 State the energy. [3]"
            ),
            preview="1 State the force.",
            page_count=3,
            character_count=54,
            is_text_based=True,
            message="fixture",
        ),
        questions=[
            QuestionItem(
                id="q-1",
                original_number="1",
                original_text="State the force. [2]",
                translated_text="اذكر القوة. [2]",
                marks=2,
                detected_marks=2,
                status=question_status,
                order_index=1,
                source_page_numbers=[2],
                source_page_start=2,
                source_page_end=2,
                linked_layout_asset_ids=["layout-2"],
            ),
            QuestionItem(
                id="q-2",
                original_number="2",
                original_text="State the energy. [3]",
                translated_text="اذكر الطاقة. [3]",
                marks=3,
                detected_marks=3,
                status=question_status,
                order_index=2,
                source_page_numbers=[3],
                source_page_start=3,
                source_page_end=3,
                linked_layout_asset_ids=["layout-3"],
            ),
        ],
        glossary=[
            GlossaryTerm(
                id="term-force",
                english_term="force",
                arabic_term="القوة",
                subject="الفيزياء",
                status=GlossaryTermStatus.approved,
            ),
            GlossaryTerm(
                id="term-energy",
                english_term="energy",
                arabic_term="الطاقة",
                subject="الفيزياء",
                status=GlossaryTermStatus.approved,
            ),
        ],
        layout_assets=[
            PdfLayoutAssetInfo(
                id=f"layout-{page_number}",
                name=f"page-{page_number}.png",
                size=10,
                data_base64="AA==",
                page_number=page_number,
            )
            for page_number in range(1, 4)
        ],
        full_exam_intake_report=_accepted_intake_report(),
    )


def _stage(result, key: FullExamEndToEndStageKey):
    return next(
        stage
        for stage in result.report.stages
        if stage.stage == key
    )


def test_a6d_accepts_complete_exam_and_generates_both_formats() -> None:
    result = run_full_exam_end_to_end_acceptance(
        _complete_project()
    )

    assert result.report.status == (
        FullExamEndToEndAcceptanceStatus.accepted
    )
    assert result.report.page_count == 3
    assert result.report.active_question_count == 2
    assert result.report.total_marks == 5
    assert result.report.translation_completion_percent == 100
    assert result.report.generated_formats == [
        ExportFormat.docx,
        ExportFormat.pdf,
    ]
    assert result.report.accepted_formats == [
        ExportFormat.docx,
        ExportFormat.pdf,
    ]
    assert result.export_report is not None
    assert result.export_report.status.value == "accepted"
    assert all(check.passed for check in result.report.checks)
    assert _stage(
        result,
        FullExamEndToEndStageKey.final_consistency,
    ).status == FullExamEndToEndStageStatus.accepted


def test_a6d_skips_unrequested_pdf_without_lowering_acceptance() -> None:
    result = run_full_exam_end_to_end_acceptance(
        _complete_project(export_formats=[ExportFormat.docx])
    )

    assert result.report.status == (
        FullExamEndToEndAcceptanceStatus.accepted
    )
    assert result.report.generated_formats == [ExportFormat.docx]
    assert result.report.accepted_formats == [ExportFormat.docx]
    assert _stage(
        result,
        FullExamEndToEndStageKey.pdf_export,
    ).status == FullExamEndToEndStageStatus.skipped


def test_a6d_marks_teacher_review_gaps_as_needs_review() -> None:
    result = run_full_exam_end_to_end_acceptance(
        _complete_project(
            question_status=QuestionStatus.needs_review,
        )
    )

    assert result.report.status == (
        FullExamEndToEndAcceptanceStatus.needs_review
    )
    assert _stage(
        result,
        FullExamEndToEndStageKey.translation,
    ).status == FullExamEndToEndStageStatus.needs_review
    assert _stage(
        result,
        FullExamEndToEndStageKey.readiness,
    ).status == FullExamEndToEndStageStatus.needs_review
    assert result.report.errors == []


def test_a6d_rejects_project_with_blocking_readiness_errors() -> None:
    project = ProjectSession(
        metadata=ProjectMetadata(
            export_formats=[ExportFormat.docx, ExportFormat.pdf],
        )
    )

    result = run_full_exam_end_to_end_acceptance(project)

    assert result.report.status == (
        FullExamEndToEndAcceptanceStatus.rejected
    )
    assert _stage(
        result,
        FullExamEndToEndStageKey.readiness,
    ).status == FullExamEndToEndStageStatus.failed
    assert _stage(
        result,
        FullExamEndToEndStageKey.docx_export,
    ).status == FullExamEndToEndStageStatus.skipped
    assert _stage(
        result,
        FullExamEndToEndStageKey.pdf_export,
    ).status == FullExamEndToEndStageStatus.skipped
    assert result.report.errors


def test_a6d_api_persists_gate_and_invalidates_it_after_question_edit() -> None:
    project = _complete_project()
    project_store._projects[project.id] = project
    project_store._repository.save(project)

    try:
        run_response = client.post(
            f"/api/projects/{project.id}/full-exam/acceptance/run"
        )
        assert run_response.status_code == 200
        run_body = run_response.json()
        report = run_body["full_exam_end_to_end_report"]
        assert report["status"] == "accepted"
        assert report["generated_formats"] == ["docx", "pdf"]
        assert run_body["full_exam_export_report"]["status"] == "accepted"

        get_response = client.get(
            f"/api/projects/{project.id}/full-exam/acceptance"
        )
        assert get_response.status_code == 200
        assert get_response.json()["run_id"] == report["run_id"]

        edit_response = client.patch(
            f"/api/projects/{project.id}/questions/q-1",
            json={"status": "needs_review"},
        )
        assert edit_response.status_code == 200
        assert (
            edit_response.json()["full_exam_end_to_end_report"]
            is None
        )
        assert edit_response.json()["full_exam_export_report"] is None
    finally:
        project_store.delete(project.id)
