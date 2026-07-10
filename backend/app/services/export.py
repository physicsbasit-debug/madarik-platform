from __future__ import annotations

from io import BytesIO
import os
import re
from typing import Iterable

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import arabic_reshaper
from bidi.algorithm import get_display

from app.models.project import OutputMode, ProjectSession, QuestionItem, QuestionStatus

DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PDF_MIME_TYPE = "application/pdf"

ARABIC_FONT_NAME = "MadarikArabic"
ENGLISH_FONT_NAME = "Helvetica"


def _set_paragraph_bidi(paragraph, *, rtl: bool = True) -> None:
    """Set paragraph direction for Arabic/English blocks."""

    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT if rtl else WD_ALIGN_PARAGRAPH.LEFT
    p_pr = paragraph._p.get_or_add_pPr()
    bidi = p_pr.find(qn("w:bidi"))
    if rtl and bidi is None:
        p_pr.append(OxmlElement("w:bidi"))
    if not rtl and bidi is not None:
        p_pr.remove(bidi)


def _set_run_rtl(run, *, rtl: bool = True) -> None:
    r_pr = run._r.get_or_add_rPr()
    rtl_el = r_pr.find(qn("w:rtl"))
    if rtl and rtl_el is None:
        r_pr.append(OxmlElement("w:rtl"))
    if not rtl and rtl_el is not None:
        r_pr.remove(rtl_el)


def _set_cell_text(cell, label: str, value: str) -> None:
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    paragraph = cell.paragraphs[0]
    paragraph.clear()
    _set_paragraph_bidi(paragraph, rtl=True)
    label_run = paragraph.add_run(f"{label}: ")
    label_run.bold = True
    _set_run_rtl(label_run, rtl=True)
    value_run = paragraph.add_run(value or "__________")
    _set_run_rtl(value_run, rtl=True)


def _set_table_bidi(table) -> None:
    tbl_pr = table._tbl.tblPr
    bidi = tbl_pr.find(qn("w:bidiVisual"))
    if bidi is None:
        tbl_pr.append(OxmlElement("w:bidiVisual"))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER


def _configure_document(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)
    section.start_type = WD_SECTION_START.NEW_PAGE

    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:cs"), "Arial")
    normal.font.size = Pt(12)


def _add_title(document: Document, project: ProjectSession) -> None:
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_bidi(title, rtl=True)
    title_run = title.add_run(project.metadata.paper_title or "ورقة تدريبية مترجمة")
    title_run.bold = True
    title_run.font.size = Pt(17)
    _set_run_rtl(title_run, rtl=True)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_paragraph_bidi(subtitle, rtl=True)
    subtitle_run = subtitle.add_run("منصة مدارك")
    subtitle_run.font.size = Pt(10)
    _set_run_rtl(subtitle_run, rtl=True)


def _add_metadata_table(document: Document, project: ProjectSession, question_count: int, marks_total: int) -> None:
    metadata = project.metadata
    table = document.add_table(rows=4, cols=2)
    table.style = "Table Grid"
    _set_table_bidi(table)

    rows = [
        (("اسم المدرسة", metadata.school_name), ("المادة", metadata.subject)),
        (("الصف", metadata.grade), ("الفصل الدراسي", metadata.semester)),
        (("الزمن", metadata.duration), ("الدرجة", metadata.total_marks or str(marks_total))),
        (("اسم المعلم", metadata.teacher_name), ("التاريخ", metadata.date)),
    ]

    for row, row_data in zip(table.rows, rows):
        _set_cell_text(row.cells[0], row_data[0][0], row_data[0][1])
        _set_cell_text(row.cells[1], row_data[1][0], row_data[1][1])

    summary = document.add_paragraph()
    _set_paragraph_bidi(summary, rtl=True)
    mode = "ثنائية اللغة" if metadata.output_mode == OutputMode.bilingual else "عربية نظيفة"
    run = summary.add_run(f"نوع النسخة: {mode} | عدد الأسئلة: {question_count} | مجموع الدرجات المحسوب: {marks_total}")
    run.font.size = Pt(10)
    _set_run_rtl(run, rtl=True)


def _active_questions(project: ProjectSession) -> list[QuestionItem]:
    return sorted(
        [question for question in project.questions if question.status != QuestionStatus.deleted],
        key=lambda question: question.order_index,
    )


def _question_marks_label(question: QuestionItem) -> str:
    if question.marks is None:
        return ""
    return f" [{question.marks}]"


def _add_question_number(document: Document, number: int, question: QuestionItem) -> None:
    paragraph = document.add_paragraph()
    _set_paragraph_bidi(paragraph, rtl=True)
    run = paragraph.add_run(f"{number}. السؤال{_question_marks_label(question)}")
    run.bold = True
    run.font.size = Pt(13)
    _set_run_rtl(run, rtl=True)


