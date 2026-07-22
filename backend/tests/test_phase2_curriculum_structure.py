from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_curriculum_types_are_declared() -> None:
    content = read("frontend/src/types/project.ts")

    assert "export type ScienceDomain" in content
    assert "export type CurriculumSemester" in content
    assert "export type CurriculumSubject" in content
    assert "export type CurriculumUnit" in content
    assert "export type CurriculumLesson" in content
    assert "export type CurriculumLearningOutcome" in content


def test_catalog_covers_grades_1_to_12() -> None:
    content = read(
        "frontend/src/content/seed/science-curriculum.seed.ts"
    )

    assert "Array.from({ length: 12 }" in content
    assert "grade <= 8" in content
    assert '"physics"' in content
    assert '"general_science"' in content


def test_repository_is_only_seed_reader_for_ui() -> None:
    repository = read(
        "frontend/src/features/curriculum/local-curriculum.repository.ts"
    )
    browser = read(
        "frontend/src/features/curriculum/CurriculumBrowser.tsx"
    )

    assert "scienceCurriculumCatalog" in repository
    assert "science-curriculum.seed" not in browser
    assert "localCurriculumRepository" in browser


def test_repository_exposes_curriculum_navigation() -> None:
    content = read(
        "frontend/src/features/curriculum/local-curriculum.repository.ts"
    )

    assert "listGrades()" in content
    assert "listSemesters(grade" in content
    assert "listSubjects(grade" in content
    assert "listUnits(subjectId, semesterId)" in content
    assert "listLessons(unitId)" in content
    assert "listLearningOutcomes" in content


def test_curriculum_browser_exists() -> None:
    content = read(
        "frontend/src/features/curriculum/CurriculumBrowser.tsx"
    )

    assert "هيكل مناهج العلوم من الصف 1 إلى 12" in content
    assert "الوحدات والدروس" in content
    assert "نواتج التعلم" not in content or "curriculum-outcomes-list" in content


def test_task_home_opens_curriculum_browser() -> None:
    home = read(
        "frontend/src/features/workflow/ScienceTaskHome.tsx"
    )
    app = read("frontend/src/app/App.tsx")

    assert "onOpenCurriculum" in home
    assert "فتح مكتبة المناهج" in home
    assert 'workspaceMode === "curriculum"' in app
    assert "CurriculumBrowser" in app


def test_styles_are_responsive() -> None:
    content = read("frontend/src/styles/global.css")

    assert ".curriculum-browser" in content
    assert ".curriculum-unit-layout" in content
    assert "@media (max-width: 960px)" in content


def test_phase_document_exists() -> None:
    assert (
        ROOT / "docs/PHASE_2_CURRICULUM_STRUCTURE.md"
    ).exists()
