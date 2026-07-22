from pathlib import Path
from zipfile import ZipFile

from app.models.assessment import (
    AssessmentBlueprint,
    AssessmentDraft,
    AssessmentItemConfiguration,
    AssessmentSection,
)
from app.models.project import QuestionItem
from app.models.question_bank import QuestionBankItem
from app.services.assessment_export import (
    export_assessment_foundation,
)
from app.services.question_bank_repository import (
    QuestionBankRepository,
)


ROOT = Path(__file__).resolve().parents[2]


def save_item(
    repository: QuestionBankRepository,
    item_id: str,
    marks: int,
) -> None:
    item = QuestionBankItem(
        id=item_id,
        source_project_id="source",
        source_question_id=f"q-{item_id}",
        content_fingerprint=item_id,
        question_snapshot=QuestionItem(
            id=f"q-{item_id}",
            original_number=item_id,
            original_text="سؤال علمي",
            translated_text="سؤال علمي",
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


def draft() -> AssessmentDraft:
    section = AssessmentSection(
        id="s1",
        title="القسم الأول",
        instructions="أجب عن جميع الأسئلة.",
        order_index=1,
    )
    return AssessmentDraft(
        blueprint=AssessmentBlueprint(
            title="اختبار العلوم",
            grade=10,
            duration_minutes=40,
            total_marks=2,
            target_question_count=1,
        ),
        sections=[section],
        question_bank_item_ids=["one"],
        item_configurations=[
            AssessmentItemConfiguration(
                bank_item_id="one",
                section_id="s1",
                order_index=1,
            )
        ],
    )


def test_native_docx_export(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "db.sqlite"
    )
    save_item(repository, "one", 2)

    import app.services.assessment_export as module
    monkeypatch.setattr(
        module,
        "EXPORT_DIR",
        tmp_path / "exports",
    )

    result = export_assessment_foundation(
        draft(),
        repository,
        "docx",
    )

    assert result.export_ready is True
    assert result.filename.endswith(".docx")
    assert Path(result.path).exists()

    with ZipFile(result.path) as archive:
        assert "word/document.xml" in archive.namelist()


def test_native_pdf_export(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "db.sqlite"
    )
    save_item(repository, "one", 2)

    import app.services.assessment_export as module
    monkeypatch.setattr(
        module,
        "EXPORT_DIR",
        tmp_path / "exports",
    )

    result = export_assessment_foundation(
        draft(),
        repository,
        "pdf",
    )

    assert result.export_ready is True
    assert result.filename.endswith(".pdf")
    assert Path(result.path).read_bytes().startswith(
        b"%PDF"
    )


def test_export_blocked_when_not_ready(
    tmp_path: Path,
) -> None:
    repository = QuestionBankRepository(
        tmp_path / "db.sqlite"
    )
    incomplete = AssessmentDraft(
        blueprint=AssessmentBlueprint(
            title="اختبار",
            total_marks=1,
            target_question_count=1,
        )
    )

    result = export_assessment_foundation(
        incomplete,
        repository,
        "docx",
    )

    assert result.export_ready is False
    assert result.path == ""
    assert result.issues


def test_api_uses_file_response() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")
    assert "FileResponse" in content
    assert "Assessment is not export ready" in content


def test_frontend_downloads_blob() -> None:
    content = (
        ROOT / "frontend/src/services/api.ts"
    ).read_text(encoding="utf-8")
    assert "response.blob()" in content
    assert "URL.createObjectURL" in content
    assert "anchor.download" in content


def test_readme_tracks_phase_6e() -> None:
    content = (ROOT / "README.md").read_text(
        encoding="utf-8"
    )
    assert "Phase 6-E" in content
    assert "Native DOCX and PDF Assessment Export" in content
