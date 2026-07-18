from __future__ import annotations

import base64
import hashlib
from io import BytesIO
import re
from typing import Iterable
from zipfile import BadZipFile, ZipFile

import arabic_reshaper
from docx import Document
from PIL import Image as PILImage
from pypdf import PdfReader

from app.models.project import (
    ExportFormat,
    FullExamExportAcceptanceStatus,
    FullExamExportArtifactStatus,
    FullExamExportCheck,
    FullExamExportFormatSummary,
    FullExamExportReport,
    FullExamIntakeStatus,
    FullExamTranslationAcceptanceStatus,
    ProjectSession,
    QuestionItem,
    QuestionPart,
    QuestionStatus,
)
from app.services.export_review import (
    missing_visual_asset_question_numbers,
    parse_declared_total_marks,
)


EXPORT_MANIFEST_PREFIX = "MADARIK-A6C-V1"
_MANIFEST_FIELD_RE = re.compile(r"(?P<key>[a-z_]+)=(?P<value>[^;]*)")
_DOCX_QUESTION_HEADING_RE = re.compile(
    r"^السؤال\s+(?P<number>\d+)(?:\s+\[(?P<marks>\d+)\])?$"
)


def _active_questions(project: ProjectSession) -> list[QuestionItem]:
    return sorted(
        (
            question
            for question in project.questions
            if question.status != QuestionStatus.deleted
        ),
        key=lambda question: question.order_index,
    )


def _question_part_depth(
    part: QuestionPart,
    parts: list[QuestionPart],
) -> int:
    parts_by_id = {item.id: item for item in parts}
    current = part
    visited = {part.id}
    depth = 0

    while current.parent_id:
        parent = parts_by_id.get(current.parent_id)
        if parent is None or parent.id in visited:
            break
        visited.add(parent.id)
        current = parent
        depth += 1

    return depth


def question_export_total_marks(question: QuestionItem) -> int | None:
    """Return the same hierarchy-safe total used by the export renderers."""

    if question.marks is not None:
        return question.marks

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

        child_marks = [
            branch_marks(child, visited | {part.id})
            for child in children.get(part.id, [])
        ]
        concrete_child_marks = [
            value
            for value in child_marks
            if value is not None
        ]

        if concrete_child_marks:
            return sum(concrete_child_marks)

        return part.marks

    root_totals = [branch_marks(root, set()) for root in roots]
    concrete_totals = [
        value
        for value in root_totals
        if value is not None
    ]
    return sum(concrete_totals) if concrete_totals else None


def _expected_structure(project: ProjectSession) -> dict[str, object]:
    questions = _active_questions(project)
    sequence_source = "\x1f".join(question.id for question in questions)
    sequence = hashlib.sha256(sequence_source.encode("utf-8")).hexdigest()[:20]
    return {
        "questions": len(questions),
        "parts": sum(len(question.parts) for question in questions),
        "attachments": sum(len(question.attachments) for question in questions),
        "marks": sum(question_export_total_marks(question) or 0 for question in questions),
        "order": ",".join(str(index) for index in range(1, len(questions) + 1)),
        "sequence": sequence,
    }


def build_full_exam_export_manifest(project: ProjectSession) -> str:
    """Build an ASCII artifact manifest stored invisibly in DOCX/PDF metadata."""

    structure = _expected_structure(project)
    return ";".join(
        [
            EXPORT_MANIFEST_PREFIX,
            f"questions={structure['questions']}",
            f"parts={structure['parts']}",
            f"attachments={structure['attachments']}",
            f"marks={structure['marks']}",
            f"order={structure['order']}",
            f"sequence={structure['sequence']}",
        ]
    )


