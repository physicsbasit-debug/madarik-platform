from __future__ import annotations

import base64
from io import BytesIO

from docx import Document
from docx.oxml.ns import qn
from PIL import Image as PILImage

from app.models.project import (
    ExportFormat,
    FullExamExportArtifactStatus,
    ProjectMetadata,
    ProjectSession,
    QuestionAssetInfo,
    QuestionItem,
    QuestionStatus,
)
from app.services.export import (
    _attachment_note_for_export,
    _clean_export_text,
    build_project_docx_bytes,
)
from app.services.full_exam_export import build_full_exam_export_report
from app.services.readiness import build_project_readiness_report
from app.services.scientific_text import normalise_scientific_text


def _png_asset(asset_id: str) -> QuestionAssetInfo:
    image = PILImage.new("RGB", (64, 40), (255, 255, 255))
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


def _docx_blocks(payload: bytes) -> list[tuple[str, bool]]:
    document = Document(BytesIO(payload))
    blocks: list[tuple[str, bool]] = []

    for child in document._element.body.iterchildren():
        if child.tag != qn("w:p"):
            continue
        text = "".join(node.text or "" for node in child.iter(qn("w:t")))
        has_image = any(node.tag == qn("w:drawing") for node in child.iter())
        blocks.append((text.strip(), has_image))

    return blocks


def test_scientific_text_repairs_known_ocr_corruption_patterns() -> None:
    repaired = normalise_scientific_text(
        "duration 4–10 × 5.0 s; charge 10–10 × 8.5 C; "
        "sample 8.0 × 1014 atoms; decayed 1014 × 6.0 atoms; "
        "pressure 1.0 × 10 5 Pa; resistance /g58; Am95 241; "
        "volume 9.6 m3 and area 1800 m 2; points F 1 and F 2."
    )

    assert "5.0 × 10⁻⁴" in repaired
    assert "8.5 × 10⁻¹⁰" in repaired
    assert "8.0 × 10¹⁴" in repaired
    assert "6.0 × 10¹⁴" in repaired
    assert "1.0 × 10⁵" in repaired
    assert "Ω" in repaired
    assert "²⁴¹₉₅Am" in repaired
    assert "9.6 m³" in repaired
    assert "1800 m²" in repaired
    assert "F₁" in repaired
    assert "F₂" in repaired


def test_export_cleaning_applies_scientific_repair() -> None:
    cleaned = _clean_export_text(
        "charge 10–10 × 8.5 C and 2.1 × 103 J / kg °C"
    )

    assert cleaned == "charge 8.5 × 10⁻¹⁰ C and 2.1 × 10³ J / kg °C"


def test_internal_layout_note_is_never_exported_to_student_file() -> None:
    question = QuestionItem(
        id="q-1",
        original_number="1",
        original_text="State the value.",
        translated_text="اذكر القيمة.",
        order_index=1,
        attachment_note=(
            "تم ربط 1 لقطة صفحة PDF آليًا بهذا السؤال وفق صفحات المصدر. "
            "استخدم القص البصري لاحقًا لعزل الرسم أو الجدول المطلوب."
        ),
    )

    assert _attachment_note_for_export(question) == ""


def test_docx_places_each_question_asset_before_the_next_question() -> None:
    project = ProjectSession(
        metadata=ProjectMetadata(
            paper_title="Visual placement",
            total_marks="4",
            export_formats=[ExportFormat.docx],
        ),
        questions=[
            QuestionItem(
                id="q-1",
                original_number="1",
                original_text="Use Fig. 1.1. [2]",
                translated_text="استخدم الشكل 1.1. [2]",
                marks=2,
                status=QuestionStatus.approved,
                order_index=1,
                attachments=[_png_asset("asset-1")],
            ),
            QuestionItem(
                id="q-2",
                original_number="2",
                original_text="Use Fig. 2.1. [2]",
                translated_text="استخدم الشكل 2.1. [2]",
                marks=2,
                status=QuestionStatus.approved,
                order_index=2,
                attachments=[_png_asset("asset-2")],
            ),
        ],
    )

    blocks = _docx_blocks(build_project_docx_bytes(project))
    q1_index = next(index for index, block in enumerate(blocks) if block[0] == "السؤال 1 [2]")
    q2_index = next(index for index, block in enumerate(blocks) if block[0] == "السؤال 2 [2]")
    image_indices = [index for index, block in enumerate(blocks) if block[1]]

    assert len(image_indices) == 2
    assert q1_index < image_indices[0] < q2_index < image_indices[1]


def test_visual_question_without_asset_lowers_docx_artifact_acceptance() -> None:
    project = ProjectSession(
        metadata=ProjectMetadata(
            paper_title="Visual coverage",
            total_marks="4",
            export_formats=[ExportFormat.docx],
        ),
        questions=[
            QuestionItem(
                id="q-1",
                original_number="1",
                original_text="Use Fig. 1.1. [2]",
                translated_text="استخدم الشكل 1.1. [2]",
                marks=2,
                status=QuestionStatus.approved,
                order_index=1,
                attachments=[_png_asset("asset-1")],
            ),
            QuestionItem(
                id="q-2",
                original_number="2",
                original_text="Calculate from Fig. 2.1. [2]",
                translated_text="احسب من الشكل 2.1. [2]",
                marks=2,
                status=QuestionStatus.approved,
                order_index=2,
            ),
        ],
    )

    payload = build_project_docx_bytes(project)
    report = build_full_exam_export_report(
        project,
        ExportFormat.docx,
        payload,
    )
    summary = report.formats[0]
    visual_check = next(
        check
        for check in summary.checks
        if check.code == "docx_visual_question_coverage"
    )

    assert summary.status == FullExamExportArtifactStatus.needs_review
    assert visual_check.passed is False
    assert "2" in visual_check.message


def test_readiness_reports_declared_total_and_visual_asset_mismatches() -> None:
    project = ProjectSession(
        metadata=ProjectMetadata(total_marks="20"),
        questions=[
            QuestionItem(
                id="q-1",
                original_number="1",
                original_text="Use Fig. 1.1. [80]",
                translated_text="استخدم الشكل 1.1. [80]",
                marks=80,
                status=QuestionStatus.approved,
                order_index=1,
            )
        ],
    )

    report = build_project_readiness_report(project)
    issues = {issue.code: issue for issue in report.issues}

    assert report.total_marks == 80
    assert "paper_total_marks_mismatch" in issues
    assert "20" in issues["paper_total_marks_mismatch"].message
    assert "80" in issues["paper_total_marks_mismatch"].message
    assert "visual_questions_missing_assets" in issues
