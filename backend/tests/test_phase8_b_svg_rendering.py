from pathlib import Path

from app.models.scientific_diagram import (
    ScientificDiagram,
    ScientificDiagramEdge,
    ScientificDiagramNode,
    ScientificDiagramType,
)
from app.services.scientific_diagram_renderer import (
    build_scientific_diagram_preview,
    export_scientific_diagram_svg,
)


ROOT = Path(__file__).resolve().parents[2]


def diagram(
    diagram_type: ScientificDiagramType,
) -> ScientificDiagram:
    first = ScientificDiagramNode(
        id="n1",
        label="بداية",
        order_index=1,
    )
    second = ScientificDiagramNode(
        id="n2",
        label="نهاية",
        order_index=2,
    )
    edge = ScientificDiagramEdge(
        id="e1",
        source_node_id="n1",
        target_node_id="n2",
        label="يؤدي إلى",
        order_index=1,
    )
    return ScientificDiagram(
        title="مخطط علمي",
        diagram_type=diagram_type,
        grade=10,
        science_domain="physics",
        subject_id="g10-physics",
        nodes=[first, second],
        edges=[edge],
    )


def test_preview_renders_svg() -> None:
    preview = build_scientific_diagram_preview(
        diagram(ScientificDiagramType.sequence)
    )

    assert preview.export_ready is True
    assert preview.svg.startswith("<svg")
    assert "arrowhead" in preview.svg
    assert "يؤدي إلى" in preview.svg


def test_cycle_positions_are_distinct() -> None:
    preview = build_scientific_diagram_preview(
        diagram(ScientificDiagramType.cycle)
    )

    first, second = preview.nodes
    assert (first.x, first.y) != (
        second.x,
        second.y,
    )


def test_invalid_edge_reports_issue() -> None:
    item = diagram(ScientificDiagramType.process)
    item.edges[0].target_node_id = "missing"

    preview = build_scientific_diagram_preview(
        item
    )

    assert preview.export_ready is False
    assert preview.issues


def test_svg_export_has_filename() -> None:
    result = export_scientific_diagram_svg(
        diagram(ScientificDiagramType.structure)
    )

    assert result.export_ready is True
    assert result.filename.endswith(".svg")
    assert "<rect" in result.svg


def test_api_routes_exist() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")

    assert "get_scientific_diagram_preview" in content
    assert "export_scientific_diagram_as_svg" in content


def test_frontend_has_preview_and_download() -> None:
    content = (
        ROOT
        / "frontend/src/features/diagrams/ScientificDiagrams.tsx"
    ).read_text(encoding="utf-8")

    assert "ScientificDiagramPreviewCard" in content
    assert "downloadSvg" in content
    assert "تنزيل SVG" in content


def test_readme_tracks_phase_8b() -> None:
    content = (
        ROOT / "README.md"
    ).read_text(encoding="utf-8")

    assert "Phase 8-B" in content
    assert (
        "Scientific Diagram Preview and SVG Rendering"
        in content
    )
