from pathlib import Path

from app.models.assessment import (
    AssessmentBlueprint,
    AssessmentDraft,
    AssessmentItemConfiguration,
    AssessmentSection,
)
from app.models.project import QuestionItem
from app.models.question_bank import QuestionBankItem
from app.services.assessment_export import (
    build_student_paper_preview,
    export_assessment_foundation,
)
from app.services.question_bank_repository import (
    QuestionBankRepository,
)


ROOT = Path(__file__).resolve().parents[2]


def save_bank_item(
    repository: QuestionBankRepository,
    item_id: str,
    text: str,
    marks: int,
) -> QuestionBankItem:
    item = QuestionBankItem(
        id=item_id,
        source_project_id="source",
        source_question_id=f"q-{item_id}",
        content_fingerprint=item_id,
        question_snapshot=QuestionItem(
            id=f"q-{item_id}",
            original_number=item_id,
            original_text=text,
            translated_text=text,
            marks=marks,
            order_index=1,
        ),
    )
    with repository._connect() as connection:
        connection.execute(
            """
            INSERT INTO question_bank (
                id,
                source_project_id,
                source_question_id,
                owner_account_id,
                content_fingerprint,
                updated_at,
                payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id,
                item.source_project_id,
                item.source_question_id,
                None,
                item.content_fingerprint,
                item.updated_at.isoformat(),
                item.model_dump_json(),
            ),
        )
    return item


def build_draft() -> AssessmentDraft:
    section = AssessmentSection(
        id="s1",
        title="القسم الأول",
        instructions="أجب عن جميع الأسئلة.",
        order_index=1,
    )
    return AssessmentDraft(
        blueprint=AssessmentBlueprint(
            title="اختبار الفيزياء",
            grade=10,
            duration_minutes=40,
            total_marks=5,
            target_question_count=2,
        ),
        sections=[section],
        question_bank_item_ids=["one", "two"],
        item_configurations=[
            AssessmentItemConfiguration(
                bank_item_id="two",
                section_id="s1",
                order_index=1,
                marks_override=3,
            ),
            AssessmentItemConfiguration(
                bank_item_id="one",
                section_id="s1",
                order_index=2,
            ),
        ],
    )


def test_preview_groups_and_orders_questions(
    tmp_path: Path,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "db.sqlite"
    )
    save_bank_item(repository, "one", "السؤال الأول", 2)
    save_bank_item(repository, "two", "السؤال الثاني", 2)

    preview = build_student_paper_preview(
        build_draft(),
        repository,
    )

    assert preview.export_ready is True
    assert preview.sections[0].title == "القسم الأول"
    assert (
        preview.sections[0].questions[0].bank_item_id
        == "two"
    )
    assert preview.sections[0].questions[0].marks == 3


def test_preview_reports_missing_questions(
    tmp_path: Path,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "db.sqlite"
    )
    draft = AssessmentDraft(
        title="اختبار",
        target_question_count=1,
        total_marks=1,
    )

    preview = build_student_paper_preview(
        draft,
        repository,
    )

    assert preview.export_ready is False
    assert preview.issues


def test_foundation_export_writes_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "db.sqlite"
    )
    save_bank_item(repository, "one", "السؤال الأول", 2)
    save_bank_item(repository, "two", "السؤال الثاني", 2)

    import app.services.assessment_export as module
    monkeypatch.setattr(
        module,
        "EXPORT_DIR",
        tmp_path / "exports",
    )

    result = export_assessment_foundation(
        build_draft(),
        repository,
        "docx",
    )

    assert Path(result.path).exists()
    content = Path(result.path).read_text(
        encoding="utf-8"
    )
    assert "اختبار الفيزياء" in content
    assert "صفحة الإجابة" in content


def test_api_routes_exist() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")
    assert "get_assessment_student_preview" in content
    assert "export_assessment_draft" in content
    assert "student-preview" in content


def test_frontend_has_preview_and_export() -> None:
    content = (
        ROOT
        / "frontend/src/features/assessment/AssessmentBuilder.tsx"
    ).read_text(encoding="utf-8")
    assert "معاينة ورقة الطالب" in content
    assert "تصدير DOCX أولي" in content
    assert "AssessmentStudentPreview" in content


def test_readme_tracks_phase_6d() -> None:
    content = (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Phase 6-D" in content
    assert (
        "Student Paper Preview and Assessment Export Foundation"
        in content
    )
