from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend" / "src"


def read(relative_path: str) -> str:
    return (FRONTEND / relative_path).read_text(encoding="utf-8")


def test_uploaded_file_starts_preparation_automatically() -> None:
    source = read("features/workflow/QuickTranslationWorkspace.tsx")

    assert "useEffect(() =>" in source
    assert "autoStartedFileRef" in source
    assert 'quickRunStatus !== "idle"' in source
    assert "autoStartedFileRef.current === fileRunKey" in source
    assert "onRunQuickTranslation();" in source
    assert "مدارك يجهّز الورقة" in source
    assert "لا تحتاج إلى الضغط على أي زر" in source


def test_workspace_reveals_only_the_current_stage() -> None:
    source = read("features/workflow/QuickTranslationWorkspace.tsx")

    assert 'type JourneyView = "upload" | "processing" | "error" | "decision"' in source
    assert 'viewStage === "upload"' in source
    assert 'viewStage === "processing"' in source
    assert 'viewStage === "error"' in source
    assert 'viewStage === "decision"' in source
    assert "mdk-simple-single-stage" in source
    assert "ستظهر النتيجة هنا بعد التجهيز" not in source


def test_error_state_keeps_a_safe_manual_retry() -> None:
    source = read("features/workflow/QuickTranslationWorkspace.tsx")

    assert 'quickRunStatus === "error"' in source
    assert "إعادة المحاولة" in source
    assert "retryDisabled" in source
    assert "retryAction" in source
    assert "onRunQuickTranslation" in source


def test_batch_3_styles_support_selected_file_and_mobile_layout() -> None:
    source = read("styles/simplified-platform.css")

    assert ".mdk-simple-file-ribbon" in source
    assert ".mdk-simple-journey-nav" in source
    assert ".mdk-simple-replace-file" in source
    assert "@media (max-width: 640px)" in source
    assert source.count("{") == source.count("}")
