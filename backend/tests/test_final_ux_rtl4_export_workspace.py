from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_export_workspace_has_readiness_summary() -> None:
    content = (
        ROOT / "frontend/src/features/export/ExportStep.tsx"
    ).read_text(encoding="utf-8")

    assert 'className="export-workspace export-workspace-redesign"' in content
    assert "مركز الجاهزية والتصدير" in content
    assert 'className="export-readiness-summary"' in content
    assert "المراجعة اليدوية" in content
    assert "الرسوم المرتبطة" in content


def test_export_workspace_has_three_choice_cards() -> None:
    content = (
        ROOT / "frontend/src/features/export/ExportStep.tsx"
    ).read_text(encoding="utf-8")

    assert 'className="export-choice-grid"' in content
    assert "نسخة عربية نظيفة" in content
    assert "نسخة ثنائية اللغة" in content
    assert "Word DOCX" in content
    assert "PDF للطباعة" in content
    assert "هوية المدرسة" in content


def test_export_workspace_has_single_primary_export_action() -> None:
    content = (
        ROOT / "frontend/src/features/export/ExportStep.tsx"
    ).read_text(encoding="utf-8")

    assert "handleExportSelected" in content
    assert 'className="primary-button export-main-button"' in content
    assert "تصدير Word وPDF" in content


def test_advanced_export_reports_are_collapsed() -> None:
    content = (
        ROOT / "frontend/src/features/export/ExportStep.tsx"
    ).read_text(encoding="utf-8")

    assert 'className="export-advanced-tools"' in content
    assert "الفحوص والتقارير المتقدمة" in content
    assert 'className="form-card export-legacy-hidden"' in content


def test_export_workspace_rtl_styles_exist() -> None:
    content = (
        ROOT / "frontend/src/styles/global.css"
    ).read_text(encoding="utf-8")

    assert ".export-choice-grid" in content
    assert ".export-preview-grid" in content
    assert ".export-primary-action" in content
    assert ".export-advanced-tools" in content
