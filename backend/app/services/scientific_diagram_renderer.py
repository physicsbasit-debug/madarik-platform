from __future__ import annotations

from html import escape
from pathlib import Path

import cairosvg
from math import cos, pi, sin

from app.models.scientific_diagram import (
    ScientificDiagram,
    ScientificDiagramPreview,
    ScientificDiagramPreviewEdge,
    ScientificDiagramPreviewNode,
    ScientificDiagramSvgExportResponse,
    ScientificDiagramBinaryExportResponse,
    ScientificDiagramType,
)


EXPORT_DIR = Path("data/exports/scientific-diagrams")

CANVAS_WIDTH = 960
CANVAS_HEIGHT = 620
NODE_WIDTH = 180
NODE_HEIGHT = 72


def _linear_positions(
    count: int,
    *,
    horizontal: bool = True,
) -> list[tuple[float, float]]:
    if count <= 0:
        return []

    margin = 90
    if horizontal:
        usable = CANVAS_WIDTH - (2 * margin)
        step = usable / max(count - 1, 1)
        return [
            (margin + index * step, CANVAS_HEIGHT / 2)
            for index in range(count)
        ]

    usable = CANVAS_HEIGHT - (2 * margin)
    step = usable / max(count - 1, 1)
    return [
        (CANVAS_WIDTH / 2, margin + index * step)
        for index in range(count)
    ]


def _cycle_positions(
    count: int,
) -> list[tuple[float, float]]:
    if count <= 0:
        return []

    radius = min(CANVAS_WIDTH, CANVAS_HEIGHT) * 0.32
    center_x = CANVAS_WIDTH / 2
    center_y = CANVAS_HEIGHT / 2

    return [
        (
            center_x
            + radius
            * cos((2 * pi * index / count) - (pi / 2)),
            center_y
            + radius
            * sin((2 * pi * index / count) - (pi / 2)),
        )
        for index in range(count)
    ]


def _comparison_positions(
    count: int,
) -> list[tuple[float, float]]:
    if count <= 0:
        return []

    left_count = (count + 1) // 2
    right_count = count - left_count
    positions: list[tuple[float, float]] = []

    for index in range(left_count):
        y = 150 + index * 120
        positions.append((CANVAS_WIDTH * 0.28, y))

    for index in range(right_count):
        y = 150 + index * 120
        positions.append((CANVAS_WIDTH * 0.72, y))

    return positions


def _structure_positions(
    count: int,
) -> list[tuple[float, float]]:
    if count <= 0:
        return []

    positions = [(CANVAS_WIDTH / 2, 110)]
    if count == 1:
        return positions

    child_count = count - 1
    usable = CANVAS_WIDTH - 180
    step = usable / max(child_count - 1, 1)
    for index in range(child_count):
        positions.append(
            (90 + index * step, CANVAS_HEIGHT - 130)
        )
    return positions


def _positions(
    diagram_type: ScientificDiagramType,
    count: int,
) -> list[tuple[float, float]]:
    if diagram_type is ScientificDiagramType.cycle:
        return _cycle_positions(count)
    if diagram_type is ScientificDiagramType.comparison:
        return _comparison_positions(count)
    if diagram_type is ScientificDiagramType.structure:
        return _structure_positions(count)
    if diagram_type is ScientificDiagramType.cause_effect:
        return _linear_positions(count, horizontal=True)
    if diagram_type is ScientificDiagramType.sequence:
        return _linear_positions(count, horizontal=True)
    return _linear_positions(count, horizontal=False)


def build_scientific_diagram_preview(
    diagram: ScientificDiagram,
) -> ScientificDiagramPreview:
    issues: list[str] = []

    if not diagram.title.strip():
        issues.append("عنوان الرسم غير موجود.")
    if not diagram.nodes:
        issues.append("لا توجد عقد في الرسم.")

    sorted_nodes = sorted(
        diagram.nodes,
        key=lambda item: item.order_index,
    )
    positions = _positions(
        diagram.diagram_type,
        len(sorted_nodes),
    )

    preview_nodes = [
        ScientificDiagramPreviewNode(
            id=node.id,
            label=node.label,
            description=node.description,
            x=x,
            y=y,
            width=NODE_WIDTH,
            height=NODE_HEIGHT,
        )
        for node, (x, y) in zip(sorted_nodes, positions)
    ]

    node_map = {
        node.id: node for node in preview_nodes
    }
    preview_edges: list[
        ScientificDiagramPreviewEdge
    ] = []

    for edge in sorted(
        diagram.edges,
        key=lambda item: item.order_index,
    ):
        source = node_map.get(edge.source_node_id)
        target = node_map.get(edge.target_node_id)

        if source is None or target is None:
            issues.append(
                "يوجد رابط يشير إلى عقدة غير موجودة."
            )
            continue

        preview_edges.append(
            ScientificDiagramPreviewEdge(
                id=edge.id,
                source_node_id=edge.source_node_id,
                target_node_id=edge.target_node_id,
                label=edge.label,
                x1=source.x,
                y1=source.y,
                x2=target.x,
                y2=target.y,
            )
        )

    svg = render_svg(
        diagram.title,
        preview_nodes,
        preview_edges,
    )

    return ScientificDiagramPreview(
        id=diagram.id,
        title=diagram.title,
        diagram_type=diagram.diagram_type,
        width=CANVAS_WIDTH,
        height=CANVAS_HEIGHT,
        nodes=preview_nodes,
        edges=preview_edges,
        svg=svg,
        export_ready=not issues,
        issues=issues,
    )


