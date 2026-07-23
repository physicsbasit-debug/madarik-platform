from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.main import app
from app.models.assessment import AssessmentBlueprint
from app.models.cloud_source import (
    CloudSource,
    CloudSourceProvider,
    CloudSourceSyncResponse,
)
from app.models.differentiated_activity import (
    DifferentiatedActivityGenerationRequest,
)
from app.models.project import ProjectSession
from app.models.scientific_diagram import (
    ScientificDiagramCreateRequest,
    ScientificDiagramEdge,
    ScientificDiagramNode,
    ScientificDiagramType,
)
from app.services.assessment_builder import build_assessment_detail
from app.services.assessment_repository import AssessmentRepository
from app.services.auth_repository import AuthRepository
from app.services.cloud_source_lifecycle import (
    intake_cloud_source_version,
    refresh_cloud_source,
)
from app.services.cloud_source_repository import CloudSourceRepository
from app.services.cloud_source_version_repository import (
    CloudSourceVersionRepository,
)
from app.services.differentiated_activity_export import export_activity
from app.services.differentiated_activity_generator import (
    generate_differentiated_activity_set,
)
from app.services.differentiated_activity_repository import (
    DifferentiatedActivityRepository,
)
from app.services.project_repository import ProjectRepository
from app.services.question_bank_repository import QuestionBankRepository
from app.services.release_readiness import build_release_readiness_report
from app.services.scientific_diagram_renderer import (
    export_scientific_diagram_binary,
)
from app.services.scientific_diagram_repository import (
    ScientificDiagramRepository,
)
from app.services.session_store import InMemoryProjectStore, project_store


client = TestClient(app)


def _pdf_bytes(text: str = "1. Calculate wave speed. [2]") -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, 780, text)
    pdf.drawString(72, 750, "2. Explain wave frequency. [2]")
    pdf.save()
    return buffer.getvalue()


def _initialize_schema(db_path: Path) -> None:
    for repository in (
        ProjectRepository,
        AuthRepository,
        QuestionBankRepository,
        AssessmentRepository,
        DifferentiatedActivityRepository,
        ScientificDiagramRepository,
        CloudSourceRepository,
        CloudSourceVersionRepository,
    ):
        repository(db_path)


