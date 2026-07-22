from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_quick_translation_workspace_exists() -> None:
    assert (
        ROOT
        / "frontend/src/features/workflow/QuickTranslationWorkspace.tsx"
    ).exists()


def test_quick_workspace_exposes_required_actions() -> None:
    content = (
        ROOT
        / "frontend/src/features/workflow/QuickTranslationWorkspace.tsx"
    ).read_text(encoding="utf-8")

    assert "تشغيل الترجمة السريعة" in content
    assert "فتح المراجعة الاحترافية" in content
    assert "الانتقال إلى التصدير" in content
    assert "onRunQuickTranslation" in content


def test_app_orchestrates_parse_translate_and_readiness() -> None:
    content = (
        ROOT / "frontend/src/app/App.tsx"
    ).read_text(encoding="utf-8")

    assert "runQuickTranslationWorkflow" in content
    assert "await parseExtractedQuestions(projectId)" in content
    assert "await translateProjectQuestions(projectId)" in content
    assert "await getProjectReadiness(projectId)" in content


def test_quick_flow_requires_extracted_text_and_backend() -> None:
    content = (
        ROOT / "frontend/src/app/App.tsx"
    ).read_text(encoding="utf-8")

    assert 'apiStatus === "offline"' in content
    assert "!extractedText?.isTextBased" in content


def test_quick_flow_can_open_review_and_export() -> None:
    content = (
        ROOT / "frontend/src/app/App.tsx"
    ).read_text(encoding="utf-8")

    assert "openQuickProfessionalReview" in content
    assert "setActiveIndex(1)" in content
    assert "openQuickExport" in content
    assert "setActiveIndex(2)" in content


def test_science_task_home_import_is_valid() -> None:
    content = (
        ROOT / "frontend/src/app/App.tsx"
    ).read_text(encoding="utf-8")

    assert (
        'import ScienceTaskHome from '
        '"../features/workflow/ScienceTaskHome";'
    ) in content
    assert "import type {\nimport ScienceTaskHome" not in content


def test_quick_translation_styles_are_responsive() -> None:
    content = (
        ROOT / "frontend/src/styles/global.css"
    ).read_text(encoding="utf-8")

    assert ".quick-translation-workspace" in content
    assert ".quick-translation-grid" in content
    assert "@media (max-width: 920px)" in content
    assert "@media (max-width: 640px)" in content


def test_phase_document_exists() -> None:
    assert (
        ROOT / "docs/PHASE_1_QUICK_TRANSLATION_WORKFLOW.md"
    ).exists()