def _node_svg(
    node: ScientificDiagramPreviewNode,
) -> str:
    x = node.x - (node.width / 2)
    y = node.y - (node.height / 2)
    label = escape(node.label)
    description = (
        escape(node.description)
        if node.description
        else ""
    )

    description_svg = ""
    if description:
        description_svg = (
            f'<text x="{node.x}" y="{node.y + 18}" '
            'text-anchor="middle" '
            'font-size="12" fill="#5e6877">'
            f"{description}</text>"
        )

    return (
        f'<g data-node-id="{node.id}">'
        f'<rect x="{x}" y="{y}" '
        f'width="{node.width}" height="{node.height}" '
        'rx="14" fill="#ffffff" '
        'stroke="#415d91" stroke-width="2"/>'
        f'<text x="{node.x}" y="{node.y - 4}" '
        'text-anchor="middle" '
        'font-size="16" font-weight="700" '
        'fill="#28303f">'
        f"{label}</text>"
        f"{description_svg}"
        "</g>"
    )


def _edge_svg(
    edge: ScientificDiagramPreviewEdge,
) -> str:
    label = ""
    if edge.label:
        mid_x = (edge.x1 + edge.x2) / 2
        mid_y = (edge.y1 + edge.y2) / 2
        label = (
            f'<text x="{mid_x}" y="{mid_y - 8}" '
            'text-anchor="middle" '
            'font-size="12" fill="#52617a">'
            f"{escape(edge.label)}</text>"
        )

    return (
        f'<g data-edge-id="{edge.id}">'
        f'<line x1="{edge.x1}" y1="{edge.y1}" '
        f'x2="{edge.x2}" y2="{edge.y2}" '
        'stroke="#6a7da3" stroke-width="2.5" '
        'marker-end="url(#arrowhead)"/>'
        f"{label}"
        "</g>"
    )


def render_svg(
    title: str,
    nodes: list[ScientificDiagramPreviewNode],
    edges: list[ScientificDiagramPreviewEdge],
) -> str:
    title_text = escape(title)
    edges_svg = "".join(
        _edge_svg(edge) for edge in edges
    )
    nodes_svg = "".join(
        _node_svg(node) for node in nodes
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{CANVAS_WIDTH}" '
        f'height="{CANVAS_HEIGHT}" '
        f'viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}" '
        'role="img" '
        f'aria-label="{title_text}">'
        '<defs>'
        '<marker id="arrowhead" markerWidth="10" '
        'markerHeight="7" refX="9" refY="3.5" '
        'orient="auto">'
        '<polygon points="0 0, 10 3.5, 0 7" '
        'fill="#6a7da3"/>'
        '</marker>'
        '</defs>'
        '<rect width="100%" height="100%" '
        'fill="#f8faff"/>'
        f'<text x="{CANVAS_WIDTH / 2}" y="42" '
        'text-anchor="middle" '
        'font-size="24" font-weight="700" '
        'fill="#28303f">'
        f"{title_text}</text>"
        f"{edges_svg}"
        f"{nodes_svg}"
        "</svg>"
    )


def export_scientific_diagram_svg(
    diagram: ScientificDiagram,
) -> ScientificDiagramSvgExportResponse:
    preview = build_scientific_diagram_preview(
        diagram
    )
    filename = (
        diagram.title.strip().replace("/", "-")
        or "scientific-diagram"
    ) + f"-{diagram.id}.svg"

    return ScientificDiagramSvgExportResponse(
        diagram_id=diagram.id,
        filename=filename,
        svg=preview.svg,
        export_ready=preview.export_ready,
        issues=preview.issues,
    )


def export_scientific_diagram_binary(
    diagram: ScientificDiagram,
    output_format: str,
) -> ScientificDiagramBinaryExportResponse:
    preview = build_scientific_diagram_preview(
        diagram
    )

    if not preview.export_ready:
        return ScientificDiagramBinaryExportResponse(
            diagram_id=diagram.id,
            format=output_format,
            filename="",
            path="",
            export_ready=False,
            issues=preview.issues,
        )

    EXPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    safe_title = (
        diagram.title.strip().replace("/", "-")
        or "scientific-diagram"
    )
    filename = (
        f"{safe_title}-{diagram.id}."
        f"{output_format}"
    )
    path = EXPORT_DIR / filename
    svg_bytes = preview.svg.encode("utf-8")

    if output_format == "png":
        cairosvg.svg2png(
            bytestring=svg_bytes,
            write_to=str(path),
            output_width=preview.width,
            output_height=preview.height,
        )
    elif output_format == "pdf":
        cairosvg.svg2pdf(
            bytestring=svg_bytes,
            write_to=str(path),
        )
    else:
        raise ValueError(
            "Unsupported scientific diagram format"
        )

    return ScientificDiagramBinaryExportResponse(
        diagram_id=diagram.id,
        format=output_format,
        filename=filename,
        path=str(path),
        export_ready=True,
        issues=[],
    )