def _add_arabic_text(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    _set_paragraph_bidi(paragraph, rtl=True)
    run = paragraph.add_run(text.strip() or "[ترجمة تحتاج مراجعة]")
    run.font.size = Pt(12)
    _set_run_rtl(run, rtl=True)


def _add_english_text(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    _set_paragraph_bidi(paragraph, rtl=False)
    paragraph.paragraph_format.left_indent = Inches(0.2)
    run = paragraph.add_run(text.strip())
    run.font.size = Pt(10.5)
    _set_run_rtl(run, rtl=False)


def _add_questions(document: Document, project: ProjectSession, questions: list[QuestionItem]) -> None:
    for display_number, question in enumerate(questions, start=1):
        _add_question_number(document, display_number, question)

        if project.metadata.output_mode == OutputMode.bilingual:
            _add_english_text(document, question.original_text)
            _add_arabic_text(document, question.translated_text or "[تحتاج ترجمة]")
        else:
            _add_arabic_text(document, question.translated_text or question.original_text)

        if question.attachment_note:
            note = document.add_paragraph()
            _set_paragraph_bidi(note, rtl=True)
            note_run = note.add_run(f"ملاحظة مرفق: {question.attachment_note}")
            note_run.italic = True
            note_run.font.size = Pt(10)
            _set_run_rtl(note_run, rtl=True)


def _add_footer_note(document: Document) -> None:
    paragraph = document.add_paragraph()
    _set_paragraph_bidi(paragraph, rtl=True)
    run = paragraph.add_run("أُنشئت هذه الورقة عبر منصة مدارك. يُوصى بمراجعة المعلم للترجمة قبل الاستخدام الصفي.")
    run.font.size = Pt(9)
    run.italic = True
    _set_run_rtl(run, rtl=True)


def build_project_docx_bytes(project: ProjectSession) -> bytes:
    """Build a Phase 1-F1 RTL DOCX for the active project questions."""

    questions = _active_questions(project)
    if not questions:
        raise ValueError("لا توجد أسئلة نشطة قابلة للتصدير.")

    document = Document()
    _configure_document(document)

    marks_total = sum(question.marks or 0 for question in questions)
    _add_title(document, project)
    _add_metadata_table(document, project, question_count=len(questions), marks_total=marks_total)
    _add_questions(document, project, questions)
    _add_footer_note(document)

    output = BytesIO()
    document.save(output)
    return output.getvalue()


def safe_docx_filename(project: ProjectSession) -> str:
    title = project.metadata.paper_title or "madarik_export"
    subject = project.metadata.subject or "paper"
    raw = f"madarik_{subject}_{title}"
    normalized = re.sub(r"[^A-Za-z0-9_\-]+", "_", raw).strip("_")
    if not normalized:
        normalized = "madarik_export"
    return f"{normalized[:90]}.docx"


# -----------------------------
# Phase 1-F2: PDF export
# -----------------------------


def _font_candidates() -> Iterable[str]:
    yield "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    yield "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    yield "/Library/Fonts/Arial Unicode.ttf"
    yield "C:/Windows/Fonts/arial.ttf"


def _ensure_pdf_font() -> str:
    """Register a Unicode-capable font when available.

    GitHub Actions Ubuntu images normally include DejaVu Sans. If no Unicode font
    is available, the PDF still builds with Helvetica, but Arabic glyph coverage
    will be limited. This fallback keeps the endpoint testable without bundling
    font files in the repository.
    """

    if ARABIC_FONT_NAME in pdfmetrics.getRegisteredFontNames():
        return ARABIC_FONT_NAME

    for path in _font_candidates():
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(ARABIC_FONT_NAME, path))
            return ARABIC_FONT_NAME

    return ENGLISH_FONT_NAME


def _shape_arabic(text: str) -> str:
    """Shape Arabic text for ReportLab's left-to-right drawing model."""

    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def _pdf_paragraph(text: str, style: ParagraphStyle, *, rtl: bool = True) -> Paragraph:
    prepared = _shape_arabic(text) if rtl else text
    safe = prepared.replace("\n", "<br/>")
    return Paragraph(safe, style)


def _pdf_styles() -> dict[str, ParagraphStyle]:
    font = _ensure_pdf_font()
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "MadarikTitle",
            parent=base["Title"],
            fontName=font,
            fontSize=18,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "MadarikSubtitle",
            parent=base["Normal"],
            fontName=font,
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12,
        ),
        "body_ar": ParagraphStyle(
            "MadarikBodyArabic",
            parent=base["Normal"],
            fontName=font,
            fontSize=11,
            leading=17,
            alignment=TA_RIGHT,
            spaceAfter=8,
        ),
        "body_en": ParagraphStyle(
            "MadarikBodyEnglish",
            parent=base["Normal"],
            fontName=ENGLISH_FONT_NAME,
            fontSize=9.5,
            leading=14,
            alignment=TA_LEFT,
            leftIndent=10,
            textColor=colors.HexColor("#334155"),
            spaceAfter=5,
        ),
        "question": ParagraphStyle(
            "MadarikQuestionTitle",
            parent=base["Normal"],
            fontName=font,
            fontSize=12,
            leading=18,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=10,
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "MadarikSmall",
            parent=base["Normal"],
            fontName=font,
            fontSize=8.5,
            leading=12,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#64748b"),
        ),
    }


