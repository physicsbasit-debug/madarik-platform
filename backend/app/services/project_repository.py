from __future__ import annotations

import sqlite3
from pathlib import Path

from app.core.config import settings
from app.models.project import ProjectSession


class ProjectRepository:
    """SQLite-backed repository for Phase 2-A1.

    The app still keeps an in-memory cache for speed and simple object mutation,
    but every committed project state is mirrored to SQLite. This gives Phase 2
    a durable foundation without introducing accounts, users, or a full database
    circus before the tent is even standing.
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
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
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at)"
            )

    def save(self, project: ProjectSession) -> ProjectSession:
        payload = project.model_dump_json()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO projects (id, title, subject, grade, updated_at, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    subject = excluded.subject,
                    grade = excluded.grade,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    project.id,
                    project.metadata.paper_title,
                    project.metadata.subject,
                    project.metadata.grade,
                    project.updated_at.isoformat(),
                    payload,
                ),
            )
        return project

    def load(self, project_id: str) -> ProjectSession | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()

        if row is None:
            return None

        return ProjectSession.model_validate_json(row["payload"])

    def delete(self, project_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0

    def list_recent(self, limit: int = 50) -> list[ProjectSession]:
        safe_limit = max(1, min(limit, 200))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM projects ORDER BY updated_at DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()

        return [ProjectSession.model_validate_json(row["payload"]) for row in rows]


project_repository = ProjectRepository()
