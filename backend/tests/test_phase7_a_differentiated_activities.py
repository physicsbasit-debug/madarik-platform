from pathlib import Path

from app.models.differentiated_activity import (
    DifferentiatedActivityCreateRequest,
    DifferentiationLevel,
)
from app.services.differentiated_activity_repository import (
    DifferentiatedActivityRepository,
)

ROOT = Path(__file__).resolve().parents[2]


def payload(level: DifferentiationLevel):
    return DifferentiatedActivityCreateRequest(
        title="نشاط",
        grade=10,
        science_domain="physics",
        subject_id="g10-physics",
        level=level,
        objective="هدف",
        instructions="تعليمات",
    )


def test_create_list_filter(tmp_path):
    repository = DifferentiatedActivityRepository(tmp_path / "db.sqlite")
    created = repository.create(payload(DifferentiationLevel.support))
    items = repository.list(grade=10, level="support")
    assert len(items) == 1
    assert items[0].id == created.id


def test_delete(tmp_path):
    repository = DifferentiatedActivityRepository(tmp_path / "db.sqlite")
    created = repository.create(payload(DifferentiationLevel.core))
    assert repository.delete(created.id) is not None
    assert repository.list() == []


def test_api_routes():
    content = (ROOT / "backend/app/api/projects.py").read_text(encoding="utf-8")
    assert "list_differentiated_activities" in content
    assert "create_differentiated_activity" in content
    assert "delete_differentiated_activity" in content


def test_frontend_workspace():
    content = (ROOT / "frontend/src/features/activities/DifferentiatedActivities.tsx").read_text(encoding="utf-8")
    assert "الأنشطة المتمايزة" in content
    assert "حفظ النشاط" in content
    assert "إثراء" in content


def test_task_home():
    home = (ROOT / "frontend/src/features/workflow/ScienceTaskHome.tsx").read_text(encoding="utf-8")
    app = (ROOT / "frontend/src/app/App.tsx").read_text(encoding="utf-8")
    assert "onOpenDifferentiatedActivities" in home
    assert "فتح الأنشطة المتمايزة" in home
    assert 'workspaceMode === "differentiated-activities"' in app


def test_readme():
    content = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Phase 7-A" in content
    assert "Differentiated Science Activities Foundation" in content
