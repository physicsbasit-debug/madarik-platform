from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START = ROOT / "frontend/src/features/workflow/StartWorkspace.tsx"
CSS = ROOT / "frontend/src/styles/simplified-platform.css"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_batch_7_turns_start_workspace_into_simple_work_library() -> None:
    source = read(START)
    assert "أعمالي" in source
    assert "ابحث باسم العمل أو الملف" in source
    assert 'type WorkFilter = "all" | "current" | "review" | "ready" | "draft"' in source
    assert "الكل" in source
    assert "تحتاج مراجعة" in source
    assert "جاهزة" in source
    assert "مسودات" in source


def test_batch_7_keeps_real_project_actions_without_fake_exports() -> None:
    source = read(START)
    assert "onRefreshProjects" in source
    assert "onOpenProject(project.id)" in source
    assert "onDeleteProject(project.id)" in source
    assert "onDeleteProjects(selectedProjectIds)" in source
    assert "تصدير مباشر من البطاقة" not in source
    assert "نسخ العمل" not in source


def test_batch_7_hides_bulk_management_until_requested() -> None:
    source = read(START)
    assert '<details className="mdk-work-library__advanced">' in source
    assert "إدارة متقدمة" in source
    assert "تحديد عدة أعمال" in source
    assert "selectionMode ?" in source
    assert "حذف المحدد" in source


def test_batch_7_keeps_current_draft_upload_and_recovery() -> None:
    source = read(START)
    assert "رفع ورقة للعمل الحالي" in source
    assert "onFileSelected(file)" in source
    assert "onRetryInitialExtraction" in source
    assert "إعادة القراءة" in source
    assert "متابعة العمل" in source


def test_batch_7_has_responsive_library_styles() -> None:
    css = read(CSS)
    assert ".mdk-work-library__grid" in css
    assert ".mdk-current-work" in css
    assert ".mdk-work-card" in css
    assert "@media (max-width: 980px)" in css
    assert "@media (max-width: 720px)" in css
    assert "@media (max-width: 480px)" in css