def _parse_manifest(value: str | None) -> dict[str, object] | None:
    manifest = (value or "").strip()
    if not manifest.startswith(f"{EXPORT_MANIFEST_PREFIX};"):
        return None

    fields = {
        match.group("key"): match.group("value")
        for match in _MANIFEST_FIELD_RE.finditer(manifest)
    }

    try:
        return {
            "questions": int(fields["questions"]),
            "parts": int(fields["parts"]),
            "attachments": int(fields["attachments"]),
            "marks": int(fields["marks"]),
            "order": fields.get("order", ""),
            "sequence": fields.get("sequence", ""),
        }
    except (KeyError, TypeError, ValueError):
        return None


def _is_valid_image_payload(data_base64: str) -> bool:
    if not data_base64:
        return False
    try:
        payload = base64.b64decode(data_base64, validate=True)
        with PILImage.open(BytesIO(payload)) as image:
            image.verify()
        return True
    except Exception:
        return False


def _valid_logo_count(project: ProjectSession) -> int:
    if not project.school_logo:
        return 0
    return int(_is_valid_image_payload(project.school_logo.data_base64))


def _valid_attachment_ids(project: ProjectSession) -> set[str]:
    return {
        attachment.id
        for question in _active_questions(project)
        for attachment in question.attachments
        if _is_valid_image_payload(attachment.data_base64)
    }


def _valid_attachment_count(project: ProjectSession) -> int:
    return len(_valid_attachment_ids(project))


