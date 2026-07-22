from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_start_workspace_has_professional_overview_strip() -> None:
    content = read("frontend/src/features/workflow/StartWorkspace.tsx")
    assert "start-overview-strip" in content
    assert "المشروع الحالي" in content
    assert "تحتاج مراجعة" in content


def test_review_workspace_has_summary_and_balanced_actions() -> None:
    content = read("frontend/src/features/review/ReviewStep.tsx")
    assert "review-overview-panel" in content
    assert "review-layout-redesign" in content
    assert "راجع التنبيهات بدل مراجعة كل شيء من الصفر" in content


def test_export_workspace_separates_readiness_from_advanced_tools() -> None:
    content = read("frontend/src/features/export/ExportStep.tsx")
    assert "export-control-bar-redesign" in content
    assert "export-readiness-button" in content
    assert "الفحوص والتقارير المتقدمة أسفل الصفحة" in content


def test_marks_decision_choices_have_consistent_structure() -> None:
    content = read("frontend/src/features/export/ExportStep.tsx")
    assert "اعتماد مجموع الأسئلة" in content
    assert "تحويل الدرجة إلى المعلنة" in content
    assert "<strong>{totalMarks}</strong>" in content
    assert "<strong>{declaredMarks}</strong>" in content


def test_css_contains_complete_responsive_redesign() -> None:
    content = read("frontend/src/styles/global.css")
    assert "Madarik UX final professional redesign" in content
    assert ".start-overview-strip" in content
    assert ".review-overview-panel" in content
    assert ".export-workspace-redesign .marks-decision-actions" in content
    assert "@media (max-width: 760px)" in content
