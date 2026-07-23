from __future__ import annotations

import base64
from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient
from PIL import Image as PILImage
from pypdf import PdfReader

from app.main import app
from app.models.project import (
    ExportFormat,
    FullExamExportAcceptanceStatus,
    FullExamExportArtifactStatus,
    FullExamIntakeReport,
    FullExamIntakeStatus,
    FullExamTranslationAcceptanceStatus,
    FullExamTranslationReport,
    OutputMode,
    ProjectMetadata,
    ProjectSession,
    QuestionAssetInfo,
    QuestionItem,
    QuestionPart,
)
from app.services.export import (
    build_project_docx_bytes,
    build_project_pdf_bytes,
)
from app.services.full_exam_export import (
    EXPORT_MANIFEST_PREFIX,
    _pdf_image_count,
    _pdf_question_heading_count,
    build_full_exam_export_report,
)
from app.services.session_store import project_store


client = TestClient(app)


def _png_asset(asset_id: str = "asset-1") -> QuestionAssetInfo:
    image = PILImage.new("RGB", (80, 50), (255, 255, 255))
    output = BytesIO()
    image.save(output, format="PNG")
    payload = output.getvalue()
    return QuestionAssetInfo(
        id=asset_id,
        name=f"{asset_id}.png",
        size=len(payload),
        type="image/png",
        data_base64=base64.b64encode(payload).decode("ascii"),
    )


def _accepted_intake_report() -> FullExamIntakeReport:
    return FullExamIntakeReport(
        status=FullExamIntakeStatus.accepted,
        page_count=4,
        content_page_count=4,
        question_page_count=3,
        cover_page_count=1,
        detected_question_count=2,
        detected_question_numbers=["1", "2"],
        reported_total_marks=5,
        detected_total_marks=5,
        multi_page_question_count=1,
    )


def _accepted_translation_report() -> FullExamTranslationReport:
    return FullExamTranslationReport(
        status=FullExamTranslationAcceptanceStatus.accepted,
        total_questions=2,
        active_questions=2,
        translated_questions=2,
        accepted_questions=2,
        completion_percent=100,
        total_items=4,
        translated_items=4,
        source_page_linked_questions=2,
        multi_page_questions=1,
    )


def _full_exam_project(
    *,
    export_formats: list[ExportFormat] | None = None,
    include_translation_report: bool = True,
    invalid_attachment: bool = False,
) -> ProjectSession:
    attachment = _png_asset()
    if invalid_attachment:
        attachment = attachment.model_copy(
            update={"data_base64": "not-valid-base64"}
        )

    project = ProjectSession(
        metadata=ProjectMetadata(
            paper_title="Full exam export acceptance",
            subject="الفيزياء",
            grade="العاشر",
            total_marks="5",
            output_mode=OutputMode.bilingual,
            export_formats=export_formats
            or [ExportFormat.docx, ExportFormat.pdf],
        ),
        questions=[
            QuestionItem(
                id="question-1",
                original_number="1",
                original_text="State the unit of force. [2]",
                translated_text="اذكر وحدة القوة. [2]",
                marks=2,
                detected_marks=2,
                order_index=1,
                source_page_numbers=[2],
                source_page_start=2,
                source_page_end=2,
                linked_layout_asset_ids=["layout-page-2"],
                attachments=[attachment],
            ),
            QuestionItem(
                id="question-2",
                original_number="2",
                original_text="RAW PARENT TEXT MUST NOT BE EXPORTED",
                translated_text="",
                order_index=2,
                source_page_numbers=[3, 4],
                source_page_start=3,
                source_page_end=4,
                linked_layout_asset_ids=["layout-page-3", "layout-page-4"],
                parts=[
                    QuestionPart(
                        id="part-parent",
                        label="(a)",
                        original_text="",
                        translated_text="",
                        marks=3,
                        order_index=1,
                    ),
                    QuestionPart(
                        id="part-i",
                        label="(i)",
                        original_text="State the direction.",
                        translated_text="اذكر الاتجاه.",
                        marks=1,
                        parent_id="part-parent",
                        order_index=2,
                    ),
                    QuestionPart(
                        id="part-ii",
                        label="(ii)",
                        original_text="Calculate the force.",
                        translated_text="احسب القوة.",
                        marks=2,
                        parent_id="part-parent",
                        order_index=3,
                    ),
                ],
            ),
        ],
        full_exam_intake_report=_accepted_intake_report(),
        full_exam_translation_report=(
            _accepted_translation_report()
            if include_translation_report
            else None
        ),
    )
    return project



class _FakePdfReference:
    def __init__(
        self,
        idnum: int,
        value: object,
    ) -> None:
        self.idnum = idnum
        self.generation = 0
        self._value = value

    def get_object(self) -> object:
        return self._value


class _FakePdfPage(dict):
    pass


class _FakePdfReader:
    def __init__(self, pages: list[_FakePdfPage]) -> None:
        self.pages = pages


def test_pdf_heading_count_handles_rtl_and_split_extraction() -> None:
    project = _full_exam_project()

    assert _pdf_question_heading_count(
        project,
        "\u202bالسؤال ١ [٢]\u202c\n"
        "State the unit of force.\n"
        "\u200f[٣] ٢\n",
    ) == 2

    assert _pdf_question_heading_count(
        project,
        "1\n[2]\n"
        "State the unit of force.\n"
        "2 [ 3 ]\n",
    ) == 2