def _docx_text(document: Document) -> str:
    blocks = [paragraph.text for paragraph in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                blocks.extend(paragraph.text for paragraph in cell.paragraphs)
    return "\n".join(blocks)


def _docx_question_headings(document: Document) -> tuple[list[int], int]:
    order: list[int] = []
    marks_total = 0
    for paragraph in document.paragraphs:
        match = _DOCX_QUESTION_HEADING_RE.match(paragraph.text.strip())
        if not match:
            continue
        order.append(int(match.group("number")))
        if match.group("marks"):
            marks_total += int(match.group("marks"))
    return order, marks_total


def _pdf_image_count(reader: PdfReader) -> int:
    image_count = 0
    seen_references: set[tuple[int, int] | str] = set()

    for page in reader.pages:
        resources = page.get("/Resources")
        if resources is None:
            continue
        resources = resources.get_object()
        xobjects = resources.get("/XObject")
        if xobjects is None:
            continue
        xobjects = xobjects.get_object()

        for name, reference in xobjects.items():
            try:
                object_value = reference.get_object()
            except Exception:
                continue
            if object_value.get("/Subtype") != "/Image":
                continue

            identity: tuple[int, int] | str
            if hasattr(reference, "idnum"):
                identity = (reference.idnum, reference.generation)
            else:
                identity = str(name)

            if identity in seen_references:
                continue
            seen_references.add(identity)
            image_count += 1

    return image_count


def _metadata_value(metadata: object, key: str) -> str:
    if metadata is None:
        return ""
    value = getattr(metadata, key, None)
    if value is None and isinstance(metadata, dict):
        value = metadata.get(key)
    return str(value or "")


def _manifest_checks(
    project: ProjectSession,
    manifest: dict[str, object] | None,
) -> list[FullExamExportCheck]:
    expected = _expected_structure(project)

    if manifest is None:
        return [
            FullExamExportCheck(
                code="artifact_manifest",
                passed=False,
                message="لم يُعثر على بصمة بنية A6c داخل ملف التصدير.",
            )
        ]

    fields = (
        "questions",
        "parts",
        "attachments",
        "marks",
        "order",
        "sequence",
    )
    return [
        FullExamExportCheck(
            code=f"manifest_{field}",
            passed=manifest[field] == expected[field],
            message=(
                f"تطابق حقل {field} في بصمة ملف التصدير."
                if manifest[field] == expected[field]
                else (
                    f"حقل {field} في الملف ({manifest[field]}) لا يطابق "
                    f"بنية المشروع الحالية ({expected[field]})."
                )
            ),
        )
        for field in fields
    ]


def _inspect_docx(
    project: ProjectSession,
    artifact_bytes: bytes,
) -> FullExamExportFormatSummary:
    checks: list[FullExamExportCheck] = []
    warnings: list[str] = []
    manifest: dict[str, object] | None = None
    question_order: list[int] = []
    heading_marks = 0
    exported_images = 0
    body_text = ""

    try:
        with ZipFile(BytesIO(artifact_bytes)) as archive:
            checks.append(
                FullExamExportCheck(
                    code="docx_container",
                    passed="word/document.xml" in archive.namelist(),
                    message="ملف Word حاوية DOCX صالحة وقابلة للقراءة.",
                )
            )
    except BadZipFile:
        checks.append(
            FullExamExportCheck(
                code="docx_container",
                passed=False,
                message="ملف Word الناتج ليس حاوية DOCX صالحة.",
            )
        )

    try:
        document = Document(BytesIO(artifact_bytes))
        manifest = _parse_manifest(document.core_properties.subject)
        question_order, heading_marks = _docx_question_headings(document)
        exported_images = max(
            0,
            len(document.inline_shapes) - _valid_logo_count(project),
        )
        body_text = _docx_text(document)
    except Exception as exc:
        warnings.append(f"تعذر فحص محتوى Word تفصيليًا: {exc}")

    checks.extend(_manifest_checks(project, manifest))
    expected = _expected_structure(project)
    expected_order = list(range(1, int(expected["questions"]) + 1))
    valid_attachment_ids = _valid_attachment_ids(project)
    valid_attachments = len(valid_attachment_ids)
    missing_visual_questions = missing_visual_asset_question_numbers(
        _active_questions(project),
        valid_attachment_ids=valid_attachment_ids,
    )

    checks.extend(
        [
            FullExamExportCheck(
                code="docx_question_order",
                passed=question_order == expected_order,
                message=(
                    "ترتيب عناوين الأسئلة داخل Word مطابق للترتيب النشط."
                    if question_order == expected_order
                    else (
                        f"ترتيب عناوين Word المكتشف {question_order} لا يطابق "
                        f"الترتيب المتوقع {expected_order}."
                    )
                ),
            ),
            FullExamExportCheck(
                code="docx_marks_total",
                passed=heading_marks == expected["marks"],
                message=(
                    "مجموع درجات عناوين Word مطابق دون جمع درجات الأجزاء مرتين."
                    if heading_marks == expected["marks"]
                    else (
                        f"مجموع الدرجات المكتشف في عناوين Word ({heading_marks}) "
                        f"لا يطابق المتوقع ({expected['marks']})."
                    )
                ),
            ),
            FullExamExportCheck(
                code="docx_attachments_once",
                passed=exported_images == valid_attachments,
                message=(
                    "أُدرجت مرفقات الأسئلة الصالحة مرة واحدة في Word."
                    if exported_images == valid_attachments
                    else (
                        f"عدد صور الأسئلة داخل Word ({exported_images}) لا يطابق "
                        f"المرفقات الصالحة ({valid_attachments})."
                    )
                ),
            ),
            FullExamExportCheck(
                code="docx_visual_question_coverage",
                passed=not missing_visual_questions,
                message=(
                    "كل سؤال يعتمد على رسم أو مخطط يملك مرفقًا بصريًا صالحًا في Word."
                    if not missing_visual_questions
                    else (
                        "توجد أسئلة تعتمد على رسم أو مخطط دون مرفق بصري صالح في Word: "
                        + "، ".join(missing_visual_questions)
                    )
                ),
            ),
            FullExamExportCheck(
                code="docx_body_content",
                passed=bool(body_text.strip()),
                message="يحتوي ملف Word على نص قابل للقراءة.",
            ),
        ]
    )

    invalid_attachments = int(expected["attachments"]) - valid_attachments
    if invalid_attachments:
        warnings.append(
            f"تعذر إدراج {invalid_attachments} مرفق بسبب بيانات صورة غير صالحة."
        )

    status = (
        FullExamExportArtifactStatus.accepted
        if all(check.passed for check in checks) and not warnings
        else FullExamExportArtifactStatus.needs_review
    )
    if not artifact_bytes or not checks[0].passed or manifest is None:
        status = FullExamExportArtifactStatus.failed

    return FullExamExportFormatSummary(
        format=ExportFormat.docx,
        status=status,
        byte_size=len(artifact_bytes),
        page_count=None,
        exported_question_count=(
            int(manifest["questions"])
            if manifest is not None
            else len(question_order)
        ),
        exported_part_count=(
            int(manifest["parts"])
            if manifest is not None
            else 0
        ),
        exported_attachment_count=exported_images,
        detected_total_marks=(
            int(manifest["marks"])
            if manifest is not None
            else heading_marks
        ),
        question_order=[str(number) for number in question_order],
        checks=checks,
        warnings=warnings,
    )


def _inspect_pdf(
    project: ProjectSession,
    artifact_bytes: bytes,
) -> FullExamExportFormatSummary:
    checks: list[FullExamExportCheck] = []
    warnings: list[str] = []
    manifest: dict[str, object] | None = None
    page_count = 0
    exported_images = 0
    extracted_text = ""

    signature_valid = artifact_bytes.startswith(b"%PDF")
    checks.append(
        FullExamExportCheck(
            code="pdf_signature",
            passed=signature_valid,
            message=(
                "ملف PDF يبدأ بتوقيع PDF صالح."
                if signature_valid
                else "ملف PDF الناتج لا يبدأ بتوقيع PDF صالح."
            ),
        )
    )

    try:
        reader = PdfReader(BytesIO(artifact_bytes))
        page_count = len(reader.pages)
        manifest = _parse_manifest(
            _metadata_value(reader.metadata, "subject")
        )
        exported_images = max(
            0,
            _pdf_image_count(reader) - _valid_logo_count(project),
        )
        extracted_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )
    except Exception as exc:
        warnings.append(f"تعذر فحص محتوى PDF تفصيليًا: {exc}")

    checks.extend(_manifest_checks(project, manifest))
    expected = _expected_structure(project)
    valid_attachment_ids = _valid_attachment_ids(project)
    valid_attachments = len(valid_attachment_ids)
    missing_visual_questions = missing_visual_asset_question_numbers(
        _active_questions(project),
        valid_attachment_ids=valid_attachment_ids,
    )

    checks.extend(
        [
            FullExamExportCheck(
                code="pdf_pages",
                passed=page_count > 0,
                message=(
                    f"يحتوي PDF على {page_count} صفحة قابلة للقراءة."
                    if page_count > 0
                    else "لا يحتوي PDF على صفحات قابلة للقراءة."
                ),
            ),
            FullExamExportCheck(
                code="pdf_question_headings",
                passed=(
                    sum(
                        line.strip() == arabic_reshaper.reshape("السؤال")
                        for line in extracted_text.splitlines()
                    )
                    == expected["questions"]
                ),
                message=(
                    "عدد عناوين الأسئلة المرئية داخل PDF مطابق للبنية المتوقعة."
                    if sum(
                        line.strip() == arabic_reshaper.reshape("السؤال")
                        for line in extracted_text.splitlines()
                    )
                    == expected["questions"]
                    else (
                        "عدد عناوين الأسئلة المكتشف داخل PDF لا يطابق "
                        "عدد الأسئلة النشطة."
                    )
                ),
            ),
            FullExamExportCheck(
                code="pdf_attachments_once",
                passed=exported_images == valid_attachments,
                message=(
                    "أُدرجت مرفقات الأسئلة الصالحة مرة واحدة في PDF."
                    if exported_images == valid_attachments
                    else (
                        f"عدد صور الأسئلة داخل PDF ({exported_images}) لا يطابق "
                        f"المرفقات الصالحة ({valid_attachments})."
                    )
                ),
            ),
            FullExamExportCheck(
                code="pdf_visual_question_coverage",
                passed=not missing_visual_questions,
                message=(
                    "كل سؤال يعتمد على رسم أو مخطط يملك مرفقًا بصريًا صالحًا في PDF."
                    if not missing_visual_questions
                    else (
                        "توجد أسئلة تعتمد على رسم أو مخطط دون مرفق بصري صالح في PDF: "
                        + "، ".join(missing_visual_questions)
                    )
                ),
            ),
            FullExamExportCheck(
                code="pdf_text_layer",
                passed=bool(extracted_text.strip()),
                message=(
                    "يحتوي PDF على طبقة نصية قابلة للاستخراج."
                    if extracted_text.strip()
                    else "لم تُكتشف طبقة نصية قابلة للاستخراج داخل PDF."
                ),
            ),
        ]
    )

    invalid_attachments = int(expected["attachments"]) - valid_attachments
    if invalid_attachments:
        warnings.append(
            f"تعذر إدراج {invalid_attachments} مرفق بسبب بيانات صورة غير صالحة."
        )

    status = (
        FullExamExportArtifactStatus.accepted
        if all(check.passed for check in checks) and not warnings
        else FullExamExportArtifactStatus.needs_review
    )
    if not signature_valid or manifest is None or page_count == 0:
        status = FullExamExportArtifactStatus.failed

    manifest_order = str(manifest.get("order", "")) if manifest else ""
    return FullExamExportFormatSummary(
        format=ExportFormat.pdf,
        status=status,
        byte_size=len(artifact_bytes),
        page_count=page_count or None,
        exported_question_count=(
            int(manifest["questions"])
            if manifest is not None
            else 0
        ),
        exported_part_count=(
            int(manifest["parts"])
            if manifest is not None
            else 0
        ),
        exported_attachment_count=exported_images,
        detected_total_marks=(
            int(manifest["marks"])
            if manifest is not None
            else 0
        ),
        question_order=[
            item
            for item in manifest_order.split(",")
            if item
        ],
        checks=checks,
        warnings=warnings,
    )


