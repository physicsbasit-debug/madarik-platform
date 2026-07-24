from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/deploy-phase11a-preview.yml"
VITE_CONFIG = ROOT / "frontend/vite.config.ts"


def test_phase11_a_preview_workflow_builds_and_deploys_pages() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    required_markers = (
        "name: Deploy Phase 11-A Platform Preview",
        "feat/madarik-science-platform-v2",
        "actions/checkout@v6",
        "actions/setup-node@v6",
        "actions/configure-pages@v5",
        "actions/upload-pages-artifact@v4",
        "actions/deploy-pages@v4",
        "pages: write",
        "id-token: write",
        "needs: build",
        "environment:",
        "name: github-pages",
        "path: frontend/dist",
        "npm ci --no-audit --no-fund",
        "npm run lint",
        "npm run build -- --base=/${{ github.event.repository.name }}/",
        "vars.MADARIK_API_BASE_URL",
    )

    for marker in required_markers:
        assert marker in workflow


def test_pages_base_path_is_scoped_to_the_deployment_command() -> None:
    config = VITE_CONFIG.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "VITE_BASE_PATH" not in config
    assert "base:" not in config
    assert "npm run build -- --base=/${{ github.event.repository.name }}/" in workflow
