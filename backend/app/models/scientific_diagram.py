from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class ScientificDiagramType(str, Enum):
    process = "process"
    cycle = "cycle"
    comparison = "comparison"
    sequence = "sequence"
    structure = "structure"
    cause_effect = "cause_effect"


class ScientificDiagramNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    label: str
    description: str | None = None
    order_index: int = Field(default=1, ge=1)


class ScientificDiagramEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_node_id: str
    target_node_id: str
    label: str | None = None
    order_index: int = Field(default=1, ge=1)


class ScientificDiagram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    owner_account_id: str | None = None
    source_project_id: str | None = None
    title: str
    diagram_type: ScientificDiagramType
    grade: int = Field(ge=1, le=12)
    science_domain: str
    subject_id: str
    semester_id: str | None = None
    unit_id: str | None = None
    lesson_id: str | None = None
    learning_outcome_ids: list[str] = Field(default_factory=list)
    description: str | None = None
    nodes: list[ScientificDiagramNode] = Field(default_factory=list)
    edges: list[ScientificDiagramEdge] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ScientificDiagramCreateRequest(BaseModel):
    source_project_id: str | None = None
    title: str
    diagram_type: ScientificDiagramType
    grade: int = Field(ge=1, le=12)
    science_domain: str
    subject_id: str
    semester_id: str | None = None
    unit_id: str | None = None
    lesson_id: str | None = None
    learning_outcome_ids: list[str] = Field(default_factory=list)
    description: str | None = None
    nodes: list[ScientificDiagramNode] = Field(default_factory=list)
    edges: list[ScientificDiagramEdge] = Field(default_factory=list)


class ScientificDiagramListResponse(BaseModel):
    items: list[ScientificDiagram]
    total: int


class ScientificDiagramPreviewNode(BaseModel):
    id: str
    label: str
    description: str | None = None
    x: float
    y: float
    width: float
    height: float


class ScientificDiagramPreviewEdge(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    label: str | None = None
    x1: float
    y1: float
    x2: float
    y2: float


class ScientificDiagramPreview(BaseModel):
    id: str
    title: str
    diagram_type: ScientificDiagramType
    width: int
    height: int
    nodes: list[ScientificDiagramPreviewNode] = Field(
        default_factory=list
    )
    edges: list[ScientificDiagramPreviewEdge] = Field(
        default_factory=list
    )
    svg: str
    export_ready: bool
    issues: list[str] = Field(default_factory=list)


class ScientificDiagramSvgExportResponse(BaseModel):
    diagram_id: str
    filename: str
    svg: str
    export_ready: bool
    issues: list[str] = Field(default_factory=list)