def _unique_formats(formats: Iterable[ExportFormat]) -> list[ExportFormat]:
    result: list[ExportFormat] = []
    for item in formats:
        if item not in result:
            result.append(item)
    return result


def build_full_exam_export_report(
    project: ProjectSession,
    artifact_format: ExportFormat,
    artifact_bytes: bytes,
    existing_report: FullExamExportReport | None = None,
) -> FullExamExportReport:
    """Inspect one real artifact and merge it into the persisted exam report."""

    format_summary = (
        _inspect_docx(project, artifact_bytes)
        if artifact_format == ExportFormat.docx
        else _inspect_pdf(project, artifact_bytes)
    )

    summaries_by_format = {
        summary.format: summary
        for summary in (existing_report.formats if existing_report else [])
    }
    summaries_by_format[artifact_format] = format_summary

    requested_formats = _unique_formats(
        project.metadata.export_formats or [ExportFormat.docx, ExportFormat.pdf]
    )
    summaries = [
        summaries_by_format[item]
        for item in (ExportFormat.docx, ExportFormat.pdf)
        if item in summaries_by_format
    ]
    generated_formats = [summary.format for summary in summaries]
    accepted_formats = [
        summary.format
        for summary in summaries
        if summary.status == FullExamExportArtifactStatus.accepted
    ]
    needs_review_formats = [
        summary.format
        for summary in summaries
        if summary.status == FullExamExportArtifactStatus.needs_review
    ]
    failed_formats = [
        summary.format
        for summary in summaries
        if summary.status == FullExamExportArtifactStatus.failed
    ]

    questions = _active_questions(project)
    expected = _expected_structure(project)
    reported_marks = parse_declared_total_marks(project.metadata.total_marks)
    missing_formats = [
        item
        for item in requested_formats
        if item not in generated_formats
    ]

    checks = [
        FullExamExportCheck(
            code="active_questions",
            passed=bool(questions),
            message=(
                f"توجد {len(questions)} أسئلة نشطة قابلة للتصدير."
                if questions
                else "لا توجد أسئلة نشطة قابلة للتصدير."
            ),
        ),
        FullExamExportCheck(
            code="question_order",
            passed=(
                len({question.order_index for question in questions})
                == len(questions)
                and [question.order_index for question in questions]
                == sorted(question.order_index for question in questions)
            ),
            message="ترتيب الأسئلة النشطة فريد ومستقر قبل التصدير.",
        ),
        FullExamExportCheck(
            code="paper_total_matches",
            passed=(
                reported_marks is None
                or reported_marks == expected["marks"]
            ),
            message=(
                "مجموع درجات التصدير يطابق الدرجة المعلنة للورقة."
                if reported_marks is None or reported_marks == expected["marks"]
                else (
                    f"مجموع الأسئلة ({expected['marks']}) لا يطابق الدرجة "
                    f"المعلنة ({reported_marks})."
                )
            ),
        ),
        FullExamExportCheck(
            code="requested_formats_generated",
            passed=not missing_formats,
            message=(
                "تم إنشاء جميع صيغ التصدير المطلوبة."
                if not missing_formats
                else "لم تُنشأ بعد الصيغ المطلوبة: "
                + "، ".join(item.value.upper() for item in missing_formats)
            ),
        ),
        FullExamExportCheck(
            code="artifacts_accepted",
            passed=not failed_formats and not needs_review_formats,
            message=(
                "اجتازت ملفات التصدير المنشأة فحوص البنية."
                if not failed_formats and not needs_review_formats
                else "توجد ملفات تصدير تحتاج مراجعة أو فشلت فحوصها."
            ),
        ),
    ]

    warnings: list[str] = []
    if project.full_exam_intake_report is None:
        warnings.append("لا يوجد تقرير قبول لبنية الورقة الكاملة.")
    elif project.full_exam_intake_report.status != FullExamIntakeStatus.accepted:
        warnings.append("تقرير إدخال الورقة الكاملة لم يصل إلى حالة accepted.")

    if project.full_exam_translation_report is None:
        warnings.append("لا يوجد تقرير قبول لترجمة الورقة الكاملة.")
    elif (
        project.full_exam_translation_report.status
        != FullExamTranslationAcceptanceStatus.accepted
    ):
        warnings.append("تقرير ترجمة الورقة الكاملة لم يصل إلى حالة accepted.")

    for summary in summaries:
        warnings.extend(
            f"{summary.format.value.upper()}: {warning}"
            for warning in summary.warnings
        )

    if failed_formats or not questions:
        status = FullExamExportAcceptanceStatus.failed
    elif missing_formats:
        status = FullExamExportAcceptanceStatus.incomplete
    elif needs_review_formats or warnings or not all(check.passed for check in checks):
        status = FullExamExportAcceptanceStatus.needs_review
    else:
        status = FullExamExportAcceptanceStatus.accepted

    return FullExamExportReport(
        status=status,
        requested_formats=requested_formats,
        generated_formats=generated_formats,
        accepted_formats=accepted_formats,
        needs_review_formats=needs_review_formats,
        failed_formats=failed_formats,
        active_question_count=len(questions),
        expected_total_marks=int(expected["marks"]),
        expected_part_count=int(expected["parts"]),
        expected_attachment_count=int(expected["attachments"]),
        source_page_linked_questions=sum(
            bool(question.source_page_numbers)
            for question in questions
        ),
        multi_page_questions=sum(
            len(question.source_page_numbers) > 1
            for question in questions
        ),
        formats=summaries,
        checks=checks,
        warnings=warnings,
    )
