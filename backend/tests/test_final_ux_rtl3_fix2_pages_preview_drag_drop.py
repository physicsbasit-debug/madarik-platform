from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_upload_zone_has_drag_and_drop_handlers() -> None:
    content = (
        ROOT
        / "frontend/src/features/file-upload/FileUploadStep.tsx"
    ).read_text(encoding="utf-8")

    assert "onDragEnter={handleDragOver}" in content
    assert "onDragOver={handleDragOver}" in content
    assert "onDragLeave={handleDragLeave}" in content
    assert "onDrop={handleDrop}" in content
    assert "event.dataTransfer.files" in content


def test_github_pages_preview_message_is_explicit() -> None:
    content = (
        ROOT / "frontend/src/app/App.tsx"
    ).read_text(encoding="utf-8")

    assert 'window.location.hostname.endsWith(".github.io")' in content
    assert "هذه نسخة معاينة على GitHub Pages" in content
    assert "الاستخراج والترجمة والقص تحتاج Backend" in content


def test_drag_active_style_exists() -> None:
    content = (
        ROOT / "frontend/src/styles/global.css"
    ).read_text(encoding="utf-8")

    assert ".start-upload-zone.is-drag-active" in content
