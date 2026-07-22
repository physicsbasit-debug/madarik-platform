from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.models.scientific_diagram import (
    ScientificDiagram,
    ScientificDiagramCreateRequest,
)


class ScientificDiagramRepository:
    def __init__(
        self,
        db_path: str | Path | None = None,
    ) -> None:
        self.db_path = Path(db_path or settings.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS scientific_diagrams (
                    id TEXT PRIMARY KEY,
                    owner_account_id TEXT,
                    source_project_id TEXT,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

    def create(
        self,
        payload: ScientificDiagramCreateRequest,
        owner_account_id: str | None = None,
    ) -> ScientificDiagram:
        return self.save(
            ScientificDiagram(
                owner_account_id=owner_account_id,
                **payload.model_dump(),
            )
        )

    def save(
        self,
        diagram: ScientificDiagram,
    ) -> ScientificDiagram:
        diagram.updated_at = datetime.now(timezone.utc)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO scientific_diagrams (
                    id,
                    owner_account_id,
                    source_project_id,
                    updated_at,
                    payload
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id)
                DO UPDATE SET
                    owner_account_id = excluded.owner_account_id,
                    source_project_id = excluded.source_project_id,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    diagram.id,
                    diagram.owner_account_id,
                    diagram.source_project_id,
                    diagram.updated_at.isoformat(),
                    diagram.model_dump_json(),
                ),
            )
        return diagram

    def list(
        self,
        *,
        owner_account_id: str | None = None,
        grade: int | None = None,
        science_domain: str | None = None,
        unit_id: str | None = None,
        diagram_type: str | None = None,
    ) -> list[ScientificDiagram]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload
                FROM scientific_diagrams
                ORDER BY updated_at DESC
                """
            ).fetchall()

        items = [
            ScientificDiagram.model_validate_json(row["payload"])
            for row in rows
        ]

        if owner_account_id:
            items = [
                item
                for item in items
                if item.owner_account_id == owner_account_id
            ]
        if grade is not None:
            items = [item for item in items if item.grade == grade]
        if science_domain:
            items = [
                item
                for item in items
                if item.science_domain == science_domain
            ]
        if unit_id:
            items = [item for item in items if item.unit_id == unit_id]
        if diagram_type:
            items = [
                item
                for item in items
                if item.diagram_type.value == diagram_type
            ]
        return items

    def get(
        self,
        diagram_id: str,
    ) -> ScientificDiagram | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM scientific_diagrams
                WHERE id = ?
                """,
                (diagram_id,),
            ).fetchone()
        if row is None:
            return None
        return ScientificDiagram.model_validate_json(
            row["payload"]
        )

    def delete(
        self,
        diagram_id: str,
    ) -> ScientificDiagram | None:
        diagram = self.get(diagram_id)
        if diagram is None:
            return None
        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM scientific_diagrams
                WHERE id = ?
                """,
                (diagram_id,),
            )
        return diagram


scientific_diagram_repository = ScientificDiagramRepository()