def _add_pdf_header(story: list, project: ProjectSession, questions: list[QuestionItem], styles: dict[str, ParagraphStyle]) -> None:
    metadata = project.metadata
    marks_total = sum(question.marks or 0 for question in questions)
    mode = "ثنائية اللغة" if metadata.output_mode == OutputMode.bilingual else "عربية نظيفة"

    story.append(_pdf_paragraph(metadata.paper_title or "ورقة تدريبية مترجمة", styles["title"], rtl=True))
    story.append(_pdf_paragraph("منصة مدارك", styles["subtitle"], rtl=True))

    rows = [
        ("اسم المدرسة", metadata.school_name, "المادة", metadata.subject),
        ("الصف", metadata.grade, "الفصل الدراسي", metadata.semester),
        ("الزمن", metadata.duration, "الدرجة", metadata.total_marks or str(marks_total)),
        ("اسم المعلم", metadata.teacher_name, "التاريخ", metadata.date),
        ("نوع النسخة", mode, "عدد الأسئلة", str(len(questions))),
    ]

    table_data = []
    for right_label, right_value, left_label, left_value in rows:
        table_data.append([
            _pdf_paragraph(f"{left_label}: {left_value or '__________'}", styles["small"], rtl=True),
            _pdf_paragraph(f"{right_label}: {right_value or '__________'}", styles["small"], rtl=True),
        ])

    table = Table(table_data, colWidths=[8.1 * cm, 8.1 * cm], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 10))


def _add_pdf_questions(story: list, project: ProjectSession, questions: list[QuestionItem], styles: dict[str, ParagraphStyle]) -> None:
    for display_number, question in enumerate(questions, start=1):
        story.append(_pdf_paragraph(f"{display_number}. السؤال{_question_marks_label(question)}", styles["question"], rtl=True))

        if project.metadata.output_mode == OutputMode.bilingual:
            story.append(_pdf_paragraph(question.original_text.strip(), styles["body_en"], rtl=False))
            story.append(_pdf_paragraph(question.translated_text or "[تحتاج ترجمة]", styles["body_ar"], rtl=True))
        else:
            story.append(_pdf_paragraph(question.translated_text or question.original_text, styles["body_ar"], rtl=True))

        if question.attachment_note:
            story.append(_pdf_paragraph(f"ملاحظة مرفق: {question.attachment_note}", styles["small"], rtl=True))


def _draw_pdf_footer(canvas, doc) -> None:
    font = _ensure_pdf_font()
    canvas.saveState()
    canvas.setFont(font, 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    footer = _shape_arabic("أُنشئت هذه الورقة عبر منصة مدارك - مراجعة المعلم ضرورية قبل الاستخدام الصفي")
    canvas.drawCentredString(A4[0] / 2, 1.05 * cm, footer)
    canvas.drawRightString(A4[0] - 1.4 * cm, 1.05 * cm, str(doc.page))
    canvas.restoreState()


def build_project_pdf_bytes(project: ProjectSession) -> bytes:
    """Build a Phase 1-F2 RTL-friendly PDF for active project questions."""

    questions = _active_questions(project)
    if not questions:
        raise ValueError("لا توجد أسئلة نشطة قابلة للتصدير.")

    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.8 * cm,
        title=project.metadata.paper_title or "Madarik Export",
        author="Madarik Platform",
    )
    styles = _pdf_styles()
    story: list = []

    _add_pdf_header(story, project, questions, styles)
    _add_pdf_questions(story, project, questions, styles)

    document.build(story, onFirstPage=_draw_pdf_footer, onLaterPages=_draw_pdf_footer)
    return output.getvalue()


def safe_pdf_filename(project: ProjectSession) -> str:
    title = project.metadata.paper_title or "madarik_export"
    subject = project.metadata.subject or "paper"
    raw = f"madarik_{subject}_{title}"
    normalized = re.sub(r"[^A-Za-z0-9_\-]+", "_", raw).strip("_")
    if not normalized:
        normalized = "madarik_export"
    return f"{normalized[:90]}.pdf"