def test_phase10_a_local_release_acceptance(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project_id = client.post("/api/projects", json={}).json()["id"]
    try:
        upload = client.post(
            f"/api/projects/{project_id}/upload-pdf",
            files={
                "file": (
                    "release-paper.pdf",
                    _pdf_bytes(),
                    "application/pdf",
                )
            },
        )
        assert upload.status_code == 200
        assert upload.json()["extracted_text"]["is_text_based"] is True

        parsed = client.post(
            f"/api/projects/{project_id}/parse-questions"
        )
        assert parsed.status_code == 200
        assert len(parsed.json()["questions"]) == 2

        glossary = client.post(
            f"/api/projects/{project_id}/glossary/generate"
        )
        assert glossary.status_code == 200

        translated = client.post(
            f"/api/projects/{project_id}/translate-questions"
        )
        assert translated.status_code == 200
        project = ProjectSession.model_validate(translated.json())
        assert all(item.translated_text for item in project.questions)

        readiness = client.get(
            f"/api/projects/{project_id}/readiness"
        )
        assert readiness.status_code == 200
        assert readiness.json()["ready"] is True

        docx = client.post(f"/api/projects/{project_id}/export/docx")
        pdf = client.post(f"/api/projects/{project_id}/export/pdf")
        assert docx.status_code == 200
        assert docx.content.startswith(b"PK")
        assert pdf.status_code == 200
        assert pdf.content.startswith(b"%PDF")

        db_path = tmp_path / "release.sqlite3"
        _initialize_schema(db_path)
        bank_repository = QuestionBankRepository(db_path)
        assessment_repository = AssessmentRepository(db_path)
        activity_repository = DifferentiatedActivityRepository(db_path)
        diagram_repository = ScientificDiagramRepository(db_path)

        bank_item = bank_repository.save_from_project_question(
            project,
            project.questions[0],
        )
        draft = assessment_repository.create(
            blueprint=AssessmentBlueprint(
                total_marks=2,
                target_question_count=1,
            ),
            owner_account_id=None,
            source_project_id=project.id,
        )
        draft, added = assessment_repository.add_bank_item(
            draft,
            bank_item,
        )
        detail = build_assessment_detail(draft, bank_repository)
        assert added is True
        assert detail.balance.selected_question_count == 1
        assert detail.balance.selected_marks == 2

        activity_set = generate_differentiated_activity_set(
            DifferentiatedActivityGenerationRequest(
                source_project_id=project.id,
                source_question_bank_item_id=bank_item.id,
                title="نشاط قبول الإصدار",
                grade=10,
                science_domain="physics",
                subject_id="g10-physics",
                objective="تفسير العلاقة بين خصائص الموجة.",
                core_task="قارن بين التردد والطول الموجي.",
                estimated_minutes=20,
            ),
            activity_repository,
            bank_item=bank_item,
        )
        assert activity_set.total == 3

        import app.services.differentiated_activity_export as activity_export

        monkeypatch.setattr(
            activity_export,
            "EXPORT_DIR",
            tmp_path / "activity-exports",
        )
        activity_file = export_activity(activity_set.items[0], "pdf")
        assert Path(activity_file.path).read_bytes().startswith(b"%PDF")

        first_node = ScientificDiagramNode(
            id="node-1",
            label="تردد",
            order_index=1,
        )
        second_node = ScientificDiagramNode(
            id="node-2",
            label="طول موجي",
            order_index=2,
        )
        diagram = diagram_repository.create(
            ScientificDiagramCreateRequest(
                source_project_id=project.id,
                title="العلاقة بين خصائص الموجة",
                diagram_type=ScientificDiagramType.cause_effect,
                grade=10,
                science_domain="physics",
                subject_id="g10-physics",
                nodes=[first_node, second_node],
                edges=[
                    ScientificDiagramEdge(
                        source_node_id=first_node.id,
                        target_node_id=second_node.id,
                        label="علاقة عكسية",
                    )
                ],
            )
        )

        import app.services.scientific_diagram_renderer as diagram_renderer

        monkeypatch.setattr(
            diagram_renderer,
            "EXPORT_DIR",
            tmp_path / "diagram-exports",
        )
        diagram_png = export_scientific_diagram_binary(diagram, "png")
        diagram_pdf = export_scientific_diagram_binary(diagram, "pdf")
        assert Path(diagram_png.path).read_bytes().startswith(b"\x89PNG")
        assert Path(diagram_pdf.path).read_bytes().startswith(b"%PDF")

        cloud_pdf = tmp_path / "cloud-release-paper.pdf"
        cloud_pdf.write_bytes(_pdf_bytes("1. State wave speed. [1]"))
        source_repository = CloudSourceRepository(db_path)
        version_repository = CloudSourceVersionRepository(db_path)
        source = source_repository.save(
            CloudSource(
                provider=CloudSourceProvider.onedrive,
                display_name="cloud-release-paper.pdf",
                external_id="phase10-a-file",
                web_url="https://example.invalid/cloud-release-paper.pdf",
                mime_type="application/pdf",
            )
        )

        def fake_sync(*args, **kwargs):
            current = args[0]
            current.etag = "phase10-a-etag"
            current.modified_at_external = datetime(
                2026,
                7,
                23,
                8,
                0,
                tzinfo=timezone.utc,
            )
            current.metadata["local_path"] = str(cloud_pdf)
            return CloudSourceSyncResponse(
                source=current,
                changed=False,
                downloaded=True,
                local_path=str(cloud_pdf),
                message="synced",
            )

        monkeypatch.setattr(
            "app.services.cloud_source_lifecycle."
            "synchronize_onedrive_source",
            fake_sync,
        )
        refreshed = refresh_cloud_source(
            source,
            source_repository,
            version_repository,
        )
        intake_store = InMemoryProjectStore(ProjectRepository(db_path))
        intake = intake_cloud_source_version(
            refreshed.source,
            refreshed.version,
            source_repository,
            version_repository,
            intake_store,
        )
        assert intake.created_project is True
        assert intake.project.extracted_text is not None
        assert intake.project.extracted_text.is_text_based is True

        runtime_report = build_release_readiness_report(
            db_path=db_path,
            data_dir=tmp_path / "runtime-data",
        )
        assert runtime_report.technical_ready is True
        assert runtime_report.blocking_count == 0
    finally:
        project_store.delete(project_id)