def test_pdf_image_count_handles_nested_form_xobjects() -> None:
    image = {"/Subtype": "/Image"}
    image_reference = _FakePdfReference(30, image)
    nested_resources = {
        "/XObject": {
            "/NestedImage": image_reference,
        }
    }
    form = {
        "/Subtype": "/Form",
        "/Resources": nested_resources,
    }
    form_reference = _FakePdfReference(20, form)
    reader = _FakePdfReader(
        [
            _FakePdfPage(
                {
                    "/Resources": {
                        "/XObject": {
                            "/Form": form_reference,
                        }
                    }
                }
            )
        ]
    )

    assert _pdf_image_count(reader) == 1


def test_pdf_image_count_excludes_soft_masks() -> None:
    mask = {
        "/Subtype": "/Image",
        "/ImageMask": True,
    }
    mask_reference = _FakePdfReference(31, mask)
    image = {
        "/Subtype": "/Image",
        "/SMask": mask_reference,
    }
    image_reference = _FakePdfReference(30, image)
    reader = _FakePdfReader(
        [
            _FakePdfPage(
                {
                    "/Resources": {
                        "/XObject": {
                            "/Image": image_reference,
                            "/Mask": mask_reference,
                        }
                    }
                }
            )
        ]
    )

    assert _pdf_image_count(reader) == 1

def test_docx_report_is_incomplete_until_requested_pdf_is_generated() -> None:
    project = _full_exam_project()
    docx_bytes = build_project_docx_bytes(project)

    report = build_full_exam_export_report(
        project,
        ExportFormat.docx,
        docx_bytes,
    )

    document = Document(BytesIO(docx_bytes))
    assert document.core_properties.subject.startswith(EXPORT_MANIFEST_PREFIX)
    assert report.status == FullExamExportAcceptanceStatus.incomplete
    assert report.generated_formats == [ExportFormat.docx]
    assert report.formats[0].status == FullExamExportArtifactStatus.accepted
    assert report.formats[0].exported_question_count == 2
    assert report.formats[0].detected_total_marks == 5


def test_docx_and_pdf_accept_full_structure_without_duplicate_marks_or_assets() -> None:
    project = _full_exam_project()
    docx_bytes = build_project_docx_bytes(project)
    docx_report = build_full_exam_export_report(
        project,
        ExportFormat.docx,
        docx_bytes,
    )
    pdf_bytes = build_project_pdf_bytes(project)
    final_report = build_full_exam_export_report(
        project,
        ExportFormat.pdf,
        pdf_bytes,
        docx_report,
    )

    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    assert str(pdf_reader.metadata.subject).startswith(EXPORT_MANIFEST_PREFIX)
    assert final_report.status == FullExamExportAcceptanceStatus.accepted
    assert final_report.active_question_count == 2
    assert final_report.expected_total_marks == 5
    assert final_report.expected_part_count == 3
    assert final_report.expected_attachment_count == 1
    assert final_report.source_page_linked_questions == 2
    assert final_report.multi_page_questions == 1
    assert final_report.accepted_formats == [
        ExportFormat.docx,
        ExportFormat.pdf,
    ]
    assert all(
        summary.exported_attachment_count == 1
        for summary in final_report.formats
    )
    assert all(
        summary.detected_total_marks == 5
        for summary in final_report.formats
    )


def test_export_report_requires_translation_acceptance_for_final_acceptance() -> None:
    project = _full_exam_project(
        export_formats=[ExportFormat.docx],
        include_translation_report=False,
    )
    docx_bytes = build_project_docx_bytes(project)

    report = build_full_exam_export_report(
        project,
        ExportFormat.docx,
        docx_bytes,
    )

    assert report.formats[0].status == FullExamExportArtifactStatus.accepted
    assert report.status == FullExamExportAcceptanceStatus.needs_review
    assert any("تقرير قبول لترجمة" in warning for warning in report.warnings)


def test_invalid_question_asset_is_reported_without_blocking_file_generation() -> None:
    project = _full_exam_project(
        export_formats=[ExportFormat.docx],
        invalid_attachment=True,
    )
    docx_bytes = build_project_docx_bytes(project)

    report = build_full_exam_export_report(
        project,
        ExportFormat.docx,
        docx_bytes,
    )

    assert docx_bytes.startswith(b"PK")
    assert report.status == FullExamExportAcceptanceStatus.needs_review
    assert report.formats[0].status == FullExamExportArtifactStatus.needs_review
    assert report.formats[0].exported_attachment_count == 0
    assert any("تعذر إدراج 1 مرفق" in warning for warning in report.warnings)


def test_export_endpoints_persist_combined_acceptance_report() -> None:
    project = _full_exam_project()
    project_store._projects[project.id] = project
    project_store._repository.save(project)

    try:
        docx_response = client.post(
            f"/api/projects/{project.id}/export/docx"
        )
        assert docx_response.status_code == 200
        assert docx_response.headers["x-madarik-export-acceptance"] == "incomplete"

        pdf_response = client.post(
            f"/api/projects/{project.id}/export/pdf"
        )
        assert pdf_response.status_code == 200
        assert pdf_response.headers["x-madarik-export-acceptance"] == "accepted"

        report_response = client.get(
            f"/api/projects/{project.id}/export/acceptance"
        )
        assert report_response.status_code == 200
        body = report_response.json()
        assert body["status"] == "accepted"
        assert body["generated_formats"] == ["docx", "pdf"]
        assert body["active_question_count"] == 2
        assert body["expected_total_marks"] == 5
        assert len(body["formats"]) == 2
    finally:
        project_store.delete(project.id)
