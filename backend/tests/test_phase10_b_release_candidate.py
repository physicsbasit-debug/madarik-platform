import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.release import (
    APP_VERSION,
    RELEASE_CHANNEL,
    RELEASE_PHASE,
    RELEASE_TITLE,
)
from app.main import app


ROOT = Path(__file__).resolve().parents[2]
CLIENT = TestClient(app)


def test_phase10_b_release_metadata_is_consistent() -> None:
    package = json.loads(
        (ROOT / "frontend/package.json").read_text(encoding="utf-8")
    )
    package_lock = json.loads(
        (ROOT / "frontend/package-lock.json").read_text(encoding="utf-8")
    )
    status = json.loads(
        (ROOT / "docs/FINAL_RELEASE_STATUS.json").read_text(encoding="utf-8")
    )
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert APP_VERSION == "2.0.0-rc.2"
    assert RELEASE_CHANNEL == "release-candidate"
    assert RELEASE_PHASE == "Phase 10-B"
    assert RELEASE_TITLE == "Final Release Candidate Consolidation and Sign-off"
    assert package["version"] == APP_VERSION
    assert package_lock["version"] == APP_VERSION
    assert package_lock["packages"][""]["version"] == APP_VERSION
    assert status["version"] == APP_VERSION
    assert status["phase"] == RELEASE_PHASE
    assert f"`{APP_VERSION}`" in readme
    assert RELEASE_PHASE in readme


def test_phase10_b_readiness_endpoint_uses_rc_metadata() -> None:
    response = CLIENT.get("/api/health/readiness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["version"] == APP_VERSION
    assert payload["channel"] == RELEASE_CHANNEL
    assert payload["phase"] == RELEASE_PHASE
    assert payload["phase_title"] == RELEASE_TITLE
    assert payload["technical_ready"] is True
    assert payload["live_external_acceptance_required"] is True
    assert payload["live_external_acceptance_completed"] is False


def test_final_release_status_preserves_required_live_blockers() -> None:
    status = json.loads(
        (ROOT / "docs/FINAL_RELEASE_STATUS.json").read_text(encoding="utf-8")
    )

    open_blockers = {
        item["id"]
        for item in status["blockers"]
        if item["status"] == "open"
    }
    assert open_blockers == {
        "live_external_provider_acceptance",
        "visual_docx_pdf_review",
    }
    assert status["technical_candidate"] == "ready_for_ci"
    assert status["production_release"] == "blocked"
    assert status["tag_allowed"] is False
    assert status["github_release_allowed"] is False


def test_only_one_release_gate_workflow_is_active() -> None:
    workflow_dir = ROOT / ".github/workflows"
    release_workflows: list[Path] = []

    for path in [*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")]:
        text = path.read_text(encoding="utf-8")
        if any(
            marker in text
            for marker in (
                "RUN_PHASE10_B_RC_PREFLIGHT.py",
                "Backend full test suite",
                "Final RC",
                "Release Gate",
                "Final Release Checks",
            )
        ):
            release_workflows.append(path)

    assert [path.name for path in release_workflows] == ["phase0-check.yml"]
    workflow = release_workflows[0].read_text(encoding="utf-8")
    assert "name: Phase 10-B Final RC Gate" in workflow
    assert "RUN_PHASE10_B_RC_PREFLIGHT.py" in workflow
    assert "test_phase10_b_release_candidate.py" in workflow
    assert "npm run lint" in workflow
    assert "npm run build" in workflow
    assert "name: Final Release Checks" not in workflow
    assert "name: Phase 10-A Release Gate" not in workflow


def test_phase10_b_acceptance_documents_are_versioned() -> None:
    for relative in (
        "docs/FINAL_RELEASE_ACCEPTANCE.md",
        "docs/FINAL_RELEASE_ACCEPTANCE_CHECKLIST.md",
        "docs/PHASE_10_B_FINAL_RC_SIGNOFF.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert APP_VERSION in text
        assert RELEASE_PHASE in text



def test_phase10_c_live_acceptance_assets_are_present_and_redacted() -> None:
    workflow = (
        ROOT / ".github/workflows/phase10-c-live-gemini.yml"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "RUN_PHASE10_C_LIVE_GEMINI_ACCEPTANCE.py"
    ).read_text(encoding="utf-8")
    status = json.loads(
        (ROOT / "docs/FINAL_RELEASE_STATUS.json").read_text(
            encoding="utf-8"
        )
    )

    assert "name: Phase 10-C Live Gemini Acceptance" in workflow
    assert "pull_request:" not in workflow
    assert "secrets.GEMINI_API_KEY" in workflow
    assert "provider_note" not in runner
    assert "translated_text_sha256" in runner
    assert status["live_external_acceptance"] == {
        "provider": "gemini",
        "status": "pending_ci",
        "gate": "phase10-c-live-gemini-acceptance",
        "evidence": "GitHub Actions redacted JSON artifact",
        "stores_secret_or_raw_content": False,
        "closes_full_cambridge_blocker": False,
    }
