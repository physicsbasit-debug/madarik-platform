from pathlib import Path

from app.models.scientific_diagram import (
    ScientificDiagramCreateRequest,
    ScientificDiagramNode,
    ScientificDiagramType,
)
from app.services.scientific_diagram_repository import (
    ScientificDiagramRepository,
)

ROOT = Path(__file__).resolve().parents[2]


def request() -> ScientificDiagramCreateRequest:
    return ScientificDiagramCreateRequest(
        title="دورة الماء",
        diagram_type=ScientificDiagramType.cycle,
        grade=6,
        science_domain="general_science",
        subject_id="g6-science",
        nodes=[
            ScientificDiagramNode(
                label="تبخر",
                order_index=1,
            ),
            ScientificDiagramNode(
                label="تكاثف",
                order_index=2,
            ),
        ],
    )


def test_repository_creates_and_lists(tmp_path: Path) -> None:
    repository = ScientificDiagramRepository(
        tmp_path / "db.sqlite"
    )
    created = repository.create(request())
    items = repository.list(diagram_type="cycle")
    assert len(items) == 1
    assert items[0].id == created.id


def test_repository_deletes(tmp_path: Path) -> None:
    repository = ScientificDiagramRepository(
        tmp_path / "db.sqlite"
    )
    created = repository.create(request())
    removed = repository.delete(created.id)
    assert removed is not None
    assert repository.list() == []


def test_model_keeps_nodes() -> None:
    payload = request()
    assert len(payload.nodes) == 2
    assert payload.nodes[0].label == "تبخر"


def test_api_routes_exist() -> None:
    content = (ROOT / "backend/app/api/projects.py").read_text(
        encoding="utf-8"
    )
    assert "list_scientific_diagrams" in content
    assert "create_scientific_diagram" in content
    assert "delete_scientific_diagram" in content


def test_frontend_workspace_exists() -> None:
    content = (
        ROOT
        / "frontend/src/features/diagrams/ScientificDiagrams.tsx"
    ).read_text(encoding="utf-8")
    assert "الرسوم والمخططات العلمية" in content
    assert "حفظ الرسم" in content
    assert "سبب ونتيجة" in content


def test_task_home_opens_diagrams() -> None:
    home = (
        ROOT
        / "frontend/src/features/workflow/ScienceTaskHome.tsx"
    ).read_text(encoding="utf-8")
    app = (
        ROOT / "frontend/src/app/App.tsx"
    ).read_text(encoding="utf-8")
    assert "onOpenScientificDiagrams" in home
    assert 'workspaceMode === "scientific-diagrams"' in app


def test_readme_tracks_phase_8a() -> None:
    content = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Phase 8-A" in content
    assert "Scientific Diagram Data Model and Workspace Foundation" in content
