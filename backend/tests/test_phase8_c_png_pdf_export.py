from pathlib import Path

from app.models.scientific_diagram import (
    ScientificDiagram,
    ScientificDiagramEdge,
    ScientificDiagramNode,
    ScientificDiagramType,
)
from app.services.scientific_diagram_renderer import (
    export_scientific_diagram_binary,
)


ROOT = Path(__file__).resolve().parents[2]


def diagram() -> ScientificDiagram:
    first = ScientificDiagramNode(
        id="n1",
        label="تبخر",
        order_index=1,
    )
    second = ScientificDiagramNode(
        id="n2",
        label="تكاثف",
        order_index=2,
    )
    edge = ScientificDiagramEdge(
        id="e1",
        source_node_id="n1",
        target_node_id="n2",
        order_index=1,
    )
    return ScientificDiagram(
        title="دورة الماء",
        diagram_type=ScientificDiagramType.cycle,
        grade=6,
        science_domain="general_science",
        subject_id="g6-science",
        nodes=[first, second],
        edges=[edge],
    )


def test_png_export(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import app.services.scientific_diagram_renderer as module

    monkeypatch.setattr(
        module,
        "EXPORT_DIR",
        tmp_path / "exports",
    )

    result = export_scientific_diagram_binary(
        diagram(),
        "png",
    )

    assert result.export_ready is True
    assert result.filename.endswith(".png")
    assert Path(result.path).read_bytes().startswith(
        b"\x89PNG"
    )


def test_pdf_export(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import app.services.scientific_diagram_renderer as module

    monkeypatch.setattr(
        module,
        "EXPORT_DIR",
        tmp_path / "exports",
    )

    result = export_scientific_diagram_binary(
        diagram(),
        "pdf",
    )

    assert result.export_ready is True
    assert result.filename.endswith(".pdf")
    assert Path(result.path).read_bytes().startswith(
        b"%PDF"
    )


def test_export_blocked_when_invalid(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import app.services.scientific_diagram_renderer as module

    monkeypatch.setattr(
        module,
        "EXPORT_DIR",
        tmp_path / "exports",
    )

    item = diagram()
    item.nodes = []

    result = export_scientific_diagram_binary(
        item,
        "png",
    )

    assert result.export_ready is False
    assert result.path == ""
    assert result.issues


def test_api_route_exists() -> None:
    content = (
        ROOT / "backend/app/api/projects.py"
    ).read_text(encoding="utf-8")

    assert "export_scientific_diagram_file" in content
    assert "FileResponse" in content


def test_frontend_has_png_pdf_controls() -> None:
    content = (
        ROOT
        / "frontend/src/features/diagrams/ScientificDiagrams.tsx"
    ).read_text(encoding="utf-8")

    assert "تنزيل PNG" in content
    assert "تنزيل PDF" in content
    assert "downloadBinary" in content


def test_readme_tracks_phase_8c() -> None:
    content = (
        ROOT / "README.md"
    ).read_text(encoding="utf-8")

    assert "Phase 8-C" in content
    assert "Scientific Diagram PNG and PDF Export" in content
