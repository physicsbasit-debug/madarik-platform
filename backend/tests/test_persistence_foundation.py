from pathlib import Path

from app.models.project import ProjectMetadata, QuestionPatch, QuestionStatus
from app.services.project_repository import ProjectRepository
from app.services.session_store import InMemoryProjectStore


def test_project_repository_persists_created_project(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "madarik-test.sqlite3")
    store = InMemoryProjectStore(repository)

    created = store.create(ProjectMetadata(paper_title="اختبار حفظ دائم", subject="فيزياء"))
    project_id = created.id

    fresh_store = InMemoryProjectStore(repository)
    loaded = fresh_store.get(project_id)

    assert loaded is not None
    assert loaded.id == project_id
    assert loaded.metadata.paper_title == "اختبار حفظ دائم"
    assert loaded.metadata.subject == "فيزياء"


def test_project_repository_persists_question_updates(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "madarik-test.sqlite3")
    store = InMemoryProjectStore(repository)

    created = store.create()
    store.load_demo_content(created.id)
    project = store.get(created.id)
    assert project is not None
    question_id = project.questions[0].id

    store.update_question(
        created.id,
        question_id,
        QuestionPatch(status=QuestionStatus.approved, translated_text="ترجمة محفوظة"),
    )

    fresh_store = InMemoryProjectStore(repository)
    loaded = fresh_store.get(created.id)
    assert loaded is not None
    updated_question = next(question for question in loaded.questions if question.id == question_id)

    assert updated_question.status == QuestionStatus.approved
    assert updated_question.translated_text == "ترجمة محفوظة"


def test_project_repository_deletes_persisted_project(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "madarik-test.sqlite3")
    store = InMemoryProjectStore(repository)

    created = store.create()
    assert store.delete(created.id) is True

    fresh_store = InMemoryProjectStore(repository)
    assert fresh_store.get(created.id) is None


def test_project_repository_lists_recent_projects(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "madarik-test.sqlite3")
    store = InMemoryProjectStore(repository)

    first = store.create(ProjectMetadata(paper_title="الأول"))
    second = store.create(ProjectMetadata(paper_title="الثاني"))

    recent = store.list_recent()

    recent_ids = [project.id for project in recent]
    assert second.id in recent_ids
    assert first.id in recent_ids
