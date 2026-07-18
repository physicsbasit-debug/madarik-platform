from app.models.project import (
    ExtractedPdfPageInfo,
    ExtractedTextInfo,
    FullExamIntakeStatus,
    PdfLayoutAssetInfo,
    PdfPageKind,
    ProjectSession,
)
from app.services.full_exam_intake import (
    build_full_exam_intake_report,
    link_layout_assets_to_page_aware_questions,
    parse_full_exam_questions_from_pages,
)


def _page(page_number: int, text: str) -> ExtractedPdfPageInfo:
    return ExtractedPdfPageInfo(
        page_number=page_number,
        text=text,
        character_count=len(text),
        is_text_empty=not bool(text.strip()),
    )


def _reference_exam_pages(*, reported_total: int = 80) -> list[ExtractedPdfPageInfo]:
    question_totals = [8, 7, 9, 7, 6, 7, 7, 6, 7, 6, 6, 4]
    pages = [
        _page(
            1,
            "PHYSICS 0625/04\nINSTRUCTIONS\nAnswer all questions.\n"
            f"INFORMATION\nThe total mark for this paper is {reported_total}.",
        ),
        _page(2, "2\n1 Fig. 1.1 shows a speed-time graph.\n20 40 60 80\n(a) Calculate. [3]\n[Total: 8]"),
        _page(3, "3\n2 (a) Complete the definitions. [2]\n(b) Fig. 2.2 shows a ball.\n[Total: 7]"),
        _page(4, "4\n3 Fig. 3.1 shows solar cells.\n(a) State. [1]\n[Total: 9]"),
        _page(5, "5\n4 Fig. 4.1 shows a balloon.\n(a) Explain. [3]\n[Total: 7]"),
        _page(6, "6\n5 (a) Compare particles. [2]\n(b) Calculate mass. [2]\n[Total: 6]"),
        _page(7, "7\n0625/04/SP/23 © UCLES 2020 [Turn over\nBLANK PAGE"),
        _page(8, "8\n6 (a) Fig. 6.1 shows a lens.\n(i) Draw rays. [3]\nFig. 6.2"),
        _page(9, "9\n(b) Fig. 6.3 shows a prism. [2]\n[Total: 7]"),
        _page(10, "10\n7 (a) State the speed of sound. [1]\nFig. 7.1\n[Total: 7]"),
        _page(11, "11\n8 Fig. 8.1 is a circuit diagram.\n24 V\n(a) Calculate. [4]\n[Total: 6]"),
        _page(12, "12\n9 Fig. 9.1 shows a conducting ball.\n(a) Explain. [2]"),
        _page(13, "13\n(c) Calculate the current. [3]\n[Total: 7]"),
        _page(14, "14\n10 (a) Complete the nuclear equation. [2]\n[Total: 6]"),
        _page(15, "15\n11 (a) Describe a stable star. [3]\n(b) Describe CMBR. [3]\n[Total: 6]"),
        _page(16, "16\nPermission to reproduce items where third-party material is included.\n12 Fig. 12.1 shows a transformer.\n(a) Calculate turns. [2]\n[Total: 4]"),
    ]
    assert sum(question_totals) == 80
    return pages


def test_full_exam_report_accepts_reference_structure():
    report = build_full_exam_intake_report(_reference_exam_pages())

    assert report.status == FullExamIntakeStatus.accepted
    assert report.page_count == 16
    assert report.content_page_count == 15
    assert report.blank_page_count == 1
    assert report.cover_page_count == 1
    assert report.detected_question_count == 12
    assert report.detected_question_numbers == [str(value) for value in range(1, 13)]
    assert report.reported_total_marks == 80
    assert report.detected_total_marks == 80
    assert report.multi_page_question_count == 2
    assert report.pages[6].kind == PdfPageKind.blank


def test_page_aware_parser_preserves_continuation_pages_and_totals():
    questions = parse_full_exam_questions_from_pages(_reference_exam_pages())

    assert len(questions) == 12
    assert questions[0].original_number == "1"
    assert questions[0].detected_marks == 8
    assert questions[5].source_page_numbers == [8, 9]
    assert questions[5].source_page_start == 8
    assert questions[5].source_page_end == 9
    assert questions[8].source_page_numbers == [12, 13]
    assert questions[10].source_page_numbers == [15]
    assert questions[11].source_page_numbers == [16]


def test_graph_axis_values_do_not_become_questions():
    pages = _reference_exam_pages()
    questions = parse_full_exam_questions_from_pages(pages)

    assert [question.original_number for question in questions] == [
        str(value) for value in range(1, 13)
    ]
    assert "20 40 60 80" in questions[0].original_text


def test_layout_snapshots_are_linked_by_source_page():
    questions = parse_full_exam_questions_from_pages(_reference_exam_pages())
    assets = [
        PdfLayoutAssetInfo(
            id=f"page-{page_number}",
            name=f"page-{page_number}.png",
            size=100,
            type="image/png",
            data_base64="AA==",
            page_number=page_number,
        )
        for page_number in range(1, 17)
    ]

    linked = link_layout_assets_to_page_aware_questions(questions, assets)
    report = build_full_exam_intake_report(_reference_exam_pages(), questions=linked)

    assert linked[5].linked_layout_asset_ids == ["page-8", "page-9"]
    assert linked[8].linked_layout_asset_ids == ["page-12", "page-13"]
    assert report.auto_linked_layout_asset_count == 14


def test_report_requires_review_when_paper_total_does_not_match():
    report = build_full_exam_intake_report(
        _reference_exam_pages(reported_total=81),
    )

    assert report.status == FullExamIntakeStatus.needs_review
    assert report.reported_total_marks == 81
    assert report.detected_total_marks == 80
    assert any("لا تطابق" in warning for warning in report.warnings)


def test_old_extracted_text_payload_remains_compatible():
    extracted = ExtractedTextInfo(
        text="1 State the unit of force. [1]",
        preview="1 State the unit of force.",
        page_count=1,
        character_count=35,
        is_text_based=True,
        message="legacy",
    )

    assert extracted.pages == []


def test_old_project_snapshot_remains_compatible_without_intake_report():
    project = ProjectSession.model_validate({})

    assert project.full_exam_intake_report is None
